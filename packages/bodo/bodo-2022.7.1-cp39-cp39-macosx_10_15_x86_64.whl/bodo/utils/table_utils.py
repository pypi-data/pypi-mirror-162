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
    cza__qpou = not is_overload_none(func_name)
    if cza__qpou:
        func_name = get_overload_const_str(func_name)
        lbflz__eaoiq = get_overload_const_bool(is_method)
    elxh__uzjvr = out_arr_typ.instance_type if isinstance(out_arr_typ,
        types.TypeRef) else out_arr_typ
    onzvv__mqm = elxh__uzjvr == types.none
    zjp__jdb = len(table.arr_types)
    if onzvv__mqm:
        puj__nrys = table
    else:
        bpgmi__sxltr = tuple([elxh__uzjvr] * zjp__jdb)
        puj__nrys = TableType(bpgmi__sxltr)
    jjdq__jeksi = {'bodo': bodo, 'lst_dtype': elxh__uzjvr, 'table_typ':
        puj__nrys}
    uvkge__wij = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if onzvv__mqm:
        uvkge__wij += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        uvkge__wij += f'  l = len(table)\n'
    else:
        uvkge__wij += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({zjp__jdb}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        nohdw__ktnj = used_cols.instance_type
        znt__renly = np.array(nohdw__ktnj.meta, dtype=np.int64)
        jjdq__jeksi['used_cols_glbl'] = znt__renly
        kgsix__ozij = set([table.block_nums[lnmvr__ddlud] for lnmvr__ddlud in
            znt__renly])
        uvkge__wij += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        uvkge__wij += f'  used_cols_set = None\n'
        znt__renly = None
    uvkge__wij += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for ehgu__getp in table.type_to_blk.values():
        uvkge__wij += f"""  blk_{ehgu__getp} = bodo.hiframes.table.get_table_block(table, {ehgu__getp})
"""
        if onzvv__mqm:
            uvkge__wij += f"""  out_list_{ehgu__getp} = bodo.hiframes.table.alloc_list_like(blk_{ehgu__getp}, len(blk_{ehgu__getp}), False)
"""
            cmf__gvuft = f'out_list_{ehgu__getp}'
        else:
            cmf__gvuft = 'out_list'
        if znt__renly is None or ehgu__getp in kgsix__ozij:
            uvkge__wij += f'  for i in range(len(blk_{ehgu__getp})):\n'
            jjdq__jeksi[f'col_indices_{ehgu__getp}'] = np.array(table.
                block_to_arr_ind[ehgu__getp], dtype=np.int64)
            uvkge__wij += f'    col_loc = col_indices_{ehgu__getp}[i]\n'
            if znt__renly is not None:
                uvkge__wij += f'    if col_loc not in used_cols_set:\n'
                uvkge__wij += f'        continue\n'
            if onzvv__mqm:
                rsff__qpyy = 'i'
            else:
                rsff__qpyy = 'col_loc'
            if not cza__qpou:
                uvkge__wij += (
                    f'    {cmf__gvuft}[{rsff__qpyy}] = blk_{ehgu__getp}[i]\n')
            elif lbflz__eaoiq:
                uvkge__wij += f"""    {cmf__gvuft}[{rsff__qpyy}] = blk_{ehgu__getp}[i].{func_name}()
"""
            else:
                uvkge__wij += (
                    f'    {cmf__gvuft}[{rsff__qpyy}] = {func_name}(blk_{ehgu__getp}[i])\n'
                    )
        if onzvv__mqm:
            uvkge__wij += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {cmf__gvuft}, {ehgu__getp})
