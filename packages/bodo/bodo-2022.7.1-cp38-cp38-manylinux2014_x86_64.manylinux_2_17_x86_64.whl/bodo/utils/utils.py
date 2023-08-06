"""
Collection of utility functions. Needs to be refactored in separate files.
"""
import hashlib
import inspect
import keyword
import re
import warnings
from enum import Enum
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, types
from numba.core.imputils import lower_builtin, lower_constant
from numba.core.ir_utils import find_callname, find_const, get_definition, guard, mk_unique_var, require
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload
from numba.np.arrayobj import get_itemsize, make_array, populate_array
import bodo
from bodo.libs.binary_arr_ext import bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import num_total_chars, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import NOT_CONSTANT, BodoError, BodoWarning, MetaType, is_str_arr_type
int128_type = types.Integer('int128', 128)


class CTypeEnum(Enum):
    Int8 = 0
    UInt8 = 1
    Int32 = 2
    UInt32 = 3
    Int64 = 4
    UInt64 = 7
    Float32 = 5
    Float64 = 6
    Int16 = 8
    UInt16 = 9
    STRING = 10
    Bool = 11
    Decimal = 12
    Date = 13
    Datetime = 14
    Timedelta = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 20


_numba_to_c_type_map = {types.int8: CTypeEnum.Int8.value, types.uint8:
    CTypeEnum.UInt8.value, types.int32: CTypeEnum.Int32.value, types.uint32:
    CTypeEnum.UInt32.value, types.int64: CTypeEnum.Int64.value, types.
    uint64: CTypeEnum.UInt64.value, types.float32: CTypeEnum.Float32.value,
    types.float64: CTypeEnum.Float64.value, types.NPDatetime('ns'):
    CTypeEnum.Datetime.value, types.NPTimedelta('ns'): CTypeEnum.Timedelta.
    value, types.bool_: CTypeEnum.Bool.value, types.int16: CTypeEnum.Int16.
    value, types.uint16: CTypeEnum.UInt16.value, int128_type: CTypeEnum.
    Int128.value}
numba.core.errors.error_extras = {'unsupported_error': '', 'typing': '',
    'reportable': '', 'interpreter': '', 'constant_inference': ''}
np_alloc_callnames = 'empty', 'zeros', 'ones', 'full'
CONST_DICT_SLOW_WARN_THRESHOLD = 100
CONST_LIST_SLOW_WARN_THRESHOLD = 100000


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


def get_constant(func_ir, var, default=NOT_CONSTANT):
    ajwx__mkig = guard(get_definition, func_ir, var)
    if ajwx__mkig is None:
        return default
    if isinstance(ajwx__mkig, ir.Const):
        return ajwx__mkig.value
    if isinstance(ajwx__mkig, ir.Var):
        return get_constant(func_ir, ajwx__mkig, default)
    return default


def numba_to_c_type(t):
    if isinstance(t, bodo.libs.decimal_arr_ext.Decimal128Type):
        return CTypeEnum.Decimal.value
    if t == bodo.hiframes.datetime_date_ext.datetime_date_type:
        return CTypeEnum.Date.value
    return _numba_to_c_type_map[t]


def is_alloc_callname(func_name, mod_name):
    return isinstance(mod_name, str) and (mod_name == 'numpy' and func_name in
        np_alloc_callnames or func_name == 'empty_inferred' and mod_name in
        ('numba.extending', 'numba.np.unsafe.ndarray') or func_name ==
        'pre_alloc_string_array' and mod_name == 'bodo.libs.str_arr_ext' or
        func_name == 'pre_alloc_binary_array' and mod_name ==
        'bodo.libs.binary_arr_ext' or func_name ==
        'alloc_random_access_string_array' and mod_name ==
        'bodo.libs.str_ext' or func_name == 'pre_alloc_array_item_array' and
        mod_name == 'bodo.libs.array_item_arr_ext' or func_name ==
        'pre_alloc_struct_array' and mod_name == 'bodo.libs.struct_arr_ext' or
        func_name == 'pre_alloc_map_array' and mod_name ==
        'bodo.libs.map_arr_ext' or func_name == 'pre_alloc_tuple_array' and
        mod_name == 'bodo.libs.tuple_arr_ext' or func_name ==
        'alloc_bool_array' and mod_name == 'bodo.libs.bool_arr_ext' or 
        func_name == 'alloc_int_array' and mod_name ==
        'bodo.libs.int_arr_ext' or func_name == 'alloc_datetime_date_array' and
        mod_name == 'bodo.hiframes.datetime_date_ext' or func_name ==
        'alloc_datetime_timedelta_array' and mod_name ==
        'bodo.hiframes.datetime_timedelta_ext' or func_name ==
        'alloc_decimal_array' and mod_name == 'bodo.libs.decimal_arr_ext' or
        func_name == 'alloc_categorical_array' and mod_name ==
        'bodo.hiframes.pd_categorical_ext' or func_name == 'gen_na_array' and
        mod_name == 'bodo.libs.array_kernels')


