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
            efytg__srut = val.dtype.numpy_dtype
            dtype = numba.np.numpy_support.from_dtype(efytg__srut)
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
        ncspl__xjkhq = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(_dt_index_data_typ.dtype, types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, ncspl__xjkhq)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    czkv__ggv = dict(deep=deep, dtype=dtype, names=names)
    xbvb__ksriz = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()')
    check_unsupported_args('copy', czkv__ggv, idx_cpy_arg_defaults, fn_str=
        xbvb__ksriz, package_name='pandas', module_name='Index')
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
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    ckxf__cvmt = c.pyapi.import_module_noblock(skow__dmu)
    qis__pkvjf = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, qis__pkvjf.data)
    vtta__qjuae = c.pyapi.from_native_value(typ.data, qis__pkvjf.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, qis__pkvjf.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, qis__pkvjf.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([vtta__qjuae])
    cwyl__pnoav = c.pyapi.object_getattr_string(ckxf__cvmt, 'DatetimeIndex')
    kws = c.pyapi.dict_pack([('name', nqtiq__nslf)])
    ggoc__jshm = c.pyapi.call(cwyl__pnoav, args, kws)
    c.pyapi.decref(vtta__qjuae)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(ckxf__cvmt)
    c.pyapi.decref(cwyl__pnoav)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return ggoc__jshm


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        gjycm__lrenq = c.pyapi.object_getattr_string(val, 'array')
    else:
        gjycm__lrenq = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, gjycm__lrenq).value
    nqtiq__nslf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nqtiq__nslf).value
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nov__uenru.data = data
    nov__uenru.name = name
    dtype = _dt_index_data_typ.dtype
    nvr__rieu, laz__xxqi = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    nov__uenru.dict = laz__xxqi
    c.pyapi.decref(gjycm__lrenq)
    c.pyapi.decref(nqtiq__nslf)
    return NativeValue(nov__uenru._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        skkn__ngqsq, wwp__uhch = args
        qis__pkvjf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        qis__pkvjf.data = skkn__ngqsq
        qis__pkvjf.name = wwp__uhch
        context.nrt.incref(builder, signature.args[0], skkn__ngqsq)
        context.nrt.incref(builder, signature.args[1], wwp__uhch)
        dtype = _dt_index_data_typ.dtype
        qis__pkvjf.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return qis__pkvjf._getvalue()
    ctd__zqtfg = DatetimeIndexType(name, data)
    sig = signature(ctd__zqtfg, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    ffv__otx = args[0]
    if equiv_set.has_shape(ffv__otx):
        return ArrayAnalysis.AnalyzeResult(shape=ffv__otx, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    byk__jnbzo = 'def impl(dti):\n'
    byk__jnbzo += '    numba.parfors.parfor.init_prange()\n'
    byk__jnbzo += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    byk__jnbzo += '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n'
    byk__jnbzo += '    n = len(A)\n'
    byk__jnbzo += '    S = np.empty(n, np.int64)\n'
    byk__jnbzo += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    byk__jnbzo += '        val = A[i]\n'
    byk__jnbzo += '        ts = bodo.utils.conversion.box_if_dt64(val)\n'
    if field in ['weekday']:
        byk__jnbzo += '        S[i] = ts.' + field + '()\n'
    else:
        byk__jnbzo += '        S[i] = ts.' + field + '\n'
    byk__jnbzo += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    wrho__oyzq = {}
    exec(byk__jnbzo, {'numba': numba, 'np': np, 'bodo': bodo}, wrho__oyzq)
    impl = wrho__oyzq['impl']
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
        yxvx__ksf = len(A)
        S = np.empty(yxvx__ksf, np.bool_)
        for i in numba.parfors.parfor.internal_prange(yxvx__ksf):
            val = A[i]
            huo__ymbdh = bodo.utils.conversion.box_if_dt64(val)
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(huo__ymbdh.year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        yxvx__ksf = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(yxvx__ksf
            )
        for i in numba.parfors.parfor.internal_prange(yxvx__ksf):
            val = A[i]
            huo__ymbdh = bodo.utils.conversion.box_if_dt64(val)
            S[i] = datetime.date(huo__ymbdh.year, huo__ymbdh.month,
                huo__ymbdh.day)
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
    xhyri__ochcw = dict(axis=axis, skipna=skipna)
    gju__epwlp = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.min()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        jghat__ekrt = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(jghat__ekrt)):
            if not bodo.libs.array_kernels.isna(jghat__ekrt, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jghat__ekrt[i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    xhyri__ochcw = dict(axis=axis, skipna=skipna)
    gju__epwlp = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.max()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        jghat__ekrt = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(jghat__ekrt)):
            if not bodo.libs.array_kernels.isna(jghat__ekrt, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jghat__ekrt[i])
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
    xhyri__ochcw = dict(freq=freq, tz=tz, normalize=normalize, closed=
        closed, ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst,
        dtype=dtype, copy=copy)
    gju__epwlp = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        mixqb__oswjl = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(mixqb__oswjl)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        jsng__imdi = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            jghat__ekrt = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            yxvx__ksf = len(jghat__ekrt)
            S = np.empty(yxvx__ksf, jsng__imdi)
            cwrjb__hxrvl = rhs.value
            for i in numba.parfors.parfor.internal_prange(yxvx__ksf):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jghat__ekrt[i]) - cwrjb__hxrvl)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        jsng__imdi = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            jghat__ekrt = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            yxvx__ksf = len(jghat__ekrt)
            S = np.empty(yxvx__ksf, jsng__imdi)
            cwrjb__hxrvl = lhs.value
            for i in numba.parfors.parfor.internal_prange(yxvx__ksf):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    cwrjb__hxrvl - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(jghat__ekrt[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    eai__kfk = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    byk__jnbzo = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        byk__jnbzo += '  dt_index, _str = lhs, rhs\n'
        scbhw__mmw = 'arr[i] {} other'.format(eai__kfk)
    else:
        byk__jnbzo += '  dt_index, _str = rhs, lhs\n'
        scbhw__mmw = 'other {} arr[i]'.format(eai__kfk)
    byk__jnbzo += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    byk__jnbzo += '  l = len(arr)\n'
    byk__jnbzo += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    byk__jnbzo += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    byk__jnbzo += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    byk__jnbzo += '    S[i] = {}\n'.format(scbhw__mmw)
    byk__jnbzo += '  return S\n'
    wrho__oyzq = {}
    exec(byk__jnbzo, {'bodo': bodo, 'numba': numba, 'np': np}, wrho__oyzq)
    impl = wrho__oyzq['impl']
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
        vytn__dzjw = parse_dtype(dtype, 'pandas.Index')
        jftwr__njytw = False
    else:
        vytn__dzjw = getattr(data, 'dtype', None)
        jftwr__njytw = True
    if isinstance(vytn__dzjw, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or vytn__dzjw == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType
        ) or vytn__dzjw == types.NPTimedelta('ns'):

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
        if isinstance(vytn__dzjw, (types.Integer, types.Float, types.Boolean)):
            if jftwr__njytw:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    mixqb__oswjl = bodo.utils.conversion.coerce_to_array(data)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        mixqb__oswjl, name)
            else:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    mixqb__oswjl = bodo.utils.conversion.coerce_to_array(data)
                    bla__wfxp = bodo.utils.conversion.fix_arr_dtype(
                        mixqb__oswjl, vytn__dzjw)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        bla__wfxp, name)
        elif vytn__dzjw in [types.string, bytes_type]:

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
                ffc__aoxl = bodo.hiframes.pd_index_ext.get_index_data(dti)
                val = ffc__aoxl[ind]
                return bodo.utils.conversion.box_if_dt64(val)
            return impl
        else:

            def impl(dti, ind):
                ffc__aoxl = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                ftgow__fcni = ffc__aoxl[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(
                    ftgow__fcni, name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            opipd__lpdq = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(opipd__lpdq[ind])
        return impl

    def impl(I, ind):
        opipd__lpdq = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        ftgow__fcni = opipd__lpdq[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(ftgow__fcni,
            name)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_categorical_index_getitem(I, ind):
    if not isinstance(I, CategoricalIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            snz__wqv = bodo.hiframes.pd_index_ext.get_index_data(I)
            val = snz__wqv[ind]
            return val
        return impl
    if isinstance(ind, types.SliceType):

        def impl(I, ind):
            snz__wqv = bodo.hiframes.pd_index_ext.get_index_data(I)
            name = bodo.hiframes.pd_index_ext.get_index_name(I)
            ftgow__fcni = snz__wqv[ind]
            return bodo.hiframes.pd_index_ext.init_categorical_index(
                ftgow__fcni, name)
        return impl
    raise BodoError(
        f'pd.CategoricalIndex.__getitem__: unsupported index type {ind}')


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    xvg__fzzq = False
    uukcv__iglyv = False
    if closed is None:
        xvg__fzzq = True
        uukcv__iglyv = True
    elif closed == 'left':
        xvg__fzzq = True
    elif closed == 'right':
        uukcv__iglyv = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return xvg__fzzq, uukcv__iglyv


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
    xhyri__ochcw = dict(tz=tz, normalize=normalize, closed=closed)
    gju__epwlp = dict(tz=None, normalize=False, closed=None)
    check_unsupported_args('pandas.date_range', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise_bodo_error('pd.date_range(): tz argument not supported yet')
    fpjv__qhcqo = ''
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
        fpjv__qhcqo = "  freq = 'D'\n"
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise_bodo_error(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )
    byk__jnbzo = """def f(start=None, end=None, periods=None, freq=None, tz=None, normalize=False, name=None, closed=None):
"""
    byk__jnbzo += fpjv__qhcqo
    if is_overload_none(start):
        byk__jnbzo += "  start_t = pd.Timestamp('1800-01-03')\n"
    else:
        byk__jnbzo += '  start_t = pd.Timestamp(start)\n'
    if is_overload_none(end):
        byk__jnbzo += "  end_t = pd.Timestamp('1800-01-03')\n"
    else:
        byk__jnbzo += '  end_t = pd.Timestamp(end)\n'
    if not is_overload_none(freq):
        byk__jnbzo += (
            '  stride = bodo.hiframes.pd_index_ext.to_offset_value(freq)\n')
        if is_overload_none(periods):
            byk__jnbzo += '  b = start_t.value\n'
            byk__jnbzo += (
                '  e = b + (end_t.value - b) // stride * stride + stride // 2 + 1\n'
                )
        elif not is_overload_none(start):
            byk__jnbzo += '  b = start_t.value\n'
            byk__jnbzo += '  addend = np.int64(periods) * np.int64(stride)\n'
            byk__jnbzo += '  e = np.int64(b) + addend\n'
        elif not is_overload_none(end):
            byk__jnbzo += '  e = end_t.value + stride\n'
            byk__jnbzo += '  addend = np.int64(periods) * np.int64(-stride)\n'
            byk__jnbzo += '  b = np.int64(e) + addend\n'
        else:
            raise_bodo_error(
                "at least 'start' or 'end' should be specified if a 'period' is given."
                )
        byk__jnbzo += '  arr = np.arange(b, e, stride, np.int64)\n'
    else:
        byk__jnbzo += '  delta = end_t.value - start_t.value\n'
        byk__jnbzo += '  step = delta / (periods - 1)\n'
        byk__jnbzo += '  arr1 = np.arange(0, periods, 1, np.float64)\n'
        byk__jnbzo += '  arr1 *= step\n'
        byk__jnbzo += '  arr1 += start_t.value\n'
        byk__jnbzo += '  arr = arr1.astype(np.int64)\n'
        byk__jnbzo += '  arr[-1] = end_t.value\n'
    byk__jnbzo += '  A = bodo.utils.conversion.convert_to_dt64ns(arr)\n'
    byk__jnbzo += (
        '  return bodo.hiframes.pd_index_ext.init_datetime_index(A, name)\n')
    wrho__oyzq = {}
    exec(byk__jnbzo, {'bodo': bodo, 'np': np, 'pd': pd}, wrho__oyzq)
    f = wrho__oyzq['f']
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
        kkh__djt = pd.Timedelta('1 day')
        if start is not None:
            kkh__djt = pd.Timedelta(start)
        aklfs__zti = pd.Timedelta('1 day')
        if end is not None:
            aklfs__zti = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        xvg__fzzq, uukcv__iglyv = (bodo.hiframes.pd_index_ext.
            validate_endpoints(closed))
        if freq is not None:
            ltfzh__khcc = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = kkh__djt.value
                nrkr__gbuy = b + (aklfs__zti.value - b
                    ) // ltfzh__khcc * ltfzh__khcc + ltfzh__khcc // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = kkh__djt.value
                ydpx__png = np.int64(periods) * np.int64(ltfzh__khcc)
                nrkr__gbuy = np.int64(b) + ydpx__png
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                nrkr__gbuy = aklfs__zti.value + ltfzh__khcc
                ydpx__png = np.int64(periods) * np.int64(-ltfzh__khcc)
                b = np.int64(nrkr__gbuy) + ydpx__png
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            lkr__abdn = np.arange(b, nrkr__gbuy, ltfzh__khcc, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            hok__psym = aklfs__zti.value - kkh__djt.value
            step = hok__psym / (periods - 1)
            elj__pifat = np.arange(0, periods, 1, np.float64)
            elj__pifat *= step
            elj__pifat += kkh__djt.value
            lkr__abdn = elj__pifat.astype(np.int64)
            lkr__abdn[-1] = aklfs__zti.value
        if not xvg__fzzq and len(lkr__abdn) and lkr__abdn[0] == kkh__djt.value:
            lkr__abdn = lkr__abdn[1:]
        if not uukcv__iglyv and len(lkr__abdn) and lkr__abdn[-1
            ] == aklfs__zti.value:
            lkr__abdn = lkr__abdn[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(lkr__abdn)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):
    kub__estcv = ColNamesMetaType(('year', 'week', 'day'))

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        yxvx__ksf = len(A)
        ivska__qvcd = bodo.libs.int_arr_ext.alloc_int_array(yxvx__ksf, np.
            uint32)
        mjglx__tsc = bodo.libs.int_arr_ext.alloc_int_array(yxvx__ksf, np.uint32
            )
        ravk__mvbz = bodo.libs.int_arr_ext.alloc_int_array(yxvx__ksf, np.uint32
            )
        for i in numba.parfors.parfor.internal_prange(yxvx__ksf):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(ivska__qvcd, i)
                bodo.libs.array_kernels.setna(mjglx__tsc, i)
                bodo.libs.array_kernels.setna(ravk__mvbz, i)
                continue
            ivska__qvcd[i], mjglx__tsc[i], ravk__mvbz[i
                ] = bodo.utils.conversion.box_if_dt64(A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((ivska__qvcd,
            mjglx__tsc, ravk__mvbz), idx, kub__estcv)
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
        ncspl__xjkhq = [('data', _timedelta_index_data_typ), ('name',
            fe_type.name_typ), ('dict', types.DictType(
            _timedelta_index_data_typ.dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type,
            ncspl__xjkhq)


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    ckxf__cvmt = c.pyapi.import_module_noblock(skow__dmu)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    vtta__qjuae = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([vtta__qjuae])
    kws = c.pyapi.dict_pack([('name', nqtiq__nslf)])
    cwyl__pnoav = c.pyapi.object_getattr_string(ckxf__cvmt, 'TimedeltaIndex')
    ggoc__jshm = c.pyapi.call(cwyl__pnoav, args, kws)
    c.pyapi.decref(vtta__qjuae)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(ckxf__cvmt)
    c.pyapi.decref(cwyl__pnoav)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return ggoc__jshm


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    mhq__sfl = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, mhq__sfl).value
    nqtiq__nslf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nqtiq__nslf).value
    c.pyapi.decref(mhq__sfl)
    c.pyapi.decref(nqtiq__nslf)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nov__uenru.data = data
    nov__uenru.name = name
    dtype = _timedelta_index_data_typ.dtype
    nvr__rieu, laz__xxqi = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    nov__uenru.dict = laz__xxqi
    return NativeValue(nov__uenru._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        skkn__ngqsq, wwp__uhch = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = skkn__ngqsq
        timedelta_index.name = wwp__uhch
        context.nrt.incref(builder, signature.args[0], skkn__ngqsq)
        context.nrt.incref(builder, signature.args[1], wwp__uhch)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    ctd__zqtfg = TimedeltaIndexType(name)
    sig = signature(ctd__zqtfg, data, name)
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
    czkv__ggv = dict(deep=deep, dtype=dtype, names=names)
    xbvb__ksriz = idx_typ_to_format_str_map[TimedeltaIndexType].format('copy()'
        )
    check_unsupported_args('TimedeltaIndex.copy', czkv__ggv,
        idx_cpy_arg_defaults, fn_str=xbvb__ksriz, package_name='pandas',
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
    xhyri__ochcw = dict(axis=axis, skipna=skipna)
    gju__epwlp = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        yxvx__ksf = len(data)
        pzeq__jknwk = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(yxvx__ksf):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            pzeq__jknwk = min(pzeq__jknwk, val)
        ptwdj__hpk = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            pzeq__jknwk)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(ptwdj__hpk, count)
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    xhyri__ochcw = dict(axis=axis, skipna=skipna)
    gju__epwlp = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        yxvx__ksf = len(data)
        gtb__zaju = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(yxvx__ksf):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            gtb__zaju = max(gtb__zaju, val)
        ptwdj__hpk = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            gtb__zaju)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(ptwdj__hpk, count)
    return impl


def gen_tdi_field_impl(field):
    byk__jnbzo = 'def impl(tdi):\n'
    byk__jnbzo += '    numba.parfors.parfor.init_prange()\n'
    byk__jnbzo += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    byk__jnbzo += '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n'
    byk__jnbzo += '    n = len(A)\n'
    byk__jnbzo += '    S = np.empty(n, np.int64)\n'
    byk__jnbzo += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    byk__jnbzo += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        byk__jnbzo += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        byk__jnbzo += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        byk__jnbzo += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        byk__jnbzo += (
            '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
    else:
        assert False, 'invalid timedelta field'
    byk__jnbzo += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    wrho__oyzq = {}
    exec(byk__jnbzo, {'numba': numba, 'np': np, 'bodo': bodo}, wrho__oyzq)
    impl = wrho__oyzq['impl']
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
    xhyri__ochcw = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    gju__epwlp = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', xhyri__ochcw,
        gju__epwlp, package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        mixqb__oswjl = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(mixqb__oswjl)
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
        ncspl__xjkhq = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, ncspl__xjkhq)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    czkv__ggv = dict(deep=deep, dtype=dtype, names=names)
    xbvb__ksriz = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', czkv__ggv,
        idx_cpy_arg_defaults, fn_str=xbvb__ksriz, package_name='pandas',
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
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    unsrm__pkusz = c.pyapi.import_module_noblock(skow__dmu)
    kzavk__xpyd = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    bigp__khxga = c.pyapi.from_native_value(types.int64, kzavk__xpyd.start,
        c.env_manager)
    yxo__kvjpc = c.pyapi.from_native_value(types.int64, kzavk__xpyd.stop, c
        .env_manager)
    yjmxq__psan = c.pyapi.from_native_value(types.int64, kzavk__xpyd.step,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, kzavk__xpyd.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, kzavk__xpyd.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([bigp__khxga, yxo__kvjpc, yjmxq__psan])
    kws = c.pyapi.dict_pack([('name', nqtiq__nslf)])
    cwyl__pnoav = c.pyapi.object_getattr_string(unsrm__pkusz, 'RangeIndex')
    mgmc__kpjtu = c.pyapi.call(cwyl__pnoav, args, kws)
    c.pyapi.decref(bigp__khxga)
    c.pyapi.decref(yxo__kvjpc)
    c.pyapi.decref(yjmxq__psan)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(unsrm__pkusz)
    c.pyapi.decref(cwyl__pnoav)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return mgmc__kpjtu


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name
    hun__jkdg = is_overload_constant_int(step) and get_overload_const_int(step
        ) == 0

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        if hun__jkdg:
            raise_bodo_error('Step must not be zero')
        qjz__qxh = cgutils.is_scalar_zero(builder, args[2])
        yula__miee = context.get_python_api(builder)
        with builder.if_then(qjz__qxh):
            yula__miee.err_format('PyExc_ValueError', 'Step must not be zero')
            val = context.get_constant(types.int32, -1)
            builder.ret(val)
        kzavk__xpyd = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        kzavk__xpyd.start = args[0]
        kzavk__xpyd.stop = args[1]
        kzavk__xpyd.step = args[2]
        kzavk__xpyd.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return kzavk__xpyd._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, hia__zliui = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    bigp__khxga = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, bigp__khxga).value
    yxo__kvjpc = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, yxo__kvjpc).value
    yjmxq__psan = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, yjmxq__psan).value
    nqtiq__nslf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nqtiq__nslf).value
    c.pyapi.decref(bigp__khxga)
    c.pyapi.decref(yxo__kvjpc)
    c.pyapi.decref(yjmxq__psan)
    c.pyapi.decref(nqtiq__nslf)
    kzavk__xpyd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kzavk__xpyd.start = start
    kzavk__xpyd.stop = stop
    kzavk__xpyd.step = step
    kzavk__xpyd.name = name
    return NativeValue(kzavk__xpyd._getvalue())


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
        vygo__oxz = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(vygo__oxz.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        vygo__oxz = 'RangeIndex(...) must be called with integers'
        raise BodoError(vygo__oxz)
    oxew__uap = 'start'
    mhqyf__bmti = 'stop'
    jkw__urvrp = 'step'
    if is_overload_none(start):
        oxew__uap = '0'
    if is_overload_none(stop):
        mhqyf__bmti = 'start'
        oxew__uap = '0'
    if is_overload_none(step):
        jkw__urvrp = '1'
    byk__jnbzo = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    byk__jnbzo += '  return init_range_index({}, {}, {}, name)\n'.format(
        oxew__uap, mhqyf__bmti, jkw__urvrp)
    wrho__oyzq = {}
    exec(byk__jnbzo, {'init_range_index': init_range_index}, wrho__oyzq)
    kyg__jta = wrho__oyzq['_pd_range_index_imp']
    return kyg__jta


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
                sjo__hvhra = numba.cpython.unicode._normalize_slice(idx, len(I)
                    )
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * sjo__hvhra.start
                stop = I._start + I._step * sjo__hvhra.stop
                step = I._step * sjo__hvhra.step
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
        ncspl__xjkhq = [('data', bodo.IntegerArrayType(types.int64)), (
            'name', fe_type.name_typ), ('dict', types.DictType(types.int64,
            types.int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, ncspl__xjkhq)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    czkv__ggv = dict(deep=deep, dtype=dtype, names=names)
    xbvb__ksriz = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', czkv__ggv,
        idx_cpy_arg_defaults, fn_str=xbvb__ksriz, package_name='pandas',
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
        skkn__ngqsq, wwp__uhch, hia__zliui = args
        qcu__ktqol = signature.return_type
        jzvy__fue = cgutils.create_struct_proxy(qcu__ktqol)(context, builder)
        jzvy__fue.data = skkn__ngqsq
        jzvy__fue.name = wwp__uhch
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        jzvy__fue.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return jzvy__fue._getvalue()
    eil__rrxd = get_overload_const_str(freq)
    ctd__zqtfg = PeriodIndexType(eil__rrxd, name)
    sig = signature(ctd__zqtfg, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    unsrm__pkusz = c.pyapi.import_module_noblock(skow__dmu)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        nov__uenru.data)
    gjycm__lrenq = c.pyapi.from_native_value(bodo.IntegerArrayType(types.
        int64), nov__uenru.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, nov__uenru.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, nov__uenru.name,
        c.env_manager)
    khc__eve = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', gjycm__lrenq), ('name',
        nqtiq__nslf), ('freq', khc__eve)])
    cwyl__pnoav = c.pyapi.object_getattr_string(unsrm__pkusz, 'PeriodIndex')
    mgmc__kpjtu = c.pyapi.call(cwyl__pnoav, args, kws)
    c.pyapi.decref(gjycm__lrenq)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(khc__eve)
    c.pyapi.decref(unsrm__pkusz)
    c.pyapi.decref(cwyl__pnoav)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return mgmc__kpjtu


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    imumh__kapnc = c.pyapi.object_getattr_string(val, 'asi8')
    uvmp__vbxc = c.pyapi.call_method(val, 'isna', ())
    nqtiq__nslf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nqtiq__nslf).value
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    ckxf__cvmt = c.pyapi.import_module_noblock(skow__dmu)
    ufakb__omzp = c.pyapi.object_getattr_string(ckxf__cvmt, 'arrays')
    gjycm__lrenq = c.pyapi.call_method(ufakb__omzp, 'IntegerArray', (
        imumh__kapnc, uvmp__vbxc))
    data = c.pyapi.to_native_value(arr_typ, gjycm__lrenq).value
    c.pyapi.decref(imumh__kapnc)
    c.pyapi.decref(uvmp__vbxc)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(ckxf__cvmt)
    c.pyapi.decref(ufakb__omzp)
    c.pyapi.decref(gjycm__lrenq)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nov__uenru.data = data
    nov__uenru.name = name
    nvr__rieu, laz__xxqi = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(types.int64, types.int64), types.DictType(types.int64, types.
        int64)(), [])
    nov__uenru.dict = laz__xxqi
    return NativeValue(nov__uenru._getvalue())


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
        clfq__ktgd = get_categories_int_type(fe_type.data.dtype)
        ncspl__xjkhq = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(clfq__ktgd, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            ncspl__xjkhq)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    ckxf__cvmt = c.pyapi.import_module_noblock(skow__dmu)
    zgsw__tlx = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, zgsw__tlx.data)
    vtta__qjuae = c.pyapi.from_native_value(typ.data, zgsw__tlx.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, zgsw__tlx.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, zgsw__tlx.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([vtta__qjuae])
    kws = c.pyapi.dict_pack([('name', nqtiq__nslf)])
    cwyl__pnoav = c.pyapi.object_getattr_string(ckxf__cvmt, 'CategoricalIndex')
    ggoc__jshm = c.pyapi.call(cwyl__pnoav, args, kws)
    c.pyapi.decref(vtta__qjuae)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(ckxf__cvmt)
    c.pyapi.decref(cwyl__pnoav)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return ggoc__jshm


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    mhq__sfl = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, mhq__sfl).value
    nqtiq__nslf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nqtiq__nslf).value
    c.pyapi.decref(mhq__sfl)
    c.pyapi.decref(nqtiq__nslf)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nov__uenru.data = data
    nov__uenru.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    nvr__rieu, laz__xxqi = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    nov__uenru.dict = laz__xxqi
    return NativeValue(nov__uenru._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        skkn__ngqsq, wwp__uhch = args
        zgsw__tlx = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        zgsw__tlx.data = skkn__ngqsq
        zgsw__tlx.name = wwp__uhch
        context.nrt.incref(builder, signature.args[0], skkn__ngqsq)
        context.nrt.incref(builder, signature.args[1], wwp__uhch)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        zgsw__tlx.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return zgsw__tlx._getvalue()
    ctd__zqtfg = CategoricalIndexType(data, name)
    sig = signature(ctd__zqtfg, data, name)
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
    xbvb__ksriz = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    czkv__ggv = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', czkv__ggv,
        idx_cpy_arg_defaults, fn_str=xbvb__ksriz, package_name='pandas',
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
        ncspl__xjkhq = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, ncspl__xjkhq
            )


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    ckxf__cvmt = c.pyapi.import_module_noblock(skow__dmu)
    tghul__moil = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, tghul__moil.data)
    vtta__qjuae = c.pyapi.from_native_value(typ.data, tghul__moil.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, tghul__moil.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, tghul__moil.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([vtta__qjuae])
    kws = c.pyapi.dict_pack([('name', nqtiq__nslf)])
    cwyl__pnoav = c.pyapi.object_getattr_string(ckxf__cvmt, 'IntervalIndex')
    ggoc__jshm = c.pyapi.call(cwyl__pnoav, args, kws)
    c.pyapi.decref(vtta__qjuae)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(ckxf__cvmt)
    c.pyapi.decref(cwyl__pnoav)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return ggoc__jshm


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    mhq__sfl = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, mhq__sfl).value
    nqtiq__nslf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nqtiq__nslf).value
    c.pyapi.decref(mhq__sfl)
    c.pyapi.decref(nqtiq__nslf)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nov__uenru.data = data
    nov__uenru.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    nvr__rieu, laz__xxqi = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    nov__uenru.dict = laz__xxqi
    return NativeValue(nov__uenru._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        skkn__ngqsq, wwp__uhch = args
        tghul__moil = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        tghul__moil.data = skkn__ngqsq
        tghul__moil.name = wwp__uhch
        context.nrt.incref(builder, signature.args[0], skkn__ngqsq)
        context.nrt.incref(builder, signature.args[1], wwp__uhch)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        tghul__moil.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return tghul__moil._getvalue()
    ctd__zqtfg = IntervalIndexType(data, name)
    sig = signature(ctd__zqtfg, data, name)
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
        ncspl__xjkhq = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, ncspl__xjkhq)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    xbvb__ksriz = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    czkv__ggv = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', czkv__ggv, idx_cpy_arg_defaults,
        fn_str=xbvb__ksriz, package_name='pandas', module_name='Index')
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
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    unsrm__pkusz = c.pyapi.import_module_noblock(skow__dmu)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, nov__uenru.data)
    gjycm__lrenq = c.pyapi.from_native_value(typ.data, nov__uenru.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, nov__uenru.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, nov__uenru.name,
        c.env_manager)
    gdmfn__iepv = c.pyapi.make_none()
    tcp__vfeb = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_, 
        False))
    mgmc__kpjtu = c.pyapi.call_method(unsrm__pkusz, 'Index', (gjycm__lrenq,
        gdmfn__iepv, tcp__vfeb, nqtiq__nslf))
    c.pyapi.decref(gjycm__lrenq)
    c.pyapi.decref(gdmfn__iepv)
    c.pyapi.decref(tcp__vfeb)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(unsrm__pkusz)
    c.context.nrt.decref(c.builder, typ, val)
    return mgmc__kpjtu


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        qcu__ktqol = signature.return_type
        nov__uenru = cgutils.create_struct_proxy(qcu__ktqol)(context, builder)
        nov__uenru.data = args[0]
        nov__uenru.name = args[1]
        context.nrt.incref(builder, qcu__ktqol.data, args[0])
        context.nrt.incref(builder, qcu__ktqol.name_typ, args[1])
        dtype = qcu__ktqol.dtype
        nov__uenru.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return nov__uenru._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    mhq__sfl = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, mhq__sfl).value
    nqtiq__nslf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nqtiq__nslf).value
    c.pyapi.decref(mhq__sfl)
    c.pyapi.decref(nqtiq__nslf)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nov__uenru.data = data
    nov__uenru.name = name
    dtype = typ.dtype
    nvr__rieu, laz__xxqi = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    nov__uenru.dict = laz__xxqi
    return NativeValue(nov__uenru._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        yplj__lcdc = dict(dtype=dtype)
        chtis__mgv = dict(dtype=None)
        check_unsupported_args(func_str, yplj__lcdc, chtis__mgv,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                mixqb__oswjl = bodo.utils.conversion.coerce_to_ndarray(data)
                oyiax__ijay = bodo.utils.conversion.fix_arr_dtype(mixqb__oswjl,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(
                    oyiax__ijay, name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                mixqb__oswjl = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    mixqb__oswjl = mixqb__oswjl.copy()
                oyiax__ijay = bodo.utils.conversion.fix_arr_dtype(mixqb__oswjl,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(
                    oyiax__ijay, name)
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
        ncspl__xjkhq = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, ncspl__xjkhq)


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
        ncspl__xjkhq = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, ncspl__xjkhq)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    updhl__vgy = typ.data
    scalar_type = typ.data.dtype
    mhq__sfl = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(updhl__vgy, mhq__sfl).value
    nqtiq__nslf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nqtiq__nslf).value
    c.pyapi.decref(mhq__sfl)
    c.pyapi.decref(nqtiq__nslf)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nov__uenru.data = data
    nov__uenru.name = name
    nvr__rieu, laz__xxqi = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(scalar_type, types.int64), types.DictType(scalar_type, types.
        int64)(), [])
    nov__uenru.dict = laz__xxqi
    return NativeValue(nov__uenru._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    updhl__vgy = typ.data
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    unsrm__pkusz = c.pyapi.import_module_noblock(skow__dmu)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, updhl__vgy, nov__uenru.data)
    gjycm__lrenq = c.pyapi.from_native_value(updhl__vgy, nov__uenru.data, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, nov__uenru.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, nov__uenru.name,
        c.env_manager)
    gdmfn__iepv = c.pyapi.make_none()
    tcp__vfeb = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_, 
        False))
    mgmc__kpjtu = c.pyapi.call_method(unsrm__pkusz, 'Index', (gjycm__lrenq,
        gdmfn__iepv, tcp__vfeb, nqtiq__nslf))
    c.pyapi.decref(gjycm__lrenq)
    c.pyapi.decref(gdmfn__iepv)
    c.pyapi.decref(tcp__vfeb)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(unsrm__pkusz)
    c.context.nrt.decref(c.builder, typ, val)
    return mgmc__kpjtu


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name,
        data)(data, name)
    abwhn__lmn = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, abwhn__lmn


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        okcye__fhp = 'bytes_type'
    else:
        okcye__fhp = 'string_type'
    byk__jnbzo = 'def impl(context, builder, signature, args):\n'
    byk__jnbzo += '    assert len(args) == 2\n'
    byk__jnbzo += '    index_typ = signature.return_type\n'
    byk__jnbzo += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    byk__jnbzo += '    index_val.data = args[0]\n'
    byk__jnbzo += '    index_val.name = args[1]\n'
    byk__jnbzo += '    # increase refcount of stored values\n'
    byk__jnbzo += (
        '    context.nrt.incref(builder, signature.args[0], args[0])\n')
    byk__jnbzo += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    byk__jnbzo += '    # create empty dict for get_loc hashmap\n'
    byk__jnbzo += '    index_val.dict = context.compile_internal(\n'
    byk__jnbzo += '       builder,\n'
    byk__jnbzo += (
        f'       lambda: numba.typed.Dict.empty({okcye__fhp}, types.int64),\n')
    byk__jnbzo += (
        f'        types.DictType({okcye__fhp}, types.int64)(), [],)\n')
    byk__jnbzo += '    return index_val._getvalue()\n'
    wrho__oyzq = {}
    exec(byk__jnbzo, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type}, wrho__oyzq)
    impl = wrho__oyzq['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    xbvb__ksriz = idx_typ_to_format_str_map[typ].format('copy()')
    czkv__ggv = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', czkv__ggv, idx_cpy_arg_defaults,
        fn_str=xbvb__ksriz, package_name='pandas', module_name='Index')
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
    yqpwd__zfhk = I.dtype if not isinstance(I, RangeIndexType) else types.int64
    tnypf__wdvy = other.dtype if not isinstance(other, RangeIndexType
        ) else types.int64
    if yqpwd__zfhk != tnypf__wdvy:
        raise BodoError(
            f'Index.{func_name}(): incompatible types {yqpwd__zfhk} and {tnypf__wdvy}'
            )


