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
            self.na_position_b = tuple([(True if ghood__hqtpz == 'last' else
                False) for ghood__hqtpz in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [kteo__dkj for kteo__dkj in self.in_vars if kteo__dkj is not
            None]

    def get_live_out_vars(self):
        return [kteo__dkj for kteo__dkj in self.out_vars if kteo__dkj is not
            None]

    def __repr__(self):
        hpik__gync = ', '.join(kteo__dkj.name for kteo__dkj in self.
            get_live_in_vars())
        chhyt__guybj = f'{self.df_in}{{{hpik__gync}}}'
        ojzyu__nhhbl = ', '.join(kteo__dkj.name for kteo__dkj in self.
            get_live_out_vars())
        ngz__wsb = f'{self.df_out}{{{ojzyu__nhhbl}}}'
        return f'Sort (keys: {self.key_inds}): {chhyt__guybj} {ngz__wsb}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    hamde__zubgt = []
    for ggc__gwvbh in sort_node.get_live_in_vars():
        qzyc__rzkl = equiv_set.get_shape(ggc__gwvbh)
        if qzyc__rzkl is not None:
            hamde__zubgt.append(qzyc__rzkl[0])
    if len(hamde__zubgt) > 1:
        equiv_set.insert_equiv(*hamde__zubgt)
    mtpfy__ttu = []
    hamde__zubgt = []
    for ggc__gwvbh in sort_node.get_live_out_vars():
        fgd__edarg = typemap[ggc__gwvbh.name]
        lxsu__elej = array_analysis._gen_shape_call(equiv_set, ggc__gwvbh,
            fgd__edarg.ndim, None, mtpfy__ttu)
        equiv_set.insert_equiv(ggc__gwvbh, lxsu__elej)
        hamde__zubgt.append(lxsu__elej[0])
        equiv_set.define(ggc__gwvbh, set())
    if len(hamde__zubgt) > 1:
        equiv_set.insert_equiv(*hamde__zubgt)
    return [], mtpfy__ttu


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    rpgar__yzng = sort_node.get_live_in_vars()
    hpql__qmwp = sort_node.get_live_out_vars()
    lmd__ksm = Distribution.OneD
    for ggc__gwvbh in rpgar__yzng:
        lmd__ksm = Distribution(min(lmd__ksm.value, array_dists[ggc__gwvbh.
            name].value))
    wmnu__ubpa = Distribution(min(lmd__ksm.value, Distribution.OneD_Var.value))
    for ggc__gwvbh in hpql__qmwp:
        if ggc__gwvbh.name in array_dists:
            wmnu__ubpa = Distribution(min(wmnu__ubpa.value, array_dists[
                ggc__gwvbh.name].value))
    if wmnu__ubpa != Distribution.OneD_Var:
        lmd__ksm = wmnu__ubpa
    for ggc__gwvbh in rpgar__yzng:
        array_dists[ggc__gwvbh.name] = lmd__ksm
    for ggc__gwvbh in hpql__qmwp:
        array_dists[ggc__gwvbh.name] = wmnu__ubpa


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for pqvej__uypk, gjcw__gzt in enumerate(sort_node.out_vars):
        ajhwq__fmcde = sort_node.in_vars[pqvej__uypk]
        if ajhwq__fmcde is not None and gjcw__gzt is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                gjcw__gzt.name, src=ajhwq__fmcde.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for ggc__gwvbh in sort_node.get_live_out_vars():
            definitions[ggc__gwvbh.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for pqvej__uypk in range(len(sort_node.in_vars)):
        if sort_node.in_vars[pqvej__uypk] is not None:
            sort_node.in_vars[pqvej__uypk] = visit_vars_inner(sort_node.
                in_vars[pqvej__uypk], callback, cbdata)
        if sort_node.out_vars[pqvej__uypk] is not None:
            sort_node.out_vars[pqvej__uypk] = visit_vars_inner(sort_node.
                out_vars[pqvej__uypk], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        gwvi__rnw = sort_node.out_vars[0]
        if gwvi__rnw is not None and gwvi__rnw.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            qhs__yesq = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & qhs__yesq)
            sort_node.dead_var_inds.update(dead_cols - qhs__yesq)
            if len(qhs__yesq & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for pqvej__uypk in range(1, len(sort_node.out_vars)):
            kteo__dkj = sort_node.out_vars[pqvej__uypk]
            if kteo__dkj is not None and kteo__dkj.name not in lives:
                sort_node.out_vars[pqvej__uypk] = None
                poa__vazq = sort_node.num_table_arrays + pqvej__uypk - 1
                if poa__vazq in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(poa__vazq)
                else:
                    sort_node.dead_var_inds.add(poa__vazq)
                    sort_node.in_vars[pqvej__uypk] = None
    else:
        for pqvej__uypk in range(len(sort_node.out_vars)):
            kteo__dkj = sort_node.out_vars[pqvej__uypk]
            if kteo__dkj is not None and kteo__dkj.name not in lives:
                sort_node.out_vars[pqvej__uypk] = None
                if pqvej__uypk in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(pqvej__uypk)
                else:
                    sort_node.dead_var_inds.add(pqvej__uypk)
                    sort_node.in_vars[pqvej__uypk] = None
    if all(kteo__dkj is None for kteo__dkj in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({kteo__dkj.name for kteo__dkj in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({kteo__dkj.name for kteo__dkj in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    tan__uhcyv = set()
    if not sort_node.inplace:
        tan__uhcyv.update({kteo__dkj.name for kteo__dkj in sort_node.
            get_live_out_vars()})
    return set(), tan__uhcyv


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for pqvej__uypk in range(len(sort_node.in_vars)):
        if sort_node.in_vars[pqvej__uypk] is not None:
            sort_node.in_vars[pqvej__uypk] = replace_vars_inner(sort_node.
                in_vars[pqvej__uypk], var_dict)
        if sort_node.out_vars[pqvej__uypk] is not None:
            sort_node.out_vars[pqvej__uypk] = replace_vars_inner(sort_node.
                out_vars[pqvej__uypk], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for kteo__dkj in (in_vars + out_vars):
            if array_dists[kteo__dkj.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                kteo__dkj.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        chj__yzc = []
        for kteo__dkj in in_vars:
            nzp__edv = _copy_array_nodes(kteo__dkj, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            chj__yzc.append(nzp__edv)
        in_vars = chj__yzc
    out_types = [(typemap[kteo__dkj.name] if kteo__dkj is not None else
        types.none) for kteo__dkj in sort_node.out_vars]
    rirk__hrwnc, vxp__pkgpk = get_sort_cpp_section(sort_node, out_types,
        parallel)
    tdjc__ppa = {}
    exec(rirk__hrwnc, {}, tdjc__ppa)
    gruav__nllq = tdjc__ppa['f']
    vxp__pkgpk.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    vxp__pkgpk.update({f'out_type{pqvej__uypk}': out_types[pqvej__uypk] for
        pqvej__uypk in range(len(out_types))})
    hrxyn__otj = compile_to_numba_ir(gruav__nllq, vxp__pkgpk, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[kteo__dkj.
        name] for kteo__dkj in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(hrxyn__otj, in_vars)
    efncc__zxcd = hrxyn__otj.body[-2].value.value
    nodes += hrxyn__otj.body[:-2]
    for pqvej__uypk, kteo__dkj in enumerate(out_vars):
        gen_getitem(kteo__dkj, efncc__zxcd, pqvej__uypk, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    uapfh__qwnba = lambda arr: arr.copy()
    qib__ssz = None
    if isinstance(typemap[var.name], TableType):
        zkjq__lrwpi = len(typemap[var.name].arr_types)
        qib__ssz = set(range(zkjq__lrwpi)) - dead_cols
        qib__ssz = MetaType(tuple(sorted(qib__ssz)))
        uapfh__qwnba = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    hrxyn__otj = compile_to_numba_ir(uapfh__qwnba, {'bodo': bodo, 'types':
        types, '_used_columns': qib__ssz}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(hrxyn__otj, [var])
    nodes += hrxyn__otj.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    iaxw__myl = len(sort_node.key_inds)
    lheg__lzb = len(sort_node.in_vars)
    rlzs__vzmy = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + lheg__lzb - 1 if sort_node.
        is_table_format else lheg__lzb)
    vdan__alo, lngrl__wxyia, gacz__glyxu = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    bjk__amle = []
    if sort_node.is_table_format:
        bjk__amle.append('arg0')
        for pqvej__uypk in range(1, lheg__lzb):
            poa__vazq = sort_node.num_table_arrays + pqvej__uypk - 1
            if poa__vazq not in sort_node.dead_var_inds:
                bjk__amle.append(f'arg{poa__vazq}')
    else:
        for pqvej__uypk in range(n_cols):
            if pqvej__uypk not in sort_node.dead_var_inds:
                bjk__amle.append(f'arg{pqvej__uypk}')
    rirk__hrwnc = f"def f({', '.join(bjk__amle)}):\n"
    if sort_node.is_table_format:
        jfs__ubc = ',' if lheg__lzb - 1 == 1 else ''
        vpfd__rqj = []
        for pqvej__uypk in range(sort_node.num_table_arrays, n_cols):
            if pqvej__uypk in sort_node.dead_var_inds:
                vpfd__rqj.append('None')
            else:
                vpfd__rqj.append(f'arg{pqvej__uypk}')
        rirk__hrwnc += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(vpfd__rqj)}{jfs__ubc}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        zsho__ibgz = {pmibc__rvl: pqvej__uypk for pqvej__uypk, pmibc__rvl in
            enumerate(vdan__alo)}
        redk__xudix = [None] * len(vdan__alo)
        for pqvej__uypk in range(n_cols):
            kundx__opcgd = zsho__ibgz.get(pqvej__uypk, -1)
            if kundx__opcgd != -1:
                redk__xudix[kundx__opcgd] = f'array_to_info(arg{pqvej__uypk})'
        rirk__hrwnc += '  info_list_total = [{}]\n'.format(','.join(
            redk__xudix))
        rirk__hrwnc += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    rirk__hrwnc += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if qnup__lrz else '0' for qnup__lrz in sort_node.
        ascending_list))
    rirk__hrwnc += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if qnup__lrz else '0' for qnup__lrz in sort_node.
        na_position_b))
    rirk__hrwnc += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if pqvej__uypk in gacz__glyxu else '0' for pqvej__uypk in
        range(iaxw__myl)))
    rirk__hrwnc += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    rirk__hrwnc += f"""  out_cpp_table = sort_values_table(in_cpp_table, {iaxw__myl}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        jfs__ubc = ',' if rlzs__vzmy == 1 else ''
        znv__dlqu = (
            f"({', '.join(f'out_type{pqvej__uypk}' if not type_has_unknown_cats(out_types[pqvej__uypk]) else f'arg{pqvej__uypk}' for pqvej__uypk in range(rlzs__vzmy))}{jfs__ubc})"
            )
        rirk__hrwnc += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {znv__dlqu}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        zsho__ibgz = {pmibc__rvl: pqvej__uypk for pqvej__uypk, pmibc__rvl in
            enumerate(lngrl__wxyia)}
        redk__xudix = []
        for pqvej__uypk in range(n_cols):
            kundx__opcgd = zsho__ibgz.get(pqvej__uypk, -1)
            if kundx__opcgd != -1:
                wgv__wwt = (f'out_type{pqvej__uypk}' if not
                    type_has_unknown_cats(out_types[pqvej__uypk]) else
                    f'arg{pqvej__uypk}')
                rirk__hrwnc += f"""  out{pqvej__uypk} = info_to_array(info_from_table(out_cpp_table, {kundx__opcgd}), {wgv__wwt})
"""
                redk__xudix.append(f'out{pqvej__uypk}')
        jfs__ubc = ',' if len(redk__xudix) == 1 else ''
        uxmnv__zwm = f"({', '.join(redk__xudix)}{jfs__ubc})"
        rirk__hrwnc += f'  out_data = {uxmnv__zwm}\n'
    rirk__hrwnc += '  delete_table(out_cpp_table)\n'
    rirk__hrwnc += '  delete_table(in_cpp_table)\n'
    rirk__hrwnc += f'  return out_data\n'
    return rirk__hrwnc, {'in_col_inds': MetaType(tuple(vdan__alo)),
        'out_col_inds': MetaType(tuple(lngrl__wxyia))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    vdan__alo = []
    lngrl__wxyia = []
    gacz__glyxu = []
    for pmibc__rvl, pqvej__uypk in enumerate(key_inds):
        vdan__alo.append(pqvej__uypk)
        if pqvej__uypk in dead_key_var_inds:
            gacz__glyxu.append(pmibc__rvl)
        else:
            lngrl__wxyia.append(pqvej__uypk)
    for pqvej__uypk in range(n_cols):
        if pqvej__uypk in dead_var_inds or pqvej__uypk in key_inds:
            continue
        vdan__alo.append(pqvej__uypk)
        lngrl__wxyia.append(pqvej__uypk)
    return vdan__alo, lngrl__wxyia, gacz__glyxu


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    grd__nha = sort_node.in_vars[0].name
    lehk__owvz = sort_node.out_vars[0].name
    esnn__wqi, oky__xebe, vkd__ojzbr = block_use_map[grd__nha]
    if oky__xebe or vkd__ojzbr:
        return
    ikd__ukj, skm__mqta, mgdnv__rff = _compute_table_column_uses(lehk__owvz,
        table_col_use_map, equiv_vars)
    uekw__nezr = set(pqvej__uypk for pqvej__uypk in sort_node.key_inds if 
        pqvej__uypk < sort_node.num_table_arrays)
    block_use_map[grd__nha
        ] = esnn__wqi | ikd__ukj | uekw__nezr, skm__mqta or mgdnv__rff, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    zkjq__lrwpi = sort_node.num_table_arrays
    lehk__owvz = sort_node.out_vars[0].name
    qib__ssz = _find_used_columns(lehk__owvz, zkjq__lrwpi, column_live_map,
        equiv_vars)
    if qib__ssz is None:
        return False
    eqo__ggg = set(range(zkjq__lrwpi)) - qib__ssz
    uekw__nezr = set(pqvej__uypk for pqvej__uypk in sort_node.key_inds if 
        pqvej__uypk < zkjq__lrwpi)
    mzjiq__ftfr = sort_node.dead_key_var_inds | eqo__ggg & uekw__nezr
    ygbn__eab = sort_node.dead_var_inds | eqo__ggg - uekw__nezr
    foay__ftcm = (mzjiq__ftfr != sort_node.dead_key_var_inds) | (ygbn__eab !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = mzjiq__ftfr
    sort_node.dead_var_inds = ygbn__eab
    return foay__ftcm


remove_dead_column_extensions[Sort] = sort_remove_dead_column