def find_build_tuple(func_ir, var):
    require(isinstance(var, (ir.Var, str)))
    twu__fqknr = get_definition(func_ir, var)
    require(isinstance(twu__fqknr, ir.Expr))
    require(twu__fqknr.op == 'build_tuple')
    return twu__fqknr.items


def cprint(*s):
    print(*s)


@infer_global(cprint)
class CprintInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.none, *unliteral_all(args))


typ_to_format = {types.int32: 'd', types.uint32: 'u', types.int64: 'lld',
    types.uint64: 'llu', types.float32: 'f', types.float64: 'lf', types.
    voidptr: 's'}


@lower_builtin(cprint, types.VarArg(types.Any))
def cprint_lower(context, builder, sig, args):
    for hkp__rmwtk, val in enumerate(args):
        typ = sig.args[hkp__rmwtk]
        if isinstance(typ, types.ArrayCTypes):
            cgutils.printf(builder, '%p ', val)
            continue
        owca__yspi = typ_to_format[typ]
        cgutils.printf(builder, '%{} '.format(owca__yspi), val)
    cgutils.printf(builder, '\n')
    return context.get_dummy_value()


def is_whole_slice(typemap, func_ir, var, accept_stride=False):
    require(typemap[var.name] == types.slice2_type or accept_stride and 
        typemap[var.name] == types.slice3_type)
    nfpd__oqpa = get_definition(func_ir, var)
    require(isinstance(nfpd__oqpa, ir.Expr) and nfpd__oqpa.op == 'call')
    assert len(nfpd__oqpa.args) == 2 or accept_stride and len(nfpd__oqpa.args
        ) == 3
    assert find_callname(func_ir, nfpd__oqpa) == ('slice', 'builtins')
    wuac__amkmd = get_definition(func_ir, nfpd__oqpa.args[0])
    ssfbn__bsrah = get_definition(func_ir, nfpd__oqpa.args[1])
    require(isinstance(wuac__amkmd, ir.Const) and wuac__amkmd.value == None)
    require(isinstance(ssfbn__bsrah, ir.Const) and ssfbn__bsrah.value == None)
    return True


def is_slice_equiv_arr(arr_var, index_var, func_ir, equiv_set,
    accept_stride=False):
    hod__jlbk = get_definition(func_ir, index_var)
    require(find_callname(func_ir, hod__jlbk) == ('slice', 'builtins'))
    require(len(hod__jlbk.args) in (2, 3))
    require(find_const(func_ir, hod__jlbk.args[0]) in (0, None))
    require(equiv_set.is_equiv(hod__jlbk.args[1], arr_var.name + '#0'))
    require(accept_stride or len(hod__jlbk.args) == 2 or find_const(func_ir,
        hod__jlbk.args[2]) == 1)
    return True


def get_slice_step(typemap, func_ir, var):
    require(typemap[var.name] == types.slice3_type)
    nfpd__oqpa = get_definition(func_ir, var)
    require(isinstance(nfpd__oqpa, ir.Expr) and nfpd__oqpa.op == 'call')
    assert len(nfpd__oqpa.args) == 3
    return nfpd__oqpa.args[2]


def is_array_typ(var_typ, include_index_series=True):
    return is_np_array_typ(var_typ) or var_typ in (string_array_type, bodo.
        binary_array_type, bodo.dict_str_arr_type, bodo.hiframes.split_impl
        .string_array_split_view_type, bodo.hiframes.datetime_date_ext.
        datetime_date_array_type, bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type, boolean_array, bodo.libs.str_ext.
        random_access_string_array, bodo.libs.interval_arr_ext.
        IntervalArrayType) or isinstance(var_typ, (IntegerArrayType, bodo.
        libs.decimal_arr_ext.DecimalArrayType, bodo.hiframes.
        pd_categorical_ext.CategoricalArrayType, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType, bodo.libs.struct_arr_ext.
        StructArrayType, bodo.libs.interval_arr_ext.IntervalArrayType, bodo
        .libs.tuple_arr_ext.TupleArrayType, bodo.libs.map_arr_ext.
        MapArrayType, bodo.libs.csr_matrix_ext.CSRMatrixType, bodo.
        DatetimeArrayType)) or include_index_series and (isinstance(var_typ,
        (bodo.hiframes.pd_series_ext.SeriesType, bodo.hiframes.
        pd_multi_index_ext.MultiIndexType)) or bodo.hiframes.pd_index_ext.
        is_pd_index_type(var_typ))


