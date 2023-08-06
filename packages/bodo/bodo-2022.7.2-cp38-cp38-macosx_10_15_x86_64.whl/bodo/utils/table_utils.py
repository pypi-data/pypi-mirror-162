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
    wlikj__kzu = not is_overload_none(func_name)
    if wlikj__kzu:
        func_name = get_overload_const_str(func_name)
        xzoh__lnm = get_overload_const_bool(is_method)
    xexi__njx = out_arr_typ.instance_type if isinstance(out_arr_typ, types.
        TypeRef) else out_arr_typ
    uul__hbb = xexi__njx == types.none
    huko__fvan = len(table.arr_types)
    if uul__hbb:
        wokyx__fzelk = table
    else:
        wce__rlp = tuple([xexi__njx] * huko__fvan)
        wokyx__fzelk = TableType(wce__rlp)
    zsdwb__tdjwx = {'bodo': bodo, 'lst_dtype': xexi__njx, 'table_typ':
        wokyx__fzelk}
    dsvkd__xtb = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if uul__hbb:
        dsvkd__xtb += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        dsvkd__xtb += f'  l = len(table)\n'
    else:
        dsvkd__xtb += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({huko__fvan}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        gjayu__zja = used_cols.instance_type
        ktiub__udxft = np.array(gjayu__zja.meta, dtype=np.int64)
        zsdwb__tdjwx['used_cols_glbl'] = ktiub__udxft
        soxjb__uvg = set([table.block_nums[nqq__kibuc] for nqq__kibuc in
            ktiub__udxft])
        dsvkd__xtb += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        dsvkd__xtb += f'  used_cols_set = None\n'
        ktiub__udxft = None
    dsvkd__xtb += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for rrjj__bwb in table.type_to_blk.values():
        dsvkd__xtb += f"""  blk_{rrjj__bwb} = bodo.hiframes.table.get_table_block(table, {rrjj__bwb})
"""
        if uul__hbb:
            dsvkd__xtb += f"""  out_list_{rrjj__bwb} = bodo.hiframes.table.alloc_list_like(blk_{rrjj__bwb}, len(blk_{rrjj__bwb}), False)
"""
            uly__xhvav = f'out_list_{rrjj__bwb}'
        else:
            uly__xhvav = 'out_list'
        if ktiub__udxft is None or rrjj__bwb in soxjb__uvg:
            dsvkd__xtb += f'  for i in range(len(blk_{rrjj__bwb})):\n'
            zsdwb__tdjwx[f'col_indices_{rrjj__bwb}'] = np.array(table.
                block_to_arr_ind[rrjj__bwb], dtype=np.int64)
            dsvkd__xtb += f'    col_loc = col_indices_{rrjj__bwb}[i]\n'
            if ktiub__udxft is not None:
                dsvkd__xtb += f'    if col_loc not in used_cols_set:\n'
                dsvkd__xtb += f'        continue\n'
            if uul__hbb:
                urnc__gqafl = 'i'
            else:
                urnc__gqafl = 'col_loc'
            if not wlikj__kzu:
                dsvkd__xtb += (
                    f'    {uly__xhvav}[{urnc__gqafl}] = blk_{rrjj__bwb}[i]\n')
            elif xzoh__lnm:
                dsvkd__xtb += f"""    {uly__xhvav}[{urnc__gqafl}] = blk_{rrjj__bwb}[i].{func_name}()
"""
            else:
                dsvkd__xtb += (
                    f'    {uly__xhvav}[{urnc__gqafl}] = {func_name}(blk_{rrjj__bwb}[i])\n'
                    )
        if uul__hbb:
            dsvkd__xtb += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {uly__xhvav}, {rrjj__bwb})
