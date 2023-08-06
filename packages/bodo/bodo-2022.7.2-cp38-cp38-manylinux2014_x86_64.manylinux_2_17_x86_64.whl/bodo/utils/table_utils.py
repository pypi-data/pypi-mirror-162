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
    cge__xnmy = not is_overload_none(func_name)
    if cge__xnmy:
        func_name = get_overload_const_str(func_name)
        jru__zfiob = get_overload_const_bool(is_method)
    jrs__nucib = out_arr_typ.instance_type if isinstance(out_arr_typ, types
        .TypeRef) else out_arr_typ
    grdna__ufo = jrs__nucib == types.none
    ziihj__vsj = len(table.arr_types)
    if grdna__ufo:
        nhsn__iqtx = table
    else:
        naa__qom = tuple([jrs__nucib] * ziihj__vsj)
        nhsn__iqtx = TableType(naa__qom)
    hhn__vlts = {'bodo': bodo, 'lst_dtype': jrs__nucib, 'table_typ': nhsn__iqtx
        }
    ezg__ryym = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if grdna__ufo:
        ezg__ryym += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        ezg__ryym += f'  l = len(table)\n'
    else:
        ezg__ryym += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({ziihj__vsj}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        vktj__wfceg = used_cols.instance_type
        ymhze__obh = np.array(vktj__wfceg.meta, dtype=np.int64)
        hhn__vlts['used_cols_glbl'] = ymhze__obh
        cyi__dfr = set([table.block_nums[usuj__hwfyz] for usuj__hwfyz in
            ymhze__obh])
        ezg__ryym += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        ezg__ryym += f'  used_cols_set = None\n'
        ymhze__obh = None
    ezg__ryym += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for kja__xidr in table.type_to_blk.values():
        ezg__ryym += f"""  blk_{kja__xidr} = bodo.hiframes.table.get_table_block(table, {kja__xidr})
"""
        if grdna__ufo:
            ezg__ryym += f"""  out_list_{kja__xidr} = bodo.hiframes.table.alloc_list_like(blk_{kja__xidr}, len(blk_{kja__xidr}), False)
"""
            rfy__hmf = f'out_list_{kja__xidr}'
        else:
            rfy__hmf = 'out_list'
        if ymhze__obh is None or kja__xidr in cyi__dfr:
            ezg__ryym += f'  for i in range(len(blk_{kja__xidr})):\n'
            hhn__vlts[f'col_indices_{kja__xidr}'] = np.array(table.
                block_to_arr_ind[kja__xidr], dtype=np.int64)
            ezg__ryym += f'    col_loc = col_indices_{kja__xidr}[i]\n'
            if ymhze__obh is not None:
                ezg__ryym += f'    if col_loc not in used_cols_set:\n'
                ezg__ryym += f'        continue\n'
            if grdna__ufo:
                qhx__yyfz = 'i'
            else:
                qhx__yyfz = 'col_loc'
            if not cge__xnmy:
                ezg__ryym += (
                    f'    {rfy__hmf}[{qhx__yyfz}] = blk_{kja__xidr}[i]\n')
            elif jru__zfiob:
                ezg__ryym += (
                    f'    {rfy__hmf}[{qhx__yyfz}] = blk_{kja__xidr}[i].{func_name}()\n'
                    )
            else:
                ezg__ryym += (
                    f'    {rfy__hmf}[{qhx__yyfz}] = {func_name}(blk_{kja__xidr}[i])\n'
                    )
        if grdna__ufo:
            ezg__ryym += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {rfy__hmf}, {kja__xidr})
