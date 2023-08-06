import datetime
import operator
import warnings
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_constant
from numba.core.typing.templates import AttributeTemplate, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
import bodo.hiframes
import bodo.utils.conversion
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_func, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_udf_error_msg, get_udf_out_arr_type, get_val_type_maybe_str_literal, is_const_func_type, is_heterogeneous_tuple_type, is_iterable_type, is_overload_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_nan, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
from bodo.utils.utils import is_null_value
_dt_index_data_typ = types.Array(types.NPDatetime('ns'), 1, 'C')
_timedelta_index_data_typ = types.Array(types.NPTimedelta('ns'), 1, 'C')
iNaT = pd._libs.tslibs.iNaT
NaT = types.NPDatetime('ns')('NaT')
idx_cpy_arg_defaults = dict(deep=False, dtype=None, names=None)
idx_typ_to_format_str_map = dict()


@typeof_impl.register(pd.Index)
def typeof_pd_index(val, c):
    if val.inferred_type == 'string' or pd._libs.lib.infer_dtype(val, True
        ) == 'string':
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'bytes' or pd._libs.lib.infer_dtype(val, True
        ) == 'bytes':
        return BinaryIndexType(get_val_type_maybe_str_literal(val.name))
    if val.equals(pd.Index([])):
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'date':
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'integer' or pd._libs.lib.infer_dtype(val, True
        ) == 'integer':
        if isinstance(val.dtype, pd.core.arrays.integer._IntegerDtype):
            gsm__tjt = val.dtype.numpy_dtype
            dtype = numba.np.numpy_support.from_dtype(gsm__tjt)
        else:
            dtype = types.int64
        return NumericIndexType(dtype, get_val_type_maybe_str_literal(val.
            name), IntegerArrayType(dtype))
    if val.inferred_type == 'boolean' or pd._libs.lib.infer_dtype(val, True
        ) == 'boolean':
        return NumericIndexType(types.bool_, get_val_type_maybe_str_literal
            (val.name), boolean_array)
    raise NotImplementedError(f'unsupported pd.Index type {val}')


class DatetimeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.datetime64ns, 1, 'C'
            ) if data is None else data
        super(DatetimeIndexType, self).__init__(name=
            f'DatetimeIndex({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def tzval(self):
        return self.data.tz if isinstance(self.data, bodo.DatetimeArrayType
            ) else None

    def copy(self):
        return DatetimeIndexType(self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.hiframes.
            pd_timestamp_ext.PandasTimestampType(self.tzval))

    @property
    def pandas_type_name(self):
        return self.data.dtype.type_name

    @property
    def numpy_type_name(self):
        return str(self.data.dtype)


types.datetime_index = DatetimeIndexType()


@typeof_impl.register(pd.DatetimeIndex)
def typeof_datetime_index(val, c):
    if isinstance(val.dtype, pd.DatetimeTZDtype):
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name),
            DatetimeArrayType(val.tz))
    return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(DatetimeIndexType)
class DatetimeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(_dt_index_data_typ.dtype, types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, tbe__yyb)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    pefwt__inf = dict(deep=deep, dtype=dtype, names=names)
    jfi__neahh = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()')
    check_unsupported_args('copy', pefwt__inf, idx_cpy_arg_defaults, fn_str
        =jfi__neahh, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), A._name)
    return impl


@box(DatetimeIndexType)
def box_dt_index(typ, val, c):
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    uqk__pvpe = c.pyapi.import_module_noblock(hpy__ngo)
    gnyhl__hsa = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, gnyhl__hsa.data)
    wpnz__jwqr = c.pyapi.from_native_value(typ.data, gnyhl__hsa.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, gnyhl__hsa.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, gnyhl__hsa.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([wpnz__jwqr])
    bmhn__eil = c.pyapi.object_getattr_string(uqk__pvpe, 'DatetimeIndex')
    kws = c.pyapi.dict_pack([('name', gkan__mcd)])
    vyifq__epqxp = c.pyapi.call(bmhn__eil, args, kws)
    c.pyapi.decref(wpnz__jwqr)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(uqk__pvpe)
    c.pyapi.decref(bmhn__eil)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return vyifq__epqxp


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        ousir__tbnzj = c.pyapi.object_getattr_string(val, 'array')
    else:
        ousir__tbnzj = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, ousir__tbnzj).value
    gkan__mcd = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gkan__mcd).value
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wgxui__swb.data = data
    wgxui__swb.name = name
    dtype = _dt_index_data_typ.dtype
    ncsxu__wkh, tgqv__qimu = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    wgxui__swb.dict = tgqv__qimu
    c.pyapi.decref(ousir__tbnzj)
    c.pyapi.decref(gkan__mcd)
    return NativeValue(wgxui__swb._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        zgrf__nprdf, nflrl__wrql = args
        gnyhl__hsa = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        gnyhl__hsa.data = zgrf__nprdf
        gnyhl__hsa.name = nflrl__wrql
        context.nrt.incref(builder, signature.args[0], zgrf__nprdf)
        context.nrt.incref(builder, signature.args[1], nflrl__wrql)
        dtype = _dt_index_data_typ.dtype
        gnyhl__hsa.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return gnyhl__hsa._getvalue()
    dwge__ian = DatetimeIndexType(name, data)
    sig = signature(dwge__ian, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    udfo__qvqfx = args[0]
    if equiv_set.has_shape(udfo__qvqfx):
        return ArrayAnalysis.AnalyzeResult(shape=udfo__qvqfx, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    yghmj__qmoxo = 'def impl(dti):\n'
    yghmj__qmoxo += '    numba.parfors.parfor.init_prange()\n'
    yghmj__qmoxo += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    yghmj__qmoxo += (
        '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n')
    yghmj__qmoxo += '    n = len(A)\n'
    yghmj__qmoxo += '    S = np.empty(n, np.int64)\n'
    yghmj__qmoxo += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    yghmj__qmoxo += '        val = A[i]\n'
    yghmj__qmoxo += '        ts = bodo.utils.conversion.box_if_dt64(val)\n'
    if field in ['weekday']:
        yghmj__qmoxo += '        S[i] = ts.' + field + '()\n'
    else:
        yghmj__qmoxo += '        S[i] = ts.' + field + '\n'
    yghmj__qmoxo += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'numba': numba, 'np': np, 'bodo': bodo}, kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


def _install_dti_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        if field in ['is_leap_year']:
            continue
        impl = gen_dti_field_impl(field)
        overload_attribute(DatetimeIndexType, field)(lambda dti: impl)


_install_dti_date_fields()


@overload_attribute(DatetimeIndexType, 'is_leap_year')
def overload_datetime_index_is_leap_year(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        ojmdy__rqxb = len(A)
        S = np.empty(ojmdy__rqxb, np.bool_)
        for i in numba.parfors.parfor.internal_prange(ojmdy__rqxb):
            val = A[i]
            sfgn__mgpzv = bodo.utils.conversion.box_if_dt64(val)
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(sfgn__mgpzv.year
                )
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        ojmdy__rqxb = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            ojmdy__rqxb)
        for i in numba.parfors.parfor.internal_prange(ojmdy__rqxb):
            val = A[i]
            sfgn__mgpzv = bodo.utils.conversion.box_if_dt64(val)
            S[i] = datetime.date(sfgn__mgpzv.year, sfgn__mgpzv.month,
                sfgn__mgpzv.day)
        return S
    return impl


@numba.njit(no_cpython_wrapper=True)
def _dti_val_finalize(s, count):
    if not count:
        s = iNaT
    return bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(s)


@numba.njit(no_cpython_wrapper=True)
def _tdi_val_finalize(s, count):
    return pd.Timedelta('nan') if not count else pd.Timedelta(s)


@overload_method(DatetimeIndexType, 'min', no_unliteral=True)
def overload_datetime_index_min(dti, axis=None, skipna=True):
    lqtbn__vgbyf = dict(axis=axis, skipna=skipna)
    adb__uebz = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.min()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        dred__fdx = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(dred__fdx)):
            if not bodo.libs.array_kernels.isna(dred__fdx, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(dred__fdx
                    [i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    lqtbn__vgbyf = dict(axis=axis, skipna=skipna)
    adb__uebz = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.max()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        dred__fdx = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(dred__fdx)):
            if not bodo.libs.array_kernels.isna(dred__fdx, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(dred__fdx
                    [i])
                s = max(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'tz_convert', no_unliteral=True)
def overload_pd_datetime_tz_convert(A, tz):

    def impl(A, tz):
        return init_datetime_index(A._data.tz_convert(tz), A._name)
    return impl


@infer_getattr
class DatetimeIndexAttribute(AttributeTemplate):
    key = DatetimeIndexType

    def resolve_values(self, ary):
        return _dt_index_data_typ


@overload(pd.DatetimeIndex, no_unliteral=True)
def pd_datetimeindex_overload(data=None, freq=None, tz=None, normalize=
    False, closed=None, ambiguous='raise', dayfirst=False, yearfirst=False,
    dtype=None, copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.DatetimeIndex() expected')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.DatetimeIndex()')
    lqtbn__vgbyf = dict(freq=freq, tz=tz, normalize=normalize, closed=
        closed, ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst,
        dtype=dtype, copy=copy)
    adb__uebz = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        eptta__ytdfw = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(eptta__ytdfw)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        xwja__kocd = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            dred__fdx = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            ojmdy__rqxb = len(dred__fdx)
            S = np.empty(ojmdy__rqxb, xwja__kocd)
            vne__ytnjc = rhs.value
            for i in numba.parfors.parfor.internal_prange(ojmdy__rqxb):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    dred__fdx[i]) - vne__ytnjc)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        xwja__kocd = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            dred__fdx = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            ojmdy__rqxb = len(dred__fdx)
            S = np.empty(ojmdy__rqxb, xwja__kocd)
            vne__ytnjc = lhs.value
            for i in numba.parfors.parfor.internal_prange(ojmdy__rqxb):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    vne__ytnjc - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(dred__fdx[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    bpltw__gqdl = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    yghmj__qmoxo = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        yghmj__qmoxo += '  dt_index, _str = lhs, rhs\n'
        xqc__ejtn = 'arr[i] {} other'.format(bpltw__gqdl)
    else:
        yghmj__qmoxo += '  dt_index, _str = rhs, lhs\n'
        xqc__ejtn = 'other {} arr[i]'.format(bpltw__gqdl)
    yghmj__qmoxo += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    yghmj__qmoxo += '  l = len(arr)\n'
    yghmj__qmoxo += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    yghmj__qmoxo += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    yghmj__qmoxo += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    yghmj__qmoxo += '    S[i] = {}\n'.format(xqc__ejtn)
    yghmj__qmoxo += '  return S\n'
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'bodo': bodo, 'numba': numba, 'np': np}, kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


def overload_binop_dti_str(op):

    def overload_impl(lhs, rhs):
        if isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, True)
        if isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, False)
    return overload_impl


@overload(pd.Index, inline='always', no_unliteral=True)
def pd_index_overload(data=None, dtype=None, copy=False, name=None,
    tupleize_cols=True):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.Index()')
    data = types.unliteral(data) if not isinstance(data, types.LiteralList
        ) else data
    if not is_overload_none(dtype):
        vgmj__hrpb = parse_dtype(dtype, 'pandas.Index')
        rmzp__czx = False
    else:
        vgmj__hrpb = getattr(data, 'dtype', None)
        rmzp__czx = True
    if isinstance(vgmj__hrpb, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or vgmj__hrpb == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType
        ) or vgmj__hrpb == types.NPTimedelta('ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.TimedeltaIndex(data, name=name)
    elif is_heterogeneous_tuple_type(data):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return bodo.hiframes.pd_index_ext.init_heter_index(data, name)
        return impl
    elif bodo.utils.utils.is_array_typ(data, False) or isinstance(data, (
        SeriesType, types.List, types.UniTuple)):
        if isinstance(vgmj__hrpb, (types.Integer, types.Float, types.Boolean)):
            if rmzp__czx:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    eptta__ytdfw = bodo.utils.conversion.coerce_to_array(data)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        eptta__ytdfw, name)
            else:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    eptta__ytdfw = bodo.utils.conversion.coerce_to_array(data)
                    lrot__ikb = bodo.utils.conversion.fix_arr_dtype(
                        eptta__ytdfw, vgmj__hrpb)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        lrot__ikb, name)
        elif vgmj__hrpb in [types.string, bytes_type]:

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                return bodo.hiframes.pd_index_ext.init_binary_str_index(bodo
                    .utils.conversion.coerce_to_array(data), name)
        else:
            raise BodoError(
                'pd.Index(): provided array is of unsupported type.')
    elif is_overload_none(data):
        raise BodoError(
            'data argument in pd.Index() is invalid: None or scalar is not acceptable'
            )
    else:
        raise BodoError(
            f'pd.Index(): the provided argument type {data} is not supported')
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_datetime_index_getitem(dti, ind):
    if isinstance(dti, DatetimeIndexType):
        if isinstance(ind, types.Integer):

            def impl(dti, ind):
                yhz__bmfmc = bodo.hiframes.pd_index_ext.get_index_data(dti)
                val = yhz__bmfmc[ind]
                return bodo.utils.conversion.box_if_dt64(val)
            return impl
        else:

            def impl(dti, ind):
                yhz__bmfmc = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                fdg__skksm = yhz__bmfmc[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(
                    fdg__skksm, name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            mtqx__uhwkk = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(mtqx__uhwkk[ind])
        return impl

    def impl(I, ind):
        mtqx__uhwkk = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        fdg__skksm = mtqx__uhwkk[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(fdg__skksm, name
            )
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_categorical_index_getitem(I, ind):
    if not isinstance(I, CategoricalIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            frjvl__jta = bodo.hiframes.pd_index_ext.get_index_data(I)
            val = frjvl__jta[ind]
            return val
        return impl
    if isinstance(ind, types.SliceType):

        def impl(I, ind):
            frjvl__jta = bodo.hiframes.pd_index_ext.get_index_data(I)
            name = bodo.hiframes.pd_index_ext.get_index_name(I)
            fdg__skksm = frjvl__jta[ind]
            return bodo.hiframes.pd_index_ext.init_categorical_index(fdg__skksm
                , name)
        return impl
    raise BodoError(
        f'pd.CategoricalIndex.__getitem__: unsupported index type {ind}')


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    jgmh__zkz = False
    aiohv__oqw = False
    if closed is None:
        jgmh__zkz = True
        aiohv__oqw = True
    elif closed == 'left':
        jgmh__zkz = True
    elif closed == 'right':
        aiohv__oqw = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return jgmh__zkz, aiohv__oqw


@numba.njit(no_cpython_wrapper=True)
def to_offset_value(freq):
    if freq is None:
        return None
    with numba.objmode(r='int64'):
        r = pd.tseries.frequencies.to_offset(freq).nanos
    return r


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _dummy_convert_none_to_int(val):
    if is_overload_none(val):

        def impl(val):
            return 0
        return impl
    if isinstance(val, types.Optional):

        def impl(val):
            if val is None:
                return 0
            return bodo.utils.indexing.unoptional(val)
        return impl
    return lambda val: val


@overload(pd.date_range, inline='always')
def pd_date_range_overload(start=None, end=None, periods=None, freq=None,
    tz=None, normalize=False, name=None, closed=None):
    lqtbn__vgbyf = dict(tz=tz, normalize=normalize, closed=closed)
    adb__uebz = dict(tz=None, normalize=False, closed=None)
    check_unsupported_args('pandas.date_range', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise_bodo_error('pd.date_range(): tz argument not supported yet')
    ljxck__lulxp = ''
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
        ljxck__lulxp = "  freq = 'D'\n"
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise_bodo_error(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )
    yghmj__qmoxo = """def f(start=None, end=None, periods=None, freq=None, tz=None, normalize=False, name=None, closed=None):
"""
    yghmj__qmoxo += ljxck__lulxp
    if is_overload_none(start):
        yghmj__qmoxo += "  start_t = pd.Timestamp('1800-01-03')\n"
    else:
        yghmj__qmoxo += '  start_t = pd.Timestamp(start)\n'
    if is_overload_none(end):
        yghmj__qmoxo += "  end_t = pd.Timestamp('1800-01-03')\n"
    else:
        yghmj__qmoxo += '  end_t = pd.Timestamp(end)\n'
    if not is_overload_none(freq):
        yghmj__qmoxo += (
            '  stride = bodo.hiframes.pd_index_ext.to_offset_value(freq)\n')
        if is_overload_none(periods):
            yghmj__qmoxo += '  b = start_t.value\n'
            yghmj__qmoxo += (
                '  e = b + (end_t.value - b) // stride * stride + stride // 2 + 1\n'
                )
        elif not is_overload_none(start):
            yghmj__qmoxo += '  b = start_t.value\n'
            yghmj__qmoxo += '  addend = np.int64(periods) * np.int64(stride)\n'
            yghmj__qmoxo += '  e = np.int64(b) + addend\n'
        elif not is_overload_none(end):
            yghmj__qmoxo += '  e = end_t.value + stride\n'
            yghmj__qmoxo += (
                '  addend = np.int64(periods) * np.int64(-stride)\n')
            yghmj__qmoxo += '  b = np.int64(e) + addend\n'
        else:
            raise_bodo_error(
                "at least 'start' or 'end' should be specified if a 'period' is given."
                )
        yghmj__qmoxo += '  arr = np.arange(b, e, stride, np.int64)\n'
    else:
        yghmj__qmoxo += '  delta = end_t.value - start_t.value\n'
        yghmj__qmoxo += '  step = delta / (periods - 1)\n'
        yghmj__qmoxo += '  arr1 = np.arange(0, periods, 1, np.float64)\n'
        yghmj__qmoxo += '  arr1 *= step\n'
        yghmj__qmoxo += '  arr1 += start_t.value\n'
        yghmj__qmoxo += '  arr = arr1.astype(np.int64)\n'
        yghmj__qmoxo += '  arr[-1] = end_t.value\n'
    yghmj__qmoxo += '  A = bodo.utils.conversion.convert_to_dt64ns(arr)\n'
    yghmj__qmoxo += (
        '  return bodo.hiframes.pd_index_ext.init_datetime_index(A, name)\n')
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'bodo': bodo, 'np': np, 'pd': pd}, kqik__vrd)
    f = kqik__vrd['f']
    return f


@overload(pd.timedelta_range, no_unliteral=True)
def pd_timedelta_range_overload(start=None, end=None, periods=None, freq=
    None, name=None, closed=None):
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, name=None, closed=None
        ):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        rzt__rvxaw = pd.Timedelta('1 day')
        if start is not None:
            rzt__rvxaw = pd.Timedelta(start)
        rmm__fmvtt = pd.Timedelta('1 day')
        if end is not None:
            rmm__fmvtt = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        jgmh__zkz, aiohv__oqw = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            ddpfn__oiajd = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = rzt__rvxaw.value
                cwc__vmp = b + (rmm__fmvtt.value - b
                    ) // ddpfn__oiajd * ddpfn__oiajd + ddpfn__oiajd // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = rzt__rvxaw.value
                hfm__wfuu = np.int64(periods) * np.int64(ddpfn__oiajd)
                cwc__vmp = np.int64(b) + hfm__wfuu
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                cwc__vmp = rmm__fmvtt.value + ddpfn__oiajd
                hfm__wfuu = np.int64(periods) * np.int64(-ddpfn__oiajd)
                b = np.int64(cwc__vmp) + hfm__wfuu
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            fxeys__lkvm = np.arange(b, cwc__vmp, ddpfn__oiajd, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            mbobi__uvb = rmm__fmvtt.value - rzt__rvxaw.value
            step = mbobi__uvb / (periods - 1)
            yplo__rog = np.arange(0, periods, 1, np.float64)
            yplo__rog *= step
            yplo__rog += rzt__rvxaw.value
            fxeys__lkvm = yplo__rog.astype(np.int64)
            fxeys__lkvm[-1] = rmm__fmvtt.value
        if not jgmh__zkz and len(fxeys__lkvm) and fxeys__lkvm[0
            ] == rzt__rvxaw.value:
            fxeys__lkvm = fxeys__lkvm[1:]
        if not aiohv__oqw and len(fxeys__lkvm) and fxeys__lkvm[-1
            ] == rmm__fmvtt.value:
            fxeys__lkvm = fxeys__lkvm[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(fxeys__lkvm)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):
    qbfm__zwv = ColNamesMetaType(('year', 'week', 'day'))

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        ojmdy__rqxb = len(A)
        gpjm__utwbv = bodo.libs.int_arr_ext.alloc_int_array(ojmdy__rqxb, np
            .uint32)
        wbthy__yfv = bodo.libs.int_arr_ext.alloc_int_array(ojmdy__rqxb, np.
            uint32)
        yvx__ycu = bodo.libs.int_arr_ext.alloc_int_array(ojmdy__rqxb, np.uint32
            )
        for i in numba.parfors.parfor.internal_prange(ojmdy__rqxb):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(gpjm__utwbv, i)
                bodo.libs.array_kernels.setna(wbthy__yfv, i)
                bodo.libs.array_kernels.setna(yvx__ycu, i)
                continue
            gpjm__utwbv[i], wbthy__yfv[i], yvx__ycu[i
                ] = bodo.utils.conversion.box_if_dt64(A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((gpjm__utwbv,
            wbthy__yfv, yvx__ycu), idx, qbfm__zwv)
    return impl


class TimedeltaIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.timedelta64ns, 1, 'C'
            ) if data is None else data
        super(TimedeltaIndexType, self).__init__(name=
            f'TimedeltaIndexType({name_typ}, {self.data})')
    ndim = 1

    def copy(self):
        return TimedeltaIndexType(self.name_typ)

    @property
    def dtype(self):
        return types.NPTimedelta('ns')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.pd_timedelta_type
            )

    @property
    def pandas_type_name(self):
        return 'timedelta'

    @property
    def numpy_type_name(self):
        return 'timedelta64[ns]'


timedelta_index = TimedeltaIndexType()
types.timedelta_index = timedelta_index


@register_model(TimedeltaIndexType)
class TimedeltaIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('data', _timedelta_index_data_typ), ('name', fe_type.
            name_typ), ('dict', types.DictType(_timedelta_index_data_typ.
            dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, tbe__yyb)


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    uqk__pvpe = c.pyapi.import_module_noblock(hpy__ngo)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    wpnz__jwqr = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([wpnz__jwqr])
    kws = c.pyapi.dict_pack([('name', gkan__mcd)])
    bmhn__eil = c.pyapi.object_getattr_string(uqk__pvpe, 'TimedeltaIndex')
    vyifq__epqxp = c.pyapi.call(bmhn__eil, args, kws)
    c.pyapi.decref(wpnz__jwqr)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(uqk__pvpe)
    c.pyapi.decref(bmhn__eil)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return vyifq__epqxp


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    wup__dgwy = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, wup__dgwy).value
    gkan__mcd = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gkan__mcd).value
    c.pyapi.decref(wup__dgwy)
    c.pyapi.decref(gkan__mcd)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wgxui__swb.data = data
    wgxui__swb.name = name
    dtype = _timedelta_index_data_typ.dtype
    ncsxu__wkh, tgqv__qimu = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    wgxui__swb.dict = tgqv__qimu
    return NativeValue(wgxui__swb._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        zgrf__nprdf, nflrl__wrql = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = zgrf__nprdf
        timedelta_index.name = nflrl__wrql
        context.nrt.incref(builder, signature.args[0], zgrf__nprdf)
        context.nrt.incref(builder, signature.args[1], nflrl__wrql)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    dwge__ian = TimedeltaIndexType(name)
    sig = signature(dwge__ian, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_timedelta_index
    ) = init_index_equiv


@infer_getattr
class TimedeltaIndexAttribute(AttributeTemplate):
    key = TimedeltaIndexType

    def resolve_values(self, ary):
        return _timedelta_index_data_typ


make_attribute_wrapper(TimedeltaIndexType, 'data', '_data')
make_attribute_wrapper(TimedeltaIndexType, 'name', '_name')
make_attribute_wrapper(TimedeltaIndexType, 'dict', '_dict')


@overload_method(TimedeltaIndexType, 'copy', no_unliteral=True)
def overload_timedelta_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    pefwt__inf = dict(deep=deep, dtype=dtype, names=names)
    jfi__neahh = idx_typ_to_format_str_map[TimedeltaIndexType].format('copy()')
    check_unsupported_args('TimedeltaIndex.copy', pefwt__inf,
        idx_cpy_arg_defaults, fn_str=jfi__neahh, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), A._name)
    return impl


@overload_method(TimedeltaIndexType, 'min', inline='always', no_unliteral=True)
def overload_timedelta_index_min(tdi, axis=None, skipna=True):
    lqtbn__vgbyf = dict(axis=axis, skipna=skipna)
    adb__uebz = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        ojmdy__rqxb = len(data)
        rhgsm__vughd = numba.cpython.builtins.get_type_max_value(numba.core
            .types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(ojmdy__rqxb):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            rhgsm__vughd = min(rhgsm__vughd, val)
        lgpmr__ekt = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            rhgsm__vughd)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(lgpmr__ekt, count)
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    lqtbn__vgbyf = dict(axis=axis, skipna=skipna)
    adb__uebz = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        ojmdy__rqxb = len(data)
        nmw__mfc = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(ojmdy__rqxb):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            nmw__mfc = max(nmw__mfc, val)
        lgpmr__ekt = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            nmw__mfc)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(lgpmr__ekt, count)
    return impl