def is_np_array_typ(var_typ):
    return isinstance(var_typ, types.Array)


def is_distributable_typ(var_typ):
    return is_array_typ(var_typ) or isinstance(var_typ, bodo.hiframes.table
        .TableType) or isinstance(var_typ, bodo.hiframes.pd_dataframe_ext.
        DataFrameType) or isinstance(var_typ, types.List
        ) and is_distributable_typ(var_typ.dtype) or isinstance(var_typ,
        types.DictType) and is_distributable_typ(var_typ.value_type)


def is_distributable_tuple_typ(var_typ):
    return isinstance(var_typ, types.BaseTuple) and any(
        is_distributable_typ(t) or is_distributable_tuple_typ(t) for t in
        var_typ.types) or isinstance(var_typ, types.List
        ) and is_distributable_tuple_typ(var_typ.dtype) or isinstance(var_typ,
        types.DictType) and is_distributable_tuple_typ(var_typ.value_type
        ) or isinstance(var_typ, types.iterators.EnumerateType) and (
        is_distributable_typ(var_typ.yield_type[1]) or
        is_distributable_tuple_typ(var_typ.yield_type[1]))


@numba.generated_jit(nopython=True, cache=True)
def build_set_seen_na(A):

    def impl(A):
        s = dict()
        ytqb__srxn = False
        for hkp__rmwtk in range(len(A)):
            if bodo.libs.array_kernels.isna(A, hkp__rmwtk):
                ytqb__srxn = True
                continue
            s[A[hkp__rmwtk]] = 0
        return s, ytqb__srxn
    return impl


def empty_like_type(n, arr):
    return np.empty(n, arr.dtype)


@overload(empty_like_type, no_unliteral=True)
def empty_like_type_overload(n, arr):
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return (lambda n, arr: bodo.hiframes.pd_categorical_ext.
            alloc_categorical_array(n, arr.dtype))
    if isinstance(arr, types.Array):
        return lambda n, arr: np.empty(n, arr.dtype)
    if isinstance(arr, types.List) and arr.dtype == string_type:

        def empty_like_type_str_list(n, arr):
            return [''] * n
        return empty_like_type_str_list
    if isinstance(arr, types.List) and arr.dtype == bytes_type:

        def empty_like_type_binary_list(n, arr):
            return [b''] * n
        return empty_like_type_binary_list
    if isinstance(arr, IntegerArrayType):
        guq__lhb = arr.dtype

        def empty_like_type_int_arr(n, arr):
            return bodo.libs.int_arr_ext.alloc_int_array(n, guq__lhb)
        return empty_like_type_int_arr
    if arr == boolean_array:

        def empty_like_type_bool_arr(n, arr):
            return bodo.libs.bool_arr_ext.alloc_bool_array(n)
        return empty_like_type_bool_arr
    if arr == bodo.hiframes.datetime_date_ext.datetime_date_array_type:

        def empty_like_type_datetime_date_arr(n, arr):
            return bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(n)
        return empty_like_type_datetime_date_arr
    if (arr == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type):

        def empty_like_type_datetime_timedelta_arr(n, arr):
            return (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(n))
        return empty_like_type_datetime_timedelta_arr
    if isinstance(arr, bodo.libs.decimal_arr_ext.DecimalArrayType):
        precision = arr.precision
        scale = arr.scale

        def empty_like_type_decimal_arr(n, arr):
            return bodo.libs.decimal_arr_ext.alloc_decimal_array(n,
                precision, scale)
        return empty_like_type_decimal_arr
    assert arr == string_array_type

    def empty_like_type_str_arr(n, arr):
        pgcty__netda = 20
        if len(arr) != 0:
            pgcty__netda = num_total_chars(arr) // len(arr)
        return pre_alloc_string_array(n, n * pgcty__netda)
    return empty_like_type_str_arr