"""
    if grdna__ufo:
        ezg__ryym += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        ezg__ryym += '  return out_table\n'
    else:
        ezg__ryym += (
            '  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)\n'
            )
    tzsg__oyuvo = {}
    exec(ezg__ryym, hhn__vlts, tzsg__oyuvo)
    return tzsg__oyuvo['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    wswqy__psjnu = args[0]
    if equiv_set.has_shape(wswqy__psjnu):
        return ArrayAnalysis.AnalyzeResult(shape=wswqy__psjnu, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    hhn__vlts = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.distributed_api
        .Reduce_Type.Sum.value)}
    ezg__ryym = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    ezg__ryym += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for kja__xidr in table.type_to_blk.values():
        ezg__ryym += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {kja__xidr})\n'
            )
        hhn__vlts[f'col_indices_{kja__xidr}'] = np.array(table.
            block_to_arr_ind[kja__xidr], dtype=np.int64)
        ezg__ryym += '  for i in range(len(blk)):\n'
        ezg__ryym += f'    col_loc = col_indices_{kja__xidr}[i]\n'
        ezg__ryym += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    ezg__ryym += '  if parallel:\n'
    ezg__ryym += '    for i in range(start_offset, len(out_arr)):\n'
    ezg__ryym += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    tzsg__oyuvo = {}
    exec(ezg__ryym, hhn__vlts, tzsg__oyuvo)
    return tzsg__oyuvo['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    you__qpoio = table.type_to_blk[arr_type]
    hhn__vlts = {'bodo': bodo}
    hhn__vlts['col_indices'] = np.array(table.block_to_arr_ind[you__qpoio],
        dtype=np.int64)
    wxqiq__llvo = col_nums_meta.instance_type
    hhn__vlts['col_nums'] = np.array(wxqiq__llvo.meta, np.int64)
    ezg__ryym = 'def impl(table, col_nums_meta, arr_type):\n'
    ezg__ryym += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {you__qpoio})\n')
    ezg__ryym += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    ezg__ryym += '  n = len(table)\n'
    saot__thk = bodo.utils.typing.is_str_arr_type(arr_type)
    if saot__thk:
        ezg__ryym += '  total_chars = 0\n'
        ezg__ryym += '  for c in col_nums:\n'
        ezg__ryym += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        ezg__ryym += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        ezg__ryym += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        ezg__ryym += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        ezg__ryym += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    ezg__ryym += '  for i in range(len(col_nums)):\n'
    ezg__ryym += '    c = col_nums[i]\n'
    if not saot__thk:
        ezg__ryym += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    ezg__ryym += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    ezg__ryym += '    off = i * n\n'
    ezg__ryym += '    for j in range(len(arr)):\n'
    ezg__ryym += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    ezg__ryym += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    ezg__ryym += '      else:\n'
    ezg__ryym += '        out_arr[off+j] = arr[j]\n'
    ezg__ryym += '  return out_arr\n'
    caw__ymym = {}
    exec(ezg__ryym, hhn__vlts, caw__ymym)
    fadsz__pbpyq = caw__ymym['impl']
    return fadsz__pbpyq


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    wstc__ifbl = not is_overload_false(copy)
    hdrwu__twju = is_overload_true(copy)
    hhn__vlts = {'bodo': bodo}
    udurs__ftrzp = table.arr_types
    mmpix__xkl = new_table_typ.arr_types
    hksuc__sdkdw: Set[int] = set()
    syuj__edvkx: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    becu__gvw: Set[types.Type] = set()
    for usuj__hwfyz, ngsl__wsp in enumerate(udurs__ftrzp):
        rfla__iwudi = mmpix__xkl[usuj__hwfyz]
        if ngsl__wsp == rfla__iwudi:
            becu__gvw.add(ngsl__wsp)
        else:
            hksuc__sdkdw.add(usuj__hwfyz)
            syuj__edvkx[rfla__iwudi].add(ngsl__wsp)
    ezg__ryym = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    ezg__ryym += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    ezg__ryym += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    ojyk__zra = set(range(len(udurs__ftrzp)))
    acijp__ybjjv = ojyk__zra - hksuc__sdkdw
    if not is_overload_none(used_cols):
        vktj__wfceg = used_cols.instance_type
        ybk__npb = set(vktj__wfceg.meta)
        hksuc__sdkdw = hksuc__sdkdw & ybk__npb
        acijp__ybjjv = acijp__ybjjv & ybk__npb
        cyi__dfr = set([table.block_nums[usuj__hwfyz] for usuj__hwfyz in
            ybk__npb])
    else:
        ybk__npb = None
    hhn__vlts['cast_cols'] = np.array(list(hksuc__sdkdw), dtype=np.int64)
    hhn__vlts['copied_cols'] = np.array(list(acijp__ybjjv), dtype=np.int64)
    ezg__ryym += f'  copied_cols_set = set(copied_cols)\n'
    ezg__ryym += f'  cast_cols_set = set(cast_cols)\n'
    for bdu__ycqq, kja__xidr in new_table_typ.type_to_blk.items():
        hhn__vlts[f'typ_list_{kja__xidr}'] = types.List(bdu__ycqq)
        ezg__ryym += f"""  out_arr_list_{kja__xidr} = bodo.hiframes.table.alloc_list_like(typ_list_{kja__xidr}, {len(new_table_typ.block_to_arr_ind[kja__xidr])}, False)
"""
        if bdu__ycqq in becu__gvw:
            lmy__rqr = table.type_to_blk[bdu__ycqq]
            if ybk__npb is None or lmy__rqr in cyi__dfr:
                lrih__cqmvz = table.block_to_arr_ind[lmy__rqr]
                kbqs__cvfpi = [new_table_typ.block_offsets[yaewg__iwl] for
                    yaewg__iwl in lrih__cqmvz]
                hhn__vlts[f'new_idx_{lmy__rqr}'] = np.array(kbqs__cvfpi, np
                    .int64)
                hhn__vlts[f'orig_arr_inds_{lmy__rqr}'] = np.array(lrih__cqmvz,
                    np.int64)
                ezg__ryym += f"""  arr_list_{lmy__rqr} = bodo.hiframes.table.get_table_block(table, {lmy__rqr})
