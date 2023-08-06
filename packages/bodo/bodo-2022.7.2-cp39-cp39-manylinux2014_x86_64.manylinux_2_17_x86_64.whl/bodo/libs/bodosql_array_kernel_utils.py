"""
Common utilities for all BodoSQL array kernels
"""
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from numba.core import types
import bodo
from bodo.utils.typing import is_overload_bool, is_overload_constant_bytes, is_overload_constant_number, is_overload_constant_str, is_overload_int, raise_bodo_error


def gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
    out_dtype, arg_string=None, arg_sources=None, array_override=None,
    support_dict_encoding=True):
    msyhk__bxdnz = [bodo.utils.utils.is_array_typ(aywyc__mxbqx, True) for
        aywyc__mxbqx in arg_types]
    ccj__mmx = not any(msyhk__bxdnz)
    urh__wxbm = any([propagate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    fjjq__mmpj = 0
    fdisx__nkojv = -1
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            fjjq__mmpj += 1
            if arg_types[i] == bodo.dict_str_arr_type:
                fdisx__nkojv = i
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            fjjq__mmpj += 1
            if arg_types[i].dtype == bodo.dict_str_arr_type:
                fdisx__nkojv = i
    smc__szyll = (support_dict_encoding and fjjq__mmpj == 1 and 
        fdisx__nkojv >= 0 and out_dtype == bodo.string_array_type)
    rtwo__pwa = scalar_text.splitlines()[0]
    fjb__tdg = len(rtwo__pwa) - len(rtwo__pwa.lstrip())
    if arg_string is None:
        arg_string = ', '.join(arg_names)
    gbh__agmx = f'def impl({arg_string}):\n'
    if arg_sources is not None:
        for kulu__pmjci, yzg__fatr in arg_sources.items():
            gbh__agmx += f'   {kulu__pmjci} = {yzg__fatr}\n'
    if ccj__mmx and array_override == None:
        if urh__wxbm:
            gbh__agmx += '   return None'
        else:
            for i in range(len(arg_names)):
                gbh__agmx += f'   arg{i} = {arg_names[i]}\n'
            for yqtdl__lpo in scalar_text.splitlines():
                gbh__agmx += ' ' * 3 + yqtdl__lpo[fjb__tdg:].replace('res[i] ='
                    , 'answer =').replace(
                    'bodo.libs.array_kernels.setna(res, i)', 'return None'
                    ) + '\n'
            gbh__agmx += '   return answer'
    else:
        for i in range(len(arg_names)):
            if bodo.hiframes.pd_series_ext.is_series_type(arg_types[i]):
                gbh__agmx += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        if array_override != None:
            ixn__utjwo = f'len({array_override})'
        else:
            for i in range(len(arg_names)):
                if msyhk__bxdnz[i]:
                    ixn__utjwo = f'len({arg_names[i]})'
                    break
        if smc__szyll:
            gbh__agmx += (
                f'   indices = {arg_names[fdisx__nkojv]}._indices.copy()\n')
            gbh__agmx += (
                f'   has_global = {arg_names[fdisx__nkojv]}._has_global_dictionary\n'
                )
            gbh__agmx += (
                f'   {arg_names[i]} = {arg_names[fdisx__nkojv]}._data\n')
        gbh__agmx += f'   n = {ixn__utjwo}\n'
        if smc__szyll:
            gbh__agmx += (
                '   res = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                )
            gbh__agmx += '   for i in range(n):\n'
        else:
            gbh__agmx += (
                f'   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n')
            gbh__agmx += '   numba.parfors.parfor.init_prange()\n'
            gbh__agmx += (
                '   for i in numba.parfors.parfor.internal_prange(n):\n')
        if urh__wxbm:
            gbh__agmx += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if msyhk__bxdnz[i]:
                    if propagate_null[i]:
                        gbh__agmx += (
                            f'      if bodo.libs.array_kernels.isna({arg_names[i]}, i):\n'
                            )
                        gbh__agmx += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        gbh__agmx += '         continue\n'
            for i in range(len(arg_names)):
                if msyhk__bxdnz[i]:
                    gbh__agmx += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    gbh__agmx += f'      arg{i} = {arg_names[i]}\n'
            for yqtdl__lpo in scalar_text.splitlines():
                gbh__agmx += ' ' * 6 + yqtdl__lpo[fjb__tdg:] + '\n'
        if smc__szyll:
            gbh__agmx += '   for i in range(n):\n'
            gbh__agmx += (
                '      if not bodo.libs.array_kernels.isna(indices, i):\n')
            gbh__agmx += '         loc = indices[i]\n'
            gbh__agmx += (
                '         if bodo.libs.array_kernels.isna(res, loc):\n')
            gbh__agmx += (
                '            bodo.libs.array_kernels.setna(indices, i)\n')
            gbh__agmx += """   res = bodo.libs.dict_arr_ext.init_dict_arr(res, indices, has_global)
"""
            gbh__agmx += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, len(indices), 1), None)'
                )
        else:
            gbh__agmx += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
                )
    xypaz__onpfb = {}
    exec(gbh__agmx, {'bodo': bodo, 'numba': numba, 'np': np, 'out_dtype':
        out_dtype, 'pd': pd}, xypaz__onpfb)
    rrmw__pdegk = xypaz__onpfb['impl']
    return rrmw__pdegk


