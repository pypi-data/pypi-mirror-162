"""
Utility functions for conversion of data such as list to array.
Need to be inlined for better optimization.
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.binary_arr_ext import bytes_type
from bodo.libs.bool_arr_ext import boolean_dtype
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.nullable_tuple_ext import NullableTupleType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_list, get_overload_const_str, is_heterogeneous_tuple_type, is_np_arr_typ, is_overload_constant_list, is_overload_constant_str, is_overload_none, is_overload_true, is_str_arr_type, to_nullable_type, unwrap_typeref
NS_DTYPE = np.dtype('M8[ns]')
TD_DTYPE = np.dtype('m8[ns]')


def coerce_to_ndarray(data, error_on_nonarray=True, use_nullable_array=None,
    scalar_to_arr_len=None):
    return data


@overload(coerce_to_ndarray)
def overload_coerce_to_ndarray(data, error_on_nonarray=True,
    use_nullable_array=None, scalar_to_arr_len=None):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, RangeIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    data = types.unliteral(data)
    if isinstance(data, types.Optional) and bodo.utils.typing.is_scalar_type(
        data.type):
        data = data.type
        use_nullable_array = True
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType
        ) and not is_overload_none(use_nullable_array):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.int_arr_ext.
            get_int_arr_data(data))
    if data == bodo.libs.bool_arr_ext.boolean_array and not is_overload_none(
        use_nullable_array):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.bool_arr_ext.
            get_bool_arr_data(data))
    if isinstance(data, types.Array):
        if not is_overload_none(use_nullable_array) and isinstance(data.
            dtype, (types.Boolean, types.Integer)):
            if data.dtype == types.bool_:
                if data.layout != 'C':
                    return (lambda data, error_on_nonarray=True,
                        use_nullable_array=None, scalar_to_arr_len=None:
                        bodo.libs.bool_arr_ext.init_bool_array(np.
                        ascontiguousarray(data), np.full(len(data) + 7 >> 3,
                        255, np.uint8)))
                else:
                    return (lambda data, error_on_nonarray=True,
                        use_nullable_array=None, scalar_to_arr_len=None:
                        bodo.libs.bool_arr_ext.init_bool_array(data, np.
                        full(len(data) + 7 >> 3, 255, np.uint8)))
            elif data.layout != 'C':
                return (lambda data, error_on_nonarray=True,
                    use_nullable_array=None, scalar_to_arr_len=None: bodo.
                    libs.int_arr_ext.init_integer_array(np.
                    ascontiguousarray(data), np.full(len(data) + 7 >> 3, 
                    255, np.uint8)))
            else:
                return (lambda data, error_on_nonarray=True,
                    use_nullable_array=None, scalar_to_arr_len=None: bodo.
                    libs.int_arr_ext.init_integer_array(data, np.full(len(
                    data) + 7 >> 3, 255, np.uint8)))
        if data.layout != 'C':
            return (lambda data, error_on_nonarray=True, use_nullable_array
                =None, scalar_to_arr_len=None: np.ascontiguousarray(data))
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if isinstance(data, (types.List, types.UniTuple)):
        surui__hre = data.dtype
        if isinstance(surui__hre, types.Optional):
            surui__hre = surui__hre.type
            if bodo.utils.typing.is_scalar_type(surui__hre):
                use_nullable_array = True
        if isinstance(surui__hre, (types.Boolean, types.Integer,
            Decimal128Type)) or surui__hre in [bodo.hiframes.
            pd_timestamp_ext.pd_timestamp_type, bodo.hiframes.
            datetime_date_ext.datetime_date_type, bodo.hiframes.
            datetime_timedelta_ext.datetime_timedelta_type]:
            tar__swjn = dtype_to_array_type(surui__hre)
            if not is_overload_none(use_nullable_array):
                tar__swjn = to_nullable_type(tar__swjn)

            def impl(data, error_on_nonarray=True, use_nullable_array=None,
                scalar_to_arr_len=None):
                nbh__aoxv = len(data)
                A = bodo.utils.utils.alloc_type(nbh__aoxv, tar__swjn, (-1,))
                bodo.utils.utils.tuple_list_to_array(A, data, surui__hre)
                return A
            return impl
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.asarray(data))
    if isinstance(data, SeriesType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_series_ext.
            get_series_data(data))
    if isinstance(data, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_index_ext.
            get_index_data(data))
    if isinstance(data, RangeIndexType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.arange(data._start, data._stop,
            data._step))
    if isinstance(data, types.RangeType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.arange(data.start, data.stop,
            data.step))
    if not is_overload_none(scalar_to_arr_len):
        if isinstance(data, Decimal128Type):
            hkj__qchw = data.precision
            lwn__can = data.scale

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                nbh__aoxv = scalar_to_arr_len
                A = bodo.libs.decimal_arr_ext.alloc_decimal_array(nbh__aoxv,
                    hkj__qchw, lwn__can)
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    A[dwb__ylc] = data
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
            neait__bcrw = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                nbh__aoxv = scalar_to_arr_len
                A = np.empty(nbh__aoxv, neait__bcrw)
                jyzyj__tdco = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(data))
                shnr__ngvi = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    jyzyj__tdco)
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    A[dwb__ylc] = shnr__ngvi
                return A
            return impl_ts
        if (data == bodo.hiframes.datetime_timedelta_ext.
            datetime_timedelta_type):
            gjy__leya = np.dtype('timedelta64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                nbh__aoxv = scalar_to_arr_len
                A = np.empty(nbh__aoxv, gjy__leya)
                sarz__mkix = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(data))
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    A[dwb__ylc] = sarz__mkix
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_date_ext.datetime_date_type:

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                nbh__aoxv = scalar_to_arr_len
                A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                    nbh__aoxv)
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    A[dwb__ylc] = data
                return A
            return impl_ts
        if data == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            neait__bcrw = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                nbh__aoxv = scalar_to_arr_len
                A = np.empty(scalar_to_arr_len, neait__bcrw)
                jyzyj__tdco = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    data.value)
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    A[dwb__ylc] = jyzyj__tdco
                return A
            return impl_ts
        dtype = types.unliteral(data)
        if not is_overload_none(use_nullable_array) and isinstance(dtype,
            types.Integer):

            def impl_null_integer(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                nbh__aoxv = scalar_to_arr_len
                dmz__krpg = bodo.libs.int_arr_ext.alloc_int_array(nbh__aoxv,
                    dtype)
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    dmz__krpg[dwb__ylc] = data
                return dmz__krpg
            return impl_null_integer
        if not is_overload_none(use_nullable_array) and dtype == types.bool_:

            def impl_null_bool(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                nbh__aoxv = scalar_to_arr_len
                dmz__krpg = bodo.libs.bool_arr_ext.alloc_bool_array(nbh__aoxv)
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    dmz__krpg[dwb__ylc] = data
                return dmz__krpg
            return impl_null_bool

        def impl_num(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            numba.parfors.parfor.init_prange()
            nbh__aoxv = scalar_to_arr_len
            dmz__krpg = np.empty(nbh__aoxv, dtype)
            for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv):
                dmz__krpg[dwb__ylc] = data
            return dmz__krpg
        return impl_num
    if isinstance(data, types.BaseTuple) and all(isinstance(jibop__pyx, (
        types.Float, types.Integer)) for jibop__pyx in data.types):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.array(data))
    if bodo.utils.utils.is_array_typ(data, False):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if is_overload_true(error_on_nonarray):
        raise BodoError(f'cannot coerce {data} to array')
    return (lambda data, error_on_nonarray=True, use_nullable_array=None,
        scalar_to_arr_len=None: data)


def coerce_scalar_to_array(scalar, length, arr_type):
    pass


@overload(coerce_scalar_to_array)
def overload_coerce_scalar_to_array(scalar, length, arr_type):
    fhd__uho = to_nullable_type(unwrap_typeref(arr_type))
    if scalar == types.none:

        def impl(scalar, length, arr_type):
            return bodo.libs.array_kernels.gen_na_array(length, fhd__uho, True)
    elif isinstance(scalar, types.Optional):

        def impl(scalar, length, arr_type):
            if scalar is None:
                return bodo.libs.array_kernels.gen_na_array(length,
                    fhd__uho, True)
            else:
                return bodo.utils.conversion.coerce_to_array(bodo.utils.
                    indexing.unoptional(scalar), True, True, length)
    else:

        def impl(scalar, length, arr_type):
            return bodo.utils.conversion.coerce_to_array(scalar, True, None,
                length)
    return impl


def coerce_to_array(data, error_on_nonarray=True, use_nullable_array=None,
    scalar_to_arr_len=None):
    return data


@overload(coerce_to_array, no_unliteral=True)
def overload_coerce_to_array(data, error_on_nonarray=True,
    use_nullable_array=None, scalar_to_arr_len=None):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, StringIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    data = types.unliteral(data)
    if isinstance(data, types.Optional) and bodo.utils.typing.is_scalar_type(
        data.type):
        data = data.type
        use_nullable_array = True
    if isinstance(data, SeriesType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_series_ext.
            get_series_data(data))
    if isinstance(data, (StringIndexType, BinaryIndexType,
        CategoricalIndexType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_index_ext.
            get_index_data(data))
    if isinstance(data, types.List) and data.dtype in (bodo.string_type,
        bodo.bytes_type):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            str_arr_from_sequence(data))
    if isinstance(data, types.BaseTuple) and data.count == 0:
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            empty_str_arr(data))
    if isinstance(data, types.UniTuple) and isinstance(data.dtype, (types.
        UnicodeType, types.StringLiteral)) or isinstance(data, types.BaseTuple
        ) and all(isinstance(jibop__pyx, types.StringLiteral) for
        jibop__pyx in data.types):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            str_arr_from_sequence(data))
    if data in (bodo.string_array_type, bodo.dict_str_arr_type, bodo.
        binary_array_type, bodo.libs.bool_arr_ext.boolean_array, bodo.
        hiframes.datetime_date_ext.datetime_date_array_type, bodo.hiframes.
        datetime_timedelta_ext.datetime_timedelta_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type) or isinstance(data, (bodo
        .libs.int_arr_ext.IntegerArrayType, DecimalArrayType, bodo.libs.
        interval_arr_ext.IntervalArrayType, bodo.libs.tuple_arr_ext.
        TupleArrayType, bodo.libs.struct_arr_ext.StructArrayType, bodo.
        hiframes.pd_categorical_ext.CategoricalArrayType, bodo.libs.
        csr_matrix_ext.CSRMatrixType, bodo.DatetimeArrayType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if isinstance(data, (types.List, types.UniTuple)) and isinstance(data.
        dtype, types.BaseTuple):
        pidkv__gki = tuple(dtype_to_array_type(jibop__pyx) for jibop__pyx in
            data.dtype.types)

        def impl_tuple_list(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            nbh__aoxv = len(data)
            arr = bodo.libs.tuple_arr_ext.pre_alloc_tuple_array(nbh__aoxv,
                (-1,), pidkv__gki)
            for dwb__ylc in range(nbh__aoxv):
                arr[dwb__ylc] = data[dwb__ylc]
            return arr
        return impl_tuple_list
    if isinstance(data, types.List) and (bodo.utils.utils.is_array_typ(data
        .dtype, False) or isinstance(data.dtype, types.List)):
        jifry__nuy = dtype_to_array_type(data.dtype.dtype)

        def impl_array_item_arr(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            nbh__aoxv = len(data)
            vdit__qsr = init_nested_counts(jifry__nuy)
            for dwb__ylc in range(nbh__aoxv):
                kuhw__mnv = bodo.utils.conversion.coerce_to_array(data[
                    dwb__ylc], use_nullable_array=True)
                vdit__qsr = add_nested_counts(vdit__qsr, kuhw__mnv)
            dmz__krpg = (bodo.libs.array_item_arr_ext.
                pre_alloc_array_item_array(nbh__aoxv, vdit__qsr, jifry__nuy))
            ituf__wnn = bodo.libs.array_item_arr_ext.get_null_bitmap(dmz__krpg)
            for gyhw__gvh in range(nbh__aoxv):
                kuhw__mnv = bodo.utils.conversion.coerce_to_array(data[
                    gyhw__gvh], use_nullable_array=True)
                dmz__krpg[gyhw__gvh] = kuhw__mnv
                bodo.libs.int_arr_ext.set_bit_to_arr(ituf__wnn, gyhw__gvh, 1)
            return dmz__krpg
        return impl_array_item_arr
    if not is_overload_none(scalar_to_arr_len) and isinstance(data, (types.
        UnicodeType, types.StringLiteral)):

        def impl_str(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            nbh__aoxv = scalar_to_arr_len
            lowa__rkj = bodo.libs.str_arr_ext.str_arr_from_sequence([data])
            imc__vyil = bodo.libs.int_arr_ext.alloc_int_array(nbh__aoxv, np
                .int32)
            numba.parfors.parfor.init_prange()
            for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv):
                imc__vyil[dwb__ylc] = 0
            A = bodo.libs.dict_arr_ext.init_dict_arr(lowa__rkj, imc__vyil, True
                )
            return A
        return impl_str
    if isinstance(data, types.List) and isinstance(data.dtype, bodo.
        hiframes.pd_timestamp_ext.PandasTimestampType):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
            'coerce_to_array()')

        def impl_list_timestamp(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            nbh__aoxv = len(data)
            A = np.empty(nbh__aoxv, np.dtype('datetime64[ns]'))
            for dwb__ylc in range(nbh__aoxv):
                A[dwb__ylc] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    data[dwb__ylc].value)
            return A
        return impl_list_timestamp
    if isinstance(data, types.List) and data.dtype == bodo.pd_timedelta_type:

        def impl_list_timedelta(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            nbh__aoxv = len(data)
            A = np.empty(nbh__aoxv, np.dtype('timedelta64[ns]'))
            for dwb__ylc in range(nbh__aoxv):
                A[dwb__ylc
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    data[dwb__ylc].value)
            return A
        return impl_list_timedelta
    if isinstance(data, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
            'coerce_to_array()')
    if not is_overload_none(scalar_to_arr_len) and data in [bodo.
        pd_timestamp_type, bodo.pd_timedelta_type]:
        otq__wdhs = ('datetime64[ns]' if data == bodo.pd_timestamp_type else
            'timedelta64[ns]')

        def impl_timestamp(data, error_on_nonarray=True, use_nullable_array
            =None, scalar_to_arr_len=None):
            nbh__aoxv = scalar_to_arr_len
            A = np.empty(nbh__aoxv, otq__wdhs)
            data = bodo.utils.conversion.unbox_if_timestamp(data)
            for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv):
                A[dwb__ylc] = data
            return A
        return impl_timestamp
    return (lambda data, error_on_nonarray=True, use_nullable_array=None,
        scalar_to_arr_len=None: bodo.utils.conversion.coerce_to_ndarray(
        data, error_on_nonarray, use_nullable_array, scalar_to_arr_len))


def _is_str_dtype(dtype):
    return isinstance(dtype, bodo.libs.str_arr_ext.StringDtype) or isinstance(
        dtype, types.Function) and dtype.key[0
        ] == str or is_overload_constant_str(dtype) and get_overload_const_str(
        dtype) == 'str' or isinstance(dtype, types.TypeRef
        ) and dtype.instance_type == types.unicode_type


def fix_arr_dtype(data, new_dtype, copy=None, nan_to_str=True, from_series=
    False):
    return data


@overload(fix_arr_dtype, no_unliteral=True)
def overload_fix_arr_dtype(data, new_dtype, copy=None, nan_to_str=True,
    from_series=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'fix_arr_dtype()')
    bgkny__lvnyz = is_overload_true(copy)
    rbws__egt = is_overload_constant_str(new_dtype) and get_overload_const_str(
        new_dtype) == 'object'
    if is_overload_none(new_dtype) or rbws__egt:
        if bgkny__lvnyz:
            return (lambda data, new_dtype, copy=None, nan_to_str=True,
                from_series=False: data.copy())
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(data, NullableTupleType):
        nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
        if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
            nb_dtype = nb_dtype.dtype
        vff__cieoc = {types.unicode_type: '', boolean_dtype: False, types.
            bool_: False, types.int8: np.int8(0), types.int16: np.int16(0),
            types.int32: np.int32(0), types.int64: np.int64(0), types.uint8:
            np.uint8(0), types.uint16: np.uint16(0), types.uint32: np.
            uint32(0), types.uint64: np.uint64(0), types.float32: np.
            float32(0), types.float64: np.float64(0), bodo.datetime64ns: pd
            .Timestamp(0), bodo.timedelta64ns: pd.Timedelta(0)}
        xkzzc__arz = {types.unicode_type: str, types.bool_: bool,
            boolean_dtype: bool, types.int8: np.int8, types.int16: np.int16,
            types.int32: np.int32, types.int64: np.int64, types.uint8: np.
            uint8, types.uint16: np.uint16, types.uint32: np.uint32, types.
            uint64: np.uint64, types.float32: np.float32, types.float64: np
            .float64, bodo.datetime64ns: pd.to_datetime, bodo.timedelta64ns:
            pd.to_timedelta}
        ryppf__enc = vff__cieoc.keys()
        iecm__pvii = list(data._tuple_typ.types)
        if nb_dtype not in ryppf__enc:
            raise BodoError(f'type conversion to {nb_dtype} types unsupported.'
                )
        for dvfrn__kuxaw in iecm__pvii:
            if dvfrn__kuxaw == bodo.datetime64ns:
                if nb_dtype not in (types.unicode_type, types.int64, types.
                    uint64, bodo.datetime64ns):
                    raise BodoError(
                        f'invalid type conversion from {dvfrn__kuxaw} to {nb_dtype}.'
                        )
            elif dvfrn__kuxaw == bodo.timedelta64ns:
                if nb_dtype not in (types.unicode_type, types.int64, types.
                    uint64, bodo.timedelta64ns):
                    raise BodoError(
                        f'invalid type conversion from {dvfrn__kuxaw} to {nb_dtype}.'
                        )
        mpu__out = (
            'def impl(data, new_dtype, copy=None, nan_to_str=True, from_series=False):\n'
            )
        mpu__out += '  data_tup = data._data\n'
        mpu__out += '  null_tup = data._null_values\n'
        for dwb__ylc in range(len(iecm__pvii)):
            mpu__out += f'  val_{dwb__ylc} = convert_func(default_value)\n'
            mpu__out += f'  if not null_tup[{dwb__ylc}]:\n'
            mpu__out += (
                f'    val_{dwb__ylc} = convert_func(data_tup[{dwb__ylc}])\n')
        owzq__juro = ', '.join(f'val_{dwb__ylc}' for dwb__ylc in range(len(
            iecm__pvii)))
        mpu__out += f'  vals_tup = ({owzq__juro},)\n'
        mpu__out += """  res_tup = bodo.libs.nullable_tuple_ext.build_nullable_tuple(vals_tup, null_tup)
