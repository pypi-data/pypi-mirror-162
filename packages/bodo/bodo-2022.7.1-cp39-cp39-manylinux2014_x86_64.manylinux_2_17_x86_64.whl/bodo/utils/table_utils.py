"""File containing utility functions for supporting DataFrame operations with Table Format."""
from collections import defaultdict
from typing import Dict, Set
import numba
import numpy as np
from numba.core import types
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.table import TableType
from bodo.utils.typing import get_overload_const_bool, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, raise_bodo_error


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_mappable_table_func(table, func_name, out_arr_typ, is_method,
    used_cols=None):
    if not is_overload_constant_str(func_name) and not is_overload_none(
        func_name):
        raise_bodo_error(
            'generate_mappable_table_func(): func_name must be a constant string'
            )
    if not is_overload_constant_bool(is_method):
        raise_bodo_error(
            'generate_mappable_table_func(): is_method must be a constant boolean'
            )
    irqbc__qqg = not is_overload_none(func_name)
    if irqbc__qqg:
        func_name = get_overload_const_str(func_name)
        yjnj__zwg = get_overload_const_bool(is_method)
    ltesn__oynu = out_arr_typ.instance_type if isinstance(out_arr_typ,
        types.TypeRef) else out_arr_typ
    upnw__fbmet = ltesn__oynu == types.none
    atk__pvbgy = len(table.arr_types)
    if upnw__fbmet:
        rqnzp__bsyqe = table
    else:
        svd__vopw = tuple([ltesn__oynu] * atk__pvbgy)
        rqnzp__bsyqe = TableType(svd__vopw)
    yvz__vop = {'bodo': bodo, 'lst_dtype': ltesn__oynu, 'table_typ':
        rqnzp__bsyqe}
    phqg__cbgyc = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if upnw__fbmet:
        phqg__cbgyc += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        phqg__cbgyc += f'  l = len(table)\n'
    else:
        phqg__cbgyc += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({atk__pvbgy}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        ifvn__fvi = used_cols.instance_type
        xul__bmgm = np.array(ifvn__fvi.meta, dtype=np.int64)
        yvz__vop['used_cols_glbl'] = xul__bmgm
        qmrd__ecjpz = set([table.block_nums[ucx__lny] for ucx__lny in
            xul__bmgm])
        phqg__cbgyc += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        phqg__cbgyc += f'  used_cols_set = None\n'
        xul__bmgm = None
    phqg__cbgyc += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for phebn__drfal in table.type_to_blk.values():
        phqg__cbgyc += f"""  blk_{phebn__drfal} = bodo.hiframes.table.get_table_block(table, {phebn__drfal})
"""
        if upnw__fbmet:
            phqg__cbgyc += f"""  out_list_{phebn__drfal} = bodo.hiframes.table.alloc_list_like(blk_{phebn__drfal}, len(blk_{phebn__drfal}), False)
"""
            bapj__rlv = f'out_list_{phebn__drfal}'
        else:
            bapj__rlv = 'out_list'
        if xul__bmgm is None or phebn__drfal in qmrd__ecjpz:
            phqg__cbgyc += f'  for i in range(len(blk_{phebn__drfal})):\n'
            yvz__vop[f'col_indices_{phebn__drfal}'] = np.array(table.
                block_to_arr_ind[phebn__drfal], dtype=np.int64)
            phqg__cbgyc += f'    col_loc = col_indices_{phebn__drfal}[i]\n'
            if xul__bmgm is not None:
                phqg__cbgyc += f'    if col_loc not in used_cols_set:\n'
                phqg__cbgyc += f'        continue\n'
            if upnw__fbmet:
                cafpm__hfu = 'i'
            else:
                cafpm__hfu = 'col_loc'
            if not irqbc__qqg:
                phqg__cbgyc += (
                    f'    {bapj__rlv}[{cafpm__hfu}] = blk_{phebn__drfal}[i]\n')
            elif yjnj__zwg:
                phqg__cbgyc += f"""    {bapj__rlv}[{cafpm__hfu}] = blk_{phebn__drfal}[i].{func_name}()
"""
            else:
                phqg__cbgyc += f"""    {bapj__rlv}[{cafpm__hfu}] = {func_name}(blk_{phebn__drfal}[i])
"""
        if upnw__fbmet:
            phqg__cbgyc += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {bapj__rlv}, {phebn__drfal})