def gen_tdi_field_impl(field):
    yghmj__qmoxo = 'def impl(tdi):\n'
    yghmj__qmoxo += '    numba.parfors.parfor.init_prange()\n'
    yghmj__qmoxo += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    yghmj__qmoxo += (
        '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n')
    yghmj__qmoxo += '    n = len(A)\n'
    yghmj__qmoxo += '    S = np.empty(n, np.int64)\n'
    yghmj__qmoxo += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    yghmj__qmoxo += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        yghmj__qmoxo += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        yghmj__qmoxo += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        yghmj__qmoxo += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        yghmj__qmoxo += (
            '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
    else:
        assert False, 'invalid timedelta field'
    yghmj__qmoxo += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'numba': numba, 'np': np, 'bodo': bodo}, kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


def _install_tdi_time_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        impl = gen_tdi_field_impl(field)
        overload_attribute(TimedeltaIndexType, field)(lambda tdi: impl)


_install_tdi_time_fields()


@overload(pd.TimedeltaIndex, no_unliteral=True)
def pd_timedelta_index_overload(data=None, unit=None, freq=None, dtype=None,
    copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.TimedeltaIndex() expected')
    lqtbn__vgbyf = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    adb__uebz = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        eptta__ytdfw = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(eptta__ytdfw)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return impl


class RangeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        if name_typ is None:
            name_typ = types.none
        self.name_typ = name_typ
        super(RangeIndexType, self).__init__(name=f'RangeIndexType({name_typ})'
            )
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return RangeIndexType(self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.RangeIteratorType(types.int64)

    @property
    def dtype(self):
        return types.int64

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)

    def unify(self, typingctx, other):
        if isinstance(other, NumericIndexType):
            name_typ = self.name_typ.unify(typingctx, other.name_typ)
            if name_typ is None:
                name_typ = types.none
            return NumericIndexType(types.int64, name_typ)


@typeof_impl.register(pd.RangeIndex)
def typeof_pd_range_index(val, c):
    return RangeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(RangeIndexType)
class RangeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('start', types.int64), ('stop', types.int64), ('step',
            types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, tbe__yyb)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    pefwt__inf = dict(deep=deep, dtype=dtype, names=names)
    jfi__neahh = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', pefwt__inf,
        idx_cpy_arg_defaults, fn_str=jfi__neahh, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, A._name)
    return impl


@box(RangeIndexType)
def box_range_index(typ, val, c):
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    yhv__awjk = c.pyapi.import_module_noblock(hpy__ngo)
    xpb__enua = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    qoxun__rrao = c.pyapi.from_native_value(types.int64, xpb__enua.start, c
        .env_manager)
    ozipf__tsaa = c.pyapi.from_native_value(types.int64, xpb__enua.stop, c.
        env_manager)
    kfb__ugu = c.pyapi.from_native_value(types.int64, xpb__enua.step, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, xpb__enua.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, xpb__enua.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([qoxun__rrao, ozipf__tsaa, kfb__ugu])
    kws = c.pyapi.dict_pack([('name', gkan__mcd)])
    bmhn__eil = c.pyapi.object_getattr_string(yhv__awjk, 'RangeIndex')
    axu__osght = c.pyapi.call(bmhn__eil, args, kws)
    c.pyapi.decref(qoxun__rrao)
    c.pyapi.decref(ozipf__tsaa)
    c.pyapi.decref(kfb__ugu)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(yhv__awjk)
    c.pyapi.decref(bmhn__eil)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return axu__osght


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name
    rpfim__etms = is_overload_constant_int(step) and get_overload_const_int(
        step) == 0

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        if rpfim__etms:
            raise_bodo_error('Step must not be zero')
        akv__mdue = cgutils.is_scalar_zero(builder, args[2])
        eiiqv__mxbs = context.get_python_api(builder)
        with builder.if_then(akv__mdue):
            eiiqv__mxbs.err_format('PyExc_ValueError', 'Step must not be zero')
            val = context.get_constant(types.int32, -1)
            builder.ret(val)
        xpb__enua = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        xpb__enua.start = args[0]
        xpb__enua.stop = args[1]
        xpb__enua.step = args[2]
        xpb__enua.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return xpb__enua._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, dzze__doqk = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    qoxun__rrao = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, qoxun__rrao).value
    ozipf__tsaa = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, ozipf__tsaa).value
    kfb__ugu = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, kfb__ugu).value
    gkan__mcd = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gkan__mcd).value
    c.pyapi.decref(qoxun__rrao)
    c.pyapi.decref(ozipf__tsaa)
    c.pyapi.decref(kfb__ugu)
    c.pyapi.decref(gkan__mcd)
    xpb__enua = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xpb__enua.start = start
    xpb__enua.stop = stop
    xpb__enua.step = step
    xpb__enua.name = name
    return NativeValue(xpb__enua._getvalue())


