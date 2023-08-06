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
    nukng__spah = [bodo.utils.utils.is_array_typ(gti__pav, True) for
        gti__pav in arg_types]
    xqhdg__ohfy = not any(nukng__spah)
    aiisx__piuup = any([propagate_null[i] for i in range(len(arg_types)) if
        arg_types[i] == bodo.none])
    rngp__nmcia = 0
    xnch__wrf = -1
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            rngp__nmcia += 1
            if arg_types[i] == bodo.dict_str_arr_type:
                xnch__wrf = i
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            rngp__nmcia += 1
            if arg_types[i].dtype == bodo.dict_str_arr_type:
                xnch__wrf = i
    gzvjn__hgejh = (support_dict_encoding and rngp__nmcia == 1 and 
        xnch__wrf >= 0 and out_dtype == bodo.string_array_type)
    iyxpz__lcr = scalar_text.splitlines()[0]
    yxy__rmkgr = len(iyxpz__lcr) - len(iyxpz__lcr.lstrip())
    if arg_string is None:
        arg_string = ', '.join(arg_names)
    faobl__vpgb = f'def impl({arg_string}):\n'
    if arg_sources is not None:
        for fjex__ogs, cmnmr__uzp in arg_sources.items():
            faobl__vpgb += f'   {fjex__ogs} = {cmnmr__uzp}\n'
    if xqhdg__ohfy and array_override == None:
        if aiisx__piuup:
            faobl__vpgb += '   return None'
        else:
            for i in range(len(arg_names)):
                faobl__vpgb += f'   arg{i} = {arg_names[i]}\n'
            for eqwbq__okmxh in scalar_text.splitlines():
                faobl__vpgb += ' ' * 3 + eqwbq__okmxh[yxy__rmkgr:].replace(
                    'res[i] =', 'answer =').replace(
                    'bodo.libs.array_kernels.setna(res, i)', 'return None'
                    ) + '\n'
            faobl__vpgb += '   return answer'
    else:
        for i in range(len(arg_names)):
            if bodo.hiframes.pd_series_ext.is_series_type(arg_types[i]):
                faobl__vpgb += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        if array_override != None:
            cean__ngnjn = f'len({array_override})'
        else:
            for i in range(len(arg_names)):
                if nukng__spah[i]:
                    cean__ngnjn = f'len({arg_names[i]})'
                    break
        if gzvjn__hgejh:
            faobl__vpgb += (
                f'   indices = {arg_names[xnch__wrf]}._indices.copy()\n')
            faobl__vpgb += (
                f'   has_global = {arg_names[xnch__wrf]}._has_global_dictionary\n'
                )
            faobl__vpgb += (
                f'   {arg_names[i]} = {arg_names[xnch__wrf]}._data\n')
        faobl__vpgb += f'   n = {cean__ngnjn}\n'
        if gzvjn__hgejh:
            faobl__vpgb += (
                '   res = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                )
            faobl__vpgb += '   for i in range(n):\n'
        else:
            faobl__vpgb += (
                f'   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n')
            faobl__vpgb += '   numba.parfors.parfor.init_prange()\n'
            faobl__vpgb += (
                '   for i in numba.parfors.parfor.internal_prange(n):\n')
        if aiisx__piuup:
            faobl__vpgb += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if nukng__spah[i]:
                    if propagate_null[i]:
                        faobl__vpgb += f"""      if bodo.libs.array_kernels.isna({arg_names[i]}, i):
"""
                        faobl__vpgb += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        faobl__vpgb += '         continue\n'
            for i in range(len(arg_names)):
                if nukng__spah[i]:
                    faobl__vpgb += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    faobl__vpgb += f'      arg{i} = {arg_names[i]}\n'
            for eqwbq__okmxh in scalar_text.splitlines():
                faobl__vpgb += ' ' * 6 + eqwbq__okmxh[yxy__rmkgr:] + '\n'
        if gzvjn__hgejh:
            faobl__vpgb += '   for i in range(n):\n'
            faobl__vpgb += (
                '      if not bodo.libs.array_kernels.isna(indices, i):\n')
            faobl__vpgb += '         loc = indices[i]\n'
            faobl__vpgb += (
                '         if bodo.libs.array_kernels.isna(res, loc):\n')
            faobl__vpgb += (
                '            bodo.libs.array_kernels.setna(indices, i)\n')
            faobl__vpgb += """   res = bodo.libs.dict_arr_ext.init_dict_arr(res, indices, has_global)
"""
            faobl__vpgb += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, len(indices), 1), None)'
                )
        else:
            faobl__vpgb += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
                )
    vytk__sjqjs = {}
    exec(faobl__vpgb, {'bodo': bodo, 'numba': numba, 'np': np, 'out_dtype':
        out_dtype, 'pd': pd}, vytk__sjqjs)
    phz__hobc = vytk__sjqjs['impl']
    return phz__hobc