"""
    if upnw__fbmet:
        phqg__cbgyc += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        phqg__cbgyc += '  return out_table\n'
    else:
        phqg__cbgyc += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    gyzku__rtmnh = {}
    exec(phqg__cbgyc, yvz__vop, gyzku__rtmnh)
    return gyzku__rtmnh['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    wzbf__mfqtc = args[0]
    if equiv_set.has_shape(wzbf__mfqtc):
        return ArrayAnalysis.AnalyzeResult(shape=wzbf__mfqtc, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    yvz__vop = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.distributed_api.
        Reduce_Type.Sum.value)}
    phqg__cbgyc = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    phqg__cbgyc += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for phebn__drfal in table.type_to_blk.values():
        phqg__cbgyc += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {phebn__drfal})\n'
            )
        yvz__vop[f'col_indices_{phebn__drfal}'] = np.array(table.
            block_to_arr_ind[phebn__drfal], dtype=np.int64)
        phqg__cbgyc += '  for i in range(len(blk)):\n'
        phqg__cbgyc += f'    col_loc = col_indices_{phebn__drfal}[i]\n'
        phqg__cbgyc += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    phqg__cbgyc += '  if parallel:\n'
    phqg__cbgyc += '    for i in range(start_offset, len(out_arr)):\n'
    phqg__cbgyc += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    gyzku__rtmnh = {}
    exec(phqg__cbgyc, yvz__vop, gyzku__rtmnh)
    return gyzku__rtmnh['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    xdqx__rrtl = table.type_to_blk[arr_type]
    yvz__vop = {'bodo': bodo}
    yvz__vop['col_indices'] = np.array(table.block_to_arr_ind[xdqx__rrtl],
        dtype=np.int64)
    ugwl__mstdg = col_nums_meta.instance_type
    yvz__vop['col_nums'] = np.array(ugwl__mstdg.meta, np.int64)
    phqg__cbgyc = 'def impl(table, col_nums_meta, arr_type):\n'
    phqg__cbgyc += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {xdqx__rrtl})\n')
    phqg__cbgyc += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    phqg__cbgyc += '  n = len(table)\n'
    dxq__wran = bodo.utils.typing.is_str_arr_type(arr_type)
    if dxq__wran:
        phqg__cbgyc += '  total_chars = 0\n'
        phqg__cbgyc += '  for c in col_nums:\n'
        phqg__cbgyc += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        phqg__cbgyc += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        phqg__cbgyc += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        phqg__cbgyc += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        phqg__cbgyc += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    phqg__cbgyc += '  for i in range(len(col_nums)):\n'
    phqg__cbgyc += '    c = col_nums[i]\n'
    if not dxq__wran:
        phqg__cbgyc += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    phqg__cbgyc += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    phqg__cbgyc += '    off = i * n\n'
    phqg__cbgyc += '    for j in range(len(arr)):\n'
    phqg__cbgyc += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    phqg__cbgyc += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    phqg__cbgyc += '      else:\n'
    phqg__cbgyc += '        out_arr[off+j] = arr[j]\n'
    phqg__cbgyc += '  return out_arr\n'
    afgr__sar = {}
    exec(phqg__cbgyc, yvz__vop, afgr__sar)
    uydv__lxqe = afgr__sar['impl']
    return uydv__lxqe


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    jphy__xmdp = not is_overload_false(copy)
    mnfz__qxrv = is_overload_true(copy)
    yvz__vop = {'bodo': bodo}
    afwpp__aryzw = table.arr_types
    lna__kelo = new_table_typ.arr_types
    ttpl__vlz: Set[int] = set()
    fjlj__ectz: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    ekxu__cjx: Set[types.Type] = set()
    for ucx__lny, vudnk__jbol in enumerate(afwpp__aryzw):
        rwv__aha = lna__kelo[ucx__lny]
        if vudnk__jbol == rwv__aha:
            ekxu__cjx.add(vudnk__jbol)
        else:
            ttpl__vlz.add(ucx__lny)
            fjlj__ectz[rwv__aha].add(vudnk__jbol)
    phqg__cbgyc = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    phqg__cbgyc += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    phqg__cbgyc += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    wdsdk__mhthn = set(range(len(afwpp__aryzw)))
    wan__srmfi = wdsdk__mhthn - ttpl__vlz
    if not is_overload_none(used_cols):
        ifvn__fvi = used_cols.instance_type
        jbhni__los = set(ifvn__fvi.meta)
        ttpl__vlz = ttpl__vlz & jbhni__los
        wan__srmfi = wan__srmfi & jbhni__los
        qmrd__ecjpz = set([table.block_nums[ucx__lny] for ucx__lny in
            jbhni__los])
    else:
        jbhni__los = None
    yvz__vop['cast_cols'] = np.array(list(ttpl__vlz), dtype=np.int64)
    yvz__vop['copied_cols'] = np.array(list(wan__srmfi), dtype=np.int64)
    phqg__cbgyc += f'  copied_cols_set = set(copied_cols)\n'
    phqg__cbgyc += f'  cast_cols_set = set(cast_cols)\n'
    for ufwr__hnncu, phebn__drfal in new_table_typ.type_to_blk.items():
        yvz__vop[f'typ_list_{phebn__drfal}'] = types.List(ufwr__hnncu)
        phqg__cbgyc += f"""  out_arr_list_{phebn__drfal} = bodo.hiframes.table.alloc_list_like(typ_list_{phebn__drfal}, {len(new_table_typ.block_to_arr_ind[phebn__drfal])}, False)