"""
        mpu__out += '  return res_tup\n'
        xiqa__xjvn = {}
        ksri__wxvde = xkzzc__arz[nb_dtype]
        pnewj__fzp = vff__cieoc[nb_dtype]
        exec(mpu__out, {'bodo': bodo, 'np': np, 'pd': pd, 'default_value':
            pnewj__fzp, 'convert_func': ksri__wxvde}, xiqa__xjvn)
        impl = xiqa__xjvn['impl']
        return impl
    if _is_str_dtype(new_dtype):
        if isinstance(data.dtype, types.Integer):

            def impl_int_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                nbh__aoxv = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(nbh__aoxv, -1)
                for rppa__ypv in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    if bodo.libs.array_kernels.isna(data, rppa__ypv):
                        if nan_to_str:
                            bodo.libs.str_arr_ext.str_arr_setitem_NA_str(A,
                                rppa__ypv)
                        else:
                            bodo.libs.array_kernels.setna(A, rppa__ypv)
                    else:
                        bodo.libs.str_arr_ext.str_arr_setitem_int_to_str(A,
                            rppa__ypv, data[rppa__ypv])
                return A
            return impl_int_str
        if data.dtype == bytes_type:

            def impl_binary(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                nbh__aoxv = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(nbh__aoxv, -1)
                for rppa__ypv in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    if bodo.libs.array_kernels.isna(data, rppa__ypv):
                        bodo.libs.array_kernels.setna(A, rppa__ypv)
                    else:
                        A[rppa__ypv] = ''.join([chr(stit__eyu) for
                            stit__eyu in data[rppa__ypv]])
                return A
            return impl_binary
        if is_overload_true(from_series) and data.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns):

            def impl_str_dt_series(data, new_dtype, copy=None, nan_to_str=
                True, from_series=False):
                numba.parfors.parfor.init_prange()
                nbh__aoxv = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(nbh__aoxv, -1)
                for rppa__ypv in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    if bodo.libs.array_kernels.isna(data, rppa__ypv):
                        if nan_to_str:
                            A[rppa__ypv] = 'NaT'
                        else:
                            bodo.libs.array_kernels.setna(A, rppa__ypv)
                        continue
                    A[rppa__ypv] = str(box_if_dt64(data[rppa__ypv]))
                return A
            return impl_str_dt_series
        else:

            def impl_str_array(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                nbh__aoxv = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(nbh__aoxv, -1)
                for rppa__ypv in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    if bodo.libs.array_kernels.isna(data, rppa__ypv):
                        if nan_to_str:
                            A[rppa__ypv] = 'nan'
                        else:
                            bodo.libs.array_kernels.setna(A, rppa__ypv)
                        continue
                    A[rppa__ypv] = str(data[rppa__ypv])
                return A
            return impl_str_array
    if isinstance(new_dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):

        def impl_cat_dtype(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            nbh__aoxv = len(data)
            numba.parfors.parfor.init_prange()
            zmbx__rina = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories(new_dtype.categories.values))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                nbh__aoxv, new_dtype)
            kjjki__mkh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv):
                if bodo.libs.array_kernels.isna(data, dwb__ylc):
                    bodo.libs.array_kernels.setna(A, dwb__ylc)
                    continue
                val = data[dwb__ylc]
                if val not in zmbx__rina:
                    bodo.libs.array_kernels.setna(A, dwb__ylc)
                    continue
                kjjki__mkh[dwb__ylc] = zmbx__rina[val]
            return A
        return impl_cat_dtype
    if is_overload_constant_str(new_dtype) and get_overload_const_str(new_dtype
        ) == 'category':

        def impl_category(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            lsl__vwf = bodo.libs.array_kernels.unique(data, dropna=True)
            lsl__vwf = pd.Series(lsl__vwf).sort_values().values
            lsl__vwf = bodo.allgatherv(lsl__vwf, False)
            fftj__vmke = bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo
                .utils.conversion.index_from_array(lsl__vwf, None), False,
                None, None)
            nbh__aoxv = len(data)
            numba.parfors.parfor.init_prange()
            zmbx__rina = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories_no_duplicates(lsl__vwf))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                nbh__aoxv, fftj__vmke)
            kjjki__mkh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv):
                if bodo.libs.array_kernels.isna(data, dwb__ylc):
                    bodo.libs.array_kernels.setna(A, dwb__ylc)
                    continue
                val = data[dwb__ylc]
                kjjki__mkh[dwb__ylc] = zmbx__rina[val]
            return A
        return impl_category
    nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType):
        vzq__ofuvq = isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype
            ) and data.dtype == nb_dtype.dtype
    else:
        vzq__ofuvq = data.dtype == nb_dtype
    if bgkny__lvnyz and vzq__ofuvq:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.copy())
    if vzq__ofuvq:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
        if isinstance(nb_dtype, types.Integer):
            otq__wdhs = nb_dtype
        else:
            otq__wdhs = nb_dtype.dtype
        if isinstance(data.dtype, types.Float):

            def impl_float(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                nbh__aoxv = len(data)
                numba.parfors.parfor.init_prange()
                cvs__ocw = bodo.libs.int_arr_ext.alloc_int_array(nbh__aoxv,
                    otq__wdhs)
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    if bodo.libs.array_kernels.isna(data, dwb__ylc):
                        bodo.libs.array_kernels.setna(cvs__ocw, dwb__ylc)
                    else:
                        cvs__ocw[dwb__ylc] = int(data[dwb__ylc])
                return cvs__ocw
            return impl_float
        else:
            if data == bodo.dict_str_arr_type:

                def impl_dict(data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False):
                    return bodo.libs.dict_arr_ext.convert_dict_arr_to_int(data,
                        otq__wdhs)
                return impl_dict

            def impl(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                nbh__aoxv = len(data)
                numba.parfors.parfor.init_prange()
                cvs__ocw = bodo.libs.int_arr_ext.alloc_int_array(nbh__aoxv,
                    otq__wdhs)
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    if bodo.libs.array_kernels.isna(data, dwb__ylc):
                        bodo.libs.array_kernels.setna(cvs__ocw, dwb__ylc)
                    else:
                        cvs__ocw[dwb__ylc] = np.int64(data[dwb__ylc])
                return cvs__ocw
            return impl
    if isinstance(nb_dtype, types.Integer) and isinstance(data.dtype, types
        .Integer):

        def impl(data, new_dtype, copy=None, nan_to_str=True, from_series=False
            ):
            return data.astype(nb_dtype)
        return impl
    if nb_dtype == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            nbh__aoxv = len(data)
            numba.parfors.parfor.init_prange()
            cvs__ocw = bodo.libs.bool_arr_ext.alloc_bool_array(nbh__aoxv)
            for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv):
                if bodo.libs.array_kernels.isna(data, dwb__ylc):
                    bodo.libs.array_kernels.setna(cvs__ocw, dwb__ylc)
                else:
                    cvs__ocw[dwb__ylc] = bool(data[dwb__ylc])
            return cvs__ocw
        return impl_bool
    if nb_dtype == bodo.datetime_date_type:
        if data.dtype == bodo.datetime64ns:

            def impl_date(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                nbh__aoxv = len(data)
                dmz__krpg = (bodo.hiframes.datetime_date_ext.
                    alloc_datetime_date_array(nbh__aoxv))
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    if bodo.libs.array_kernels.isna(data, dwb__ylc):
                        bodo.libs.array_kernels.setna(dmz__krpg, dwb__ylc)
                    else:
                        dmz__krpg[dwb__ylc
                            ] = bodo.utils.conversion.box_if_dt64(data[
                            dwb__ylc]).date()
                return dmz__krpg
            return impl_date
    if nb_dtype == bodo.datetime64ns:
        if data.dtype == bodo.string_type:

            def impl_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return bodo.hiframes.pd_timestamp_ext.series_str_dt64_astype(
                    data)
            return impl_str
        if data == bodo.datetime_date_array_type:

            def impl_date(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return (bodo.hiframes.pd_timestamp_ext.
                    datetime_date_arr_to_dt64_arr(data))
            return impl_date
        if isinstance(data.dtype, types.Number) or data.dtype in [bodo.
            timedelta64ns, types.bool_]:

            def impl_numeric(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                nbh__aoxv = len(data)
                numba.parfors.parfor.init_prange()
                dmz__krpg = np.empty(nbh__aoxv, dtype=np.dtype(
                    'datetime64[ns]'))
                for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv
                    ):
                    if bodo.libs.array_kernels.isna(data, dwb__ylc):
                        bodo.libs.array_kernels.setna(dmz__krpg, dwb__ylc)
                    else:
                        dmz__krpg[dwb__ylc
                            ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                            np.int64(data[dwb__ylc]))
                return dmz__krpg
            return impl_numeric
    if nb_dtype == bodo.timedelta64ns:
        if data.dtype == bodo.string_type:

            def impl_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return bodo.hiframes.pd_timestamp_ext.series_str_td64_astype(
                    data)
            return impl_str
        if isinstance(data.dtype, types.Number) or data.dtype in [bodo.
            datetime64ns, types.bool_]:
            if bgkny__lvnyz:

                def impl_numeric(data, new_dtype, copy=None, nan_to_str=
                    True, from_series=False):
                    nbh__aoxv = len(data)
                    numba.parfors.parfor.init_prange()
                    dmz__krpg = np.empty(nbh__aoxv, dtype=np.dtype(
                        'timedelta64[ns]'))
                    for dwb__ylc in numba.parfors.parfor.internal_prange(
                        nbh__aoxv):
                        if bodo.libs.array_kernels.isna(data, dwb__ylc):
                            bodo.libs.array_kernels.setna(dmz__krpg, dwb__ylc)
                        else:
                            dmz__krpg[dwb__ylc] = (bodo.hiframes.
                                pd_timestamp_ext.integer_to_timedelta64(np.
                                int64(data[dwb__ylc])))
                    return dmz__krpg
                return impl_numeric
            else:
                return (lambda data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False: data.view('int64'))
    if nb_dtype == types.int64 and data.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]:

        def impl_datelike_to_integer(data, new_dtype, copy=None, nan_to_str
            =True, from_series=False):
            nbh__aoxv = len(data)
            numba.parfors.parfor.init_prange()
            A = np.empty(nbh__aoxv, types.int64)
            for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv):
                if bodo.libs.array_kernels.isna(data, dwb__ylc):
                    bodo.libs.array_kernels.setna(A, dwb__ylc)
                else:
                    A[dwb__ylc] = np.int64(data[dwb__ylc])
            return A
        return impl_datelike_to_integer
    if data.dtype != nb_dtype:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.astype(nb_dtype))
    raise BodoError(f'Conversion from {data} to {new_dtype} not supported yet')


def array_type_from_dtype(dtype):
    return dtype_to_array_type(bodo.utils.typing.parse_dtype(dtype))


@overload(array_type_from_dtype)
def overload_array_type_from_dtype(dtype):
    arr_type = dtype_to_array_type(bodo.utils.typing.parse_dtype(dtype))
    return lambda dtype: arr_type


@numba.jit
def flatten_array(A):
    kiysp__ymjwj = []
    nbh__aoxv = len(A)
    for dwb__ylc in range(nbh__aoxv):
        usnm__vih = A[dwb__ylc]
        for btj__gyv in usnm__vih:
            kiysp__ymjwj.append(btj__gyv)
    return bodo.utils.conversion.coerce_to_array(kiysp__ymjwj)


def parse_datetimes_from_strings(data):
    return data


@overload(parse_datetimes_from_strings, no_unliteral=True)
def overload_parse_datetimes_from_strings(data):
    assert is_str_arr_type(data
        ), 'parse_datetimes_from_strings: string array expected'

    def parse_impl(data):
        numba.parfors.parfor.init_prange()
        nbh__aoxv = len(data)
        ptd__vdxu = np.empty(nbh__aoxv, bodo.utils.conversion.NS_DTYPE)
        for dwb__ylc in numba.parfors.parfor.internal_prange(nbh__aoxv):
            ptd__vdxu[dwb__ylc
                ] = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(data[
                dwb__ylc])
        return ptd__vdxu
    return parse_impl


def convert_to_dt64ns(data):
    return data


@overload(convert_to_dt64ns, no_unliteral=True)
def overload_convert_to_dt64ns(data):
    if data == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        return (lambda data: bodo.hiframes.pd_timestamp_ext.
            datetime_date_arr_to_dt64_arr(data))
    if is_np_arr_typ(data, types.int64):
        return lambda data: data.view(bodo.utils.conversion.NS_DTYPE)
    if is_np_arr_typ(data, types.NPDatetime('ns')):
        return lambda data: data
    if is_str_arr_type(data):
        return lambda data: bodo.utils.conversion.parse_datetimes_from_strings(
            data)
    raise BodoError(f'invalid data type {data} for dt64 conversion')


def convert_to_td64ns(data):
    return data


@overload(convert_to_td64ns, no_unliteral=True)
def overload_convert_to_td64ns(data):
    if is_np_arr_typ(data, types.int64):
        return lambda data: data.view(bodo.utils.conversion.TD_DTYPE)
    if is_np_arr_typ(data, types.NPTimedelta('ns')):
        return lambda data: data
    if is_str_arr_type(data):
        raise BodoError('conversion to timedelta from string not supported yet'
            )
    raise BodoError(f'invalid data type {data} for timedelta64 conversion')


def convert_to_index(data, name=None):
    return data


@overload(convert_to_index, no_unliteral=True)
def overload_convert_to_index(data, name=None):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
    if isinstance(data, (RangeIndexType, NumericIndexType,
        DatetimeIndexType, TimedeltaIndexType, StringIndexType,
        BinaryIndexType, CategoricalIndexType, PeriodIndexType, types.NoneType)
        ):
        return lambda data, name=None: data

    def impl(data, name=None):
        bdq__byrjt = bodo.utils.conversion.coerce_to_array(data)
        return bodo.utils.conversion.index_from_array(bdq__byrjt, name)
    return impl


def force_convert_index(I1, I2):
    return I2


@overload(force_convert_index, no_unliteral=True)
def overload_force_convert_index(I1, I2):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if isinstance(I2, RangeIndexType):
        return lambda I1, I2: pd.RangeIndex(len(I1._data))
    return lambda I1, I2: I1


def index_from_array(data, name=None):
    return data


@overload(index_from_array, no_unliteral=True)
def overload_index_from_array(data, name=None):
    if data in [bodo.string_array_type, bodo.binary_array_type, bodo.
        dict_str_arr_type]:
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_binary_str_index(data, name))
    if (data == bodo.hiframes.datetime_date_ext.datetime_date_array_type or
        data.dtype == types.NPDatetime('ns')):
        return lambda data, name=None: pd.DatetimeIndex(data, name=name)
    if data.dtype == types.NPTimedelta('ns'):
        return lambda data, name=None: pd.TimedeltaIndex(data, name=name)
    if isinstance(data.dtype, (types.Integer, types.Float, types.Boolean)):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_numeric_index(data, name))
    if isinstance(data, bodo.libs.interval_arr_ext.IntervalArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_interval_index(data, name))
    if isinstance(data, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_categorical_index(data, name))
    if isinstance(data, bodo.libs.pd_datetime_arr_ext.DatetimeArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_datetime_index(data, name))
    raise BodoError(f'cannot convert {data} to Index')


def index_to_array(data):
    return data


@overload(index_to_array, no_unliteral=True)
def overload_index_to_array(I):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if isinstance(I, RangeIndexType):
        return lambda I: np.arange(I._start, I._stop, I._step)
    return lambda I: bodo.hiframes.pd_index_ext.get_index_data(I)


def false_if_none(val):
    return False if val is None else val


@overload(false_if_none, no_unliteral=True)
def overload_false_if_none(val):
    if is_overload_none(val):
        return lambda val: False
    return lambda val: val


def extract_name_if_none(data, name):
    return name


@overload(extract_name_if_none, no_unliteral=True)
def overload_extract_name_if_none(data, name):
    from bodo.hiframes.pd_index_ext import CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    if not is_overload_none(name):
        return lambda data, name: name
    if isinstance(data, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, PeriodIndexType, CategoricalIndexType)):
        return lambda data, name: bodo.hiframes.pd_index_ext.get_index_name(
            data)
    if isinstance(data, SeriesType):
        return lambda data, name: bodo.hiframes.pd_series_ext.get_series_name(
            data)
    return lambda data, name: name


def extract_index_if_none(data, index):
    return index


@overload(extract_index_if_none, no_unliteral=True)
def overload_extract_index_if_none(data, index):
    from bodo.hiframes.pd_series_ext import SeriesType
    if not is_overload_none(index):
        return lambda data, index: index
    if isinstance(data, SeriesType):
        return (lambda data, index: bodo.hiframes.pd_series_ext.
            get_series_index(data))
    return lambda data, index: bodo.hiframes.pd_index_ext.init_range_index(
        0, len(data), 1, None)


def box_if_dt64(val):
    return val


@overload(box_if_dt64, no_unliteral=True)
def overload_box_if_dt64(val):
    if val == types.NPDatetime('ns'):
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            convert_datetime64_to_timestamp(val))
    if val == types.NPTimedelta('ns'):
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            convert_numpy_timedelta64_to_pd_timedelta(val))
    return lambda val: val


def unbox_if_timestamp(val):
    return val


@overload(unbox_if_timestamp, no_unliteral=True)
def overload_unbox_if_timestamp(val):
    if val == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        return lambda val: bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val
            .value)
    if val == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
        return lambda val: bodo.hiframes.pd_timestamp_ext.integer_to_dt64(pd
            .Timestamp(val).value)
    if val == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(val.value))
    if val == types.Optional(bodo.hiframes.pd_timestamp_ext.pd_timestamp_type):

        def impl_optional(val):
            if val is None:
                lanm__tezy = None
            else:
                lanm__tezy = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    bodo.utils.indexing.unoptional(val).value)
            return lanm__tezy
        return impl_optional
    if val == types.Optional(bodo.hiframes.datetime_timedelta_ext.
        pd_timedelta_type):

        def impl_optional_td(val):
            if val is None:
                lanm__tezy = None
            else:
                lanm__tezy = (bodo.hiframes.pd_timestamp_ext.
                    integer_to_timedelta64(bodo.utils.indexing.unoptional(
                    val).value))
            return lanm__tezy
        return impl_optional_td
    return lambda val: val


def to_tuple(val):
    return val


@overload(to_tuple, no_unliteral=True)
def overload_to_tuple(val):
    if not isinstance(val, types.BaseTuple) and is_overload_constant_list(val):
        yyrjs__ksmlf = len(val.types if isinstance(val, types.LiteralList) else
            get_overload_const_list(val))
        mpu__out = 'def f(val):\n'
        apjiu__ycgs = ','.join(f'val[{dwb__ylc}]' for dwb__ylc in range(
            yyrjs__ksmlf))
        mpu__out += f'  return ({apjiu__ycgs},)\n'
        xiqa__xjvn = {}
        exec(mpu__out, {}, xiqa__xjvn)
        impl = xiqa__xjvn['f']
        return impl
    assert isinstance(val, types.BaseTuple), 'tuple type expected'
    return lambda val: val


def get_array_if_series_or_index(data):
    return data


@overload(get_array_if_series_or_index)
def overload_get_array_if_series_or_index(data):
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(data, SeriesType):
        return lambda data: bodo.hiframes.pd_series_ext.get_series_data(data)
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        return lambda data: bodo.utils.conversion.coerce_to_array(data)
    if isinstance(data, bodo.hiframes.pd_index_ext.HeterogeneousIndexType):
        if not is_heterogeneous_tuple_type(data.data):

            def impl(data):
                jqt__axrrp = bodo.hiframes.pd_index_ext.get_index_data(data)
                return bodo.utils.conversion.coerce_to_array(jqt__axrrp)
            return impl

        def impl(data):
            return bodo.hiframes.pd_index_ext.get_index_data(data)
        return impl
    return lambda data: data


def extract_index_array(A):
    return np.arange(len(A))


@overload(extract_index_array, no_unliteral=True)
def overload_extract_index_array(A):
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(A, SeriesType):

        def impl(A):
            index = bodo.hiframes.pd_series_ext.get_series_index(A)
            rzc__vmi = bodo.utils.conversion.coerce_to_array(index)
            return rzc__vmi
        return impl
    return lambda A: np.arange(len(A))


def ensure_contig_if_np(arr):
    return np.ascontiguousarray(arr)


@overload(ensure_contig_if_np, no_unliteral=True)
def overload_ensure_contig_if_np(arr):
    if isinstance(arr, types.Array):
        return lambda arr: np.ascontiguousarray(arr)
    return lambda arr: arr


def struct_if_heter_dict(values, names):
    return {qqgm__dgs: jyzyj__tdco for qqgm__dgs, jyzyj__tdco in zip(names,
        values)}


@overload(struct_if_heter_dict, no_unliteral=True)
def overload_struct_if_heter_dict(values, names):
    if not types.is_homogeneous(*values.types):
        return lambda values, names: bodo.libs.struct_arr_ext.init_struct(
            values, names)
    ygoy__tmbo = len(values.types)
    mpu__out = 'def f(values, names):\n'
    apjiu__ycgs = ','.join("'{}': values[{}]".format(get_overload_const_str
        (names.types[dwb__ylc]), dwb__ylc) for dwb__ylc in range(ygoy__tmbo))
    mpu__out += '  return {{{}}}\n'.format(apjiu__ycgs)
    xiqa__xjvn = {}
    exec(mpu__out, {}, xiqa__xjvn)
    impl = xiqa__xjvn['f']
    return impl
