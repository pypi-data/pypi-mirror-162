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
            pwnio__wll = val.dtype.numpy_dtype
            dtype = numba.np.numpy_support.from_dtype(pwnio__wll)
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
        cviiw__asrva = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(_dt_index_data_typ.dtype, types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, cviiw__asrva)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    drm__ltos = dict(deep=deep, dtype=dtype, names=names)
    cuyrm__tky = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()')
    check_unsupported_args('copy', drm__ltos, idx_cpy_arg_defaults, fn_str=
        cuyrm__tky, package_name='pandas', module_name='Index')
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
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    ciig__hcul = c.pyapi.import_module_noblock(ppke__pyosq)
    ikcn__tqvzx = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, ikcn__tqvzx.data)
    wldk__tws = c.pyapi.from_native_value(typ.data, ikcn__tqvzx.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ikcn__tqvzx.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, ikcn__tqvzx.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([wldk__tws])
    dgtbh__bad = c.pyapi.object_getattr_string(ciig__hcul, 'DatetimeIndex')
    kws = c.pyapi.dict_pack([('name', dpkeg__thv)])
    nonhz__ptqsk = c.pyapi.call(dgtbh__bad, args, kws)
    c.pyapi.decref(wldk__tws)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(ciig__hcul)
    c.pyapi.decref(dgtbh__bad)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return nonhz__ptqsk


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        dnq__fgdp = c.pyapi.object_getattr_string(val, 'array')
    else:
        dnq__fgdp = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, dnq__fgdp).value
    dpkeg__thv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dpkeg__thv).value
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    quvw__ccjb.data = data
    quvw__ccjb.name = name
    dtype = _dt_index_data_typ.dtype
    dkae__hyl, nopst__nsk = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    quvw__ccjb.dict = nopst__nsk
    c.pyapi.decref(dnq__fgdp)
    c.pyapi.decref(dpkeg__thv)
    return NativeValue(quvw__ccjb._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        jvib__uis, gjl__pnrwl = args
        ikcn__tqvzx = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        ikcn__tqvzx.data = jvib__uis
        ikcn__tqvzx.name = gjl__pnrwl
        context.nrt.incref(builder, signature.args[0], jvib__uis)
        context.nrt.incref(builder, signature.args[1], gjl__pnrwl)
        dtype = _dt_index_data_typ.dtype
        ikcn__tqvzx.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return ikcn__tqvzx._getvalue()
    sqmys__niv = DatetimeIndexType(name, data)
    sig = signature(sqmys__niv, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    fdj__sivyx = args[0]
    if equiv_set.has_shape(fdj__sivyx):
        return ArrayAnalysis.AnalyzeResult(shape=fdj__sivyx, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    ulg__nte = 'def impl(dti):\n'
    ulg__nte += '    numba.parfors.parfor.init_prange()\n'
    ulg__nte += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    ulg__nte += '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n'
    ulg__nte += '    n = len(A)\n'
    ulg__nte += '    S = np.empty(n, np.int64)\n'
    ulg__nte += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    ulg__nte += '        val = A[i]\n'
    ulg__nte += '        ts = bodo.utils.conversion.box_if_dt64(val)\n'
    if field in ['weekday']:
        ulg__nte += '        S[i] = ts.' + field + '()\n'
    else:
        ulg__nte += '        S[i] = ts.' + field + '\n'
    ulg__nte += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    ohydy__rgmvy = {}
    exec(ulg__nte, {'numba': numba, 'np': np, 'bodo': bodo}, ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
        vjz__zuza = len(A)
        S = np.empty(vjz__zuza, np.bool_)
        for i in numba.parfors.parfor.internal_prange(vjz__zuza):
            val = A[i]
            tpl__ksw = bodo.utils.conversion.box_if_dt64(val)
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(tpl__ksw.year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        vjz__zuza = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(vjz__zuza
            )
        for i in numba.parfors.parfor.internal_prange(vjz__zuza):
            val = A[i]
            tpl__ksw = bodo.utils.conversion.box_if_dt64(val)
            S[i] = datetime.date(tpl__ksw.year, tpl__ksw.month, tpl__ksw.day)
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
    jfp__lmj = dict(axis=axis, skipna=skipna)
    vswn__kjn = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.min()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        qiv__qlgm = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(qiv__qlgm)):
            if not bodo.libs.array_kernels.isna(qiv__qlgm, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(qiv__qlgm
                    [i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    jfp__lmj = dict(axis=axis, skipna=skipna)
    vswn__kjn = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.max()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        qiv__qlgm = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(qiv__qlgm)):
            if not bodo.libs.array_kernels.isna(qiv__qlgm, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(qiv__qlgm
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
    jfp__lmj = dict(freq=freq, tz=tz, normalize=normalize, closed=closed,
        ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst, dtype=
        dtype, copy=copy)
    vswn__kjn = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        aqqgq__pvz = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(aqqgq__pvz)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        cqx__kjdqw = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            qiv__qlgm = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            vjz__zuza = len(qiv__qlgm)
            S = np.empty(vjz__zuza, cqx__kjdqw)
            qcfzz__fpxfn = rhs.value
            for i in numba.parfors.parfor.internal_prange(vjz__zuza):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    qiv__qlgm[i]) - qcfzz__fpxfn)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        cqx__kjdqw = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            qiv__qlgm = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            vjz__zuza = len(qiv__qlgm)
            S = np.empty(vjz__zuza, cqx__kjdqw)
            qcfzz__fpxfn = lhs.value
            for i in numba.parfors.parfor.internal_prange(vjz__zuza):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    qcfzz__fpxfn - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(qiv__qlgm[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    lrjhv__fce = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    ulg__nte = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        ulg__nte += '  dt_index, _str = lhs, rhs\n'
        pccz__kob = 'arr[i] {} other'.format(lrjhv__fce)
    else:
        ulg__nte += '  dt_index, _str = rhs, lhs\n'
        pccz__kob = 'other {} arr[i]'.format(lrjhv__fce)
    ulg__nte += '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n'
    ulg__nte += '  l = len(arr)\n'
    ulg__nte += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    ulg__nte += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    ulg__nte += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    ulg__nte += '    S[i] = {}\n'.format(pccz__kob)
    ulg__nte += '  return S\n'
    ohydy__rgmvy = {}
    exec(ulg__nte, {'bodo': bodo, 'numba': numba, 'np': np}, ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
        lpyhx__eisg = parse_dtype(dtype, 'pandas.Index')
        ubr__qxs = False
    else:
        lpyhx__eisg = getattr(data, 'dtype', None)
        ubr__qxs = True
    if isinstance(lpyhx__eisg, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType
        ) or lpyhx__eisg == types.NPDatetime('ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType
        ) or lpyhx__eisg == types.NPTimedelta('ns'):

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
        if isinstance(lpyhx__eisg, (types.Integer, types.Float, types.Boolean)
            ):
            if ubr__qxs:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    aqqgq__pvz = bodo.utils.conversion.coerce_to_array(data)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        aqqgq__pvz, name)
            else:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    aqqgq__pvz = bodo.utils.conversion.coerce_to_array(data)
                    rljc__jrq = bodo.utils.conversion.fix_arr_dtype(aqqgq__pvz,
                        lpyhx__eisg)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        rljc__jrq, name)
        elif lpyhx__eisg in [types.string, bytes_type]:

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
                pvn__pmqs = bodo.hiframes.pd_index_ext.get_index_data(dti)
                val = pvn__pmqs[ind]
                return bodo.utils.conversion.box_if_dt64(val)
            return impl
        else:

            def impl(dti, ind):
                pvn__pmqs = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                hvnrq__qllc = pvn__pmqs[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(
                    hvnrq__qllc, name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            peyw__eauew = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(peyw__eauew[ind])
        return impl

    def impl(I, ind):
        peyw__eauew = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        hvnrq__qllc = peyw__eauew[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(hvnrq__qllc,
            name)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_categorical_index_getitem(I, ind):
    if not isinstance(I, CategoricalIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            zks__qvkb = bodo.hiframes.pd_index_ext.get_index_data(I)
            val = zks__qvkb[ind]
            return val
        return impl
    if isinstance(ind, types.SliceType):

        def impl(I, ind):
            zks__qvkb = bodo.hiframes.pd_index_ext.get_index_data(I)
            name = bodo.hiframes.pd_index_ext.get_index_name(I)
            hvnrq__qllc = zks__qvkb[ind]
            return bodo.hiframes.pd_index_ext.init_categorical_index(
                hvnrq__qllc, name)
        return impl
    raise BodoError(
        f'pd.CategoricalIndex.__getitem__: unsupported index type {ind}')


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    kgoy__jkgt = False
    wpxe__tjnvq = False
    if closed is None:
        kgoy__jkgt = True
        wpxe__tjnvq = True
    elif closed == 'left':
        kgoy__jkgt = True
    elif closed == 'right':
        wpxe__tjnvq = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return kgoy__jkgt, wpxe__tjnvq


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
    jfp__lmj = dict(tz=tz, normalize=normalize, closed=closed)
    vswn__kjn = dict(tz=None, normalize=False, closed=None)
    check_unsupported_args('pandas.date_range', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise_bodo_error('pd.date_range(): tz argument not supported yet')
    hrspe__sdzdt = ''
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
        hrspe__sdzdt = "  freq = 'D'\n"
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise_bodo_error(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )
    ulg__nte = """def f(start=None, end=None, periods=None, freq=None, tz=None, normalize=False, name=None, closed=None):
"""
    ulg__nte += hrspe__sdzdt
    if is_overload_none(start):
        ulg__nte += "  start_t = pd.Timestamp('1800-01-03')\n"
    else:
        ulg__nte += '  start_t = pd.Timestamp(start)\n'
    if is_overload_none(end):
        ulg__nte += "  end_t = pd.Timestamp('1800-01-03')\n"
    else:
        ulg__nte += '  end_t = pd.Timestamp(end)\n'
    if not is_overload_none(freq):
        ulg__nte += (
            '  stride = bodo.hiframes.pd_index_ext.to_offset_value(freq)\n')
        if is_overload_none(periods):
            ulg__nte += '  b = start_t.value\n'
            ulg__nte += (
                '  e = b + (end_t.value - b) // stride * stride + stride // 2 + 1\n'
                )
        elif not is_overload_none(start):
            ulg__nte += '  b = start_t.value\n'
            ulg__nte += '  addend = np.int64(periods) * np.int64(stride)\n'
            ulg__nte += '  e = np.int64(b) + addend\n'
        elif not is_overload_none(end):
            ulg__nte += '  e = end_t.value + stride\n'
            ulg__nte += '  addend = np.int64(periods) * np.int64(-stride)\n'
            ulg__nte += '  b = np.int64(e) + addend\n'
        else:
            raise_bodo_error(
                "at least 'start' or 'end' should be specified if a 'period' is given."
                )
        ulg__nte += '  arr = np.arange(b, e, stride, np.int64)\n'
    else:
        ulg__nte += '  delta = end_t.value - start_t.value\n'
        ulg__nte += '  step = delta / (periods - 1)\n'
        ulg__nte += '  arr1 = np.arange(0, periods, 1, np.float64)\n'
        ulg__nte += '  arr1 *= step\n'
        ulg__nte += '  arr1 += start_t.value\n'
        ulg__nte += '  arr = arr1.astype(np.int64)\n'
        ulg__nte += '  arr[-1] = end_t.value\n'
    ulg__nte += '  A = bodo.utils.conversion.convert_to_dt64ns(arr)\n'
    ulg__nte += (
        '  return bodo.hiframes.pd_index_ext.init_datetime_index(A, name)\n')
    ohydy__rgmvy = {}
    exec(ulg__nte, {'bodo': bodo, 'np': np, 'pd': pd}, ohydy__rgmvy)
    f = ohydy__rgmvy['f']
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
        nbi__duuw = pd.Timedelta('1 day')
        if start is not None:
            nbi__duuw = pd.Timedelta(start)
        psbei__cutk = pd.Timedelta('1 day')
        if end is not None:
            psbei__cutk = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        kgoy__jkgt, wpxe__tjnvq = (bodo.hiframes.pd_index_ext.
            validate_endpoints(closed))
        if freq is not None:
            ieb__rjnr = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = nbi__duuw.value
                aocj__wtsvj = b + (psbei__cutk.value - b
                    ) // ieb__rjnr * ieb__rjnr + ieb__rjnr // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = nbi__duuw.value
                hvobc__vyc = np.int64(periods) * np.int64(ieb__rjnr)
                aocj__wtsvj = np.int64(b) + hvobc__vyc
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                aocj__wtsvj = psbei__cutk.value + ieb__rjnr
                hvobc__vyc = np.int64(periods) * np.int64(-ieb__rjnr)
                b = np.int64(aocj__wtsvj) + hvobc__vyc
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            pbe__ghba = np.arange(b, aocj__wtsvj, ieb__rjnr, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            trn__mli = psbei__cutk.value - nbi__duuw.value
            step = trn__mli / (periods - 1)
            cixfn__wvikr = np.arange(0, periods, 1, np.float64)
            cixfn__wvikr *= step
            cixfn__wvikr += nbi__duuw.value
            pbe__ghba = cixfn__wvikr.astype(np.int64)
            pbe__ghba[-1] = psbei__cutk.value
        if not kgoy__jkgt and len(pbe__ghba) and pbe__ghba[0
            ] == nbi__duuw.value:
            pbe__ghba = pbe__ghba[1:]
        if not wpxe__tjnvq and len(pbe__ghba) and pbe__ghba[-1
            ] == psbei__cutk.value:
            pbe__ghba = pbe__ghba[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(pbe__ghba)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):
    evv__opsg = ColNamesMetaType(('year', 'week', 'day'))

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        vjz__zuza = len(A)
        vzpz__bcspe = bodo.libs.int_arr_ext.alloc_int_array(vjz__zuza, np.
            uint32)
        jqr__bogwn = bodo.libs.int_arr_ext.alloc_int_array(vjz__zuza, np.uint32
            )
        fypz__gxa = bodo.libs.int_arr_ext.alloc_int_array(vjz__zuza, np.uint32)
        for i in numba.parfors.parfor.internal_prange(vjz__zuza):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(vzpz__bcspe, i)
                bodo.libs.array_kernels.setna(jqr__bogwn, i)
                bodo.libs.array_kernels.setna(fypz__gxa, i)
                continue
            vzpz__bcspe[i], jqr__bogwn[i], fypz__gxa[i
                ] = bodo.utils.conversion.box_if_dt64(A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((vzpz__bcspe,
            jqr__bogwn, fypz__gxa), idx, evv__opsg)
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
        cviiw__asrva = [('data', _timedelta_index_data_typ), ('name',
            fe_type.name_typ), ('dict', types.DictType(
            _timedelta_index_data_typ.dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type,
            cviiw__asrva)


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    ciig__hcul = c.pyapi.import_module_noblock(ppke__pyosq)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    wldk__tws = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([wldk__tws])
    kws = c.pyapi.dict_pack([('name', dpkeg__thv)])
    dgtbh__bad = c.pyapi.object_getattr_string(ciig__hcul, 'TimedeltaIndex')
    nonhz__ptqsk = c.pyapi.call(dgtbh__bad, args, kws)
    c.pyapi.decref(wldk__tws)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(ciig__hcul)
    c.pyapi.decref(dgtbh__bad)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return nonhz__ptqsk


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    lfk__iifyz = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, lfk__iifyz).value
    dpkeg__thv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dpkeg__thv).value
    c.pyapi.decref(lfk__iifyz)
    c.pyapi.decref(dpkeg__thv)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    quvw__ccjb.data = data
    quvw__ccjb.name = name
    dtype = _timedelta_index_data_typ.dtype
    dkae__hyl, nopst__nsk = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    quvw__ccjb.dict = nopst__nsk
    return NativeValue(quvw__ccjb._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        jvib__uis, gjl__pnrwl = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = jvib__uis
        timedelta_index.name = gjl__pnrwl
        context.nrt.incref(builder, signature.args[0], jvib__uis)
        context.nrt.incref(builder, signature.args[1], gjl__pnrwl)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    sqmys__niv = TimedeltaIndexType(name)
    sig = signature(sqmys__niv, data, name)
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
    drm__ltos = dict(deep=deep, dtype=dtype, names=names)
    cuyrm__tky = idx_typ_to_format_str_map[TimedeltaIndexType].format('copy()')
    check_unsupported_args('TimedeltaIndex.copy', drm__ltos,
        idx_cpy_arg_defaults, fn_str=cuyrm__tky, package_name='pandas',
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
    jfp__lmj = dict(axis=axis, skipna=skipna)
    vswn__kjn = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        vjz__zuza = len(data)
        flojo__ertq = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(vjz__zuza):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            flojo__ertq = min(flojo__ertq, val)
        gkj__gsi = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            flojo__ertq)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(gkj__gsi, count)
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    jfp__lmj = dict(axis=axis, skipna=skipna)
    vswn__kjn = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        vjz__zuza = len(data)
        igbco__uik = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(vjz__zuza):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            igbco__uik = max(igbco__uik, val)
        gkj__gsi = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            igbco__uik)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(gkj__gsi, count)
    return impl


def gen_tdi_field_impl(field):
    ulg__nte = 'def impl(tdi):\n'
    ulg__nte += '    numba.parfors.parfor.init_prange()\n'
    ulg__nte += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    ulg__nte += '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n'
    ulg__nte += '    n = len(A)\n'
    ulg__nte += '    S = np.empty(n, np.int64)\n'
    ulg__nte += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    ulg__nte += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        ulg__nte += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        ulg__nte += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        ulg__nte += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        ulg__nte += '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n'
    else:
        assert False, 'invalid timedelta field'
    ulg__nte += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    ohydy__rgmvy = {}
    exec(ulg__nte, {'numba': numba, 'np': np, 'bodo': bodo}, ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
    jfp__lmj = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    vswn__kjn = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        aqqgq__pvz = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(aqqgq__pvz)
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
        cviiw__asrva = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, cviiw__asrva)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    drm__ltos = dict(deep=deep, dtype=dtype, names=names)
    cuyrm__tky = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', drm__ltos,
        idx_cpy_arg_defaults, fn_str=cuyrm__tky, package_name='pandas',
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
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    eesbn__ovmxi = c.pyapi.import_module_noblock(ppke__pyosq)
    hwgmu__afz = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    dsjck__hmc = c.pyapi.from_native_value(types.int64, hwgmu__afz.start, c
        .env_manager)
    gatsw__skeql = c.pyapi.from_native_value(types.int64, hwgmu__afz.stop,
        c.env_manager)
    ugi__eku = c.pyapi.from_native_value(types.int64, hwgmu__afz.step, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, hwgmu__afz.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, hwgmu__afz.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([dsjck__hmc, gatsw__skeql, ugi__eku])
    kws = c.pyapi.dict_pack([('name', dpkeg__thv)])
    dgtbh__bad = c.pyapi.object_getattr_string(eesbn__ovmxi, 'RangeIndex')
    vjqnu__cdbv = c.pyapi.call(dgtbh__bad, args, kws)
    c.pyapi.decref(dsjck__hmc)
    c.pyapi.decref(gatsw__skeql)
    c.pyapi.decref(ugi__eku)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(eesbn__ovmxi)
    c.pyapi.decref(dgtbh__bad)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return vjqnu__cdbv


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name
    ulx__vfs = is_overload_constant_int(step) and get_overload_const_int(step
        ) == 0

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        if ulx__vfs:
            raise_bodo_error('Step must not be zero')
        noaaw__qvrqk = cgutils.is_scalar_zero(builder, args[2])
        xcxe__vsyzw = context.get_python_api(builder)
        with builder.if_then(noaaw__qvrqk):
            xcxe__vsyzw.err_format('PyExc_ValueError', 'Step must not be zero')
            val = context.get_constant(types.int32, -1)
            builder.ret(val)
        hwgmu__afz = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        hwgmu__afz.start = args[0]
        hwgmu__afz.stop = args[1]
        hwgmu__afz.step = args[2]
        hwgmu__afz.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return hwgmu__afz._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, jlh__eqsq = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    dsjck__hmc = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, dsjck__hmc).value
    gatsw__skeql = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, gatsw__skeql).value
    ugi__eku = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, ugi__eku).value
    dpkeg__thv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dpkeg__thv).value
    c.pyapi.decref(dsjck__hmc)
    c.pyapi.decref(gatsw__skeql)
    c.pyapi.decref(ugi__eku)
    c.pyapi.decref(dpkeg__thv)
    hwgmu__afz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hwgmu__afz.start = start
    hwgmu__afz.stop = stop
    hwgmu__afz.step = step
    hwgmu__afz.name = name
    return NativeValue(hwgmu__afz._getvalue())


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
        wsidr__wpck = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(wsidr__wpck.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        wsidr__wpck = 'RangeIndex(...) must be called with integers'
        raise BodoError(wsidr__wpck)
    dyym__wlu = 'start'
    iopz__yqwdr = 'stop'
    rqj__bwxq = 'step'
    if is_overload_none(start):
        dyym__wlu = '0'
    if is_overload_none(stop):
        iopz__yqwdr = 'start'
        dyym__wlu = '0'
    if is_overload_none(step):
        rqj__bwxq = '1'
    ulg__nte = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    ulg__nte += '  return init_range_index({}, {}, {}, name)\n'.format(
        dyym__wlu, iopz__yqwdr, rqj__bwxq)
    ohydy__rgmvy = {}
    exec(ulg__nte, {'init_range_index': init_range_index}, ohydy__rgmvy)
    txxq__nyiu = ohydy__rgmvy['_pd_range_index_imp']
    return txxq__nyiu


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
                eairl__pacg = numba.cpython.unicode._normalize_slice(idx,
                    len(I))
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * eairl__pacg.start
                stop = I._start + I._step * eairl__pacg.stop
                step = I._step * eairl__pacg.step
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
        cviiw__asrva = [('data', bodo.IntegerArrayType(types.int64)), (
            'name', fe_type.name_typ), ('dict', types.DictType(types.int64,
            types.int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, cviiw__asrva)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    drm__ltos = dict(deep=deep, dtype=dtype, names=names)
    cuyrm__tky = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', drm__ltos,
        idx_cpy_arg_defaults, fn_str=cuyrm__tky, package_name='pandas',
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
        jvib__uis, gjl__pnrwl, jlh__eqsq = args
        oaao__umodf = signature.return_type
        vce__jsmx = cgutils.create_struct_proxy(oaao__umodf)(context, builder)
        vce__jsmx.data = jvib__uis
        vce__jsmx.name = gjl__pnrwl
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        vce__jsmx.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return vce__jsmx._getvalue()
    knbh__sem = get_overload_const_str(freq)
    sqmys__niv = PeriodIndexType(knbh__sem, name)
    sig = signature(sqmys__niv, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    eesbn__ovmxi = c.pyapi.import_module_noblock(ppke__pyosq)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        quvw__ccjb.data)
    dnq__fgdp = c.pyapi.from_native_value(bodo.IntegerArrayType(types.int64
        ), quvw__ccjb.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, quvw__ccjb.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, quvw__ccjb.name, c
        .env_manager)
    hiy__vwy = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', dnq__fgdp), ('name', dpkeg__thv),
        ('freq', hiy__vwy)])
    dgtbh__bad = c.pyapi.object_getattr_string(eesbn__ovmxi, 'PeriodIndex')
    vjqnu__cdbv = c.pyapi.call(dgtbh__bad, args, kws)
    c.pyapi.decref(dnq__fgdp)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(hiy__vwy)
    c.pyapi.decref(eesbn__ovmxi)
    c.pyapi.decref(dgtbh__bad)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return vjqnu__cdbv


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    enefg__huhnb = c.pyapi.object_getattr_string(val, 'asi8')
    gane__afcy = c.pyapi.call_method(val, 'isna', ())
    dpkeg__thv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dpkeg__thv).value
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    ciig__hcul = c.pyapi.import_module_noblock(ppke__pyosq)
    nvn__mvrmy = c.pyapi.object_getattr_string(ciig__hcul, 'arrays')
    dnq__fgdp = c.pyapi.call_method(nvn__mvrmy, 'IntegerArray', (
        enefg__huhnb, gane__afcy))
    data = c.pyapi.to_native_value(arr_typ, dnq__fgdp).value
    c.pyapi.decref(enefg__huhnb)
    c.pyapi.decref(gane__afcy)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(ciig__hcul)
    c.pyapi.decref(nvn__mvrmy)
    c.pyapi.decref(dnq__fgdp)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    quvw__ccjb.data = data
    quvw__ccjb.name = name
    dkae__hyl, nopst__nsk = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(types.int64, types.int64), types.DictType(types.int64, types
        .int64)(), [])
    quvw__ccjb.dict = nopst__nsk
    return NativeValue(quvw__ccjb._getvalue())


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
        xzp__dgf = get_categories_int_type(fe_type.data.dtype)
        cviiw__asrva = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(xzp__dgf, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            cviiw__asrva)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    ciig__hcul = c.pyapi.import_module_noblock(ppke__pyosq)
    cbx__yhd = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, cbx__yhd.data)
    wldk__tws = c.pyapi.from_native_value(typ.data, cbx__yhd.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, cbx__yhd.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, cbx__yhd.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([wldk__tws])
    kws = c.pyapi.dict_pack([('name', dpkeg__thv)])
    dgtbh__bad = c.pyapi.object_getattr_string(ciig__hcul, 'CategoricalIndex')
    nonhz__ptqsk = c.pyapi.call(dgtbh__bad, args, kws)
    c.pyapi.decref(wldk__tws)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(ciig__hcul)
    c.pyapi.decref(dgtbh__bad)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return nonhz__ptqsk


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    lfk__iifyz = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, lfk__iifyz).value
    dpkeg__thv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dpkeg__thv).value
    c.pyapi.decref(lfk__iifyz)
    c.pyapi.decref(dpkeg__thv)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    quvw__ccjb.data = data
    quvw__ccjb.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    dkae__hyl, nopst__nsk = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    quvw__ccjb.dict = nopst__nsk
    return NativeValue(quvw__ccjb._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        jvib__uis, gjl__pnrwl = args
        cbx__yhd = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        cbx__yhd.data = jvib__uis
        cbx__yhd.name = gjl__pnrwl
        context.nrt.incref(builder, signature.args[0], jvib__uis)
        context.nrt.incref(builder, signature.args[1], gjl__pnrwl)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        cbx__yhd.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return cbx__yhd._getvalue()
    sqmys__niv = CategoricalIndexType(data, name)
    sig = signature(sqmys__niv, data, name)
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
    cuyrm__tky = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    drm__ltos = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', drm__ltos,
        idx_cpy_arg_defaults, fn_str=cuyrm__tky, package_name='pandas',
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
        cviiw__asrva = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, cviiw__asrva
            )


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    ciig__hcul = c.pyapi.import_module_noblock(ppke__pyosq)
    yvx__bbg = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, yvx__bbg.data)
    wldk__tws = c.pyapi.from_native_value(typ.data, yvx__bbg.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, yvx__bbg.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, yvx__bbg.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([wldk__tws])
    kws = c.pyapi.dict_pack([('name', dpkeg__thv)])
    dgtbh__bad = c.pyapi.object_getattr_string(ciig__hcul, 'IntervalIndex')
    nonhz__ptqsk = c.pyapi.call(dgtbh__bad, args, kws)
    c.pyapi.decref(wldk__tws)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(ciig__hcul)
    c.pyapi.decref(dgtbh__bad)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return nonhz__ptqsk


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    lfk__iifyz = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, lfk__iifyz).value
    dpkeg__thv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dpkeg__thv).value
    c.pyapi.decref(lfk__iifyz)
    c.pyapi.decref(dpkeg__thv)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    quvw__ccjb.data = data
    quvw__ccjb.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    dkae__hyl, nopst__nsk = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    quvw__ccjb.dict = nopst__nsk
    return NativeValue(quvw__ccjb._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        jvib__uis, gjl__pnrwl = args
        yvx__bbg = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        yvx__bbg.data = jvib__uis
        yvx__bbg.name = gjl__pnrwl
        context.nrt.incref(builder, signature.args[0], jvib__uis)
        context.nrt.incref(builder, signature.args[1], gjl__pnrwl)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        yvx__bbg.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return yvx__bbg._getvalue()
    sqmys__niv = IntervalIndexType(data, name)
    sig = signature(sqmys__niv, data, name)
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
        cviiw__asrva = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, cviiw__asrva)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    cuyrm__tky = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    drm__ltos = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', drm__ltos, idx_cpy_arg_defaults,
        fn_str=cuyrm__tky, package_name='pandas', module_name='Index')
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
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    eesbn__ovmxi = c.pyapi.import_module_noblock(ppke__pyosq)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, quvw__ccjb.data)
    dnq__fgdp = c.pyapi.from_native_value(typ.data, quvw__ccjb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, quvw__ccjb.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, quvw__ccjb.name, c
        .env_manager)
    cdi__mehxs = c.pyapi.make_none()
    ellk__hndg = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    vjqnu__cdbv = c.pyapi.call_method(eesbn__ovmxi, 'Index', (dnq__fgdp,
        cdi__mehxs, ellk__hndg, dpkeg__thv))
    c.pyapi.decref(dnq__fgdp)
    c.pyapi.decref(cdi__mehxs)
    c.pyapi.decref(ellk__hndg)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(eesbn__ovmxi)
    c.context.nrt.decref(c.builder, typ, val)
    return vjqnu__cdbv


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        oaao__umodf = signature.return_type
        quvw__ccjb = cgutils.create_struct_proxy(oaao__umodf)(context, builder)
        quvw__ccjb.data = args[0]
        quvw__ccjb.name = args[1]
        context.nrt.incref(builder, oaao__umodf.data, args[0])
        context.nrt.incref(builder, oaao__umodf.name_typ, args[1])
        dtype = oaao__umodf.dtype
        quvw__ccjb.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return quvw__ccjb._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    lfk__iifyz = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, lfk__iifyz).value
    dpkeg__thv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dpkeg__thv).value
    c.pyapi.decref(lfk__iifyz)
    c.pyapi.decref(dpkeg__thv)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    quvw__ccjb.data = data
    quvw__ccjb.name = name
    dtype = typ.dtype
    dkae__hyl, nopst__nsk = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    quvw__ccjb.dict = nopst__nsk
    return NativeValue(quvw__ccjb._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        tamj__luwvn = dict(dtype=dtype)
        glo__lzbia = dict(dtype=None)
        check_unsupported_args(func_str, tamj__luwvn, glo__lzbia,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                aqqgq__pvz = bodo.utils.conversion.coerce_to_ndarray(data)
                xps__iof = bodo.utils.conversion.fix_arr_dtype(aqqgq__pvz,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(xps__iof,
                    name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                aqqgq__pvz = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    aqqgq__pvz = aqqgq__pvz.copy()
                xps__iof = bodo.utils.conversion.fix_arr_dtype(aqqgq__pvz,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(xps__iof,
                    name)
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
        cviiw__asrva = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, cviiw__asrva)


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
        cviiw__asrva = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, cviiw__asrva)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    kmky__qlau = typ.data
    scalar_type = typ.data.dtype
    lfk__iifyz = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(kmky__qlau, lfk__iifyz).value
    dpkeg__thv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dpkeg__thv).value
    c.pyapi.decref(lfk__iifyz)
    c.pyapi.decref(dpkeg__thv)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    quvw__ccjb.data = data
    quvw__ccjb.name = name
    dkae__hyl, nopst__nsk = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(scalar_type, types.int64), types.DictType(scalar_type, types
        .int64)(), [])
    quvw__ccjb.dict = nopst__nsk
    return NativeValue(quvw__ccjb._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    kmky__qlau = typ.data
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    eesbn__ovmxi = c.pyapi.import_module_noblock(ppke__pyosq)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, kmky__qlau, quvw__ccjb.data)
    dnq__fgdp = c.pyapi.from_native_value(kmky__qlau, quvw__ccjb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, quvw__ccjb.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, quvw__ccjb.name, c
        .env_manager)
    cdi__mehxs = c.pyapi.make_none()
    ellk__hndg = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    vjqnu__cdbv = c.pyapi.call_method(eesbn__ovmxi, 'Index', (dnq__fgdp,
        cdi__mehxs, ellk__hndg, dpkeg__thv))
    c.pyapi.decref(dnq__fgdp)
    c.pyapi.decref(cdi__mehxs)
    c.pyapi.decref(ellk__hndg)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(eesbn__ovmxi)
    c.context.nrt.decref(c.builder, typ, val)
    return vjqnu__cdbv


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name,
        data)(data, name)
    wcy__kbu = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, wcy__kbu


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        sdp__kdq = 'bytes_type'
    else:
        sdp__kdq = 'string_type'
    ulg__nte = 'def impl(context, builder, signature, args):\n'
    ulg__nte += '    assert len(args) == 2\n'
    ulg__nte += '    index_typ = signature.return_type\n'
    ulg__nte += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    ulg__nte += '    index_val.data = args[0]\n'
    ulg__nte += '    index_val.name = args[1]\n'
    ulg__nte += '    # increase refcount of stored values\n'
    ulg__nte += '    context.nrt.incref(builder, signature.args[0], args[0])\n'
    ulg__nte += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    ulg__nte += '    # create empty dict for get_loc hashmap\n'
    ulg__nte += '    index_val.dict = context.compile_internal(\n'
    ulg__nte += '       builder,\n'
    ulg__nte += (
        f'       lambda: numba.typed.Dict.empty({sdp__kdq}, types.int64),\n')
    ulg__nte += f'        types.DictType({sdp__kdq}, types.int64)(), [],)\n'
    ulg__nte += '    return index_val._getvalue()\n'
    ohydy__rgmvy = {}
    exec(ulg__nte, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type}, ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    cuyrm__tky = idx_typ_to_format_str_map[typ].format('copy()')
    drm__ltos = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', drm__ltos, idx_cpy_arg_defaults,
        fn_str=cuyrm__tky, package_name='pandas', module_name='Index')
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
    uks__vxz = I.dtype if not isinstance(I, RangeIndexType) else types.int64
    yjqf__sryx = other.dtype if not isinstance(other, RangeIndexType
        ) else types.int64
    if uks__vxz != yjqf__sryx:
        raise BodoError(
            f'Index.{func_name}(): incompatible types {uks__vxz} and {yjqf__sryx}'
            )


@overload_method(NumericIndexType, 'union', inline='always')
@overload_method(StringIndexType, 'union', inline='always')
@overload_method(BinaryIndexType, 'union', inline='always')
@overload_method(DatetimeIndexType, 'union', inline='always')
@overload_method(TimedeltaIndexType, 'union', inline='always')
@overload_method(RangeIndexType, 'union', inline='always')
def overload_index_union(I, other, sort=None):
    jfp__lmj = dict(sort=sort)
    zktd__beb = dict(sort=None)
    check_unsupported_args('Index.union', jfp__lmj, zktd__beb, package_name
        ='pandas', module_name='Index')
    _verify_setop_compatible('union', I, other)
    vhdb__yatb = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        fdgl__fvnfw = bodo.utils.conversion.coerce_to_array(I)
        cld__osa = bodo.utils.conversion.coerce_to_array(other)
        oofvh__kvq = bodo.libs.array_kernels.concat([fdgl__fvnfw, cld__osa])
        lhrj__ehc = bodo.libs.array_kernels.unique(oofvh__kvq)
        return vhdb__yatb(lhrj__ehc, None)
    return impl


@overload_method(NumericIndexType, 'intersection', inline='always')
@overload_method(StringIndexType, 'intersection', inline='always')
@overload_method(BinaryIndexType, 'intersection', inline='always')
@overload_method(DatetimeIndexType, 'intersection', inline='always')
@overload_method(TimedeltaIndexType, 'intersection', inline='always')
@overload_method(RangeIndexType, 'intersection', inline='always')
def overload_index_intersection(I, other, sort=None):
    jfp__lmj = dict(sort=sort)
    zktd__beb = dict(sort=None)
    check_unsupported_args('Index.intersection', jfp__lmj, zktd__beb,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('intersection', I, other)
    vhdb__yatb = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        fdgl__fvnfw = bodo.utils.conversion.coerce_to_array(I)
        cld__osa = bodo.utils.conversion.coerce_to_array(other)
        bavs__unji = bodo.libs.array_kernels.unique(fdgl__fvnfw)
        ynnsh__jsxqr = bodo.libs.array_kernels.unique(cld__osa)
        oofvh__kvq = bodo.libs.array_kernels.concat([bavs__unji, ynnsh__jsxqr])
        pkur__xaqs = pd.Series(oofvh__kvq).sort_values().values
        wgga__kmo = bodo.libs.array_kernels.intersection_mask(pkur__xaqs)
        return vhdb__yatb(pkur__xaqs[wgga__kmo], None)
    return impl


@overload_method(NumericIndexType, 'difference', inline='always')
@overload_method(StringIndexType, 'difference', inline='always')
@overload_method(BinaryIndexType, 'difference', inline='always')
@overload_method(DatetimeIndexType, 'difference', inline='always')
@overload_method(TimedeltaIndexType, 'difference', inline='always')
@overload_method(RangeIndexType, 'difference', inline='always')
def overload_index_difference(I, other, sort=None):
    jfp__lmj = dict(sort=sort)
    zktd__beb = dict(sort=None)
    check_unsupported_args('Index.difference', jfp__lmj, zktd__beb,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('difference', I, other)
    vhdb__yatb = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        fdgl__fvnfw = bodo.utils.conversion.coerce_to_array(I)
        cld__osa = bodo.utils.conversion.coerce_to_array(other)
        bavs__unji = bodo.libs.array_kernels.unique(fdgl__fvnfw)
        ynnsh__jsxqr = bodo.libs.array_kernels.unique(cld__osa)
        wgga__kmo = np.empty(len(bavs__unji), np.bool_)
        bodo.libs.array.array_isin(wgga__kmo, bavs__unji, ynnsh__jsxqr, False)
        return vhdb__yatb(bavs__unji[~wgga__kmo], None)
    return impl


@overload_method(NumericIndexType, 'symmetric_difference', inline='always')
@overload_method(StringIndexType, 'symmetric_difference', inline='always')
@overload_method(BinaryIndexType, 'symmetric_difference', inline='always')
@overload_method(DatetimeIndexType, 'symmetric_difference', inline='always')
@overload_method(TimedeltaIndexType, 'symmetric_difference', inline='always')
@overload_method(RangeIndexType, 'symmetric_difference', inline='always')
def overload_index_symmetric_difference(I, other, result_name=None, sort=None):
    jfp__lmj = dict(result_name=result_name, sort=sort)
    zktd__beb = dict(result_name=None, sort=None)
    check_unsupported_args('Index.symmetric_difference', jfp__lmj,
        zktd__beb, package_name='pandas', module_name='Index')
    _verify_setop_compatible('symmetric_difference', I, other)
    vhdb__yatb = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, result_name=None, sort=None):
        fdgl__fvnfw = bodo.utils.conversion.coerce_to_array(I)
        cld__osa = bodo.utils.conversion.coerce_to_array(other)
        bavs__unji = bodo.libs.array_kernels.unique(fdgl__fvnfw)
        ynnsh__jsxqr = bodo.libs.array_kernels.unique(cld__osa)
        cww__gpz = np.empty(len(bavs__unji), np.bool_)
        qhddx__miw = np.empty(len(ynnsh__jsxqr), np.bool_)
        bodo.libs.array.array_isin(cww__gpz, bavs__unji, ynnsh__jsxqr, False)
        bodo.libs.array.array_isin(qhddx__miw, ynnsh__jsxqr, bavs__unji, False)
        tti__dionv = bodo.libs.array_kernels.concat([bavs__unji[~cww__gpz],
            ynnsh__jsxqr[~qhddx__miw]])
        return vhdb__yatb(tti__dionv, None)
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
    jfp__lmj = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value)
    zktd__beb = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', jfp__lmj, zktd__beb, package_name=
        'pandas', module_name='Index')
    return lambda I, indices: I[indices]