@lower_constant(RangeIndexType)
def lower_constant_range_index(context, builder, ty, pyval):
    start = context.get_constant(types.int64, pyval.start)
    stop = context.get_constant(types.int64, pyval.stop)
    step = context.get_constant(types.int64, pyval.step)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    return lir.Constant.literal_struct([start, stop, step, name])


@overload(pd.RangeIndex, no_unliteral=True, inline='always')
def range_index_overload(start=None, stop=None, step=None, dtype=None, copy
    =False, name=None):

    def _ensure_int_or_none(value, field):
        wqe__iuvas = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(wqe__iuvas.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        wqe__iuvas = 'RangeIndex(...) must be called with integers'
        raise BodoError(wqe__iuvas)
    sxsnc__eubjh = 'start'
    qetv__seawt = 'stop'
    lzf__uzeu = 'step'
    if is_overload_none(start):
        sxsnc__eubjh = '0'
    if is_overload_none(stop):
        qetv__seawt = 'start'
        sxsnc__eubjh = '0'
    if is_overload_none(step):
        lzf__uzeu = '1'
    yghmj__qmoxo = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    yghmj__qmoxo += '  return init_range_index({}, {}, {}, name)\n'.format(
        sxsnc__eubjh, qetv__seawt, lzf__uzeu)
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'init_range_index': init_range_index}, kqik__vrd)
    wtum__zhhlj = kqik__vrd['_pd_range_index_imp']
    return wtum__zhhlj


@overload(pd.CategoricalIndex, no_unliteral=True, inline='always')
def categorical_index_overload(data=None, categories=None, ordered=None,
    dtype=None, copy=False, name=None):
    raise BodoError('pd.CategoricalIndex() initializer not yet supported.')


@overload_attribute(RangeIndexType, 'start')
def rangeIndex_get_start(ri):

    def impl(ri):
        return ri._start
    return impl


@overload_attribute(RangeIndexType, 'stop')
def rangeIndex_get_stop(ri):

    def impl(ri):
        return ri._stop
    return impl


@overload_attribute(RangeIndexType, 'step')
def rangeIndex_get_step(ri):

    def impl(ri):
        return ri._step
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_range_index_getitem(I, idx):
    if isinstance(I, RangeIndexType):
        if isinstance(types.unliteral(idx), types.Integer):
            return lambda I, idx: idx * I._step + I._start
        if isinstance(idx, types.SliceType):

            def impl(I, idx):
                rmego__hucov = numba.cpython.unicode._normalize_slice(idx,
                    len(I))
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * rmego__hucov.start
                stop = I._start + I._step * rmego__hucov.stop
                step = I._step * rmego__hucov.step
                return bodo.hiframes.pd_index_ext.init_range_index(start,
                    stop, step, name)
            return impl
        return lambda I, idx: bodo.hiframes.pd_index_ext.init_numeric_index(np
            .arange(I._start, I._stop, I._step, np.int64)[idx], bodo.
            hiframes.pd_index_ext.get_index_name(I))


@overload(len, no_unliteral=True)
def overload_range_len(r):
    if isinstance(r, RangeIndexType):
        return lambda r: max(0, -(-(r._stop - r._start) // r._step))


class PeriodIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, freq, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.freq = freq
        self.name_typ = name_typ
        super(PeriodIndexType, self).__init__(name=
            'PeriodIndexType({}, {})'.format(freq, name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return PeriodIndexType(self.freq, self.name_typ)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'period[{self.freq}]'


@typeof_impl.register(pd.PeriodIndex)
def typeof_pd_period_index(val, c):
    return PeriodIndexType(val.freqstr, get_val_type_maybe_str_literal(val.
        name))


@register_model(PeriodIndexType)
class PeriodIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('data', bodo.IntegerArrayType(types.int64)), ('name',
            fe_type.name_typ), ('dict', types.DictType(types.int64, types.
            int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, tbe__yyb)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    pefwt__inf = dict(deep=deep, dtype=dtype, names=names)
    jfi__neahh = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', pefwt__inf,
        idx_cpy_arg_defaults, fn_str=jfi__neahh, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), name, freq)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), A._name, freq)
    return impl


@intrinsic
def init_period_index(typingctx, data, name, freq):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        zgrf__nprdf, nflrl__wrql, dzze__doqk = args
        rok__opi = signature.return_type
        ssi__ypzng = cgutils.create_struct_proxy(rok__opi)(context, builder)
        ssi__ypzng.data = zgrf__nprdf
        ssi__ypzng.name = nflrl__wrql
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        ssi__ypzng.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return ssi__ypzng._getvalue()
    mnvll__wuum = get_overload_const_str(freq)
    dwge__ian = PeriodIndexType(mnvll__wuum, name)
    sig = signature(dwge__ian, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    yhv__awjk = c.pyapi.import_module_noblock(hpy__ngo)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        wgxui__swb.data)
    ousir__tbnzj = c.pyapi.from_native_value(bodo.IntegerArrayType(types.
        int64), wgxui__swb.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, wgxui__swb.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, wgxui__swb.name, c.
        env_manager)
    ovsr__dlu = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', ousir__tbnzj), ('name', gkan__mcd),
        ('freq', ovsr__dlu)])
    bmhn__eil = c.pyapi.object_getattr_string(yhv__awjk, 'PeriodIndex')
    axu__osght = c.pyapi.call(bmhn__eil, args, kws)
    c.pyapi.decref(ousir__tbnzj)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(ovsr__dlu)
    c.pyapi.decref(yhv__awjk)
    c.pyapi.decref(bmhn__eil)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return axu__osght


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    ubzbf__iionb = c.pyapi.object_getattr_string(val, 'asi8')
    fnlxg__lpdof = c.pyapi.call_method(val, 'isna', ())
    gkan__mcd = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gkan__mcd).value
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    uqk__pvpe = c.pyapi.import_module_noblock(hpy__ngo)
    kozj__lchr = c.pyapi.object_getattr_string(uqk__pvpe, 'arrays')
    ousir__tbnzj = c.pyapi.call_method(kozj__lchr, 'IntegerArray', (
        ubzbf__iionb, fnlxg__lpdof))
    data = c.pyapi.to_native_value(arr_typ, ousir__tbnzj).value
    c.pyapi.decref(ubzbf__iionb)
    c.pyapi.decref(fnlxg__lpdof)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(uqk__pvpe)
    c.pyapi.decref(kozj__lchr)
    c.pyapi.decref(ousir__tbnzj)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wgxui__swb.data = data
    wgxui__swb.name = name
    ncsxu__wkh, tgqv__qimu = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(types.int64, types.int64), types.DictType(types.int64,
        types.int64)(), [])
    wgxui__swb.dict = tgqv__qimu
    return NativeValue(wgxui__swb._getvalue())


class CategoricalIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
        assert isinstance(data, CategoricalArrayType
            ), 'CategoricalIndexType expects CategoricalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(CategoricalIndexType, self).__init__(name=
            f'CategoricalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return CategoricalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'categorical'

    @property
    def numpy_type_name(self):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        return str(get_categories_int_type(self.dtype))

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, self.dtype.elem_type)


@register_model(CategoricalIndexType)
class CategoricalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        wrnx__gpnb = get_categories_int_type(fe_type.data.dtype)
        tbe__yyb = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(wrnx__gpnb, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type, tbe__yyb)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    uqk__pvpe = c.pyapi.import_module_noblock(hpy__ngo)
    edm__pgcr = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, edm__pgcr.data)
    wpnz__jwqr = c.pyapi.from_native_value(typ.data, edm__pgcr.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, edm__pgcr.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, edm__pgcr.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([wpnz__jwqr])
    kws = c.pyapi.dict_pack([('name', gkan__mcd)])
    bmhn__eil = c.pyapi.object_getattr_string(uqk__pvpe, 'CategoricalIndex')
    vyifq__epqxp = c.pyapi.call(bmhn__eil, args, kws)
    c.pyapi.decref(wpnz__jwqr)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(uqk__pvpe)
    c.pyapi.decref(bmhn__eil)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return vyifq__epqxp


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    wup__dgwy = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, wup__dgwy).value
    gkan__mcd = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gkan__mcd).value
    c.pyapi.decref(wup__dgwy)
    c.pyapi.decref(gkan__mcd)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wgxui__swb.data = data
    wgxui__swb.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    ncsxu__wkh, tgqv__qimu = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    wgxui__swb.dict = tgqv__qimu
    return NativeValue(wgxui__swb._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        zgrf__nprdf, nflrl__wrql = args
        edm__pgcr = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        edm__pgcr.data = zgrf__nprdf
        edm__pgcr.name = nflrl__wrql
        context.nrt.incref(builder, signature.args[0], zgrf__nprdf)
        context.nrt.incref(builder, signature.args[1], nflrl__wrql)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        edm__pgcr.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return edm__pgcr._getvalue()
    dwge__ian = CategoricalIndexType(data, name)
    sig = signature(dwge__ian, data, name)
    return sig, codegen


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_categorical_index
    ) = init_index_equiv
make_attribute_wrapper(CategoricalIndexType, 'data', '_data')
make_attribute_wrapper(CategoricalIndexType, 'name', '_name')
make_attribute_wrapper(CategoricalIndexType, 'dict', '_dict')


@overload_method(CategoricalIndexType, 'copy', no_unliteral=True)
def overload_categorical_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    jfi__neahh = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    pefwt__inf = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', pefwt__inf,
        idx_cpy_arg_defaults, fn_str=jfi__neahh, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), A._name)
    return impl


class IntervalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.libs.interval_arr_ext import IntervalArrayType
        assert isinstance(data, IntervalArrayType
            ), 'IntervalIndexType expects IntervalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(IntervalIndexType, self).__init__(name=
            f'IntervalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return IntervalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'interval[{self.data.arr_type.dtype}, right]'