def _empty_nd_impl(context, builder, arrtype, shapes):
    bwj__dmiz = make_array(arrtype)
    zhyld__muwg = bwj__dmiz(context, builder)
    jikbu__cyuv = context.get_data_type(arrtype.dtype)
    fxu__dcct = context.get_constant(types.intp, get_itemsize(context, arrtype)
        )
    jrb__vpjjn = context.get_constant(types.intp, 1)
    pusrj__jvfmo = lir.Constant(lir.IntType(1), 0)
    for s in shapes:
        hlh__gvp = builder.smul_with_overflow(jrb__vpjjn, s)
        jrb__vpjjn = builder.extract_value(hlh__gvp, 0)
        pusrj__jvfmo = builder.or_(pusrj__jvfmo, builder.extract_value(
            hlh__gvp, 1))
    if arrtype.ndim == 0:
        jib__prh = ()
    elif arrtype.layout == 'C':
        jib__prh = [fxu__dcct]
        for ropy__mwwgi in reversed(shapes[1:]):
            jib__prh.append(builder.mul(jib__prh[-1], ropy__mwwgi))
        jib__prh = tuple(reversed(jib__prh))
    elif arrtype.layout == 'F':
        jib__prh = [fxu__dcct]
        for ropy__mwwgi in shapes[:-1]:
            jib__prh.append(builder.mul(jib__prh[-1], ropy__mwwgi))
        jib__prh = tuple(jib__prh)
    else:
        raise NotImplementedError(
            "Don't know how to allocate array with layout '{0}'.".format(
            arrtype.layout))
    wnyu__jmj = builder.smul_with_overflow(jrb__vpjjn, fxu__dcct)
    izf__aom = builder.extract_value(wnyu__jmj, 0)
    pusrj__jvfmo = builder.or_(pusrj__jvfmo, builder.extract_value(
        wnyu__jmj, 1))
    with builder.if_then(pusrj__jvfmo, likely=False):
        cgutils.printf(builder,
            'array is too big; `arr.size * arr.dtype.itemsize` is larger than the maximum possible size.'
            )
    dtype = arrtype.dtype
    kji__zzgfc = context.get_preferred_array_alignment(dtype)
    fze__sirs = context.get_constant(types.uint32, kji__zzgfc)
    kkp__cvy = context.nrt.meminfo_alloc_aligned(builder, size=izf__aom,
        align=fze__sirs)
    data = context.nrt.meminfo_data(builder, kkp__cvy)
    aei__bny = context.get_value_type(types.intp)
    wgiyv__mqcqz = cgutils.pack_array(builder, shapes, ty=aei__bny)
    tlt__wjx = cgutils.pack_array(builder, jib__prh, ty=aei__bny)
    populate_array(zhyld__muwg, data=builder.bitcast(data, jikbu__cyuv.
        as_pointer()), shape=wgiyv__mqcqz, strides=tlt__wjx, itemsize=
        fxu__dcct, meminfo=kkp__cvy)
    return zhyld__muwg


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.np.arrayobj._empty_nd_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b6a998927680caa35917a553c79704e9d813d8f1873d83a5f8513837c159fa29':
        warnings.warn('numba.np.arrayobj._empty_nd_impl has changed')


def alloc_arr_tup(n, arr_tup, init_vals=()):
    geapp__vjgj = []
    for gnnq__drx in arr_tup:
        geapp__vjgj.append(np.empty(n, gnnq__drx.dtype))
    return tuple(geapp__vjgj)


@overload(alloc_arr_tup, no_unliteral=True)
def alloc_arr_tup_overload(n, data, init_vals=()):
    ykaid__tido = data.count
    dry__jxgjc = ','.join(['empty_like_type(n, data[{}])'.format(hkp__rmwtk
        ) for hkp__rmwtk in range(ykaid__tido)])
    if init_vals != ():
        dry__jxgjc = ','.join(['np.full(n, init_vals[{}], data[{}].dtype)'.
            format(hkp__rmwtk, hkp__rmwtk) for hkp__rmwtk in range(
            ykaid__tido)])
    jnrb__ulpu = 'def f(n, data, init_vals=()):\n'
    jnrb__ulpu += '  return ({}{})\n'.format(dry__jxgjc, ',' if ykaid__tido ==
        1 else '')
    nput__tnuo = {}
    exec(jnrb__ulpu, {'empty_like_type': empty_like_type, 'np': np}, nput__tnuo
        )
    ifok__egsr = nput__tnuo['f']
    return ifok__egsr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_to_scalar(n):
    if isinstance(n, types.BaseTuple) and len(n.types) == 1:
        return lambda n: n[0]
    return lambda n: n


