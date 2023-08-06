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
            self.na_position_b = tuple([(True if ondvl__jnfc == 'last' else
                False) for ondvl__jnfc in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [hxeh__pmqhz for hxeh__pmqhz in self.in_vars if hxeh__pmqhz
             is not None]

    def get_live_out_vars(self):
        return [hxeh__pmqhz for hxeh__pmqhz in self.out_vars if hxeh__pmqhz
             is not None]

    def __repr__(self):
        ilifu__ntsh = ', '.join(hxeh__pmqhz.name for hxeh__pmqhz in self.
            get_live_in_vars())
        pzv__uaw = f'{self.df_in}{{{ilifu__ntsh}}}'
        zav__hsqs = ', '.join(hxeh__pmqhz.name for hxeh__pmqhz in self.
            get_live_out_vars())
        nuns__ajh = f'{self.df_out}{{{zav__hsqs}}}'
        return f'Sort (keys: {self.key_inds}): {pzv__uaw} {nuns__ajh}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    nktbq__aipsc = []
    for yqt__yhxk in sort_node.get_live_in_vars():
        opu__yfw = equiv_set.get_shape(yqt__yhxk)
        if opu__yfw is not None:
            nktbq__aipsc.append(opu__yfw[0])
    if len(nktbq__aipsc) > 1:
        equiv_set.insert_equiv(*nktbq__aipsc)
    vrikt__frti = []
    nktbq__aipsc = []
    for yqt__yhxk in sort_node.get_live_out_vars():
        goqq__zfn = typemap[yqt__yhxk.name]
        ngt__qcift = array_analysis._gen_shape_call(equiv_set, yqt__yhxk,
            goqq__zfn.ndim, None, vrikt__frti)
        equiv_set.insert_equiv(yqt__yhxk, ngt__qcift)
        nktbq__aipsc.append(ngt__qcift[0])
        equiv_set.define(yqt__yhxk, set())
    if len(nktbq__aipsc) > 1:
        equiv_set.insert_equiv(*nktbq__aipsc)
    return [], vrikt__frti


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    eclfw__uqoy = sort_node.get_live_in_vars()
    yauh__twz = sort_node.get_live_out_vars()
    lgtle__kswbu = Distribution.OneD
    for yqt__yhxk in eclfw__uqoy:
        lgtle__kswbu = Distribution(min(lgtle__kswbu.value, array_dists[
            yqt__yhxk.name].value))
    spd__zvcr = Distribution(min(lgtle__kswbu.value, Distribution.OneD_Var.
        value))
    for yqt__yhxk in yauh__twz:
        if yqt__yhxk.name in array_dists:
            spd__zvcr = Distribution(min(spd__zvcr.value, array_dists[
                yqt__yhxk.name].value))
    if spd__zvcr != Distribution.OneD_Var:
        lgtle__kswbu = spd__zvcr
    for yqt__yhxk in eclfw__uqoy:
        array_dists[yqt__yhxk.name] = lgtle__kswbu
    for yqt__yhxk in yauh__twz:
        array_dists[yqt__yhxk.name] = spd__zvcr


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for omwp__ozvxl, lusu__mfaw in enumerate(sort_node.out_vars):
        uyrfx__kgpqm = sort_node.in_vars[omwp__ozvxl]
        if uyrfx__kgpqm is not None and lusu__mfaw is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                lusu__mfaw.name, src=uyrfx__kgpqm.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for yqt__yhxk in sort_node.get_live_out_vars():
            definitions[yqt__yhxk.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for omwp__ozvxl in range(len(sort_node.in_vars)):
        if sort_node.in_vars[omwp__ozvxl] is not None:
            sort_node.in_vars[omwp__ozvxl] = visit_vars_inner(sort_node.
                in_vars[omwp__ozvxl], callback, cbdata)
        if sort_node.out_vars[omwp__ozvxl] is not None:
            sort_node.out_vars[omwp__ozvxl] = visit_vars_inner(sort_node.
                out_vars[omwp__ozvxl], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        qmxh__eylo = sort_node.out_vars[0]
        if qmxh__eylo is not None and qmxh__eylo.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            vvkzh__lbay = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & vvkzh__lbay)
            sort_node.dead_var_inds.update(dead_cols - vvkzh__lbay)
            if len(vvkzh__lbay & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for omwp__ozvxl in range(1, len(sort_node.out_vars)):
            hxeh__pmqhz = sort_node.out_vars[omwp__ozvxl]
            if hxeh__pmqhz is not None and hxeh__pmqhz.name not in lives:
                sort_node.out_vars[omwp__ozvxl] = None
                lpyh__tqgte = sort_node.num_table_arrays + omwp__ozvxl - 1
                if lpyh__tqgte in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(lpyh__tqgte)
                else:
                    sort_node.dead_var_inds.add(lpyh__tqgte)
                    sort_node.in_vars[omwp__ozvxl] = None
    else:
        for omwp__ozvxl in range(len(sort_node.out_vars)):
            hxeh__pmqhz = sort_node.out_vars[omwp__ozvxl]
            if hxeh__pmqhz is not None and hxeh__pmqhz.name not in lives:
                sort_node.out_vars[omwp__ozvxl] = None
                if omwp__ozvxl in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(omwp__ozvxl)
                else:
                    sort_node.dead_var_inds.add(omwp__ozvxl)
                    sort_node.in_vars[omwp__ozvxl] = None
    if all(hxeh__pmqhz is None for hxeh__pmqhz in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({hxeh__pmqhz.name for hxeh__pmqhz in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({hxeh__pmqhz.name for hxeh__pmqhz in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    iwhiq__rjsyp = set()
    if not sort_node.inplace:
        iwhiq__rjsyp.update({hxeh__pmqhz.name for hxeh__pmqhz in sort_node.
            get_live_out_vars()})
    return set(), iwhiq__rjsyp


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for omwp__ozvxl in range(len(sort_node.in_vars)):
        if sort_node.in_vars[omwp__ozvxl] is not None:
            sort_node.in_vars[omwp__ozvxl] = replace_vars_inner(sort_node.
                in_vars[omwp__ozvxl], var_dict)
        if sort_node.out_vars[omwp__ozvxl] is not None:
            sort_node.out_vars[omwp__ozvxl] = replace_vars_inner(sort_node.
                out_vars[omwp__ozvxl], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for hxeh__pmqhz in (in_vars + out_vars):
            if array_dists[hxeh__pmqhz.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                hxeh__pmqhz.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        fgswc__tzb = []
        for hxeh__pmqhz in in_vars:
            omv__ugfe = _copy_array_nodes(hxeh__pmqhz, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            fgswc__tzb.append(omv__ugfe)
        in_vars = fgswc__tzb
    out_types = [(typemap[hxeh__pmqhz.name] if hxeh__pmqhz is not None else
        types.none) for hxeh__pmqhz in sort_node.out_vars]
    chp__amba, lcl__jgt = get_sort_cpp_section(sort_node, out_types, parallel)
    uvjkh__olwi = {}
    exec(chp__amba, {}, uvjkh__olwi)
    ots__bnu = uvjkh__olwi['f']
    lcl__jgt.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    lcl__jgt.update({f'out_type{omwp__ozvxl}': out_types[omwp__ozvxl] for
        omwp__ozvxl in range(len(out_types))})
    gofc__efsxg = compile_to_numba_ir(ots__bnu, lcl__jgt, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[hxeh__pmqhz.
        name] for hxeh__pmqhz in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(gofc__efsxg, in_vars)
    hrgqz__bxhhx = gofc__efsxg.body[-2].value.value
    nodes += gofc__efsxg.body[:-2]
    for omwp__ozvxl, hxeh__pmqhz in enumerate(out_vars):
        gen_getitem(hxeh__pmqhz, hrgqz__bxhhx, omwp__ozvxl, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    mrqv__qgbk = lambda arr: arr.copy()
    zfc__rpm = None
    if isinstance(typemap[var.name], TableType):
        vjx__arfw = len(typemap[var.name].arr_types)
        zfc__rpm = set(range(vjx__arfw)) - dead_cols
        zfc__rpm = MetaType(tuple(sorted(zfc__rpm)))
        mrqv__qgbk = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    gofc__efsxg = compile_to_numba_ir(mrqv__qgbk, {'bodo': bodo, 'types':
        types, '_used_columns': zfc__rpm}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(gofc__efsxg, [var])
    nodes += gofc__efsxg.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    spu__glv = len(sort_node.key_inds)
    ftzw__rot = len(sort_node.in_vars)
    rbezj__obxw = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + ftzw__rot - 1 if sort_node.
        is_table_format else ftzw__rot)
    fxvzc__vtwr, oigqu__mbgat, xmaby__xxmpz = _get_cpp_col_ind_mappings(
        sort_node.key_inds, sort_node.dead_var_inds, sort_node.
        dead_key_var_inds, n_cols)
    epe__hql = []
    if sort_node.is_table_format:
        epe__hql.append('arg0')
        for omwp__ozvxl in range(1, ftzw__rot):
            lpyh__tqgte = sort_node.num_table_arrays + omwp__ozvxl - 1
            if lpyh__tqgte not in sort_node.dead_var_inds:
                epe__hql.append(f'arg{lpyh__tqgte}')
    else:
        for omwp__ozvxl in range(n_cols):
            if omwp__ozvxl not in sort_node.dead_var_inds:
                epe__hql.append(f'arg{omwp__ozvxl}')
    chp__amba = f"def f({', '.join(epe__hql)}):\n"
    if sort_node.is_table_format:
        zanoq__ctf = ',' if ftzw__rot - 1 == 1 else ''
        lkni__dntxh = []
        for omwp__ozvxl in range(sort_node.num_table_arrays, n_cols):
            if omwp__ozvxl in sort_node.dead_var_inds:
                lkni__dntxh.append('None')
            else:
                lkni__dntxh.append(f'arg{omwp__ozvxl}')
        chp__amba += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(lkni__dntxh)}{zanoq__ctf}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        hnol__uast = {tyrei__gaf: omwp__ozvxl for omwp__ozvxl, tyrei__gaf in
            enumerate(fxvzc__vtwr)}
        ialw__xarmc = [None] * len(fxvzc__vtwr)
        for omwp__ozvxl in range(n_cols):
            yegdu__cyzu = hnol__uast.get(omwp__ozvxl, -1)
            if yegdu__cyzu != -1:
                ialw__xarmc[yegdu__cyzu] = f'array_to_info(arg{omwp__ozvxl})'
        chp__amba += '  info_list_total = [{}]\n'.format(','.join(ialw__xarmc))
        chp__amba += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    chp__amba += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if kxjc__auh else '0' for kxjc__auh in sort_node.
        ascending_list))
    chp__amba += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if kxjc__auh else '0' for kxjc__auh in sort_node.
        na_position_b))
    chp__amba += '  dead_keys = np.array([{}], np.int64)\n'.format(','.join
        ('1' if omwp__ozvxl in xmaby__xxmpz else '0' for omwp__ozvxl in
        range(spu__glv)))
    chp__amba += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    chp__amba += f"""  out_cpp_table = sort_values_table(in_cpp_table, {spu__glv}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        zanoq__ctf = ',' if rbezj__obxw == 1 else ''
        ymdw__exzvb = (
            f"({', '.join(f'out_type{omwp__ozvxl}' if not type_has_unknown_cats(out_types[omwp__ozvxl]) else f'arg{omwp__ozvxl}' for omwp__ozvxl in range(rbezj__obxw))}{zanoq__ctf})"
            )
        chp__amba += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {ymdw__exzvb}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        hnol__uast = {tyrei__gaf: omwp__ozvxl for omwp__ozvxl, tyrei__gaf in
            enumerate(oigqu__mbgat)}
        ialw__xarmc = []
        for omwp__ozvxl in range(n_cols):
            yegdu__cyzu = hnol__uast.get(omwp__ozvxl, -1)
            if yegdu__cyzu != -1:
                reept__szcj = (f'out_type{omwp__ozvxl}' if not
                    type_has_unknown_cats(out_types[omwp__ozvxl]) else
                    f'arg{omwp__ozvxl}')
                chp__amba += f"""  out{omwp__ozvxl} = info_to_array(info_from_table(out_cpp_table, {yegdu__cyzu}), {reept__szcj})
"""
                ialw__xarmc.append(f'out{omwp__ozvxl}')
        zanoq__ctf = ',' if len(ialw__xarmc) == 1 else ''
        aeblo__pzxxk = f"({', '.join(ialw__xarmc)}{zanoq__ctf})"
        chp__amba += f'  out_data = {aeblo__pzxxk}\n'
    chp__amba += '  delete_table(out_cpp_table)\n'
    chp__amba += '  delete_table(in_cpp_table)\n'
    chp__amba += f'  return out_data\n'
    return chp__amba, {'in_col_inds': MetaType(tuple(fxvzc__vtwr)),
        'out_col_inds': MetaType(tuple(oigqu__mbgat))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    fxvzc__vtwr = []
    oigqu__mbgat = []
    xmaby__xxmpz = []
    for tyrei__gaf, omwp__ozvxl in enumerate(key_inds):
        fxvzc__vtwr.append(omwp__ozvxl)
        if omwp__ozvxl in dead_key_var_inds:
            xmaby__xxmpz.append(tyrei__gaf)
        else:
            oigqu__mbgat.append(omwp__ozvxl)
    for omwp__ozvxl in range(n_cols):
        if omwp__ozvxl in dead_var_inds or omwp__ozvxl in key_inds:
            continue
        fxvzc__vtwr.append(omwp__ozvxl)
        oigqu__mbgat.append(omwp__ozvxl)
    return fxvzc__vtwr, oigqu__mbgat, xmaby__xxmpz


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    ofo__vsfvn = sort_node.in_vars[0].name
    zhje__tdbre = sort_node.out_vars[0].name
    llql__ttrjc, ixs__hpod, grn__bdlhh = block_use_map[ofo__vsfvn]
    if ixs__hpod or grn__bdlhh:
        return
    uxalg__utyey, chybb__hfum, cccv__aqox = _compute_table_column_uses(
        zhje__tdbre, table_col_use_map, equiv_vars)
    tmxi__yhhop = set(omwp__ozvxl for omwp__ozvxl in sort_node.key_inds if 
        omwp__ozvxl < sort_node.num_table_arrays)
    block_use_map[ofo__vsfvn] = (llql__ttrjc | uxalg__utyey | tmxi__yhhop, 
        chybb__hfum or cccv__aqox, False)


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    vjx__arfw = sort_node.num_table_arrays
    zhje__tdbre = sort_node.out_vars[0].name
    zfc__rpm = _find_used_columns(zhje__tdbre, vjx__arfw, column_live_map,
        equiv_vars)
    if zfc__rpm is None:
        return False
    jymof__ngroi = set(range(vjx__arfw)) - zfc__rpm
    tmxi__yhhop = set(omwp__ozvxl for omwp__ozvxl in sort_node.key_inds if 
        omwp__ozvxl < vjx__arfw)
    ghk__ewhhd = sort_node.dead_key_var_inds | jymof__ngroi & tmxi__yhhop
    dohw__rmynv = sort_node.dead_var_inds | jymof__ngroi - tmxi__yhhop
    vnep__phiyh = (ghk__ewhhd != sort_node.dead_key_var_inds) | (dohw__rmynv !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = ghk__ewhhd
    sort_node.dead_var_inds = dohw__rmynv
    return vnep__phiyh


remove_dead_column_extensions[Sort] = sort_remove_dead_column
