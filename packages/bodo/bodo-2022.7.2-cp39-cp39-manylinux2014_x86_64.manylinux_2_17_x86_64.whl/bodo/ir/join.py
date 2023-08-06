"""IR node for the join and merge"""
from collections import defaultdict
from typing import Dict, List, Literal, Optional, Set, Tuple, Union
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes, replace_vars_inner, visit_vars_inner
from numba.extending import intrinsic
import bodo
from bodo.hiframes.table import TableType
from bodo.ir.connector import trim_extra_used_columns
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, delete_table, hash_join_table, py_data_to_cpp_table
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, get_live_column_nums_block, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import INDEX_SENTINEL, BodoError, MetaType, dtype_to_array_type, find_common_np_dtype, is_dtype_nullable, is_nullable_type, is_str_arr_type, to_nullable_type
from bodo.utils.utils import alloc_arr_tup, is_null_pointer
join_gen_cond_cfunc = {}
join_gen_cond_cfunc_addr = {}


@intrinsic
def add_join_gen_cond_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        wozcz__ojoww = func.signature
        pnq__psj = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        oroc__zey = cgutils.get_or_insert_function(builder.module, pnq__psj,
            sym._literal_value)
        builder.call(oroc__zey, [context.get_constant_null(wozcz__ojoww.
            args[0]), context.get_constant_null(wozcz__ojoww.args[1]),
            context.get_constant_null(wozcz__ojoww.args[2]), context.
            get_constant_null(wozcz__ojoww.args[3]), context.
            get_constant_null(wozcz__ojoww.args[4]), context.
            get_constant_null(wozcz__ojoww.args[5]), context.get_constant(
            types.int64, 0), context.get_constant(types.int64, 0)])
        context.add_linking_libs([join_gen_cond_cfunc[sym._literal_value].
            _library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_join_cond_addr(name):
    with numba.objmode(addr='int64'):
        addr = join_gen_cond_cfunc_addr[name]
    return addr


HOW_OPTIONS = Literal['inner', 'left', 'right', 'outer', 'asof']


class Join(ir.Stmt):

    def __init__(self, left_keys: Union[List[str], str], right_keys: Union[
        List[str], str], out_data_vars: List[ir.Var], out_df_type: bodo.
        DataFrameType, left_vars: List[ir.Var], left_df_type: bodo.
        DataFrameType, right_vars: List[ir.Var], right_df_type: bodo.
        DataFrameType, how: HOW_OPTIONS, suffix_left: str, suffix_right:
        str, loc: ir.Loc, is_left: bool, is_right: bool, is_join: bool,
        left_index: bool, right_index: bool, indicator_col_num: int,
        is_na_equal: bool, gen_cond_expr: str):
        self.left_keys = left_keys
        self.right_keys = right_keys
        self.out_data_vars = out_data_vars
        self.out_col_names = out_df_type.columns
        self.left_vars = left_vars
        self.right_vars = right_vars
        self.how = how
        self.loc = loc
        self.is_left = is_left
        self.is_right = is_right
        self.is_join = is_join
        self.left_index = left_index
        self.right_index = right_index
        self.indicator_col_num = indicator_col_num
        self.is_na_equal = is_na_equal
        self.gen_cond_expr = gen_cond_expr
        self.n_out_table_cols = len(self.out_col_names)
        self.out_used_cols = set(range(self.n_out_table_cols))
        if self.out_data_vars[1] is not None:
            self.out_used_cols.add(self.n_out_table_cols)
        wclmk__zhap = left_df_type.columns
        gmzcl__swu = right_df_type.columns
        self.left_col_names = wclmk__zhap
        self.right_col_names = gmzcl__swu
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(wclmk__zhap) if self.is_left_table else 0
        self.n_right_table_cols = len(gmzcl__swu) if self.is_right_table else 0
        iqhxz__udam = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        qmfhg__iria = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(iqhxz__udam)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(qmfhg__iria)
        self.left_var_map = {vtor__rikh: smb__lhfkm for smb__lhfkm,
            vtor__rikh in enumerate(wclmk__zhap)}
        self.right_var_map = {vtor__rikh: smb__lhfkm for smb__lhfkm,
            vtor__rikh in enumerate(gmzcl__swu)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = iqhxz__udam
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = qmfhg__iria
        self.left_key_set = set(self.left_var_map[vtor__rikh] for
            vtor__rikh in left_keys)
        self.right_key_set = set(self.right_var_map[vtor__rikh] for
            vtor__rikh in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[vtor__rikh] for
                vtor__rikh in wclmk__zhap if f'(left.{vtor__rikh})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[vtor__rikh] for
                vtor__rikh in gmzcl__swu if f'(right.{vtor__rikh})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        tltwq__ahsj: int = -1
        gnort__xjla = set(left_keys) & set(right_keys)
        gri__kstt = set(wclmk__zhap) & set(gmzcl__swu)
        oshh__ndst = gri__kstt - gnort__xjla
        rqyj__bpt: Dict[int, (Literal['left', 'right'], int)] = {}
        iaap__efd: Dict[int, int] = {}
        wwpe__hubf: Dict[int, int] = {}
        for smb__lhfkm, vtor__rikh in enumerate(wclmk__zhap):
            if vtor__rikh in oshh__ndst:
                aoqsi__jmb = str(vtor__rikh) + suffix_left
                ssd__dpzxh = out_df_type.column_index[aoqsi__jmb]
                if (right_index and not left_index and smb__lhfkm in self.
                    left_key_set):
                    tltwq__ahsj = out_df_type.column_index[vtor__rikh]
                    rqyj__bpt[tltwq__ahsj] = 'left', smb__lhfkm
            else:
                ssd__dpzxh = out_df_type.column_index[vtor__rikh]
            rqyj__bpt[ssd__dpzxh] = 'left', smb__lhfkm
            iaap__efd[smb__lhfkm] = ssd__dpzxh
        for smb__lhfkm, vtor__rikh in enumerate(gmzcl__swu):
            if vtor__rikh not in gnort__xjla:
                if vtor__rikh in oshh__ndst:
                    nda__kpon = str(vtor__rikh) + suffix_right
                    ssd__dpzxh = out_df_type.column_index[nda__kpon]
                    if (left_index and not right_index and smb__lhfkm in
                        self.right_key_set):
                        tltwq__ahsj = out_df_type.column_index[vtor__rikh]
                        rqyj__bpt[tltwq__ahsj] = 'right', smb__lhfkm
                else:
                    ssd__dpzxh = out_df_type.column_index[vtor__rikh]
                rqyj__bpt[ssd__dpzxh] = 'right', smb__lhfkm
                wwpe__hubf[smb__lhfkm] = ssd__dpzxh
        if self.left_vars[-1] is not None:
            iaap__efd[iqhxz__udam] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            wwpe__hubf[qmfhg__iria] = self.n_out_table_cols
        self.out_to_input_col_map = rqyj__bpt
        self.left_to_output_map = iaap__efd
        self.right_to_output_map = wwpe__hubf
        self.extra_data_col_num = tltwq__ahsj
        if len(out_data_vars) > 1:
            lfby__kcaj = 'left' if right_index else 'right'
            if lfby__kcaj == 'left':
                sgu__bgrsx = iqhxz__udam
            elif lfby__kcaj == 'right':
                sgu__bgrsx = qmfhg__iria
        else:
            lfby__kcaj = None
            sgu__bgrsx = -1
        self.index_source = lfby__kcaj
        self.index_col_num = sgu__bgrsx
        ohoa__prcer = []
        jqn__wvraj = len(left_keys)
        for yjrqa__gudef in range(jqn__wvraj):
            cbr__kxf = left_keys[yjrqa__gudef]
            nidt__heevm = right_keys[yjrqa__gudef]
            ohoa__prcer.append(cbr__kxf == nidt__heevm)
        self.vect_same_key = ohoa__prcer

    @property
    def has_live_left_table_var(self):
        return self.is_left_table and self.left_vars[0] is not None

    @property
    def has_live_right_table_var(self):
        return self.is_right_table and self.right_vars[0] is not None

    @property
    def has_live_out_table_var(self):
        return self.out_data_vars[0] is not None

    @property
    def has_live_out_index_var(self):
        return self.out_data_vars[1] is not None

    def get_out_table_var(self):
        return self.out_data_vars[0]

    def get_out_index_var(self):
        return self.out_data_vars[1]

    def get_live_left_vars(self):
        vars = []
        for wovbj__puhv in self.left_vars:
            if wovbj__puhv is not None:
                vars.append(wovbj__puhv)
        return vars

    def get_live_right_vars(self):
        vars = []
        for wovbj__puhv in self.right_vars:
            if wovbj__puhv is not None:
                vars.append(wovbj__puhv)
        return vars

    def get_live_out_vars(self):
        vars = []
        for wovbj__puhv in self.out_data_vars:
            if wovbj__puhv is not None:
                vars.append(wovbj__puhv)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        miw__atpb = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[miw__atpb])
                miw__atpb += 1
            else:
                left_vars.append(None)
            start = 1
        oenzv__eeynd = max(self.n_left_table_cols - 1, 0)
        for smb__lhfkm in range(start, len(self.left_vars)):
            if smb__lhfkm + oenzv__eeynd in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[miw__atpb])
                miw__atpb += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        miw__atpb = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[miw__atpb])
                miw__atpb += 1
            else:
                right_vars.append(None)
            start = 1
        oenzv__eeynd = max(self.n_right_table_cols - 1, 0)
        for smb__lhfkm in range(start, len(self.right_vars)):
            if smb__lhfkm + oenzv__eeynd in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[miw__atpb])
                miw__atpb += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        tpwu__qbu = [self.has_live_out_table_var, self.has_live_out_index_var]
        miw__atpb = 0
        for smb__lhfkm in range(len(self.out_data_vars)):
            if not tpwu__qbu[smb__lhfkm]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[miw__atpb])
                miw__atpb += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {smb__lhfkm for smb__lhfkm in self.out_used_cols if 
            smb__lhfkm < self.n_out_table_cols}

    def __repr__(self):
        ecmi__duyo = ', '.join([f'{vtor__rikh}' for vtor__rikh in self.
            left_col_names])
        xghdi__oscv = f'left={{{ecmi__duyo}}}'
        ecmi__duyo = ', '.join([f'{vtor__rikh}' for vtor__rikh in self.
            right_col_names])
        kpraj__ekpx = f'right={{{ecmi__duyo}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, xghdi__oscv, kpraj__ekpx)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    spl__ljpl = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    hspk__duze = []
    zmobj__peyfa = join_node.get_live_left_vars()
    for ehox__ucqj in zmobj__peyfa:
        seh__fnwyr = typemap[ehox__ucqj.name]
        vued__mojkw = equiv_set.get_shape(ehox__ucqj)
        if vued__mojkw:
            hspk__duze.append(vued__mojkw[0])
    if len(hspk__duze) > 1:
        equiv_set.insert_equiv(*hspk__duze)
    hspk__duze = []
    zmobj__peyfa = list(join_node.get_live_right_vars())
    for ehox__ucqj in zmobj__peyfa:
        seh__fnwyr = typemap[ehox__ucqj.name]
        vued__mojkw = equiv_set.get_shape(ehox__ucqj)
        if vued__mojkw:
            hspk__duze.append(vued__mojkw[0])
    if len(hspk__duze) > 1:
        equiv_set.insert_equiv(*hspk__duze)
    hspk__duze = []
    for iznxq__dmrn in join_node.get_live_out_vars():
        seh__fnwyr = typemap[iznxq__dmrn.name]
        buf__fdcw = array_analysis._gen_shape_call(equiv_set, iznxq__dmrn,
            seh__fnwyr.ndim, None, spl__ljpl)
        equiv_set.insert_equiv(iznxq__dmrn, buf__fdcw)
        hspk__duze.append(buf__fdcw[0])
        equiv_set.define(iznxq__dmrn, set())
    if len(hspk__duze) > 1:
        equiv_set.insert_equiv(*hspk__duze)
    return [], spl__ljpl


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    nybxh__efcv = Distribution.OneD
    uoz__deqhy = Distribution.OneD
    for ehox__ucqj in join_node.get_live_left_vars():
        nybxh__efcv = Distribution(min(nybxh__efcv.value, array_dists[
            ehox__ucqj.name].value))
    for ehox__ucqj in join_node.get_live_right_vars():
        uoz__deqhy = Distribution(min(uoz__deqhy.value, array_dists[
            ehox__ucqj.name].value))
    jkbx__cjn = Distribution.OneD_Var
    for iznxq__dmrn in join_node.get_live_out_vars():
        if iznxq__dmrn.name in array_dists:
            jkbx__cjn = Distribution(min(jkbx__cjn.value, array_dists[
                iznxq__dmrn.name].value))
    wdhtu__qyxdr = Distribution(min(jkbx__cjn.value, nybxh__efcv.value))
    bddqe__poyxd = Distribution(min(jkbx__cjn.value, uoz__deqhy.value))
    jkbx__cjn = Distribution(max(wdhtu__qyxdr.value, bddqe__poyxd.value))
    for iznxq__dmrn in join_node.get_live_out_vars():
        array_dists[iznxq__dmrn.name] = jkbx__cjn
    if jkbx__cjn != Distribution.OneD_Var:
        nybxh__efcv = jkbx__cjn
        uoz__deqhy = jkbx__cjn
    for ehox__ucqj in join_node.get_live_left_vars():
        array_dists[ehox__ucqj.name] = nybxh__efcv
    for ehox__ucqj in join_node.get_live_right_vars():
        array_dists[ehox__ucqj.name] = uoz__deqhy
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(wovbj__puhv, callback,
        cbdata) for wovbj__puhv in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(wovbj__puhv, callback,
        cbdata) for wovbj__puhv in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(wovbj__puhv,
        callback, cbdata) for wovbj__puhv in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        rckpv__jnutn = []
        ivinu__gtmq = join_node.get_out_table_var()
        if ivinu__gtmq.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for xxrg__vzetv in join_node.out_to_input_col_map.keys():
            if xxrg__vzetv in join_node.out_used_cols:
                continue
            rckpv__jnutn.append(xxrg__vzetv)
            if join_node.indicator_col_num == xxrg__vzetv:
                join_node.indicator_col_num = -1
                continue
            if xxrg__vzetv == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            nudc__fsgh, xxrg__vzetv = join_node.out_to_input_col_map[
                xxrg__vzetv]
            if nudc__fsgh == 'left':
                if (xxrg__vzetv not in join_node.left_key_set and 
                    xxrg__vzetv not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(xxrg__vzetv)
                    if not join_node.is_left_table:
                        join_node.left_vars[xxrg__vzetv] = None
            elif nudc__fsgh == 'right':
                if (xxrg__vzetv not in join_node.right_key_set and 
                    xxrg__vzetv not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(xxrg__vzetv)
                    if not join_node.is_right_table:
                        join_node.right_vars[xxrg__vzetv] = None
        for smb__lhfkm in rckpv__jnutn:
            del join_node.out_to_input_col_map[smb__lhfkm]
        if join_node.is_left_table:
            vgvb__nyc = set(range(join_node.n_left_table_cols))
            hhyxq__pmkqh = not bool(vgvb__nyc - join_node.left_dead_var_inds)
            if hhyxq__pmkqh:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            vgvb__nyc = set(range(join_node.n_right_table_cols))
            hhyxq__pmkqh = not bool(vgvb__nyc - join_node.right_dead_var_inds)
            if hhyxq__pmkqh:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        cqyi__hndh = join_node.get_out_index_var()
        if cqyi__hndh.name not in lives:
            join_node.out_data_vars[1] = None
            join_node.out_used_cols.remove(join_node.n_out_table_cols)
            if join_node.index_source == 'left':
                if (join_node.index_col_num not in join_node.left_key_set and
                    join_node.index_col_num not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(join_node.index_col_num)
                    join_node.left_vars[-1] = None
            elif join_node.index_col_num not in join_node.right_key_set and join_node.index_col_num not in join_node.right_cond_cols:
                join_node.right_dead_var_inds.add(join_node.index_col_num)
                join_node.right_vars[-1] = None
    if not (join_node.has_live_out_table_var or join_node.
        has_live_out_index_var):
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_remove_dead_column(join_node, column_live_map, equiv_vars, typemap):
    bttty__rfq = False
    if join_node.has_live_out_table_var:
        ljihf__sdoay = join_node.get_out_table_var().name
        undug__joue, ebmvp__npmoh, pltr__qny = get_live_column_nums_block(
            column_live_map, equiv_vars, ljihf__sdoay)
        if not (ebmvp__npmoh or pltr__qny):
            undug__joue = trim_extra_used_columns(undug__joue, join_node.
                n_out_table_cols)
            pcd__vznrw = join_node.get_out_table_used_cols()
            if len(undug__joue) != len(pcd__vznrw):
                bttty__rfq = not (join_node.is_left_table and join_node.
                    is_right_table)
                ifv__omv = pcd__vznrw - undug__joue
                join_node.out_used_cols = join_node.out_used_cols - ifv__omv
    return bttty__rfq


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        cirs__qva = join_node.get_out_table_var()
        vdo__hdin, ebmvp__npmoh, pltr__qny = _compute_table_column_uses(
            cirs__qva.name, table_col_use_map, equiv_vars)
    else:
        vdo__hdin, ebmvp__npmoh, pltr__qny = set(), False, False
    if join_node.has_live_left_table_var:
        uovcq__tihjd = join_node.left_vars[0].name
        bgptp__cmvu, mmow__vltu, ewnd__flwm = block_use_map[uovcq__tihjd]
        if not (mmow__vltu or ewnd__flwm):
            rreeo__fiaqf = set([join_node.out_to_input_col_map[smb__lhfkm][
                1] for smb__lhfkm in vdo__hdin if join_node.
                out_to_input_col_map[smb__lhfkm][0] == 'left'])
            ovs__exuv = set(smb__lhfkm for smb__lhfkm in join_node.
                left_key_set | join_node.left_cond_cols if smb__lhfkm <
                join_node.n_left_table_cols)
            if not (ebmvp__npmoh or pltr__qny):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (rreeo__fiaqf | ovs__exuv)
            block_use_map[uovcq__tihjd] = (bgptp__cmvu | rreeo__fiaqf |
                ovs__exuv, ebmvp__npmoh or pltr__qny, False)
    if join_node.has_live_right_table_var:
        xjxvc__ywp = join_node.right_vars[0].name
        bgptp__cmvu, mmow__vltu, ewnd__flwm = block_use_map[xjxvc__ywp]
        if not (mmow__vltu or ewnd__flwm):
            afcbr__woqc = set([join_node.out_to_input_col_map[smb__lhfkm][1
                ] for smb__lhfkm in vdo__hdin if join_node.
                out_to_input_col_map[smb__lhfkm][0] == 'right'])
            heqch__zvey = set(smb__lhfkm for smb__lhfkm in join_node.
                right_key_set | join_node.right_cond_cols if smb__lhfkm <
                join_node.n_right_table_cols)
            if not (ebmvp__npmoh or pltr__qny):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (afcbr__woqc | heqch__zvey)
            block_use_map[xjxvc__ywp] = (bgptp__cmvu | afcbr__woqc |
                heqch__zvey, ebmvp__npmoh or pltr__qny, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({ksamq__pcjkw.name for ksamq__pcjkw in join_node.
        get_live_left_vars()})
    use_set.update({ksamq__pcjkw.name for ksamq__pcjkw in join_node.
        get_live_right_vars()})
    def_set.update({ksamq__pcjkw.name for ksamq__pcjkw in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    ghpqv__nfj = set(ksamq__pcjkw.name for ksamq__pcjkw in join_node.
        get_live_out_vars())
    return set(), ghpqv__nfj


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(wovbj__puhv, var_dict) for
        wovbj__puhv in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(wovbj__puhv, var_dict
        ) for wovbj__puhv in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(wovbj__puhv,
        var_dict) for wovbj__puhv in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for ehox__ucqj in join_node.get_live_out_vars():
        definitions[ehox__ucqj.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        ocy__wsat = join_node.loc.strformat()
        gbiri__sfkf = [join_node.left_col_names[smb__lhfkm] for smb__lhfkm in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        bntf__xnue = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', bntf__xnue,
            ocy__wsat, gbiri__sfkf)
        qlnf__emrl = [join_node.right_col_names[smb__lhfkm] for smb__lhfkm in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        bntf__xnue = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', bntf__xnue,
            ocy__wsat, qlnf__emrl)
        kho__tehng = [join_node.out_col_names[smb__lhfkm] for smb__lhfkm in
            sorted(join_node.get_out_table_used_cols())]
        bntf__xnue = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', bntf__xnue,
            ocy__wsat, kho__tehng)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    jqn__wvraj = len(join_node.left_keys)
    out_physical_to_logical_list = []
    if join_node.has_live_out_table_var:
        out_table_type = typemap[join_node.get_out_table_var().name]
    else:
        out_table_type = types.none
    if join_node.has_live_out_index_var:
        index_col_type = typemap[join_node.get_out_index_var().name]
    else:
        index_col_type = types.none
    if join_node.extra_data_col_num != -1:
        out_physical_to_logical_list.append(join_node.extra_data_col_num)
    left_key_in_output = []
    right_key_in_output = []
    left_used_key_nums = set()
    right_used_key_nums = set()
    left_logical_physical_map = {}
    right_logical_physical_map = {}
    left_physical_to_logical_list = []
    right_physical_to_logical_list = []
    mpe__biv = 0
    tspf__apz = 0
    mbb__npwp = []
    for vtor__rikh in join_node.left_keys:
        oqlxy__frco = join_node.left_var_map[vtor__rikh]
        if not join_node.is_left_table:
            mbb__npwp.append(join_node.left_vars[oqlxy__frco])
        tpwu__qbu = 1
        ssd__dpzxh = join_node.left_to_output_map[oqlxy__frco]
        if vtor__rikh == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == oqlxy__frco):
                out_physical_to_logical_list.append(ssd__dpzxh)
                left_used_key_nums.add(oqlxy__frco)
            else:
                tpwu__qbu = 0
        elif ssd__dpzxh not in join_node.out_used_cols:
            tpwu__qbu = 0
        elif oqlxy__frco in left_used_key_nums:
            tpwu__qbu = 0
        else:
            left_used_key_nums.add(oqlxy__frco)
            out_physical_to_logical_list.append(ssd__dpzxh)
        left_physical_to_logical_list.append(oqlxy__frco)
        left_logical_physical_map[oqlxy__frco] = mpe__biv
        mpe__biv += 1
        left_key_in_output.append(tpwu__qbu)
    mbb__npwp = tuple(mbb__npwp)
    luiq__kyb = []
    for smb__lhfkm in range(len(join_node.left_col_names)):
        if (smb__lhfkm not in join_node.left_dead_var_inds and smb__lhfkm
             not in join_node.left_key_set):
            if not join_node.is_left_table:
                ksamq__pcjkw = join_node.left_vars[smb__lhfkm]
                luiq__kyb.append(ksamq__pcjkw)
            yuex__lir = 1
            ift__zrq = 1
            ssd__dpzxh = join_node.left_to_output_map[smb__lhfkm]
            if smb__lhfkm in join_node.left_cond_cols:
                if ssd__dpzxh not in join_node.out_used_cols:
                    yuex__lir = 0
                left_key_in_output.append(yuex__lir)
            elif smb__lhfkm in join_node.left_dead_var_inds:
                yuex__lir = 0
                ift__zrq = 0
            if yuex__lir:
                out_physical_to_logical_list.append(ssd__dpzxh)
            if ift__zrq:
                left_physical_to_logical_list.append(smb__lhfkm)
                left_logical_physical_map[smb__lhfkm] = mpe__biv
                mpe__biv += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            luiq__kyb.append(join_node.left_vars[join_node.index_col_num])
        ssd__dpzxh = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(ssd__dpzxh)
        left_physical_to_logical_list.append(join_node.index_col_num)
    luiq__kyb = tuple(luiq__kyb)
    if join_node.is_left_table:
        luiq__kyb = tuple(join_node.get_live_left_vars())
    aaag__tij = []
    for smb__lhfkm, vtor__rikh in enumerate(join_node.right_keys):
        oqlxy__frco = join_node.right_var_map[vtor__rikh]
        if not join_node.is_right_table:
            aaag__tij.append(join_node.right_vars[oqlxy__frco])
        if not join_node.vect_same_key[smb__lhfkm] and not join_node.is_join:
            tpwu__qbu = 1
            if oqlxy__frco not in join_node.right_to_output_map:
                tpwu__qbu = 0
            else:
                ssd__dpzxh = join_node.right_to_output_map[oqlxy__frco]
                if vtor__rikh == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        oqlxy__frco):
                        out_physical_to_logical_list.append(ssd__dpzxh)
                        right_used_key_nums.add(oqlxy__frco)
                    else:
                        tpwu__qbu = 0
                elif ssd__dpzxh not in join_node.out_used_cols:
                    tpwu__qbu = 0
                elif oqlxy__frco in right_used_key_nums:
                    tpwu__qbu = 0
                else:
                    right_used_key_nums.add(oqlxy__frco)
                    out_physical_to_logical_list.append(ssd__dpzxh)
            right_key_in_output.append(tpwu__qbu)
        right_physical_to_logical_list.append(oqlxy__frco)
        right_logical_physical_map[oqlxy__frco] = tspf__apz
        tspf__apz += 1
    aaag__tij = tuple(aaag__tij)
    paorr__rxrui = []
    for smb__lhfkm in range(len(join_node.right_col_names)):
        if (smb__lhfkm not in join_node.right_dead_var_inds and smb__lhfkm
             not in join_node.right_key_set):
            if not join_node.is_right_table:
                paorr__rxrui.append(join_node.right_vars[smb__lhfkm])
            yuex__lir = 1
            ift__zrq = 1
            ssd__dpzxh = join_node.right_to_output_map[smb__lhfkm]
            if smb__lhfkm in join_node.right_cond_cols:
                if ssd__dpzxh not in join_node.out_used_cols:
                    yuex__lir = 0
                right_key_in_output.append(yuex__lir)
            elif smb__lhfkm in join_node.right_dead_var_inds:
                yuex__lir = 0
                ift__zrq = 0
            if yuex__lir:
                out_physical_to_logical_list.append(ssd__dpzxh)
            if ift__zrq:
                right_physical_to_logical_list.append(smb__lhfkm)
                right_logical_physical_map[smb__lhfkm] = tspf__apz
                tspf__apz += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            paorr__rxrui.append(join_node.right_vars[join_node.index_col_num])
        ssd__dpzxh = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(ssd__dpzxh)
        right_physical_to_logical_list.append(join_node.index_col_num)
    paorr__rxrui = tuple(paorr__rxrui)
    if join_node.is_right_table:
        paorr__rxrui = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    xhb__apbw = mbb__npwp + aaag__tij + luiq__kyb + paorr__rxrui
    ocdti__lih = tuple(typemap[ksamq__pcjkw.name] for ksamq__pcjkw in xhb__apbw
        )
    left_other_names = tuple('t1_c' + str(smb__lhfkm) for smb__lhfkm in
        range(len(luiq__kyb)))
    right_other_names = tuple('t2_c' + str(smb__lhfkm) for smb__lhfkm in
        range(len(paorr__rxrui)))
    if join_node.is_left_table:
        zziid__dcwq = ()
    else:
        zziid__dcwq = tuple('t1_key' + str(smb__lhfkm) for smb__lhfkm in
            range(jqn__wvraj))
    if join_node.is_right_table:
        dqxj__qmeq = ()
    else:
        dqxj__qmeq = tuple('t2_key' + str(smb__lhfkm) for smb__lhfkm in
            range(jqn__wvraj))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(zziid__dcwq + dqxj__qmeq +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            txf__kpw = typemap[join_node.left_vars[0].name]
        else:
            txf__kpw = types.none
        for pur__ggnvk in left_physical_to_logical_list:
            if pur__ggnvk < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                seh__fnwyr = txf__kpw.arr_types[pur__ggnvk]
            else:
                seh__fnwyr = typemap[join_node.left_vars[-1].name]
            if pur__ggnvk in join_node.left_key_set:
                left_key_types.append(seh__fnwyr)
            else:
                left_other_types.append(seh__fnwyr)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[ksamq__pcjkw.name] for ksamq__pcjkw in
            mbb__npwp)
        left_other_types = tuple([typemap[vtor__rikh.name] for vtor__rikh in
            luiq__kyb])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            txf__kpw = typemap[join_node.right_vars[0].name]
        else:
            txf__kpw = types.none
        for pur__ggnvk in right_physical_to_logical_list:
            if pur__ggnvk < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                seh__fnwyr = txf__kpw.arr_types[pur__ggnvk]
            else:
                seh__fnwyr = typemap[join_node.right_vars[-1].name]
            if pur__ggnvk in join_node.right_key_set:
                right_key_types.append(seh__fnwyr)
            else:
                right_other_types.append(seh__fnwyr)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[ksamq__pcjkw.name] for ksamq__pcjkw in
            aaag__tij)
        right_other_types = tuple([typemap[vtor__rikh.name] for vtor__rikh in
            paorr__rxrui])
    matched_key_types = []
    for smb__lhfkm in range(jqn__wvraj):
        bvdy__bunhc = _match_join_key_types(left_key_types[smb__lhfkm],
            right_key_types[smb__lhfkm], loc)
        glbs[f'key_type_{smb__lhfkm}'] = bvdy__bunhc
        matched_key_types.append(bvdy__bunhc)
    if join_node.is_left_table:
        fct__zblo = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if fct__zblo:
            rkh__ueyh = False
            niya__mlnnr = False
            qhp__dbc = None
            if join_node.has_live_left_table_var:
                qynx__nmse = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                qynx__nmse = None
            for xxrg__vzetv, seh__fnwyr in fct__zblo.items():
                if xxrg__vzetv < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    qynx__nmse[xxrg__vzetv] = seh__fnwyr
                    rkh__ueyh = True
                else:
                    qhp__dbc = seh__fnwyr
                    niya__mlnnr = True
            if rkh__ueyh:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(qynx__nmse))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if niya__mlnnr:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = qhp__dbc
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({zziid__dcwq[smb__lhfkm]}, key_type_{smb__lhfkm})'
             if left_key_types[smb__lhfkm] != matched_key_types[smb__lhfkm]
             else f'{zziid__dcwq[smb__lhfkm]}' for smb__lhfkm in range(
            jqn__wvraj)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        fct__zblo = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if fct__zblo:
            rkh__ueyh = False
            niya__mlnnr = False
            qhp__dbc = None
            if join_node.has_live_right_table_var:
                qynx__nmse = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                qynx__nmse = None
            for xxrg__vzetv, seh__fnwyr in fct__zblo.items():
                if xxrg__vzetv < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    qynx__nmse[xxrg__vzetv] = seh__fnwyr
                    rkh__ueyh = True
                else:
                    qhp__dbc = seh__fnwyr
                    niya__mlnnr = True
            if rkh__ueyh:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(qynx__nmse))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if niya__mlnnr:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = qhp__dbc
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({dqxj__qmeq[smb__lhfkm]}, key_type_{smb__lhfkm})'
             if right_key_types[smb__lhfkm] != matched_key_types[smb__lhfkm
            ] else f'{dqxj__qmeq[smb__lhfkm]}' for smb__lhfkm in range(
            jqn__wvraj)))
        func_text += '    data_right = ({}{})\n'.format(','.join(
            right_other_names), ',' if len(right_other_names) != 0 else '')
    general_cond_cfunc, left_col_nums, right_col_nums = (
        _gen_general_cond_cfunc(join_node, typemap,
        left_logical_physical_map, right_logical_physical_map))
    if join_node.how == 'asof':
        if left_parallel or right_parallel:
            assert left_parallel and right_parallel, 'pd.merge_asof requires both left and right to be replicated or distributed'
            func_text += """    t2_keys, data_right = parallel_asof_comm(t1_keys, t2_keys, data_right)
"""
        func_text += """    out_t1_keys, out_t2_keys, out_data_left, out_data_right = bodo.ir.join.local_merge_asof(t1_keys, t2_keys, data_left, data_right)
"""
    else:
        func_text += _gen_local_hash_join(join_node, left_key_types,
            right_key_types, matched_key_types, left_other_names,
            right_other_names, left_other_types, right_other_types,
            left_key_in_output, right_key_in_output, left_parallel,
            right_parallel, glbs, out_physical_to_logical_list,
            out_table_type, index_col_type, join_node.
            get_out_table_used_cols(), left_used_key_nums,
            right_used_key_nums, general_cond_cfunc, left_col_nums,
            right_col_nums, left_physical_to_logical_list,
            right_physical_to_logical_list)
    if join_node.how == 'asof':
        for smb__lhfkm in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(smb__lhfkm,
                smb__lhfkm)
        for smb__lhfkm in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                smb__lhfkm, smb__lhfkm)
        for smb__lhfkm in range(jqn__wvraj):
            func_text += (
                f'    t1_keys_{smb__lhfkm} = out_t1_keys[{smb__lhfkm}]\n')
        for smb__lhfkm in range(jqn__wvraj):
            func_text += (
                f'    t2_keys_{smb__lhfkm} = out_t2_keys[{smb__lhfkm}]\n')
    znuj__ajh = {}
    exec(func_text, {}, znuj__ajh)
    kvwex__tnk = znuj__ajh['f']
    glbs.update({'bodo': bodo, 'np': np, 'pd': pd, 'parallel_asof_comm':
        parallel_asof_comm, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'hash_join_table':
        hash_join_table, 'delete_table': delete_table,
        'add_join_gen_cond_cfunc_sym': add_join_gen_cond_cfunc_sym,
        'get_join_cond_addr': get_join_cond_addr, 'key_in_output': np.array
        (left_key_in_output + right_key_in_output, dtype=np.bool_),
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    if general_cond_cfunc:
        glbs.update({'general_cond_cfunc': general_cond_cfunc})
    rmi__npk = compile_to_numba_ir(kvwex__tnk, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=ocdti__lih, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(rmi__npk, xhb__apbw)
    nve__zuk = rmi__npk.body[:-3]
    if join_node.has_live_out_index_var:
        nve__zuk[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        nve__zuk[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        nve__zuk.pop(-1)
    elif not join_node.has_live_out_table_var:
        nve__zuk.pop(-2)
    return nve__zuk


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    sma__emi = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{sma__emi}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        left_logical_physical_map, join_node.left_var_map, typemap,
        join_node.left_vars, table_getitem_funcs, func_text, 'left',
        join_node.left_key_set, na_check_name, join_node.is_left_table)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        right_logical_physical_map, join_node.right_var_map, typemap,
        join_node.right_vars, table_getitem_funcs, func_text, 'right',
        join_node.right_key_set, na_check_name, join_node.is_right_table)
    func_text += f'  return {expr}'
    znuj__ajh = {}
    exec(func_text, table_getitem_funcs, znuj__ajh)
    wrhey__ilrsq = znuj__ajh[f'bodo_join_gen_cond{sma__emi}']
    dyrrc__cpupw = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    tjwt__fpmbc = numba.cfunc(dyrrc__cpupw, nopython=True)(wrhey__ilrsq)
    join_gen_cond_cfunc[tjwt__fpmbc.native_name] = tjwt__fpmbc
    join_gen_cond_cfunc_addr[tjwt__fpmbc.native_name] = tjwt__fpmbc.address
    return tjwt__fpmbc, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    djhma__qyodb = []
    for vtor__rikh, kuyuk__eiud in name_to_var_map.items():
        cmv__hcvfb = f'({table_name}.{vtor__rikh})'
        if cmv__hcvfb not in expr:
            continue
        rfhho__mfj = f'getitem_{table_name}_val_{kuyuk__eiud}'
        ikjvu__qwvdu = f'_bodo_{table_name}_val_{kuyuk__eiud}'
        if is_table_var:
            aim__evdow = typemap[col_vars[0].name].arr_types[kuyuk__eiud]
        else:
            aim__evdow = typemap[col_vars[kuyuk__eiud].name]
        if is_str_arr_type(aim__evdow) or aim__evdow == bodo.binary_array_type:
            func_text += f"""  {ikjvu__qwvdu}, {ikjvu__qwvdu}_size = {rfhho__mfj}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {ikjvu__qwvdu} = bodo.libs.str_arr_ext.decode_utf8({ikjvu__qwvdu}, {ikjvu__qwvdu}_size)
"""
        else:
            func_text += (
                f'  {ikjvu__qwvdu} = {rfhho__mfj}({table_name}_data1, {table_name}_ind)\n'
                )
        pgct__shxk = logical_to_physical_ind[kuyuk__eiud]
        table_getitem_funcs[rfhho__mfj
            ] = bodo.libs.array._gen_row_access_intrinsic(aim__evdow,
            pgct__shxk)
        expr = expr.replace(cmv__hcvfb, ikjvu__qwvdu)
        tqylu__wdxt = f'({na_check_name}.{table_name}.{vtor__rikh})'
        if tqylu__wdxt in expr:
            bzjl__xbja = f'nacheck_{table_name}_val_{kuyuk__eiud}'
            jxfm__unt = f'_bodo_isna_{table_name}_val_{kuyuk__eiud}'
            if isinstance(aim__evdow, bodo.libs.int_arr_ext.IntegerArrayType
                ) or aim__evdow in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(aim__evdow):
                func_text += f"""  {jxfm__unt} = {bzjl__xbja}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {jxfm__unt} = {bzjl__xbja}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[bzjl__xbja
                ] = bodo.libs.array._gen_row_na_check_intrinsic(aim__evdow,
                pgct__shxk)
            expr = expr.replace(tqylu__wdxt, jxfm__unt)
        if kuyuk__eiud not in key_set:
            djhma__qyodb.append(pgct__shxk)
    return expr, func_text, djhma__qyodb


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as bvcsp__evuln:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    jmhs__zlsmo = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[ksamq__pcjkw.name] in jmhs__zlsmo for
        ksamq__pcjkw in join_node.get_live_left_vars())
    right_parallel = all(array_dists[ksamq__pcjkw.name] in jmhs__zlsmo for
        ksamq__pcjkw in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[ksamq__pcjkw.name] in jmhs__zlsmo for
            ksamq__pcjkw in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[ksamq__pcjkw.name] in jmhs__zlsmo for
            ksamq__pcjkw in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[ksamq__pcjkw.name] in jmhs__zlsmo for
            ksamq__pcjkw in join_node.get_live_out_vars())
    return left_parallel, right_parallel


def _gen_local_hash_join(join_node, left_key_types, right_key_types,
    matched_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, left_key_in_output,
    right_key_in_output, left_parallel, right_parallel, glbs,
    out_physical_to_logical_list, out_table_type, index_col_type,
    out_table_used_cols, left_used_key_nums, right_used_key_nums,
    general_cond_cfunc, left_col_nums, right_col_nums,
    left_physical_to_logical_list, right_physical_to_logical_list):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    lpz__nlt = set(left_col_nums)
    bqs__qatrd = set(right_col_nums)
    ohoa__prcer = join_node.vect_same_key
    zacfm__vjyww = []
    for smb__lhfkm in range(len(left_key_types)):
        if left_key_in_output[smb__lhfkm]:
            zacfm__vjyww.append(needs_typechange(matched_key_types[
                smb__lhfkm], join_node.is_right, ohoa__prcer[smb__lhfkm]))
    lzcgd__vkedm = len(left_key_types)
    pzf__igsy = 0
    ycwdw__kxeud = left_physical_to_logical_list[len(left_key_types):]
    for smb__lhfkm, pur__ggnvk in enumerate(ycwdw__kxeud):
        ktvh__fwiqb = True
        if pur__ggnvk in lpz__nlt:
            ktvh__fwiqb = left_key_in_output[lzcgd__vkedm]
            lzcgd__vkedm += 1
        if ktvh__fwiqb:
            zacfm__vjyww.append(needs_typechange(left_other_types[
                smb__lhfkm], join_node.is_right, False))
    for smb__lhfkm in range(len(right_key_types)):
        if not ohoa__prcer[smb__lhfkm] and not join_node.is_join:
            if right_key_in_output[pzf__igsy]:
                zacfm__vjyww.append(needs_typechange(matched_key_types[
                    smb__lhfkm], join_node.is_left, False))
            pzf__igsy += 1
    zadev__twoku = right_physical_to_logical_list[len(right_key_types):]
    for smb__lhfkm, pur__ggnvk in enumerate(zadev__twoku):
        ktvh__fwiqb = True
        if pur__ggnvk in bqs__qatrd:
            ktvh__fwiqb = right_key_in_output[pzf__igsy]
            pzf__igsy += 1
        if ktvh__fwiqb:
            zacfm__vjyww.append(needs_typechange(right_other_types[
                smb__lhfkm], join_node.is_left, False))
    jqn__wvraj = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            qsfj__mgy = left_other_names[1:]
            ivinu__gtmq = left_other_names[0]
        else:
            qsfj__mgy = left_other_names
            ivinu__gtmq = None
        ypfl__apjho = '()' if len(qsfj__mgy) == 0 else f'({qsfj__mgy[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({ivinu__gtmq}, {ypfl__apjho}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        mbe__acr = []
        for smb__lhfkm in range(jqn__wvraj):
            mbe__acr.append('t1_keys[{}]'.format(smb__lhfkm))
        for smb__lhfkm in range(len(left_other_names)):
            mbe__acr.append('data_left[{}]'.format(smb__lhfkm))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(plo__oom) for plo__oom in mbe__acr))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            tgnt__sol = right_other_names[1:]
            ivinu__gtmq = right_other_names[0]
        else:
            tgnt__sol = right_other_names
            ivinu__gtmq = None
        ypfl__apjho = '()' if len(tgnt__sol) == 0 else f'({tgnt__sol[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({ivinu__gtmq}, {ypfl__apjho}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        mhm__jip = []
        for smb__lhfkm in range(jqn__wvraj):
            mhm__jip.append('t2_keys[{}]'.format(smb__lhfkm))
        for smb__lhfkm in range(len(right_other_names)):
            mhm__jip.append('data_right[{}]'.format(smb__lhfkm))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(plo__oom) for plo__oom in mhm__jip))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(ohoa__prcer, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(zacfm__vjyww, dtype=np.int64)
    glbs['left_table_cond_columns'] = np.array(left_col_nums if len(
        left_col_nums) > 0 else [-1], dtype=np.int64)
    glbs['right_table_cond_columns'] = np.array(right_col_nums if len(
        right_col_nums) > 0 else [-1], dtype=np.int64)
    if general_cond_cfunc:
        func_text += f"""    cfunc_cond = add_join_gen_cond_cfunc_sym(general_cond_cfunc, '{general_cond_cfunc.native_name}')
"""
        func_text += (
            f"    cfunc_cond = get_join_cond_addr('{general_cond_cfunc.native_name}')\n"
            )
    else:
        func_text += '    cfunc_cond = 0\n'
    func_text += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    func_text += (
        """    out_table = hash_join_table(table_left, table_right, {}, {}, {}, {}, {}, vect_same_key.ctypes, key_in_output.ctypes, vect_need_typechange.ctypes, {}, {}, {}, {}, {}, {}, cfunc_cond, left_table_cond_columns.ctypes, {}, right_table_cond_columns.ctypes, {}, total_rows_np.ctypes)
"""
        .format(left_parallel, right_parallel, jqn__wvraj, len(ycwdw__kxeud
        ), len(zadev__twoku), join_node.is_left, join_node.is_right,
        join_node.is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    bfw__rqfgi = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {bfw__rqfgi}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        miw__atpb = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{miw__atpb}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        fct__zblo = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        fct__zblo.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        rkh__ueyh = False
        niya__mlnnr = False
        if join_node.has_live_out_table_var:
            qynx__nmse = list(out_table_type.arr_types)
        else:
            qynx__nmse = None
        for xxrg__vzetv, seh__fnwyr in fct__zblo.items():
            if xxrg__vzetv < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                qynx__nmse[xxrg__vzetv] = seh__fnwyr
                rkh__ueyh = True
            else:
                qhp__dbc = seh__fnwyr
                niya__mlnnr = True
        if rkh__ueyh:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            jmeqd__ckjca = bodo.TableType(tuple(qynx__nmse))
            glbs['py_table_type'] = jmeqd__ckjca
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if niya__mlnnr:
            glbs['index_col_type'] = qhp__dbc
            glbs['index_cast_type'] = index_col_type
            func_text += (
                f'    index_var = bodo.utils.utils.astype(index_var, index_cast_type)\n'
                )
    func_text += f'    out_table = T\n'
    func_text += f'    out_index = index_var\n'
    return func_text


def determine_table_cast_map(matched_key_types: List[types.Type], key_types:
    List[types.Type], used_key_nums: Optional[Set[int]], output_map:
    Optional[Dict[int, int]], convert_dict_col: bool, loc: ir.Loc):
    fct__zblo: Dict[int, types.Type] = {}
    jqn__wvraj = len(matched_key_types)
    for smb__lhfkm in range(jqn__wvraj):
        if used_key_nums is None or smb__lhfkm in used_key_nums:
            if matched_key_types[smb__lhfkm] != key_types[smb__lhfkm] and (
                convert_dict_col or key_types[smb__lhfkm] != bodo.
                dict_str_arr_type):
                if output_map:
                    miw__atpb = output_map[smb__lhfkm]
                else:
                    miw__atpb = smb__lhfkm
                fct__zblo[miw__atpb] = matched_key_types[smb__lhfkm]
    return fct__zblo


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    pfenl__gxon = bodo.libs.distributed_api.get_size()
    iyx__vvw = np.empty(pfenl__gxon, left_key_arrs[0].dtype)
    nivj__itrje = np.empty(pfenl__gxon, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(iyx__vvw, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(nivj__itrje, left_key_arrs[0][-1])
    lowmd__sklcx = np.zeros(pfenl__gxon, np.int32)
    khyg__ujws = np.zeros(pfenl__gxon, np.int32)
    mnxmh__araw = np.zeros(pfenl__gxon, np.int32)
    pstmo__revz = right_key_arrs[0][0]
    wql__gpwmt = right_key_arrs[0][-1]
    oenzv__eeynd = -1
    smb__lhfkm = 0
    while smb__lhfkm < pfenl__gxon - 1 and nivj__itrje[smb__lhfkm
        ] < pstmo__revz:
        smb__lhfkm += 1
    while smb__lhfkm < pfenl__gxon and iyx__vvw[smb__lhfkm] <= wql__gpwmt:
        oenzv__eeynd, ucehf__rsu = _count_overlap(right_key_arrs[0],
            iyx__vvw[smb__lhfkm], nivj__itrje[smb__lhfkm])
        if oenzv__eeynd != 0:
            oenzv__eeynd -= 1
            ucehf__rsu += 1
        lowmd__sklcx[smb__lhfkm] = ucehf__rsu
        khyg__ujws[smb__lhfkm] = oenzv__eeynd
        smb__lhfkm += 1
    while smb__lhfkm < pfenl__gxon:
        lowmd__sklcx[smb__lhfkm] = 1
        khyg__ujws[smb__lhfkm] = len(right_key_arrs[0]) - 1
        smb__lhfkm += 1
    bodo.libs.distributed_api.alltoall(lowmd__sklcx, mnxmh__araw, 1)
    orsc__yasmh = mnxmh__araw.sum()
    qhrtb__xgt = np.empty(orsc__yasmh, right_key_arrs[0].dtype)
    tey__xki = alloc_arr_tup(orsc__yasmh, right_data)
    zywph__sjddc = bodo.ir.join.calc_disp(mnxmh__araw)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], qhrtb__xgt,
        lowmd__sklcx, mnxmh__araw, khyg__ujws, zywph__sjddc)
    bodo.libs.distributed_api.alltoallv_tup(right_data, tey__xki,
        lowmd__sklcx, mnxmh__araw, khyg__ujws, zywph__sjddc)
    return (qhrtb__xgt,), tey__xki


@numba.njit
def _count_overlap(r_key_arr, start, end):
    ucehf__rsu = 0
    oenzv__eeynd = 0
    art__ntcj = 0
    while art__ntcj < len(r_key_arr) and r_key_arr[art__ntcj] < start:
        oenzv__eeynd += 1
        art__ntcj += 1
    while art__ntcj < len(r_key_arr) and start <= r_key_arr[art__ntcj] <= end:
        art__ntcj += 1
        ucehf__rsu += 1
    return oenzv__eeynd, ucehf__rsu


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    etvxx__vutv = np.empty_like(arr)
    etvxx__vutv[0] = 0
    for smb__lhfkm in range(1, len(arr)):
        etvxx__vutv[smb__lhfkm] = etvxx__vutv[smb__lhfkm - 1] + arr[
            smb__lhfkm - 1]
    return etvxx__vutv


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    jixpj__doakt = len(left_keys[0])
    rzap__wmn = len(right_keys[0])
    vsq__pxor = alloc_arr_tup(jixpj__doakt, left_keys)
    zel__idfh = alloc_arr_tup(jixpj__doakt, right_keys)
    odid__spe = alloc_arr_tup(jixpj__doakt, data_left)
    hmyam__xjed = alloc_arr_tup(jixpj__doakt, data_right)
    ryian__xrwh = 0
    ocf__faf = 0
    for ryian__xrwh in range(jixpj__doakt):
        if ocf__faf < 0:
            ocf__faf = 0
        while ocf__faf < rzap__wmn and getitem_arr_tup(right_keys, ocf__faf
            ) <= getitem_arr_tup(left_keys, ryian__xrwh):
            ocf__faf += 1
        ocf__faf -= 1
        setitem_arr_tup(vsq__pxor, ryian__xrwh, getitem_arr_tup(left_keys,
            ryian__xrwh))
        setitem_arr_tup(odid__spe, ryian__xrwh, getitem_arr_tup(data_left,
            ryian__xrwh))
        if ocf__faf >= 0:
            setitem_arr_tup(zel__idfh, ryian__xrwh, getitem_arr_tup(
                right_keys, ocf__faf))
            setitem_arr_tup(hmyam__xjed, ryian__xrwh, getitem_arr_tup(
                data_right, ocf__faf))
        else:
            bodo.libs.array_kernels.setna_tup(zel__idfh, ryian__xrwh)
            bodo.libs.array_kernels.setna_tup(hmyam__xjed, ryian__xrwh)
    return vsq__pxor, zel__idfh, odid__spe, hmyam__xjed