@register_model(IntervalIndexType)
class IntervalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, tbe__yyb)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    uqk__pvpe = c.pyapi.import_module_noblock(hpy__ngo)
    mvbod__buqo = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, mvbod__buqo.data)
    wpnz__jwqr = c.pyapi.from_native_value(typ.data, mvbod__buqo.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, mvbod__buqo.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, mvbod__buqo.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([wpnz__jwqr])
    kws = c.pyapi.dict_pack([('name', gkan__mcd)])
    bmhn__eil = c.pyapi.object_getattr_string(uqk__pvpe, 'IntervalIndex')
    vyifq__epqxp = c.pyapi.call(bmhn__eil, args, kws)
    c.pyapi.decref(wpnz__jwqr)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(uqk__pvpe)
    c.pyapi.decref(bmhn__eil)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return vyifq__epqxp


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    wup__dgwy = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, wup__dgwy).value
    gkan__mcd = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gkan__mcd).value
    c.pyapi.decref(wup__dgwy)
    c.pyapi.decref(gkan__mcd)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wgxui__swb.data = data
    wgxui__swb.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    ncsxu__wkh, tgqv__qimu = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    wgxui__swb.dict = tgqv__qimu
    return NativeValue(wgxui__swb._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        zgrf__nprdf, nflrl__wrql = args
        mvbod__buqo = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        mvbod__buqo.data = zgrf__nprdf
        mvbod__buqo.name = nflrl__wrql
        context.nrt.incref(builder, signature.args[0], zgrf__nprdf)
        context.nrt.incref(builder, signature.args[1], nflrl__wrql)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        mvbod__buqo.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return mvbod__buqo._getvalue()
    dwge__ian = IntervalIndexType(data, name)
    sig = signature(dwge__ian, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_interval_index
    ) = init_index_equiv
make_attribute_wrapper(IntervalIndexType, 'data', '_data')
make_attribute_wrapper(IntervalIndexType, 'name', '_name')
make_attribute_wrapper(IntervalIndexType, 'dict', '_dict')


class NumericIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, dtype, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.dtype = dtype
        self.name_typ = name_typ
        data = dtype_to_array_type(dtype) if data is None else data
        self.data = data
        super(NumericIndexType, self).__init__(name=
            f'NumericIndexType({dtype}, {name_typ}, {data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return NumericIndexType(self.dtype, self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)


with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    Int64Index = pd.Int64Index
    UInt64Index = pd.UInt64Index
    Float64Index = pd.Float64Index


@typeof_impl.register(Int64Index)
def typeof_pd_int64_index(val, c):
    return NumericIndexType(types.int64, get_val_type_maybe_str_literal(val
        .name))


@typeof_impl.register(UInt64Index)
def typeof_pd_uint64_index(val, c):
    return NumericIndexType(types.uint64, get_val_type_maybe_str_literal(
        val.name))


@typeof_impl.register(Float64Index)
def typeof_pd_float64_index(val, c):
    return NumericIndexType(types.float64, get_val_type_maybe_str_literal(
        val.name))


@register_model(NumericIndexType)
class NumericIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, tbe__yyb)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    jfi__neahh = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    pefwt__inf = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', pefwt__inf, idx_cpy_arg_defaults,
        fn_str=jfi__neahh, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(NumericIndexType)
def box_numeric_index(typ, val, c):
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    yhv__awjk = c.pyapi.import_module_noblock(hpy__ngo)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, wgxui__swb.data)
    ousir__tbnzj = c.pyapi.from_native_value(typ.data, wgxui__swb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, wgxui__swb.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, wgxui__swb.name, c.
        env_manager)
    obkt__srzrb = c.pyapi.make_none()
    lpzmx__qamo = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    axu__osght = c.pyapi.call_method(yhv__awjk, 'Index', (ousir__tbnzj,
        obkt__srzrb, lpzmx__qamo, gkan__mcd))
    c.pyapi.decref(ousir__tbnzj)
    c.pyapi.decref(obkt__srzrb)
    c.pyapi.decref(lpzmx__qamo)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(yhv__awjk)
    c.context.nrt.decref(c.builder, typ, val)
    return axu__osght


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        rok__opi = signature.return_type
        wgxui__swb = cgutils.create_struct_proxy(rok__opi)(context, builder)
        wgxui__swb.data = args[0]
        wgxui__swb.name = args[1]
        context.nrt.incref(builder, rok__opi.data, args[0])
        context.nrt.incref(builder, rok__opi.name_typ, args[1])
        dtype = rok__opi.dtype
        wgxui__swb.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return wgxui__swb._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    wup__dgwy = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, wup__dgwy).value
    gkan__mcd = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gkan__mcd).value
    c.pyapi.decref(wup__dgwy)
    c.pyapi.decref(gkan__mcd)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wgxui__swb.data = data
    wgxui__swb.name = name
    dtype = typ.dtype
    ncsxu__wkh, tgqv__qimu = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    wgxui__swb.dict = tgqv__qimu
    return NativeValue(wgxui__swb._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        qvcax__hoah = dict(dtype=dtype)
        ykuu__qfzwf = dict(dtype=None)
        check_unsupported_args(func_str, qvcax__hoah, ykuu__qfzwf,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                eptta__ytdfw = bodo.utils.conversion.coerce_to_ndarray(data)
                sxd__ulshz = bodo.utils.conversion.fix_arr_dtype(eptta__ytdfw,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(sxd__ulshz
                    , name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                eptta__ytdfw = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    eptta__ytdfw = eptta__ytdfw.copy()
                sxd__ulshz = bodo.utils.conversion.fix_arr_dtype(eptta__ytdfw,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(sxd__ulshz
                    , name)
        return impl
    return overload_impl


def _install_numeric_constructors():
    for func, func_str, default_dtype in ((Int64Index, 'pandas.Int64Index',
        np.int64), (UInt64Index, 'pandas.UInt64Index', np.uint64), (
        Float64Index, 'pandas.Float64Index', np.float64)):
        overload_impl = create_numeric_constructor(func, func_str,
            default_dtype)
        overload(func, no_unliteral=True)(overload_impl)


_install_numeric_constructors()


class StringIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = string_array_type if data_typ is None else data_typ
        super(StringIndexType, self).__init__(name=
            f'StringIndexType({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return StringIndexType(self.name_typ, self.data)

    @property
    def dtype(self):
        return string_type

    @property
    def pandas_type_name(self):
        return 'unicode'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(StringIndexType)
class StringIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, tbe__yyb)


make_attribute_wrapper(StringIndexType, 'data', '_data')
make_attribute_wrapper(StringIndexType, 'name', '_name')
make_attribute_wrapper(StringIndexType, 'dict', '_dict')


class BinaryIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        assert data_typ is None or data_typ == binary_array_type, 'data_typ must be binary_array_type'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = binary_array_type
        super(BinaryIndexType, self).__init__(name='BinaryIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return BinaryIndexType(self.name_typ)

    @property
    def dtype(self):
        return bytes_type

    @property
    def pandas_type_name(self):
        return 'bytes'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(BinaryIndexType)
class BinaryIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('data', binary_array_type), ('name', fe_type.name_typ),
            ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, tbe__yyb)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    euo__bhm = typ.data
    scalar_type = typ.data.dtype
    wup__dgwy = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(euo__bhm, wup__dgwy).value
    gkan__mcd = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gkan__mcd).value
    c.pyapi.decref(wup__dgwy)
    c.pyapi.decref(gkan__mcd)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wgxui__swb.data = data
    wgxui__swb.name = name
    ncsxu__wkh, tgqv__qimu = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(scalar_type, types.int64), types.DictType(scalar_type,
        types.int64)(), [])
    wgxui__swb.dict = tgqv__qimu
    return NativeValue(wgxui__swb._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    euo__bhm = typ.data
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    yhv__awjk = c.pyapi.import_module_noblock(hpy__ngo)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, euo__bhm, wgxui__swb.data)
    ousir__tbnzj = c.pyapi.from_native_value(euo__bhm, wgxui__swb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, wgxui__swb.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, wgxui__swb.name, c.
        env_manager)
    obkt__srzrb = c.pyapi.make_none()
    lpzmx__qamo = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    axu__osght = c.pyapi.call_method(yhv__awjk, 'Index', (ousir__tbnzj,
        obkt__srzrb, lpzmx__qamo, gkan__mcd))
    c.pyapi.decref(ousir__tbnzj)
    c.pyapi.decref(obkt__srzrb)
    c.pyapi.decref(lpzmx__qamo)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(yhv__awjk)
    c.context.nrt.decref(c.builder, typ, val)
    return axu__osght


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name,
        data)(data, name)
    krsio__qgydn = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, krsio__qgydn


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        urpf__umkdw = 'bytes_type'
    else:
        urpf__umkdw = 'string_type'
    yghmj__qmoxo = 'def impl(context, builder, signature, args):\n'
    yghmj__qmoxo += '    assert len(args) == 2\n'
    yghmj__qmoxo += '    index_typ = signature.return_type\n'
    yghmj__qmoxo += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    yghmj__qmoxo += '    index_val.data = args[0]\n'
    yghmj__qmoxo += '    index_val.name = args[1]\n'
    yghmj__qmoxo += '    # increase refcount of stored values\n'
    yghmj__qmoxo += (
        '    context.nrt.incref(builder, signature.args[0], args[0])\n')
    yghmj__qmoxo += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    yghmj__qmoxo += '    # create empty dict for get_loc hashmap\n'
    yghmj__qmoxo += '    index_val.dict = context.compile_internal(\n'
    yghmj__qmoxo += '       builder,\n'
    yghmj__qmoxo += (
        f'       lambda: numba.typed.Dict.empty({urpf__umkdw}, types.int64),\n'
        )
    yghmj__qmoxo += (
        f'        types.DictType({urpf__umkdw}, types.int64)(), [],)\n')
    yghmj__qmoxo += '    return index_val._getvalue()\n'
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type}, kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    jfi__neahh = idx_typ_to_format_str_map[typ].format('copy()')
    pefwt__inf = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', pefwt__inf, idx_cpy_arg_defaults,
        fn_str=jfi__neahh, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), A._name)
    return impl


@overload_attribute(BinaryIndexType, 'name')
@overload_attribute(StringIndexType, 'name')
@overload_attribute(DatetimeIndexType, 'name')
@overload_attribute(TimedeltaIndexType, 'name')
@overload_attribute(RangeIndexType, 'name')
@overload_attribute(PeriodIndexType, 'name')
@overload_attribute(NumericIndexType, 'name')
@overload_attribute(IntervalIndexType, 'name')
@overload_attribute(CategoricalIndexType, 'name')
@overload_attribute(MultiIndexType, 'name')
def Index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_index_getitem(I, ind):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType)
        ) and isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, NumericIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_numeric_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))
    if isinstance(I, (StringIndexType, BinaryIndexType)):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_binary_str_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))


def array_type_to_index(arr_typ, name_typ=None):
    if is_str_arr_type(arr_typ):
        return StringIndexType(name_typ, arr_typ)
    if arr_typ == bodo.binary_array_type:
        return BinaryIndexType(name_typ)
    assert isinstance(arr_typ, (types.Array, IntegerArrayType, bodo.
        CategoricalArrayType)) or arr_typ in (bodo.datetime_date_array_type,
        bodo.boolean_array
        ), f'Converting array type {arr_typ} to index not supported'
    if (arr_typ == bodo.datetime_date_array_type or arr_typ.dtype == types.
        NPDatetime('ns')):
        return DatetimeIndexType(name_typ)
    if isinstance(arr_typ, bodo.DatetimeArrayType):
        return DatetimeIndexType(name_typ, arr_typ)
    if isinstance(arr_typ, bodo.CategoricalArrayType):
        return CategoricalIndexType(arr_typ, name_typ)
    if arr_typ.dtype == types.NPTimedelta('ns'):
        return TimedeltaIndexType(name_typ)
    if isinstance(arr_typ.dtype, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(arr_typ.dtype, name_typ, arr_typ)
    raise BodoError(f'invalid index type {arr_typ}')


def is_pd_index_type(t):
    return isinstance(t, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, StringIndexType, BinaryIndexType, RangeIndexType,
        HeterogeneousIndexType))


def _verify_setop_compatible(func_name, I, other):
    if not is_pd_index_type(other) and not isinstance(other, (SeriesType,
        types.Array)):
        raise BodoError(
            f'pd.Index.{func_name}(): unsupported type for argument other: {other}'
            )
    obtw__wzxa = I.dtype if not isinstance(I, RangeIndexType) else types.int64
    zvngf__xuldc = other.dtype if not isinstance(other, RangeIndexType
        ) else types.int64
    if obtw__wzxa != zvngf__xuldc:
        raise BodoError(
            f'Index.{func_name}(): incompatible types {obtw__wzxa} and {zvngf__xuldc}'
            )


@overload_method(NumericIndexType, 'union', inline='always')
@overload_method(StringIndexType, 'union', inline='always')
@overload_method(BinaryIndexType, 'union', inline='always')
@overload_method(DatetimeIndexType, 'union', inline='always')
@overload_method(TimedeltaIndexType, 'union', inline='always')
@overload_method(RangeIndexType, 'union', inline='always')
def overload_index_union(I, other, sort=None):
    lqtbn__vgbyf = dict(sort=sort)
    fedb__merk = dict(sort=None)
    check_unsupported_args('Index.union', lqtbn__vgbyf, fedb__merk,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('union', I, other)
    wyevm__kxc = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        mcdph__pkri = bodo.utils.conversion.coerce_to_array(I)
        thbdu__qywfg = bodo.utils.conversion.coerce_to_array(other)
        rfsv__brhoa = bodo.libs.array_kernels.concat([mcdph__pkri,
            thbdu__qywfg])
        uzkvx__uglik = bodo.libs.array_kernels.unique(rfsv__brhoa)
        return wyevm__kxc(uzkvx__uglik, None)
    return impl


@overload_method(NumericIndexType, 'intersection', inline='always')
@overload_method(StringIndexType, 'intersection', inline='always')
@overload_method(BinaryIndexType, 'intersection', inline='always')
@overload_method(DatetimeIndexType, 'intersection', inline='always')
@overload_method(TimedeltaIndexType, 'intersection', inline='always')
@overload_method(RangeIndexType, 'intersection', inline='always')
def overload_index_intersection(I, other, sort=None):
    lqtbn__vgbyf = dict(sort=sort)
    fedb__merk = dict(sort=None)
    check_unsupported_args('Index.intersection', lqtbn__vgbyf, fedb__merk,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('intersection', I, other)
    wyevm__kxc = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        mcdph__pkri = bodo.utils.conversion.coerce_to_array(I)
        thbdu__qywfg = bodo.utils.conversion.coerce_to_array(other)
        qsb__hjoj = bodo.libs.array_kernels.unique(mcdph__pkri)
        lnbue__mstjt = bodo.libs.array_kernels.unique(thbdu__qywfg)
        rfsv__brhoa = bodo.libs.array_kernels.concat([qsb__hjoj, lnbue__mstjt])
        nyi__zyjdv = pd.Series(rfsv__brhoa).sort_values().values
        jux__dkyf = bodo.libs.array_kernels.intersection_mask(nyi__zyjdv)
        return wyevm__kxc(nyi__zyjdv[jux__dkyf], None)
    return impl


@overload_method(NumericIndexType, 'difference', inline='always')
@overload_method(StringIndexType, 'difference', inline='always')
@overload_method(BinaryIndexType, 'difference', inline='always')
@overload_method(DatetimeIndexType, 'difference', inline='always')
@overload_method(TimedeltaIndexType, 'difference', inline='always')
@overload_method(RangeIndexType, 'difference', inline='always')
def overload_index_difference(I, other, sort=None):
    lqtbn__vgbyf = dict(sort=sort)
    fedb__merk = dict(sort=None)
    check_unsupported_args('Index.difference', lqtbn__vgbyf, fedb__merk,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('difference', I, other)
    wyevm__kxc = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        mcdph__pkri = bodo.utils.conversion.coerce_to_array(I)
        thbdu__qywfg = bodo.utils.conversion.coerce_to_array(other)
        qsb__hjoj = bodo.libs.array_kernels.unique(mcdph__pkri)
        lnbue__mstjt = bodo.libs.array_kernels.unique(thbdu__qywfg)
        jux__dkyf = np.empty(len(qsb__hjoj), np.bool_)
        bodo.libs.array.array_isin(jux__dkyf, qsb__hjoj, lnbue__mstjt, False)
        return wyevm__kxc(qsb__hjoj[~jux__dkyf], None)
    return impl


@overload_method(NumericIndexType, 'symmetric_difference', inline='always')
@overload_method(StringIndexType, 'symmetric_difference', inline='always')
@overload_method(BinaryIndexType, 'symmetric_difference', inline='always')
@overload_method(DatetimeIndexType, 'symmetric_difference', inline='always')
@overload_method(TimedeltaIndexType, 'symmetric_difference', inline='always')
@overload_method(RangeIndexType, 'symmetric_difference', inline='always')
def overload_index_symmetric_difference(I, other, result_name=None, sort=None):
    lqtbn__vgbyf = dict(result_name=result_name, sort=sort)
    fedb__merk = dict(result_name=None, sort=None)
    check_unsupported_args('Index.symmetric_difference', lqtbn__vgbyf,
        fedb__merk, package_name='pandas', module_name='Index')
    _verify_setop_compatible('symmetric_difference', I, other)
    wyevm__kxc = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, result_name=None, sort=None):
        mcdph__pkri = bodo.utils.conversion.coerce_to_array(I)
        thbdu__qywfg = bodo.utils.conversion.coerce_to_array(other)
        qsb__hjoj = bodo.libs.array_kernels.unique(mcdph__pkri)
        lnbue__mstjt = bodo.libs.array_kernels.unique(thbdu__qywfg)
        nkiw__fkzz = np.empty(len(qsb__hjoj), np.bool_)
        pmfs__iftbb = np.empty(len(lnbue__mstjt), np.bool_)
        bodo.libs.array.array_isin(nkiw__fkzz, qsb__hjoj, lnbue__mstjt, False)
        bodo.libs.array.array_isin(pmfs__iftbb, lnbue__mstjt, qsb__hjoj, False)
        lee__zqw = bodo.libs.array_kernels.concat([qsb__hjoj[~nkiw__fkzz],
            lnbue__mstjt[~pmfs__iftbb]])
        return wyevm__kxc(lee__zqw, None)
    return impl


@overload_method(RangeIndexType, 'take', no_unliteral=True)
@overload_method(NumericIndexType, 'take', no_unliteral=True)
@overload_method(StringIndexType, 'take', no_unliteral=True)
@overload_method(BinaryIndexType, 'take', no_unliteral=True)
@overload_method(CategoricalIndexType, 'take', no_unliteral=True)
@overload_method(PeriodIndexType, 'take', no_unliteral=True)
@overload_method(DatetimeIndexType, 'take', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'take', no_unliteral=True)
def overload_index_take(I, indices, axis=0, allow_fill=True, fill_value=None):
    lqtbn__vgbyf = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value
        )
    fedb__merk = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', lqtbn__vgbyf, fedb__merk,
        package_name='pandas', module_name='Index')
    return lambda I, indices: I[indices]


def _init_engine(I, ban_unique=True):
    pass


