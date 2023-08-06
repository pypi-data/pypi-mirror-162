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
            self.na_position_b = tuple([(True if dvkn__fmk == 'last' else 
                False) for dvkn__fmk in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [wloy__iyyt for wloy__iyyt in self.in_vars if wloy__iyyt is not
            None]

    def get_live_out_vars(self):
        return [wloy__iyyt for wloy__iyyt in self.out_vars if wloy__iyyt is not
            None]

    def __repr__(self):
        vhc__yrttp = ', '.join(wloy__iyyt.name for wloy__iyyt in self.
            get_live_in_vars())
        vca__crgt = f'{self.df_in}{{{vhc__yrttp}}}'
        usl__fnap = ', '.join(wloy__iyyt.name for wloy__iyyt in self.
            get_live_out_vars())
        ikkyh__owpm = f'{self.df_out}{{{usl__fnap}}}'
        return f'Sort (keys: {self.key_inds}): {vca__crgt} {ikkyh__owpm}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    znky__lsp = []
    for wzthg__hrtu in sort_node.get_live_in_vars():
        wsig__ucunt = equiv_set.get_shape(wzthg__hrtu)
        if wsig__ucunt is not None:
            znky__lsp.append(wsig__ucunt[0])
    if len(znky__lsp) > 1:
        equiv_set.insert_equiv(*znky__lsp)
    txrnt__pcbqz = []
    znky__lsp = []
    for wzthg__hrtu in sort_node.get_live_out_vars():
        vukw__qtkh = typemap[wzthg__hrtu.name]
        qfol__ovtt = array_analysis._gen_shape_call(equiv_set, wzthg__hrtu,
            vukw__qtkh.ndim, None, txrnt__pcbqz)
        equiv_set.insert_equiv(wzthg__hrtu, qfol__ovtt)
        znky__lsp.append(qfol__ovtt[0])
        equiv_set.define(wzthg__hrtu, set())
    if len(znky__lsp) > 1:
        equiv_set.insert_equiv(*znky__lsp)
    return [], txrnt__pcbqz


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    wlrdv__uqkt = sort_node.get_live_in_vars()
    vae__yhtbi = sort_node.get_live_out_vars()
    qbm__vxha = Distribution.OneD
    for wzthg__hrtu in wlrdv__uqkt:
        qbm__vxha = Distribution(min(qbm__vxha.value, array_dists[
            wzthg__hrtu.name].value))
    svfm__zdcoc = Distribution(min(qbm__vxha.value, Distribution.OneD_Var.
        value))
    for wzthg__hrtu in vae__yhtbi:
        if wzthg__hrtu.name in array_dists:
            svfm__zdcoc = Distribution(min(svfm__zdcoc.value, array_dists[
                wzthg__hrtu.name].value))
    if svfm__zdcoc != Distribution.OneD_Var:
        qbm__vxha = svfm__zdcoc
    for wzthg__hrtu in wlrdv__uqkt:
        array_dists[wzthg__hrtu.name] = qbm__vxha
    for wzthg__hrtu in vae__yhtbi:
        array_dists[wzthg__hrtu.name] = svfm__zdcoc


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for srw__qxay, dwid__lry in enumerate(sort_node.out_vars):
        slzp__bxg = sort_node.in_vars[srw__qxay]
        if slzp__bxg is not None and dwid__lry is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                dwid__lry.name, src=slzp__bxg.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for wzthg__hrtu in sort_node.get_live_out_vars():
            definitions[wzthg__hrtu.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for srw__qxay in range(len(sort_node.in_vars)):
        if sort_node.in_vars[srw__qxay] is not None:
            sort_node.in_vars[srw__qxay] = visit_vars_inner(sort_node.
                in_vars[srw__qxay], callback, cbdata)
        if sort_node.out_vars[srw__qxay] is not None:
            sort_node.out_vars[srw__qxay] = visit_vars_inner(sort_node.
                out_vars[srw__qxay], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        xelvu__luz = sort_node.out_vars[0]
        if xelvu__luz is not None and xelvu__luz.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            wblrn__hcx = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & wblrn__hcx)
            sort_node.dead_var_inds.update(dead_cols - wblrn__hcx)
            if len(wblrn__hcx & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for srw__qxay in range(1, len(sort_node.out_vars)):
            wloy__iyyt = sort_node.out_vars[srw__qxay]
            if wloy__iyyt is not None and wloy__iyyt.name not in lives:
                sort_node.out_vars[srw__qxay] = None
                nglj__zbxn = sort_node.num_table_arrays + srw__qxay - 1
                if nglj__zbxn in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(nglj__zbxn)
                else:
                    sort_node.dead_var_inds.add(nglj__zbxn)
                    sort_node.in_vars[srw__qxay] = None
    else:
        for srw__qxay in range(len(sort_node.out_vars)):
            wloy__iyyt = sort_node.out_vars[srw__qxay]
            if wloy__iyyt is not None and wloy__iyyt.name not in lives:
                sort_node.out_vars[srw__qxay] = None
                if srw__qxay in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(srw__qxay)
                else:
                    sort_node.dead_var_inds.add(srw__qxay)
                    sort_node.in_vars[srw__qxay] = None
    if all(wloy__iyyt is None for wloy__iyyt in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({wloy__iyyt.name for wloy__iyyt in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({wloy__iyyt.name for wloy__iyyt in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    maor__ufry = set()
    if not sort_node.inplace:
        maor__ufry.update({wloy__iyyt.name for wloy__iyyt in sort_node.
            get_live_out_vars()})
    return set(), maor__ufry


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for srw__qxay in range(len(sort_node.in_vars)):
        if sort_node.in_vars[srw__qxay] is not None:
            sort_node.in_vars[srw__qxay] = replace_vars_inner(sort_node.
                in_vars[srw__qxay], var_dict)
        if sort_node.out_vars[srw__qxay] is not None:
            sort_node.out_vars[srw__qxay] = replace_vars_inner(sort_node.
                out_vars[srw__qxay], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for wloy__iyyt in (in_vars + out_vars):
            if array_dists[wloy__iyyt.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                wloy__iyyt.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        tuxmc__qbyiy = []
        for wloy__iyyt in in_vars:
            zlkeo__usweb = _copy_array_nodes(wloy__iyyt, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            tuxmc__qbyiy.append(zlkeo__usweb)
        in_vars = tuxmc__qbyiy
    out_types = [(typemap[wloy__iyyt.name] if wloy__iyyt is not None else
        types.none) for wloy__iyyt in sort_node.out_vars]
    btbz__pwask, xxua__mzg = get_sort_cpp_section(sort_node, out_types,
        parallel)
    tkitv__ahp = {}
    exec(btbz__pwask, {}, tkitv__ahp)
    xcycw__pcfmd = tkitv__ahp['f']
    xxua__mzg.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    xxua__mzg.update({f'out_type{srw__qxay}': out_types[srw__qxay] for
        srw__qxay in range(len(out_types))})
    nobm__xqmzb = compile_to_numba_ir(xcycw__pcfmd, xxua__mzg, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[wloy__iyyt.
        name] for wloy__iyyt in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(nobm__xqmzb, in_vars)
    vpi__ptj = nobm__xqmzb.body[-2].value.value
    nodes += nobm__xqmzb.body[:-2]
    for srw__qxay, wloy__iyyt in enumerate(out_vars):
        gen_getitem(wloy__iyyt, vpi__ptj, srw__qxay, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    dyz__cxfn = lambda arr: arr.copy()
    xpudj__wbmz = None
    if isinstance(typemap[var.name], TableType):
        rsuty__lfzi = len(typemap[var.name].arr_types)
        xpudj__wbmz = set(range(rsuty__lfzi)) - dead_cols
        xpudj__wbmz = MetaType(tuple(sorted(xpudj__wbmz)))
        dyz__cxfn = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    nobm__xqmzb = compile_to_numba_ir(dyz__cxfn, {'bodo': bodo, 'types':
        types, '_used_columns': xpudj__wbmz}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(nobm__xqmzb, [var])
    nodes += nobm__xqmzb.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    wvs__jkdu = len(sort_node.key_inds)
    gvri__ygux = len(sort_node.in_vars)
    yfwil__qplo = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + gvri__ygux - 1 if sort_node.
        is_table_format else gvri__ygux)
    tbx__nqivf, enxux__ktf, eyqke__jiszr = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    zvhl__cxuek = []
    if sort_node.is_table_format:
        zvhl__cxuek.append('arg0')
        for srw__qxay in range(1, gvri__ygux):
            nglj__zbxn = sort_node.num_table_arrays + srw__qxay - 1
            if nglj__zbxn not in sort_node.dead_var_inds:
                zvhl__cxuek.append(f'arg{nglj__zbxn}')
    else:
        for srw__qxay in range(n_cols):
            if srw__qxay not in sort_node.dead_var_inds:
                zvhl__cxuek.append(f'arg{srw__qxay}')
    btbz__pwask = f"def f({', '.join(zvhl__cxuek)}):\n"
    if sort_node.is_table_format:
        bzbp__ianc = ',' if gvri__ygux - 1 == 1 else ''
        mqlvw__psw = []
        for srw__qxay in range(sort_node.num_table_arrays, n_cols):
            if srw__qxay in sort_node.dead_var_inds:
                mqlvw__psw.append('None')
            else:
                mqlvw__psw.append(f'arg{srw__qxay}')
        btbz__pwask += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(mqlvw__psw)}{bzbp__ianc}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        gael__dhmgo = {iuch__zebna: srw__qxay for srw__qxay, iuch__zebna in
            enumerate(tbx__nqivf)}
        vxcwg__lhra = [None] * len(tbx__nqivf)
        for srw__qxay in range(n_cols):
            lda__sznak = gael__dhmgo.get(srw__qxay, -1)
            if lda__sznak != -1:
                vxcwg__lhra[lda__sznak] = f'array_to_info(arg{srw__qxay})'
        btbz__pwask += '  info_list_total = [{}]\n'.format(','.join(
            vxcwg__lhra))
        btbz__pwask += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    btbz__pwask += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if zhaj__abo else '0' for zhaj__abo in sort_node.
        ascending_list))
    btbz__pwask += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if zhaj__abo else '0' for zhaj__abo in sort_node.
        na_position_b))
    btbz__pwask += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if srw__qxay in eyqke__jiszr else '0' for srw__qxay in
        range(wvs__jkdu)))
    btbz__pwask += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    btbz__pwask += f"""  out_cpp_table = sort_values_table(in_cpp_table, {wvs__jkdu}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        bzbp__ianc = ',' if yfwil__qplo == 1 else ''
        ozebz__stgih = (
            f"({', '.join(f'out_type{srw__qxay}' if not type_has_unknown_cats(out_types[srw__qxay]) else f'arg{srw__qxay}' for srw__qxay in range(yfwil__qplo))}{bzbp__ianc})"
            )
        btbz__pwask += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {ozebz__stgih}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        gael__dhmgo = {iuch__zebna: srw__qxay for srw__qxay, iuch__zebna in
            enumerate(enxux__ktf)}
        vxcwg__lhra = []
        for srw__qxay in range(n_cols):
            lda__sznak = gael__dhmgo.get(srw__qxay, -1)
            if lda__sznak != -1:
                wjcpu__gdgav = (f'out_type{srw__qxay}' if not
                    type_has_unknown_cats(out_types[srw__qxay]) else
                    f'arg{srw__qxay}')
                btbz__pwask += f"""  out{srw__qxay} = info_to_array(info_from_table(out_cpp_table, {lda__sznak}), {wjcpu__gdgav})
"""
                vxcwg__lhra.append(f'out{srw__qxay}')
        bzbp__ianc = ',' if len(vxcwg__lhra) == 1 else ''
        besrz__vtka = f"({', '.join(vxcwg__lhra)}{bzbp__ianc})"
        btbz__pwask += f'  out_data = {besrz__vtka}\n'
    btbz__pwask += '  delete_table(out_cpp_table)\n'
    btbz__pwask += '  delete_table(in_cpp_table)\n'
    btbz__pwask += f'  return out_data\n'
    return btbz__pwask, {'in_col_inds': MetaType(tuple(tbx__nqivf)),
        'out_col_inds': MetaType(tuple(enxux__ktf))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    tbx__nqivf = []
    enxux__ktf = []
    eyqke__jiszr = []
    for iuch__zebna, srw__qxay in enumerate(key_inds):
        tbx__nqivf.append(srw__qxay)
        if srw__qxay in dead_key_var_inds:
            eyqke__jiszr.append(iuch__zebna)
        else:
            enxux__ktf.append(srw__qxay)
    for srw__qxay in range(n_cols):
        if srw__qxay in dead_var_inds or srw__qxay in key_inds:
            continue
        tbx__nqivf.append(srw__qxay)
        enxux__ktf.append(srw__qxay)
    return tbx__nqivf, enxux__ktf, eyqke__jiszr


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    tkyzj__dod = sort_node.in_vars[0].name
    zwfgg__grt = sort_node.out_vars[0].name
    gxz__lwel, rcxid__eyuw, kypnc__qrp = block_use_map[tkyzj__dod]
    if rcxid__eyuw or kypnc__qrp:
        return
    hkbpj__qcgqi, rmxej__asuix, mvinc__oamqh = _compute_table_column_uses(
        zwfgg__grt, table_col_use_map, equiv_vars)
    fxvg__bkagd = set(srw__qxay for srw__qxay in sort_node.key_inds if 
        srw__qxay < sort_node.num_table_arrays)
    block_use_map[tkyzj__dod] = (gxz__lwel | hkbpj__qcgqi | fxvg__bkagd, 
        rmxej__asuix or mvinc__oamqh, False)


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    rsuty__lfzi = sort_node.num_table_arrays
    zwfgg__grt = sort_node.out_vars[0].name
    xpudj__wbmz = _find_used_columns(zwfgg__grt, rsuty__lfzi,
        column_live_map, equiv_vars)
    if xpudj__wbmz is None:
        return False
    fepr__ijpu = set(range(rsuty__lfzi)) - xpudj__wbmz
    fxvg__bkagd = set(srw__qxay for srw__qxay in sort_node.key_inds if 
        srw__qxay < rsuty__lfzi)
    jesi__tfy = sort_node.dead_key_var_inds | fepr__ijpu & fxvg__bkagd
    njjiu__dwj = sort_node.dead_var_inds | fepr__ijpu - fxvg__bkagd
    dmv__afjd = (jesi__tfy != sort_node.dead_key_var_inds) | (njjiu__dwj !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = jesi__tfy
    sort_node.dead_var_inds = njjiu__dwj
    return dmv__afjd


remove_dead_column_extensions[Sort] = sort_remove_dead_column