def _init_engine(I, ban_unique=True):
    pass


@overload(_init_engine)
def overload_init_engine(I, ban_unique=True):
    if isinstance(I, CategoricalIndexType):

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                pbe__ghba = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(pbe__ghba)):
                    if not bodo.libs.array_kernels.isna(pbe__ghba, i):
                        val = (bodo.hiframes.pd_categorical_ext.
                            get_code_for_value(pbe__ghba.dtype, pbe__ghba[i]))
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl
    else:

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                pbe__ghba = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(pbe__ghba)):
                    if not bodo.libs.array_kernels.isna(pbe__ghba, i):
                        val = pbe__ghba[i]
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
                pbe__ghba = bodo.utils.conversion.coerce_to_array(I)
                zogfd__kfn = (bodo.hiframes.pd_categorical_ext.
                    get_code_for_value(pbe__ghba.dtype, key))
                return zogfd__kfn in I._dict
            else:
                wsidr__wpck = (
                    'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                    )
                warnings.warn(wsidr__wpck)
                pbe__ghba = bodo.utils.conversion.coerce_to_array(I)
                ind = -1
                for i in range(len(pbe__ghba)):
                    if not bodo.libs.array_kernels.isna(pbe__ghba, i):
                        if pbe__ghba[i] == key:
                            ind = i
            return ind != -1
        return impl

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I, False)
            return key in I._dict
        else:
            wsidr__wpck = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(wsidr__wpck)
            pbe__ghba = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(pbe__ghba)):
                if not bodo.libs.array_kernels.isna(pbe__ghba, i):
                    if pbe__ghba[i] == key:
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
    jfp__lmj = dict(method=method, tolerance=tolerance)
    vswn__kjn = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', jfp__lmj, vswn__kjn,
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
            wsidr__wpck = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(wsidr__wpck)
            pbe__ghba = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(pbe__ghba)):
                if pbe__ghba[i] == key:
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
        avzob__azauq = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                vjz__zuza = len(I)
                jzryw__rgd = np.empty(vjz__zuza, np.bool_)
                for i in numba.parfors.parfor.internal_prange(vjz__zuza):
                    jzryw__rgd[i] = not avzob__azauq
                return jzryw__rgd
            return impl
        ulg__nte = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if avzob__azauq else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        ohydy__rgmvy = {}
        exec(ulg__nte, {'bodo': bodo, 'np': np, 'numba': numba}, ohydy__rgmvy)
        impl = ohydy__rgmvy['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for vblm__hral in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(vblm__hral, overload_name, no_unliteral=True,
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
            pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(pbe__ghba, 1)
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
            pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(pbe__ghba, 2)
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
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        jzryw__rgd = bodo.libs.array_kernels.duplicated((pbe__ghba,))
        return jzryw__rgd
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
    jfp__lmj = dict(keep=keep)
    vswn__kjn = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    ulg__nte = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        ulg__nte += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        ulg__nte += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    ohydy__rgmvy = {}
    exec(ulg__nte, {'bodo': bodo}, ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
    fdj__sivyx = args[0]
    if isinstance(self.typemap[fdj__sivyx.name], (HeterogeneousIndexType,
        MultiIndexType)):
        return None
    if equiv_set.has_shape(fdj__sivyx):
        return ArrayAnalysis.AnalyzeResult(shape=fdj__sivyx, pre=[])
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
    jfp__lmj = dict(na_action=na_action)
    bshfr__nza = dict(na_action=None)
    check_unsupported_args('Index.map', jfp__lmj, bshfr__nza, package_name=
        'pandas', module_name='Index')
    dtype = I.dtype
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.map')
    if dtype == types.NPDatetime('ns'):
        dtype = pd_timestamp_type
    if dtype == types.NPTimedelta('ns'):
        dtype = pd_timedelta_type
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = dtype.elem_type
    cli__zzaj = numba.core.registry.cpu_target.typing_context
    qpscp__hdl = numba.core.registry.cpu_target.target_context
    try:
        uaxb__zjj = get_const_func_output_type(mapper, (dtype,), {},
            cli__zzaj, qpscp__hdl)
    except Exception as aocj__wtsvj:
        raise_bodo_error(get_udf_error_msg('Index.map()', aocj__wtsvj))
    ktwoo__evsv = get_udf_out_arr_type(uaxb__zjj)
    func = get_overload_const_func(mapper, None)
    ulg__nte = 'def f(I, mapper, na_action=None):\n'
    ulg__nte += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    ulg__nte += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    ulg__nte += '  numba.parfors.parfor.init_prange()\n'
    ulg__nte += '  n = len(A)\n'
    ulg__nte += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    ulg__nte += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ulg__nte += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    ulg__nte += '    v = map_func(t2)\n'
    ulg__nte += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    ulg__nte += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    fqeti__uszk = bodo.compiler.udf_jit(func)
    ohydy__rgmvy = {}
    exec(ulg__nte, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': fqeti__uszk, '_arr_typ': ktwoo__evsv,
        'init_nested_counts': bodo.utils.indexing.init_nested_counts,
        'add_nested_counts': bodo.utils.indexing.add_nested_counts,
        'data_arr_type': ktwoo__evsv.dtype}, ohydy__rgmvy)
    f = ohydy__rgmvy['f']
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
    acfof__xfa, bkj__cdpd = sig.args
    if acfof__xfa != bkj__cdpd:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    acfof__xfa, bkj__cdpd = sig.args
    if acfof__xfa != bkj__cdpd:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):
            ulg__nte = (
                'def impl(lhs, rhs):\n  arr = bodo.utils.conversion.coerce_to_array(lhs)\n'
                )
            if rhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                ulg__nte += """  dt = bodo.utils.conversion.unbox_if_timestamp(rhs)
  return op(arr, dt)
"""
            else:
                ulg__nte += """  rhs_arr = bodo.utils.conversion.get_array_if_series_or_index(rhs)
  return op(arr, rhs_arr)
"""
            ohydy__rgmvy = {}
            exec(ulg__nte, {'bodo': bodo, 'op': op}, ohydy__rgmvy)
            impl = ohydy__rgmvy['impl']
            return impl
        if is_index_type(rhs):
            ulg__nte = (
                'def impl(lhs, rhs):\n  arr = bodo.utils.conversion.coerce_to_array(rhs)\n'
                )
            if lhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                ulg__nte += """  dt = bodo.utils.conversion.unbox_if_timestamp(lhs)
  return op(dt, arr)
"""
            else:
                ulg__nte += """  lhs_arr = bodo.utils.conversion.get_array_if_series_or_index(lhs)
  return op(lhs_arr, arr)
"""
            ohydy__rgmvy = {}
            exec(ulg__nte, {'bodo': bodo, 'op': op}, ohydy__rgmvy)
            impl = ohydy__rgmvy['impl']
            return impl
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    pbe__ghba = bodo.utils.conversion.coerce_to_array(data)
                    ctk__yeqj = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    jzryw__rgd = op(pbe__ghba, ctk__yeqj)
                    return jzryw__rgd
                return impl3
            count = len(lhs.data.types)
            ulg__nte = 'def f(lhs, rhs):\n'
            ulg__nte += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            ohydy__rgmvy = {}
            exec(ulg__nte, {'op': op, 'np': np}, ohydy__rgmvy)
            impl = ohydy__rgmvy['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    pbe__ghba = bodo.utils.conversion.coerce_to_array(data)
                    ctk__yeqj = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    jzryw__rgd = op(ctk__yeqj, pbe__ghba)
                    return jzryw__rgd
                return impl4
            count = len(rhs.data.types)
            ulg__nte = 'def f(lhs, rhs):\n'
            ulg__nte += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            ohydy__rgmvy = {}
            exec(ulg__nte, {'op': op, 'np': np}, ohydy__rgmvy)
            impl = ohydy__rgmvy['f']
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
        cviiw__asrva = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type,
            cviiw__asrva)


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    cuyrm__tky = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    drm__ltos = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', drm__ltos, idx_cpy_arg_defaults,
        fn_str=cuyrm__tky, package_name='pandas', module_name='Index')
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
    ppke__pyosq = c.context.insert_const_string(c.builder.module, 'pandas')
    eesbn__ovmxi = c.pyapi.import_module_noblock(ppke__pyosq)
    quvw__ccjb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, quvw__ccjb.data)
    dnq__fgdp = c.pyapi.from_native_value(typ.data, quvw__ccjb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, quvw__ccjb.name)
    dpkeg__thv = c.pyapi.from_native_value(typ.name_typ, quvw__ccjb.name, c
        .env_manager)
    cdi__mehxs = c.pyapi.make_none()
    ellk__hndg = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    vjqnu__cdbv = c.pyapi.call_method(eesbn__ovmxi, 'Index', (dnq__fgdp,
        cdi__mehxs, ellk__hndg, dpkeg__thv))
    c.pyapi.decref(dnq__fgdp)
    c.pyapi.decref(cdi__mehxs)
    c.pyapi.decref(ellk__hndg)
    c.pyapi.decref(dpkeg__thv)
    c.pyapi.decref(eesbn__ovmxi)
    c.context.nrt.decref(c.builder, typ, val)
    return vjqnu__cdbv


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        oaao__umodf = signature.return_type
        quvw__ccjb = cgutils.create_struct_proxy(oaao__umodf)(context, builder)
        quvw__ccjb.data = args[0]
        quvw__ccjb.name = args[1]
        context.nrt.incref(builder, oaao__umodf.data, args[0])
        context.nrt.incref(builder, oaao__umodf.name_typ, args[1])
        return quvw__ccjb._getvalue()
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
        ulg__nte = 'def _impl_nbytes(I):\n'
        ulg__nte += '    total = 0\n'
        ulg__nte += '    data = I._data\n'
        for i in range(I.nlevels):
            ulg__nte += f'    total += data[{i}].nbytes\n'
        ulg__nte += '    return total\n'
        npyp__xsjty = {}
        exec(ulg__nte, {}, npyp__xsjty)
        return npyp__xsjty['_impl_nbytes']
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
        oksa__qczu = 'bodo.hiframes.pd_index_ext.get_index_name(I)'
    else:
        oksa__qczu = 'name'
    ulg__nte = 'def impl(I, index=None, name=None):\n'
    ulg__nte += '    data = bodo.utils.conversion.index_to_array(I)\n'
    if is_overload_none(index):
        ulg__nte += '    new_index = I\n'
    elif is_pd_index_type(index):
        ulg__nte += '    new_index = index\n'
    elif isinstance(index, SeriesType):
        ulg__nte += '    arr = bodo.utils.conversion.coerce_to_array(index)\n'
        ulg__nte += (
            '    index_name = bodo.hiframes.pd_series_ext.get_series_name(index)\n'
            )
        ulg__nte += (
            '    new_index = bodo.utils.conversion.index_from_array(arr, index_name)\n'
            )
    elif bodo.utils.utils.is_array_typ(index, False):
        ulg__nte += (
            '    new_index = bodo.utils.conversion.index_from_array(index)\n')
    elif isinstance(index, (types.List, types.BaseTuple)):
        ulg__nte += '    arr = bodo.utils.conversion.coerce_to_array(index)\n'
        ulg__nte += (
            '    new_index = bodo.utils.conversion.index_from_array(arr)\n')
    else:
        raise_bodo_error(
            f'Index.to_series(): unsupported type for argument index: {type(index).__name__}'
            )
    ulg__nte += f'    new_name = {oksa__qczu}\n'
    ulg__nte += (
        '    return bodo.hiframes.pd_series_ext.init_series(data, new_index, new_name)'
        )
    ohydy__rgmvy = {}
    exec(ulg__nte, {'bodo': bodo, 'np': np}, ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
        bhacg__uko = 'I'
    elif is_overload_false(index):
        bhacg__uko = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'Index.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'Index.to_frame(): index argument must be a compile time constant')
    ulg__nte = 'def impl(I, index=True, name=None):\n'
    ulg__nte += '    data = bodo.utils.conversion.index_to_array(I)\n'
    ulg__nte += f'    new_index = {bhacg__uko}\n'
    if is_overload_none(name) and I.name_typ == types.none:
        qqay__dhjqk = ColNamesMetaType((0,))
    elif is_overload_none(name):
        qqay__dhjqk = ColNamesMetaType((I.name_typ,))
    elif is_overload_constant_str(name):
        qqay__dhjqk = ColNamesMetaType((get_overload_const_str(name),))
    elif is_overload_constant_int(name):
        qqay__dhjqk = ColNamesMetaType((get_overload_const_int(name),))
    else:
        raise_bodo_error(
            f'Index.to_frame(): only constant string/int are supported for argument name'
            )
    ulg__nte += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((data,), new_index, __col_name_meta_value)
"""
    ohydy__rgmvy = {}
    exec(ulg__nte, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        qqay__dhjqk}, ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
    return impl


@overload_method(MultiIndexType, 'to_frame', inline='always', no_unliteral=True
    )
def overload_multi_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        bhacg__uko = 'I'
    elif is_overload_false(index):
        bhacg__uko = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a compile time constant'
            )
    ulg__nte = 'def impl(I, index=True, name=None):\n'
    ulg__nte += '    data = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    ulg__nte += f'    new_index = {bhacg__uko}\n'
    vicys__dgow = len(I.array_types)
    if is_overload_none(name) and I.names_typ == (types.none,) * vicys__dgow:
        qqay__dhjqk = ColNamesMetaType(tuple(range(vicys__dgow)))
    elif is_overload_none(name):
        qqay__dhjqk = ColNamesMetaType(I.names_typ)
    elif is_overload_constant_tuple(name) or is_overload_constant_list(name):
        if is_overload_constant_list(name):
            names = tuple(get_overload_const_list(name))
        else:
            names = get_overload_const_tuple(name)
        if vicys__dgow != len(names):
            raise_bodo_error(
                f'MultiIndex.to_frame(): expected {vicys__dgow} names, not {len(names)}'
                )
        if all(is_overload_constant_str(wdxj__dqp) or
            is_overload_constant_int(wdxj__dqp) for wdxj__dqp in names):
            qqay__dhjqk = ColNamesMetaType(names)
        else:
            raise_bodo_error(
                'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
                )
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
            )
    ulg__nte += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(data, new_index, __col_name_meta_value,)
"""
    ohydy__rgmvy = {}
    exec(ulg__nte, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        qqay__dhjqk}, ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
    jfp__lmj = dict(dtype=dtype, na_value=na_value)
    vswn__kjn = dict(dtype=None, na_value=None)
    check_unsupported_args('Index.to_numpy', jfp__lmj, vswn__kjn,
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
            evo__dofvn = list()
            for i in range(I._start, I._stop, I.step):
                evo__dofvn.append(i)
            return evo__dofvn
        return impl

    def impl(I):
        evo__dofvn = list()
        for i in range(len(I)):
            evo__dofvn.append(I[i])
        return evo__dofvn
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
    uhqm__hfqs = {DatetimeIndexType: 'datetime64', TimedeltaIndexType:
        'timedelta64', RangeIndexType: 'integer', BinaryIndexType: 'bytes',
        CategoricalIndexType: 'categorical', PeriodIndexType: 'period',
        IntervalIndexType: 'interval', MultiIndexType: 'mixed'}
    inferred_type = uhqm__hfqs[type(I)]
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
    ftcz__mwpka = {DatetimeIndexType: np.dtype('datetime64[ns]'),
        TimedeltaIndexType: np.dtype('timedelta64[ns]'), RangeIndexType: np
        .dtype('int64'), StringIndexType: np.dtype('O'), BinaryIndexType:
        np.dtype('O'), MultiIndexType: np.dtype('O')}
    dtype = ftcz__mwpka[type(I)]
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
    boymh__mod = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in boymh__mod:
        init_func = boymh__mod[type(I)]
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
    avcxp__dwop = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index, RangeIndexType: bodo.
        hiframes.pd_index_ext.init_range_index}
    if type(I) in avcxp__dwop:
        return avcxp__dwop[type(I)]
    raise BodoError(
        f'Unsupported type for standard Index constructor: {type(I)}')


@overload_method(NumericIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'min', no_unliteral=True, inline=
    'always')
def overload_index_min(I, axis=None, skipna=True):
    jfp__lmj = dict(axis=axis, skipna=skipna)
    vswn__kjn = dict(axis=None, skipna=True)
    check_unsupported_args('Index.min', jfp__lmj, vswn__kjn, package_name=
        'pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            zvhgx__oef = len(I)
            if zvhgx__oef == 0:
                return np.nan
            if I._step < 0:
                return I._start + I._step * (zvhgx__oef - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.min(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_min(pbe__ghba)
    return impl


@overload_method(NumericIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'max', no_unliteral=True, inline=
    'always')
def overload_index_max(I, axis=None, skipna=True):
    jfp__lmj = dict(axis=axis, skipna=skipna)
    vswn__kjn = dict(axis=None, skipna=True)
    check_unsupported_args('Index.max', jfp__lmj, vswn__kjn, package_name=
        'pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            zvhgx__oef = len(I)
            if zvhgx__oef == 0:
                return np.nan
            if I._step > 0:
                return I._start + I._step * (zvhgx__oef - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.max(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_max(pbe__ghba)
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
    jfp__lmj = dict(axis=axis, skipna=skipna)
    vswn__kjn = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmin', jfp__lmj, vswn__kjn,
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
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = init_numeric_index(np.arange(len(pbe__ghba)))
        return bodo.libs.array_ops.array_op_idxmin(pbe__ghba, index)
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
    jfp__lmj = dict(axis=axis, skipna=skipna)
    vswn__kjn = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmax', jfp__lmj, vswn__kjn,
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
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = np.arange(len(pbe__ghba))
        return bodo.libs.array_ops.array_op_idxmax(pbe__ghba, index)
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
    vhdb__yatb = get_index_constructor(I)

    def impl(I):
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        jmzw__uouf = bodo.libs.array_kernels.unique(pbe__ghba)
        return vhdb__yatb(jmzw__uouf, name)
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
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        vjz__zuza = bodo.libs.array_kernels.nunique(pbe__ghba, dropna)
        return vjz__zuza
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
            lfp__rielh = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_index_ext.get_index_data(I)
            vjz__zuza = len(A)
            jzryw__rgd = np.empty(vjz__zuza, np.bool_)
            bodo.libs.array.array_isin(jzryw__rgd, A, lfp__rielh, False)
            return jzryw__rgd
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        jzryw__rgd = bodo.libs.array_ops.array_op_isin(A, values)
        return jzryw__rgd
    return impl


@overload_method(RangeIndexType, 'isin', no_unliteral=True, inline='always')
def overload_range_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            lfp__rielh = bodo.utils.conversion.coerce_to_array(values)
            A = np.arange(I.start, I.stop, I.step)
            vjz__zuza = len(A)
            jzryw__rgd = np.empty(vjz__zuza, np.bool_)
            bodo.libs.array.array_isin(jzryw__rgd, A, lfp__rielh, False)
            return jzryw__rgd
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Index.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = np.arange(I.start, I.stop, I.step)
        jzryw__rgd = bodo.libs.array_ops.array_op_isin(A, values)
        return jzryw__rgd
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
        zvhgx__oef = len(I)
        ejc__odd = start + step * (zvhgx__oef - 1)
        lkau__npm = ejc__odd - step * zvhgx__oef
        return init_range_index(ejc__odd, lkau__npm, -step, name)


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
    jfp__lmj = dict(return_indexer=return_indexer, key=key)
    vswn__kjn = dict(return_indexer=False, key=None)
    check_unsupported_args('Index.sort_values', jfp__lmj, vswn__kjn,
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
    vhdb__yatb = get_index_constructor(I)
    rmvmr__nnfd = ColNamesMetaType(('$_bodo_col_',))

    def impl(I, return_indexer=False, ascending=True, na_position='last',
        key=None):
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = get_index_name(I)
        index = init_range_index(0, len(pbe__ghba), 1, None)
        wpj__knnf = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            pbe__ghba,), index, rmvmr__nnfd)
        fayo__nppn = wpj__knnf.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=False, na_position=na_position)
        jzryw__rgd = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            fayo__nppn, 0)
        return vhdb__yatb(jzryw__rgd, name)
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
    jfp__lmj = dict(axis=axis, kind=kind, order=order)
    vswn__kjn = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Index.argsort', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, kind='quicksort', order=None):
            if I._step > 0:
                return np.arange(0, len(I), 1)
            else:
                return np.arange(len(I) - 1, -1, -1)
        return impl

    def impl(I, axis=0, kind='quicksort', order=None):
        pbe__ghba = bodo.hiframes.pd_index_ext.get_index_data(I)
        jzryw__rgd = bodo.hiframes.series_impl.argsort(pbe__ghba)
        return jzryw__rgd
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
        pai__lwy = 'None'
    else:
        pai__lwy = 'other'
    ulg__nte = 'def impl(I, cond, other=np.nan):\n'
    if isinstance(I, RangeIndexType):
        ulg__nte += '  arr = np.arange(I._start, I._stop, I._step)\n'
        vhdb__yatb = 'init_numeric_index'
    else:
        ulg__nte += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    ulg__nte += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    ulg__nte += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {pai__lwy})\n'
        )
    ulg__nte += f'  return constructor(out_arr, name)\n'
    ohydy__rgmvy = {}
    vhdb__yatb = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(ulg__nte, {'bodo': bodo, 'np': np, 'constructor': vhdb__yatb},
        ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
        pai__lwy = 'None'
    else:
        pai__lwy = 'other'
    ulg__nte = 'def impl(I, cond, other):\n'
    ulg__nte += '  cond = ~cond\n'
    if isinstance(I, RangeIndexType):
        ulg__nte += '  arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        ulg__nte += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    ulg__nte += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    ulg__nte += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {pai__lwy})\n'
        )
    ulg__nte += f'  return constructor(out_arr, name)\n'
    ohydy__rgmvy = {}
    vhdb__yatb = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(ulg__nte, {'bodo': bodo, 'np': np, 'constructor': vhdb__yatb},
        ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
    jfp__lmj = dict(axis=axis)
    vswn__kjn = dict(axis=None)
    check_unsupported_args('Index.repeat', jfp__lmj, vswn__kjn,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Index.repeat(): 'repeats' should be an integer or array of integers"
            )
    ulg__nte = 'def impl(I, repeats, axis=None):\n'
    if not isinstance(repeats, types.Integer):
        ulg__nte += (
            '    repeats = bodo.utils.conversion.coerce_to_array(repeats)\n')
    if isinstance(I, RangeIndexType):
        ulg__nte += '    arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        ulg__nte += '    arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    ulg__nte += '    name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    ulg__nte += (
        '    out_arr = bodo.libs.array_kernels.repeat_kernel(arr, repeats)\n')
    ulg__nte += '    return constructor(out_arr, name)'
    ohydy__rgmvy = {}
    vhdb__yatb = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(ulg__nte, {'bodo': bodo, 'np': np, 'constructor': vhdb__yatb},
        ohydy__rgmvy)
    impl = ohydy__rgmvy['impl']
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
    utt__lklw = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, utt__lklw])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    utt__lklw = context.get_constant_null(types.DictType(types.int64, types
        .int64))
    return lir.Constant.literal_struct([data, name, utt__lklw])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    utt__lklw = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, utt__lklw])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    kmky__qlau = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, kmky__qlau, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    utt__lklw = context.get_constant_null(types.DictType(scalar_type, types
        .int64))
    return lir.Constant.literal_struct([data, name, utt__lklw])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [jdc__qqjuu] = sig.args
    [index] = args
    aul__fziis = context.make_helper(builder, jdc__qqjuu, value=index)
    egc__escx = context.make_helper(builder, sig.return_type)
    xwatr__mosk = cgutils.alloca_once_value(builder, aul__fziis.start)
    hwp__sad = context.get_constant(types.intp, 0)
    znwb__hia = cgutils.alloca_once_value(builder, hwp__sad)
    egc__escx.iter = xwatr__mosk
    egc__escx.stop = aul__fziis.stop
    egc__escx.step = aul__fziis.step
    egc__escx.count = znwb__hia
    axxd__gvff = builder.sub(aul__fziis.stop, aul__fziis.start)
    namcf__arm = context.get_constant(types.intp, 1)
    lbnoo__vcu = builder.icmp_signed('>', axxd__gvff, hwp__sad)
    bnvm__snmf = builder.icmp_signed('>', aul__fziis.step, hwp__sad)
    xucxp__qsdds = builder.not_(builder.xor(lbnoo__vcu, bnvm__snmf))
    with builder.if_then(xucxp__qsdds):
        pslg__lbslv = builder.srem(axxd__gvff, aul__fziis.step)
        pslg__lbslv = builder.select(lbnoo__vcu, pslg__lbslv, builder.neg(
            pslg__lbslv))
        dmv__rvfp = builder.icmp_signed('>', pslg__lbslv, hwp__sad)
        comq__qyiae = builder.add(builder.sdiv(axxd__gvff, aul__fziis.step),
            builder.select(dmv__rvfp, namcf__arm, hwp__sad))
        builder.store(comq__qyiae, znwb__hia)
    nonhz__ptqsk = egc__escx._getvalue()
    oeng__hxgsv = impl_ret_new_ref(context, builder, sig.return_type,
        nonhz__ptqsk)
    return oeng__hxgsv


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
    for pfdk__whqm in index_unsupported_methods:
        for btcxc__rfhnt, typ in index_types:
            overload_method(typ, pfdk__whqm, no_unliteral=True)(
                create_unsupported_overload(btcxc__rfhnt.format(pfdk__whqm +
                '()')))
    for wij__huuh in index_unsupported_atrs:
        for btcxc__rfhnt, typ in index_types:
            overload_attribute(typ, wij__huuh, no_unliteral=True)(
                create_unsupported_overload(btcxc__rfhnt.format(wij__huuh)))
    tqtth__nkjej = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    xom__rfj = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods), (BinaryIndexType,
        binary_index_unsupported_methods), (StringIndexType,
        string_index_unsupported_methods)]
    for typ, wghn__ubzsr in xom__rfj:
        btcxc__rfhnt = idx_typ_to_format_str_map[typ]
        for iri__umm in wghn__ubzsr:
            overload_method(typ, iri__umm, no_unliteral=True)(
                create_unsupported_overload(btcxc__rfhnt.format(iri__umm +
                '()')))
    for typ, ace__orjc in tqtth__nkjej:
        btcxc__rfhnt = idx_typ_to_format_str_map[typ]
        for wij__huuh in ace__orjc:
            overload_attribute(typ, wij__huuh, no_unliteral=True)(
                create_unsupported_overload(btcxc__rfhnt.format(wij__huuh)))


_install_index_unsupported()