@overload(_init_engine)
def overload_init_engine(I, ban_unique=True):
    if isinstance(I, CategoricalIndexType):

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                fxeys__lkvm = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(fxeys__lkvm)):
                    if not bodo.libs.array_kernels.isna(fxeys__lkvm, i):
                        val = (bodo.hiframes.pd_categorical_ext.
                            get_code_for_value(fxeys__lkvm.dtype,
                            fxeys__lkvm[i]))
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl
    else:

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                fxeys__lkvm = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(fxeys__lkvm)):
                    if not bodo.libs.array_kernels.isna(fxeys__lkvm, i):
                        val = fxeys__lkvm[i]
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl


@overload(operator.contains, no_unliteral=True)
def index_contains(I, val):
    if not is_index_type(I):
        return
    if isinstance(I, RangeIndexType):
        return lambda I, val: range_contains(I.start, I.stop, I.step, val)
    if isinstance(I, CategoricalIndexType):

        def impl(I, val):
            key = bodo.utils.conversion.unbox_if_timestamp(val)
            if not is_null_value(I._dict):
                _init_engine(I, False)
                fxeys__lkvm = bodo.utils.conversion.coerce_to_array(I)
                pcs__ygi = bodo.hiframes.pd_categorical_ext.get_code_for_value(
                    fxeys__lkvm.dtype, key)
                return pcs__ygi in I._dict
            else:
                wqe__iuvas = (
                    'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                    )
                warnings.warn(wqe__iuvas)
                fxeys__lkvm = bodo.utils.conversion.coerce_to_array(I)
                ind = -1
                for i in range(len(fxeys__lkvm)):
                    if not bodo.libs.array_kernels.isna(fxeys__lkvm, i):
                        if fxeys__lkvm[i] == key:
                            ind = i
            return ind != -1
        return impl

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I, False)
            return key in I._dict
        else:
            wqe__iuvas = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(wqe__iuvas)
            fxeys__lkvm = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(fxeys__lkvm)):
                if not bodo.libs.array_kernels.isna(fxeys__lkvm, i):
                    if fxeys__lkvm[i] == key:
                        ind = i
        return ind != -1
    return impl


@register_jitable
def range_contains(start, stop, step, val):
    if step > 0 and not start <= val < stop:
        return False
    if step < 0 and not stop <= val < start:
        return False
    return (val - start) % step == 0


@overload_method(RangeIndexType, 'get_loc', no_unliteral=True)
@overload_method(NumericIndexType, 'get_loc', no_unliteral=True)
@overload_method(StringIndexType, 'get_loc', no_unliteral=True)
@overload_method(BinaryIndexType, 'get_loc', no_unliteral=True)
@overload_method(PeriodIndexType, 'get_loc', no_unliteral=True)
@overload_method(DatetimeIndexType, 'get_loc', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'get_loc', no_unliteral=True)
def overload_index_get_loc(I, key, method=None, tolerance=None):
    lqtbn__vgbyf = dict(method=method, tolerance=tolerance)
    adb__uebz = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    key = types.unliteral(key)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.get_loc')
    if key == pd_timestamp_type:
        key = bodo.datetime64ns
    if key == pd_timedelta_type:
        key = bodo.timedelta64ns
    if key != I.dtype:
        raise_bodo_error(
            'Index.get_loc(): invalid label type in Index.get_loc()')
    if isinstance(I, RangeIndexType):

        def impl_range(I, key, method=None, tolerance=None):
            if not range_contains(I.start, I.stop, I.step, key):
                raise KeyError('Index.get_loc(): key not found')
            return key - I.start if I.step == 1 else (key - I.start) // I.step
        return impl_range

    def impl(I, key, method=None, tolerance=None):
        key = bodo.utils.conversion.unbox_if_timestamp(key)
        if not is_null_value(I._dict):
            _init_engine(I)
            ind = I._dict.get(key, -1)
        else:
            wqe__iuvas = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(wqe__iuvas)
            fxeys__lkvm = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(fxeys__lkvm)):
                if fxeys__lkvm[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        if ind == -1:
            raise KeyError('Index.get_loc(): key not found')
        return ind
    return impl


def create_isna_specific_method(overload_name):

    def overload_index_isna_specific_method(I):
        dpmot__bcody = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                ojmdy__rqxb = len(I)
                hysz__acydf = np.empty(ojmdy__rqxb, np.bool_)
                for i in numba.parfors.parfor.internal_prange(ojmdy__rqxb):
                    hysz__acydf[i] = not dpmot__bcody
                return hysz__acydf
            return impl
        yghmj__qmoxo = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if dpmot__bcody else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        kqik__vrd = {}
        exec(yghmj__qmoxo, {'bodo': bodo, 'np': np, 'numba': numba}, kqik__vrd)
        impl = kqik__vrd['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for aeclv__qwtl in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(aeclv__qwtl, overload_name, no_unliteral=True,
                inline='always')(overload_impl)


_install_isna_specific_methods()


@overload_attribute(RangeIndexType, 'values')
@overload_attribute(NumericIndexType, 'values')
@overload_attribute(StringIndexType, 'values')
@overload_attribute(BinaryIndexType, 'values')
@overload_attribute(CategoricalIndexType, 'values')
@overload_attribute(PeriodIndexType, 'values')
@overload_attribute(DatetimeIndexType, 'values')
@overload_attribute(TimedeltaIndexType, 'values')
def overload_values(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I, 'Index.values'
        )
    return lambda I: bodo.utils.conversion.coerce_to_array(I)


@overload(len, no_unliteral=True)
def overload_index_len(I):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType,
        PeriodIndexType, IntervalIndexType, CategoricalIndexType,
        DatetimeIndexType, TimedeltaIndexType, HeterogeneousIndexType)):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I))


@overload(len, no_unliteral=True)
def overload_multi_index_len(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I)[0])


@overload_attribute(DatetimeIndexType, 'shape')
@overload_attribute(NumericIndexType, 'shape')
@overload_attribute(StringIndexType, 'shape')
@overload_attribute(BinaryIndexType, 'shape')
@overload_attribute(PeriodIndexType, 'shape')
@overload_attribute(TimedeltaIndexType, 'shape')
@overload_attribute(IntervalIndexType, 'shape')
@overload_attribute(CategoricalIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)),)


@overload_attribute(RangeIndexType, 'shape')
def overload_range_index_shape(s):
    return lambda s: (len(s),)


@overload_attribute(MultiIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)[0]),)


