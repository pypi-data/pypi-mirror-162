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
            iabd__ptyg = val.dtype.numpy_dtype
            dtype = numba.np.numpy_support.from_dtype(iabd__ptyg)
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
        wae__mtj = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(_dt_index_data_typ.dtype, types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, wae__mtj)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    qxr__mphgl = dict(deep=deep, dtype=dtype, names=names)
    btw__vdeav = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()')
    check_unsupported_args('copy', qxr__mphgl, idx_cpy_arg_defaults, fn_str
        =btw__vdeav, package_name='pandas', module_name='Index')
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
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    pvl__jxac = c.pyapi.import_module_noblock(rptsq__afmc)
    wgohi__xihmg = numba.core.cgutils.create_struct_proxy(typ)(c.context, c
        .builder, val)
    c.context.nrt.incref(c.builder, typ.data, wgohi__xihmg.data)
    gle__iuvb = c.pyapi.from_native_value(typ.data, wgohi__xihmg.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, wgohi__xihmg.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, wgohi__xihmg.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([gle__iuvb])
    qtlqi__jtfyi = c.pyapi.object_getattr_string(pvl__jxac, 'DatetimeIndex')
    kws = c.pyapi.dict_pack([('name', nyvht__fdyuv)])
    xmp__zpraf = c.pyapi.call(qtlqi__jtfyi, args, kws)
    c.pyapi.decref(gle__iuvb)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(pvl__jxac)
    c.pyapi.decref(qtlqi__jtfyi)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return xmp__zpraf


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        isn__keuib = c.pyapi.object_getattr_string(val, 'array')
    else:
        isn__keuib = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, isn__keuib).value
    nyvht__fdyuv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nyvht__fdyuv).value
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oxnr__nmv.data = data
    oxnr__nmv.name = name
    dtype = _dt_index_data_typ.dtype
    clgus__coc, ekvv__jgng = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    oxnr__nmv.dict = ekvv__jgng
    c.pyapi.decref(isn__keuib)
    c.pyapi.decref(nyvht__fdyuv)
    return NativeValue(oxnr__nmv._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        hkao__secw, evoae__lxuhm = args
        wgohi__xihmg = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        wgohi__xihmg.data = hkao__secw
        wgohi__xihmg.name = evoae__lxuhm
        context.nrt.incref(builder, signature.args[0], hkao__secw)
        context.nrt.incref(builder, signature.args[1], evoae__lxuhm)
        dtype = _dt_index_data_typ.dtype
        wgohi__xihmg.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return wgohi__xihmg._getvalue()
    dbey__qgtw = DatetimeIndexType(name, data)
    sig = signature(dbey__qgtw, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    zpc__gvppl = args[0]
    if equiv_set.has_shape(zpc__gvppl):
        return ArrayAnalysis.AnalyzeResult(shape=zpc__gvppl, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    qfh__ebhl = 'def impl(dti):\n'
    qfh__ebhl += '    numba.parfors.parfor.init_prange()\n'
    qfh__ebhl += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    qfh__ebhl += '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n'
    qfh__ebhl += '    n = len(A)\n'
    qfh__ebhl += '    S = np.empty(n, np.int64)\n'
    qfh__ebhl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    qfh__ebhl += '        val = A[i]\n'
    qfh__ebhl += '        ts = bodo.utils.conversion.box_if_dt64(val)\n'
    if field in ['weekday']:
        qfh__ebhl += '        S[i] = ts.' + field + '()\n'
    else:
        qfh__ebhl += '        S[i] = ts.' + field + '\n'
    qfh__ebhl += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    ege__wueb = {}
    exec(qfh__ebhl, {'numba': numba, 'np': np, 'bodo': bodo}, ege__wueb)
    impl = ege__wueb['impl']
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
        gpw__vko = len(A)
        S = np.empty(gpw__vko, np.bool_)
        for i in numba.parfors.parfor.internal_prange(gpw__vko):
            val = A[i]
            vlif__zfixj = bodo.utils.conversion.box_if_dt64(val)
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(vlif__zfixj.year
                )
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        gpw__vko = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(gpw__vko)
        for i in numba.parfors.parfor.internal_prange(gpw__vko):
            val = A[i]
            vlif__zfixj = bodo.utils.conversion.box_if_dt64(val)
            S[i] = datetime.date(vlif__zfixj.year, vlif__zfixj.month,
                vlif__zfixj.day)
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
    ojrg__xpwq = dict(axis=axis, skipna=skipna)
    blc__lmlms = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.min()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        ymdxc__jgiqa = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(ymdxc__jgiqa)):
            if not bodo.libs.array_kernels.isna(ymdxc__jgiqa, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ymdxc__jgiqa[i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    ojrg__xpwq = dict(axis=axis, skipna=skipna)
    blc__lmlms = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.max()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        ymdxc__jgiqa = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(ymdxc__jgiqa)):
            if not bodo.libs.array_kernels.isna(ymdxc__jgiqa, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ymdxc__jgiqa[i])
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
    ojrg__xpwq = dict(freq=freq, tz=tz, normalize=normalize, closed=closed,
        ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst, dtype=
        dtype, copy=copy)
    blc__lmlms = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        nmxk__pwuty = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(nmxk__pwuty)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        aoi__gnuno = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            ymdxc__jgiqa = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            gpw__vko = len(ymdxc__jgiqa)
            S = np.empty(gpw__vko, aoi__gnuno)
            wjo__luqst = rhs.value
            for i in numba.parfors.parfor.internal_prange(gpw__vko):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ymdxc__jgiqa[i]) - wjo__luqst)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        aoi__gnuno = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            ymdxc__jgiqa = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            gpw__vko = len(ymdxc__jgiqa)
            S = np.empty(gpw__vko, aoi__gnuno)
            wjo__luqst = lhs.value
            for i in numba.parfors.parfor.internal_prange(gpw__vko):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    wjo__luqst - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(ymdxc__jgiqa[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    shmgc__ayu = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    qfh__ebhl = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        qfh__ebhl += '  dt_index, _str = lhs, rhs\n'
        gghu__btnj = 'arr[i] {} other'.format(shmgc__ayu)
    else:
        qfh__ebhl += '  dt_index, _str = rhs, lhs\n'
        gghu__btnj = 'other {} arr[i]'.format(shmgc__ayu)
    qfh__ebhl += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    qfh__ebhl += '  l = len(arr)\n'
    qfh__ebhl += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    qfh__ebhl += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    qfh__ebhl += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    qfh__ebhl += '    S[i] = {}\n'.format(gghu__btnj)
    qfh__ebhl += '  return S\n'
    ege__wueb = {}
    exec(qfh__ebhl, {'bodo': bodo, 'numba': numba, 'np': np}, ege__wueb)
    impl = ege__wueb['impl']
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
        epwl__pmbzi = parse_dtype(dtype, 'pandas.Index')
        tsng__qeytl = False
    else:
        epwl__pmbzi = getattr(data, 'dtype', None)
        tsng__qeytl = True
    if isinstance(epwl__pmbzi, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType
        ) or epwl__pmbzi == types.NPDatetime('ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType
        ) or epwl__pmbzi == types.NPTimedelta('ns'):

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
        if isinstance(epwl__pmbzi, (types.Integer, types.Float, types.Boolean)
            ):
            if tsng__qeytl:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    nmxk__pwuty = bodo.utils.conversion.coerce_to_array(data)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        nmxk__pwuty, name)
            else:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    nmxk__pwuty = bodo.utils.conversion.coerce_to_array(data)
                    jmb__jncv = bodo.utils.conversion.fix_arr_dtype(nmxk__pwuty
                        , epwl__pmbzi)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        jmb__jncv, name)
        elif epwl__pmbzi in [types.string, bytes_type]:

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
                rpuv__tmt = bodo.hiframes.pd_index_ext.get_index_data(dti)
                val = rpuv__tmt[ind]
                return bodo.utils.conversion.box_if_dt64(val)
            return impl
        else:

            def impl(dti, ind):
                rpuv__tmt = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                kgt__tof = rpuv__tmt[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(kgt__tof,
                    name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            rzw__ytje = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(rzw__ytje[ind])
        return impl

    def impl(I, ind):
        rzw__ytje = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        kgt__tof = rzw__ytje[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(kgt__tof, name)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_categorical_index_getitem(I, ind):
    if not isinstance(I, CategoricalIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            rgw__yoo = bodo.hiframes.pd_index_ext.get_index_data(I)
            val = rgw__yoo[ind]
            return val
        return impl
    if isinstance(ind, types.SliceType):

        def impl(I, ind):
            rgw__yoo = bodo.hiframes.pd_index_ext.get_index_data(I)
            name = bodo.hiframes.pd_index_ext.get_index_name(I)
            kgt__tof = rgw__yoo[ind]
            return bodo.hiframes.pd_index_ext.init_categorical_index(kgt__tof,
                name)
        return impl
    raise BodoError(
        f'pd.CategoricalIndex.__getitem__: unsupported index type {ind}')


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    ojxmo__ixy = False
    grqtz__jsm = False
    if closed is None:
        ojxmo__ixy = True
        grqtz__jsm = True
    elif closed == 'left':
        ojxmo__ixy = True
    elif closed == 'right':
        grqtz__jsm = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return ojxmo__ixy, grqtz__jsm


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
    ojrg__xpwq = dict(tz=tz, normalize=normalize, closed=closed)
    blc__lmlms = dict(tz=None, normalize=False, closed=None)
    check_unsupported_args('pandas.date_range', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise_bodo_error('pd.date_range(): tz argument not supported yet')
    wuxci__lvw = ''
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
        wuxci__lvw = "  freq = 'D'\n"
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise_bodo_error(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )
    qfh__ebhl = """def f(start=None, end=None, periods=None, freq=None, tz=None, normalize=False, name=None, closed=None):
"""
    qfh__ebhl += wuxci__lvw
    if is_overload_none(start):
        qfh__ebhl += "  start_t = pd.Timestamp('1800-01-03')\n"
    else:
        qfh__ebhl += '  start_t = pd.Timestamp(start)\n'
    if is_overload_none(end):
        qfh__ebhl += "  end_t = pd.Timestamp('1800-01-03')\n"
    else:
        qfh__ebhl += '  end_t = pd.Timestamp(end)\n'
    if not is_overload_none(freq):
        qfh__ebhl += (
            '  stride = bodo.hiframes.pd_index_ext.to_offset_value(freq)\n')
        if is_overload_none(periods):
            qfh__ebhl += '  b = start_t.value\n'
            qfh__ebhl += (
                '  e = b + (end_t.value - b) // stride * stride + stride // 2 + 1\n'
                )
        elif not is_overload_none(start):
            qfh__ebhl += '  b = start_t.value\n'
            qfh__ebhl += '  addend = np.int64(periods) * np.int64(stride)\n'
            qfh__ebhl += '  e = np.int64(b) + addend\n'
        elif not is_overload_none(end):
            qfh__ebhl += '  e = end_t.value + stride\n'
            qfh__ebhl += '  addend = np.int64(periods) * np.int64(-stride)\n'
            qfh__ebhl += '  b = np.int64(e) + addend\n'
        else:
            raise_bodo_error(
                "at least 'start' or 'end' should be specified if a 'period' is given."
                )
        qfh__ebhl += '  arr = np.arange(b, e, stride, np.int64)\n'
    else:
        qfh__ebhl += '  delta = end_t.value - start_t.value\n'
        qfh__ebhl += '  step = delta / (periods - 1)\n'
        qfh__ebhl += '  arr1 = np.arange(0, periods, 1, np.float64)\n'
        qfh__ebhl += '  arr1 *= step\n'
        qfh__ebhl += '  arr1 += start_t.value\n'
        qfh__ebhl += '  arr = arr1.astype(np.int64)\n'
        qfh__ebhl += '  arr[-1] = end_t.value\n'
    qfh__ebhl += '  A = bodo.utils.conversion.convert_to_dt64ns(arr)\n'
    qfh__ebhl += (
        '  return bodo.hiframes.pd_index_ext.init_datetime_index(A, name)\n')
    ege__wueb = {}
    exec(qfh__ebhl, {'bodo': bodo, 'np': np, 'pd': pd}, ege__wueb)
    f = ege__wueb['f']
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
        ton__bvy = pd.Timedelta('1 day')
        if start is not None:
            ton__bvy = pd.Timedelta(start)
        pda__fyl = pd.Timedelta('1 day')
        if end is not None:
            pda__fyl = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        ojxmo__ixy, grqtz__jsm = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            blfm__jvomf = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = ton__bvy.value
                czlf__auhza = b + (pda__fyl.value - b
                    ) // blfm__jvomf * blfm__jvomf + blfm__jvomf // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = ton__bvy.value
                wnu__tjh = np.int64(periods) * np.int64(blfm__jvomf)
                czlf__auhza = np.int64(b) + wnu__tjh
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                czlf__auhza = pda__fyl.value + blfm__jvomf
                wnu__tjh = np.int64(periods) * np.int64(-blfm__jvomf)
                b = np.int64(czlf__auhza) + wnu__tjh
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            dvsig__zzk = np.arange(b, czlf__auhza, blfm__jvomf, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            tse__gqo = pda__fyl.value - ton__bvy.value
            step = tse__gqo / (periods - 1)
            kuoj__gkh = np.arange(0, periods, 1, np.float64)
            kuoj__gkh *= step
            kuoj__gkh += ton__bvy.value
            dvsig__zzk = kuoj__gkh.astype(np.int64)
            dvsig__zzk[-1] = pda__fyl.value
        if not ojxmo__ixy and len(dvsig__zzk) and dvsig__zzk[0
            ] == ton__bvy.value:
            dvsig__zzk = dvsig__zzk[1:]
        if not grqtz__jsm and len(dvsig__zzk) and dvsig__zzk[-1
            ] == pda__fyl.value:
            dvsig__zzk = dvsig__zzk[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(dvsig__zzk)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):
    nbuc__ykg = ColNamesMetaType(('year', 'week', 'day'))

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        gpw__vko = len(A)
        qbvy__lfmyb = bodo.libs.int_arr_ext.alloc_int_array(gpw__vko, np.uint32
            )
        ujnvh__wtg = bodo.libs.int_arr_ext.alloc_int_array(gpw__vko, np.uint32)
        aln__ejlo = bodo.libs.int_arr_ext.alloc_int_array(gpw__vko, np.uint32)
        for i in numba.parfors.parfor.internal_prange(gpw__vko):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(qbvy__lfmyb, i)
                bodo.libs.array_kernels.setna(ujnvh__wtg, i)
                bodo.libs.array_kernels.setna(aln__ejlo, i)
                continue
            qbvy__lfmyb[i], ujnvh__wtg[i], aln__ejlo[i
                ] = bodo.utils.conversion.box_if_dt64(A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((qbvy__lfmyb,
            ujnvh__wtg, aln__ejlo), idx, nbuc__ykg)
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
        wae__mtj = [('data', _timedelta_index_data_typ), ('name', fe_type.
            name_typ), ('dict', types.DictType(_timedelta_index_data_typ.
            dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, wae__mtj)


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    pvl__jxac = c.pyapi.import_module_noblock(rptsq__afmc)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    gle__iuvb = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([gle__iuvb])
    kws = c.pyapi.dict_pack([('name', nyvht__fdyuv)])
    qtlqi__jtfyi = c.pyapi.object_getattr_string(pvl__jxac, 'TimedeltaIndex')
    xmp__zpraf = c.pyapi.call(qtlqi__jtfyi, args, kws)
    c.pyapi.decref(gle__iuvb)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(pvl__jxac)
    c.pyapi.decref(qtlqi__jtfyi)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return xmp__zpraf


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    jcaa__ezjzb = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, jcaa__ezjzb
        ).value
    nyvht__fdyuv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nyvht__fdyuv).value
    c.pyapi.decref(jcaa__ezjzb)
    c.pyapi.decref(nyvht__fdyuv)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oxnr__nmv.data = data
    oxnr__nmv.name = name
    dtype = _timedelta_index_data_typ.dtype
    clgus__coc, ekvv__jgng = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    oxnr__nmv.dict = ekvv__jgng
    return NativeValue(oxnr__nmv._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        hkao__secw, evoae__lxuhm = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = hkao__secw
        timedelta_index.name = evoae__lxuhm
        context.nrt.incref(builder, signature.args[0], hkao__secw)
        context.nrt.incref(builder, signature.args[1], evoae__lxuhm)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    dbey__qgtw = TimedeltaIndexType(name)
    sig = signature(dbey__qgtw, data, name)
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
    qxr__mphgl = dict(deep=deep, dtype=dtype, names=names)
    btw__vdeav = idx_typ_to_format_str_map[TimedeltaIndexType].format('copy()')
    check_unsupported_args('TimedeltaIndex.copy', qxr__mphgl,
        idx_cpy_arg_defaults, fn_str=btw__vdeav, package_name='pandas',
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
    ojrg__xpwq = dict(axis=axis, skipna=skipna)
    blc__lmlms = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        gpw__vko = len(data)
        pqh__mdi = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(gpw__vko):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            pqh__mdi = min(pqh__mdi, val)
        amw__jrgr = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            pqh__mdi)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(amw__jrgr, count)
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    ojrg__xpwq = dict(axis=axis, skipna=skipna)
    blc__lmlms = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        gpw__vko = len(data)
        paazq__tqsb = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(gpw__vko):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            paazq__tqsb = max(paazq__tqsb, val)
        amw__jrgr = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            paazq__tqsb)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(amw__jrgr, count)
    return impl


def gen_tdi_field_impl(field):
    qfh__ebhl = 'def impl(tdi):\n'
    qfh__ebhl += '    numba.parfors.parfor.init_prange()\n'
    qfh__ebhl += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    qfh__ebhl += '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n'
    qfh__ebhl += '    n = len(A)\n'
    qfh__ebhl += '    S = np.empty(n, np.int64)\n'
    qfh__ebhl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    qfh__ebhl += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        qfh__ebhl += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        qfh__ebhl += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        qfh__ebhl += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        qfh__ebhl += '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n'
    else:
        assert False, 'invalid timedelta field'
    qfh__ebhl += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    ege__wueb = {}
    exec(qfh__ebhl, {'numba': numba, 'np': np, 'bodo': bodo}, ege__wueb)
    impl = ege__wueb['impl']
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
    ojrg__xpwq = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    blc__lmlms = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        nmxk__pwuty = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(nmxk__pwuty)
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
        wae__mtj = [('start', types.int64), ('stop', types.int64), ('step',
            types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, wae__mtj)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    qxr__mphgl = dict(deep=deep, dtype=dtype, names=names)
    btw__vdeav = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', qxr__mphgl,
        idx_cpy_arg_defaults, fn_str=btw__vdeav, package_name='pandas',
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
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    foax__alsw = c.pyapi.import_module_noblock(rptsq__afmc)
    ykxsv__fer = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    tbux__six = c.pyapi.from_native_value(types.int64, ykxsv__fer.start, c.
        env_manager)
    hybo__tmof = c.pyapi.from_native_value(types.int64, ykxsv__fer.stop, c.
        env_manager)
    gvnp__ymlsg = c.pyapi.from_native_value(types.int64, ykxsv__fer.step, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ykxsv__fer.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, ykxsv__fer.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([tbux__six, hybo__tmof, gvnp__ymlsg])
    kws = c.pyapi.dict_pack([('name', nyvht__fdyuv)])
    qtlqi__jtfyi = c.pyapi.object_getattr_string(foax__alsw, 'RangeIndex')
    lpob__waoup = c.pyapi.call(qtlqi__jtfyi, args, kws)
    c.pyapi.decref(tbux__six)
    c.pyapi.decref(hybo__tmof)
    c.pyapi.decref(gvnp__ymlsg)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(foax__alsw)
    c.pyapi.decref(qtlqi__jtfyi)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return lpob__waoup


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name
    ffhhf__chag = is_overload_constant_int(step) and get_overload_const_int(
        step) == 0

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        if ffhhf__chag:
            raise_bodo_error('Step must not be zero')
        lswe__bpet = cgutils.is_scalar_zero(builder, args[2])
        jejrl__evcad = context.get_python_api(builder)
        with builder.if_then(lswe__bpet):
            jejrl__evcad.err_format('PyExc_ValueError', 'Step must not be zero'
                )
            val = context.get_constant(types.int32, -1)
            builder.ret(val)
        ykxsv__fer = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ykxsv__fer.start = args[0]
        ykxsv__fer.stop = args[1]
        ykxsv__fer.step = args[2]
        ykxsv__fer.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return ykxsv__fer._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, bpcpk__yzmkn = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    tbux__six = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, tbux__six).value
    hybo__tmof = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, hybo__tmof).value
    gvnp__ymlsg = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, gvnp__ymlsg).value
    nyvht__fdyuv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nyvht__fdyuv).value
    c.pyapi.decref(tbux__six)
    c.pyapi.decref(hybo__tmof)
    c.pyapi.decref(gvnp__ymlsg)
    c.pyapi.decref(nyvht__fdyuv)
    ykxsv__fer = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ykxsv__fer.start = start
    ykxsv__fer.stop = stop
    ykxsv__fer.step = step
    ykxsv__fer.name = name
    return NativeValue(ykxsv__fer._getvalue())


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
        fzx__oxw = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(fzx__oxw.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        fzx__oxw = 'RangeIndex(...) must be called with integers'
        raise BodoError(fzx__oxw)
    jmofu__ucbm = 'start'
    wzip__hypmd = 'stop'
    cbjm__rgbp = 'step'
    if is_overload_none(start):
        jmofu__ucbm = '0'
    if is_overload_none(stop):
        wzip__hypmd = 'start'
        jmofu__ucbm = '0'
    if is_overload_none(step):
        cbjm__rgbp = '1'
    qfh__ebhl = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    qfh__ebhl += '  return init_range_index({}, {}, {}, name)\n'.format(
        jmofu__ucbm, wzip__hypmd, cbjm__rgbp)
    ege__wueb = {}
    exec(qfh__ebhl, {'init_range_index': init_range_index}, ege__wueb)
    cyxyk__arv = ege__wueb['_pd_range_index_imp']
    return cyxyk__arv


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
                usfvi__flph = numba.cpython.unicode._normalize_slice(idx,
                    len(I))
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * usfvi__flph.start
                stop = I._start + I._step * usfvi__flph.stop
                step = I._step * usfvi__flph.step
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
        wae__mtj = [('data', bodo.IntegerArrayType(types.int64)), ('name',
            fe_type.name_typ), ('dict', types.DictType(types.int64, types.
            int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, wae__mtj)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    qxr__mphgl = dict(deep=deep, dtype=dtype, names=names)
    btw__vdeav = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', qxr__mphgl,
        idx_cpy_arg_defaults, fn_str=btw__vdeav, package_name='pandas',
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
        hkao__secw, evoae__lxuhm, bpcpk__yzmkn = args
        nbsv__dfv = signature.return_type
        zhey__uzav = cgutils.create_struct_proxy(nbsv__dfv)(context, builder)
        zhey__uzav.data = hkao__secw
        zhey__uzav.name = evoae__lxuhm
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        zhey__uzav.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return zhey__uzav._getvalue()
    qhrkv__zoeto = get_overload_const_str(freq)
    dbey__qgtw = PeriodIndexType(qhrkv__zoeto, name)
    sig = signature(dbey__qgtw, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    foax__alsw = c.pyapi.import_module_noblock(rptsq__afmc)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        oxnr__nmv.data)
    isn__keuib = c.pyapi.from_native_value(bodo.IntegerArrayType(types.
        int64), oxnr__nmv.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, oxnr__nmv.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, oxnr__nmv.name,
        c.env_manager)
    jhi__bvb = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', isn__keuib), ('name', nyvht__fdyuv
        ), ('freq', jhi__bvb)])
    qtlqi__jtfyi = c.pyapi.object_getattr_string(foax__alsw, 'PeriodIndex')
    lpob__waoup = c.pyapi.call(qtlqi__jtfyi, args, kws)
    c.pyapi.decref(isn__keuib)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(jhi__bvb)
    c.pyapi.decref(foax__alsw)
    c.pyapi.decref(qtlqi__jtfyi)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return lpob__waoup


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    edk__wbb = c.pyapi.object_getattr_string(val, 'asi8')
    ckmh__fszqi = c.pyapi.call_method(val, 'isna', ())
    nyvht__fdyuv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nyvht__fdyuv).value
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    pvl__jxac = c.pyapi.import_module_noblock(rptsq__afmc)
    hpwb__euy = c.pyapi.object_getattr_string(pvl__jxac, 'arrays')
    isn__keuib = c.pyapi.call_method(hpwb__euy, 'IntegerArray', (edk__wbb,
        ckmh__fszqi))
    data = c.pyapi.to_native_value(arr_typ, isn__keuib).value
    c.pyapi.decref(edk__wbb)
    c.pyapi.decref(ckmh__fszqi)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(pvl__jxac)
    c.pyapi.decref(hpwb__euy)
    c.pyapi.decref(isn__keuib)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oxnr__nmv.data = data
    oxnr__nmv.name = name
    clgus__coc, ekvv__jgng = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(types.int64, types.int64), types.DictType(types.int64,
        types.int64)(), [])
    oxnr__nmv.dict = ekvv__jgng
    return NativeValue(oxnr__nmv._getvalue())


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
        xioul__rsxhx = get_categories_int_type(fe_type.data.dtype)
        wae__mtj = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(xioul__rsxhx, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type, wae__mtj)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    pvl__jxac = c.pyapi.import_module_noblock(rptsq__afmc)
    sbe__rior = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, sbe__rior.data)
    gle__iuvb = c.pyapi.from_native_value(typ.data, sbe__rior.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, sbe__rior.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, sbe__rior.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([gle__iuvb])
    kws = c.pyapi.dict_pack([('name', nyvht__fdyuv)])
    qtlqi__jtfyi = c.pyapi.object_getattr_string(pvl__jxac, 'CategoricalIndex')
    xmp__zpraf = c.pyapi.call(qtlqi__jtfyi, args, kws)
    c.pyapi.decref(gle__iuvb)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(pvl__jxac)
    c.pyapi.decref(qtlqi__jtfyi)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return xmp__zpraf


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    jcaa__ezjzb = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, jcaa__ezjzb).value
    nyvht__fdyuv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nyvht__fdyuv).value
    c.pyapi.decref(jcaa__ezjzb)
    c.pyapi.decref(nyvht__fdyuv)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oxnr__nmv.data = data
    oxnr__nmv.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    clgus__coc, ekvv__jgng = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    oxnr__nmv.dict = ekvv__jgng
    return NativeValue(oxnr__nmv._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        hkao__secw, evoae__lxuhm = args
        sbe__rior = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        sbe__rior.data = hkao__secw
        sbe__rior.name = evoae__lxuhm
        context.nrt.incref(builder, signature.args[0], hkao__secw)
        context.nrt.incref(builder, signature.args[1], evoae__lxuhm)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        sbe__rior.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return sbe__rior._getvalue()
    dbey__qgtw = CategoricalIndexType(data, name)
    sig = signature(dbey__qgtw, data, name)
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
    btw__vdeav = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    qxr__mphgl = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', qxr__mphgl,
        idx_cpy_arg_defaults, fn_str=btw__vdeav, package_name='pandas',
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
        wae__mtj = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, wae__mtj)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    pvl__jxac = c.pyapi.import_module_noblock(rptsq__afmc)
    mqpci__ktn = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, mqpci__ktn.data)
    gle__iuvb = c.pyapi.from_native_value(typ.data, mqpci__ktn.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, mqpci__ktn.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, mqpci__ktn.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([gle__iuvb])
    kws = c.pyapi.dict_pack([('name', nyvht__fdyuv)])
    qtlqi__jtfyi = c.pyapi.object_getattr_string(pvl__jxac, 'IntervalIndex')
    xmp__zpraf = c.pyapi.call(qtlqi__jtfyi, args, kws)
    c.pyapi.decref(gle__iuvb)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(pvl__jxac)
    c.pyapi.decref(qtlqi__jtfyi)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return xmp__zpraf


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    jcaa__ezjzb = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, jcaa__ezjzb).value
    nyvht__fdyuv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nyvht__fdyuv).value
    c.pyapi.decref(jcaa__ezjzb)
    c.pyapi.decref(nyvht__fdyuv)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oxnr__nmv.data = data
    oxnr__nmv.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    clgus__coc, ekvv__jgng = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    oxnr__nmv.dict = ekvv__jgng
    return NativeValue(oxnr__nmv._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        hkao__secw, evoae__lxuhm = args
        mqpci__ktn = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        mqpci__ktn.data = hkao__secw
        mqpci__ktn.name = evoae__lxuhm
        context.nrt.incref(builder, signature.args[0], hkao__secw)
        context.nrt.incref(builder, signature.args[1], evoae__lxuhm)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        mqpci__ktn.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return mqpci__ktn._getvalue()
    dbey__qgtw = IntervalIndexType(data, name)
    sig = signature(dbey__qgtw, data, name)
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
        wae__mtj = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, wae__mtj)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    btw__vdeav = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    qxr__mphgl = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', qxr__mphgl, idx_cpy_arg_defaults,
        fn_str=btw__vdeav, package_name='pandas', module_name='Index')
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
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    foax__alsw = c.pyapi.import_module_noblock(rptsq__afmc)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, oxnr__nmv.data)
    isn__keuib = c.pyapi.from_native_value(typ.data, oxnr__nmv.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, oxnr__nmv.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, oxnr__nmv.name,
        c.env_manager)
    hqc__ctsad = c.pyapi.make_none()
    qvt__bcdey = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    lpob__waoup = c.pyapi.call_method(foax__alsw, 'Index', (isn__keuib,
        hqc__ctsad, qvt__bcdey, nyvht__fdyuv))
    c.pyapi.decref(isn__keuib)
    c.pyapi.decref(hqc__ctsad)
    c.pyapi.decref(qvt__bcdey)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(foax__alsw)
    c.context.nrt.decref(c.builder, typ, val)
    return lpob__waoup


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        nbsv__dfv = signature.return_type
        oxnr__nmv = cgutils.create_struct_proxy(nbsv__dfv)(context, builder)
        oxnr__nmv.data = args[0]
        oxnr__nmv.name = args[1]
        context.nrt.incref(builder, nbsv__dfv.data, args[0])
        context.nrt.incref(builder, nbsv__dfv.name_typ, args[1])
        dtype = nbsv__dfv.dtype
        oxnr__nmv.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return oxnr__nmv._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    jcaa__ezjzb = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, jcaa__ezjzb).value
    nyvht__fdyuv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nyvht__fdyuv).value
    c.pyapi.decref(jcaa__ezjzb)
    c.pyapi.decref(nyvht__fdyuv)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oxnr__nmv.data = data
    oxnr__nmv.name = name
    dtype = typ.dtype
    clgus__coc, ekvv__jgng = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    oxnr__nmv.dict = ekvv__jgng
    return NativeValue(oxnr__nmv._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        wkhr__abt = dict(dtype=dtype)
        rign__jgwq = dict(dtype=None)
        check_unsupported_args(func_str, wkhr__abt, rign__jgwq,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                nmxk__pwuty = bodo.utils.conversion.coerce_to_ndarray(data)
                vymt__vuw = bodo.utils.conversion.fix_arr_dtype(nmxk__pwuty,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(vymt__vuw,
                    name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                nmxk__pwuty = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    nmxk__pwuty = nmxk__pwuty.copy()
                vymt__vuw = bodo.utils.conversion.fix_arr_dtype(nmxk__pwuty,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(vymt__vuw,
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
        wae__mtj = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, wae__mtj)


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
        wae__mtj = [('data', binary_array_type), ('name', fe_type.name_typ),
            ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, wae__mtj)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    qmbd__cpon = typ.data
    scalar_type = typ.data.dtype
    jcaa__ezjzb = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(qmbd__cpon, jcaa__ezjzb).value
    nyvht__fdyuv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, nyvht__fdyuv).value
    c.pyapi.decref(jcaa__ezjzb)
    c.pyapi.decref(nyvht__fdyuv)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oxnr__nmv.data = data
    oxnr__nmv.name = name
    clgus__coc, ekvv__jgng = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(scalar_type, types.int64), types.DictType(scalar_type,
        types.int64)(), [])
    oxnr__nmv.dict = ekvv__jgng
    return NativeValue(oxnr__nmv._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    qmbd__cpon = typ.data
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    foax__alsw = c.pyapi.import_module_noblock(rptsq__afmc)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, qmbd__cpon, oxnr__nmv.data)
    isn__keuib = c.pyapi.from_native_value(qmbd__cpon, oxnr__nmv.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, oxnr__nmv.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, oxnr__nmv.name,
        c.env_manager)
    hqc__ctsad = c.pyapi.make_none()
    qvt__bcdey = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    lpob__waoup = c.pyapi.call_method(foax__alsw, 'Index', (isn__keuib,
        hqc__ctsad, qvt__bcdey, nyvht__fdyuv))
    c.pyapi.decref(isn__keuib)
    c.pyapi.decref(hqc__ctsad)
    c.pyapi.decref(qvt__bcdey)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(foax__alsw)
    c.context.nrt.decref(c.builder, typ, val)
    return lpob__waoup


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name,
        data)(data, name)
    kenfi__ecwme = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, kenfi__ecwme


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        pfxv__fhi = 'bytes_type'
    else:
        pfxv__fhi = 'string_type'
    qfh__ebhl = 'def impl(context, builder, signature, args):\n'
    qfh__ebhl += '    assert len(args) == 2\n'
    qfh__ebhl += '    index_typ = signature.return_type\n'
    qfh__ebhl += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    qfh__ebhl += '    index_val.data = args[0]\n'
    qfh__ebhl += '    index_val.name = args[1]\n'
    qfh__ebhl += '    # increase refcount of stored values\n'
    qfh__ebhl += (
        '    context.nrt.incref(builder, signature.args[0], args[0])\n')
    qfh__ebhl += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    qfh__ebhl += '    # create empty dict for get_loc hashmap\n'
    qfh__ebhl += '    index_val.dict = context.compile_internal(\n'
    qfh__ebhl += '       builder,\n'
    qfh__ebhl += (
        f'       lambda: numba.typed.Dict.empty({pfxv__fhi}, types.int64),\n')
    qfh__ebhl += f'        types.DictType({pfxv__fhi}, types.int64)(), [],)\n'
    qfh__ebhl += '    return index_val._getvalue()\n'
    ege__wueb = {}
    exec(qfh__ebhl, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type}, ege__wueb)
    impl = ege__wueb['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    btw__vdeav = idx_typ_to_format_str_map[typ].format('copy()')
    qxr__mphgl = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', qxr__mphgl, idx_cpy_arg_defaults,
        fn_str=btw__vdeav, package_name='pandas', module_name='Index')
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
    jnsna__wvqic = I.dtype if not isinstance(I, RangeIndexType
        ) else types.int64
    eqa__galb = other.dtype if not isinstance(other, RangeIndexType
        ) else types.int64
    if jnsna__wvqic != eqa__galb:
        raise BodoError(
            f'Index.{func_name}(): incompatible types {jnsna__wvqic} and {eqa__galb}'
            )


@overload_method(NumericIndexType, 'union', inline='always')
@overload_method(StringIndexType, 'union', inline='always')
@overload_method(BinaryIndexType, 'union', inline='always')
@overload_method(DatetimeIndexType, 'union', inline='always')
@overload_method(TimedeltaIndexType, 'union', inline='always')
@overload_method(RangeIndexType, 'union', inline='always')
def overload_index_union(I, other, sort=None):
    ojrg__xpwq = dict(sort=sort)
    clie__tbqoq = dict(sort=None)
    check_unsupported_args('Index.union', ojrg__xpwq, clie__tbqoq,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('union', I, other)
    gwb__yocix = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        vfnp__bvft = bodo.utils.conversion.coerce_to_array(I)
        wjs__wsb = bodo.utils.conversion.coerce_to_array(other)
        hijwh__gaeq = bodo.libs.array_kernels.concat([vfnp__bvft, wjs__wsb])
        rtq__oasvm = bodo.libs.array_kernels.unique(hijwh__gaeq)
        return gwb__yocix(rtq__oasvm, None)
    return impl


@overload_method(NumericIndexType, 'intersection', inline='always')
@overload_method(StringIndexType, 'intersection', inline='always')
@overload_method(BinaryIndexType, 'intersection', inline='always')
@overload_method(DatetimeIndexType, 'intersection', inline='always')
@overload_method(TimedeltaIndexType, 'intersection', inline='always')
@overload_method(RangeIndexType, 'intersection', inline='always')
def overload_index_intersection(I, other, sort=None):
    ojrg__xpwq = dict(sort=sort)
    clie__tbqoq = dict(sort=None)
    check_unsupported_args('Index.intersection', ojrg__xpwq, clie__tbqoq,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('intersection', I, other)
    gwb__yocix = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        vfnp__bvft = bodo.utils.conversion.coerce_to_array(I)
        wjs__wsb = bodo.utils.conversion.coerce_to_array(other)
        suz__asvm = bodo.libs.array_kernels.unique(vfnp__bvft)
        qmka__oesuy = bodo.libs.array_kernels.unique(wjs__wsb)
        hijwh__gaeq = bodo.libs.array_kernels.concat([suz__asvm, qmka__oesuy])
        uvqy__opz = pd.Series(hijwh__gaeq).sort_values().values
        apz__xsfz = bodo.libs.array_kernels.intersection_mask(uvqy__opz)
        return gwb__yocix(uvqy__opz[apz__xsfz], None)
    return impl


@overload_method(NumericIndexType, 'difference', inline='always')
@overload_method(StringIndexType, 'difference', inline='always')
@overload_method(BinaryIndexType, 'difference', inline='always')
@overload_method(DatetimeIndexType, 'difference', inline='always')
@overload_method(TimedeltaIndexType, 'difference', inline='always')
@overload_method(RangeIndexType, 'difference', inline='always')
def overload_index_difference(I, other, sort=None):
    ojrg__xpwq = dict(sort=sort)
    clie__tbqoq = dict(sort=None)
    check_unsupported_args('Index.difference', ojrg__xpwq, clie__tbqoq,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('difference', I, other)
    gwb__yocix = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        vfnp__bvft = bodo.utils.conversion.coerce_to_array(I)
        wjs__wsb = bodo.utils.conversion.coerce_to_array(other)
        suz__asvm = bodo.libs.array_kernels.unique(vfnp__bvft)
        qmka__oesuy = bodo.libs.array_kernels.unique(wjs__wsb)
        apz__xsfz = np.empty(len(suz__asvm), np.bool_)
        bodo.libs.array.array_isin(apz__xsfz, suz__asvm, qmka__oesuy, False)
        return gwb__yocix(suz__asvm[~apz__xsfz], None)
    return impl


@overload_method(NumericIndexType, 'symmetric_difference', inline='always')
@overload_method(StringIndexType, 'symmetric_difference', inline='always')
@overload_method(BinaryIndexType, 'symmetric_difference', inline='always')
@overload_method(DatetimeIndexType, 'symmetric_difference', inline='always')
@overload_method(TimedeltaIndexType, 'symmetric_difference', inline='always')
@overload_method(RangeIndexType, 'symmetric_difference', inline='always')
def overload_index_symmetric_difference(I, other, result_name=None, sort=None):
    ojrg__xpwq = dict(result_name=result_name, sort=sort)
    clie__tbqoq = dict(result_name=None, sort=None)
    check_unsupported_args('Index.symmetric_difference', ojrg__xpwq,
        clie__tbqoq, package_name='pandas', module_name='Index')
    _verify_setop_compatible('symmetric_difference', I, other)
    gwb__yocix = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, result_name=None, sort=None):
        vfnp__bvft = bodo.utils.conversion.coerce_to_array(I)
        wjs__wsb = bodo.utils.conversion.coerce_to_array(other)
        suz__asvm = bodo.libs.array_kernels.unique(vfnp__bvft)
        qmka__oesuy = bodo.libs.array_kernels.unique(wjs__wsb)
        ycc__exc = np.empty(len(suz__asvm), np.bool_)
        uft__uxgiz = np.empty(len(qmka__oesuy), np.bool_)
        bodo.libs.array.array_isin(ycc__exc, suz__asvm, qmka__oesuy, False)
        bodo.libs.array.array_isin(uft__uxgiz, qmka__oesuy, suz__asvm, False)
        glx__hmem = bodo.libs.array_kernels.concat([suz__asvm[~ycc__exc],
            qmka__oesuy[~uft__uxgiz]])
        return gwb__yocix(glx__hmem, None)
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
    ojrg__xpwq = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value)
    clie__tbqoq = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', ojrg__xpwq, clie__tbqoq,
        package_name='pandas', module_name='Index')
    return lambda I, indices: I[indices]


def _init_engine(I, ban_unique=True):
    pass


@overload(_init_engine)
def overload_init_engine(I, ban_unique=True):
    if isinstance(I, CategoricalIndexType):

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                dvsig__zzk = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(dvsig__zzk)):
                    if not bodo.libs.array_kernels.isna(dvsig__zzk, i):
                        val = (bodo.hiframes.pd_categorical_ext.
                            get_code_for_value(dvsig__zzk.dtype, dvsig__zzk[i])
                            )
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl
    else:

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                dvsig__zzk = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(dvsig__zzk)):
                    if not bodo.libs.array_kernels.isna(dvsig__zzk, i):
                        val = dvsig__zzk[i]
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
                dvsig__zzk = bodo.utils.conversion.coerce_to_array(I)
                xrqga__ath = (bodo.hiframes.pd_categorical_ext.
                    get_code_for_value(dvsig__zzk.dtype, key))
                return xrqga__ath in I._dict
            else:
                fzx__oxw = (
                    'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                    )
                warnings.warn(fzx__oxw)
                dvsig__zzk = bodo.utils.conversion.coerce_to_array(I)
                ind = -1
                for i in range(len(dvsig__zzk)):
                    if not bodo.libs.array_kernels.isna(dvsig__zzk, i):
                        if dvsig__zzk[i] == key:
                            ind = i
            return ind != -1
        return impl

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I, False)
            return key in I._dict
        else:
            fzx__oxw = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(fzx__oxw)
            dvsig__zzk = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(dvsig__zzk)):
                if not bodo.libs.array_kernels.isna(dvsig__zzk, i):
                    if dvsig__zzk[i] == key:
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
    ojrg__xpwq = dict(method=method, tolerance=tolerance)
    blc__lmlms = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', ojrg__xpwq, blc__lmlms,
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
            fzx__oxw = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(fzx__oxw)
            dvsig__zzk = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(dvsig__zzk)):
                if dvsig__zzk[i] == key:
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
        hmekk__jjczo = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                gpw__vko = len(I)
                lsri__qjci = np.empty(gpw__vko, np.bool_)
                for i in numba.parfors.parfor.internal_prange(gpw__vko):
                    lsri__qjci[i] = not hmekk__jjczo
                return lsri__qjci
            return impl
        qfh__ebhl = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if hmekk__jjczo else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        ege__wueb = {}
        exec(qfh__ebhl, {'bodo': bodo, 'np': np, 'numba': numba}, ege__wueb)
        impl = ege__wueb['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for occ__kzdm in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(occ__kzdm, overload_name, no_unliteral=True,
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
            dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(dvsig__zzk, 1)
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
            dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(dvsig__zzk, 2)
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
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        lsri__qjci = bodo.libs.array_kernels.duplicated((dvsig__zzk,))
        return lsri__qjci
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
    ojrg__xpwq = dict(keep=keep)
    blc__lmlms = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    qfh__ebhl = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        qfh__ebhl += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        qfh__ebhl += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    ege__wueb = {}
    exec(qfh__ebhl, {'bodo': bodo}, ege__wueb)
    impl = ege__wueb['impl']
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
    zpc__gvppl = args[0]
    if isinstance(self.typemap[zpc__gvppl.name], (HeterogeneousIndexType,
        MultiIndexType)):
        return None
    if equiv_set.has_shape(zpc__gvppl):
        return ArrayAnalysis.AnalyzeResult(shape=zpc__gvppl, pre=[])
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
    ojrg__xpwq = dict(na_action=na_action)
    imcj__ebajl = dict(na_action=None)
    check_unsupported_args('Index.map', ojrg__xpwq, imcj__ebajl,
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
    bvq__gnygg = numba.core.registry.cpu_target.typing_context
    xsmt__zef = numba.core.registry.cpu_target.target_context
    try:
        aweme__tmm = get_const_func_output_type(mapper, (dtype,), {},
            bvq__gnygg, xsmt__zef)
    except Exception as czlf__auhza:
        raise_bodo_error(get_udf_error_msg('Index.map()', czlf__auhza))
    pop__nyff = get_udf_out_arr_type(aweme__tmm)
    func = get_overload_const_func(mapper, None)
    qfh__ebhl = 'def f(I, mapper, na_action=None):\n'
    qfh__ebhl += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    qfh__ebhl += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    qfh__ebhl += '  numba.parfors.parfor.init_prange()\n'
    qfh__ebhl += '  n = len(A)\n'
    qfh__ebhl += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    qfh__ebhl += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    qfh__ebhl += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    qfh__ebhl += '    v = map_func(t2)\n'
    qfh__ebhl += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    qfh__ebhl += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    jejf__qosiw = bodo.compiler.udf_jit(func)
    ege__wueb = {}
    exec(qfh__ebhl, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': jejf__qosiw, '_arr_typ': pop__nyff,
        'init_nested_counts': bodo.utils.indexing.init_nested_counts,
        'add_nested_counts': bodo.utils.indexing.add_nested_counts,
        'data_arr_type': pop__nyff.dtype}, ege__wueb)
    f = ege__wueb['f']
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
    uoj__ncl, cbc__kquf = sig.args
    if uoj__ncl != cbc__kquf:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    uoj__ncl, cbc__kquf = sig.args
    if uoj__ncl != cbc__kquf:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):
            qfh__ebhl = (
                'def impl(lhs, rhs):\n  arr = bodo.utils.conversion.coerce_to_array(lhs)\n'
                )
            if rhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                qfh__ebhl += """  dt = bodo.utils.conversion.unbox_if_timestamp(rhs)
  return op(arr, dt)
"""
            else:
                qfh__ebhl += """  rhs_arr = bodo.utils.conversion.get_array_if_series_or_index(rhs)
  return op(arr, rhs_arr)
"""
            ege__wueb = {}
            exec(qfh__ebhl, {'bodo': bodo, 'op': op}, ege__wueb)
            impl = ege__wueb['impl']
            return impl
        if is_index_type(rhs):
            qfh__ebhl = (
                'def impl(lhs, rhs):\n  arr = bodo.utils.conversion.coerce_to_array(rhs)\n'
                )
            if lhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                qfh__ebhl += """  dt = bodo.utils.conversion.unbox_if_timestamp(lhs)
  return op(dt, arr)
"""
            else:
                qfh__ebhl += """  lhs_arr = bodo.utils.conversion.get_array_if_series_or_index(lhs)
  return op(lhs_arr, arr)
"""
            ege__wueb = {}
            exec(qfh__ebhl, {'bodo': bodo, 'op': op}, ege__wueb)
            impl = ege__wueb['impl']
            return impl
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    dvsig__zzk = bodo.utils.conversion.coerce_to_array(data)
                    ocu__kcy = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    lsri__qjci = op(dvsig__zzk, ocu__kcy)
                    return lsri__qjci
                return impl3
            count = len(lhs.data.types)
            qfh__ebhl = 'def f(lhs, rhs):\n'
            qfh__ebhl += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            ege__wueb = {}
            exec(qfh__ebhl, {'op': op, 'np': np}, ege__wueb)
            impl = ege__wueb['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    dvsig__zzk = bodo.utils.conversion.coerce_to_array(data)
                    ocu__kcy = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    lsri__qjci = op(ocu__kcy, dvsig__zzk)
                    return lsri__qjci
                return impl4
            count = len(rhs.data.types)
            qfh__ebhl = 'def f(lhs, rhs):\n'
            qfh__ebhl += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            ege__wueb = {}
            exec(qfh__ebhl, {'op': op, 'np': np}, ege__wueb)
            impl = ege__wueb['f']
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
        wae__mtj = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, wae__mtj)


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    btw__vdeav = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    qxr__mphgl = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', qxr__mphgl, idx_cpy_arg_defaults,
        fn_str=btw__vdeav, package_name='pandas', module_name='Index')
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
    rptsq__afmc = c.context.insert_const_string(c.builder.module, 'pandas')
    foax__alsw = c.pyapi.import_module_noblock(rptsq__afmc)
    oxnr__nmv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, oxnr__nmv.data)
    isn__keuib = c.pyapi.from_native_value(typ.data, oxnr__nmv.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, oxnr__nmv.name)
    nyvht__fdyuv = c.pyapi.from_native_value(typ.name_typ, oxnr__nmv.name,
        c.env_manager)
    hqc__ctsad = c.pyapi.make_none()
    qvt__bcdey = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    lpob__waoup = c.pyapi.call_method(foax__alsw, 'Index', (isn__keuib,
        hqc__ctsad, qvt__bcdey, nyvht__fdyuv))
    c.pyapi.decref(isn__keuib)
    c.pyapi.decref(hqc__ctsad)
    c.pyapi.decref(qvt__bcdey)
    c.pyapi.decref(nyvht__fdyuv)
    c.pyapi.decref(foax__alsw)
    c.context.nrt.decref(c.builder, typ, val)
    return lpob__waoup


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        nbsv__dfv = signature.return_type
        oxnr__nmv = cgutils.create_struct_proxy(nbsv__dfv)(context, builder)
        oxnr__nmv.data = args[0]
        oxnr__nmv.name = args[1]
        context.nrt.incref(builder, nbsv__dfv.data, args[0])
        context.nrt.incref(builder, nbsv__dfv.name_typ, args[1])
        return oxnr__nmv._getvalue()
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
        qfh__ebhl = 'def _impl_nbytes(I):\n'
        qfh__ebhl += '    total = 0\n'
        qfh__ebhl += '    data = I._data\n'
        for i in range(I.nlevels):
            qfh__ebhl += f'    total += data[{i}].nbytes\n'
        qfh__ebhl += '    return total\n'
        zaoeq__itc = {}
        exec(qfh__ebhl, {}, zaoeq__itc)
        return zaoeq__itc['_impl_nbytes']
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
        jozb__hmuel = 'bodo.hiframes.pd_index_ext.get_index_name(I)'
    else:
        jozb__hmuel = 'name'
    qfh__ebhl = 'def impl(I, index=None, name=None):\n'
    qfh__ebhl += '    data = bodo.utils.conversion.index_to_array(I)\n'
    if is_overload_none(index):
        qfh__ebhl += '    new_index = I\n'
    elif is_pd_index_type(index):
        qfh__ebhl += '    new_index = index\n'
    elif isinstance(index, SeriesType):
        qfh__ebhl += '    arr = bodo.utils.conversion.coerce_to_array(index)\n'
        qfh__ebhl += (
            '    index_name = bodo.hiframes.pd_series_ext.get_series_name(index)\n'
            )
        qfh__ebhl += (
            '    new_index = bodo.utils.conversion.index_from_array(arr, index_name)\n'
            )
    elif bodo.utils.utils.is_array_typ(index, False):
        qfh__ebhl += (
            '    new_index = bodo.utils.conversion.index_from_array(index)\n')
    elif isinstance(index, (types.List, types.BaseTuple)):
        qfh__ebhl += '    arr = bodo.utils.conversion.coerce_to_array(index)\n'
        qfh__ebhl += (
            '    new_index = bodo.utils.conversion.index_from_array(arr)\n')
    else:
        raise_bodo_error(
            f'Index.to_series(): unsupported type for argument index: {type(index).__name__}'
            )
    qfh__ebhl += f'    new_name = {jozb__hmuel}\n'
    qfh__ebhl += (
        '    return bodo.hiframes.pd_series_ext.init_series(data, new_index, new_name)'
        )
    ege__wueb = {}
    exec(qfh__ebhl, {'bodo': bodo, 'np': np}, ege__wueb)
    impl = ege__wueb['impl']
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
        avnl__lvfx = 'I'
    elif is_overload_false(index):
        avnl__lvfx = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'Index.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'Index.to_frame(): index argument must be a compile time constant')
    qfh__ebhl = 'def impl(I, index=True, name=None):\n'
    qfh__ebhl += '    data = bodo.utils.conversion.index_to_array(I)\n'
    qfh__ebhl += f'    new_index = {avnl__lvfx}\n'
    if is_overload_none(name) and I.name_typ == types.none:
        ospo__uzuxc = ColNamesMetaType((0,))
    elif is_overload_none(name):
        ospo__uzuxc = ColNamesMetaType((I.name_typ,))
    elif is_overload_constant_str(name):
        ospo__uzuxc = ColNamesMetaType((get_overload_const_str(name),))
    elif is_overload_constant_int(name):
        ospo__uzuxc = ColNamesMetaType((get_overload_const_int(name),))
    else:
        raise_bodo_error(
            f'Index.to_frame(): only constant string/int are supported for argument name'
            )
    qfh__ebhl += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((data,), new_index, __col_name_meta_value)
