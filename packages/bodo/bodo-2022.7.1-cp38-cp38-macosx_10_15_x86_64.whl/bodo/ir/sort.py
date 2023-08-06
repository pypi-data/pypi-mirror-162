"""IR node for the data sorting"""
from collections import defaultdict
from typing import List, Set, Tuple, Union
import numba
import numpy as np
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes, replace_vars_inner, visit_vars_inner
import bodo
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_data_to_cpp_table, sort_values_table
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, _find_used_columns, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import MetaType, type_has_unknown_cats
from bodo.utils.utils import gen_getitem


class Sort(ir.Stmt):

    def __init__(self, df_in: str, df_out: str, in_vars: List[ir.Var],
        out_vars: List[ir.Var], key_inds: Tuple[int], inplace: bool, loc:
        ir.Loc, ascending_list: Union[List[bool], bool]=True, na_position:
        Union[List[str], str]='last', is_table_format: bool=False,
        num_table_arrays: int=0):
        self.df_in = df_in
        self.df_out = df_out
        self.in_vars = in_vars
        self.out_vars = out_vars
        self.key_inds = key_inds
        self.inplace = inplace
        self.is_table_format = is_table_format
        self.num_table_arrays = num_table_arrays
        self.dead_var_inds: Set[int] = set()
        self.dead_key_var_inds: Set[int] = set()
        if isinstance(na_position, str):
            if na_position == 'last':
                self.na_position_b = (True,) * len(key_inds)
            else:
                self.na_position_b = (False,) * len(key_inds)
        else:
            self.na_position_b = tuple([(True if ixe__ivayt == 'last' else 
                False) for ixe__ivayt in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [uottr__xil for uottr__xil in self.in_vars if uottr__xil is not
            None]

    def get_live_out_vars(self):
        return [uottr__xil for uottr__xil in self.out_vars if uottr__xil is not
            None]

    def __repr__(self):
        agaz__avgxj = ', '.join(uottr__xil.name for uottr__xil in self.
            get_live_in_vars())
        enjod__vdnls = f'{self.df_in}{{{agaz__avgxj}}}'
        jtuz__omkjd = ', '.join(uottr__xil.name for uottr__xil in self.
            get_live_out_vars())
        aluqe__crubr = f'{self.df_out}{{{jtuz__omkjd}}}'
        return f'Sort (keys: {self.key_inds}): {enjod__vdnls} {aluqe__crubr}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    hia__rtqs = []
    for pis__uhig in sort_node.get_live_in_vars():
        qqt__bzs = equiv_set.get_shape(pis__uhig)
        if qqt__bzs is not None:
            hia__rtqs.append(qqt__bzs[0])
    if len(hia__rtqs) > 1:
        equiv_set.insert_equiv(*hia__rtqs)
    mlx__ihqlm = []
    hia__rtqs = []
    for pis__uhig in sort_node.get_live_out_vars():
        dpf__zsck = typemap[pis__uhig.name]
        zxczh__ked = array_analysis._gen_shape_call(equiv_set, pis__uhig,
            dpf__zsck.ndim, None, mlx__ihqlm)
        equiv_set.insert_equiv(pis__uhig, zxczh__ked)
        hia__rtqs.append(zxczh__ked[0])
        equiv_set.define(pis__uhig, set())
    if len(hia__rtqs) > 1:
        equiv_set.insert_equiv(*hia__rtqs)
    return [], mlx__ihqlm


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    htrd__rhbx = sort_node.get_live_in_vars()
    asi__gog = sort_node.get_live_out_vars()
    axnt__owlk = Distribution.OneD
    for pis__uhig in htrd__rhbx:
        axnt__owlk = Distribution(min(axnt__owlk.value, array_dists[
            pis__uhig.name].value))
    ndtb__rnsoq = Distribution(min(axnt__owlk.value, Distribution.OneD_Var.
        value))
    for pis__uhig in asi__gog:
        if pis__uhig.name in array_dists:
            ndtb__rnsoq = Distribution(min(ndtb__rnsoq.value, array_dists[
                pis__uhig.name].value))
    if ndtb__rnsoq != Distribution.OneD_Var:
        axnt__owlk = ndtb__rnsoq
    for pis__uhig in htrd__rhbx:
        array_dists[pis__uhig.name] = axnt__owlk
    for pis__uhig in asi__gog:
        array_dists[pis__uhig.name] = ndtb__rnsoq


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for nfzsa__fzz, qnt__hrpqh in enumerate(sort_node.out_vars):
        mah__kwrnq = sort_node.in_vars[nfzsa__fzz]
        if mah__kwrnq is not None and qnt__hrpqh is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                qnt__hrpqh.name, src=mah__kwrnq.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for pis__uhig in sort_node.get_live_out_vars():
            definitions[pis__uhig.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for nfzsa__fzz in range(len(sort_node.in_vars)):
        if sort_node.in_vars[nfzsa__fzz] is not None:
            sort_node.in_vars[nfzsa__fzz] = visit_vars_inner(sort_node.
                in_vars[nfzsa__fzz], callback, cbdata)
        if sort_node.out_vars[nfzsa__fzz] is not None:
            sort_node.out_vars[nfzsa__fzz] = visit_vars_inner(sort_node.
                out_vars[nfzsa__fzz], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        htop__nznbz = sort_node.out_vars[0]
        if htop__nznbz is not None and htop__nznbz.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            gsq__gmbe = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & gsq__gmbe)
            sort_node.dead_var_inds.update(dead_cols - gsq__gmbe)
            if len(gsq__gmbe & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for nfzsa__fzz in range(1, len(sort_node.out_vars)):
            uottr__xil = sort_node.out_vars[nfzsa__fzz]
            if uottr__xil is not None and uottr__xil.name not in lives:
                sort_node.out_vars[nfzsa__fzz] = None
                ayt__gqov = sort_node.num_table_arrays + nfzsa__fzz - 1
                if ayt__gqov in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(ayt__gqov)
                else:
                    sort_node.dead_var_inds.add(ayt__gqov)
                    sort_node.in_vars[nfzsa__fzz] = None
    else:
        for nfzsa__fzz in range(len(sort_node.out_vars)):
            uottr__xil = sort_node.out_vars[nfzsa__fzz]
            if uottr__xil is not None and uottr__xil.name not in lives:
                sort_node.out_vars[nfzsa__fzz] = None
                if nfzsa__fzz in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(nfzsa__fzz)
                else:
                    sort_node.dead_var_inds.add(nfzsa__fzz)
                    sort_node.in_vars[nfzsa__fzz] = None
    if all(uottr__xil is None for uottr__xil in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({uottr__xil.name for uottr__xil in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({uottr__xil.name for uottr__xil in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    xflnn__gqjs = set()
    if not sort_node.inplace:
        xflnn__gqjs.update({uottr__xil.name for uottr__xil in sort_node.
            get_live_out_vars()})
    return set(), xflnn__gqjs


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for nfzsa__fzz in range(len(sort_node.in_vars)):
        if sort_node.in_vars[nfzsa__fzz] is not None:
            sort_node.in_vars[nfzsa__fzz] = replace_vars_inner(sort_node.
                in_vars[nfzsa__fzz], var_dict)
        if sort_node.out_vars[nfzsa__fzz] is not None:
            sort_node.out_vars[nfzsa__fzz] = replace_vars_inner(sort_node.
                out_vars[nfzsa__fzz], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for uottr__xil in (in_vars + out_vars):
            if array_dists[uottr__xil.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                uottr__xil.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        allla__bzy = []
        for uottr__xil in in_vars:
            pmpjm__vscam = _copy_array_nodes(uottr__xil, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            allla__bzy.append(pmpjm__vscam)
        in_vars = allla__bzy
    out_types = [(typemap[uottr__xil.name] if uottr__xil is not None else
        types.none) for uottr__xil in sort_node.out_vars]
    hbtw__jno, miqt__zucj = get_sort_cpp_section(sort_node, out_types, parallel
        )
    vljql__hgolf = {}
    exec(hbtw__jno, {}, vljql__hgolf)
    iukqh__dmmb = vljql__hgolf['f']
    miqt__zucj.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    miqt__zucj.update({f'out_type{nfzsa__fzz}': out_types[nfzsa__fzz] for
        nfzsa__fzz in range(len(out_types))})
    vpuo__die = compile_to_numba_ir(iukqh__dmmb, miqt__zucj, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[uottr__xil.
        name] for uottr__xil in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(vpuo__die, in_vars)
    xzctz__xdcku = vpuo__die.body[-2].value.value
    nodes += vpuo__die.body[:-2]
    for nfzsa__fzz, uottr__xil in enumerate(out_vars):
        gen_getitem(uottr__xil, xzctz__xdcku, nfzsa__fzz, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    kbqfs__ufp = lambda arr: arr.copy()
    fqxx__sny = None
    if isinstance(typemap[var.name], TableType):
        cofc__mhyg = len(typemap[var.name].arr_types)
        fqxx__sny = set(range(cofc__mhyg)) - dead_cols
        fqxx__sny = MetaType(tuple(sorted(fqxx__sny)))
        kbqfs__ufp = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    vpuo__die = compile_to_numba_ir(kbqfs__ufp, {'bodo': bodo, 'types':
        types, '_used_columns': fqxx__sny}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(vpuo__die, [var])
    nodes += vpuo__die.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    lhnlo__gjpw = len(sort_node.key_inds)
    gcjs__qtc = len(sort_node.in_vars)
    leil__emwe = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + gcjs__qtc - 1 if sort_node.
        is_table_format else gcjs__qtc)
    dxfx__aoc, uzpjz__uvc, tgc__jhtr = _get_cpp_col_ind_mappings(sort_node.
        key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols)
    qiep__xqbo = []
    if sort_node.is_table_format:
        qiep__xqbo.append('arg0')
        for nfzsa__fzz in range(1, gcjs__qtc):
            ayt__gqov = sort_node.num_table_arrays + nfzsa__fzz - 1
            if ayt__gqov not in sort_node.dead_var_inds:
                qiep__xqbo.append(f'arg{ayt__gqov}')
    else:
        for nfzsa__fzz in range(n_cols):
            if nfzsa__fzz not in sort_node.dead_var_inds:
                qiep__xqbo.append(f'arg{nfzsa__fzz}')
    hbtw__jno = f"def f({', '.join(qiep__xqbo)}):\n"
    if sort_node.is_table_format:
        itqfe__yfyc = ',' if gcjs__qtc - 1 == 1 else ''
        zkzt__zqvi = []
        for nfzsa__fzz in range(sort_node.num_table_arrays, n_cols):
            if nfzsa__fzz in sort_node.dead_var_inds:
                zkzt__zqvi.append('None')
            else:
                zkzt__zqvi.append(f'arg{nfzsa__fzz}')
        hbtw__jno += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(zkzt__zqvi)}{itqfe__yfyc}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        dius__rjuuw = {mmqk__cxa: nfzsa__fzz for nfzsa__fzz, mmqk__cxa in
            enumerate(dxfx__aoc)}
        qmx__sbi = [None] * len(dxfx__aoc)
        for nfzsa__fzz in range(n_cols):
            ktgeh__mnqx = dius__rjuuw.get(nfzsa__fzz, -1)
            if ktgeh__mnqx != -1:
                qmx__sbi[ktgeh__mnqx] = f'array_to_info(arg{nfzsa__fzz})'
        hbtw__jno += '  info_list_total = [{}]\n'.format(','.join(qmx__sbi))
        hbtw__jno += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    hbtw__jno += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if nxxie__icfm else '0' for nxxie__icfm in sort_node.
        ascending_list))
    hbtw__jno += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if nxxie__icfm else '0' for nxxie__icfm in sort_node.
        na_position_b))
    hbtw__jno += '  dead_keys = np.array([{}], np.int64)\n'.format(','.join
        ('1' if nfzsa__fzz in tgc__jhtr else '0' for nfzsa__fzz in range(
        lhnlo__gjpw)))
    hbtw__jno += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    hbtw__jno += f"""  out_cpp_table = sort_values_table(in_cpp_table, {lhnlo__gjpw}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        itqfe__yfyc = ',' if leil__emwe == 1 else ''
        sstlp__lplcz = (
            f"({', '.join(f'out_type{nfzsa__fzz}' if not type_has_unknown_cats(out_types[nfzsa__fzz]) else f'arg{nfzsa__fzz}' for nfzsa__fzz in range(leil__emwe))}{itqfe__yfyc})"
            )
        hbtw__jno += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {sstlp__lplcz}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        dius__rjuuw = {mmqk__cxa: nfzsa__fzz for nfzsa__fzz, mmqk__cxa in
            enumerate(uzpjz__uvc)}
        qmx__sbi = []
        for nfzsa__fzz in range(n_cols):
            ktgeh__mnqx = dius__rjuuw.get(nfzsa__fzz, -1)
            if ktgeh__mnqx != -1:
                ocd__lbjcl = (f'out_type{nfzsa__fzz}' if not
                    type_has_unknown_cats(out_types[nfzsa__fzz]) else
                    f'arg{nfzsa__fzz}')
                hbtw__jno += f"""  out{nfzsa__fzz} = info_to_array(info_from_table(out_cpp_table, {ktgeh__mnqx}), {ocd__lbjcl})
"""
                qmx__sbi.append(f'out{nfzsa__fzz}')
        itqfe__yfyc = ',' if len(qmx__sbi) == 1 else ''
        bqncv__dqwqh = f"({', '.join(qmx__sbi)}{itqfe__yfyc})"
        hbtw__jno += f'  out_data = {bqncv__dqwqh}\n'
    hbtw__jno += '  delete_table(out_cpp_table)\n'
    hbtw__jno += '  delete_table(in_cpp_table)\n'
    hbtw__jno += f'  return out_data\n'
    return hbtw__jno, {'in_col_inds': MetaType(tuple(dxfx__aoc)),
        'out_col_inds': MetaType(tuple(uzpjz__uvc))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    dxfx__aoc = []
    uzpjz__uvc = []
    tgc__jhtr = []
    for mmqk__cxa, nfzsa__fzz in enumerate(key_inds):
        dxfx__aoc.append(nfzsa__fzz)
        if nfzsa__fzz in dead_key_var_inds:
            tgc__jhtr.append(mmqk__cxa)
        else:
            uzpjz__uvc.append(nfzsa__fzz)
    for nfzsa__fzz in range(n_cols):
        if nfzsa__fzz in dead_var_inds or nfzsa__fzz in key_inds:
            continue
        dxfx__aoc.append(nfzsa__fzz)
        uzpjz__uvc.append(nfzsa__fzz)
    return dxfx__aoc, uzpjz__uvc, tgc__jhtr


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    xpoiu__csqf = sort_node.in_vars[0].name
    yhes__egr = sort_node.out_vars[0].name
    okiq__wyu, ohqkt__phvtp, wgwzz__ezxz = block_use_map[xpoiu__csqf]
    if ohqkt__phvtp or wgwzz__ezxz:
        return
    hynjw__moxk, nbwk__gzmr, cfydr__dtry = _compute_table_column_uses(yhes__egr
        , table_col_use_map, equiv_vars)
    aqvz__tcpc = set(nfzsa__fzz for nfzsa__fzz in sort_node.key_inds if 
        nfzsa__fzz < sort_node.num_table_arrays)
    block_use_map[xpoiu__csqf
        ] = okiq__wyu | hynjw__moxk | aqvz__tcpc, nbwk__gzmr or cfydr__dtry, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    cofc__mhyg = sort_node.num_table_arrays
    yhes__egr = sort_node.out_vars[0].name
    fqxx__sny = _find_used_columns(yhes__egr, cofc__mhyg, column_live_map,
        equiv_vars)
    if fqxx__sny is None:
        return False
    plk__yblry = set(range(cofc__mhyg)) - fqxx__sny
    aqvz__tcpc = set(nfzsa__fzz for nfzsa__fzz in sort_node.key_inds if 
        nfzsa__fzz < cofc__mhyg)
    rsrhb__evt = sort_node.dead_key_var_inds | plk__yblry & aqvz__tcpc
    cis__zmto = sort_node.dead_var_inds | plk__yblry - aqvz__tcpc
    zwm__eje = (rsrhb__evt != sort_node.dead_key_var_inds) | (cis__zmto !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = rsrhb__evt
    sort_node.dead_var_inds = cis__zmto
    return zwm__eje


remove_dead_column_extensions[Sort] = sort_remove_dead_column