@overload_attribute(NumericIndexType, 'is_monotonic', inline='always')
@overload_attribute(RangeIndexType, 'is_monotonic', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic', inline='always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic', inline='always')
@overload_attribute(NumericIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_increasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_increasing', inline=
    'always')
def overload_index_is_montonic(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_increasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(fxeys__lkvm, 1)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step > 0 or len(I) <= 1
        return impl


@overload_attribute(NumericIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_decreasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_decreasing', inline=
    'always')
def overload_index_is_montonic_decreasing(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_decreasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(fxeys__lkvm, 2)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step < 0 or len(I) <= 1
        return impl


@overload_method(NumericIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(StringIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(PeriodIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(CategoricalIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(BinaryIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
def overload_index_duplicated(I, keep='first'):
    if isinstance(I, RangeIndexType):

        def impl(I, keep='first'):
            return np.zeros(len(I), np.bool_)
        return impl

    def impl(I, keep='first'):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        hysz__acydf = bodo.libs.array_kernels.duplicated((fxeys__lkvm,))
        return hysz__acydf
    return impl


@overload_method(NumericIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'any', no_unliteral=True, inline='always')
def overload_index_any(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) > 0 and (I._start != 0 or len(I) > 1)
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(NumericIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'all', no_unliteral=True, inline='always')
def overload_index_all(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) == 0 or I._step > 0 and (I._start > 0 or I._stop <= 0
                ) or I._step < 0 and (I._start < 0 or I._stop >= 0
                ) or I._start % I._step != 0
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(RangeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(NumericIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(StringIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(BinaryIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(CategoricalIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(PeriodIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
def overload_index_drop_duplicates(I, keep='first'):
    lqtbn__vgbyf = dict(keep=keep)
    adb__uebz = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    yghmj__qmoxo = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        yghmj__qmoxo += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        yghmj__qmoxo += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'bodo': bodo}, kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


@numba.generated_jit(nopython=True)
def get_index_data(S):
    return lambda S: S._data


@numba.generated_jit(nopython=True)
def get_index_name(S):
    return lambda S: S._name


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_index_data',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_datetime_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_timedelta_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_numeric_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_binary_str_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_categorical_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func


def get_index_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    udfo__qvqfx = args[0]
    if isinstance(self.typemap[udfo__qvqfx.name], (HeterogeneousIndexType,
        MultiIndexType)):
        return None
    if equiv_set.has_shape(udfo__qvqfx):
        return ArrayAnalysis.AnalyzeResult(shape=udfo__qvqfx, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_get_index_data
    ) = get_index_data_equiv


@overload_method(RangeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(NumericIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(StringIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(BinaryIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(CategoricalIndexType, 'map', inline='always', no_unliteral
    =True)
@overload_method(PeriodIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(DatetimeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'map', inline='always', no_unliteral=True)
def overload_index_map(I, mapper, na_action=None):
    if not is_const_func_type(mapper):
        raise BodoError("Index.map(): 'mapper' should be a function")
    lqtbn__vgbyf = dict(na_action=na_action)
    apqtk__xjb = dict(na_action=None)
    check_unsupported_args('Index.map', lqtbn__vgbyf, apqtk__xjb,
        package_name='pandas', module_name='Index')
    dtype = I.dtype
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.map')
    if dtype == types.NPDatetime('ns'):
        dtype = pd_timestamp_type
    if dtype == types.NPTimedelta('ns'):
        dtype = pd_timedelta_type
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = dtype.elem_type
    xown__cpk = numba.core.registry.cpu_target.typing_context
    esg__pdw = numba.core.registry.cpu_target.target_context
    try:
        oup__yfn = get_const_func_output_type(mapper, (dtype,), {},
            xown__cpk, esg__pdw)
    except Exception as cwc__vmp:
        raise_bodo_error(get_udf_error_msg('Index.map()', cwc__vmp))
    eohu__xacb = get_udf_out_arr_type(oup__yfn)
    func = get_overload_const_func(mapper, None)
    yghmj__qmoxo = 'def f(I, mapper, na_action=None):\n'
    yghmj__qmoxo += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    yghmj__qmoxo += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    yghmj__qmoxo += '  numba.parfors.parfor.init_prange()\n'
    yghmj__qmoxo += '  n = len(A)\n'
    yghmj__qmoxo += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    yghmj__qmoxo += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    yghmj__qmoxo += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    yghmj__qmoxo += '    v = map_func(t2)\n'
    yghmj__qmoxo += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    yghmj__qmoxo += (
        '  return bodo.utils.conversion.index_from_array(S, name)\n')
    nbd__uzah = bodo.compiler.udf_jit(func)
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': nbd__uzah, '_arr_typ': eohu__xacb, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'data_arr_type': eohu__xacb.dtype
        }, kqik__vrd)
    f = kqik__vrd['f']
    return f


@lower_builtin(operator.is_, NumericIndexType, NumericIndexType)
@lower_builtin(operator.is_, StringIndexType, StringIndexType)
@lower_builtin(operator.is_, BinaryIndexType, BinaryIndexType)
@lower_builtin(operator.is_, PeriodIndexType, PeriodIndexType)
@lower_builtin(operator.is_, DatetimeIndexType, DatetimeIndexType)
@lower_builtin(operator.is_, TimedeltaIndexType, TimedeltaIndexType)
@lower_builtin(operator.is_, IntervalIndexType, IntervalIndexType)
@lower_builtin(operator.is_, CategoricalIndexType, CategoricalIndexType)
def index_is(context, builder, sig, args):
    kjdrz__ayk, nix__npi = sig.args
    if kjdrz__ayk != nix__npi:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    kjdrz__ayk, nix__npi = sig.args
    if kjdrz__ayk != nix__npi:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):
            yghmj__qmoxo = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(lhs)
"""
            if rhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                yghmj__qmoxo += """  dt = bodo.utils.conversion.unbox_if_timestamp(rhs)
  return op(arr, dt)
"""
            else:
                yghmj__qmoxo += """  rhs_arr = bodo.utils.conversion.get_array_if_series_or_index(rhs)
  return op(arr, rhs_arr)
"""
            kqik__vrd = {}
            exec(yghmj__qmoxo, {'bodo': bodo, 'op': op}, kqik__vrd)
            impl = kqik__vrd['impl']
            return impl
        if is_index_type(rhs):
            yghmj__qmoxo = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(rhs)
"""
            if lhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                yghmj__qmoxo += """  dt = bodo.utils.conversion.unbox_if_timestamp(lhs)
  return op(dt, arr)
"""
            else:
                yghmj__qmoxo += """  lhs_arr = bodo.utils.conversion.get_array_if_series_or_index(lhs)
  return op(lhs_arr, arr)
"""
            kqik__vrd = {}
            exec(yghmj__qmoxo, {'bodo': bodo, 'op': op}, kqik__vrd)
            impl = kqik__vrd['impl']
            return impl
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    fxeys__lkvm = bodo.utils.conversion.coerce_to_array(data)
                    fybr__whqgk = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    hysz__acydf = op(fxeys__lkvm, fybr__whqgk)
                    return hysz__acydf
                return impl3
            count = len(lhs.data.types)
            yghmj__qmoxo = 'def f(lhs, rhs):\n'
            yghmj__qmoxo += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            kqik__vrd = {}
            exec(yghmj__qmoxo, {'op': op, 'np': np}, kqik__vrd)
            impl = kqik__vrd['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    fxeys__lkvm = bodo.utils.conversion.coerce_to_array(data)
                    fybr__whqgk = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    hysz__acydf = op(fybr__whqgk, fxeys__lkvm)
                    return hysz__acydf
                return impl4
            count = len(rhs.data.types)
            yghmj__qmoxo = 'def f(lhs, rhs):\n'
            yghmj__qmoxo += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            kqik__vrd = {}
            exec(yghmj__qmoxo, {'op': op, 'np': np}, kqik__vrd)
            impl = kqik__vrd['f']
            return impl
    return overload_index_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        overload_impl = create_binary_op_overload(op)
        overload(op, inline='always')(overload_impl)


_install_binary_ops()


def is_index_type(t):
    return isinstance(t, (RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, PeriodIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType))


@lower_cast(RangeIndexType, NumericIndexType)
def cast_range_index_to_int_index(context, builder, fromty, toty, val):
    f = lambda I: init_numeric_index(np.arange(I._start, I._stop, I._step),
        bodo.hiframes.pd_index_ext.get_index_name(I))
    return context.compile_internal(builder, f, toty(fromty), [val])


@numba.njit(no_cpython_wrapper=True)
def range_index_to_numeric(I):
    return init_numeric_index(np.arange(I._start, I._stop, I._step), bodo.
        hiframes.pd_index_ext.get_index_name(I))


class HeterogeneousIndexType(types.Type):
    ndim = 1

    def __init__(self, data=None, name_typ=None):
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        super(HeterogeneousIndexType, self).__init__(name=
            f'heter_index({data}, {name_typ})')

    def copy(self):
        return HeterogeneousIndexType(self.data, self.name_typ)

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return 'object'


@register_model(HeterogeneousIndexType)
class HeterogeneousIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbe__yyb = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, tbe__yyb)


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    jfi__neahh = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    pefwt__inf = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', pefwt__inf, idx_cpy_arg_defaults,
        fn_str=jfi__neahh, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(HeterogeneousIndexType)
def box_heter_index(typ, val, c):
    hpy__ngo = c.context.insert_const_string(c.builder.module, 'pandas')
    yhv__awjk = c.pyapi.import_module_noblock(hpy__ngo)
    wgxui__swb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, wgxui__swb.data)
    ousir__tbnzj = c.pyapi.from_native_value(typ.data, wgxui__swb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, wgxui__swb.name)
    gkan__mcd = c.pyapi.from_native_value(typ.name_typ, wgxui__swb.name, c.
        env_manager)
    obkt__srzrb = c.pyapi.make_none()
    lpzmx__qamo = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    axu__osght = c.pyapi.call_method(yhv__awjk, 'Index', (ousir__tbnzj,
        obkt__srzrb, lpzmx__qamo, gkan__mcd))
    c.pyapi.decref(ousir__tbnzj)
    c.pyapi.decref(obkt__srzrb)
    c.pyapi.decref(lpzmx__qamo)
    c.pyapi.decref(gkan__mcd)
    c.pyapi.decref(yhv__awjk)
    c.context.nrt.decref(c.builder, typ, val)
    return axu__osght


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        rok__opi = signature.return_type
        wgxui__swb = cgutils.create_struct_proxy(rok__opi)(context, builder)
        wgxui__swb.data = args[0]
        wgxui__swb.name = args[1]
        context.nrt.incref(builder, rok__opi.data, args[0])
        context.nrt.incref(builder, rok__opi.name_typ, args[1])
        return wgxui__swb._getvalue()
    return HeterogeneousIndexType(data, name)(data, name), codegen


@overload_attribute(HeterogeneousIndexType, 'name')
def heter_index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload_attribute(NumericIndexType, 'nbytes')
@overload_attribute(DatetimeIndexType, 'nbytes')
@overload_attribute(TimedeltaIndexType, 'nbytes')
@overload_attribute(RangeIndexType, 'nbytes')
@overload_attribute(StringIndexType, 'nbytes')
@overload_attribute(BinaryIndexType, 'nbytes')
@overload_attribute(CategoricalIndexType, 'nbytes')
@overload_attribute(PeriodIndexType, 'nbytes')
@overload_attribute(MultiIndexType, 'nbytes')
def overload_nbytes(I):
    if isinstance(I, RangeIndexType):

        def _impl_nbytes(I):
            return bodo.io.np_io.get_dtype_size(type(I._start)
                ) + bodo.io.np_io.get_dtype_size(type(I._step)
                ) + bodo.io.np_io.get_dtype_size(type(I._stop))
        return _impl_nbytes
    elif isinstance(I, MultiIndexType):
        yghmj__qmoxo = 'def _impl_nbytes(I):\n'
        yghmj__qmoxo += '    total = 0\n'
        yghmj__qmoxo += '    data = I._data\n'
        for i in range(I.nlevels):
            yghmj__qmoxo += f'    total += data[{i}].nbytes\n'
        yghmj__qmoxo += '    return total\n'
        nhr__mfh = {}
        exec(yghmj__qmoxo, {}, nhr__mfh)
        return nhr__mfh['_impl_nbytes']
    else:

        def _impl_nbytes(I):
            return I._data.nbytes
        return _impl_nbytes


@overload_method(NumericIndexType, 'to_series', inline='always')
@overload_method(DatetimeIndexType, 'to_series', inline='always')
@overload_method(TimedeltaIndexType, 'to_series', inline='always')
@overload_method(RangeIndexType, 'to_series', inline='always')
@overload_method(StringIndexType, 'to_series', inline='always')
@overload_method(BinaryIndexType, 'to_series', inline='always')
@overload_method(CategoricalIndexType, 'to_series', inline='always')
def overload_index_to_series(I, index=None, name=None):
    if not (is_overload_constant_str(name) or is_overload_constant_int(name
        ) or is_overload_none(name)):
        raise_bodo_error(
            f'Index.to_series(): only constant string/int are supported for argument name'
            )
    if is_overload_none(name):
        ravq__zrywg = 'bodo.hiframes.pd_index_ext.get_index_name(I)'
    else:
        ravq__zrywg = 'name'
    yghmj__qmoxo = 'def impl(I, index=None, name=None):\n'
    yghmj__qmoxo += '    data = bodo.utils.conversion.index_to_array(I)\n'
    if is_overload_none(index):
        yghmj__qmoxo += '    new_index = I\n'
    elif is_pd_index_type(index):
        yghmj__qmoxo += '    new_index = index\n'
    elif isinstance(index, SeriesType):
        yghmj__qmoxo += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        yghmj__qmoxo += (
            '    index_name = bodo.hiframes.pd_series_ext.get_series_name(index)\n'
            )
        yghmj__qmoxo += (
            '    new_index = bodo.utils.conversion.index_from_array(arr, index_name)\n'
            )
    elif bodo.utils.utils.is_array_typ(index, False):
        yghmj__qmoxo += (
            '    new_index = bodo.utils.conversion.index_from_array(index)\n')
    elif isinstance(index, (types.List, types.BaseTuple)):
        yghmj__qmoxo += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        yghmj__qmoxo += (
            '    new_index = bodo.utils.conversion.index_from_array(arr)\n')
    else:
        raise_bodo_error(
            f'Index.to_series(): unsupported type for argument index: {type(index).__name__}'
            )
    yghmj__qmoxo += f'    new_name = {ravq__zrywg}\n'
    yghmj__qmoxo += (
        '    return bodo.hiframes.pd_series_ext.init_series(data, new_index, new_name)'
        )
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'bodo': bodo, 'np': np}, kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


@overload_method(NumericIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'to_frame', inline='always', no_unliteral=True
    )
@overload_method(StringIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(BinaryIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(CategoricalIndexType, 'to_frame', inline='always',
    no_unliteral=True)
def overload_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        bbfg__dtpa = 'I'
    elif is_overload_false(index):
        bbfg__dtpa = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'Index.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'Index.to_frame(): index argument must be a compile time constant')
    yghmj__qmoxo = 'def impl(I, index=True, name=None):\n'
    yghmj__qmoxo += '    data = bodo.utils.conversion.index_to_array(I)\n'
    yghmj__qmoxo += f'    new_index = {bbfg__dtpa}\n'
    if is_overload_none(name) and I.name_typ == types.none:
        pige__hrp = ColNamesMetaType((0,))
    elif is_overload_none(name):
        pige__hrp = ColNamesMetaType((I.name_typ,))
    elif is_overload_constant_str(name):
        pige__hrp = ColNamesMetaType((get_overload_const_str(name),))
    elif is_overload_constant_int(name):
        pige__hrp = ColNamesMetaType((get_overload_const_int(name),))
    else:
        raise_bodo_error(
            f'Index.to_frame(): only constant string/int are supported for argument name'
            )
    yghmj__qmoxo += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((data,), new_index, __col_name_meta_value)
"""
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        pige__hrp}, kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


@overload_method(MultiIndexType, 'to_frame', inline='always', no_unliteral=True
    )
def overload_multi_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        bbfg__dtpa = 'I'
    elif is_overload_false(index):
        bbfg__dtpa = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a compile time constant'
            )
    yghmj__qmoxo = 'def impl(I, index=True, name=None):\n'
    yghmj__qmoxo += '    data = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    yghmj__qmoxo += f'    new_index = {bbfg__dtpa}\n'
    xfetm__tkyp = len(I.array_types)
    if is_overload_none(name) and I.names_typ == (types.none,) * xfetm__tkyp:
        pige__hrp = ColNamesMetaType(tuple(range(xfetm__tkyp)))
    elif is_overload_none(name):
        pige__hrp = ColNamesMetaType(I.names_typ)
    elif is_overload_constant_tuple(name) or is_overload_constant_list(name):
        if is_overload_constant_list(name):
            names = tuple(get_overload_const_list(name))
        else:
            names = get_overload_const_tuple(name)
        if xfetm__tkyp != len(names):
            raise_bodo_error(
                f'MultiIndex.to_frame(): expected {xfetm__tkyp} names, not {len(names)}'
                )
        if all(is_overload_constant_str(mqg__knfp) or
            is_overload_constant_int(mqg__knfp) for mqg__knfp in names):
            pige__hrp = ColNamesMetaType(names)
        else:
            raise_bodo_error(
                'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
                )
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
            )
    yghmj__qmoxo += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(data, new_index, __col_name_meta_value,)
"""
    kqik__vrd = {}
    exec(yghmj__qmoxo, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        pige__hrp}, kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


@overload_method(NumericIndexType, 'to_numpy', inline='always')
@overload_method(DatetimeIndexType, 'to_numpy', inline='always')
@overload_method(TimedeltaIndexType, 'to_numpy', inline='always')
@overload_method(RangeIndexType, 'to_numpy', inline='always')
@overload_method(StringIndexType, 'to_numpy', inline='always')
@overload_method(BinaryIndexType, 'to_numpy', inline='always')
@overload_method(CategoricalIndexType, 'to_numpy', inline='always')
@overload_method(IntervalIndexType, 'to_numpy', inline='always')
def overload_index_to_numpy(I, dtype=None, copy=False, na_value=None):
    lqtbn__vgbyf = dict(dtype=dtype, na_value=na_value)
    adb__uebz = dict(dtype=None, na_value=None)
    check_unsupported_args('Index.to_numpy', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(copy):
        raise_bodo_error('Index.to_numpy(): copy argument must be a boolean')
    if isinstance(I, RangeIndexType):

        def impl(I, dtype=None, copy=False, na_value=None):
            return np.arange(I._start, I._stop, I._step)
        return impl
    if is_overload_true(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I).copy()
        return impl
    if is_overload_false(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I)
        return impl

    def impl(I, dtype=None, copy=False, na_value=None):
        data = bodo.hiframes.pd_index_ext.get_index_data(I)
        return data.copy() if copy else data
    return impl


@overload_method(NumericIndexType, 'to_list', inline='always')
@overload_method(RangeIndexType, 'to_list', inline='always')
@overload_method(StringIndexType, 'to_list', inline='always')
@overload_method(BinaryIndexType, 'to_list', inline='always')
@overload_method(CategoricalIndexType, 'to_list', inline='always')
@overload_method(DatetimeIndexType, 'to_list', inline='always')
@overload_method(TimedeltaIndexType, 'to_list', inline='always')
@overload_method(NumericIndexType, 'tolist', inline='always')
@overload_method(RangeIndexType, 'tolist', inline='always')
@overload_method(StringIndexType, 'tolist', inline='always')
@overload_method(BinaryIndexType, 'tolist', inline='always')
@overload_method(CategoricalIndexType, 'tolist', inline='always')
@overload_method(DatetimeIndexType, 'tolist', inline='always')
@overload_method(TimedeltaIndexType, 'tolist', inline='always')
def overload_index_to_list(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            eloms__uxym = list()
            for i in range(I._start, I._stop, I.step):
                eloms__uxym.append(i)
            return eloms__uxym
        return impl

    def impl(I):
        eloms__uxym = list()
        for i in range(len(I)):
            eloms__uxym.append(I[i])
        return eloms__uxym
    return impl


@overload_attribute(NumericIndexType, 'T')
@overload_attribute(DatetimeIndexType, 'T')
@overload_attribute(TimedeltaIndexType, 'T')
@overload_attribute(RangeIndexType, 'T')
@overload_attribute(StringIndexType, 'T')
@overload_attribute(BinaryIndexType, 'T')
@overload_attribute(CategoricalIndexType, 'T')
@overload_attribute(PeriodIndexType, 'T')
@overload_attribute(MultiIndexType, 'T')
@overload_attribute(IntervalIndexType, 'T')
def overload_T(I):
    return lambda I: I


@overload_attribute(NumericIndexType, 'size')
@overload_attribute(DatetimeIndexType, 'size')
@overload_attribute(TimedeltaIndexType, 'size')
@overload_attribute(RangeIndexType, 'size')
@overload_attribute(StringIndexType, 'size')
@overload_attribute(BinaryIndexType, 'size')
@overload_attribute(CategoricalIndexType, 'size')
@overload_attribute(PeriodIndexType, 'size')
@overload_attribute(MultiIndexType, 'size')
@overload_attribute(IntervalIndexType, 'size')
def overload_size(I):
    return lambda I: len(I)


@overload_attribute(NumericIndexType, 'ndim')
@overload_attribute(DatetimeIndexType, 'ndim')
@overload_attribute(TimedeltaIndexType, 'ndim')
@overload_attribute(RangeIndexType, 'ndim')
@overload_attribute(StringIndexType, 'ndim')
@overload_attribute(BinaryIndexType, 'ndim')
@overload_attribute(CategoricalIndexType, 'ndim')
@overload_attribute(PeriodIndexType, 'ndim')
@overload_attribute(MultiIndexType, 'ndim')
@overload_attribute(IntervalIndexType, 'ndim')
def overload_ndim(I):
    return lambda I: 1


@overload_attribute(NumericIndexType, 'nlevels')
@overload_attribute(DatetimeIndexType, 'nlevels')
@overload_attribute(TimedeltaIndexType, 'nlevels')
@overload_attribute(RangeIndexType, 'nlevels')
@overload_attribute(StringIndexType, 'nlevels')
@overload_attribute(BinaryIndexType, 'nlevels')
@overload_attribute(CategoricalIndexType, 'nlevels')
@overload_attribute(PeriodIndexType, 'nlevels')
@overload_attribute(MultiIndexType, 'nlevels')
@overload_attribute(IntervalIndexType, 'nlevels')
def overload_nlevels(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(I._data)
    return lambda I: 1


@overload_attribute(NumericIndexType, 'empty')
@overload_attribute(DatetimeIndexType, 'empty')
@overload_attribute(TimedeltaIndexType, 'empty')
@overload_attribute(RangeIndexType, 'empty')
@overload_attribute(StringIndexType, 'empty')
@overload_attribute(BinaryIndexType, 'empty')
@overload_attribute(CategoricalIndexType, 'empty')
@overload_attribute(PeriodIndexType, 'empty')
@overload_attribute(MultiIndexType, 'empty')
@overload_attribute(IntervalIndexType, 'empty')
def overload_empty(I):
    return lambda I: len(I) == 0


@overload_attribute(NumericIndexType, 'is_all_dates')
@overload_attribute(DatetimeIndexType, 'is_all_dates')
@overload_attribute(TimedeltaIndexType, 'is_all_dates')
@overload_attribute(RangeIndexType, 'is_all_dates')
@overload_attribute(StringIndexType, 'is_all_dates')
@overload_attribute(BinaryIndexType, 'is_all_dates')
@overload_attribute(CategoricalIndexType, 'is_all_dates')
@overload_attribute(PeriodIndexType, 'is_all_dates')
@overload_attribute(MultiIndexType, 'is_all_dates')
@overload_attribute(IntervalIndexType, 'is_all_dates')
def overload_is_all_dates(I):
    if isinstance(I, (DatetimeIndexType, TimedeltaIndexType, PeriodIndexType)):
        return lambda I: True
    else:
        return lambda I: False


@overload_attribute(NumericIndexType, 'inferred_type')
@overload_attribute(DatetimeIndexType, 'inferred_type')
@overload_attribute(TimedeltaIndexType, 'inferred_type')
@overload_attribute(RangeIndexType, 'inferred_type')
@overload_attribute(StringIndexType, 'inferred_type')
@overload_attribute(BinaryIndexType, 'inferred_type')
@overload_attribute(CategoricalIndexType, 'inferred_type')
@overload_attribute(PeriodIndexType, 'inferred_type')
@overload_attribute(MultiIndexType, 'inferred_type')
@overload_attribute(IntervalIndexType, 'inferred_type')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Integer):
            return lambda I: 'integer'
        elif isinstance(I.dtype, types.Float):
            return lambda I: 'floating'
        elif isinstance(I.dtype, types.Boolean):
            return lambda I: 'boolean'
        return
    if isinstance(I, StringIndexType):

        def impl(I):
            if len(I._data) == 0:
                return 'empty'
            return 'string'
        return impl
    wqvy__wcell = {DatetimeIndexType: 'datetime64', TimedeltaIndexType:
        'timedelta64', RangeIndexType: 'integer', BinaryIndexType: 'bytes',
        CategoricalIndexType: 'categorical', PeriodIndexType: 'period',
        IntervalIndexType: 'interval', MultiIndexType: 'mixed'}
    inferred_type = wqvy__wcell[type(I)]
    return lambda I: inferred_type


@overload_attribute(NumericIndexType, 'dtype')
@overload_attribute(DatetimeIndexType, 'dtype')
@overload_attribute(TimedeltaIndexType, 'dtype')
@overload_attribute(RangeIndexType, 'dtype')
@overload_attribute(StringIndexType, 'dtype')
@overload_attribute(BinaryIndexType, 'dtype')
@overload_attribute(CategoricalIndexType, 'dtype')
@overload_attribute(MultiIndexType, 'dtype')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Boolean):
            return lambda I: np.dtype('O')
        dtype = I.dtype
        return lambda I: dtype
    if isinstance(I, CategoricalIndexType):
        dtype = bodo.utils.utils.create_categorical_type(I.dtype.categories,
            I.data, I.dtype.ordered)
        return lambda I: dtype
    enaw__kpy = {DatetimeIndexType: np.dtype('datetime64[ns]'),
        TimedeltaIndexType: np.dtype('timedelta64[ns]'), RangeIndexType: np
        .dtype('int64'), StringIndexType: np.dtype('O'), BinaryIndexType:
        np.dtype('O'), MultiIndexType: np.dtype('O')}
    dtype = enaw__kpy[type(I)]
    return lambda I: dtype


@overload_attribute(NumericIndexType, 'names')
@overload_attribute(DatetimeIndexType, 'names')
@overload_attribute(TimedeltaIndexType, 'names')
@overload_attribute(RangeIndexType, 'names')
@overload_attribute(StringIndexType, 'names')
@overload_attribute(BinaryIndexType, 'names')
@overload_attribute(CategoricalIndexType, 'names')
@overload_attribute(IntervalIndexType, 'names')
@overload_attribute(PeriodIndexType, 'names')
@overload_attribute(MultiIndexType, 'names')
def overload_names(I):
    if isinstance(I, MultiIndexType):
        return lambda I: I._names
    return lambda I: (I._name,)


@overload_method(NumericIndexType, 'rename', inline='always')
@overload_method(DatetimeIndexType, 'rename', inline='always')
@overload_method(TimedeltaIndexType, 'rename', inline='always')
@overload_method(RangeIndexType, 'rename', inline='always')
@overload_method(StringIndexType, 'rename', inline='always')
@overload_method(BinaryIndexType, 'rename', inline='always')
@overload_method(CategoricalIndexType, 'rename', inline='always')
@overload_method(PeriodIndexType, 'rename', inline='always')
@overload_method(IntervalIndexType, 'rename', inline='always')
@overload_method(HeterogeneousIndexType, 'rename', inline='always')
def overload_rename(I, name, inplace=False):
    if is_overload_true(inplace):
        raise BodoError('Index.rename(): inplace index renaming unsupported')
    return init_index_from_index(I, name)


def init_index_from_index(I, name):
    myjwr__ivg = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in myjwr__ivg:
        init_func = myjwr__ivg[type(I)]
        return lambda I, name, inplace=False: init_func(bodo.hiframes.
            pd_index_ext.get_index_data(I).copy(), name)
    if isinstance(I, RangeIndexType):
        return lambda I, name, inplace=False: I.copy(name=name)
    if isinstance(I, PeriodIndexType):
        freq = I.freq
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_period_index(bodo.hiframes.pd_index_ext.get_index_data(I).
            copy(), name, freq))
    if isinstance(I, HeterogeneousIndexType):
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_heter_index(bodo.hiframes.pd_index_ext.get_index_data(I),
            name))
    raise_bodo_error(f'init_index(): Unknown type {type(I)}')


def get_index_constructor(I):
    puscl__emg = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index, RangeIndexType: bodo.
        hiframes.pd_index_ext.init_range_index}
    if type(I) in puscl__emg:
        return puscl__emg[type(I)]
    raise BodoError(
        f'Unsupported type for standard Index constructor: {type(I)}')


@overload_method(NumericIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'min', no_unliteral=True, inline=
    'always')
def overload_index_min(I, axis=None, skipna=True):
    lqtbn__vgbyf = dict(axis=axis, skipna=skipna)
    adb__uebz = dict(axis=None, skipna=True)
    check_unsupported_args('Index.min', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            wiqj__vap = len(I)
            if wiqj__vap == 0:
                return np.nan
            if I._step < 0:
                return I._start + I._step * (wiqj__vap - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.min(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_min(fxeys__lkvm)
    return impl


@overload_method(NumericIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'max', no_unliteral=True, inline=
    'always')
def overload_index_max(I, axis=None, skipna=True):
    lqtbn__vgbyf = dict(axis=axis, skipna=skipna)
    adb__uebz = dict(axis=None, skipna=True)
    check_unsupported_args('Index.max', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            wiqj__vap = len(I)
            if wiqj__vap == 0:
                return np.nan
            if I._step > 0:
                return I._start + I._step * (wiqj__vap - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.max(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_max(fxeys__lkvm)
    return impl


@overload_method(NumericIndexType, 'argmin', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(PeriodIndexType, 'argmin', no_unliteral=True, inline='always')
def overload_index_argmin(I, axis=0, skipna=True):
    lqtbn__vgbyf = dict(axis=axis, skipna=skipna)
    adb__uebz = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmin', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmin()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step < 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmin(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = init_numeric_index(np.arange(len(fxeys__lkvm)))
        return bodo.libs.array_ops.array_op_idxmin(fxeys__lkvm, index)
    return impl


@overload_method(NumericIndexType, 'argmax', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argmax', no_unliteral=True, inline='always')
def overload_index_argmax(I, axis=0, skipna=True):
    lqtbn__vgbyf = dict(axis=axis, skipna=skipna)
    adb__uebz = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmax', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmax()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step > 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmax(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = np.arange(len(fxeys__lkvm))
        return bodo.libs.array_ops.array_op_idxmax(fxeys__lkvm, index)
    return impl


@overload_method(NumericIndexType, 'unique', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(IntervalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'unique', no_unliteral=True, inline=
    'always')
def overload_index_unique(I):
    wyevm__kxc = get_index_constructor(I)

    def impl(I):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        laps__adag = bodo.libs.array_kernels.unique(fxeys__lkvm)
        return wyevm__kxc(laps__adag, name)
    return impl


@overload_method(RangeIndexType, 'unique', no_unliteral=True, inline='always')
def overload_range_index_unique(I):

    def impl(I):
        return I.copy()
    return impl


@overload_method(NumericIndexType, 'nunique', inline='always')
@overload_method(BinaryIndexType, 'nunique', inline='always')
@overload_method(StringIndexType, 'nunique', inline='always')
@overload_method(CategoricalIndexType, 'nunique', inline='always')
@overload_method(DatetimeIndexType, 'nunique', inline='always')
@overload_method(TimedeltaIndexType, 'nunique', inline='always')
@overload_method(PeriodIndexType, 'nunique', inline='always')
def overload_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        ojmdy__rqxb = bodo.libs.array_kernels.nunique(fxeys__lkvm, dropna)
        return ojmdy__rqxb
    return impl


@overload_method(RangeIndexType, 'nunique', inline='always')
def overload_range_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        start = I._start
        stop = I._stop
        step = I._step
        return max(0, -(-(stop - start) // step))
    return impl


@overload_method(NumericIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(TimedeltaIndexType, 'isin', no_unliteral=True, inline='always'
    )
def overload_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            mxehc__krezx = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_index_ext.get_index_data(I)
            ojmdy__rqxb = len(A)
            hysz__acydf = np.empty(ojmdy__rqxb, np.bool_)
            bodo.libs.array.array_isin(hysz__acydf, A, mxehc__krezx, False)
            return hysz__acydf
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        hysz__acydf = bodo.libs.array_ops.array_op_isin(A, values)
        return hysz__acydf
    return impl


@overload_method(RangeIndexType, 'isin', no_unliteral=True, inline='always')
def overload_range_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            mxehc__krezx = bodo.utils.conversion.coerce_to_array(values)
            A = np.arange(I.start, I.stop, I.step)
            ojmdy__rqxb = len(A)
            hysz__acydf = np.empty(ojmdy__rqxb, np.bool_)
            bodo.libs.array.array_isin(hysz__acydf, A, mxehc__krezx, False)
            return hysz__acydf
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Index.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = np.arange(I.start, I.stop, I.step)
        hysz__acydf = bodo.libs.array_ops.array_op_isin(A, values)
        return hysz__acydf
    return impl


@register_jitable
def order_range(I, ascending):
    step = I._step
    if ascending == (step > 0):
        return I.copy()
    else:
        start = I._start
        stop = I._stop
        name = get_index_name(I)
        wiqj__vap = len(I)
        xesyl__kjanx = start + step * (wiqj__vap - 1)
        tphzu__dxl = xesyl__kjanx - step * wiqj__vap
        return init_range_index(xesyl__kjanx, tphzu__dxl, -step, name)


@overload_method(NumericIndexType, 'sort_values', no_unliteral=True, inline
    ='always')
@overload_method(BinaryIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(RangeIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
def overload_index_sort_values(I, return_indexer=False, ascending=True,
    na_position='last', key=None):
    lqtbn__vgbyf = dict(return_indexer=return_indexer, key=key)
    adb__uebz = dict(return_indexer=False, key=None)
    check_unsupported_args('Index.sort_values', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Index.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Index.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    if isinstance(I, RangeIndexType):

        def impl(I, return_indexer=False, ascending=True, na_position=
            'last', key=None):
            return order_range(I, ascending)
        return impl
    wyevm__kxc = get_index_constructor(I)
    glmks__eyxj = ColNamesMetaType(('$_bodo_col_',))

    def impl(I, return_indexer=False, ascending=True, na_position='last',
        key=None):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = get_index_name(I)
        index = init_range_index(0, len(fxeys__lkvm), 1, None)
        bwi__kwqb = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            fxeys__lkvm,), index, glmks__eyxj)
        tjyn__mcxxq = bwi__kwqb.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=False, na_position=na_position)
        hysz__acydf = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            tjyn__mcxxq, 0)
        return wyevm__kxc(hysz__acydf, name)
    return impl


@overload_method(NumericIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(BinaryIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(CategoricalIndexType, 'argsort', no_unliteral=True, inline
    ='always')
@overload_method(DatetimeIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(RangeIndexType, 'argsort', no_unliteral=True, inline='always')
def overload_index_argsort(I, axis=0, kind='quicksort', order=None):
    lqtbn__vgbyf = dict(axis=axis, kind=kind, order=order)
    adb__uebz = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Index.argsort', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, kind='quicksort', order=None):
            if I._step > 0:
                return np.arange(0, len(I), 1)
            else:
                return np.arange(len(I) - 1, -1, -1)
        return impl

    def impl(I, axis=0, kind='quicksort', order=None):
        fxeys__lkvm = bodo.hiframes.pd_index_ext.get_index_data(I)
        hysz__acydf = bodo.hiframes.series_impl.argsort(fxeys__lkvm)
        return hysz__acydf
    return impl


@overload_method(NumericIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'where', no_unliteral=True, inline='always'
    )
@overload_method(TimedeltaIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'where', no_unliteral=True, inline='always')
def overload_index_where(I, cond, other=np.nan):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.where()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('where',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        hykl__phl = 'None'
    else:
        hykl__phl = 'other'
    yghmj__qmoxo = 'def impl(I, cond, other=np.nan):\n'
    if isinstance(I, RangeIndexType):
        yghmj__qmoxo += '  arr = np.arange(I._start, I._stop, I._step)\n'
        wyevm__kxc = 'init_numeric_index'
    else:
        yghmj__qmoxo += (
            '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n')
    yghmj__qmoxo += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    yghmj__qmoxo += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {hykl__phl})\n'
        )
    yghmj__qmoxo += f'  return constructor(out_arr, name)\n'
    kqik__vrd = {}
    wyevm__kxc = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(yghmj__qmoxo, {'bodo': bodo, 'np': np, 'constructor': wyevm__kxc},
        kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


@overload_method(NumericIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(DatetimeIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'putmask', no_unliteral=True, inline
    ='always')
@overload_method(RangeIndexType, 'putmask', no_unliteral=True, inline='always')
def overload_index_putmask(I, cond, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.putmask()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.putmask()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('putmask',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        hykl__phl = 'None'
    else:
        hykl__phl = 'other'
    yghmj__qmoxo = 'def impl(I, cond, other):\n'
    yghmj__qmoxo += '  cond = ~cond\n'
    if isinstance(I, RangeIndexType):
        yghmj__qmoxo += '  arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        yghmj__qmoxo += (
            '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n')
    yghmj__qmoxo += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    yghmj__qmoxo += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {hykl__phl})\n'
        )
    yghmj__qmoxo += f'  return constructor(out_arr, name)\n'
    kqik__vrd = {}
    wyevm__kxc = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(yghmj__qmoxo, {'bodo': bodo, 'np': np, 'constructor': wyevm__kxc},
        kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


@overload_method(NumericIndexType, 'repeat', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'repeat', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'repeat', no_unliteral=True, inline='always')
def overload_index_repeat(I, repeats, axis=None):
    lqtbn__vgbyf = dict(axis=axis)
    adb__uebz = dict(axis=None)
    check_unsupported_args('Index.repeat', lqtbn__vgbyf, adb__uebz,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Index.repeat(): 'repeats' should be an integer or array of integers"
            )
    yghmj__qmoxo = 'def impl(I, repeats, axis=None):\n'
    if not isinstance(repeats, types.Integer):
        yghmj__qmoxo += (
            '    repeats = bodo.utils.conversion.coerce_to_array(repeats)\n')
    if isinstance(I, RangeIndexType):
        yghmj__qmoxo += '    arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        yghmj__qmoxo += (
            '    arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n')
    yghmj__qmoxo += '    name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    yghmj__qmoxo += (
        '    out_arr = bodo.libs.array_kernels.repeat_kernel(arr, repeats)\n')
    yghmj__qmoxo += '    return constructor(out_arr, name)'
    kqik__vrd = {}
    wyevm__kxc = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(yghmj__qmoxo, {'bodo': bodo, 'np': np, 'constructor': wyevm__kxc},
        kqik__vrd)
    impl = kqik__vrd['impl']
    return impl


@overload_method(NumericIndexType, 'is_integer', inline='always')
def overload_is_integer_numeric(I):
    truth = isinstance(I.dtype, types.Integer)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_floating', inline='always')
def overload_is_floating_numeric(I):
    truth = isinstance(I.dtype, types.Float)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_boolean', inline='always')
def overload_is_boolean_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_numeric', inline='always')
def overload_is_numeric_numeric(I):
    truth = not isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_object', inline='always')
def overload_is_object_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(StringIndexType, 'is_object', inline='always')
@overload_method(BinaryIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_numeric', inline='always')
@overload_method(RangeIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_object', inline='always')
def overload_is_methods_true(I):
    return lambda I: True


@overload_method(NumericIndexType, 'is_categorical', inline='always')
@overload_method(NumericIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_boolean', inline='always')
@overload_method(StringIndexType, 'is_floating', inline='always')
@overload_method(StringIndexType, 'is_categorical', inline='always')
@overload_method(StringIndexType, 'is_integer', inline='always')
@overload_method(StringIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_numeric', inline='always')
@overload_method(BinaryIndexType, 'is_boolean', inline='always')
@overload_method(BinaryIndexType, 'is_floating', inline='always')
@overload_method(BinaryIndexType, 'is_categorical', inline='always')
@overload_method(BinaryIndexType, 'is_integer', inline='always')
@overload_method(BinaryIndexType, 'is_interval', inline='always')
@overload_method(BinaryIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_boolean', inline='always')
@overload_method(DatetimeIndexType, 'is_floating', inline='always')
@overload_method(DatetimeIndexType, 'is_categorical', inline='always')
@overload_method(DatetimeIndexType, 'is_integer', inline='always')
@overload_method(DatetimeIndexType, 'is_interval', inline='always')
@overload_method(DatetimeIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_object', inline='always')
@overload_method(TimedeltaIndexType, 'is_boolean', inline='always')
@overload_method(TimedeltaIndexType, 'is_floating', inline='always')
@overload_method(TimedeltaIndexType, 'is_categorical', inline='always')
@overload_method(TimedeltaIndexType, 'is_integer', inline='always')
@overload_method(TimedeltaIndexType, 'is_interval', inline='always')
@overload_method(TimedeltaIndexType, 'is_numeric', inline='always')
@overload_method(TimedeltaIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_boolean', inline='always')
@overload_method(RangeIndexType, 'is_floating', inline='always')
@overload_method(RangeIndexType, 'is_categorical', inline='always')
@overload_method(RangeIndexType, 'is_interval', inline='always')
@overload_method(RangeIndexType, 'is_object', inline='always')
@overload_method(IntervalIndexType, 'is_boolean', inline='always')
@overload_method(IntervalIndexType, 'is_floating', inline='always')
@overload_method(IntervalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_integer', inline='always')
@overload_method(IntervalIndexType, 'is_numeric', inline='always')
@overload_method(IntervalIndexType, 'is_object', inline='always')
@overload_method(CategoricalIndexType, 'is_boolean', inline='always')
@overload_method(CategoricalIndexType, 'is_floating', inline='always')
@overload_method(CategoricalIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_interval', inline='always')
@overload_method(CategoricalIndexType, 'is_numeric', inline='always')
@overload_method(CategoricalIndexType, 'is_object', inline='always')
@overload_method(PeriodIndexType, 'is_boolean', inline='always')
@overload_method(PeriodIndexType, 'is_floating', inline='always')
@overload_method(PeriodIndexType, 'is_categorical', inline='always')
@overload_method(PeriodIndexType, 'is_integer', inline='always')
@overload_method(PeriodIndexType, 'is_interval', inline='always')
@overload_method(PeriodIndexType, 'is_numeric', inline='always')
@overload_method(PeriodIndexType, 'is_object', inline='always')
@overload_method(MultiIndexType, 'is_boolean', inline='always')
@overload_method(MultiIndexType, 'is_floating', inline='always')
@overload_method(MultiIndexType, 'is_categorical', inline='always')
@overload_method(MultiIndexType, 'is_integer', inline='always')
@overload_method(MultiIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_numeric', inline='always')
def overload_is_methods_false(I):
    return lambda I: False


@overload(operator.getitem, no_unliteral=True)
def overload_heter_index_getitem(I, ind):
    if not isinstance(I, HeterogeneousIndexType):
        return
    if isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, HeterogeneousIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_heter_index(bodo
            .hiframes.pd_index_ext.get_index_data(I)[ind], bodo.hiframes.
            pd_index_ext.get_index_name(I))


@lower_constant(DatetimeIndexType)
@lower_constant(TimedeltaIndexType)
def lower_constant_time_index(context, builder, ty, pyval):
    if isinstance(ty.data, bodo.DatetimeArrayType):
        data = context.get_constant_generic(builder, ty.data, pyval.array)
    else:
        data = context.get_constant_generic(builder, types.Array(types.
            int64, 1, 'C'), pyval.values.view(np.int64))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    adzcv__tkoqa = context.get_constant_null(types.DictType(dtype, types.int64)
        )
    return lir.Constant.literal_struct([data, name, adzcv__tkoqa])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    adzcv__tkoqa = context.get_constant_null(types.DictType(types.int64,
        types.int64))
    return lir.Constant.literal_struct([data, name, adzcv__tkoqa])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    adzcv__tkoqa = context.get_constant_null(types.DictType(dtype, types.int64)
        )
    return lir.Constant.literal_struct([data, name, adzcv__tkoqa])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    euo__bhm = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, euo__bhm, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    adzcv__tkoqa = context.get_constant_null(types.DictType(scalar_type,
        types.int64))
    return lir.Constant.literal_struct([data, name, adzcv__tkoqa])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [rnce__vahx] = sig.args
    [index] = args
    iktkq__qydv = context.make_helper(builder, rnce__vahx, value=index)
    ueqef__sxrf = context.make_helper(builder, sig.return_type)
    kagy__zzga = cgutils.alloca_once_value(builder, iktkq__qydv.start)
    uus__ufcsl = context.get_constant(types.intp, 0)
    exol__hnr = cgutils.alloca_once_value(builder, uus__ufcsl)
    ueqef__sxrf.iter = kagy__zzga
    ueqef__sxrf.stop = iktkq__qydv.stop
    ueqef__sxrf.step = iktkq__qydv.step
    ueqef__sxrf.count = exol__hnr
    fog__ljk = builder.sub(iktkq__qydv.stop, iktkq__qydv.start)
    dbrb__mtu = context.get_constant(types.intp, 1)
    qswoa__xwdwi = builder.icmp_signed('>', fog__ljk, uus__ufcsl)
    gpk__msxsd = builder.icmp_signed('>', iktkq__qydv.step, uus__ufcsl)
    ctyf__gpit = builder.not_(builder.xor(qswoa__xwdwi, gpk__msxsd))
    with builder.if_then(ctyf__gpit):
        zvtb__ygp = builder.srem(fog__ljk, iktkq__qydv.step)
        zvtb__ygp = builder.select(qswoa__xwdwi, zvtb__ygp, builder.neg(
            zvtb__ygp))
        wlkeg__nhcwo = builder.icmp_signed('>', zvtb__ygp, uus__ufcsl)
        phl__ocu = builder.add(builder.sdiv(fog__ljk, iktkq__qydv.step),
            builder.select(wlkeg__nhcwo, dbrb__mtu, uus__ufcsl))
        builder.store(phl__ocu, exol__hnr)
    vyifq__epqxp = ueqef__sxrf._getvalue()
    grs__yxlp = impl_ret_new_ref(context, builder, sig.return_type,
        vyifq__epqxp)
    return grs__yxlp


def _install_index_getiter():
    index_types = [NumericIndexType, StringIndexType, BinaryIndexType,
        CategoricalIndexType, TimedeltaIndexType, DatetimeIndexType]
    for typ in index_types:
        lower_builtin('getiter', typ)(numba.np.arrayobj.getiter_array)


_install_index_getiter()
index_unsupported_methods = ['append', 'asof', 'asof_locs', 'astype',
    'delete', 'drop', 'droplevel', 'dropna', 'equals', 'factorize',
    'fillna', 'format', 'get_indexer', 'get_indexer_for',
    'get_indexer_non_unique', 'get_level_values', 'get_slice_bound',
    'get_value', 'groupby', 'holds_integer', 'identical', 'insert', 'is_',
    'is_mixed', 'is_type_compatible', 'item', 'join', 'memory_usage',
    'ravel', 'reindex', 'searchsorted', 'set_names', 'set_value', 'shift',
    'slice_indexer', 'slice_locs', 'sort', 'sortlevel', 'str',
    'to_flat_index', 'to_native_types', 'transpose', 'value_counts', 'view']
index_unsupported_atrs = ['array', 'asi8', 'has_duplicates', 'hasnans',
    'is_unique']
cat_idx_unsupported_atrs = ['codes', 'categories', 'ordered',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing']
cat_idx_unsupported_methods = ['rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered', 'get_loc', 'isin',
    'all', 'any', 'union', 'intersection', 'difference', 'symmetric_difference'
    ]
interval_idx_unsupported_atrs = ['closed', 'is_empty',
    'is_non_overlapping_monotonic', 'is_overlapping', 'left', 'right',
    'mid', 'length', 'values', 'nbytes', 'is_monotonic',
    'is_monotonic_increasing', 'is_monotonic_decreasing', 'dtype']
interval_idx_unsupported_methods = ['contains', 'copy', 'overlaps',
    'set_closed', 'to_tuples', 'take', 'get_loc', 'isna', 'isnull', 'map',
    'isin', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_frame', 'to_list', 'tolist',
    'repeat', 'min', 'max']
multi_index_unsupported_atrs = ['levshape', 'levels', 'codes', 'dtypes',
    'values', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
multi_index_unsupported_methods = ['copy', 'set_levels', 'set_codes',
    'swaplevel', 'reorder_levels', 'remove_unused_levels', 'get_loc',
    'get_locs', 'get_loc_level', 'take', 'isna', 'isnull', 'map', 'isin',
    'unique', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_list', 'tolist', 'to_numpy',
    'repeat', 'min', 'max']
dt_index_unsupported_atrs = ['time', 'timez', 'tz', 'freq', 'freqstr',
    'inferred_freq']
dt_index_unsupported_methods = ['normalize', 'strftime', 'snap',
    'tz_localize', 'round', 'floor', 'ceil', 'to_period', 'to_perioddelta',
    'to_pydatetime', 'month_name', 'day_name', 'mean', 'indexer_at_time',
    'indexer_between', 'indexer_between_time', 'all', 'any']
td_index_unsupported_atrs = ['components', 'inferred_freq']
td_index_unsupported_methods = ['to_pydatetime', 'round', 'floor', 'ceil',
    'mean', 'all', 'any']
period_index_unsupported_atrs = ['day', 'dayofweek', 'day_of_week',
    'dayofyear', 'day_of_year', 'days_in_month', 'daysinmonth', 'freq',
    'freqstr', 'hour', 'is_leap_year', 'minute', 'month', 'quarter',
    'second', 'week', 'weekday', 'weekofyear', 'year', 'end_time', 'qyear',
    'start_time', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing', 'dtype']
period_index_unsupported_methods = ['asfreq', 'strftime', 'to_timestamp',
    'isin', 'unique', 'all', 'any', 'where', 'putmask', 'sort_values',
    'union', 'intersection', 'difference', 'symmetric_difference',
    'to_series', 'to_frame', 'to_numpy', 'to_list', 'tolist', 'repeat',
    'min', 'max']
string_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
string_index_unsupported_methods = ['min', 'max']
binary_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
binary_index_unsupported_methods = ['repeat', 'min', 'max']
index_types = [('pandas.RangeIndex.{}', RangeIndexType), (
    'pandas.Index.{} with numeric data', NumericIndexType), (
    'pandas.Index.{} with string data', StringIndexType), (
    'pandas.Index.{} with binary data', BinaryIndexType), (
    'pandas.TimedeltaIndex.{}', TimedeltaIndexType), (
    'pandas.IntervalIndex.{}', IntervalIndexType), (
    'pandas.CategoricalIndex.{}', CategoricalIndexType), (
    'pandas.PeriodIndex.{}', PeriodIndexType), ('pandas.DatetimeIndex.{}',
    DatetimeIndexType), ('pandas.MultiIndex.{}', MultiIndexType)]
for name, typ in index_types:
    idx_typ_to_format_str_map[typ] = name


def _install_index_unsupported():
    for dutyr__ful in index_unsupported_methods:
        for pzpg__nnok, typ in index_types:
            overload_method(typ, dutyr__ful, no_unliteral=True)(
                create_unsupported_overload(pzpg__nnok.format(dutyr__ful +
                '()')))
    for dro__byp in index_unsupported_atrs:
        for pzpg__nnok, typ in index_types:
            overload_attribute(typ, dro__byp, no_unliteral=True)(
                create_unsupported_overload(pzpg__nnok.format(dro__byp)))
    ghve__iify = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    vsec__leb = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods), (BinaryIndexType,
        binary_index_unsupported_methods), (StringIndexType,
        string_index_unsupported_methods)]
    for typ, ruzhv__fpuho in vsec__leb:
        pzpg__nnok = idx_typ_to_format_str_map[typ]
        for hbb__hdbi in ruzhv__fpuho:
            overload_method(typ, hbb__hdbi, no_unliteral=True)(
                create_unsupported_overload(pzpg__nnok.format(hbb__hdbi +
                '()')))
    for typ, pon__irjj in ghve__iify:
        pzpg__nnok = idx_typ_to_format_str_map[typ]
        for dro__byp in pon__irjj:
            overload_attribute(typ, dro__byp, no_unliteral=True)(
                create_unsupported_overload(pzpg__nnok.format(dro__byp)))


_install_index_unsupported()