@overload_method(NumericIndexType, 'union', inline='always')
@overload_method(StringIndexType, 'union', inline='always')
@overload_method(BinaryIndexType, 'union', inline='always')
@overload_method(DatetimeIndexType, 'union', inline='always')
@overload_method(TimedeltaIndexType, 'union', inline='always')
@overload_method(RangeIndexType, 'union', inline='always')
def overload_index_union(I, other, sort=None):
    xhyri__ochcw = dict(sort=sort)
    psu__vtc = dict(sort=None)
    check_unsupported_args('Index.union', xhyri__ochcw, psu__vtc,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('union', I, other)
    qgbmi__pli = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        pios__tdaxt = bodo.utils.conversion.coerce_to_array(I)
        ecpte__ktig = bodo.utils.conversion.coerce_to_array(other)
        rjark__xquki = bodo.libs.array_kernels.concat([pios__tdaxt,
            ecpte__ktig])
        rmbw__fkwkr = bodo.libs.array_kernels.unique(rjark__xquki)
        return qgbmi__pli(rmbw__fkwkr, None)
    return impl


@overload_method(NumericIndexType, 'intersection', inline='always')
@overload_method(StringIndexType, 'intersection', inline='always')
@overload_method(BinaryIndexType, 'intersection', inline='always')
@overload_method(DatetimeIndexType, 'intersection', inline='always')
@overload_method(TimedeltaIndexType, 'intersection', inline='always')
@overload_method(RangeIndexType, 'intersection', inline='always')
def overload_index_intersection(I, other, sort=None):
    xhyri__ochcw = dict(sort=sort)
    psu__vtc = dict(sort=None)
    check_unsupported_args('Index.intersection', xhyri__ochcw, psu__vtc,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('intersection', I, other)
    qgbmi__pli = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        pios__tdaxt = bodo.utils.conversion.coerce_to_array(I)
        ecpte__ktig = bodo.utils.conversion.coerce_to_array(other)
        twqgl__dpemr = bodo.libs.array_kernels.unique(pios__tdaxt)
        tdys__mcr = bodo.libs.array_kernels.unique(ecpte__ktig)
        rjark__xquki = bodo.libs.array_kernels.concat([twqgl__dpemr, tdys__mcr]
            )
        ziquv__qoux = pd.Series(rjark__xquki).sort_values().values
        alxm__kyjiz = bodo.libs.array_kernels.intersection_mask(ziquv__qoux)
        return qgbmi__pli(ziquv__qoux[alxm__kyjiz], None)
    return impl


@overload_method(NumericIndexType, 'difference', inline='always')
@overload_method(StringIndexType, 'difference', inline='always')
@overload_method(BinaryIndexType, 'difference', inline='always')
@overload_method(DatetimeIndexType, 'difference', inline='always')
@overload_method(TimedeltaIndexType, 'difference', inline='always')
@overload_method(RangeIndexType, 'difference', inline='always')
def overload_index_difference(I, other, sort=None):
    xhyri__ochcw = dict(sort=sort)
    psu__vtc = dict(sort=None)
    check_unsupported_args('Index.difference', xhyri__ochcw, psu__vtc,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('difference', I, other)
    qgbmi__pli = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        pios__tdaxt = bodo.utils.conversion.coerce_to_array(I)
        ecpte__ktig = bodo.utils.conversion.coerce_to_array(other)
        twqgl__dpemr = bodo.libs.array_kernels.unique(pios__tdaxt)
        tdys__mcr = bodo.libs.array_kernels.unique(ecpte__ktig)
        alxm__kyjiz = np.empty(len(twqgl__dpemr), np.bool_)
        bodo.libs.array.array_isin(alxm__kyjiz, twqgl__dpemr, tdys__mcr, False)
        return qgbmi__pli(twqgl__dpemr[~alxm__kyjiz], None)
    return impl


@overload_method(NumericIndexType, 'symmetric_difference', inline='always')
@overload_method(StringIndexType, 'symmetric_difference', inline='always')
@overload_method(BinaryIndexType, 'symmetric_difference', inline='always')
@overload_method(DatetimeIndexType, 'symmetric_difference', inline='always')
@overload_method(TimedeltaIndexType, 'symmetric_difference', inline='always')
@overload_method(RangeIndexType, 'symmetric_difference', inline='always')
def overload_index_symmetric_difference(I, other, result_name=None, sort=None):
    xhyri__ochcw = dict(result_name=result_name, sort=sort)
    psu__vtc = dict(result_name=None, sort=None)
    check_unsupported_args('Index.symmetric_difference', xhyri__ochcw,
        psu__vtc, package_name='pandas', module_name='Index')
    _verify_setop_compatible('symmetric_difference', I, other)
    qgbmi__pli = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, result_name=None, sort=None):
        pios__tdaxt = bodo.utils.conversion.coerce_to_array(I)
        ecpte__ktig = bodo.utils.conversion.coerce_to_array(other)
        twqgl__dpemr = bodo.libs.array_kernels.unique(pios__tdaxt)
        tdys__mcr = bodo.libs.array_kernels.unique(ecpte__ktig)
        ttsm__bupg = np.empty(len(twqgl__dpemr), np.bool_)
        dvf__qla = np.empty(len(tdys__mcr), np.bool_)
        bodo.libs.array.array_isin(ttsm__bupg, twqgl__dpemr, tdys__mcr, False)
        bodo.libs.array.array_isin(dvf__qla, tdys__mcr, twqgl__dpemr, False)
        yilzj__usdt = bodo.libs.array_kernels.concat([twqgl__dpemr[~
            ttsm__bupg], tdys__mcr[~dvf__qla]])
        return qgbmi__pli(yilzj__usdt, None)
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
    xhyri__ochcw = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value
        )
    psu__vtc = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', xhyri__ochcw, psu__vtc,
        package_name='pandas', module_name='Index')
    return lambda I, indices: I[indices]