"""
        if ufwr__hnncu in ekxu__cjx:
            gqwc__ibio = table.type_to_blk[ufwr__hnncu]
            if jbhni__los is None or gqwc__ibio in qmrd__ecjpz:
                che__jhsa = table.block_to_arr_ind[gqwc__ibio]
                bwtpj__nmij = [new_table_typ.block_offsets[jggsr__wpg] for
                    jggsr__wpg in che__jhsa]
                yvz__vop[f'new_idx_{gqwc__ibio}'] = np.array(bwtpj__nmij,
                    np.int64)
                yvz__vop[f'orig_arr_inds_{gqwc__ibio}'] = np.array(che__jhsa,
                    np.int64)
                phqg__cbgyc += f"""  arr_list_{gqwc__ibio} = bodo.hiframes.table.get_table_block(table, {gqwc__ibio})
"""
                phqg__cbgyc += (
                    f'  for i in range(len(arr_list_{gqwc__ibio})):\n')
                phqg__cbgyc += (
                    f'    arr_ind_{gqwc__ibio} = orig_arr_inds_{gqwc__ibio}[i]\n'
                    )
                phqg__cbgyc += (
                    f'    if arr_ind_{gqwc__ibio} not in copied_cols_set:\n')
                phqg__cbgyc += f'      continue\n'
                phqg__cbgyc += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{gqwc__ibio}, i, arr_ind_{gqwc__ibio})
"""
                phqg__cbgyc += f"""    out_idx_{phebn__drfal}_{gqwc__ibio} = new_idx_{gqwc__ibio}[i]
"""
                phqg__cbgyc += (
                    f'    arr_val_{gqwc__ibio} = arr_list_{gqwc__ibio}[i]\n')
                if mnfz__qxrv:
                    phqg__cbgyc += (
                        f'    arr_val_{gqwc__ibio} = arr_val_{gqwc__ibio}.copy()\n'
                        )
                elif jphy__xmdp:
                    phqg__cbgyc += f"""    arr_val_{gqwc__ibio} = arr_val_{gqwc__ibio}.copy() if copy else arr_val_{phebn__drfal}
"""
                phqg__cbgyc += f"""    out_arr_list_{phebn__drfal}[out_idx_{phebn__drfal}_{gqwc__ibio}] = arr_val_{gqwc__ibio}
"""
    xwj__lnge = set()
    for ufwr__hnncu, phebn__drfal in new_table_typ.type_to_blk.items():
        if ufwr__hnncu in fjlj__ectz:
            if isinstance(ufwr__hnncu, bodo.IntegerArrayType):
                xzoj__tzd = ufwr__hnncu.get_pandas_scalar_type_instance.name
            else:
                xzoj__tzd = ufwr__hnncu.dtype
            yvz__vop[f'typ_{phebn__drfal}'] = xzoj__tzd
            ung__utkr = fjlj__ectz[ufwr__hnncu]
            for aqy__qqf in ung__utkr:
                gqwc__ibio = table.type_to_blk[aqy__qqf]
                if jbhni__los is None or gqwc__ibio in qmrd__ecjpz:
                    if aqy__qqf not in ekxu__cjx and aqy__qqf not in xwj__lnge:
                        che__jhsa = table.block_to_arr_ind[gqwc__ibio]
                        bwtpj__nmij = [new_table_typ.block_offsets[
                            jggsr__wpg] for jggsr__wpg in che__jhsa]
                        yvz__vop[f'new_idx_{gqwc__ibio}'] = np.array(
                            bwtpj__nmij, np.int64)
                        yvz__vop[f'orig_arr_inds_{gqwc__ibio}'] = np.array(
                            che__jhsa, np.int64)
                        phqg__cbgyc += f"""  arr_list_{gqwc__ibio} = bodo.hiframes.table.get_table_block(table, {gqwc__ibio})
"""
                    xwj__lnge.add(aqy__qqf)
                    phqg__cbgyc += (
                        f'  for i in range(len(arr_list_{gqwc__ibio})):\n')
                    phqg__cbgyc += (
                        f'    arr_ind_{gqwc__ibio} = orig_arr_inds_{gqwc__ibio}[i]\n'
                        )
                    phqg__cbgyc += (
                        f'    if arr_ind_{gqwc__ibio} not in cast_cols_set:\n')
                    phqg__cbgyc += f'      continue\n'
                    phqg__cbgyc += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{gqwc__ibio}, i, arr_ind_{gqwc__ibio})
"""
                    phqg__cbgyc += f"""    out_idx_{phebn__drfal}_{gqwc__ibio} = new_idx_{gqwc__ibio}[i]
"""
                    phqg__cbgyc += f"""    arr_val_{phebn__drfal} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{gqwc__ibio}[i], typ_{phebn__drfal}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    phqg__cbgyc += f"""    out_arr_list_{phebn__drfal}[out_idx_{phebn__drfal}_{gqwc__ibio}] = arr_val_{phebn__drfal}
"""
        phqg__cbgyc += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{phebn__drfal}, {phebn__drfal})
"""
    phqg__cbgyc += '  return out_table\n'
    gyzku__rtmnh = {}
    exec(phqg__cbgyc, yvz__vop, gyzku__rtmnh)
    return gyzku__rtmnh['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    wzbf__mfqtc = args[0]
    if equiv_set.has_shape(wzbf__mfqtc):
        return ArrayAnalysis.AnalyzeResult(shape=wzbf__mfqtc, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
