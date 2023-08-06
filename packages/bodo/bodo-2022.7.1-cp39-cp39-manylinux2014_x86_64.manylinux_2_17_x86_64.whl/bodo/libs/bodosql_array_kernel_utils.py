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
    ktics__fdos = [bodo.utils.utils.is_array_typ(sqq__qvb, True) for
        sqq__qvb in arg_types]
    yzd__knnx = not any(ktics__fdos)
    idtra__fya = any([propagate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    acy__qqi = 0
    tksy__hrdm = -1
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            acy__qqi += 1
            if arg_types[i] == bodo.dict_str_arr_type:
                tksy__hrdm = i
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            acy__qqi += 1
            if arg_types[i].dtype == bodo.dict_str_arr_type:
                tksy__hrdm = i
    qlmu__gjk = (support_dict_encoding and acy__qqi == 1 and tksy__hrdm >= 
        0 and out_dtype == bodo.string_array_type)
    fnbbd__bqao = scalar_text.splitlines()[0]
    jvjp__rmnqn = len(fnbbd__bqao) - len(fnbbd__bqao.lstrip())
    if arg_string is None:
        arg_string = ', '.join(arg_names)
    agz__xetn = f'def impl({arg_string}):\n'
    if arg_sources is not None:
        for bksx__iqn, uhs__lqz in arg_sources.items():
            agz__xetn += f'   {bksx__iqn} = {uhs__lqz}\n'
    if yzd__knnx and array_override == None:
        if idtra__fya:
            agz__xetn += '   return None'
        else:
            for i in range(len(arg_names)):
                agz__xetn += f'   arg{i} = {arg_names[i]}\n'
            for ezk__mohol in scalar_text.splitlines():
                agz__xetn += ' ' * 3 + ezk__mohol[jvjp__rmnqn:].replace(
                    'res[i] =', 'answer =').replace(
                    'bodo.libs.array_kernels.setna(res, i)', 'return None'
                    ) + '\n'
            agz__xetn += '   return answer'
    else:
        for i in range(len(arg_names)):
            if bodo.hiframes.pd_series_ext.is_series_type(arg_types[i]):
                agz__xetn += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        if array_override != None:
            eko__bwk = f'len({array_override})'
        else:
            for i in range(len(arg_names)):
                if ktics__fdos[i]:
                    eko__bwk = f'len({arg_names[i]})'
                    break
        if qlmu__gjk:
            agz__xetn += (
                f'   indices = {arg_names[tksy__hrdm]}._indices.copy()\n')
            agz__xetn += (
                f'   has_global = {arg_names[tksy__hrdm]}._has_global_dictionary\n'
                )
            agz__xetn += f'   {arg_names[i]} = {arg_names[tksy__hrdm]}._data\n'
        agz__xetn += f'   n = {eko__bwk}\n'
        if qlmu__gjk:
            agz__xetn += (
                '   res = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                )
            agz__xetn += '   for i in range(n):\n'
        else:
            agz__xetn += (
                f'   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n')
            agz__xetn += '   numba.parfors.parfor.init_prange()\n'
            agz__xetn += (
                '   for i in numba.parfors.parfor.internal_prange(n):\n')
        if idtra__fya:
            agz__xetn += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if ktics__fdos[i]:
                    if propagate_null[i]:
                        agz__xetn += (
                            f'      if bodo.libs.array_kernels.isna({arg_names[i]}, i):\n'
                            )
                        agz__xetn += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        agz__xetn += '         continue\n'
            for i in range(len(arg_names)):
                if ktics__fdos[i]:
                    agz__xetn += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    agz__xetn += f'      arg{i} = {arg_names[i]}\n'
            for ezk__mohol in scalar_text.splitlines():
                agz__xetn += ' ' * 6 + ezk__mohol[jvjp__rmnqn:] + '\n'
        if qlmu__gjk:
            agz__xetn += '   for i in range(n):\n'
            agz__xetn += (
                '      if not bodo.libs.array_kernels.isna(indices, i):\n')
            agz__xetn += '         loc = indices[i]\n'
            agz__xetn += (
                '         if bodo.libs.array_kernels.isna(res, loc):\n')
            agz__xetn += (
                '            bodo.libs.array_kernels.setna(indices, i)\n')
            agz__xetn += """   res = bodo.libs.dict_arr_ext.init_dict_arr(res, indices, has_global)
"""
            agz__xetn += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, len(indices), 1), None)'
                )
        else:
            agz__xetn += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
                )
    qhrs__qjl = {}
    exec(agz__xetn, {'bodo': bodo, 'numba': numba, 'np': np, 'out_dtype':
        out_dtype, 'pd': pd}, qhrs__qjl)
    frzdi__cro = qhrs__qjl['impl']
    return frzdi__cro