def _init_engine(I, ban_unique=True):
    pass


@overload(_init_engine)
def overload_init_engine(I, ban_unique=True):
    if isinstance(I, CategoricalIndexType):

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                lkr__abdn = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(lkr__abdn)):
                    if not bodo.libs.array_kernels.isna(lkr__abdn, i):
                        val = (bodo.hiframes.pd_categorical_ext.
                            get_code_for_value(lkr__abdn.dtype, lkr__abdn[i]))
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl
    else:

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                lkr__abdn = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(lkr__abdn)):
                    if not bodo.libs.array_kernels.isna(lkr__abdn, i):
                        val = lkr__abdn[i]
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
                lkr__abdn = bodo.utils.conversion.coerce_to_array(I)
                zdyid__rcry = (bodo.hiframes.pd_categorical_ext.
                    get_code_for_value(lkr__abdn.dtype, key))
                return zdyid__rcry in I._dict
            else:
                vygo__oxz = (
                    'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                    )
                warnings.warn(vygo__oxz)
                lkr__abdn = bodo.utils.conversion.coerce_to_array(I)
                ind = -1
                for i in range(len(lkr__abdn)):
                    if not bodo.libs.array_kernels.isna(lkr__abdn, i):
                        if lkr__abdn[i] == key:
                            ind = i
            return ind != -1
        return impl

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I, False)
            return key in I._dict
        else:
            vygo__oxz = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(vygo__oxz)
            lkr__abdn = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(lkr__abdn)):
                if not bodo.libs.array_kernels.isna(lkr__abdn, i):
                    if lkr__abdn[i] == key:
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
    xhyri__ochcw = dict(method=method, tolerance=tolerance)
    gju__epwlp = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', xhyri__ochcw, gju__epwlp,
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
            vygo__oxz = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(vygo__oxz)
            lkr__abdn = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(lkr__abdn)):
                if lkr__abdn[i] == key:
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
        qsrde__kcwfp = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                yxvx__ksf = len(I)
                uih__aruj = np.empty(yxvx__ksf, np.bool_)
                for i in numba.parfors.parfor.internal_prange(yxvx__ksf):
                    uih__aruj[i] = not qsrde__kcwfp
                return uih__aruj
            return impl
        byk__jnbzo = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if qsrde__kcwfp else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        wrho__oyzq = {}
        exec(byk__jnbzo, {'bodo': bodo, 'np': np, 'numba': numba}, wrho__oyzq)
        impl = wrho__oyzq['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for ani__mymy in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(ani__mymy, overload_name, no_unliteral=True,
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
            lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(lkr__abdn, 1)
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
            lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(lkr__abdn, 2)
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
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        uih__aruj = bodo.libs.array_kernels.duplicated((lkr__abdn,))
        return uih__aruj
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
    xhyri__ochcw = dict(keep=keep)
    gju__epwlp = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', xhyri__ochcw,
        gju__epwlp, package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    byk__jnbzo = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        byk__jnbzo += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        byk__jnbzo += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    wrho__oyzq = {}
    exec(byk__jnbzo, {'bodo': bodo}, wrho__oyzq)
    impl = wrho__oyzq['impl']
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
    ffv__otx = args[0]
    if isinstance(self.typemap[ffv__otx.name], (HeterogeneousIndexType,
        MultiIndexType)):
        return None
    if equiv_set.has_shape(ffv__otx):
        return ArrayAnalysis.AnalyzeResult(shape=ffv__otx, pre=[])
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
    xhyri__ochcw = dict(na_action=na_action)
    mkcyg__ryedz = dict(na_action=None)
    check_unsupported_args('Index.map', xhyri__ochcw, mkcyg__ryedz,
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
    sehx__rixv = numba.core.registry.cpu_target.typing_context
    rkybu__cpr = numba.core.registry.cpu_target.target_context
    try:
        vkekm__chkk = get_const_func_output_type(mapper, (dtype,), {},
            sehx__rixv, rkybu__cpr)
    except Exception as nrkr__gbuy:
        raise_bodo_error(get_udf_error_msg('Index.map()', nrkr__gbuy))
    afylo__mvt = get_udf_out_arr_type(vkekm__chkk)
    func = get_overload_const_func(mapper, None)
    byk__jnbzo = 'def f(I, mapper, na_action=None):\n'
    byk__jnbzo += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    byk__jnbzo += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    byk__jnbzo += '  numba.parfors.parfor.init_prange()\n'
    byk__jnbzo += '  n = len(A)\n'
    byk__jnbzo += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    byk__jnbzo += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    byk__jnbzo += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    byk__jnbzo += '    v = map_func(t2)\n'
    byk__jnbzo += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    byk__jnbzo += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    ozaf__ihu = bodo.compiler.udf_jit(func)
    wrho__oyzq = {}
    exec(byk__jnbzo, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': ozaf__ihu, '_arr_typ': afylo__mvt, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'data_arr_type': afylo__mvt.dtype
        }, wrho__oyzq)
    f = wrho__oyzq['f']
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
    fxa__fqls, jgzy__xogs = sig.args
    if fxa__fqls != jgzy__xogs:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    fxa__fqls, jgzy__xogs = sig.args
    if fxa__fqls != jgzy__xogs:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):
            byk__jnbzo = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(lhs)
