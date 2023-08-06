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
        btvz__lbkg = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, btvz__lbkg)


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
        cuz__ygx = args[0]
        ougk__tpy = signature.return_type
        nlrt__zwdum = cgutils.create_struct_proxy(ougk__tpy)(context, builder)
        nlrt__zwdum.obj = cuz__ygx
        context.nrt.incref(builder, signature.args[0], cuz__ygx)
        return nlrt__zwdum._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for ztfa__gdkt in keys:
        selection.remove(ztfa__gdkt)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    if is_overload_constant_int(_num_shuffle_keys):
        ivwbg__kvluh = get_overload_const_int(_num_shuffle_keys)
    else:
        ivwbg__kvluh = -1
    ougk__tpy = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False, _num_shuffle_keys=ivwbg__kvluh)
    return ougk__tpy(obj_type, by_type, as_index_type, dropna_type,
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
        grpby, nigr__caxl = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(nigr__caxl, (tuple, list)):
                if len(set(nigr__caxl).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(nigr__caxl).difference(set(grpby.
                        df_type.columns))))
                selection = nigr__caxl
            else:
                if nigr__caxl not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(nigr__caxl))
                selection = nigr__caxl,
                series_select = True
            kjii__wrxt = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True,
                series_select, _num_shuffle_keys=grpby._num_shuffle_keys)
            return signature(kjii__wrxt, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, nigr__caxl = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            nigr__caxl):
            kjii__wrxt = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(nigr__caxl)), {}).return_type
            return signature(kjii__wrxt, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    mxv__grb = arr_type == ArrayItemArrayType(string_array_type)
    ywd__vfvl = arr_type.dtype
    if isinstance(ywd__vfvl, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {ywd__vfvl} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(ywd__vfvl, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {ywd__vfvl} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(ywd__vfvl,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(ywd__vfvl, (types.Integer, types.Float, types.Boolean)):
        if mxv__grb or ywd__vfvl == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(ywd__vfvl, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not ywd__vfvl.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {ywd__vfvl} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(ywd__vfvl, types.Boolean) and func_name in {'cumsum',
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
    ywd__vfvl = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(ywd__vfvl, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(ywd__vfvl, types.Integer):
            return IntDtype(ywd__vfvl)
        return ywd__vfvl
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        tbn__vfok = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{tbn__vfok}'."
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
    for ztfa__gdkt in grp.keys:
        if multi_level_names:
            qijc__ooltv = ztfa__gdkt, ''
        else:
            qijc__ooltv = ztfa__gdkt
        umyn__ooja = grp.df_type.column_index[ztfa__gdkt]
        data = grp.df_type.data[umyn__ooja]
        out_columns.append(qijc__ooltv)
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
        pvai__mdi = tuple(grp.df_type.column_index[grp.keys[bpjt__lvesf]] for
            bpjt__lvesf in range(len(grp.keys)))
        htszr__hdo = tuple(grp.df_type.data[umyn__ooja] for umyn__ooja in
            pvai__mdi)
        index = MultiIndexType(htszr__hdo, tuple(types.StringLiteral(
            ztfa__gdkt) for ztfa__gdkt in grp.keys))
    else:
        umyn__ooja = grp.df_type.column_index[grp.keys[0]]
        shxrw__vaqrx = grp.df_type.data[umyn__ooja]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(shxrw__vaqrx,
            types.StringLiteral(grp.keys[0]))
    cjlz__yrmog = {}
    uswb__kqx = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        cjlz__yrmog[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        cjlz__yrmog[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        pkaxx__irby = dict(ascending=ascending)
        wmpmc__kmi = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', pkaxx__irby,
            wmpmc__kmi, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for uvl__jxqt in columns:
            umyn__ooja = grp.df_type.column_index[uvl__jxqt]
            data = grp.df_type.data[umyn__ooja]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            rkm__kbx = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                rkm__kbx = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    slwom__gnl = SeriesType(data.dtype, data, None, string_type
                        )
                    nfq__mlw = get_const_func_output_type(func, (slwom__gnl
                        ,), {}, typing_context, target_context)
                    if nfq__mlw != ArrayItemArrayType(string_array_type):
                        nfq__mlw = dtype_to_array_type(nfq__mlw)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=uvl__jxqt, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    bgt__jzds = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    pzpga__hhn = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    pkaxx__irby = dict(numeric_only=bgt__jzds, min_count=
                        pzpga__hhn)
                    wmpmc__kmi = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        pkaxx__irby, wmpmc__kmi, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    bgt__jzds = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    pzpga__hhn = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    pkaxx__irby = dict(numeric_only=bgt__jzds, min_count=
                        pzpga__hhn)
                    wmpmc__kmi = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        pkaxx__irby, wmpmc__kmi, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    bgt__jzds = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    pkaxx__irby = dict(numeric_only=bgt__jzds)
                    wmpmc__kmi = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        pkaxx__irby, wmpmc__kmi, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    lkmdt__dyoq = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    ydbn__iuq = args[1] if len(args) > 1 else kws.pop('skipna',
                        True)
                    pkaxx__irby = dict(axis=lkmdt__dyoq, skipna=ydbn__iuq)
                    wmpmc__kmi = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        pkaxx__irby, wmpmc__kmi, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    rle__ygnm = args[0] if len(args) > 0 else kws.pop('ddof', 1
                        )
                    pkaxx__irby = dict(ddof=rle__ygnm)
                    wmpmc__kmi = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        pkaxx__irby, wmpmc__kmi, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                nfq__mlw, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                nfq__mlw = to_str_arr_if_dict_array(nfq__mlw) if func_name in (
                    'sum', 'cumsum') else nfq__mlw
                out_data.append(nfq__mlw)
                out_columns.append(uvl__jxqt)
                if func_name == 'agg':
                    lzck__veha = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    cjlz__yrmog[uvl__jxqt, lzck__veha] = uvl__jxqt
                else:
                    cjlz__yrmog[uvl__jxqt, func_name] = uvl__jxqt
                out_column_type.append(rkm__kbx)
            else:
                uswb__kqx.append(err_msg)
    if func_name == 'sum':
        wqk__pdlv = any([(ggf__woc == ColumnType.NumericalColumn.value) for
            ggf__woc in out_column_type])
        if wqk__pdlv:
            out_data = [ggf__woc for ggf__woc, upxu__hqlxc in zip(out_data,
                out_column_type) if upxu__hqlxc != ColumnType.
                NonNumericalColumn.value]
            out_columns = [ggf__woc for ggf__woc, upxu__hqlxc in zip(
                out_columns, out_column_type) if upxu__hqlxc != ColumnType.
                NonNumericalColumn.value]
            cjlz__yrmog = {}
            for uvl__jxqt in out_columns:
                if grp.as_index is False and uvl__jxqt in grp.keys:
                    continue
                cjlz__yrmog[uvl__jxqt, func_name] = uvl__jxqt
    gcht__dhqiq = len(uswb__kqx)
    if len(out_data) == 0:
        if gcht__dhqiq == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(gcht__dhqiq, ' was' if gcht__dhqiq == 1 else
                's were', ','.join(uswb__kqx)))
    ilr__kbt = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            fwt__bsax = IntDtype(out_data[0].dtype)
        else:
            fwt__bsax = out_data[0].dtype
        bbb__hwl = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        ilr__kbt = SeriesType(fwt__bsax, data=out_data[0], index=index,
            name_typ=bbb__hwl)
    return signature(ilr__kbt, *args), cjlz__yrmog


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    wlpd__weh = True
    if isinstance(f_val, str):
        wlpd__weh = False
        jxrpd__ehn = f_val
    elif is_overload_constant_str(f_val):
        wlpd__weh = False
        jxrpd__ehn = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        wlpd__weh = False
        jxrpd__ehn = bodo.utils.typing.get_builtin_function_name(f_val)
    if not wlpd__weh:
        if jxrpd__ehn not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {jxrpd__ehn}')
        kjii__wrxt = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(kjii__wrxt, (), jxrpd__ehn, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            wowhx__xntv = types.functions.MakeFunctionLiteral(f_val)
        else:
            wowhx__xntv = f_val
        validate_udf('agg', wowhx__xntv)
        func = get_overload_const_func(wowhx__xntv, None)
        avs__qduyj = func.code if hasattr(func, 'code') else func.__code__
        jxrpd__ehn = avs__qduyj.co_name
        kjii__wrxt = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(kjii__wrxt, (), 'agg', typing_context,
            target_context, wowhx__xntv)[0].return_type
    return jxrpd__ehn, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    banxx__jyee = kws and all(isinstance(nix__vgrsn, types.Tuple) and len(
        nix__vgrsn) == 2 for nix__vgrsn in kws.values())
    if is_overload_none(func) and not banxx__jyee:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not banxx__jyee:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    dyd__zitms = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if banxx__jyee or is_overload_constant_dict(func):
        if banxx__jyee:
            pfew__tzxok = [get_literal_value(dorib__bbat) for dorib__bbat,
                zvevl__grdc in kws.values()]
            vcxx__wjfn = [get_literal_value(gfsw__wkvby) for zvevl__grdc,
                gfsw__wkvby in kws.values()]
        else:
            tev__zrcw = get_overload_constant_dict(func)
            pfew__tzxok = tuple(tev__zrcw.keys())
            vcxx__wjfn = tuple(tev__zrcw.values())
        for shdl__bql in ('head', 'ngroup'):
            if shdl__bql in vcxx__wjfn:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {shdl__bql} cannot be mixed with other groupby operations.'
                    )
        if any(uvl__jxqt not in grp.selection and uvl__jxqt not in grp.keys for
            uvl__jxqt in pfew__tzxok):
            raise_bodo_error(
                f'Selected column names {pfew__tzxok} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            vcxx__wjfn)
        if banxx__jyee and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        cjlz__yrmog = {}
        out_columns = []
        out_data = []
        out_column_type = []
        rxsnb__dna = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for dpnz__gtp, f_val in zip(pfew__tzxok, vcxx__wjfn):
            if isinstance(f_val, (tuple, list)):
                ukuz__hxmun = 0
                for wowhx__xntv in f_val:
                    jxrpd__ehn, out_tp = get_agg_funcname_and_outtyp(grp,
                        dpnz__gtp, wowhx__xntv, typing_context, target_context)
                    dyd__zitms = jxrpd__ehn in list_cumulative
                    if jxrpd__ehn == '<lambda>' and len(f_val) > 1:
                        jxrpd__ehn = '<lambda_' + str(ukuz__hxmun) + '>'
                        ukuz__hxmun += 1
                    out_columns.append((dpnz__gtp, jxrpd__ehn))
                    cjlz__yrmog[dpnz__gtp, jxrpd__ehn] = dpnz__gtp, jxrpd__ehn
                    _append_out_type(grp, out_data, out_tp)
            else:
                jxrpd__ehn, out_tp = get_agg_funcname_and_outtyp(grp,
                    dpnz__gtp, f_val, typing_context, target_context)
                dyd__zitms = jxrpd__ehn in list_cumulative
                if multi_level_names:
                    out_columns.append((dpnz__gtp, jxrpd__ehn))
                    cjlz__yrmog[dpnz__gtp, jxrpd__ehn] = dpnz__gtp, jxrpd__ehn
                elif not banxx__jyee:
                    out_columns.append(dpnz__gtp)
                    cjlz__yrmog[dpnz__gtp, jxrpd__ehn] = dpnz__gtp
                elif banxx__jyee:
                    rxsnb__dna.append(jxrpd__ehn)
                _append_out_type(grp, out_data, out_tp)
        if banxx__jyee:
            for bpjt__lvesf, xewt__tmy in enumerate(kws.keys()):
                out_columns.append(xewt__tmy)
                cjlz__yrmog[pfew__tzxok[bpjt__lvesf], rxsnb__dna[bpjt__lvesf]
                    ] = xewt__tmy
        if dyd__zitms:
            index = grp.df_type.index
        else:
            index = out_tp.index
        ilr__kbt = DataFrameType(tuple(out_data), index, tuple(out_columns),
            is_table_format=True)
        return signature(ilr__kbt, *args), cjlz__yrmog
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            fzjn__xyaw = get_overload_const_list(func)
        else:
            fzjn__xyaw = func.types
        if len(fzjn__xyaw) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        ukuz__hxmun = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        cjlz__yrmog = {}
        nndo__tfyf = grp.selection[0]
        for f_val in fzjn__xyaw:
            jxrpd__ehn, out_tp = get_agg_funcname_and_outtyp(grp,
                nndo__tfyf, f_val, typing_context, target_context)
            dyd__zitms = jxrpd__ehn in list_cumulative
            if jxrpd__ehn == '<lambda>' and len(fzjn__xyaw) > 1:
                jxrpd__ehn = '<lambda_' + str(ukuz__hxmun) + '>'
                ukuz__hxmun += 1
            out_columns.append(jxrpd__ehn)
            cjlz__yrmog[nndo__tfyf, jxrpd__ehn] = jxrpd__ehn
            _append_out_type(grp, out_data, out_tp)
        if dyd__zitms:
            index = grp.df_type.index
        else:
            index = out_tp.index
        ilr__kbt = DataFrameType(tuple(out_data), index, tuple(out_columns),
            is_table_format=True)
        return signature(ilr__kbt, *args), cjlz__yrmog
    jxrpd__ehn = ''
    if types.unliteral(func) == types.unicode_type:
        jxrpd__ehn = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        jxrpd__ehn = bodo.utils.typing.get_builtin_function_name(func)
    if jxrpd__ehn:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, jxrpd__ehn, typing_context, kws)
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
        lkmdt__dyoq = args[0] if len(args) > 0 else kws.pop('axis', 0)
        bgt__jzds = args[1] if len(args) > 1 else kws.pop('numeric_only', False
            )
        ydbn__iuq = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        pkaxx__irby = dict(axis=lkmdt__dyoq, numeric_only=bgt__jzds)
        wmpmc__kmi = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', pkaxx__irby,
            wmpmc__kmi, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        jlon__kqvrw = args[0] if len(args) > 0 else kws.pop('periods', 1)
        gmp__ufk = args[1] if len(args) > 1 else kws.pop('freq', None)
        lkmdt__dyoq = args[2] if len(args) > 2 else kws.pop('axis', 0)
        ezgl__hnudl = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        pkaxx__irby = dict(freq=gmp__ufk, axis=lkmdt__dyoq, fill_value=
            ezgl__hnudl)
        wmpmc__kmi = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', pkaxx__irby,
            wmpmc__kmi, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        ckmo__hxgco = args[0] if len(args) > 0 else kws.pop('func', None)
        wket__lvm = kws.pop('engine', None)
        gqt__dji = kws.pop('engine_kwargs', None)
        pkaxx__irby = dict(engine=wket__lvm, engine_kwargs=gqt__dji)
        wmpmc__kmi = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', pkaxx__irby,
            wmpmc__kmi, package_name='pandas', module_name='GroupBy')
    cjlz__yrmog = {}
    for uvl__jxqt in grp.selection:
        out_columns.append(uvl__jxqt)
        cjlz__yrmog[uvl__jxqt, name_operation] = uvl__jxqt
        umyn__ooja = grp.df_type.column_index[uvl__jxqt]
        data = grp.df_type.data[umyn__ooja]
        gyz__hrjyq = (name_operation if name_operation != 'transform' else
            get_literal_value(ckmo__hxgco))
        if gyz__hrjyq in ('sum', 'cumsum'):
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
            nfq__mlw, err_msg = get_groupby_output_dtype(data,
                get_literal_value(ckmo__hxgco), grp.df_type.index)
            if err_msg == 'ok':
                data = nfq__mlw
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    ilr__kbt = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        ilr__kbt = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(ilr__kbt, *args), cjlz__yrmog


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
        osl__hapio = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        ensyt__vqj = isinstance(osl__hapio, (SeriesType,
            HeterogeneousSeriesType)
            ) and osl__hapio.const_info is not None or not isinstance(
            osl__hapio, (SeriesType, DataFrameType))
        if ensyt__vqj:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                bowge__odw = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                pvai__mdi = tuple(grp.df_type.column_index[grp.keys[
                    bpjt__lvesf]] for bpjt__lvesf in range(len(grp.keys)))
                htszr__hdo = tuple(grp.df_type.data[umyn__ooja] for
                    umyn__ooja in pvai__mdi)
                bowge__odw = MultiIndexType(htszr__hdo, tuple(types.literal
                    (ztfa__gdkt) for ztfa__gdkt in grp.keys))
            else:
                umyn__ooja = grp.df_type.column_index[grp.keys[0]]
                shxrw__vaqrx = grp.df_type.data[umyn__ooja]
                bowge__odw = bodo.hiframes.pd_index_ext.array_type_to_index(
                    shxrw__vaqrx, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            tjmn__pyanl = tuple(grp.df_type.data[grp.df_type.column_index[
                uvl__jxqt]] for uvl__jxqt in grp.keys)
            fiqu__gdp = tuple(types.literal(nix__vgrsn) for nix__vgrsn in
                grp.keys) + get_index_name_types(osl__hapio.index)
            if not grp.as_index:
                tjmn__pyanl = types.Array(types.int64, 1, 'C'),
                fiqu__gdp = (types.none,) + get_index_name_types(osl__hapio
                    .index)
            bowge__odw = MultiIndexType(tjmn__pyanl +
                get_index_data_arr_types(osl__hapio.index), fiqu__gdp)
        if ensyt__vqj:
            if isinstance(osl__hapio, HeterogeneousSeriesType):
                zvevl__grdc, gjy__rkjxe = osl__hapio.const_info
                if isinstance(osl__hapio.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    fndeh__oihof = osl__hapio.data.tuple_typ.types
                elif isinstance(osl__hapio.data, types.Tuple):
                    fndeh__oihof = osl__hapio.data.types
                yypzs__akrv = tuple(to_nullable_type(dtype_to_array_type(
                    wavob__equg)) for wavob__equg in fndeh__oihof)
                jroo__bvcc = DataFrameType(out_data + yypzs__akrv,
                    bowge__odw, out_columns + gjy__rkjxe)
            elif isinstance(osl__hapio, SeriesType):
                fzsv__rec, gjy__rkjxe = osl__hapio.const_info
                yypzs__akrv = tuple(to_nullable_type(dtype_to_array_type(
                    osl__hapio.dtype)) for zvevl__grdc in range(fzsv__rec))
                jroo__bvcc = DataFrameType(out_data + yypzs__akrv,
                    bowge__odw, out_columns + gjy__rkjxe)
            else:
                gga__mdmoc = get_udf_out_arr_type(osl__hapio)
                if not grp.as_index:
                    jroo__bvcc = DataFrameType(out_data + (gga__mdmoc,),
                        bowge__odw, out_columns + ('',))
                else:
                    jroo__bvcc = SeriesType(gga__mdmoc.dtype, gga__mdmoc,
                        bowge__odw, None)
        elif isinstance(osl__hapio, SeriesType):
            jroo__bvcc = SeriesType(osl__hapio.dtype, osl__hapio.data,
                bowge__odw, osl__hapio.name_typ)
        else:
            jroo__bvcc = DataFrameType(osl__hapio.data, bowge__odw,
                osl__hapio.columns)
        muxvd__xhh = gen_apply_pysig(len(f_args), kws.keys())
        fbxf__zph = (func, *f_args) + tuple(kws.values())
        return signature(jroo__bvcc, *fbxf__zph).replace(pysig=muxvd__xhh)

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
    ervq__qadd = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            dpnz__gtp = grp.selection[0]
            gga__mdmoc = ervq__qadd.data[ervq__qadd.column_index[dpnz__gtp]]
            tjqbj__jxqh = SeriesType(gga__mdmoc.dtype, gga__mdmoc,
                ervq__qadd.index, types.literal(dpnz__gtp))
        else:
            caj__clrtv = tuple(ervq__qadd.data[ervq__qadd.column_index[
                uvl__jxqt]] for uvl__jxqt in grp.selection)
            tjqbj__jxqh = DataFrameType(caj__clrtv, ervq__qadd.index, tuple
                (grp.selection))
    else:
        tjqbj__jxqh = ervq__qadd
    uqxeb__axpo = tjqbj__jxqh,
    uqxeb__axpo += tuple(f_args)
    try:
        osl__hapio = get_const_func_output_type(func, uqxeb__axpo, kws,
            typing_context, target_context)
    except Exception as qfyn__hunmd:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', qfyn__hunmd),
            getattr(qfyn__hunmd, 'loc', None))
    return osl__hapio


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    uqxeb__axpo = (grp,) + f_args
    try:
        osl__hapio = get_const_func_output_type(func, uqxeb__axpo, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as qfyn__hunmd:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()',
            qfyn__hunmd), getattr(qfyn__hunmd, 'loc', None))
    muxvd__xhh = gen_apply_pysig(len(f_args), kws.keys())
    fbxf__zph = (func, *f_args) + tuple(kws.values())
    return signature(osl__hapio, *fbxf__zph).replace(pysig=muxvd__xhh)


def gen_apply_pysig(n_args, kws):
    hvdv__ienq = ', '.join(f'arg{bpjt__lvesf}' for bpjt__lvesf in range(n_args)
        )
    hvdv__ienq = hvdv__ienq + ', ' if hvdv__ienq else ''
    ksx__xctbb = ', '.join(f"{bwnz__ytb} = ''" for bwnz__ytb in kws)
    ufduo__ohghg = f'def apply_stub(func, {hvdv__ienq}{ksx__xctbb}):\n'
    ufduo__ohghg += '    pass\n'
    wgfs__imk = {}
    exec(ufduo__ohghg, {}, wgfs__imk)
    shx__ukubg = wgfs__imk['apply_stub']
    return numba.core.utils.pysignature(shx__ukubg)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        wlwbs__ime = types.Array(types.int64, 1, 'C')
        rvu__udplq = _pivot_values.meta
        jvsd__ygmn = len(rvu__udplq)
        aifbg__tmu = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        mquor__slppm = DataFrameType((wlwbs__ime,) * jvsd__ygmn, aifbg__tmu,
            tuple(rvu__udplq))
        return signature(mquor__slppm, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    ufduo__ohghg = 'def impl(keys, dropna, _is_parallel):\n'
    ufduo__ohghg += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    ufduo__ohghg += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{bpjt__lvesf}])' for bpjt__lvesf in range(len(
        keys.types))))
    ufduo__ohghg += '    table = arr_info_list_to_table(info_list)\n'
    ufduo__ohghg += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    ufduo__ohghg += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    ufduo__ohghg += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    ufduo__ohghg += '    delete_table_decref_arrays(table)\n'
    ufduo__ohghg += '    ev.finalize()\n'
    ufduo__ohghg += '    return sort_idx, group_labels, ngroups\n'
    wgfs__imk = {}
    exec(ufduo__ohghg, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, wgfs__imk)
    kydmd__ijuwk = wgfs__imk['impl']
    return kydmd__ijuwk


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    oozua__ovjg = len(labels)
    zwonr__feoo = np.zeros(ngroups, dtype=np.int64)
    oid__ubv = np.zeros(ngroups, dtype=np.int64)
    joia__kdrvr = 0
    hvzs__nfnt = 0
    for bpjt__lvesf in range(oozua__ovjg):
        hszv__ehbut = labels[bpjt__lvesf]
        if hszv__ehbut < 0:
            joia__kdrvr += 1
        else:
            hvzs__nfnt += 1
            if bpjt__lvesf == oozua__ovjg - 1 or hszv__ehbut != labels[
                bpjt__lvesf + 1]:
                zwonr__feoo[hszv__ehbut] = joia__kdrvr
                oid__ubv[hszv__ehbut] = joia__kdrvr + hvzs__nfnt
                joia__kdrvr += hvzs__nfnt
                hvzs__nfnt = 0
    return zwonr__feoo, oid__ubv


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    kydmd__ijuwk, zvevl__grdc = gen_shuffle_dataframe(df, keys, _is_parallel)
    return kydmd__ijuwk


def gen_shuffle_dataframe(df, keys, _is_parallel):
    fzsv__rec = len(df.columns)
    rpb__gqf = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    ufduo__ohghg = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        ufduo__ohghg += '  return df, keys, get_null_shuffle_info()\n'
        wgfs__imk = {}
        exec(ufduo__ohghg, {'get_null_shuffle_info': get_null_shuffle_info},
            wgfs__imk)
        kydmd__ijuwk = wgfs__imk['impl']
        return kydmd__ijuwk
    for bpjt__lvesf in range(fzsv__rec):
        ufduo__ohghg += f"""  in_arr{bpjt__lvesf} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {bpjt__lvesf})
"""
    ufduo__ohghg += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    ufduo__ohghg += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{bpjt__lvesf}])' for bpjt__lvesf in range(
        rpb__gqf)), ', '.join(f'array_to_info(in_arr{bpjt__lvesf})' for
        bpjt__lvesf in range(fzsv__rec)), 'array_to_info(in_index_arr)')
    ufduo__ohghg += '  table = arr_info_list_to_table(info_list)\n'
    ufduo__ohghg += (
        f'  out_table = shuffle_table(table, {rpb__gqf}, _is_parallel, 1)\n')
    for bpjt__lvesf in range(rpb__gqf):
        ufduo__ohghg += f"""  out_key{bpjt__lvesf} = info_to_array(info_from_table(out_table, {bpjt__lvesf}), keys{bpjt__lvesf}_typ)
"""
    for bpjt__lvesf in range(fzsv__rec):
        ufduo__ohghg += f"""  out_arr{bpjt__lvesf} = info_to_array(info_from_table(out_table, {bpjt__lvesf + rpb__gqf}), in_arr{bpjt__lvesf}_typ)
"""
    ufduo__ohghg += f"""  out_arr_index = info_to_array(info_from_table(out_table, {rpb__gqf + fzsv__rec}), ind_arr_typ)
"""
    ufduo__ohghg += '  shuffle_info = get_shuffle_info(out_table)\n'
    ufduo__ohghg += '  delete_table(out_table)\n'
    ufduo__ohghg += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{bpjt__lvesf}' for bpjt__lvesf in range(
        fzsv__rec))
    ufduo__ohghg += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    ufduo__ohghg += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    ufduo__ohghg += '  return out_df, ({},), shuffle_info\n'.format(', '.
        join(f'out_key{bpjt__lvesf}' for bpjt__lvesf in range(rpb__gqf)))
    pzwb__oixhl = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    pzwb__oixhl.update({f'keys{bpjt__lvesf}_typ': keys.types[bpjt__lvesf] for
        bpjt__lvesf in range(rpb__gqf)})
    pzwb__oixhl.update({f'in_arr{bpjt__lvesf}_typ': df.data[bpjt__lvesf] for
        bpjt__lvesf in range(fzsv__rec)})
    wgfs__imk = {}
    exec(ufduo__ohghg, pzwb__oixhl, wgfs__imk)
    kydmd__ijuwk = wgfs__imk['impl']
    return kydmd__ijuwk, pzwb__oixhl


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        nqp__czup = len(data.array_types)
        ufduo__ohghg = 'def impl(data, shuffle_info):\n'
        ufduo__ohghg += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{bpjt__lvesf}])' for bpjt__lvesf in
            range(nqp__czup)))
        ufduo__ohghg += '  table = arr_info_list_to_table(info_list)\n'
        ufduo__ohghg += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for bpjt__lvesf in range(nqp__czup):
            ufduo__ohghg += f"""  out_arr{bpjt__lvesf} = info_to_array(info_from_table(out_table, {bpjt__lvesf}), data._data[{bpjt__lvesf}])
"""
        ufduo__ohghg += '  delete_table(out_table)\n'
        ufduo__ohghg += '  delete_table(table)\n'
        ufduo__ohghg += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{bpjt__lvesf}' for bpjt__lvesf in
            range(nqp__czup))))
        wgfs__imk = {}
        exec(ufduo__ohghg, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, wgfs__imk)
        kydmd__ijuwk = wgfs__imk['impl']
        return kydmd__ijuwk
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            wfv__rbp = bodo.utils.conversion.index_to_array(data)
            qlf__cwuj = reverse_shuffle(wfv__rbp, shuffle_info)
            return bodo.utils.conversion.index_from_array(qlf__cwuj)
        return impl_index

    def impl_arr(data, shuffle_info):
        zhxy__ubn = [array_to_info(data)]
        zqj__yuy = arr_info_list_to_table(zhxy__ubn)
        yon__jicd = reverse_shuffle_table(zqj__yuy, shuffle_info)
        qlf__cwuj = info_to_array(info_from_table(yon__jicd, 0), data)
        delete_table(yon__jicd)
        delete_table(zqj__yuy)
        return qlf__cwuj
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    pkaxx__irby = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna
        )
    wmpmc__kmi = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', pkaxx__irby, wmpmc__kmi,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    idugp__rzm = get_overload_const_bool(ascending)
    njgzv__eizeo = grp.selection[0]
    ufduo__ohghg = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    whly__zzqgi = (
        f"lambda S: S.value_counts(ascending={idugp__rzm}, _index_name='{njgzv__eizeo}')"
        )
    ufduo__ohghg += f'    return grp.apply({whly__zzqgi})\n'
    wgfs__imk = {}
    exec(ufduo__ohghg, {'bodo': bodo}, wgfs__imk)
    kydmd__ijuwk = wgfs__imk['impl']
    return kydmd__ijuwk


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
    for ooi__ctkwg in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, ooi__ctkwg, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{ooi__ctkwg}'))
    for ooi__ctkwg in groupby_unsupported:
        overload_method(DataFrameGroupByType, ooi__ctkwg, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{ooi__ctkwg}'))
    for ooi__ctkwg in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, ooi__ctkwg, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{ooi__ctkwg}'))
    for ooi__ctkwg in series_only_unsupported:
        overload_method(DataFrameGroupByType, ooi__ctkwg, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{ooi__ctkwg}'))
    for ooi__ctkwg in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, ooi__ctkwg, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{ooi__ctkwg}'))


_install_groupby_unsupported()