"""
                ezg__ryym += f'  for i in range(len(arr_list_{lmy__rqr})):\n'
                ezg__ryym += (
                    f'    arr_ind_{lmy__rqr} = orig_arr_inds_{lmy__rqr}[i]\n')
                ezg__ryym += (
                    f'    if arr_ind_{lmy__rqr} not in copied_cols_set:\n')
                ezg__ryym += f'      continue\n'
                ezg__ryym += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{lmy__rqr}, i, arr_ind_{lmy__rqr})
"""
                ezg__ryym += (
                    f'    out_idx_{kja__xidr}_{lmy__rqr} = new_idx_{lmy__rqr}[i]\n'
                    )
                ezg__ryym += (
                    f'    arr_val_{lmy__rqr} = arr_list_{lmy__rqr}[i]\n')
                if hdrwu__twju:
                    ezg__ryym += (
                        f'    arr_val_{lmy__rqr} = arr_val_{lmy__rqr}.copy()\n'
                        )
                elif wstc__ifbl:
                    ezg__ryym += f"""    arr_val_{lmy__rqr} = arr_val_{lmy__rqr}.copy() if copy else arr_val_{kja__xidr}
"""
                ezg__ryym += f"""    out_arr_list_{kja__xidr}[out_idx_{kja__xidr}_{lmy__rqr}] = arr_val_{lmy__rqr}
"""
    jpf__xsf = set()
    for bdu__ycqq, kja__xidr in new_table_typ.type_to_blk.items():
        if bdu__ycqq in syuj__edvkx:
            if isinstance(bdu__ycqq, bodo.IntegerArrayType):
                aark__mmpwu = bdu__ycqq.get_pandas_scalar_type_instance.name
            else:
                aark__mmpwu = bdu__ycqq.dtype
            hhn__vlts[f'typ_{kja__xidr}'] = aark__mmpwu
            rdir__xvtpg = syuj__edvkx[bdu__ycqq]
            for rkmu__pseg in rdir__xvtpg:
                lmy__rqr = table.type_to_blk[rkmu__pseg]
                if ybk__npb is None or lmy__rqr in cyi__dfr:
                    if (rkmu__pseg not in becu__gvw and rkmu__pseg not in
                        jpf__xsf):
                        lrih__cqmvz = table.block_to_arr_ind[lmy__rqr]
                        kbqs__cvfpi = [new_table_typ.block_offsets[
                            yaewg__iwl] for yaewg__iwl in lrih__cqmvz]
                        hhn__vlts[f'new_idx_{lmy__rqr}'] = np.array(kbqs__cvfpi
                            , np.int64)
                        hhn__vlts[f'orig_arr_inds_{lmy__rqr}'] = np.array(
                            lrih__cqmvz, np.int64)
                        ezg__ryym += f"""  arr_list_{lmy__rqr} = bodo.hiframes.table.get_table_block(table, {lmy__rqr})
"""
                    jpf__xsf.add(rkmu__pseg)
                    ezg__ryym += (
                        f'  for i in range(len(arr_list_{lmy__rqr})):\n')
                    ezg__ryym += (
                        f'    arr_ind_{lmy__rqr} = orig_arr_inds_{lmy__rqr}[i]\n'
                        )
                    ezg__ryym += (
                        f'    if arr_ind_{lmy__rqr} not in cast_cols_set:\n')
                    ezg__ryym += f'      continue\n'
                    ezg__ryym += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{lmy__rqr}, i, arr_ind_{lmy__rqr})
"""
                    ezg__ryym += (
                        f'    out_idx_{kja__xidr}_{lmy__rqr} = new_idx_{lmy__rqr}[i]\n'
                        )
                    ezg__ryym += f"""    arr_val_{kja__xidr} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{lmy__rqr}[i], typ_{kja__xidr}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    ezg__ryym += f"""    out_arr_list_{kja__xidr}[out_idx_{kja__xidr}_{lmy__rqr}] = arr_val_{kja__xidr}
"""
        ezg__ryym += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{kja__xidr}, {kja__xidr})
"""
    ezg__ryym += '  return out_table\n'
    tzsg__oyuvo = {}
    exec(ezg__ryym, hhn__vlts, tzsg__oyuvo)
    return tzsg__oyuvo['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    wswqy__psjnu = args[0]
    if equiv_set.has_shape(wswqy__psjnu):
        return ArrayAnalysis.AnalyzeResult(shape=wswqy__psjnu, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