"""
            if rhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                byk__jnbzo += """  dt = bodo.utils.conversion.unbox_if_timestamp(rhs)
  return op(arr, dt)
"""
            else:
                byk__jnbzo += """  rhs_arr = bodo.utils.conversion.get_array_if_series_or_index(rhs)
  return op(arr, rhs_arr)
"""
            wrho__oyzq = {}
            exec(byk__jnbzo, {'bodo': bodo, 'op': op}, wrho__oyzq)
            impl = wrho__oyzq['impl']
            return impl
        if is_index_type(rhs):
            byk__jnbzo = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(rhs)
"""
            if lhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                byk__jnbzo += """  dt = bodo.utils.conversion.unbox_if_timestamp(lhs)
  return op(dt, arr)
"""
            else:
                byk__jnbzo += """  lhs_arr = bodo.utils.conversion.get_array_if_series_or_index(lhs)
  return op(lhs_arr, arr)
"""
            wrho__oyzq = {}
            exec(byk__jnbzo, {'bodo': bodo, 'op': op}, wrho__oyzq)
            impl = wrho__oyzq['impl']
            return impl
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    lkr__abdn = bodo.utils.conversion.coerce_to_array(data)
                    ajw__fgreh = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    uih__aruj = op(lkr__abdn, ajw__fgreh)
                    return uih__aruj
                return impl3
            count = len(lhs.data.types)
            byk__jnbzo = 'def f(lhs, rhs):\n'
            byk__jnbzo += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            wrho__oyzq = {}
            exec(byk__jnbzo, {'op': op, 'np': np}, wrho__oyzq)
            impl = wrho__oyzq['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    lkr__abdn = bodo.utils.conversion.coerce_to_array(data)
                    ajw__fgreh = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    uih__aruj = op(ajw__fgreh, lkr__abdn)
                    return uih__aruj
                return impl4
            count = len(rhs.data.types)
            byk__jnbzo = 'def f(lhs, rhs):\n'
            byk__jnbzo += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            wrho__oyzq = {}
            exec(byk__jnbzo, {'op': op, 'np': np}, wrho__oyzq)
            impl = wrho__oyzq['f']
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
        ncspl__xjkhq = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type,
            ncspl__xjkhq)


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    xbvb__ksriz = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    czkv__ggv = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', czkv__ggv, idx_cpy_arg_defaults,
        fn_str=xbvb__ksriz, package_name='pandas', module_name='Index')
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
    skow__dmu = c.context.insert_const_string(c.builder.module, 'pandas')
    unsrm__pkusz = c.pyapi.import_module_noblock(skow__dmu)
    nov__uenru = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, nov__uenru.data)
    gjycm__lrenq = c.pyapi.from_native_value(typ.data, nov__uenru.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, nov__uenru.name)
    nqtiq__nslf = c.pyapi.from_native_value(typ.name_typ, nov__uenru.name,
        c.env_manager)
    gdmfn__iepv = c.pyapi.make_none()
    tcp__vfeb = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_, 
        False))
    mgmc__kpjtu = c.pyapi.call_method(unsrm__pkusz, 'Index', (gjycm__lrenq,
        gdmfn__iepv, tcp__vfeb, nqtiq__nslf))
    c.pyapi.decref(gjycm__lrenq)
    c.pyapi.decref(gdmfn__iepv)
    c.pyapi.decref(tcp__vfeb)
    c.pyapi.decref(nqtiq__nslf)
    c.pyapi.decref(unsrm__pkusz)
    c.context.nrt.decref(c.builder, typ, val)
    return mgmc__kpjtu


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        qcu__ktqol = signature.return_type
        nov__uenru = cgutils.create_struct_proxy(qcu__ktqol)(context, builder)
        nov__uenru.data = args[0]
        nov__uenru.name = args[1]
        context.nrt.incref(builder, qcu__ktqol.data, args[0])
        context.nrt.incref(builder, qcu__ktqol.name_typ, args[1])
        return nov__uenru._getvalue()
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
        byk__jnbzo = 'def _impl_nbytes(I):\n'
        byk__jnbzo += '    total = 0\n'
        byk__jnbzo += '    data = I._data\n'
        for i in range(I.nlevels):
            byk__jnbzo += f'    total += data[{i}].nbytes\n'
        byk__jnbzo += '    return total\n'
        rmpi__vgoio = {}
        exec(byk__jnbzo, {}, rmpi__vgoio)
        return rmpi__vgoio['_impl_nbytes']
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
        dicxg__vzwd = 'bodo.hiframes.pd_index_ext.get_index_name(I)'
    else:
        dicxg__vzwd = 'name'
    byk__jnbzo = 'def impl(I, index=None, name=None):\n'
    byk__jnbzo += '    data = bodo.utils.conversion.index_to_array(I)\n'
    if is_overload_none(index):
        byk__jnbzo += '    new_index = I\n'
    elif is_pd_index_type(index):
        byk__jnbzo += '    new_index = index\n'
    elif isinstance(index, SeriesType):
        byk__jnbzo += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        byk__jnbzo += (
            '    index_name = bodo.hiframes.pd_series_ext.get_series_name(index)\n'
            )
        byk__jnbzo += (
            '    new_index = bodo.utils.conversion.index_from_array(arr, index_name)\n'
            )
    elif bodo.utils.utils.is_array_typ(index, False):
        byk__jnbzo += (
            '    new_index = bodo.utils.conversion.index_from_array(index)\n')
    elif isinstance(index, (types.List, types.BaseTuple)):
        byk__jnbzo += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        byk__jnbzo += (
            '    new_index = bodo.utils.conversion.index_from_array(arr)\n')
    else:
        raise_bodo_error(
            f'Index.to_series(): unsupported type for argument index: {type(index).__name__}'
            )
    byk__jnbzo += f'    new_name = {dicxg__vzwd}\n'
    byk__jnbzo += (
        '    return bodo.hiframes.pd_series_ext.init_series(data, new_index, new_name)'
        )
    wrho__oyzq = {}
    exec(byk__jnbzo, {'bodo': bodo, 'np': np}, wrho__oyzq)
    impl = wrho__oyzq['impl']
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
        qqhz__opgh = 'I'
    elif is_overload_false(index):
        qqhz__opgh = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'Index.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'Index.to_frame(): index argument must be a compile time constant')
    byk__jnbzo = 'def impl(I, index=True, name=None):\n'
    byk__jnbzo += '    data = bodo.utils.conversion.index_to_array(I)\n'
    byk__jnbzo += f'    new_index = {qqhz__opgh}\n'
    if is_overload_none(name) and I.name_typ == types.none:
        wdia__aks = ColNamesMetaType((0,))
    elif is_overload_none(name):
        wdia__aks = ColNamesMetaType((I.name_typ,))
    elif is_overload_constant_str(name):
        wdia__aks = ColNamesMetaType((get_overload_const_str(name),))
    elif is_overload_constant_int(name):
        wdia__aks = ColNamesMetaType((get_overload_const_int(name),))
    else:
        raise_bodo_error(
            f'Index.to_frame(): only constant string/int are supported for argument name'
            )
    byk__jnbzo += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((data,), new_index, __col_name_meta_value)