def unopt_argument(func_name, arg_names, i, container_length=None):
    if container_length != None:
        cbrqp__ptvlu = [(f'{arg_names[0]}{[ccssw__piju]}' if ccssw__piju !=
            i else 'None') for ccssw__piju in range(container_length)]
        qxldw__htws = [(f'{arg_names[0]}{[ccssw__piju]}' if ccssw__piju !=
            i else
            f'bodo.utils.indexing.unoptional({arg_names[0]}[{ccssw__piju}])'
            ) for ccssw__piju in range(container_length)]
        gbh__agmx = f"def impl({', '.join(arg_names)}):\n"
        gbh__agmx += f'   if {arg_names[0]}[{i}] is None:\n'
        gbh__agmx += f"      return {func_name}(({', '.join(cbrqp__ptvlu)}))\n"
        gbh__agmx += f'   else:\n'
        gbh__agmx += f"      return {func_name}(({', '.join(qxldw__htws)}))"
    else:
        cbrqp__ptvlu = [(arg_names[ccssw__piju] if ccssw__piju != i else
            'None') for ccssw__piju in range(len(arg_names))]
        qxldw__htws = [(arg_names[ccssw__piju] if ccssw__piju != i else
            f'bodo.utils.indexing.unoptional({arg_names[ccssw__piju]})') for
            ccssw__piju in range(len(arg_names))]
        gbh__agmx = f"def impl({', '.join(arg_names)}):\n"
        gbh__agmx += f'   if {arg_names[i]} is None:\n'
        gbh__agmx += f"      return {func_name}({', '.join(cbrqp__ptvlu)})\n"
        gbh__agmx += f'   else:\n'
        gbh__agmx += f"      return {func_name}({', '.join(qxldw__htws)})"
    xypaz__onpfb = {}
    exec(gbh__agmx, {'bodo': bodo, 'numba': numba}, xypaz__onpfb)
    rrmw__pdegk = xypaz__onpfb['impl']
    return rrmw__pdegk


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


def is_valid_string_arg(arg):
    return not (arg not in (types.none, types.unicode_type) and not
        isinstance(arg, types.StringLiteral) and not (bodo.utils.utils.
        is_array_typ(arg, True) and arg.dtype == types.unicode_type) and 
        not is_overload_constant_str(arg))


def is_valid_binary_arg(arg):
    return not (arg != bodo.bytes_type and not (bodo.utils.utils.
        is_array_typ(arg, True) and arg.dtype == bodo.bytes_type) and not
        is_overload_constant_bytes(arg) and not isinstance(arg, types.Bytes))


def verify_string_arg(arg, f_name, a_name):
    if not is_valid_string_arg(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a string, string column, or null'
            )


def verify_binary_arg(arg, f_name, a_name):
    if not is_valid_binary_arg(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be binary data or null')


def verify_string_binary_arg(arg, f_name, a_name):
    fssty__omqf = is_valid_string_arg(arg)
    nnbls__vxksg = is_valid_binary_arg(arg)
    if fssty__omqf or nnbls__vxksg:
        return fssty__omqf
    else:
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a binary data, string, string column, or null'
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
    ntkpb__xbtyb = []
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            ntkpb__xbtyb.append(arg_types[i])
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            ntkpb__xbtyb.append(arg_types[i].data)
        else:
            ntkpb__xbtyb.append(arg_types[i])
    if len(ntkpb__xbtyb) == 0:
        return bodo.none
    elif len(ntkpb__xbtyb) == 1:
        if bodo.utils.utils.is_array_typ(ntkpb__xbtyb[0]):
            return bodo.utils.typing.to_nullable_type(ntkpb__xbtyb[0])
        elif ntkpb__xbtyb[0] == bodo.none:
            return bodo.none
        else:
            return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
                dtype_to_array_type(ntkpb__xbtyb[0]))
    else:
        nhga__fasp = []
        for i in range(len(arg_types)):
            if bodo.utils.utils.is_array_typ(arg_types[i]):
                nhga__fasp.append(ntkpb__xbtyb[i].dtype)
            elif ntkpb__xbtyb[i] == bodo.none:
                pass
            else:
                nhga__fasp.append(ntkpb__xbtyb[i])
        if len(nhga__fasp) == 0:
            return bodo.none
        sli__qjw, wslz__tkv = bodo.utils.typing.get_common_scalar_dtype(
            nhga__fasp)
        if not wslz__tkv:
            raise_bodo_error(
                f'Cannot call {func_name} on columns with different dtypes')
        return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
            dtype_to_array_type(sli__qjw))


def vectorized_sol(args, scalar_fn, dtype, manual_coercion=False):
    vbfr__dvq = -1
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            vbfr__dvq = len(arg)
            break
    if vbfr__dvq == -1:
        return dtype(scalar_fn(*args)) if manual_coercion else scalar_fn(*args)
    dlhgu__atev = []
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            dlhgu__atev.append(arg)
        else:
            dlhgu__atev.append([arg] * vbfr__dvq)
    if manual_coercion:
        return pd.Series([dtype(scalar_fn(*jzq__agny)) for jzq__agny in zip
            (*dlhgu__atev)])
    else:
        return pd.Series([scalar_fn(*jzq__agny) for jzq__agny in zip(*
            dlhgu__atev)], dtype=dtype)