"""
    if onzvv__mqm:
        uvkge__wij += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        uvkge__wij += '  return out_table\n'
    else:
        uvkge__wij += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    lcna__cxmbs = {}
    exec(uvkge__wij, jjdq__jeksi, lcna__cxmbs)
    return lcna__cxmbs['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    ykcay__rut = args[0]
    if equiv_set.has_shape(ykcay__rut):
        return ArrayAnalysis.AnalyzeResult(shape=ykcay__rut, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    jjdq__jeksi = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    uvkge__wij = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    uvkge__wij += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for ehgu__getp in table.type_to_blk.values():
        uvkge__wij += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {ehgu__getp})\n'
            )
        jjdq__jeksi[f'col_indices_{ehgu__getp}'] = np.array(table.
            block_to_arr_ind[ehgu__getp], dtype=np.int64)
        uvkge__wij += '  for i in range(len(blk)):\n'
        uvkge__wij += f'    col_loc = col_indices_{ehgu__getp}[i]\n'
        uvkge__wij += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    uvkge__wij += '  if parallel:\n'
    uvkge__wij += '    for i in range(start_offset, len(out_arr)):\n'
    uvkge__wij += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    lcna__cxmbs = {}
    exec(uvkge__wij, jjdq__jeksi, lcna__cxmbs)
    return lcna__cxmbs['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    jbw__fuil = table.type_to_blk[arr_type]
    jjdq__jeksi = {'bodo': bodo}
    jjdq__jeksi['col_indices'] = np.array(table.block_to_arr_ind[jbw__fuil],
        dtype=np.int64)
    zbkl__lwg = col_nums_meta.instance_type
    jjdq__jeksi['col_nums'] = np.array(zbkl__lwg.meta, np.int64)
    uvkge__wij = 'def impl(table, col_nums_meta, arr_type):\n'
    uvkge__wij += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {jbw__fuil})\n')
    uvkge__wij += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    uvkge__wij += '  n = len(table)\n'
    cjey__yls = bodo.utils.typing.is_str_arr_type(arr_type)
    if cjey__yls:
        uvkge__wij += '  total_chars = 0\n'
        uvkge__wij += '  for c in col_nums:\n'
        uvkge__wij += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        uvkge__wij += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        uvkge__wij += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        uvkge__wij += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        uvkge__wij += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    uvkge__wij += '  for i in range(len(col_nums)):\n'
    uvkge__wij += '    c = col_nums[i]\n'
    if not cjey__yls:
        uvkge__wij += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    uvkge__wij += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    uvkge__wij += '    off = i * n\n'
    uvkge__wij += '    for j in range(len(arr)):\n'
    uvkge__wij += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    uvkge__wij += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    uvkge__wij += '      else:\n'
    uvkge__wij += '        out_arr[off+j] = arr[j]\n'
    uvkge__wij += '  return out_arr\n'
    igfky__vphl = {}
    exec(uvkge__wij, jjdq__jeksi, igfky__vphl)
    euqx__prbz = igfky__vphl['impl']
    return euqx__prbz


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    ihhu__vjarc = not is_overload_false(copy)
    pemu__vhi = is_overload_true(copy)
    jjdq__jeksi = {'bodo': bodo}
    vdil__hai = table.arr_types
    qhe__xyx = new_table_typ.arr_types
    hfxe__whqrd: Set[int] = set()
    ufur__bdem: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    jgcca__kxfo: Set[types.Type] = set()
    for lnmvr__ddlud, ciub__luui in enumerate(vdil__hai):
        nkvg__eah = qhe__xyx[lnmvr__ddlud]
        if ciub__luui == nkvg__eah:
            jgcca__kxfo.add(ciub__luui)
        else:
            hfxe__whqrd.add(lnmvr__ddlud)
            ufur__bdem[nkvg__eah].add(ciub__luui)
    uvkge__wij = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    uvkge__wij += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    uvkge__wij += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    tos__ypt = set(range(len(vdil__hai)))
    scjhd__igq = tos__ypt - hfxe__whqrd
    if not is_overload_none(used_cols):
        nohdw__ktnj = used_cols.instance_type
        llp__eium = set(nohdw__ktnj.meta)
        hfxe__whqrd = hfxe__whqrd & llp__eium
        scjhd__igq = scjhd__igq & llp__eium
        kgsix__ozij = set([table.block_nums[lnmvr__ddlud] for lnmvr__ddlud in
            llp__eium])
    else:
        llp__eium = None
    jjdq__jeksi['cast_cols'] = np.array(list(hfxe__whqrd), dtype=np.int64)
    jjdq__jeksi['copied_cols'] = np.array(list(scjhd__igq), dtype=np.int64)
    uvkge__wij += f'  copied_cols_set = set(copied_cols)\n'
    uvkge__wij += f'  cast_cols_set = set(cast_cols)\n'
    for halmh__kcrwy, ehgu__getp in new_table_typ.type_to_blk.items():
        jjdq__jeksi[f'typ_list_{ehgu__getp}'] = types.List(halmh__kcrwy)
        uvkge__wij += f"""  out_arr_list_{ehgu__getp} = bodo.hiframes.table.alloc_list_like(typ_list_{ehgu__getp}, {len(new_table_typ.block_to_arr_ind[ehgu__getp])}, False)
"""
        if halmh__kcrwy in jgcca__kxfo:
            ofzb__hso = table.type_to_blk[halmh__kcrwy]
            if llp__eium is None or ofzb__hso in kgsix__ozij:
                jezk__jkffj = table.block_to_arr_ind[ofzb__hso]
                pkvpu__vuh = [new_table_typ.block_offsets[xgqx__ifb] for
                    xgqx__ifb in jezk__jkffj]
                jjdq__jeksi[f'new_idx_{ofzb__hso}'] = np.array(pkvpu__vuh,
                    np.int64)
                jjdq__jeksi[f'orig_arr_inds_{ofzb__hso}'] = np.array(
                    jezk__jkffj, np.int64)
                uvkge__wij += f"""  arr_list_{ofzb__hso} = bodo.hiframes.table.get_table_block(table, {ofzb__hso})