"""
    wrho__oyzq = {}
    exec(byk__jnbzo, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        wdia__aks}, wrho__oyzq)
    impl = wrho__oyzq['impl']
    return impl


@overload_method(MultiIndexType, 'to_frame', inline='always', no_unliteral=True
    )
def overload_multi_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        qqhz__opgh = 'I'
    elif is_overload_false(index):
        qqhz__opgh = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a compile time constant'
            )
    byk__jnbzo = 'def impl(I, index=True, name=None):\n'
    byk__jnbzo += '    data = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    byk__jnbzo += f'    new_index = {qqhz__opgh}\n'
    mvt__dsykt = len(I.array_types)
    if is_overload_none(name) and I.names_typ == (types.none,) * mvt__dsykt:
        wdia__aks = ColNamesMetaType(tuple(range(mvt__dsykt)))
    elif is_overload_none(name):
        wdia__aks = ColNamesMetaType(I.names_typ)
    elif is_overload_constant_tuple(name) or is_overload_constant_list(name):
        if is_overload_constant_list(name):
            names = tuple(get_overload_const_list(name))
        else:
            names = get_overload_const_tuple(name)
        if mvt__dsykt != len(names):
            raise_bodo_error(
                f'MultiIndex.to_frame(): expected {mvt__dsykt} names, not {len(names)}'
                )
        if all(is_overload_constant_str(wekvo__nbn) or
            is_overload_constant_int(wekvo__nbn) for wekvo__nbn in names):
            wdia__aks = ColNamesMetaType(names)
        else:
            raise_bodo_error(
                'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
                )
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
            )
    byk__jnbzo += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(data, new_index, __col_name_meta_value,)
"""
    wrho__oyzq = {}
    exec(byk__jnbzo, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        wdia__aks}, wrho__oyzq)
    impl = wrho__oyzq['impl']
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
    xhyri__ochcw = dict(dtype=dtype, na_value=na_value)
    gju__epwlp = dict(dtype=None, na_value=None)
    check_unsupported_args('Index.to_numpy', xhyri__ochcw, gju__epwlp,
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
            zipo__wrs = list()
            for i in range(I._start, I._stop, I.step):
                zipo__wrs.append(i)
            return zipo__wrs
        return impl

    def impl(I):
        zipo__wrs = list()
        for i in range(len(I)):
            zipo__wrs.append(I[i])
        return zipo__wrs
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
    vbfb__fbn = {DatetimeIndexType: 'datetime64', TimedeltaIndexType:
        'timedelta64', RangeIndexType: 'integer', BinaryIndexType: 'bytes',
        CategoricalIndexType: 'categorical', PeriodIndexType: 'period',
        IntervalIndexType: 'interval', MultiIndexType: 'mixed'}
    inferred_type = vbfb__fbn[type(I)]
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
    mudyo__gqzm = {DatetimeIndexType: np.dtype('datetime64[ns]'),
        TimedeltaIndexType: np.dtype('timedelta64[ns]'), RangeIndexType: np
        .dtype('int64'), StringIndexType: np.dtype('O'), BinaryIndexType:
        np.dtype('O'), MultiIndexType: np.dtype('O')}
    dtype = mudyo__gqzm[type(I)]
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
    otsb__pou = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in otsb__pou:
        init_func = otsb__pou[type(I)]
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
    urp__tgse = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index, RangeIndexType: bodo.
        hiframes.pd_index_ext.init_range_index}
    if type(I) in urp__tgse:
        return urp__tgse[type(I)]
    raise BodoError(
        f'Unsupported type for standard Index constructor: {type(I)}')