"""
    ege__wueb = {}
    exec(qfh__ebhl, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        ospo__uzuxc}, ege__wueb)
    impl = ege__wueb['impl']
    return impl


@overload_method(MultiIndexType, 'to_frame', inline='always', no_unliteral=True
    )
def overload_multi_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        avnl__lvfx = 'I'
    elif is_overload_false(index):
        avnl__lvfx = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a compile time constant'
            )
    qfh__ebhl = 'def impl(I, index=True, name=None):\n'
    qfh__ebhl += '    data = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    qfh__ebhl += f'    new_index = {avnl__lvfx}\n'
    drw__pnfm = len(I.array_types)
    if is_overload_none(name) and I.names_typ == (types.none,) * drw__pnfm:
        ospo__uzuxc = ColNamesMetaType(tuple(range(drw__pnfm)))
    elif is_overload_none(name):
        ospo__uzuxc = ColNamesMetaType(I.names_typ)
    elif is_overload_constant_tuple(name) or is_overload_constant_list(name):
        if is_overload_constant_list(name):
            names = tuple(get_overload_const_list(name))
        else:
            names = get_overload_const_tuple(name)
        if drw__pnfm != len(names):
            raise_bodo_error(
                f'MultiIndex.to_frame(): expected {drw__pnfm} names, not {len(names)}'
                )
        if all(is_overload_constant_str(irb__nrmv) or
            is_overload_constant_int(irb__nrmv) for irb__nrmv in names):
            ospo__uzuxc = ColNamesMetaType(names)
        else:
            raise_bodo_error(
                'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
                )
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
            )
    qfh__ebhl += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(data, new_index, __col_name_meta_value,)
"""
    ege__wueb = {}
    exec(qfh__ebhl, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        ospo__uzuxc}, ege__wueb)
    impl = ege__wueb['impl']
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
    ojrg__xpwq = dict(dtype=dtype, na_value=na_value)
    blc__lmlms = dict(dtype=None, na_value=None)
    check_unsupported_args('Index.to_numpy', ojrg__xpwq, blc__lmlms,
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
            lxaps__xmfyd = list()
            for i in range(I._start, I._stop, I.step):
                lxaps__xmfyd.append(i)
            return lxaps__xmfyd
        return impl

    def impl(I):
        lxaps__xmfyd = list()
        for i in range(len(I)):
            lxaps__xmfyd.append(I[i])
        return lxaps__xmfyd
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
    zzbl__oixn = {DatetimeIndexType: 'datetime64', TimedeltaIndexType:
        'timedelta64', RangeIndexType: 'integer', BinaryIndexType: 'bytes',
        CategoricalIndexType: 'categorical', PeriodIndexType: 'period',
        IntervalIndexType: 'interval', MultiIndexType: 'mixed'}
    inferred_type = zzbl__oixn[type(I)]
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
    prpkm__jyjhi = {DatetimeIndexType: np.dtype('datetime64[ns]'),
        TimedeltaIndexType: np.dtype('timedelta64[ns]'), RangeIndexType: np
        .dtype('int64'), StringIndexType: np.dtype('O'), BinaryIndexType:
        np.dtype('O'), MultiIndexType: np.dtype('O')}
    dtype = prpkm__jyjhi[type(I)]
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
    edkp__ldx = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in edkp__ldx:
        init_func = edkp__ldx[type(I)]
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
    dbr__pdhu = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index, RangeIndexType: bodo.
        hiframes.pd_index_ext.init_range_index}
    if type(I) in dbr__pdhu:
        return dbr__pdhu[type(I)]
    raise BodoError(
        f'Unsupported type for standard Index constructor: {type(I)}')