"""
    if uul__hbb:
        dsvkd__xtb += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        dsvkd__xtb += '  return out_table\n'
    else:
        dsvkd__xtb += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    nbz__bjk = {}
    exec(dsvkd__xtb, zsdwb__tdjwx, nbz__bjk)
    return nbz__bjk['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    ngdzc__swkuk = args[0]
    if equiv_set.has_shape(ngdzc__swkuk):
        return ArrayAnalysis.AnalyzeResult(shape=ngdzc__swkuk, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    zsdwb__tdjwx = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    dsvkd__xtb = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    dsvkd__xtb += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for rrjj__bwb in table.type_to_blk.values():
        dsvkd__xtb += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {rrjj__bwb})\n'
            )
        zsdwb__tdjwx[f'col_indices_{rrjj__bwb}'] = np.array(table.
            block_to_arr_ind[rrjj__bwb], dtype=np.int64)
        dsvkd__xtb += '  for i in range(len(blk)):\n'
        dsvkd__xtb += f'    col_loc = col_indices_{rrjj__bwb}[i]\n'
        dsvkd__xtb += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    dsvkd__xtb += '  if parallel:\n'
    dsvkd__xtb += '    for i in range(start_offset, len(out_arr)):\n'
    dsvkd__xtb += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    nbz__bjk = {}
    exec(dsvkd__xtb, zsdwb__tdjwx, nbz__bjk)
    return nbz__bjk['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    ufn__bhzrj = table.type_to_blk[arr_type]
    zsdwb__tdjwx = {'bodo': bodo}
    zsdwb__tdjwx['col_indices'] = np.array(table.block_to_arr_ind[
        ufn__bhzrj], dtype=np.int64)
    fqmq__nqab = col_nums_meta.instance_type
    zsdwb__tdjwx['col_nums'] = np.array(fqmq__nqab.meta, np.int64)
    dsvkd__xtb = 'def impl(table, col_nums_meta, arr_type):\n'
    dsvkd__xtb += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {ufn__bhzrj})\n')
    dsvkd__xtb += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    dsvkd__xtb += '  n = len(table)\n'
    ijwpf__qon = bodo.utils.typing.is_str_arr_type(arr_type)
    if ijwpf__qon:
        dsvkd__xtb += '  total_chars = 0\n'
        dsvkd__xtb += '  for c in col_nums:\n'
        dsvkd__xtb += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        dsvkd__xtb += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        dsvkd__xtb += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        dsvkd__xtb += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        dsvkd__xtb += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    dsvkd__xtb += '  for i in range(len(col_nums)):\n'
    dsvkd__xtb += '    c = col_nums[i]\n'
    if not ijwpf__qon:
        dsvkd__xtb += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    dsvkd__xtb += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    dsvkd__xtb += '    off = i * n\n'
    dsvkd__xtb += '    for j in range(len(arr)):\n'
    dsvkd__xtb += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    dsvkd__xtb += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    dsvkd__xtb += '      else:\n'
    dsvkd__xtb += '        out_arr[off+j] = arr[j]\n'
    dsvkd__xtb += '  return out_arr\n'
    lvwh__ngzcm = {}
    exec(dsvkd__xtb, zsdwb__tdjwx, lvwh__ngzcm)
    ryip__yas = lvwh__ngzcm['impl']
    return ryip__yas


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    wtxq__sibd = not is_overload_false(copy)
    hdmr__zuc = is_overload_true(copy)
    zsdwb__tdjwx = {'bodo': bodo}
    yewmy__htowv = table.arr_types
    xgd__ijaew = new_table_typ.arr_types
    uosfu__jnlw: Set[int] = set()
    umzho__zci: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    tlyz__axlw: Set[types.Type] = set()
    for nqq__kibuc, xwmu__euy in enumerate(yewmy__htowv):
        dlfe__pmc = xgd__ijaew[nqq__kibuc]
        if xwmu__euy == dlfe__pmc:
            tlyz__axlw.add(xwmu__euy)
        else:
            uosfu__jnlw.add(nqq__kibuc)
            umzho__zci[dlfe__pmc].add(xwmu__euy)
    dsvkd__xtb = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    dsvkd__xtb += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    dsvkd__xtb += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    ccjjb__yymvz = set(range(len(yewmy__htowv)))
    oip__wys = ccjjb__yymvz - uosfu__jnlw
    if not is_overload_none(used_cols):
        gjayu__zja = used_cols.instance_type
        gedd__wwwe = set(gjayu__zja.meta)
        uosfu__jnlw = uosfu__jnlw & gedd__wwwe
        oip__wys = oip__wys & gedd__wwwe
        soxjb__uvg = set([table.block_nums[nqq__kibuc] for nqq__kibuc in
            gedd__wwwe])
    else:
        gedd__wwwe = None
    zsdwb__tdjwx['cast_cols'] = np.array(list(uosfu__jnlw), dtype=np.int64)
    zsdwb__tdjwx['copied_cols'] = np.array(list(oip__wys), dtype=np.int64)
    dsvkd__xtb += f'  copied_cols_set = set(copied_cols)\n'
    dsvkd__xtb += f'  cast_cols_set = set(cast_cols)\n'
    for njyi__wqvfu, rrjj__bwb in new_table_typ.type_to_blk.items():
        zsdwb__tdjwx[f'typ_list_{rrjj__bwb}'] = types.List(njyi__wqvfu)
        dsvkd__xtb += f"""  out_arr_list_{rrjj__bwb} = bodo.hiframes.table.alloc_list_like(typ_list_{rrjj__bwb}, {len(new_table_typ.block_to_arr_ind[rrjj__bwb])}, False)
"""
        if njyi__wqvfu in tlyz__axlw:
            sjlie__hjxu = table.type_to_blk[njyi__wqvfu]
            if gedd__wwwe is None or sjlie__hjxu in soxjb__uvg:
                rsk__jujtd = table.block_to_arr_ind[sjlie__hjxu]
                vwh__okrke = [new_table_typ.block_offsets[osuq__gty] for
                    osuq__gty in rsk__jujtd]
                zsdwb__tdjwx[f'new_idx_{sjlie__hjxu}'] = np.array(vwh__okrke,
                    np.int64)
                zsdwb__tdjwx[f'orig_arr_inds_{sjlie__hjxu}'] = np.array(
                    rsk__jujtd, np.int64)
                dsvkd__xtb += f"""  arr_list_{sjlie__hjxu} = bodo.hiframes.table.get_table_block(table, {sjlie__hjxu})