@overload_method(NumericIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'min', no_unliteral=True, inline=
    'always')
def overload_index_min(I, axis=None, skipna=True):
    xhyri__ochcw = dict(axis=axis, skipna=skipna)
    gju__epwlp = dict(axis=None, skipna=True)
    check_unsupported_args('Index.min', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            rzi__igfbq = len(I)
            if rzi__igfbq == 0:
                return np.nan
            if I._step < 0:
                return I._start + I._step * (rzi__igfbq - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.min(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_min(lkr__abdn)
    return impl


@overload_method(NumericIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'max', no_unliteral=True, inline=
    'always')
def overload_index_max(I, axis=None, skipna=True):
    xhyri__ochcw = dict(axis=axis, skipna=skipna)
    gju__epwlp = dict(axis=None, skipna=True)
    check_unsupported_args('Index.max', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            rzi__igfbq = len(I)
            if rzi__igfbq == 0:
                return np.nan
            if I._step > 0:
                return I._start + I._step * (rzi__igfbq - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.max(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_max(lkr__abdn)
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
    xhyri__ochcw = dict(axis=axis, skipna=skipna)
    gju__epwlp = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmin', xhyri__ochcw, gju__epwlp,
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
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = init_numeric_index(np.arange(len(lkr__abdn)))
        return bodo.libs.array_ops.array_op_idxmin(lkr__abdn, index)
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
    xhyri__ochcw = dict(axis=axis, skipna=skipna)
    gju__epwlp = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmax', xhyri__ochcw, gju__epwlp,
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
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = np.arange(len(lkr__abdn))
        return bodo.libs.array_ops.array_op_idxmax(lkr__abdn, index)
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
    qgbmi__pli = get_index_constructor(I)

    def impl(I):
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        lmqlx__tev = bodo.libs.array_kernels.unique(lkr__abdn)
        return qgbmi__pli(lmqlx__tev, name)
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
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        yxvx__ksf = bodo.libs.array_kernels.nunique(lkr__abdn, dropna)
        return yxvx__ksf
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
            izl__fmn = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_index_ext.get_index_data(I)
            yxvx__ksf = len(A)
            uih__aruj = np.empty(yxvx__ksf, np.bool_)
            bodo.libs.array.array_isin(uih__aruj, A, izl__fmn, False)
            return uih__aruj
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        uih__aruj = bodo.libs.array_ops.array_op_isin(A, values)
        return uih__aruj
    return impl


@overload_method(RangeIndexType, 'isin', no_unliteral=True, inline='always')
def overload_range_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            izl__fmn = bodo.utils.conversion.coerce_to_array(values)
            A = np.arange(I.start, I.stop, I.step)
            yxvx__ksf = len(A)
            uih__aruj = np.empty(yxvx__ksf, np.bool_)
            bodo.libs.array.array_isin(uih__aruj, A, izl__fmn, False)
            return uih__aruj
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Index.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = np.arange(I.start, I.stop, I.step)
        uih__aruj = bodo.libs.array_ops.array_op_isin(A, values)
        return uih__aruj
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
        rzi__igfbq = len(I)
        fczk__mfyt = start + step * (rzi__igfbq - 1)
        whrks__qjpp = fczk__mfyt - step * rzi__igfbq
        return init_range_index(fczk__mfyt, whrks__qjpp, -step, name)


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
    xhyri__ochcw = dict(return_indexer=return_indexer, key=key)
    gju__epwlp = dict(return_indexer=False, key=None)
    check_unsupported_args('Index.sort_values', xhyri__ochcw, gju__epwlp,
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
    qgbmi__pli = get_index_constructor(I)
    qijce__hjc = ColNamesMetaType(('$_bodo_col_',))

    def impl(I, return_indexer=False, ascending=True, na_position='last',
        key=None):
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = get_index_name(I)
        index = init_range_index(0, len(lkr__abdn), 1, None)
        jgwnt__fqe = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            lkr__abdn,), index, qijce__hjc)
        iwitt__ysu = jgwnt__fqe.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=False, na_position=na_position)
        uih__aruj = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            iwitt__ysu, 0)
        return qgbmi__pli(uih__aruj, name)
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
    xhyri__ochcw = dict(axis=axis, kind=kind, order=order)
    gju__epwlp = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Index.argsort', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, kind='quicksort', order=None):
            if I._step > 0:
                return np.arange(0, len(I), 1)
            else:
                return np.arange(len(I) - 1, -1, -1)
        return impl

    def impl(I, axis=0, kind='quicksort', order=None):
        lkr__abdn = bodo.hiframes.pd_index_ext.get_index_data(I)
        uih__aruj = bodo.hiframes.series_impl.argsort(lkr__abdn)
        return uih__aruj
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
        uxjx__thsq = 'None'
    else:
        uxjx__thsq = 'other'
    byk__jnbzo = 'def impl(I, cond, other=np.nan):\n'
    if isinstance(I, RangeIndexType):
        byk__jnbzo += '  arr = np.arange(I._start, I._stop, I._step)\n'
        qgbmi__pli = 'init_numeric_index'
    else:
        byk__jnbzo += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    byk__jnbzo += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    byk__jnbzo += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {uxjx__thsq})\n'
        )
    byk__jnbzo += f'  return constructor(out_arr, name)\n'
    wrho__oyzq = {}
    qgbmi__pli = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(byk__jnbzo, {'bodo': bodo, 'np': np, 'constructor': qgbmi__pli},
        wrho__oyzq)
    impl = wrho__oyzq['impl']
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
        uxjx__thsq = 'None'
    else:
        uxjx__thsq = 'other'
    byk__jnbzo = 'def impl(I, cond, other):\n'
    byk__jnbzo += '  cond = ~cond\n'
    if isinstance(I, RangeIndexType):
        byk__jnbzo += '  arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        byk__jnbzo += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    byk__jnbzo += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    byk__jnbzo += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {uxjx__thsq})\n'
        )
    byk__jnbzo += f'  return constructor(out_arr, name)\n'
    wrho__oyzq = {}
    qgbmi__pli = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(byk__jnbzo, {'bodo': bodo, 'np': np, 'constructor': qgbmi__pli},
        wrho__oyzq)
    impl = wrho__oyzq['impl']
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
    xhyri__ochcw = dict(axis=axis)
    gju__epwlp = dict(axis=None)
    check_unsupported_args('Index.repeat', xhyri__ochcw, gju__epwlp,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Index.repeat(): 'repeats' should be an integer or array of integers"
            )
    byk__jnbzo = 'def impl(I, repeats, axis=None):\n'
    if not isinstance(repeats, types.Integer):
        byk__jnbzo += (
            '    repeats = bodo.utils.conversion.coerce_to_array(repeats)\n')
    if isinstance(I, RangeIndexType):
        byk__jnbzo += '    arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        byk__jnbzo += (
            '    arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n')
    byk__jnbzo += '    name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    byk__jnbzo += (
        '    out_arr = bodo.libs.array_kernels.repeat_kernel(arr, repeats)\n')
    byk__jnbzo += '    return constructor(out_arr, name)'
    wrho__oyzq = {}
    qgbmi__pli = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(byk__jnbzo, {'bodo': bodo, 'np': np, 'constructor': qgbmi__pli},
        wrho__oyzq)
    impl = wrho__oyzq['impl']
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
    xyqn__dpxn = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, xyqn__dpxn])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    xyqn__dpxn = context.get_constant_null(types.DictType(types.int64,
        types.int64))
    return lir.Constant.literal_struct([data, name, xyqn__dpxn])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    xyqn__dpxn = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, xyqn__dpxn])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    updhl__vgy = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, updhl__vgy, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    xyqn__dpxn = context.get_constant_null(types.DictType(scalar_type,
        types.int64))
    return lir.Constant.literal_struct([data, name, xyqn__dpxn])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [rxnwe__eqmf] = sig.args
    [index] = args
    rzmg__nyi = context.make_helper(builder, rxnwe__eqmf, value=index)
    yuodw__jrf = context.make_helper(builder, sig.return_type)
    wxr__xfb = cgutils.alloca_once_value(builder, rzmg__nyi.start)
    mqpd__hkz = context.get_constant(types.intp, 0)
    uvfp__vyclz = cgutils.alloca_once_value(builder, mqpd__hkz)
    yuodw__jrf.iter = wxr__xfb
    yuodw__jrf.stop = rzmg__nyi.stop
    yuodw__jrf.step = rzmg__nyi.step
    yuodw__jrf.count = uvfp__vyclz
    fnfq__ratov = builder.sub(rzmg__nyi.stop, rzmg__nyi.start)
    aked__jyhvd = context.get_constant(types.intp, 1)
    cjia__kbi = builder.icmp_signed('>', fnfq__ratov, mqpd__hkz)
    vvue__ibar = builder.icmp_signed('>', rzmg__nyi.step, mqpd__hkz)
    vaurc__rqwz = builder.not_(builder.xor(cjia__kbi, vvue__ibar))
    with builder.if_then(vaurc__rqwz):
        avp__ilheb = builder.srem(fnfq__ratov, rzmg__nyi.step)
        avp__ilheb = builder.select(cjia__kbi, avp__ilheb, builder.neg(
            avp__ilheb))
        ixw__dwcf = builder.icmp_signed('>', avp__ilheb, mqpd__hkz)
        ikhdy__eifqm = builder.add(builder.sdiv(fnfq__ratov, rzmg__nyi.step
            ), builder.select(ixw__dwcf, aked__jyhvd, mqpd__hkz))
        builder.store(ikhdy__eifqm, uvfp__vyclz)
    ggoc__jshm = yuodw__jrf._getvalue()
    bcn__hfwzx = impl_ret_new_ref(context, builder, sig.return_type, ggoc__jshm
        )
    return bcn__hfwzx


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
    for jydj__nhohb in index_unsupported_methods:
        for rxwno__wogh, typ in index_types:
            overload_method(typ, jydj__nhohb, no_unliteral=True)(
                create_unsupported_overload(rxwno__wogh.format(jydj__nhohb +
                '()')))
    for nhbec__mqjx in index_unsupported_atrs:
        for rxwno__wogh, typ in index_types:
            overload_attribute(typ, nhbec__mqjx, no_unliteral=True)(
                create_unsupported_overload(rxwno__wogh.format(nhbec__mqjx)))
    jwbjz__shos = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    cfy__kyh = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods), (BinaryIndexType,
        binary_index_unsupported_methods), (StringIndexType,
        string_index_unsupported_methods)]
    for typ, mpfef__pgcf in cfy__kyh:
        rxwno__wogh = idx_typ_to_format_str_map[typ]
        for fvv__jels in mpfef__pgcf:
            overload_method(typ, fvv__jels, no_unliteral=True)(
                create_unsupported_overload(rxwno__wogh.format(fvv__jels +
                '()')))
    for typ, rdrtu__jojln in jwbjz__shos:
        rxwno__wogh = idx_typ_to_format_str_map[typ]
        for nhbec__mqjx in rdrtu__jojln:
            overload_attribute(typ, nhbec__mqjx, no_unliteral=True)(
                create_unsupported_overload(rxwno__wogh.format(nhbec__mqjx)))


_install_index_unsupported()