def unopt_argument(func_name, arg_names, i, container_length=None):
    if container_length != None:
        udjs__mswa = [(f'{arg_names[0]}{[tyq__nbh]}' if tyq__nbh != i else
            'None') for tyq__nbh in range(container_length)]
        fezjw__fmd = [(f'{arg_names[0]}{[tyq__nbh]}' if tyq__nbh != i else
            f'bodo.utils.indexing.unoptional({arg_names[0]}[{tyq__nbh}])') for
            tyq__nbh in range(container_length)]
        agz__xetn = f"def impl({', '.join(arg_names)}):\n"
        agz__xetn += f'   if {arg_names[0]}[{i}] is None:\n'
        agz__xetn += f"      return {func_name}(({', '.join(udjs__mswa)}))\n"
        agz__xetn += f'   else:\n'
        agz__xetn += f"      return {func_name}(({', '.join(fezjw__fmd)}))"
    else:
        udjs__mswa = [(arg_names[tyq__nbh] if tyq__nbh != i else 'None') for
            tyq__nbh in range(len(arg_names))]
        fezjw__fmd = [(arg_names[tyq__nbh] if tyq__nbh != i else
            f'bodo.utils.indexing.unoptional({arg_names[tyq__nbh]})') for
            tyq__nbh in range(len(arg_names))]
        agz__xetn = f"def impl({', '.join(arg_names)}):\n"
        agz__xetn += f'   if {arg_names[i]} is None:\n'
        agz__xetn += f"      return {func_name}({', '.join(udjs__mswa)})\n"
        agz__xetn += f'   else:\n'
        agz__xetn += f"      return {func_name}({', '.join(fezjw__fmd)})"
    qhrs__qjl = {}
    exec(agz__xetn, {'bodo': bodo, 'numba': numba}, qhrs__qjl)
    frzdi__cro = qhrs__qjl['impl']
    return frzdi__cro


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
    hahtr__eda = []
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            hahtr__eda.append(arg_types[i])
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            hahtr__eda.append(arg_types[i].data)
        else:
            hahtr__eda.append(arg_types[i])
    if len(hahtr__eda) == 0:
        return bodo.none
    elif len(hahtr__eda) == 1:
        if bodo.utils.utils.is_array_typ(hahtr__eda[0]):
            return bodo.utils.typing.to_nullable_type(hahtr__eda[0])
        elif hahtr__eda[0] == bodo.none:
            return bodo.none
        else:
            return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
                dtype_to_array_type(hahtr__eda[0]))
    else:
        oqyju__xwncc = []
        for i in range(len(arg_types)):
            if bodo.utils.utils.is_array_typ(arg_types[i]):
                oqyju__xwncc.append(hahtr__eda[i].dtype)
            elif hahtr__eda[i] == bodo.none:
                pass
            else:
                oqyju__xwncc.append(hahtr__eda[i])
        if len(oqyju__xwncc) == 0:
            return bodo.none
        uzjjx__mcae, efo__rdw = bodo.utils.typing.get_common_scalar_dtype(
            oqyju__xwncc)
        if not efo__rdw:
            raise_bodo_error(
                f'Cannot call {func_name} on columns with different dtypes')
        return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
            dtype_to_array_type(uzjjx__mcae))


def vectorized_sol(args, scalar_fn, dtype, manual_coercion=False):
    ktinc__zcs = -1
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            ktinc__zcs = len(arg)
            break
    if ktinc__zcs == -1:
        return dtype(scalar_fn(*args)) if manual_coercion else scalar_fn(*args)
    pwt__bkvk = []
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            pwt__bkvk.append(arg)
        else:
            pwt__bkvk.append([arg] * ktinc__zcs)
    if manual_coercion:
        return pd.Series([dtype(scalar_fn(*dna__nlh)) for dna__nlh in zip(*
            pwt__bkvk)])
    else:
        return pd.Series([scalar_fn(*dna__nlh) for dna__nlh in zip(*
            pwt__bkvk)], dtype=dtype)