def create_categorical_type(categories, data, is_ordered):
    if data == bodo.string_array_type or bodo.utils.typing.is_dtype_nullable(
        data):
        new_cats_arr = pd.CategoricalDtype(pd.array(categories), is_ordered
            ).categories.array
    else:
        new_cats_arr = pd.CategoricalDtype(categories, is_ordered
            ).categories.values
    return new_cats_arr


def alloc_type(n, t, s=None):
    return np.empty(n, t.dtype)


@overload(alloc_type)
def overload_alloc_type(n, t, s=None):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(typ,
        'bodo.alloc_type()')
    if is_str_arr_type(typ):
        return (lambda n, t, s=None: bodo.libs.str_arr_ext.
            pre_alloc_string_array(n, s[0]))
    if typ == bodo.binary_array_type:
        return (lambda n, t, s=None: bodo.libs.binary_arr_ext.
            pre_alloc_binary_array(n, s[0]))
    if isinstance(typ, bodo.libs.array_item_arr_ext.ArrayItemArrayType):
        dtype = typ.dtype
        return (lambda n, t, s=None: bodo.libs.array_item_arr_ext.
            pre_alloc_array_item_array(n, s, dtype))
    if isinstance(typ, bodo.libs.struct_arr_ext.StructArrayType):
        dtypes = typ.data
        names = typ.names
        return (lambda n, t, s=None: bodo.libs.struct_arr_ext.
            pre_alloc_struct_array(n, s, dtypes, names))
    if isinstance(typ, bodo.libs.map_arr_ext.MapArrayType):
        struct_typ = bodo.libs.struct_arr_ext.StructArrayType((typ.
            key_arr_type, typ.value_arr_type), ('key', 'value'))
        return lambda n, t, s=None: bodo.libs.map_arr_ext.pre_alloc_map_array(n
            , s, struct_typ)
    if isinstance(typ, bodo.libs.tuple_arr_ext.TupleArrayType):
        dtypes = typ.data
        return (lambda n, t, s=None: bodo.libs.tuple_arr_ext.
            pre_alloc_tuple_array(n, s, dtypes))
    if isinstance(typ, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        if isinstance(t, types.TypeRef):
            if typ.dtype.categories is None:
                raise BodoError(
                    'UDFs or Groupbys that return Categorical values must have categories known at compile time.'
                    )
            is_ordered = typ.dtype.ordered
            int_type = typ.dtype.int_type
            new_cats_arr = create_categorical_type(typ.dtype.categories,
                typ.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(new_cats_arr))
            return (lambda n, t, s=None: bodo.hiframes.pd_categorical_ext.
                alloc_categorical_array(n, bodo.hiframes.pd_categorical_ext
                .init_cat_dtype(bodo.utils.conversion.index_from_array(
                new_cats_arr), is_ordered, int_type, new_cats_tup)))
        else:
            return (lambda n, t, s=None: bodo.hiframes.pd_categorical_ext.
                alloc_categorical_array(n, t.dtype))
    if typ.dtype == bodo.hiframes.datetime_date_ext.datetime_date_type:
        return (lambda n, t, s=None: bodo.hiframes.datetime_date_ext.
            alloc_datetime_date_array(n))
    if (typ.dtype == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_type):
        return (lambda n, t, s=None: bodo.hiframes.datetime_timedelta_ext.
            alloc_datetime_timedelta_array(n))
    if isinstance(typ, DecimalArrayType):
        precision = typ.dtype.precision
        scale = typ.dtype.scale
        return (lambda n, t, s=None: bodo.libs.decimal_arr_ext.
            alloc_decimal_array(n, precision, scale))
    dtype = numba.np.numpy_support.as_dtype(typ.dtype)
    if isinstance(typ, IntegerArrayType):
        return lambda n, t, s=None: bodo.libs.int_arr_ext.alloc_int_array(n,
            dtype)
    if typ == boolean_array:
        return lambda n, t, s=None: bodo.libs.bool_arr_ext.alloc_bool_array(n)
    return lambda n, t, s=None: np.empty(n, dtype)


def astype(A, t):
    return A.astype(t.dtype)


@overload(astype, no_unliteral=True)
def overload_astype(A, t):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    dtype = typ.dtype
    if A == typ:
        return lambda A, t: A
    if isinstance(A, (types.Array, IntegerArrayType)) and isinstance(typ,
        types.Array):
        return lambda A, t: A.astype(dtype)
    if isinstance(typ, IntegerArrayType):
        return lambda A, t: bodo.libs.int_arr_ext.init_integer_array(A.
            astype(dtype), np.full(len(A) + 7 >> 3, 255, np.uint8))
    if (A == bodo.libs.dict_arr_ext.dict_str_arr_type and typ == bodo.
        string_array_type):
        return lambda A, t: bodo.utils.typing.decode_if_dict_array(A)
    raise BodoError(f'cannot convert array type {A} to {typ}')


def full_type(n, val, t):
    return np.full(n, val, t.dtype)


@overload(full_type, no_unliteral=True)
def overload_full_type(n, val, t):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    if isinstance(typ, types.Array):
        dtype = numba.np.numpy_support.as_dtype(typ.dtype)
        return lambda n, val, t: np.full(n, val, dtype)
    if isinstance(typ, IntegerArrayType):
        dtype = numba.np.numpy_support.as_dtype(typ.dtype)
        return lambda n, val, t: bodo.libs.int_arr_ext.init_integer_array(np
            .full(n, val, dtype), np.full(tuple_to_scalar(n) + 7 >> 3, 255,
            np.uint8))
    if typ == boolean_array:
        return lambda n, val, t: bodo.libs.bool_arr_ext.init_bool_array(np.
            full(n, val, np.bool_), np.full(tuple_to_scalar(n) + 7 >> 3, 
            255, np.uint8))
    if typ == string_array_type:

        def impl_str(n, val, t):
            jzsv__bdcu = n * bodo.libs.str_arr_ext.get_utf8_size(val)
            A = pre_alloc_string_array(n, jzsv__bdcu)
            for hkp__rmwtk in range(n):
                A[hkp__rmwtk] = val
            return A
        return impl_str

    def impl(n, val, t):
        A = alloc_type(n, typ, (-1,))
        for hkp__rmwtk in range(n):
            A[hkp__rmwtk] = val
        return A
    return impl


@intrinsic
def is_null_pointer(typingctx, ptr_typ=None):

    def codegen(context, builder, signature, args):
        jswa__rfn, = args
        sqh__qnbm = context.get_constant_null(ptr_typ)
        return builder.icmp_unsigned('==', jswa__rfn, sqh__qnbm)
    return types.bool_(ptr_typ), codegen


@intrinsic
def is_null_value(typingctx, val_typ=None):

    def codegen(context, builder, signature, args):
        val, = args
        zseh__gbhca = cgutils.alloca_once_value(builder, val)
        new__uycjk = cgutils.alloca_once_value(builder, context.
            get_constant_null(val_typ))
        return is_ll_eq(builder, zseh__gbhca, new__uycjk)
    return types.bool_(val_typ), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_list_to_array(A, data, elem_type):
    elem_type = elem_type.instance_type if isinstance(elem_type, types.TypeRef
        ) else elem_type
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'tuple_list_to_array()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(elem_type,
        'tuple_list_to_array()')
    jnrb__ulpu = 'def impl(A, data, elem_type):\n'
    jnrb__ulpu += '  for i, d in enumerate(data):\n'
    if elem_type == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        jnrb__ulpu += (
            '    A[i] = bodo.utils.conversion.unbox_if_timestamp(d)\n')
    else:
        jnrb__ulpu += '    A[i] = d\n'
    nput__tnuo = {}
    exec(jnrb__ulpu, {'bodo': bodo}, nput__tnuo)
    impl = nput__tnuo['impl']
    return impl