def unopt_argument(func_name, arg_names, i, container_length=None):
    if container_length != None:
        tmar__svhm = [(f'{arg_names[0]}{[ylhmp__nkfdv]}' if ylhmp__nkfdv !=
            i else 'None') for ylhmp__nkfdv in range(container_length)]
        docm__cdpg = [(f'{arg_names[0]}{[ylhmp__nkfdv]}' if ylhmp__nkfdv !=
            i else
            f'bodo.utils.indexing.unoptional({arg_names[0]}[{ylhmp__nkfdv}])'
            ) for ylhmp__nkfdv in range(container_length)]
        faobl__vpgb = f"def impl({', '.join(arg_names)}):\n"
        faobl__vpgb += f'   if {arg_names[0]}[{i}] is None:\n'
        faobl__vpgb += f"      return {func_name}(({', '.join(tmar__svhm)}))\n"
        faobl__vpgb += f'   else:\n'
        faobl__vpgb += f"      return {func_name}(({', '.join(docm__cdpg)}))"
    else:
        tmar__svhm = [(arg_names[ylhmp__nkfdv] if ylhmp__nkfdv != i else
            'None') for ylhmp__nkfdv in range(len(arg_names))]
        docm__cdpg = [(arg_names[ylhmp__nkfdv] if ylhmp__nkfdv != i else
            f'bodo.utils.indexing.unoptional({arg_names[ylhmp__nkfdv]})') for
            ylhmp__nkfdv in range(len(arg_names))]
        faobl__vpgb = f"def impl({', '.join(arg_names)}):\n"
        faobl__vpgb += f'   if {arg_names[i]} is None:\n'
        faobl__vpgb += f"      return {func_name}({', '.join(tmar__svhm)})\n"
        faobl__vpgb += f'   else:\n'
        faobl__vpgb += f"      return {func_name}({', '.join(docm__cdpg)})"
    vytk__sjqjs = {}
    exec(faobl__vpgb, {'bodo': bodo, 'numba': numba}, vytk__sjqjs)
    phz__hobc = vytk__sjqjs['impl']
    return phz__hobc


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
    lfu__yjkt = is_valid_string_arg(arg)
    evzi__uyu = is_valid_binary_arg(arg)
    if lfu__yjkt or evzi__uyu:
        return lfu__yjkt
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
    wzicy__dbyaf = []
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            wzicy__dbyaf.append(arg_types[i])
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            wzicy__dbyaf.append(arg_types[i].data)
        else:
            wzicy__dbyaf.append(arg_types[i])
    if len(wzicy__dbyaf) == 0:
        return bodo.none
    elif len(wzicy__dbyaf) == 1:
        if bodo.utils.utils.is_array_typ(wzicy__dbyaf[0]):
            return bodo.utils.typing.to_nullable_type(wzicy__dbyaf[0])
        elif wzicy__dbyaf[0] == bodo.none:
            return bodo.none
        else:
            return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
                dtype_to_array_type(wzicy__dbyaf[0]))
    else:
        gfcu__itxl = []
        for i in range(len(arg_types)):
            if bodo.utils.utils.is_array_typ(arg_types[i]):
                gfcu__itxl.append(wzicy__dbyaf[i].dtype)
            elif wzicy__dbyaf[i] == bodo.none:
                pass
            else:
                gfcu__itxl.append(wzicy__dbyaf[i])
        if len(gfcu__itxl) == 0:
            return bodo.none
        oace__xuoj, cpm__ewee = bodo.utils.typing.get_common_scalar_dtype(
            gfcu__itxl)
        if not cpm__ewee:
            raise_bodo_error(
                f'Cannot call {func_name} on columns with different dtypes')
        return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
            dtype_to_array_type(oace__xuoj))


def vectorized_sol(args, scalar_fn, dtype, manual_coercion=False):
    rzi__xem = -1
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            rzi__xem = len(arg)
            break
    if rzi__xem == -1:
        return dtype(scalar_fn(*args)) if manual_coercion else scalar_fn(*args)
    fim__pvi = []
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            fim__pvi.append(arg)
        else:
            fim__pvi.append([arg] * rzi__xem)
    if manual_coercion:
        return pd.Series([dtype(scalar_fn(*oenn__myw)) for oenn__myw in zip
            (*fim__pvi)])
    else:
        return pd.Series([scalar_fn(*oenn__myw) for oenn__myw in zip(*
            fim__pvi)], dtype=dtype)