"""
                dsvkd__xtb += (
                    f'  for i in range(len(arr_list_{sjlie__hjxu})):\n')
                dsvkd__xtb += (
                    f'    arr_ind_{sjlie__hjxu} = orig_arr_inds_{sjlie__hjxu}[i]\n'
                    )
                dsvkd__xtb += (
                    f'    if arr_ind_{sjlie__hjxu} not in copied_cols_set:\n')
                dsvkd__xtb += f'      continue\n'
                dsvkd__xtb += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{sjlie__hjxu}, i, arr_ind_{sjlie__hjxu})
"""
                dsvkd__xtb += (
                    f'    out_idx_{rrjj__bwb}_{sjlie__hjxu} = new_idx_{sjlie__hjxu}[i]\n'
                    )
                dsvkd__xtb += (
                    f'    arr_val_{sjlie__hjxu} = arr_list_{sjlie__hjxu}[i]\n')
                if hdmr__zuc:
                    dsvkd__xtb += (
                        f'    arr_val_{sjlie__hjxu} = arr_val_{sjlie__hjxu}.copy()\n'
                        )
                elif wtxq__sibd:
                    dsvkd__xtb += f"""    arr_val_{sjlie__hjxu} = arr_val_{sjlie__hjxu}.copy() if copy else arr_val_{rrjj__bwb}
"""
                dsvkd__xtb += f"""    out_arr_list_{rrjj__bwb}[out_idx_{rrjj__bwb}_{sjlie__hjxu}] = arr_val_{sjlie__hjxu}
"""
    krruf__xfpqy = set()
    for njyi__wqvfu, rrjj__bwb in new_table_typ.type_to_blk.items():
        if njyi__wqvfu in umzho__zci:
            if isinstance(njyi__wqvfu, bodo.IntegerArrayType):
                zqmq__mbaa = njyi__wqvfu.get_pandas_scalar_type_instance.name
            else:
                zqmq__mbaa = njyi__wqvfu.dtype
            zsdwb__tdjwx[f'typ_{rrjj__bwb}'] = zqmq__mbaa
            iac__gomf = umzho__zci[njyi__wqvfu]
            for ign__pois in iac__gomf:
                sjlie__hjxu = table.type_to_blk[ign__pois]
                if gedd__wwwe is None or sjlie__hjxu in soxjb__uvg:
                    if (ign__pois not in tlyz__axlw and ign__pois not in
                        krruf__xfpqy):
                        rsk__jujtd = table.block_to_arr_ind[sjlie__hjxu]
                        vwh__okrke = [new_table_typ.block_offsets[osuq__gty
                            ] for osuq__gty in rsk__jujtd]
                        zsdwb__tdjwx[f'new_idx_{sjlie__hjxu}'] = np.array(
                            vwh__okrke, np.int64)
                        zsdwb__tdjwx[f'orig_arr_inds_{sjlie__hjxu}'
                            ] = np.array(rsk__jujtd, np.int64)
                        dsvkd__xtb += f"""  arr_list_{sjlie__hjxu} = bodo.hiframes.table.get_table_block(table, {sjlie__hjxu})
"""
                    krruf__xfpqy.add(ign__pois)
                    dsvkd__xtb += (
                        f'  for i in range(len(arr_list_{sjlie__hjxu})):\n')
                    dsvkd__xtb += (
                        f'    arr_ind_{sjlie__hjxu} = orig_arr_inds_{sjlie__hjxu}[i]\n'
                        )
                    dsvkd__xtb += (
                        f'    if arr_ind_{sjlie__hjxu} not in cast_cols_set:\n'
                        )
                    dsvkd__xtb += f'      continue\n'
                    dsvkd__xtb += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{sjlie__hjxu}, i, arr_ind_{sjlie__hjxu})
"""
                    dsvkd__xtb += f"""    out_idx_{rrjj__bwb}_{sjlie__hjxu} = new_idx_{sjlie__hjxu}[i]
"""
                    dsvkd__xtb += f"""    arr_val_{rrjj__bwb} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{sjlie__hjxu}[i], typ_{rrjj__bwb}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    dsvkd__xtb += f"""    out_arr_list_{rrjj__bwb}[out_idx_{rrjj__bwb}_{sjlie__hjxu}] = arr_val_{rrjj__bwb}
"""
        dsvkd__xtb += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{rrjj__bwb}, {rrjj__bwb})
"""
    dsvkd__xtb += '  return out_table\n'
    nbz__bjk = {}
    exec(dsvkd__xtb, zsdwb__tdjwx, nbz__bjk)
    return nbz__bjk['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    ngdzc__swkuk = args[0]
    if equiv_set.has_shape(ngdzc__swkuk):
        return ArrayAnalysis.AnalyzeResult(shape=ngdzc__swkuk, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