def object_length(c, obj):
    wol__tnpy = c.context.get_argument_type(types.pyobject)
    cnvm__jqqm = lir.FunctionType(lir.IntType(64), [wol__tnpy])
    rhho__mxzv = cgutils.get_or_insert_function(c.builder.module,
        cnvm__jqqm, name='PyObject_Length')
    return c.builder.call(rhho__mxzv, (obj,))


@intrinsic
def incref(typingctx, data=None):

    def codegen(context, builder, signature, args):
        dzv__lzsh, = args
        context.nrt.incref(builder, signature.args[0], dzv__lzsh)
    return types.void(data), codegen


def gen_getitem(out_var, in_var, ind, calltypes, nodes):
    xienb__lymp = out_var.loc
    drm__vzsg = ir.Expr.static_getitem(in_var, ind, None, xienb__lymp)
    calltypes[drm__vzsg] = None
    nodes.append(ir.Assign(drm__vzsg, out_var, xienb__lymp))


def is_static_getsetitem(node):
    return is_expr(node, 'static_getitem') or isinstance(node, ir.StaticSetItem
        )


def get_getsetitem_index_var(node, typemap, nodes):
    index_var = node.index_var if is_static_getsetitem(node) else node.index
    if index_var is None:
        assert is_static_getsetitem(node)
        try:
            zro__tofr = types.literal(node.index)
        except:
            zro__tofr = numba.typeof(node.index)
        index_var = ir.Var(node.value.scope, ir_utils.mk_unique_var(
            'dummy_index'), node.loc)
        typemap[index_var.name] = zro__tofr
        nodes.append(ir.Assign(ir.Const(node.index, node.loc), index_var,
            node.loc))
    return index_var


