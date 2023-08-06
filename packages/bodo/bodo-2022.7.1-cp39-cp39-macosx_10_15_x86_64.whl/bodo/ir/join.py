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
        ehb__tbv = func.signature
        gxu__qwf = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        cubq__twv = cgutils.get_or_insert_function(builder.module, gxu__qwf,
            sym._literal_value)
        builder.call(cubq__twv, [context.get_constant_null(ehb__tbv.args[0]
            ), context.get_constant_null(ehb__tbv.args[1]), context.
            get_constant_null(ehb__tbv.args[2]), context.get_constant_null(
            ehb__tbv.args[3]), context.get_constant_null(ehb__tbv.args[4]),
            context.get_constant_null(ehb__tbv.args[5]), context.
            get_constant(types.int64, 0), context.get_constant(types.int64, 0)]
            )
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
        req__yto = left_df_type.columns
        rizlg__drqcv = right_df_type.columns
        self.left_col_names = req__yto
        self.right_col_names = rizlg__drqcv
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(req__yto) if self.is_left_table else 0
        self.n_right_table_cols = len(rizlg__drqcv
            ) if self.is_right_table else 0
        wqk__jxcab = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        tnd__eibzq = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(wqk__jxcab)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(tnd__eibzq)
        self.left_var_map = {kri__uyl: euidu__vqa for euidu__vqa, kri__uyl in
            enumerate(req__yto)}
        self.right_var_map = {kri__uyl: euidu__vqa for euidu__vqa, kri__uyl in
            enumerate(rizlg__drqcv)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = wqk__jxcab
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = tnd__eibzq
        self.left_key_set = set(self.left_var_map[kri__uyl] for kri__uyl in
            left_keys)
        self.right_key_set = set(self.right_var_map[kri__uyl] for kri__uyl in
            right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[kri__uyl] for
                kri__uyl in req__yto if f'(left.{kri__uyl})' in gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[kri__uyl] for
                kri__uyl in rizlg__drqcv if f'(right.{kri__uyl})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        xdr__oen: int = -1
        edpbb__izocb = set(left_keys) & set(right_keys)
        xblik__tgoor = set(req__yto) & set(rizlg__drqcv)
        cieh__twybh = xblik__tgoor - edpbb__izocb
        gte__towmr: Dict[int, (Literal['left', 'right'], int)] = {}
        gzwe__tov: Dict[int, int] = {}
        vqdp__ywwdm: Dict[int, int] = {}
        for euidu__vqa, kri__uyl in enumerate(req__yto):
            if kri__uyl in cieh__twybh:
                anluu__chw = str(kri__uyl) + suffix_left
                rplr__rglzo = out_df_type.column_index[anluu__chw]
                if (right_index and not left_index and euidu__vqa in self.
                    left_key_set):
                    xdr__oen = out_df_type.column_index[kri__uyl]
                    gte__towmr[xdr__oen] = 'left', euidu__vqa
            else:
                rplr__rglzo = out_df_type.column_index[kri__uyl]
            gte__towmr[rplr__rglzo] = 'left', euidu__vqa
            gzwe__tov[euidu__vqa] = rplr__rglzo
        for euidu__vqa, kri__uyl in enumerate(rizlg__drqcv):
            if kri__uyl not in edpbb__izocb:
                if kri__uyl in cieh__twybh:
                    ekv__vdxm = str(kri__uyl) + suffix_right
                    rplr__rglzo = out_df_type.column_index[ekv__vdxm]
                    if (left_index and not right_index and euidu__vqa in
                        self.right_key_set):
                        xdr__oen = out_df_type.column_index[kri__uyl]
                        gte__towmr[xdr__oen] = 'right', euidu__vqa
                else:
                    rplr__rglzo = out_df_type.column_index[kri__uyl]
                gte__towmr[rplr__rglzo] = 'right', euidu__vqa
                vqdp__ywwdm[euidu__vqa] = rplr__rglzo
        if self.left_vars[-1] is not None:
            gzwe__tov[wqk__jxcab] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            vqdp__ywwdm[tnd__eibzq] = self.n_out_table_cols
        self.out_to_input_col_map = gte__towmr
        self.left_to_output_map = gzwe__tov
        self.right_to_output_map = vqdp__ywwdm
        self.extra_data_col_num = xdr__oen
        if len(out_data_vars) > 1:
            alupc__ffmse = 'left' if right_index else 'right'
            if alupc__ffmse == 'left':
                xvyy__annc = wqk__jxcab
            elif alupc__ffmse == 'right':
                xvyy__annc = tnd__eibzq
        else:
            alupc__ffmse = None
            xvyy__annc = -1
        self.index_source = alupc__ffmse
        self.index_col_num = xvyy__annc
        pwxt__tdne = []
        hmsg__hdts = len(left_keys)
        for vnzqi__ucpw in range(hmsg__hdts):
            rjly__atgj = left_keys[vnzqi__ucpw]
            kjfon__kyrcg = right_keys[vnzqi__ucpw]
            pwxt__tdne.append(rjly__atgj == kjfon__kyrcg)
        self.vect_same_key = pwxt__tdne

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
        for czv__rzjs in self.left_vars:
            if czv__rzjs is not None:
                vars.append(czv__rzjs)
        return vars

    def get_live_right_vars(self):
        vars = []
        for czv__rzjs in self.right_vars:
            if czv__rzjs is not None:
                vars.append(czv__rzjs)
        return vars

    def get_live_out_vars(self):
        vars = []
        for czv__rzjs in self.out_data_vars:
            if czv__rzjs is not None:
                vars.append(czv__rzjs)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        gpktr__prh = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[gpktr__prh])
                gpktr__prh += 1
            else:
                left_vars.append(None)
            start = 1
        vicai__lvsz = max(self.n_left_table_cols - 1, 0)
        for euidu__vqa in range(start, len(self.left_vars)):
            if euidu__vqa + vicai__lvsz in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[gpktr__prh])
                gpktr__prh += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        gpktr__prh = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[gpktr__prh])
                gpktr__prh += 1
            else:
                right_vars.append(None)
            start = 1
        vicai__lvsz = max(self.n_right_table_cols - 1, 0)
        for euidu__vqa in range(start, len(self.right_vars)):
            if euidu__vqa + vicai__lvsz in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[gpktr__prh])
                gpktr__prh += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        tput__psq = [self.has_live_out_table_var, self.has_live_out_index_var]
        gpktr__prh = 0
        for euidu__vqa in range(len(self.out_data_vars)):
            if not tput__psq[euidu__vqa]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[gpktr__prh])
                gpktr__prh += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {euidu__vqa for euidu__vqa in self.out_used_cols if 
            euidu__vqa < self.n_out_table_cols}

    def __repr__(self):
        howd__pajg = ', '.join([f'{kri__uyl}' for kri__uyl in self.
            left_col_names])
        ptq__cdqzi = f'left={{{howd__pajg}}}'
        howd__pajg = ', '.join([f'{kri__uyl}' for kri__uyl in self.
            right_col_names])
        mincy__vgjpr = f'right={{{howd__pajg}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, ptq__cdqzi, mincy__vgjpr)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    kxvzn__wna = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    cti__ixh = []
    wyfr__ndssj = join_node.get_live_left_vars()
    for dnzzr__gpa in wyfr__ndssj:
        uogr__vrmxc = typemap[dnzzr__gpa.name]
        rfxnm__ego = equiv_set.get_shape(dnzzr__gpa)
        if rfxnm__ego:
            cti__ixh.append(rfxnm__ego[0])
    if len(cti__ixh) > 1:
        equiv_set.insert_equiv(*cti__ixh)
    cti__ixh = []
    wyfr__ndssj = list(join_node.get_live_right_vars())
    for dnzzr__gpa in wyfr__ndssj:
        uogr__vrmxc = typemap[dnzzr__gpa.name]
        rfxnm__ego = equiv_set.get_shape(dnzzr__gpa)
        if rfxnm__ego:
            cti__ixh.append(rfxnm__ego[0])
    if len(cti__ixh) > 1:
        equiv_set.insert_equiv(*cti__ixh)
    cti__ixh = []
    for xnfd__yvjz in join_node.get_live_out_vars():
        uogr__vrmxc = typemap[xnfd__yvjz.name]
        vmk__kiyw = array_analysis._gen_shape_call(equiv_set, xnfd__yvjz,
            uogr__vrmxc.ndim, None, kxvzn__wna)
        equiv_set.insert_equiv(xnfd__yvjz, vmk__kiyw)
        cti__ixh.append(vmk__kiyw[0])
        equiv_set.define(xnfd__yvjz, set())
    if len(cti__ixh) > 1:
        equiv_set.insert_equiv(*cti__ixh)
    return [], kxvzn__wna


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    vdlkc__anytg = Distribution.OneD
    pryvw__jzk = Distribution.OneD
    for dnzzr__gpa in join_node.get_live_left_vars():
        vdlkc__anytg = Distribution(min(vdlkc__anytg.value, array_dists[
            dnzzr__gpa.name].value))
    for dnzzr__gpa in join_node.get_live_right_vars():
        pryvw__jzk = Distribution(min(pryvw__jzk.value, array_dists[
            dnzzr__gpa.name].value))
    rdbrz__srpbk = Distribution.OneD_Var
    for xnfd__yvjz in join_node.get_live_out_vars():
        if xnfd__yvjz.name in array_dists:
            rdbrz__srpbk = Distribution(min(rdbrz__srpbk.value, array_dists
                [xnfd__yvjz.name].value))
    ivg__vydym = Distribution(min(rdbrz__srpbk.value, vdlkc__anytg.value))
    rsu__wvj = Distribution(min(rdbrz__srpbk.value, pryvw__jzk.value))
    rdbrz__srpbk = Distribution(max(ivg__vydym.value, rsu__wvj.value))
    for xnfd__yvjz in join_node.get_live_out_vars():
        array_dists[xnfd__yvjz.name] = rdbrz__srpbk
    if rdbrz__srpbk != Distribution.OneD_Var:
        vdlkc__anytg = rdbrz__srpbk
        pryvw__jzk = rdbrz__srpbk
    for dnzzr__gpa in join_node.get_live_left_vars():
        array_dists[dnzzr__gpa.name] = vdlkc__anytg
    for dnzzr__gpa in join_node.get_live_right_vars():
        array_dists[dnzzr__gpa.name] = pryvw__jzk
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(czv__rzjs, callback,
        cbdata) for czv__rzjs in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(czv__rzjs, callback,
        cbdata) for czv__rzjs in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(czv__rzjs, callback,
        cbdata) for czv__rzjs in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        cian__wgw = []
        pccr__wzonq = join_node.get_out_table_var()
        if pccr__wzonq.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for nsliv__rzmp in join_node.out_to_input_col_map.keys():
            if nsliv__rzmp in join_node.out_used_cols:
                continue
            cian__wgw.append(nsliv__rzmp)
            if join_node.indicator_col_num == nsliv__rzmp:
                join_node.indicator_col_num = -1
                continue
            if nsliv__rzmp == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            jrv__giw, nsliv__rzmp = join_node.out_to_input_col_map[nsliv__rzmp]
            if jrv__giw == 'left':
                if (nsliv__rzmp not in join_node.left_key_set and 
                    nsliv__rzmp not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(nsliv__rzmp)
                    if not join_node.is_left_table:
                        join_node.left_vars[nsliv__rzmp] = None
            elif jrv__giw == 'right':
                if (nsliv__rzmp not in join_node.right_key_set and 
                    nsliv__rzmp not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(nsliv__rzmp)
                    if not join_node.is_right_table:
                        join_node.right_vars[nsliv__rzmp] = None
        for euidu__vqa in cian__wgw:
            del join_node.out_to_input_col_map[euidu__vqa]
        if join_node.is_left_table:
            eruyf__mcg = set(range(join_node.n_left_table_cols))
            ryngm__ojua = not bool(eruyf__mcg - join_node.left_dead_var_inds)
            if ryngm__ojua:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            eruyf__mcg = set(range(join_node.n_right_table_cols))
            ryngm__ojua = not bool(eruyf__mcg - join_node.right_dead_var_inds)
            if ryngm__ojua:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        jlzej__mcaw = join_node.get_out_index_var()
        if jlzej__mcaw.name not in lives:
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
    xqis__irhjh = False
    if join_node.has_live_out_table_var:
        sna__aovst = join_node.get_out_table_var().name
        rhm__rso, gnn__ajr, zziws__gbaq = get_live_column_nums_block(
            column_live_map, equiv_vars, sna__aovst)
        if not (gnn__ajr or zziws__gbaq):
            rhm__rso = trim_extra_used_columns(rhm__rso, join_node.
                n_out_table_cols)
            uscm__rspl = join_node.get_out_table_used_cols()
            if len(rhm__rso) != len(uscm__rspl):
                xqis__irhjh = not (join_node.is_left_table and join_node.
                    is_right_table)
                blv__zds = uscm__rspl - rhm__rso
                join_node.out_used_cols = join_node.out_used_cols - blv__zds
    return xqis__irhjh


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        ywu__ywy = join_node.get_out_table_var()
        kosq__amub, gnn__ajr, zziws__gbaq = _compute_table_column_uses(ywu__ywy
            .name, table_col_use_map, equiv_vars)
    else:
        kosq__amub, gnn__ajr, zziws__gbaq = set(), False, False
    if join_node.has_live_left_table_var:
        sha__mxcy = join_node.left_vars[0].name
        qli__wmn, dfvld__cra, bxpp__zng = block_use_map[sha__mxcy]
        if not (dfvld__cra or bxpp__zng):
            wpsn__qqzzr = set([join_node.out_to_input_col_map[euidu__vqa][1
                ] for euidu__vqa in kosq__amub if join_node.
                out_to_input_col_map[euidu__vqa][0] == 'left'])
            omp__fzllw = set(euidu__vqa for euidu__vqa in join_node.
                left_key_set | join_node.left_cond_cols if euidu__vqa <
                join_node.n_left_table_cols)
            if not (gnn__ajr or zziws__gbaq):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (wpsn__qqzzr | omp__fzllw)
            block_use_map[sha__mxcy] = (qli__wmn | wpsn__qqzzr | omp__fzllw,
                gnn__ajr or zziws__gbaq, False)
    if join_node.has_live_right_table_var:
        txuza__fqpgg = join_node.right_vars[0].name
        qli__wmn, dfvld__cra, bxpp__zng = block_use_map[txuza__fqpgg]
        if not (dfvld__cra or bxpp__zng):
            qqywy__fpo = set([join_node.out_to_input_col_map[euidu__vqa][1] for
                euidu__vqa in kosq__amub if join_node.out_to_input_col_map[
                euidu__vqa][0] == 'right'])
            zoj__vaup = set(euidu__vqa for euidu__vqa in join_node.
                right_key_set | join_node.right_cond_cols if euidu__vqa <
                join_node.n_right_table_cols)
            if not (gnn__ajr or zziws__gbaq):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (qqywy__fpo | zoj__vaup)
            block_use_map[txuza__fqpgg] = (qli__wmn | qqywy__fpo |
                zoj__vaup, gnn__ajr or zziws__gbaq, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({qgb__nwh.name for qgb__nwh in join_node.
        get_live_left_vars()})
    use_set.update({qgb__nwh.name for qgb__nwh in join_node.
        get_live_right_vars()})
    def_set.update({qgb__nwh.name for qgb__nwh in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    xczfq__xyku = set(qgb__nwh.name for qgb__nwh in join_node.
        get_live_out_vars())
    return set(), xczfq__xyku


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(czv__rzjs, var_dict) for
        czv__rzjs in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(czv__rzjs, var_dict) for
        czv__rzjs in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(czv__rzjs,
        var_dict) for czv__rzjs in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for dnzzr__gpa in join_node.get_live_out_vars():
        definitions[dnzzr__gpa.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        cur__bazx = join_node.loc.strformat()
        vjish__okrn = [join_node.left_col_names[euidu__vqa] for euidu__vqa in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        yfgpk__muym = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', yfgpk__muym,
            cur__bazx, vjish__okrn)
        lulg__uqm = [join_node.right_col_names[euidu__vqa] for euidu__vqa in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        yfgpk__muym = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', yfgpk__muym,
            cur__bazx, lulg__uqm)
        bzkst__jele = [join_node.out_col_names[euidu__vqa] for euidu__vqa in
            sorted(join_node.get_out_table_used_cols())]
        yfgpk__muym = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', yfgpk__muym,
            cur__bazx, bzkst__jele)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    hmsg__hdts = len(join_node.left_keys)
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
    uirz__pgr = 0
    dmsjp__gjsgy = 0
    fey__jfwa = []
    for kri__uyl in join_node.left_keys:
        liya__rfqjc = join_node.left_var_map[kri__uyl]
        if not join_node.is_left_table:
            fey__jfwa.append(join_node.left_vars[liya__rfqjc])
        tput__psq = 1
        rplr__rglzo = join_node.left_to_output_map[liya__rfqjc]
        if kri__uyl == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == liya__rfqjc):
                out_physical_to_logical_list.append(rplr__rglzo)
                left_used_key_nums.add(liya__rfqjc)
            else:
                tput__psq = 0
        elif rplr__rglzo not in join_node.out_used_cols:
            tput__psq = 0
        elif liya__rfqjc in left_used_key_nums:
            tput__psq = 0
        else:
            left_used_key_nums.add(liya__rfqjc)
            out_physical_to_logical_list.append(rplr__rglzo)
        left_physical_to_logical_list.append(liya__rfqjc)
        left_logical_physical_map[liya__rfqjc] = uirz__pgr
        uirz__pgr += 1
        left_key_in_output.append(tput__psq)
    fey__jfwa = tuple(fey__jfwa)
    xyhcn__orddp = []
    for euidu__vqa in range(len(join_node.left_col_names)):
        if (euidu__vqa not in join_node.left_dead_var_inds and euidu__vqa
             not in join_node.left_key_set):
            if not join_node.is_left_table:
                qgb__nwh = join_node.left_vars[euidu__vqa]
                xyhcn__orddp.append(qgb__nwh)
            mwf__ubz = 1
            yhgs__hxq = 1
            rplr__rglzo = join_node.left_to_output_map[euidu__vqa]
            if euidu__vqa in join_node.left_cond_cols:
                if rplr__rglzo not in join_node.out_used_cols:
                    mwf__ubz = 0
                left_key_in_output.append(mwf__ubz)
            elif euidu__vqa in join_node.left_dead_var_inds:
                mwf__ubz = 0
                yhgs__hxq = 0
            if mwf__ubz:
                out_physical_to_logical_list.append(rplr__rglzo)
            if yhgs__hxq:
                left_physical_to_logical_list.append(euidu__vqa)
                left_logical_physical_map[euidu__vqa] = uirz__pgr
                uirz__pgr += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            xyhcn__orddp.append(join_node.left_vars[join_node.index_col_num])
        rplr__rglzo = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(rplr__rglzo)
        left_physical_to_logical_list.append(join_node.index_col_num)
    xyhcn__orddp = tuple(xyhcn__orddp)
    if join_node.is_left_table:
        xyhcn__orddp = tuple(join_node.get_live_left_vars())
    dwaho__lzjdm = []
    for euidu__vqa, kri__uyl in enumerate(join_node.right_keys):
        liya__rfqjc = join_node.right_var_map[kri__uyl]
        if not join_node.is_right_table:
            dwaho__lzjdm.append(join_node.right_vars[liya__rfqjc])
        if not join_node.vect_same_key[euidu__vqa] and not join_node.is_join:
            tput__psq = 1
            if liya__rfqjc not in join_node.right_to_output_map:
                tput__psq = 0
            else:
                rplr__rglzo = join_node.right_to_output_map[liya__rfqjc]
                if kri__uyl == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        liya__rfqjc):
                        out_physical_to_logical_list.append(rplr__rglzo)
                        right_used_key_nums.add(liya__rfqjc)
                    else:
                        tput__psq = 0
                elif rplr__rglzo not in join_node.out_used_cols:
                    tput__psq = 0
                elif liya__rfqjc in right_used_key_nums:
                    tput__psq = 0
                else:
                    right_used_key_nums.add(liya__rfqjc)
                    out_physical_to_logical_list.append(rplr__rglzo)
            right_key_in_output.append(tput__psq)
        right_physical_to_logical_list.append(liya__rfqjc)
        right_logical_physical_map[liya__rfqjc] = dmsjp__gjsgy
        dmsjp__gjsgy += 1
    dwaho__lzjdm = tuple(dwaho__lzjdm)
    lhwtc__qmnon = []
    for euidu__vqa in range(len(join_node.right_col_names)):
        if (euidu__vqa not in join_node.right_dead_var_inds and euidu__vqa
             not in join_node.right_key_set):
            if not join_node.is_right_table:
                lhwtc__qmnon.append(join_node.right_vars[euidu__vqa])
            mwf__ubz = 1
            yhgs__hxq = 1
            rplr__rglzo = join_node.right_to_output_map[euidu__vqa]
            if euidu__vqa in join_node.right_cond_cols:
                if rplr__rglzo not in join_node.out_used_cols:
                    mwf__ubz = 0
                right_key_in_output.append(mwf__ubz)
            elif euidu__vqa in join_node.right_dead_var_inds:
                mwf__ubz = 0
                yhgs__hxq = 0
            if mwf__ubz:
                out_physical_to_logical_list.append(rplr__rglzo)
            if yhgs__hxq:
                right_physical_to_logical_list.append(euidu__vqa)
                right_logical_physical_map[euidu__vqa] = dmsjp__gjsgy
                dmsjp__gjsgy += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            lhwtc__qmnon.append(join_node.right_vars[join_node.index_col_num])
        rplr__rglzo = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(rplr__rglzo)
        right_physical_to_logical_list.append(join_node.index_col_num)
    lhwtc__qmnon = tuple(lhwtc__qmnon)
    if join_node.is_right_table:
        lhwtc__qmnon = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    eybbu__jwr = fey__jfwa + dwaho__lzjdm + xyhcn__orddp + lhwtc__qmnon
    stvu__vtb = tuple(typemap[qgb__nwh.name] for qgb__nwh in eybbu__jwr)
    left_other_names = tuple('t1_c' + str(euidu__vqa) for euidu__vqa in
        range(len(xyhcn__orddp)))
    right_other_names = tuple('t2_c' + str(euidu__vqa) for euidu__vqa in
        range(len(lhwtc__qmnon)))
    if join_node.is_left_table:
        qfhsy__esg = ()
    else:
        qfhsy__esg = tuple('t1_key' + str(euidu__vqa) for euidu__vqa in
            range(hmsg__hdts))
    if join_node.is_right_table:
        wblrp__bxi = ()
    else:
        wblrp__bxi = tuple('t2_key' + str(euidu__vqa) for euidu__vqa in
            range(hmsg__hdts))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(qfhsy__esg + wblrp__bxi +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            vme__vute = typemap[join_node.left_vars[0].name]
        else:
            vme__vute = types.none
        for nnnm__ajocm in left_physical_to_logical_list:
            if nnnm__ajocm < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                uogr__vrmxc = vme__vute.arr_types[nnnm__ajocm]
            else:
                uogr__vrmxc = typemap[join_node.left_vars[-1].name]
            if nnnm__ajocm in join_node.left_key_set:
                left_key_types.append(uogr__vrmxc)
            else:
                left_other_types.append(uogr__vrmxc)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[qgb__nwh.name] for qgb__nwh in fey__jfwa
            )
        left_other_types = tuple([typemap[kri__uyl.name] for kri__uyl in
            xyhcn__orddp])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            vme__vute = typemap[join_node.right_vars[0].name]
        else:
            vme__vute = types.none
        for nnnm__ajocm in right_physical_to_logical_list:
            if nnnm__ajocm < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                uogr__vrmxc = vme__vute.arr_types[nnnm__ajocm]
            else:
                uogr__vrmxc = typemap[join_node.right_vars[-1].name]
            if nnnm__ajocm in join_node.right_key_set:
                right_key_types.append(uogr__vrmxc)
            else:
                right_other_types.append(uogr__vrmxc)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[qgb__nwh.name] for qgb__nwh in
            dwaho__lzjdm)
        right_other_types = tuple([typemap[kri__uyl.name] for kri__uyl in
            lhwtc__qmnon])
    matched_key_types = []
    for euidu__vqa in range(hmsg__hdts):
        akc__rolg = _match_join_key_types(left_key_types[euidu__vqa],
            right_key_types[euidu__vqa], loc)
        glbs[f'key_type_{euidu__vqa}'] = akc__rolg
        matched_key_types.append(akc__rolg)
    if join_node.is_left_table:
        lkjn__nsq = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if lkjn__nsq:
            ygi__lyss = False
            vlyi__mwbh = False
            wnwfq__mkew = None
            if join_node.has_live_left_table_var:
                faljk__bxzxr = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                faljk__bxzxr = None
            for nsliv__rzmp, uogr__vrmxc in lkjn__nsq.items():
                if nsliv__rzmp < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    faljk__bxzxr[nsliv__rzmp] = uogr__vrmxc
                    ygi__lyss = True
                else:
                    wnwfq__mkew = uogr__vrmxc
                    vlyi__mwbh = True
            if ygi__lyss:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(faljk__bxzxr))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if vlyi__mwbh:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = wnwfq__mkew
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({qfhsy__esg[euidu__vqa]}, key_type_{euidu__vqa})'
             if left_key_types[euidu__vqa] != matched_key_types[euidu__vqa]
             else f'{qfhsy__esg[euidu__vqa]}' for euidu__vqa in range(
            hmsg__hdts)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        lkjn__nsq = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if lkjn__nsq:
            ygi__lyss = False
            vlyi__mwbh = False
            wnwfq__mkew = None
            if join_node.has_live_right_table_var:
                faljk__bxzxr = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                faljk__bxzxr = None
            for nsliv__rzmp, uogr__vrmxc in lkjn__nsq.items():
                if nsliv__rzmp < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    faljk__bxzxr[nsliv__rzmp] = uogr__vrmxc
                    ygi__lyss = True
                else:
                    wnwfq__mkew = uogr__vrmxc
                    vlyi__mwbh = True
            if ygi__lyss:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(faljk__bxzxr))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if vlyi__mwbh:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = wnwfq__mkew
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({wblrp__bxi[euidu__vqa]}, key_type_{euidu__vqa})'
             if right_key_types[euidu__vqa] != matched_key_types[euidu__vqa
            ] else f'{wblrp__bxi[euidu__vqa]}' for euidu__vqa in range(
            hmsg__hdts)))
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
        for euidu__vqa in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(euidu__vqa,
                euidu__vqa)
        for euidu__vqa in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                euidu__vqa, euidu__vqa)
        for euidu__vqa in range(hmsg__hdts):
            func_text += (
                f'    t1_keys_{euidu__vqa} = out_t1_keys[{euidu__vqa}]\n')
        for euidu__vqa in range(hmsg__hdts):
            func_text += (
                f'    t2_keys_{euidu__vqa} = out_t2_keys[{euidu__vqa}]\n')
    ozbb__nquz = {}
    exec(func_text, {}, ozbb__nquz)
    nwfz__bac = ozbb__nquz['f']
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
    lkf__vhqk = compile_to_numba_ir(nwfz__bac, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=stvu__vtb, typemap=typemap, calltypes
        =calltypes).blocks.popitem()[1]
    replace_arg_nodes(lkf__vhqk, eybbu__jwr)
    hgp__jel = lkf__vhqk.body[:-3]
    if join_node.has_live_out_index_var:
        hgp__jel[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        hgp__jel[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        hgp__jel.pop(-1)
    elif not join_node.has_live_out_table_var:
        hgp__jel.pop(-2)
    return hgp__jel


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    sbtt__fmqu = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{sbtt__fmqu}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    ozbb__nquz = {}
    exec(func_text, table_getitem_funcs, ozbb__nquz)
    gra__hjglv = ozbb__nquz[f'bodo_join_gen_cond{sbtt__fmqu}']
    ycob__pepwa = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    ddee__ceqwv = numba.cfunc(ycob__pepwa, nopython=True)(gra__hjglv)
    join_gen_cond_cfunc[ddee__ceqwv.native_name] = ddee__ceqwv
    join_gen_cond_cfunc_addr[ddee__ceqwv.native_name] = ddee__ceqwv.address
    return ddee__ceqwv, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    zlqd__uzd = []
    for kri__uyl, ksvmh__szkr in name_to_var_map.items():
        fastt__ijp = f'({table_name}.{kri__uyl})'
        if fastt__ijp not in expr:
            continue
        fvhg__csgpn = f'getitem_{table_name}_val_{ksvmh__szkr}'
        trvp__accvx = f'_bodo_{table_name}_val_{ksvmh__szkr}'
        if is_table_var:
            kpivv__uhl = typemap[col_vars[0].name].arr_types[ksvmh__szkr]
        else:
            kpivv__uhl = typemap[col_vars[ksvmh__szkr].name]
        if is_str_arr_type(kpivv__uhl) or kpivv__uhl == bodo.binary_array_type:
            func_text += f"""  {trvp__accvx}, {trvp__accvx}_size = {fvhg__csgpn}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {trvp__accvx} = bodo.libs.str_arr_ext.decode_utf8({trvp__accvx}, {trvp__accvx}_size)
"""
        else:
            func_text += (
                f'  {trvp__accvx} = {fvhg__csgpn}({table_name}_data1, {table_name}_ind)\n'
                )
        dntl__mvk = logical_to_physical_ind[ksvmh__szkr]
        table_getitem_funcs[fvhg__csgpn
            ] = bodo.libs.array._gen_row_access_intrinsic(kpivv__uhl, dntl__mvk
            )
        expr = expr.replace(fastt__ijp, trvp__accvx)
        ivkzl__bkum = f'({na_check_name}.{table_name}.{kri__uyl})'
        if ivkzl__bkum in expr:
            lpac__vdp = f'nacheck_{table_name}_val_{ksvmh__szkr}'
            mtthl__gjb = f'_bodo_isna_{table_name}_val_{ksvmh__szkr}'
            if isinstance(kpivv__uhl, bodo.libs.int_arr_ext.IntegerArrayType
                ) or kpivv__uhl in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(kpivv__uhl):
                func_text += f"""  {mtthl__gjb} = {lpac__vdp}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {mtthl__gjb} = {lpac__vdp}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[lpac__vdp
                ] = bodo.libs.array._gen_row_na_check_intrinsic(kpivv__uhl,
                dntl__mvk)
            expr = expr.replace(ivkzl__bkum, mtthl__gjb)
        if ksvmh__szkr not in key_set:
            zlqd__uzd.append(dntl__mvk)
    return expr, func_text, zlqd__uzd


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as tgsfb__strhj:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    cxhi__xvzdr = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[qgb__nwh.name] in cxhi__xvzdr for
        qgb__nwh in join_node.get_live_left_vars())
    right_parallel = all(array_dists[qgb__nwh.name] in cxhi__xvzdr for
        qgb__nwh in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[qgb__nwh.name] in cxhi__xvzdr for
            qgb__nwh in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[qgb__nwh.name] in cxhi__xvzdr for
            qgb__nwh in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[qgb__nwh.name] in cxhi__xvzdr for qgb__nwh in
            join_node.get_live_out_vars())
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
    zvpe__rofa = set(left_col_nums)
    grmr__vgjw = set(right_col_nums)
    pwxt__tdne = join_node.vect_same_key
    qgdui__oyml = []
    for euidu__vqa in range(len(left_key_types)):
        if left_key_in_output[euidu__vqa]:
            qgdui__oyml.append(needs_typechange(matched_key_types[
                euidu__vqa], join_node.is_right, pwxt__tdne[euidu__vqa]))
    poac__bfk = len(left_key_types)
    yrs__wit = 0
    rwjbx__gcuha = left_physical_to_logical_list[len(left_key_types):]
    for euidu__vqa, nnnm__ajocm in enumerate(rwjbx__gcuha):
        lga__hudy = True
        if nnnm__ajocm in zvpe__rofa:
            lga__hudy = left_key_in_output[poac__bfk]
            poac__bfk += 1
        if lga__hudy:
            qgdui__oyml.append(needs_typechange(left_other_types[euidu__vqa
                ], join_node.is_right, False))
    for euidu__vqa in range(len(right_key_types)):
        if not pwxt__tdne[euidu__vqa] and not join_node.is_join:
            if right_key_in_output[yrs__wit]:
                qgdui__oyml.append(needs_typechange(matched_key_types[
                    euidu__vqa], join_node.is_left, False))
            yrs__wit += 1
    lemqw__cftk = right_physical_to_logical_list[len(right_key_types):]
    for euidu__vqa, nnnm__ajocm in enumerate(lemqw__cftk):
        lga__hudy = True
        if nnnm__ajocm in grmr__vgjw:
            lga__hudy = right_key_in_output[yrs__wit]
            yrs__wit += 1
        if lga__hudy:
            qgdui__oyml.append(needs_typechange(right_other_types[
                euidu__vqa], join_node.is_left, False))
    hmsg__hdts = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            ycjp__fdr = left_other_names[1:]
            pccr__wzonq = left_other_names[0]
        else:
            ycjp__fdr = left_other_names
            pccr__wzonq = None
        devf__wvch = '()' if len(ycjp__fdr) == 0 else f'({ycjp__fdr[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({pccr__wzonq}, {devf__wvch}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        bzg__fdtb = []
        for euidu__vqa in range(hmsg__hdts):
            bzg__fdtb.append('t1_keys[{}]'.format(euidu__vqa))
        for euidu__vqa in range(len(left_other_names)):
            bzg__fdtb.append('data_left[{}]'.format(euidu__vqa))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(ypbxx__rlnzs) for ypbxx__rlnzs in
            bzg__fdtb))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            ius__avu = right_other_names[1:]
            pccr__wzonq = right_other_names[0]
        else:
            ius__avu = right_other_names
            pccr__wzonq = None
        devf__wvch = '()' if len(ius__avu) == 0 else f'({ius__avu[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({pccr__wzonq}, {devf__wvch}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        cvnx__jbst = []
        for euidu__vqa in range(hmsg__hdts):
            cvnx__jbst.append('t2_keys[{}]'.format(euidu__vqa))
        for euidu__vqa in range(len(right_other_names)):
            cvnx__jbst.append('data_right[{}]'.format(euidu__vqa))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(ypbxx__rlnzs) for ypbxx__rlnzs in
            cvnx__jbst))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(pwxt__tdne, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(qgdui__oyml, dtype=np.int64)
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
        .format(left_parallel, right_parallel, hmsg__hdts, len(rwjbx__gcuha
        ), len(lemqw__cftk), join_node.is_left, join_node.is_right,
        join_node.is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    bzepx__osgea = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {bzepx__osgea}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        gpktr__prh = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{gpktr__prh}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        lkjn__nsq = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        lkjn__nsq.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        ygi__lyss = False
        vlyi__mwbh = False
        if join_node.has_live_out_table_var:
            faljk__bxzxr = list(out_table_type.arr_types)
        else:
            faljk__bxzxr = None
        for nsliv__rzmp, uogr__vrmxc in lkjn__nsq.items():
            if nsliv__rzmp < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                faljk__bxzxr[nsliv__rzmp] = uogr__vrmxc
                ygi__lyss = True
            else:
                wnwfq__mkew = uogr__vrmxc
                vlyi__mwbh = True
        if ygi__lyss:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            yori__fbu = bodo.TableType(tuple(faljk__bxzxr))
            glbs['py_table_type'] = yori__fbu
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if vlyi__mwbh:
            glbs['index_col_type'] = wnwfq__mkew
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
    lkjn__nsq: Dict[int, types.Type] = {}
    hmsg__hdts = len(matched_key_types)
    for euidu__vqa in range(hmsg__hdts):
        if used_key_nums is None or euidu__vqa in used_key_nums:
            if matched_key_types[euidu__vqa] != key_types[euidu__vqa] and (
                convert_dict_col or key_types[euidu__vqa] != bodo.
                dict_str_arr_type):
                if output_map:
                    gpktr__prh = output_map[euidu__vqa]
                else:
                    gpktr__prh = euidu__vqa
                lkjn__nsq[gpktr__prh] = matched_key_types[euidu__vqa]
    return lkjn__nsq


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    qfnfu__nspai = bodo.libs.distributed_api.get_size()
    nsgv__otci = np.empty(qfnfu__nspai, left_key_arrs[0].dtype)
    nsb__wqnsn = np.empty(qfnfu__nspai, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(nsgv__otci, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(nsb__wqnsn, left_key_arrs[0][-1])
    afc__mgevl = np.zeros(qfnfu__nspai, np.int32)
    xoug__sul = np.zeros(qfnfu__nspai, np.int32)
    kdicj__xcize = np.zeros(qfnfu__nspai, np.int32)
    vcoq__eqeo = right_key_arrs[0][0]
    yph__qkil = right_key_arrs[0][-1]
    vicai__lvsz = -1
    euidu__vqa = 0
    while euidu__vqa < qfnfu__nspai - 1 and nsb__wqnsn[euidu__vqa
        ] < vcoq__eqeo:
        euidu__vqa += 1
    while euidu__vqa < qfnfu__nspai and nsgv__otci[euidu__vqa] <= yph__qkil:
        vicai__lvsz, cjgap__utbh = _count_overlap(right_key_arrs[0],
            nsgv__otci[euidu__vqa], nsb__wqnsn[euidu__vqa])
        if vicai__lvsz != 0:
            vicai__lvsz -= 1
            cjgap__utbh += 1
        afc__mgevl[euidu__vqa] = cjgap__utbh
        xoug__sul[euidu__vqa] = vicai__lvsz
        euidu__vqa += 1
    while euidu__vqa < qfnfu__nspai:
        afc__mgevl[euidu__vqa] = 1
        xoug__sul[euidu__vqa] = len(right_key_arrs[0]) - 1
        euidu__vqa += 1
    bodo.libs.distributed_api.alltoall(afc__mgevl, kdicj__xcize, 1)
    uwcy__jqjy = kdicj__xcize.sum()
    elfqk__ptu = np.empty(uwcy__jqjy, right_key_arrs[0].dtype)
    hong__kad = alloc_arr_tup(uwcy__jqjy, right_data)
    lqp__zecrq = bodo.ir.join.calc_disp(kdicj__xcize)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], elfqk__ptu,
        afc__mgevl, kdicj__xcize, xoug__sul, lqp__zecrq)
    bodo.libs.distributed_api.alltoallv_tup(right_data, hong__kad,
        afc__mgevl, kdicj__xcize, xoug__sul, lqp__zecrq)
    return (elfqk__ptu,), hong__kad


@numba.njit
def _count_overlap(r_key_arr, start, end):
    cjgap__utbh = 0
    vicai__lvsz = 0
    ypspn__nkx = 0
    while ypspn__nkx < len(r_key_arr) and r_key_arr[ypspn__nkx] < start:
        vicai__lvsz += 1
        ypspn__nkx += 1
    while ypspn__nkx < len(r_key_arr) and start <= r_key_arr[ypspn__nkx
        ] <= end:
        ypspn__nkx += 1
        cjgap__utbh += 1
    return vicai__lvsz, cjgap__utbh


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    bkbea__ntkyu = np.empty_like(arr)
    bkbea__ntkyu[0] = 0
    for euidu__vqa in range(1, len(arr)):
        bkbea__ntkyu[euidu__vqa] = bkbea__ntkyu[euidu__vqa - 1] + arr[
            euidu__vqa - 1]
    return bkbea__ntkyu


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    cstl__devj = len(left_keys[0])
    aqea__cyp = len(right_keys[0])
    ehsr__oqwcj = alloc_arr_tup(cstl__devj, left_keys)
    vud__krtdf = alloc_arr_tup(cstl__devj, right_keys)
    bmtj__nrm = alloc_arr_tup(cstl__devj, data_left)
    lipts__ovddx = alloc_arr_tup(cstl__devj, data_right)
    pxz__gnxf = 0
    gqpgy__guzu = 0
    for pxz__gnxf in range(cstl__devj):
        if gqpgy__guzu < 0:
            gqpgy__guzu = 0
        while gqpgy__guzu < aqea__cyp and getitem_arr_tup(right_keys,
            gqpgy__guzu) <= getitem_arr_tup(left_keys, pxz__gnxf):
            gqpgy__guzu += 1
        gqpgy__guzu -= 1
        setitem_arr_tup(ehsr__oqwcj, pxz__gnxf, getitem_arr_tup(left_keys,
            pxz__gnxf))
        setitem_arr_tup(bmtj__nrm, pxz__gnxf, getitem_arr_tup(data_left,
            pxz__gnxf))
        if gqpgy__guzu >= 0:
            setitem_arr_tup(vud__krtdf, pxz__gnxf, getitem_arr_tup(
                right_keys, gqpgy__guzu))
            setitem_arr_tup(lipts__ovddx, pxz__gnxf, getitem_arr_tup(
                data_right, gqpgy__guzu))
        else:
            bodo.libs.array_kernels.setna_tup(vud__krtdf, pxz__gnxf)
            bodo.libs.array_kernels.setna_tup(lipts__ovddx, pxz__gnxf)
    return ehsr__oqwcj, vud__krtdf, bmtj__nrm, lipts__ovddx