@overload_method(NumericIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'min', no_unliteral=True, inline=
    'always')
def overload_index_min(I, axis=None, skipna=True):
    ojrg__xpwq = dict(axis=axis, skipna=skipna)
    blc__lmlms = dict(axis=None, skipna=True)
    check_unsupported_args('Index.min', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            jxzix__mrpb = len(I)
            if jxzix__mrpb == 0:
                return np.nan
            if I._step < 0:
                return I._start + I._step * (jxzix__mrpb - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.min(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_min(dvsig__zzk)
    return impl


@overload_method(NumericIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'max', no_unliteral=True, inline=
    'always')
def overload_index_max(I, axis=None, skipna=True):
    ojrg__xpwq = dict(axis=axis, skipna=skipna)
    blc__lmlms = dict(axis=None, skipna=True)
    check_unsupported_args('Index.max', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            jxzix__mrpb = len(I)
            if jxzix__mrpb == 0:
                return np.nan
            if I._step > 0:
                return I._start + I._step * (jxzix__mrpb - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.max(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_max(dvsig__zzk)
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
    ojrg__xpwq = dict(axis=axis, skipna=skipna)
    blc__lmlms = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmin', ojrg__xpwq, blc__lmlms,
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
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = init_numeric_index(np.arange(len(dvsig__zzk)))
        return bodo.libs.array_ops.array_op_idxmin(dvsig__zzk, index)
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
    ojrg__xpwq = dict(axis=axis, skipna=skipna)
    blc__lmlms = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmax', ojrg__xpwq, blc__lmlms,
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
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = np.arange(len(dvsig__zzk))
        return bodo.libs.array_ops.array_op_idxmax(dvsig__zzk, index)
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
    gwb__yocix = get_index_constructor(I)

    def impl(I):
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        zeou__lngrw = bodo.libs.array_kernels.unique(dvsig__zzk)
        return gwb__yocix(zeou__lngrw, name)
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
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        gpw__vko = bodo.libs.array_kernels.nunique(dvsig__zzk, dropna)
        return gpw__vko
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
            ozh__bbk = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_index_ext.get_index_data(I)
            gpw__vko = len(A)
            lsri__qjci = np.empty(gpw__vko, np.bool_)
            bodo.libs.array.array_isin(lsri__qjci, A, ozh__bbk, False)
            return lsri__qjci
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        lsri__qjci = bodo.libs.array_ops.array_op_isin(A, values)
        return lsri__qjci
    return impl


@overload_method(RangeIndexType, 'isin', no_unliteral=True, inline='always')
def overload_range_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            ozh__bbk = bodo.utils.conversion.coerce_to_array(values)
            A = np.arange(I.start, I.stop, I.step)
            gpw__vko = len(A)
            lsri__qjci = np.empty(gpw__vko, np.bool_)
            bodo.libs.array.array_isin(lsri__qjci, A, ozh__bbk, False)
            return lsri__qjci
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Index.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = np.arange(I.start, I.stop, I.step)
        lsri__qjci = bodo.libs.array_ops.array_op_isin(A, values)
        return lsri__qjci
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
        jxzix__mrpb = len(I)
        edad__eoq = start + step * (jxzix__mrpb - 1)
        zmabc__tom = edad__eoq - step * jxzix__mrpb
        return init_range_index(edad__eoq, zmabc__tom, -step, name)


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
    ojrg__xpwq = dict(return_indexer=return_indexer, key=key)
    blc__lmlms = dict(return_indexer=False, key=None)
    check_unsupported_args('Index.sort_values', ojrg__xpwq, blc__lmlms,
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
    gwb__yocix = get_index_constructor(I)
    ppuxo__prm = ColNamesMetaType(('$_bodo_col_',))

    def impl(I, return_indexer=False, ascending=True, na_position='last',
        key=None):
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = get_index_name(I)
        index = init_range_index(0, len(dvsig__zzk), 1, None)
        tfhz__edcuu = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            dvsig__zzk,), index, ppuxo__prm)
        yixaa__pfnl = tfhz__edcuu.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=False, na_position=na_position)
        lsri__qjci = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            yixaa__pfnl, 0)
        return gwb__yocix(lsri__qjci, name)
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
    ojrg__xpwq = dict(axis=axis, kind=kind, order=order)
    blc__lmlms = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Index.argsort', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, kind='quicksort', order=None):
            if I._step > 0:
                return np.arange(0, len(I), 1)
            else:
                return np.arange(len(I) - 1, -1, -1)
        return impl

    def impl(I, axis=0, kind='quicksort', order=None):
        dvsig__zzk = bodo.hiframes.pd_index_ext.get_index_data(I)
        lsri__qjci = bodo.hiframes.series_impl.argsort(dvsig__zzk)
        return lsri__qjci
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
        hvq__aotk = 'None'
    else:
        hvq__aotk = 'other'
    qfh__ebhl = 'def impl(I, cond, other=np.nan):\n'
    if isinstance(I, RangeIndexType):
        qfh__ebhl += '  arr = np.arange(I._start, I._stop, I._step)\n'
        gwb__yocix = 'init_numeric_index'
    else:
        qfh__ebhl += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    qfh__ebhl += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    qfh__ebhl += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {hvq__aotk})\n'
        )
    qfh__ebhl += f'  return constructor(out_arr, name)\n'
    ege__wueb = {}
    gwb__yocix = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(qfh__ebhl, {'bodo': bodo, 'np': np, 'constructor': gwb__yocix},
        ege__wueb)
    impl = ege__wueb['impl']
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
        hvq__aotk = 'None'
    else:
        hvq__aotk = 'other'
    qfh__ebhl = 'def impl(I, cond, other):\n'
    qfh__ebhl += '  cond = ~cond\n'
    if isinstance(I, RangeIndexType):
        qfh__ebhl += '  arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        qfh__ebhl += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    qfh__ebhl += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    qfh__ebhl += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {hvq__aotk})\n'
        )
    qfh__ebhl += f'  return constructor(out_arr, name)\n'
    ege__wueb = {}
    gwb__yocix = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(qfh__ebhl, {'bodo': bodo, 'np': np, 'constructor': gwb__yocix},
        ege__wueb)
    impl = ege__wueb['impl']
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
    ojrg__xpwq = dict(axis=axis)
    blc__lmlms = dict(axis=None)
    check_unsupported_args('Index.repeat', ojrg__xpwq, blc__lmlms,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Index.repeat(): 'repeats' should be an integer or array of integers"
            )
    qfh__ebhl = 'def impl(I, repeats, axis=None):\n'
    if not isinstance(repeats, types.Integer):
        qfh__ebhl += (
            '    repeats = bodo.utils.conversion.coerce_to_array(repeats)\n')
    if isinstance(I, RangeIndexType):
        qfh__ebhl += '    arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        qfh__ebhl += '    arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    qfh__ebhl += '    name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    qfh__ebhl += (
        '    out_arr = bodo.libs.array_kernels.repeat_kernel(arr, repeats)\n')
    qfh__ebhl += '    return constructor(out_arr, name)'
    ege__wueb = {}
    gwb__yocix = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(qfh__ebhl, {'bodo': bodo, 'np': np, 'constructor': gwb__yocix},
        ege__wueb)
    impl = ege__wueb['impl']
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
    huhpr__dxgc = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, huhpr__dxgc])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    huhpr__dxgc = context.get_constant_null(types.DictType(types.int64,
        types.int64))
    return lir.Constant.literal_struct([data, name, huhpr__dxgc])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    huhpr__dxgc = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, huhpr__dxgc])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    qmbd__cpon = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, qmbd__cpon, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    huhpr__dxgc = context.get_constant_null(types.DictType(scalar_type,
        types.int64))
    return lir.Constant.literal_struct([data, name, huhpr__dxgc])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [tmu__ghtm] = sig.args
    [index] = args
    dnnrn__hxfn = context.make_helper(builder, tmu__ghtm, value=index)
    uqtrx__vpnmc = context.make_helper(builder, sig.return_type)
    sft__czo = cgutils.alloca_once_value(builder, dnnrn__hxfn.start)
    cfy__srcd = context.get_constant(types.intp, 0)
    poqa__xrjl = cgutils.alloca_once_value(builder, cfy__srcd)
    uqtrx__vpnmc.iter = sft__czo
    uqtrx__vpnmc.stop = dnnrn__hxfn.stop
    uqtrx__vpnmc.step = dnnrn__hxfn.step
    uqtrx__vpnmc.count = poqa__xrjl
    jdho__kxl = builder.sub(dnnrn__hxfn.stop, dnnrn__hxfn.start)
    tbj__adk = context.get_constant(types.intp, 1)
    ubwj__vpxu = builder.icmp_signed('>', jdho__kxl, cfy__srcd)
    wyj__ntu = builder.icmp_signed('>', dnnrn__hxfn.step, cfy__srcd)
    vqu__ecmj = builder.not_(builder.xor(ubwj__vpxu, wyj__ntu))
    with builder.if_then(vqu__ecmj):
        kxz__oqfk = builder.srem(jdho__kxl, dnnrn__hxfn.step)
        kxz__oqfk = builder.select(ubwj__vpxu, kxz__oqfk, builder.neg(
            kxz__oqfk))
        mywi__zba = builder.icmp_signed('>', kxz__oqfk, cfy__srcd)
        pmh__ecpx = builder.add(builder.sdiv(jdho__kxl, dnnrn__hxfn.step),
            builder.select(mywi__zba, tbj__adk, cfy__srcd))
        builder.store(pmh__ecpx, poqa__xrjl)
    xmp__zpraf = uqtrx__vpnmc._getvalue()
    ipjrp__yqbwo = impl_ret_new_ref(context, builder, sig.return_type,
        xmp__zpraf)
    return ipjrp__yqbwo


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
    for dlhss__cszny in index_unsupported_methods:
        for hwjlx__zcax, typ in index_types:
            overload_method(typ, dlhss__cszny, no_unliteral=True)(
                create_unsupported_overload(hwjlx__zcax.format(dlhss__cszny +
                '()')))
    for uhk__qsey in index_unsupported_atrs:
        for hwjlx__zcax, typ in index_types:
            overload_attribute(typ, uhk__qsey, no_unliteral=True)(
                create_unsupported_overload(hwjlx__zcax.format(uhk__qsey)))
    inntq__mlo = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    nhwvj__xxih = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods), (BinaryIndexType,
        binary_index_unsupported_methods), (StringIndexType,
        string_index_unsupported_methods)]
    for typ, qmx__caxo in nhwvj__xxih:
        hwjlx__zcax = idx_typ_to_format_str_map[typ]
        for mjcb__rfvtp in qmx__caxo:
            overload_method(typ, mjcb__rfvtp, no_unliteral=True)(
                create_unsupported_overload(hwjlx__zcax.format(mjcb__rfvtp +
                '()')))
    for typ, dfov__fjsqa in inntq__mlo:
        hwjlx__zcax = idx_typ_to_format_str_map[typ]
        for uhk__qsey in dfov__fjsqa:
            overload_attribute(typ, uhk__qsey, no_unliteral=True)(
                create_unsupported_overload(hwjlx__zcax.format(uhk__qsey)))


_install_index_unsupported()