import copy
ir.Const.__deepcopy__ = lambda self, memo: ir.Const(self.value, copy.
    deepcopy(self.loc))


def is_call_assign(stmt):
    return isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
        ) and stmt.value.op == 'call'


def is_call(expr):
    return isinstance(expr, ir.Expr) and expr.op == 'call'


def is_var_assign(inst):
    return isinstance(inst, ir.Assign) and isinstance(inst.value, ir.Var)


def is_assign(inst):
    return isinstance(inst, ir.Assign)


def is_expr(val, op):
    return isinstance(val, ir.Expr) and val.op == op


def sanitize_varname(varname):
    if isinstance(varname, (tuple, list)):
        varname = '_'.join(sanitize_varname(v) for v in varname)
    varname = str(varname)
    mltp__zzdj = re.sub('\\W+', '_', varname)
    if not mltp__zzdj or not mltp__zzdj[0].isalpha():
        mltp__zzdj = '_' + mltp__zzdj
    if not mltp__zzdj.isidentifier() or keyword.iskeyword(mltp__zzdj):
        mltp__zzdj = mk_unique_var('new_name').replace('.', '_')
    return mltp__zzdj


def dump_node_list(node_list):
    for n in node_list:
        print('   ', n)


def debug_prints():
    return numba.core.config.DEBUG_ARRAY_OPT == 1


@overload(reversed)
def list_reverse(A):
    if isinstance(A, types.List):

        def impl_reversed(A):
            ystd__lczx = len(A)
            for hkp__rmwtk in range(ystd__lczx):
                yield A[ystd__lczx - 1 - hkp__rmwtk]
        return impl_reversed


@numba.njit
def count_nonnan(a):
    return np.count_nonzero(~np.isnan(a))


@numba.njit
def nanvar_ddof1(a):
    syioe__bveus = count_nonnan(a)
    if syioe__bveus <= 1:
        return np.nan
    return np.nanvar(a) * (syioe__bveus / (syioe__bveus - 1))


@numba.njit
def nanstd_ddof1(a):
    return np.sqrt(nanvar_ddof1(a))


def has_supported_h5py():
    try:
        import h5py
        from bodo.io import _hdf5
    except ImportError as xfuvv__rsw:
        pgkq__qxywv = False
    else:
        pgkq__qxywv = h5py.version.hdf5_version_tuple[1] in (10, 12)
    return pgkq__qxywv


def check_h5py():
    if not has_supported_h5py():
        raise BodoError("install 'h5py' package to enable hdf5 support")


def has_pyarrow():
    try:
        import pyarrow
    except ImportError as xfuvv__rsw:
        jqu__wlua = False
    else:
        jqu__wlua = True
    return jqu__wlua


def has_scipy():
    try:
        import scipy
    except ImportError as xfuvv__rsw:
        cdi__jra = False
    else:
        cdi__jra = True
    return cdi__jra


@intrinsic
def check_and_propagate_cpp_exception(typingctx):

    def codegen(context, builder, sig, args):
        fbzvg__jesg = context.get_python_api(builder)
        ykcwb__jdj = fbzvg__jesg.err_occurred()
        tnnm__vldk = cgutils.is_not_null(builder, ykcwb__jdj)
        with builder.if_then(tnnm__vldk):
            builder.ret(numba.core.callconv.RETCODE_EXC)
    return types.void(), codegen


def inlined_check_and_propagate_cpp_exception(context, builder):
    fbzvg__jesg = context.get_python_api(builder)
    ykcwb__jdj = fbzvg__jesg.err_occurred()
    tnnm__vldk = cgutils.is_not_null(builder, ykcwb__jdj)
    with builder.if_then(tnnm__vldk):
        builder.ret(numba.core.callconv.RETCODE_EXC)


@numba.njit
def check_java_installation(fname):
    with numba.objmode():
        check_java_installation_(fname)


def check_java_installation_(fname):
    if not fname.startswith('hdfs://'):
        return
    import shutil
    if not shutil.which('java'):
        yvrq__wuuhw = (
            "Java not found. Make sure openjdk is installed for hdfs. openjdk can be installed by calling 'conda install 'openjdk>=9.0' -c conda-forge'."
            )
        raise BodoError(yvrq__wuuhw)


