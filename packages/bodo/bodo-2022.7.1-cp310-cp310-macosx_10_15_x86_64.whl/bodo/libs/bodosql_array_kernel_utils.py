"""
Common utilities for all BodoSQL array kernels
"""
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from numba.core import types
import bodo
from bodo.utils.typing import is_overload_bool, is_overload_constant_number, is_overload_constant_str, is_overload_int, raise_bodo_error


def gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
    out_dtype, arg_string=None, arg_sources=None, array_override=None,
    support_dict_encoding=True):
    pat__uii = [bodo.utils.utils.is_array_typ(rhs__hcvrs, True) for
        rhs__hcvrs in arg_types]
    afjq__fvc = not any(pat__uii)
    wts__wlgc = any([propagate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    zzxl__izkq = 0
    udd__bzvc = -1
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            zzxl__izkq += 1
            if arg_types[i] == bodo.dict_str_arr_type:
                udd__bzvc = i
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            zzxl__izkq += 1
            if arg_types[i].dtype == bodo.dict_str_arr_type:
                udd__bzvc = i
    kwhm__ilp = (support_dict_encoding and zzxl__izkq == 1 and udd__bzvc >=
        0 and out_dtype == bodo.string_array_type)
    ysvx__udbz = scalar_text.splitlines()[0]
    cbrxx__ioffv = len(ysvx__udbz) - len(ysvx__udbz.lstrip())
    if arg_string is None:
        arg_string = ', '.join(arg_names)
    anf__ixm = f'def impl({arg_string}):\n'
    if arg_sources is not None:
        for ndwn__vtb, bal__blm in arg_sources.items():
            anf__ixm += f'   {ndwn__vtb} = {bal__blm}\n'
    if afjq__fvc and array_override == None:
        if wts__wlgc:
            anf__ixm += '   return None'
        else:
            for i in range(len(arg_names)):
                anf__ixm += f'   arg{i} = {arg_names[i]}\n'
            for rhvch__fhl in scalar_text.splitlines():
                anf__ixm += ' ' * 3 + rhvch__fhl[cbrxx__ioffv:].replace(
                    'res[i] =', 'answer =').replace(
                    'bodo.libs.array_kernels.setna(res, i)', 'return None'
                    ) + '\n'
            anf__ixm += '   return answer'
    else:
        for i in range(len(arg_names)):
            if bodo.hiframes.pd_series_ext.is_series_type(arg_types[i]):
                anf__ixm += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        if array_override != None:
            tqi__wsi = f'len({array_override})'
        else:
            for i in range(len(arg_names)):
                if pat__uii[i]:
                    tqi__wsi = f'len({arg_names[i]})'
                    break
        if kwhm__ilp:
            anf__ixm += (
                f'   indices = {arg_names[udd__bzvc]}._indices.copy()\n')
            anf__ixm += (
                f'   has_global = {arg_names[udd__bzvc]}._has_global_dictionary\n'
                )
            anf__ixm += f'   {arg_names[i]} = {arg_names[udd__bzvc]}._data\n'
        anf__ixm += f'   n = {tqi__wsi}\n'
        if kwhm__ilp:
            anf__ixm += (
                '   res = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                )
            anf__ixm += '   for i in range(n):\n'
        else:
            anf__ixm += (
                f'   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n')
            anf__ixm += '   numba.parfors.parfor.init_prange()\n'
            anf__ixm += (
                '   for i in numba.parfors.parfor.internal_prange(n):\n')
        if wts__wlgc:
            anf__ixm += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if pat__uii[i]:
                    if propagate_null[i]:
                        anf__ixm += (
                            f'      if bodo.libs.array_kernels.isna({arg_names[i]}, i):\n'
                            )
                        anf__ixm += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        anf__ixm += '         continue\n'
            for i in range(len(arg_names)):
                if pat__uii[i]:
                    anf__ixm += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    anf__ixm += f'      arg{i} = {arg_names[i]}\n'
            for rhvch__fhl in scalar_text.splitlines():
                anf__ixm += ' ' * 6 + rhvch__fhl[cbrxx__ioffv:] + '\n'
        if kwhm__ilp:
            anf__ixm += '   for i in range(n):\n'
            anf__ixm += (
                '      if not bodo.libs.array_kernels.isna(indices, i):\n')
            anf__ixm += '         loc = indices[i]\n'
            anf__ixm += '         if bodo.libs.array_kernels.isna(res, loc):\n'
            anf__ixm += (
                '            bodo.libs.array_kernels.setna(indices, i)\n')
            anf__ixm += (
                '   res = bodo.libs.dict_arr_ext.init_dict_arr(res, indices, has_global)\n'
                )
            anf__ixm += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, len(indices), 1), None)'
                )
        else:
            anf__ixm += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
                )
    nomhm__mabzs = {}
    exec(anf__ixm, {'bodo': bodo, 'numba': numba, 'np': np, 'out_dtype':
        out_dtype, 'pd': pd}, nomhm__mabzs)
    zfe__yco = nomhm__mabzs['impl']
    return zfe__yco


