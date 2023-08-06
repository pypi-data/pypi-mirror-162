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
        yiqc__wqk = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, yiqc__wqk)


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
        qvr__zlt = args[0]
        skyqk__zuwbg = signature.return_type
        voln__ymobq = cgutils.create_struct_proxy(skyqk__zuwbg)(context,
            builder)
        voln__ymobq.obj = qvr__zlt
        context.nrt.incref(builder, signature.args[0], qvr__zlt)
        return voln__ymobq._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for wgc__apxts in keys:
        selection.remove(wgc__apxts)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    if is_overload_constant_int(_num_shuffle_keys):
        uxb__ssmsd = get_overload_const_int(_num_shuffle_keys)
    else:
        uxb__ssmsd = -1
    skyqk__zuwbg = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False, _num_shuffle_keys=uxb__ssmsd)
    return skyqk__zuwbg(obj_type, by_type, as_index_type, dropna_type,
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
        grpby, kha__dzvp = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(kha__dzvp, (tuple, list)):
                if len(set(kha__dzvp).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(kha__dzvp).difference(set(grpby.df_type
                        .columns))))
                selection = kha__dzvp
            else:
                if kha__dzvp not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(kha__dzvp))
                selection = kha__dzvp,
                series_select = True
            blj__qedln = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True,
                series_select, _num_shuffle_keys=grpby._num_shuffle_keys)
            return signature(blj__qedln, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, kha__dzvp = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            kha__dzvp):
            blj__qedln = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(kha__dzvp)), {}).return_type
            return signature(blj__qedln, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    yvaj__hxrfz = arr_type == ArrayItemArrayType(string_array_type)
    ffqfm__vafdx = arr_type.dtype
    if isinstance(ffqfm__vafdx, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {ffqfm__vafdx} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(ffqfm__vafdx, (
        Decimal128Type, types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {ffqfm__vafdx} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(
        ffqfm__vafdx, (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(ffqfm__vafdx, (types.Integer, types.Float, types.Boolean)
        ):
        if yvaj__hxrfz or ffqfm__vafdx == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(ffqfm__vafdx, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not ffqfm__vafdx.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {ffqfm__vafdx} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(ffqfm__vafdx, types.Boolean) and func_name in {'cumsum',
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
    ffqfm__vafdx = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(ffqfm__vafdx, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(ffqfm__vafdx, types.Integer):
            return IntDtype(ffqfm__vafdx)
        return ffqfm__vafdx
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        agiqa__plb = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{agiqa__plb}'."
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
    for wgc__apxts in grp.keys:
        if multi_level_names:
            uof__ofuyd = wgc__apxts, ''
        else:
            uof__ofuyd = wgc__apxts
        bpc__oji = grp.df_type.column_index[wgc__apxts]
        data = grp.df_type.data[bpc__oji]
        out_columns.append(uof__ofuyd)
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
        yglz__kmo = tuple(grp.df_type.column_index[grp.keys[uydc__mtkkm]] for
            uydc__mtkkm in range(len(grp.keys)))
        snxh__qjlpm = tuple(grp.df_type.data[bpc__oji] for bpc__oji in
            yglz__kmo)
        index = MultiIndexType(snxh__qjlpm, tuple(types.StringLiteral(
            wgc__apxts) for wgc__apxts in grp.keys))
    else:
        bpc__oji = grp.df_type.column_index[grp.keys[0]]
        sut__tfh = grp.df_type.data[bpc__oji]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(sut__tfh,
            types.StringLiteral(grp.keys[0]))
    vmaq__hzomn = {}
    joytz__dbtvp = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        vmaq__hzomn[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        vmaq__hzomn[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        ftqm__oxlxh = dict(ascending=ascending)
        bpr__pki = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', ftqm__oxlxh,
            bpr__pki, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for dwv__ynsl in columns:
            bpc__oji = grp.df_type.column_index[dwv__ynsl]
            data = grp.df_type.data[bpc__oji]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            fgnes__zjadf = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                fgnes__zjadf = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    oxn__xxqdx = SeriesType(data.dtype, data, None, string_type
                        )
                    udoc__grl = get_const_func_output_type(func, (
                        oxn__xxqdx,), {}, typing_context, target_context)
                    if udoc__grl != ArrayItemArrayType(string_array_type):
                        udoc__grl = dtype_to_array_type(udoc__grl)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=dwv__ynsl, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    hju__aifzz = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    gfsz__uvib = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    ftqm__oxlxh = dict(numeric_only=hju__aifzz, min_count=
                        gfsz__uvib)
                    bpr__pki = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ftqm__oxlxh, bpr__pki, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    hju__aifzz = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    gfsz__uvib = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    ftqm__oxlxh = dict(numeric_only=hju__aifzz, min_count=
                        gfsz__uvib)
                    bpr__pki = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ftqm__oxlxh, bpr__pki, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    hju__aifzz = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    ftqm__oxlxh = dict(numeric_only=hju__aifzz)
                    bpr__pki = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ftqm__oxlxh, bpr__pki, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    dvgxf__bjsg = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    awyxr__pjoec = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    ftqm__oxlxh = dict(axis=dvgxf__bjsg, skipna=awyxr__pjoec)
                    bpr__pki = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ftqm__oxlxh, bpr__pki, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    ffh__mrw = args[0] if len(args) > 0 else kws.pop('ddof', 1)
                    ftqm__oxlxh = dict(ddof=ffh__mrw)
                    bpr__pki = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ftqm__oxlxh, bpr__pki, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                udoc__grl, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                udoc__grl = to_str_arr_if_dict_array(udoc__grl
                    ) if func_name in ('sum', 'cumsum') else udoc__grl
                out_data.append(udoc__grl)
                out_columns.append(dwv__ynsl)
                if func_name == 'agg':
                    rdiso__zkwp = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    vmaq__hzomn[dwv__ynsl, rdiso__zkwp] = dwv__ynsl
                else:
                    vmaq__hzomn[dwv__ynsl, func_name] = dwv__ynsl
                out_column_type.append(fgnes__zjadf)
            else:
                joytz__dbtvp.append(err_msg)
    if func_name == 'sum':
        wksap__xudil = any([(augif__vxssl == ColumnType.NumericalColumn.
            value) for augif__vxssl in out_column_type])
        if wksap__xudil:
            out_data = [augif__vxssl for augif__vxssl, fyyk__sjil in zip(
                out_data, out_column_type) if fyyk__sjil != ColumnType.
                NonNumericalColumn.value]
            out_columns = [augif__vxssl for augif__vxssl, fyyk__sjil in zip
                (out_columns, out_column_type) if fyyk__sjil != ColumnType.
                NonNumericalColumn.value]
            vmaq__hzomn = {}
            for dwv__ynsl in out_columns:
                if grp.as_index is False and dwv__ynsl in grp.keys:
                    continue
                vmaq__hzomn[dwv__ynsl, func_name] = dwv__ynsl
    slp__wge = len(joytz__dbtvp)
    if len(out_data) == 0:
        if slp__wge == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(slp__wge, ' was' if slp__wge == 1 else 's were',
                ','.join(joytz__dbtvp)))
    fxl__ozqd = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            idmvd__gvj = IntDtype(out_data[0].dtype)
        else:
            idmvd__gvj = out_data[0].dtype
        wzsa__fxx = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        fxl__ozqd = SeriesType(idmvd__gvj, data=out_data[0], index=index,
            name_typ=wzsa__fxx)
    return signature(fxl__ozqd, *args), vmaq__hzomn


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    rua__zig = True
    if isinstance(f_val, str):
        rua__zig = False
        ktqgx__vuk = f_val
    elif is_overload_constant_str(f_val):
        rua__zig = False
        ktqgx__vuk = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        rua__zig = False
        ktqgx__vuk = bodo.utils.typing.get_builtin_function_name(f_val)
    if not rua__zig:
        if ktqgx__vuk not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {ktqgx__vuk}')
        blj__qedln = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(blj__qedln, (), ktqgx__vuk, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            qnrh__xnti = types.functions.MakeFunctionLiteral(f_val)
        else:
            qnrh__xnti = f_val
        validate_udf('agg', qnrh__xnti)
        func = get_overload_const_func(qnrh__xnti, None)
        qpfm__tlmh = func.code if hasattr(func, 'code') else func.__code__
        ktqgx__vuk = qpfm__tlmh.co_name
        blj__qedln = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(blj__qedln, (), 'agg', typing_context,
            target_context, qnrh__xnti)[0].return_type
    return ktqgx__vuk, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    kjuaq__swl = kws and all(isinstance(eytbp__vab, types.Tuple) and len(
        eytbp__vab) == 2 for eytbp__vab in kws.values())
    if is_overload_none(func) and not kjuaq__swl:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not kjuaq__swl:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    rqak__sll = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if kjuaq__swl or is_overload_constant_dict(func):
        if kjuaq__swl:
            zxmnf__ixqpl = [get_literal_value(ruac__xqtyh) for ruac__xqtyh,
                eguc__zyvg in kws.values()]
            dcbx__fhwu = [get_literal_value(nfrs__xzt) for eguc__zyvg,
                nfrs__xzt in kws.values()]
        else:
            dppv__bpxy = get_overload_constant_dict(func)
            zxmnf__ixqpl = tuple(dppv__bpxy.keys())
            dcbx__fhwu = tuple(dppv__bpxy.values())
        for ktwod__bja in ('head', 'ngroup'):
            if ktwod__bja in dcbx__fhwu:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {ktwod__bja} cannot be mixed with other groupby operations.'
                    )
        if any(dwv__ynsl not in grp.selection and dwv__ynsl not in grp.keys for
            dwv__ynsl in zxmnf__ixqpl):
            raise_bodo_error(
                f'Selected column names {zxmnf__ixqpl} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            dcbx__fhwu)
        if kjuaq__swl and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        vmaq__hzomn = {}
        out_columns = []
        out_data = []
        out_column_type = []
        vhi__zvknc = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for vavj__gwz, f_val in zip(zxmnf__ixqpl, dcbx__fhwu):
            if isinstance(f_val, (tuple, list)):
                ivo__xflj = 0
                for qnrh__xnti in f_val:
                    ktqgx__vuk, out_tp = get_agg_funcname_and_outtyp(grp,
                        vavj__gwz, qnrh__xnti, typing_context, target_context)
                    rqak__sll = ktqgx__vuk in list_cumulative
                    if ktqgx__vuk == '<lambda>' and len(f_val) > 1:
                        ktqgx__vuk = '<lambda_' + str(ivo__xflj) + '>'
                        ivo__xflj += 1
                    out_columns.append((vavj__gwz, ktqgx__vuk))
                    vmaq__hzomn[vavj__gwz, ktqgx__vuk] = vavj__gwz, ktqgx__vuk
                    _append_out_type(grp, out_data, out_tp)
            else:
                ktqgx__vuk, out_tp = get_agg_funcname_and_outtyp(grp,
                    vavj__gwz, f_val, typing_context, target_context)
                rqak__sll = ktqgx__vuk in list_cumulative
                if multi_level_names:
                    out_columns.append((vavj__gwz, ktqgx__vuk))
                    vmaq__hzomn[vavj__gwz, ktqgx__vuk] = vavj__gwz, ktqgx__vuk
                elif not kjuaq__swl:
                    out_columns.append(vavj__gwz)
                    vmaq__hzomn[vavj__gwz, ktqgx__vuk] = vavj__gwz
                elif kjuaq__swl:
                    vhi__zvknc.append(ktqgx__vuk)
                _append_out_type(grp, out_data, out_tp)
        if kjuaq__swl:
            for uydc__mtkkm, nohqx__xnjh in enumerate(kws.keys()):
                out_columns.append(nohqx__xnjh)
                vmaq__hzomn[zxmnf__ixqpl[uydc__mtkkm], vhi__zvknc[uydc__mtkkm]
                    ] = nohqx__xnjh
        if rqak__sll:
            index = grp.df_type.index
        else:
            index = out_tp.index
        fxl__ozqd = DataFrameType(tuple(out_data), index, tuple(out_columns
            ), is_table_format=True)
        return signature(fxl__ozqd, *args), vmaq__hzomn
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            nmcs__rqp = get_overload_const_list(func)
        else:
            nmcs__rqp = func.types
        if len(nmcs__rqp) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        ivo__xflj = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        vmaq__hzomn = {}
        wgc__ect = grp.selection[0]
        for f_val in nmcs__rqp:
            ktqgx__vuk, out_tp = get_agg_funcname_and_outtyp(grp, wgc__ect,
                f_val, typing_context, target_context)
            rqak__sll = ktqgx__vuk in list_cumulative
            if ktqgx__vuk == '<lambda>' and len(nmcs__rqp) > 1:
                ktqgx__vuk = '<lambda_' + str(ivo__xflj) + '>'
                ivo__xflj += 1
            out_columns.append(ktqgx__vuk)
            vmaq__hzomn[wgc__ect, ktqgx__vuk] = ktqgx__vuk
            _append_out_type(grp, out_data, out_tp)
        if rqak__sll:
            index = grp.df_type.index
        else:
            index = out_tp.index
        fxl__ozqd = DataFrameType(tuple(out_data), index, tuple(out_columns
            ), is_table_format=True)
        return signature(fxl__ozqd, *args), vmaq__hzomn
    ktqgx__vuk = ''
    if types.unliteral(func) == types.unicode_type:
        ktqgx__vuk = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        ktqgx__vuk = bodo.utils.typing.get_builtin_function_name(func)
    if ktqgx__vuk:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, ktqgx__vuk, typing_context, kws)
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
        dvgxf__bjsg = args[0] if len(args) > 0 else kws.pop('axis', 0)
        hju__aifzz = args[1] if len(args) > 1 else kws.pop('numeric_only', 
            False)
        awyxr__pjoec = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        ftqm__oxlxh = dict(axis=dvgxf__bjsg, numeric_only=hju__aifzz)
        bpr__pki = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', ftqm__oxlxh,
            bpr__pki, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        oww__cfd = args[0] if len(args) > 0 else kws.pop('periods', 1)
        yukcu__dfz = args[1] if len(args) > 1 else kws.pop('freq', None)
        dvgxf__bjsg = args[2] if len(args) > 2 else kws.pop('axis', 0)
        xqa__fpia = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        ftqm__oxlxh = dict(freq=yukcu__dfz, axis=dvgxf__bjsg, fill_value=
            xqa__fpia)
        bpr__pki = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', ftqm__oxlxh,
            bpr__pki, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        mplxw__vano = args[0] if len(args) > 0 else kws.pop('func', None)
        tqyo__pmbfv = kws.pop('engine', None)
        kzhqr__xxm = kws.pop('engine_kwargs', None)
        ftqm__oxlxh = dict(engine=tqyo__pmbfv, engine_kwargs=kzhqr__xxm)
        bpr__pki = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', ftqm__oxlxh, bpr__pki,
            package_name='pandas', module_name='GroupBy')
    vmaq__hzomn = {}
    for dwv__ynsl in grp.selection:
        out_columns.append(dwv__ynsl)
        vmaq__hzomn[dwv__ynsl, name_operation] = dwv__ynsl
        bpc__oji = grp.df_type.column_index[dwv__ynsl]
        data = grp.df_type.data[bpc__oji]
        cjiza__mczyr = (name_operation if name_operation != 'transform' else
            get_literal_value(mplxw__vano))
        if cjiza__mczyr in ('sum', 'cumsum'):
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
            udoc__grl, err_msg = get_groupby_output_dtype(data,
                get_literal_value(mplxw__vano), grp.df_type.index)
            if err_msg == 'ok':
                data = udoc__grl
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    fxl__ozqd = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        fxl__ozqd = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(fxl__ozqd, *args), vmaq__hzomn


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
        vmvux__nlkbp = _get_groupby_apply_udf_out_type(func, grp, f_args,
            kws, self.context, numba.core.registry.cpu_target.target_context)
        ckg__tzc = isinstance(vmvux__nlkbp, (SeriesType,
            HeterogeneousSeriesType)
            ) and vmvux__nlkbp.const_info is not None or not isinstance(
            vmvux__nlkbp, (SeriesType, DataFrameType))
        if ckg__tzc:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                wsnm__avyc = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                yglz__kmo = tuple(grp.df_type.column_index[grp.keys[
                    uydc__mtkkm]] for uydc__mtkkm in range(len(grp.keys)))
                snxh__qjlpm = tuple(grp.df_type.data[bpc__oji] for bpc__oji in
                    yglz__kmo)
                wsnm__avyc = MultiIndexType(snxh__qjlpm, tuple(types.
                    literal(wgc__apxts) for wgc__apxts in grp.keys))
            else:
                bpc__oji = grp.df_type.column_index[grp.keys[0]]
                sut__tfh = grp.df_type.data[bpc__oji]
                wsnm__avyc = bodo.hiframes.pd_index_ext.array_type_to_index(
                    sut__tfh, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            wys__wpae = tuple(grp.df_type.data[grp.df_type.column_index[
                dwv__ynsl]] for dwv__ynsl in grp.keys)
            ztqq__wax = tuple(types.literal(eytbp__vab) for eytbp__vab in
                grp.keys) + get_index_name_types(vmvux__nlkbp.index)
            if not grp.as_index:
                wys__wpae = types.Array(types.int64, 1, 'C'),
                ztqq__wax = (types.none,) + get_index_name_types(vmvux__nlkbp
                    .index)
            wsnm__avyc = MultiIndexType(wys__wpae +
                get_index_data_arr_types(vmvux__nlkbp.index), ztqq__wax)
        if ckg__tzc:
            if isinstance(vmvux__nlkbp, HeterogeneousSeriesType):
                eguc__zyvg, tawla__jlk = vmvux__nlkbp.const_info
                if isinstance(vmvux__nlkbp.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    gby__cipf = vmvux__nlkbp.data.tuple_typ.types
                elif isinstance(vmvux__nlkbp.data, types.Tuple):
                    gby__cipf = vmvux__nlkbp.data.types
                oebt__dban = tuple(to_nullable_type(dtype_to_array_type(
                    xrkuq__ika)) for xrkuq__ika in gby__cipf)
                aom__bwxxt = DataFrameType(out_data + oebt__dban,
                    wsnm__avyc, out_columns + tawla__jlk)
            elif isinstance(vmvux__nlkbp, SeriesType):
                qpb__xly, tawla__jlk = vmvux__nlkbp.const_info
                oebt__dban = tuple(to_nullable_type(dtype_to_array_type(
                    vmvux__nlkbp.dtype)) for eguc__zyvg in range(qpb__xly))
                aom__bwxxt = DataFrameType(out_data + oebt__dban,
                    wsnm__avyc, out_columns + tawla__jlk)
            else:
                ydbq__bcm = get_udf_out_arr_type(vmvux__nlkbp)
                if not grp.as_index:
                    aom__bwxxt = DataFrameType(out_data + (ydbq__bcm,),
                        wsnm__avyc, out_columns + ('',))
                else:
                    aom__bwxxt = SeriesType(ydbq__bcm.dtype, ydbq__bcm,
                        wsnm__avyc, None)
        elif isinstance(vmvux__nlkbp, SeriesType):
            aom__bwxxt = SeriesType(vmvux__nlkbp.dtype, vmvux__nlkbp.data,
                wsnm__avyc, vmvux__nlkbp.name_typ)
        else:
            aom__bwxxt = DataFrameType(vmvux__nlkbp.data, wsnm__avyc,
                vmvux__nlkbp.columns)
        mszz__sez = gen_apply_pysig(len(f_args), kws.keys())
        rbwe__tntc = (func, *f_args) + tuple(kws.values())
        return signature(aom__bwxxt, *rbwe__tntc).replace(pysig=mszz__sez)

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
    imjop__oikm = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            vavj__gwz = grp.selection[0]
            ydbq__bcm = imjop__oikm.data[imjop__oikm.column_index[vavj__gwz]]
            emqae__ckbud = SeriesType(ydbq__bcm.dtype, ydbq__bcm,
                imjop__oikm.index, types.literal(vavj__gwz))
        else:
            cfyk__udm = tuple(imjop__oikm.data[imjop__oikm.column_index[
                dwv__ynsl]] for dwv__ynsl in grp.selection)
            emqae__ckbud = DataFrameType(cfyk__udm, imjop__oikm.index,
                tuple(grp.selection))
    else:
        emqae__ckbud = imjop__oikm
    vbh__hcypw = emqae__ckbud,
    vbh__hcypw += tuple(f_args)
    try:
        vmvux__nlkbp = get_const_func_output_type(func, vbh__hcypw, kws,
            typing_context, target_context)
    except Exception as zqx__vwbw:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', zqx__vwbw),
            getattr(zqx__vwbw, 'loc', None))
    return vmvux__nlkbp


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    vbh__hcypw = (grp,) + f_args
    try:
        vmvux__nlkbp = get_const_func_output_type(func, vbh__hcypw, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as zqx__vwbw:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', zqx__vwbw),
            getattr(zqx__vwbw, 'loc', None))
    mszz__sez = gen_apply_pysig(len(f_args), kws.keys())
    rbwe__tntc = (func, *f_args) + tuple(kws.values())
    return signature(vmvux__nlkbp, *rbwe__tntc).replace(pysig=mszz__sez)


def gen_apply_pysig(n_args, kws):
    vmlf__tsbk = ', '.join(f'arg{uydc__mtkkm}' for uydc__mtkkm in range(n_args)
        )
    vmlf__tsbk = vmlf__tsbk + ', ' if vmlf__tsbk else ''
    ehjkb__fnawk = ', '.join(f"{abswk__etw} = ''" for abswk__etw in kws)
    yxo__nonmy = f'def apply_stub(func, {vmlf__tsbk}{ehjkb__fnawk}):\n'
    yxo__nonmy += '    pass\n'
    lhlol__bofas = {}
    exec(yxo__nonmy, {}, lhlol__bofas)
    rwuat__hlg = lhlol__bofas['apply_stub']
    return numba.core.utils.pysignature(rwuat__hlg)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        xfxa__wzvhy = types.Array(types.int64, 1, 'C')
        lys__vkbl = _pivot_values.meta
        rcuw__kbka = len(lys__vkbl)
        xwnm__keg = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        lzyi__rhu = DataFrameType((xfxa__wzvhy,) * rcuw__kbka, xwnm__keg,
            tuple(lys__vkbl))
        return signature(lzyi__rhu, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    yxo__nonmy = 'def impl(keys, dropna, _is_parallel):\n'
    yxo__nonmy += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    yxo__nonmy += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{uydc__mtkkm}])' for uydc__mtkkm in range(len(
        keys.types))))
    yxo__nonmy += '    table = arr_info_list_to_table(info_list)\n'
    yxo__nonmy += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    yxo__nonmy += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    yxo__nonmy += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    yxo__nonmy += '    delete_table_decref_arrays(table)\n'
    yxo__nonmy += '    ev.finalize()\n'
    yxo__nonmy += '    return sort_idx, group_labels, ngroups\n'
    lhlol__bofas = {}
    exec(yxo__nonmy, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, lhlol__bofas
        )
    baq__ixcib = lhlol__bofas['impl']
    return baq__ixcib


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    zwkw__dyxnr = len(labels)
    tckdd__fdj = np.zeros(ngroups, dtype=np.int64)
    ijw__ksui = np.zeros(ngroups, dtype=np.int64)
    jxh__kvxsg = 0
    ptcd__pxtvm = 0
    for uydc__mtkkm in range(zwkw__dyxnr):
        vcfww__metqx = labels[uydc__mtkkm]
        if vcfww__metqx < 0:
            jxh__kvxsg += 1
        else:
            ptcd__pxtvm += 1
            if uydc__mtkkm == zwkw__dyxnr - 1 or vcfww__metqx != labels[
                uydc__mtkkm + 1]:
                tckdd__fdj[vcfww__metqx] = jxh__kvxsg
                ijw__ksui[vcfww__metqx] = jxh__kvxsg + ptcd__pxtvm
                jxh__kvxsg += ptcd__pxtvm
                ptcd__pxtvm = 0
    return tckdd__fdj, ijw__ksui


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    baq__ixcib, eguc__zyvg = gen_shuffle_dataframe(df, keys, _is_parallel)
    return baq__ixcib


def gen_shuffle_dataframe(df, keys, _is_parallel):
    qpb__xly = len(df.columns)
    rsr__ibyqo = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    yxo__nonmy = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        yxo__nonmy += '  return df, keys, get_null_shuffle_info()\n'
        lhlol__bofas = {}
        exec(yxo__nonmy, {'get_null_shuffle_info': get_null_shuffle_info},
            lhlol__bofas)
        baq__ixcib = lhlol__bofas['impl']
        return baq__ixcib
    for uydc__mtkkm in range(qpb__xly):
        yxo__nonmy += f"""  in_arr{uydc__mtkkm} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {uydc__mtkkm})
"""
    yxo__nonmy += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    yxo__nonmy += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{uydc__mtkkm}])' for uydc__mtkkm in range(
        rsr__ibyqo)), ', '.join(f'array_to_info(in_arr{uydc__mtkkm})' for
        uydc__mtkkm in range(qpb__xly)), 'array_to_info(in_index_arr)')
    yxo__nonmy += '  table = arr_info_list_to_table(info_list)\n'
    yxo__nonmy += (
        f'  out_table = shuffle_table(table, {rsr__ibyqo}, _is_parallel, 1)\n')
    for uydc__mtkkm in range(rsr__ibyqo):
        yxo__nonmy += f"""  out_key{uydc__mtkkm} = info_to_array(info_from_table(out_table, {uydc__mtkkm}), keys{uydc__mtkkm}_typ)
"""
    for uydc__mtkkm in range(qpb__xly):
        yxo__nonmy += f"""  out_arr{uydc__mtkkm} = info_to_array(info_from_table(out_table, {uydc__mtkkm + rsr__ibyqo}), in_arr{uydc__mtkkm}_typ)
"""
    yxo__nonmy += f"""  out_arr_index = info_to_array(info_from_table(out_table, {rsr__ibyqo + qpb__xly}), ind_arr_typ)
"""
    yxo__nonmy += '  shuffle_info = get_shuffle_info(out_table)\n'
    yxo__nonmy += '  delete_table(out_table)\n'
    yxo__nonmy += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{uydc__mtkkm}' for uydc__mtkkm in range(
        qpb__xly))
    yxo__nonmy += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    yxo__nonmy += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    yxo__nonmy += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{uydc__mtkkm}' for uydc__mtkkm in range(rsr__ibyqo)))
    kxp__rwcm = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    kxp__rwcm.update({f'keys{uydc__mtkkm}_typ': keys.types[uydc__mtkkm] for
        uydc__mtkkm in range(rsr__ibyqo)})
    kxp__rwcm.update({f'in_arr{uydc__mtkkm}_typ': df.data[uydc__mtkkm] for
        uydc__mtkkm in range(qpb__xly)})
    lhlol__bofas = {}
    exec(yxo__nonmy, kxp__rwcm, lhlol__bofas)
    baq__ixcib = lhlol__bofas['impl']
    return baq__ixcib, kxp__rwcm


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        ahljs__fwokl = len(data.array_types)
        yxo__nonmy = 'def impl(data, shuffle_info):\n'
        yxo__nonmy += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{uydc__mtkkm}])' for uydc__mtkkm in
            range(ahljs__fwokl)))
        yxo__nonmy += '  table = arr_info_list_to_table(info_list)\n'
        yxo__nonmy += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for uydc__mtkkm in range(ahljs__fwokl):
            yxo__nonmy += f"""  out_arr{uydc__mtkkm} = info_to_array(info_from_table(out_table, {uydc__mtkkm}), data._data[{uydc__mtkkm}])
"""
        yxo__nonmy += '  delete_table(out_table)\n'
        yxo__nonmy += '  delete_table(table)\n'
        yxo__nonmy += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{uydc__mtkkm}' for uydc__mtkkm in
            range(ahljs__fwokl))))
        lhlol__bofas = {}
        exec(yxo__nonmy, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, lhlol__bofas)
        baq__ixcib = lhlol__bofas['impl']
        return baq__ixcib
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            mpnxx__mmurs = bodo.utils.conversion.index_to_array(data)
            mli__kfi = reverse_shuffle(mpnxx__mmurs, shuffle_info)
            return bodo.utils.conversion.index_from_array(mli__kfi)
        return impl_index

    def impl_arr(data, shuffle_info):
        lqve__sccq = [array_to_info(data)]
        evav__dgrc = arr_info_list_to_table(lqve__sccq)
        xpnue__htwp = reverse_shuffle_table(evav__dgrc, shuffle_info)
        mli__kfi = info_to_array(info_from_table(xpnue__htwp, 0), data)
        delete_table(xpnue__htwp)
        delete_table(evav__dgrc)
        return mli__kfi
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    ftqm__oxlxh = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna
        )
    bpr__pki = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', ftqm__oxlxh, bpr__pki,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    ddwhn__poncx = get_overload_const_bool(ascending)
    akg__tqog = grp.selection[0]
    yxo__nonmy = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    orz__xea = (
        f"lambda S: S.value_counts(ascending={ddwhn__poncx}, _index_name='{akg__tqog}')"
        )
    yxo__nonmy += f'    return grp.apply({orz__xea})\n'
    lhlol__bofas = {}
    exec(yxo__nonmy, {'bodo': bodo}, lhlol__bofas)
    baq__ixcib = lhlol__bofas['impl']
    return baq__ixcib


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
    for xfufn__unuys in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, xfufn__unuys, no_unliteral
            =True)(create_unsupported_overload(
            f'DataFrameGroupBy.{xfufn__unuys}'))
    for xfufn__unuys in groupby_unsupported:
        overload_method(DataFrameGroupByType, xfufn__unuys, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{xfufn__unuys}'))
    for xfufn__unuys in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, xfufn__unuys, no_unliteral
            =True)(create_unsupported_overload(f'SeriesGroupBy.{xfufn__unuys}')
            )
    for xfufn__unuys in series_only_unsupported:
        overload_method(DataFrameGroupByType, xfufn__unuys, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{xfufn__unuys}'))
    for xfufn__unuys in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, xfufn__unuys, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{xfufn__unuys}'))


_install_groupby_unsupported()