dt_err = """
        If you are trying to set NULL values for timedelta64 in regular Python, 

        consider using np.timedelta64('nat') instead of None
        """


@lower_constant(types.List)
def lower_constant_list(context, builder, typ, pyval):
    if len(pyval) > CONST_LIST_SLOW_WARN_THRESHOLD:
        warnings.warn(BodoWarning(
            'Using large global lists can result in long compilation times. Please pass large lists as arguments to JIT functions or use arrays.'
            ))
    lvhmn__axel = []
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in list must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
        lvhmn__axel.append(context.get_constant_generic(builder, typ.dtype, a))
    rud__bkvzt = context.get_constant_generic(builder, types.int64, len(pyval))
    kkzje__mzp = context.get_constant_generic(builder, types.bool_, False)
    okf__tfz = context.get_constant_null(types.pyobject)
    eysyk__buhx = lir.Constant.literal_struct([rud__bkvzt, rud__bkvzt,
        kkzje__mzp] + lvhmn__axel)
    eysyk__buhx = cgutils.global_constant(builder, '.const.payload',
        eysyk__buhx).bitcast(cgutils.voidptr_t)
    zstkx__rsdgz = context.get_constant(types.int64, -1)
    wiub__hkhmz = context.get_constant_null(types.voidptr)
    kkp__cvy = lir.Constant.literal_struct([zstkx__rsdgz, wiub__hkhmz,
        wiub__hkhmz, eysyk__buhx, zstkx__rsdgz])
    kkp__cvy = cgutils.global_constant(builder, '.const.meminfo', kkp__cvy
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([kkp__cvy, okf__tfz])


@lower_constant(types.Set)
def lower_constant_set(context, builder, typ, pyval):
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in set must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
    ywwxd__gmac = types.List(typ.dtype)
    uwhse__ycra = context.get_constant_generic(builder, ywwxd__gmac, list(
        pyval))
    thck__cxcez = context.compile_internal(builder, lambda l: set(l), types
        .Set(typ.dtype)(ywwxd__gmac), [uwhse__ycra])
    return thck__cxcez


def lower_const_dict_fast_path(context, builder, typ, pyval):
    from bodo.utils.typing import can_replace
    amfv__zlnz = pd.Series(pyval.keys()).values
    ymu__tul = pd.Series(pyval.values()).values
    kez__lolen = bodo.typeof(amfv__zlnz)
    clw__cxxbl = bodo.typeof(ymu__tul)
    require(kez__lolen.dtype == typ.key_type or can_replace(typ.key_type,
        kez__lolen.dtype))
    require(clw__cxxbl.dtype == typ.value_type or can_replace(typ.
        value_type, clw__cxxbl.dtype))
    kvjqa__ncbo = context.get_constant_generic(builder, kez__lolen, amfv__zlnz)
    oxe__fhl = context.get_constant_generic(builder, clw__cxxbl, ymu__tul)

    def create_dict(keys, vals):
        lep__fmrul = {}
        for k, v in zip(keys, vals):
            lep__fmrul[k] = v
        return lep__fmrul
    ttjuu__djpzj = context.compile_internal(builder, create_dict, typ(
        kez__lolen, clw__cxxbl), [kvjqa__ncbo, oxe__fhl])
    return ttjuu__djpzj


@lower_constant(types.DictType)
def lower_constant_dict(context, builder, typ, pyval):
    try:
        return lower_const_dict_fast_path(context, builder, typ, pyval)
    except:
        pass
    if len(pyval) > CONST_DICT_SLOW_WARN_THRESHOLD:
        warnings.warn(BodoWarning(
            'Using large global dictionaries can result in long compilation times. Please pass large dictionaries as arguments to JIT functions.'
            ))
    krexj__hsln = typ.key_type
    ccj__rssv = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(krexj__hsln, ccj__rssv)
    ttjuu__djpzj = context.compile_internal(builder, make_dict, typ(), [])

    def set_dict_val(d, k, v):
        d[k] = v
    for k, v in pyval.items():
        cwphx__vhmti = context.get_constant_generic(builder, krexj__hsln, k)
        cnekf__rpo = context.get_constant_generic(builder, ccj__rssv, v)
        context.compile_internal(builder, set_dict_val, types.none(typ,
            krexj__hsln, ccj__rssv), [ttjuu__djpzj, cwphx__vhmti, cnekf__rpo])
    return ttjuu__djpzj