def unopt_argument(func_name, arg_names, i, container_length=None):
    if container_length != None:
        owwxp__lmux = [(f'{arg_names[0]}{[vtm__sglpz]}' if vtm__sglpz != i else
            'None') for vtm__sglpz in range(container_length)]
        qcmph__hrs = [(f'{arg_names[0]}{[vtm__sglpz]}' if vtm__sglpz != i else
            f'bodo.utils.indexing.unoptional({arg_names[0]}[{vtm__sglpz}])'
            ) for vtm__sglpz in range(container_length)]
        anf__ixm = f"def impl({', '.join(arg_names)}):\n"
        anf__ixm += f'   if {arg_names[0]}[{i}] is None:\n'
        anf__ixm += f"      return {func_name}(({', '.join(owwxp__lmux)}))\n"
        anf__ixm += f'   else:\n'
        anf__ixm += f"      return {func_name}(({', '.join(qcmph__hrs)}))"
    else:
        owwxp__lmux = [(arg_names[vtm__sglpz] if vtm__sglpz != i else
            'None') for vtm__sglpz in range(len(arg_names))]
        qcmph__hrs = [(arg_names[vtm__sglpz] if vtm__sglpz != i else
            f'bodo.utils.indexing.unoptional({arg_names[vtm__sglpz]})') for
            vtm__sglpz in range(len(arg_names))]
        anf__ixm = f"def impl({', '.join(arg_names)}):\n"
        anf__ixm += f'   if {arg_names[i]} is None:\n'
        anf__ixm += f"      return {func_name}({', '.join(owwxp__lmux)})\n"
        anf__ixm += f'   else:\n'
        anf__ixm += f"      return {func_name}({', '.join(qcmph__hrs)})"
    nomhm__mabzs = {}
    exec(anf__ixm, {'bodo': bodo, 'numba': numba}, nomhm__mabzs)
    zfe__yco = nomhm__mabzs['impl']
    return zfe__yco


def verify_int_arg(arg, f_name, a_name):
    if arg != types.none and not isinstance(arg, types.Integer) and not (bodo
        .utils.utils.is_array_typ(arg, True) and isinstance(arg.dtype,
        types.Integer)) and not is_overload_int(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be an integer, integer column, or null'
            )


def verify_int_float_arg(arg, f_name, a_name):
    if arg != types.none and not isinstance(arg, (types.Integer, types.
        Float, types.Boolean)) and not (bodo.utils.utils.is_array_typ(arg, 
        True) and isinstance(arg.dtype, (types.Integer, types.Float, types.
        Boolean))) and not is_overload_constant_number(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a numeric, numeric column, or null'
            )


def verify_string_arg(arg, f_name, a_name):
    if arg not in (types.none, types.unicode_type) and not isinstance(arg,
        types.StringLiteral) and not (bodo.utils.utils.is_array_typ(arg, 
        True) and arg.dtype == types.unicode_type
        ) and not is_overload_constant_str(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a string, string column, or null'
            )


def verify_boolean_arg(arg, f_name, a_name):
    if arg not in (types.none, types.boolean) and not (bodo.utils.utils.
        is_array_typ(arg, True) and arg.dtype == types.boolean
        ) and not is_overload_bool(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a boolean, boolean column, or null'
            )


def verify_datetime_arg(arg, f_name, a_name):
    if arg not in (types.none, bodo.datetime64ns, bodo.pd_timestamp_type,
        bodo.hiframes.datetime_date_ext.DatetimeDateType()) and not (bodo.
        utils.utils.is_array_typ(arg, True) and arg.dtype in (bodo.
        datetime64ns, bodo.hiframes.datetime_date_ext.DatetimeDateType())):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a datetime, datetime column, or null'
            )


def get_common_broadcasted_type(arg_types, func_name):
    jdsf__ycv = []
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            jdsf__ycv.append(arg_types[i])
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            jdsf__ycv.append(arg_types[i].data)
        else:
            jdsf__ycv.append(arg_types[i])
    if len(jdsf__ycv) == 0:
        return bodo.none
    elif len(jdsf__ycv) == 1:
        if bodo.utils.utils.is_array_typ(jdsf__ycv[0]):
            return bodo.utils.typing.to_nullable_type(jdsf__ycv[0])
        elif jdsf__ycv[0] == bodo.none:
            return bodo.none
        else:
            return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
                dtype_to_array_type(jdsf__ycv[0]))
    else:
        ffoet__aaox = []
        for i in range(len(arg_types)):
            if bodo.utils.utils.is_array_typ(arg_types[i]):
                ffoet__aaox.append(jdsf__ycv[i].dtype)
            elif jdsf__ycv[i] == bodo.none:
                pass
            else:
                ffoet__aaox.append(jdsf__ycv[i])
        if len(ffoet__aaox) == 0:
            return bodo.none
        pbq__jwy, vtbyz__vng = bodo.utils.typing.get_common_scalar_dtype(
            ffoet__aaox)
        if not vtbyz__vng:
            raise_bodo_error(
                f'Cannot call {func_name} on columns with different dtypes')
        return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
            dtype_to_array_type(pbq__jwy))


def vectorized_sol(args, scalar_fn, dtype, manual_coercion=False):
    zkqc__aswi = -1
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            zkqc__aswi = len(arg)
            break
    if zkqc__aswi == -1:
        return dtype(scalar_fn(*args)) if manual_coercion else scalar_fn(*args)
    vxkut__vek = []
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            vxkut__vek.append(arg)
        else:
            vxkut__vek.append([arg] * zkqc__aswi)
    if manual_coercion:
        return pd.Series([dtype(scalar_fn(*afp__rtghk)) for afp__rtghk in
            zip(*vxkut__vek)])
    else:
        return pd.Series([scalar_fn(*afp__rtghk) for afp__rtghk in zip(*
            vxkut__vek)], dtype=dtype)