"""
                uvkge__wij += f'  for i in range(len(arr_list_{ofzb__hso})):\n'
                uvkge__wij += (
                    f'    arr_ind_{ofzb__hso} = orig_arr_inds_{ofzb__hso}[i]\n'
                    )
                uvkge__wij += (
                    f'    if arr_ind_{ofzb__hso} not in copied_cols_set:\n')
                uvkge__wij += f'      continue\n'
                uvkge__wij += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{ofzb__hso}, i, arr_ind_{ofzb__hso})
"""
                uvkge__wij += (
                    f'    out_idx_{ehgu__getp}_{ofzb__hso} = new_idx_{ofzb__hso}[i]\n'
                    )
                uvkge__wij += (
                    f'    arr_val_{ofzb__hso} = arr_list_{ofzb__hso}[i]\n')
                if pemu__vhi:
                    uvkge__wij += (
                        f'    arr_val_{ofzb__hso} = arr_val_{ofzb__hso}.copy()\n'
                        )
                elif ihhu__vjarc:
                    uvkge__wij += f"""    arr_val_{ofzb__hso} = arr_val_{ofzb__hso}.copy() if copy else arr_val_{ehgu__getp}
"""
                uvkge__wij += f"""    out_arr_list_{ehgu__getp}[out_idx_{ehgu__getp}_{ofzb__hso}] = arr_val_{ofzb__hso}
"""
    qlky__fqyg = set()
    for halmh__kcrwy, ehgu__getp in new_table_typ.type_to_blk.items():
        if halmh__kcrwy in ufur__bdem:
            if isinstance(halmh__kcrwy, bodo.IntegerArrayType):
                uwck__vudc = halmh__kcrwy.get_pandas_scalar_type_instance.name
            else:
                uwck__vudc = halmh__kcrwy.dtype
            jjdq__jeksi[f'typ_{ehgu__getp}'] = uwck__vudc
            hpte__jpv = ufur__bdem[halmh__kcrwy]
            for zymu__cpxdc in hpte__jpv:
                ofzb__hso = table.type_to_blk[zymu__cpxdc]
                if llp__eium is None or ofzb__hso in kgsix__ozij:
                    if (zymu__cpxdc not in jgcca__kxfo and zymu__cpxdc not in
                        qlky__fqyg):
                        jezk__jkffj = table.block_to_arr_ind[ofzb__hso]
                        pkvpu__vuh = [new_table_typ.block_offsets[xgqx__ifb
                            ] for xgqx__ifb in jezk__jkffj]
                        jjdq__jeksi[f'new_idx_{ofzb__hso}'] = np.array(
                            pkvpu__vuh, np.int64)
                        jjdq__jeksi[f'orig_arr_inds_{ofzb__hso}'] = np.array(
                            jezk__jkffj, np.int64)
                        uvkge__wij += f"""  arr_list_{ofzb__hso} = bodo.hiframes.table.get_table_block(table, {ofzb__hso})
"""
                    qlky__fqyg.add(zymu__cpxdc)
                    uvkge__wij += (
                        f'  for i in range(len(arr_list_{ofzb__hso})):\n')
                    uvkge__wij += (
                        f'    arr_ind_{ofzb__hso} = orig_arr_inds_{ofzb__hso}[i]\n'
                        )
                    uvkge__wij += (
                        f'    if arr_ind_{ofzb__hso} not in cast_cols_set:\n')
                    uvkge__wij += f'      continue\n'
                    uvkge__wij += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{ofzb__hso}, i, arr_ind_{ofzb__hso})
"""
                    uvkge__wij += (
                        f'    out_idx_{ehgu__getp}_{ofzb__hso} = new_idx_{ofzb__hso}[i]\n'
                        )
                    uvkge__wij += f"""    arr_val_{ehgu__getp} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{ofzb__hso}[i], typ_{ehgu__getp}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    uvkge__wij += f"""    out_arr_list_{ehgu__getp}[out_idx_{ehgu__getp}_{ofzb__hso}] = arr_val_{ehgu__getp}
"""
        uvkge__wij += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{ehgu__getp}, {ehgu__getp})
"""
    uvkge__wij += '  return out_table\n'
    lcna__cxmbs = {}
    exec(uvkge__wij, jjdq__jeksi, lcna__cxmbs)
    return lcna__cxmbs['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    ykcay__rut = args[0]
    if equiv_set.has_shape(ykcay__rut):
        return ArrayAnalysis.AnalyzeResult(shape=ykcay__rut, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
