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
        iqal__cfol = func.signature
        knfc__eavwi = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        qierg__lmr = cgutils.get_or_insert_function(builder.module,
            knfc__eavwi, sym._literal_value)
        builder.call(qierg__lmr, [context.get_constant_null(iqal__cfol.args
            [0]), context.get_constant_null(iqal__cfol.args[1]), context.
            get_constant_null(iqal__cfol.args[2]), context.
            get_constant_null(iqal__cfol.args[3]), context.
            get_constant_null(iqal__cfol.args[4]), context.
            get_constant_null(iqal__cfol.args[5]), context.get_constant(
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
        qvt__hpb = left_df_type.columns
        pttpu__hdxuy = right_df_type.columns
        self.left_col_names = qvt__hpb
        self.right_col_names = pttpu__hdxuy
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(qvt__hpb) if self.is_left_table else 0
        self.n_right_table_cols = len(pttpu__hdxuy
            ) if self.is_right_table else 0
        ghykr__rddss = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        vajm__lizd = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(ghykr__rddss)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(vajm__lizd)
        self.left_var_map = {iux__nvqw: sbg__rlj for sbg__rlj, iux__nvqw in
            enumerate(qvt__hpb)}
        self.right_var_map = {iux__nvqw: sbg__rlj for sbg__rlj, iux__nvqw in
            enumerate(pttpu__hdxuy)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = ghykr__rddss
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = vajm__lizd
        self.left_key_set = set(self.left_var_map[iux__nvqw] for iux__nvqw in
            left_keys)
        self.right_key_set = set(self.right_var_map[iux__nvqw] for
            iux__nvqw in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[iux__nvqw] for
                iux__nvqw in qvt__hpb if f'(left.{iux__nvqw})' in gen_cond_expr
                )
            self.right_cond_cols = set(self.right_var_map[iux__nvqw] for
                iux__nvqw in pttpu__hdxuy if f'(right.{iux__nvqw})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        vybb__gnj: int = -1
        fgmt__aug = set(left_keys) & set(right_keys)
        zogh__njyw = set(qvt__hpb) & set(pttpu__hdxuy)
        xtes__rrwjl = zogh__njyw - fgmt__aug
        tiwrm__nvmen: Dict[int, (Literal['left', 'right'], int)] = {}
        dssqk__qykii: Dict[int, int] = {}
        eglah__gvq: Dict[int, int] = {}
        for sbg__rlj, iux__nvqw in enumerate(qvt__hpb):
            if iux__nvqw in xtes__rrwjl:
                inj__wfzjz = str(iux__nvqw) + suffix_left
                hhc__ixdq = out_df_type.column_index[inj__wfzjz]
                if (right_index and not left_index and sbg__rlj in self.
                    left_key_set):
                    vybb__gnj = out_df_type.column_index[iux__nvqw]
                    tiwrm__nvmen[vybb__gnj] = 'left', sbg__rlj
            else:
                hhc__ixdq = out_df_type.column_index[iux__nvqw]
            tiwrm__nvmen[hhc__ixdq] = 'left', sbg__rlj
            dssqk__qykii[sbg__rlj] = hhc__ixdq
        for sbg__rlj, iux__nvqw in enumerate(pttpu__hdxuy):
            if iux__nvqw not in fgmt__aug:
                if iux__nvqw in xtes__rrwjl:
                    sbdwj__ped = str(iux__nvqw) + suffix_right
                    hhc__ixdq = out_df_type.column_index[sbdwj__ped]
                    if (left_index and not right_index and sbg__rlj in self
                        .right_key_set):
                        vybb__gnj = out_df_type.column_index[iux__nvqw]
                        tiwrm__nvmen[vybb__gnj] = 'right', sbg__rlj
                else:
                    hhc__ixdq = out_df_type.column_index[iux__nvqw]
                tiwrm__nvmen[hhc__ixdq] = 'right', sbg__rlj
                eglah__gvq[sbg__rlj] = hhc__ixdq
        if self.left_vars[-1] is not None:
            dssqk__qykii[ghykr__rddss] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            eglah__gvq[vajm__lizd] = self.n_out_table_cols
        self.out_to_input_col_map = tiwrm__nvmen
        self.left_to_output_map = dssqk__qykii
        self.right_to_output_map = eglah__gvq
        self.extra_data_col_num = vybb__gnj
        if len(out_data_vars) > 1:
            jqtds__youn = 'left' if right_index else 'right'
            if jqtds__youn == 'left':
                mryal__qna = ghykr__rddss
            elif jqtds__youn == 'right':
                mryal__qna = vajm__lizd
        else:
            jqtds__youn = None
            mryal__qna = -1
        self.index_source = jqtds__youn
        self.index_col_num = mryal__qna
        pmxar__kzpek = []
        oimq__zav = len(left_keys)
        for onrxg__ffojj in range(oimq__zav):
            nyndc__ccfyt = left_keys[onrxg__ffojj]
            zzxsz__tffc = right_keys[onrxg__ffojj]
            pmxar__kzpek.append(nyndc__ccfyt == zzxsz__tffc)
        self.vect_same_key = pmxar__kzpek

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
        for rjwbg__ctj in self.left_vars:
            if rjwbg__ctj is not None:
                vars.append(rjwbg__ctj)
        return vars

    def get_live_right_vars(self):
        vars = []
        for rjwbg__ctj in self.right_vars:
            if rjwbg__ctj is not None:
                vars.append(rjwbg__ctj)
        return vars

    def get_live_out_vars(self):
        vars = []
        for rjwbg__ctj in self.out_data_vars:
            if rjwbg__ctj is not None:
                vars.append(rjwbg__ctj)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        jzv__suq = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[jzv__suq])
                jzv__suq += 1
            else:
                left_vars.append(None)
            start = 1
        rbj__goulq = max(self.n_left_table_cols - 1, 0)
        for sbg__rlj in range(start, len(self.left_vars)):
            if sbg__rlj + rbj__goulq in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[jzv__suq])
                jzv__suq += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        jzv__suq = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[jzv__suq])
                jzv__suq += 1
            else:
                right_vars.append(None)
            start = 1
        rbj__goulq = max(self.n_right_table_cols - 1, 0)
        for sbg__rlj in range(start, len(self.right_vars)):
            if sbg__rlj + rbj__goulq in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[jzv__suq])
                jzv__suq += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        jaoe__gfc = [self.has_live_out_table_var, self.has_live_out_index_var]
        jzv__suq = 0
        for sbg__rlj in range(len(self.out_data_vars)):
            if not jaoe__gfc[sbg__rlj]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[jzv__suq])
                jzv__suq += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {sbg__rlj for sbg__rlj in self.out_used_cols if sbg__rlj <
            self.n_out_table_cols}

    def __repr__(self):
        brs__amm = ', '.join([f'{iux__nvqw}' for iux__nvqw in self.
            left_col_names])
        vvzb__ngcvj = f'left={{{brs__amm}}}'
        brs__amm = ', '.join([f'{iux__nvqw}' for iux__nvqw in self.
            right_col_names])
        cvr__dfu = f'right={{{brs__amm}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, vvzb__ngcvj, cvr__dfu)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    hwec__hqci = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    pmzxr__mze = []
    jab__fzk = join_node.get_live_left_vars()
    for eya__kqi in jab__fzk:
        jgulh__zrj = typemap[eya__kqi.name]
        waju__qnr = equiv_set.get_shape(eya__kqi)
        if waju__qnr:
            pmzxr__mze.append(waju__qnr[0])
    if len(pmzxr__mze) > 1:
        equiv_set.insert_equiv(*pmzxr__mze)
    pmzxr__mze = []
    jab__fzk = list(join_node.get_live_right_vars())
    for eya__kqi in jab__fzk:
        jgulh__zrj = typemap[eya__kqi.name]
        waju__qnr = equiv_set.get_shape(eya__kqi)
        if waju__qnr:
            pmzxr__mze.append(waju__qnr[0])
    if len(pmzxr__mze) > 1:
        equiv_set.insert_equiv(*pmzxr__mze)
    pmzxr__mze = []
    for fwy__meus in join_node.get_live_out_vars():
        jgulh__zrj = typemap[fwy__meus.name]
        ufjny__ccwg = array_analysis._gen_shape_call(equiv_set, fwy__meus,
            jgulh__zrj.ndim, None, hwec__hqci)
        equiv_set.insert_equiv(fwy__meus, ufjny__ccwg)
        pmzxr__mze.append(ufjny__ccwg[0])
        equiv_set.define(fwy__meus, set())
    if len(pmzxr__mze) > 1:
        equiv_set.insert_equiv(*pmzxr__mze)
    return [], hwec__hqci


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    iwq__gscen = Distribution.OneD
    xzohf__aidfu = Distribution.OneD
    for eya__kqi in join_node.get_live_left_vars():
        iwq__gscen = Distribution(min(iwq__gscen.value, array_dists[
            eya__kqi.name].value))
    for eya__kqi in join_node.get_live_right_vars():
        xzohf__aidfu = Distribution(min(xzohf__aidfu.value, array_dists[
            eya__kqi.name].value))
    nuv__mmmv = Distribution.OneD_Var
    for fwy__meus in join_node.get_live_out_vars():
        if fwy__meus.name in array_dists:
            nuv__mmmv = Distribution(min(nuv__mmmv.value, array_dists[
                fwy__meus.name].value))
    pfvhc__oksj = Distribution(min(nuv__mmmv.value, iwq__gscen.value))
    wtdy__sjx = Distribution(min(nuv__mmmv.value, xzohf__aidfu.value))
    nuv__mmmv = Distribution(max(pfvhc__oksj.value, wtdy__sjx.value))
    for fwy__meus in join_node.get_live_out_vars():
        array_dists[fwy__meus.name] = nuv__mmmv
    if nuv__mmmv != Distribution.OneD_Var:
        iwq__gscen = nuv__mmmv
        xzohf__aidfu = nuv__mmmv
    for eya__kqi in join_node.get_live_left_vars():
        array_dists[eya__kqi.name] = iwq__gscen
    for eya__kqi in join_node.get_live_right_vars():
        array_dists[eya__kqi.name] = xzohf__aidfu
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(rjwbg__ctj, callback,
        cbdata) for rjwbg__ctj in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(rjwbg__ctj, callback,
        cbdata) for rjwbg__ctj in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(rjwbg__ctj, callback,
        cbdata) for rjwbg__ctj in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        fly__iuwl = []
        vbr__inmd = join_node.get_out_table_var()
        if vbr__inmd.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for ubfyw__bsx in join_node.out_to_input_col_map.keys():
            if ubfyw__bsx in join_node.out_used_cols:
                continue
            fly__iuwl.append(ubfyw__bsx)
            if join_node.indicator_col_num == ubfyw__bsx:
                join_node.indicator_col_num = -1
                continue
            if ubfyw__bsx == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            ckx__honly, ubfyw__bsx = join_node.out_to_input_col_map[ubfyw__bsx]
            if ckx__honly == 'left':
                if (ubfyw__bsx not in join_node.left_key_set and ubfyw__bsx
                     not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(ubfyw__bsx)
                    if not join_node.is_left_table:
                        join_node.left_vars[ubfyw__bsx] = None
            elif ckx__honly == 'right':
                if (ubfyw__bsx not in join_node.right_key_set and 
                    ubfyw__bsx not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(ubfyw__bsx)
                    if not join_node.is_right_table:
                        join_node.right_vars[ubfyw__bsx] = None
        for sbg__rlj in fly__iuwl:
            del join_node.out_to_input_col_map[sbg__rlj]
        if join_node.is_left_table:
            ypqrq__kwq = set(range(join_node.n_left_table_cols))
            fcr__fyeep = not bool(ypqrq__kwq - join_node.left_dead_var_inds)
            if fcr__fyeep:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            ypqrq__kwq = set(range(join_node.n_right_table_cols))
            fcr__fyeep = not bool(ypqrq__kwq - join_node.right_dead_var_inds)
            if fcr__fyeep:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        lwdc__deox = join_node.get_out_index_var()
        if lwdc__deox.name not in lives:
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
    rtozl__crx = False
    if join_node.has_live_out_table_var:
        fdvw__yposh = join_node.get_out_table_var().name
        gnoh__yuf, skfcq__xpzuu, crrft__yckge = get_live_column_nums_block(
            column_live_map, equiv_vars, fdvw__yposh)
        if not (skfcq__xpzuu or crrft__yckge):
            gnoh__yuf = trim_extra_used_columns(gnoh__yuf, join_node.
                n_out_table_cols)
            tme__kfxow = join_node.get_out_table_used_cols()
            if len(gnoh__yuf) != len(tme__kfxow):
                rtozl__crx = not (join_node.is_left_table and join_node.
                    is_right_table)
                slgr__nyvkj = tme__kfxow - gnoh__yuf
                join_node.out_used_cols = join_node.out_used_cols - slgr__nyvkj
    return rtozl__crx


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        eidv__lqbvx = join_node.get_out_table_var()
        nvvn__bum, skfcq__xpzuu, crrft__yckge = _compute_table_column_uses(
            eidv__lqbvx.name, table_col_use_map, equiv_vars)
    else:
        nvvn__bum, skfcq__xpzuu, crrft__yckge = set(), False, False
    if join_node.has_live_left_table_var:
        uucm__sueeb = join_node.left_vars[0].name
        lie__qgnbu, iet__fbqw, sbke__uveqg = block_use_map[uucm__sueeb]
        if not (iet__fbqw or sbke__uveqg):
            xbdd__sswj = set([join_node.out_to_input_col_map[sbg__rlj][1] for
                sbg__rlj in nvvn__bum if join_node.out_to_input_col_map[
                sbg__rlj][0] == 'left'])
            nlfdw__sqc = set(sbg__rlj for sbg__rlj in join_node.
                left_key_set | join_node.left_cond_cols if sbg__rlj <
                join_node.n_left_table_cols)
            if not (skfcq__xpzuu or crrft__yckge):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (xbdd__sswj | nlfdw__sqc)
            block_use_map[uucm__sueeb] = (lie__qgnbu | xbdd__sswj |
                nlfdw__sqc, skfcq__xpzuu or crrft__yckge, False)
    if join_node.has_live_right_table_var:
        quzbs__mvf = join_node.right_vars[0].name
        lie__qgnbu, iet__fbqw, sbke__uveqg = block_use_map[quzbs__mvf]
        if not (iet__fbqw or sbke__uveqg):
            rqidd__opwq = set([join_node.out_to_input_col_map[sbg__rlj][1] for
                sbg__rlj in nvvn__bum if join_node.out_to_input_col_map[
                sbg__rlj][0] == 'right'])
            fdmzq__huww = set(sbg__rlj for sbg__rlj in join_node.
                right_key_set | join_node.right_cond_cols if sbg__rlj <
                join_node.n_right_table_cols)
            if not (skfcq__xpzuu or crrft__yckge):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (rqidd__opwq | fdmzq__huww)
            block_use_map[quzbs__mvf] = (lie__qgnbu | rqidd__opwq |
                fdmzq__huww, skfcq__xpzuu or crrft__yckge, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({nks__dzx.name for nks__dzx in join_node.
        get_live_left_vars()})
    use_set.update({nks__dzx.name for nks__dzx in join_node.
        get_live_right_vars()})
    def_set.update({nks__dzx.name for nks__dzx in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    kgxog__juff = set(nks__dzx.name for nks__dzx in join_node.
        get_live_out_vars())
    return set(), kgxog__juff


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(rjwbg__ctj, var_dict) for
        rjwbg__ctj in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(rjwbg__ctj, var_dict) for
        rjwbg__ctj in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(rjwbg__ctj,
        var_dict) for rjwbg__ctj in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for eya__kqi in join_node.get_live_out_vars():
        definitions[eya__kqi.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        ewbv__rskg = join_node.loc.strformat()
        yvqg__svny = [join_node.left_col_names[sbg__rlj] for sbg__rlj in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        cvgw__faizz = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', cvgw__faizz,
            ewbv__rskg, yvqg__svny)
        zmqj__urwuh = [join_node.right_col_names[sbg__rlj] for sbg__rlj in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        cvgw__faizz = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', cvgw__faizz,
            ewbv__rskg, zmqj__urwuh)
        pbj__rbid = [join_node.out_col_names[sbg__rlj] for sbg__rlj in
            sorted(join_node.get_out_table_used_cols())]
        cvgw__faizz = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', cvgw__faizz,
            ewbv__rskg, pbj__rbid)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    oimq__zav = len(join_node.left_keys)
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
    maij__afelr = 0
    mleb__erbc = 0
    hnraj__pcp = []
    for iux__nvqw in join_node.left_keys:
        skkb__wowx = join_node.left_var_map[iux__nvqw]
        if not join_node.is_left_table:
            hnraj__pcp.append(join_node.left_vars[skkb__wowx])
        jaoe__gfc = 1
        hhc__ixdq = join_node.left_to_output_map[skkb__wowx]
        if iux__nvqw == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == skkb__wowx):
                out_physical_to_logical_list.append(hhc__ixdq)
                left_used_key_nums.add(skkb__wowx)
            else:
                jaoe__gfc = 0
        elif hhc__ixdq not in join_node.out_used_cols:
            jaoe__gfc = 0
        elif skkb__wowx in left_used_key_nums:
            jaoe__gfc = 0
        else:
            left_used_key_nums.add(skkb__wowx)
            out_physical_to_logical_list.append(hhc__ixdq)
        left_physical_to_logical_list.append(skkb__wowx)
        left_logical_physical_map[skkb__wowx] = maij__afelr
        maij__afelr += 1
        left_key_in_output.append(jaoe__gfc)
    hnraj__pcp = tuple(hnraj__pcp)
    zxxs__vdn = []
    for sbg__rlj in range(len(join_node.left_col_names)):
        if (sbg__rlj not in join_node.left_dead_var_inds and sbg__rlj not in
            join_node.left_key_set):
            if not join_node.is_left_table:
                nks__dzx = join_node.left_vars[sbg__rlj]
                zxxs__vdn.append(nks__dzx)
            aape__qgcqg = 1
            ppvj__yiolb = 1
            hhc__ixdq = join_node.left_to_output_map[sbg__rlj]
            if sbg__rlj in join_node.left_cond_cols:
                if hhc__ixdq not in join_node.out_used_cols:
                    aape__qgcqg = 0
                left_key_in_output.append(aape__qgcqg)
            elif sbg__rlj in join_node.left_dead_var_inds:
                aape__qgcqg = 0
                ppvj__yiolb = 0
            if aape__qgcqg:
                out_physical_to_logical_list.append(hhc__ixdq)
            if ppvj__yiolb:
                left_physical_to_logical_list.append(sbg__rlj)
                left_logical_physical_map[sbg__rlj] = maij__afelr
                maij__afelr += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            zxxs__vdn.append(join_node.left_vars[join_node.index_col_num])
        hhc__ixdq = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(hhc__ixdq)
        left_physical_to_logical_list.append(join_node.index_col_num)
    zxxs__vdn = tuple(zxxs__vdn)
    if join_node.is_left_table:
        zxxs__vdn = tuple(join_node.get_live_left_vars())
    flv__rwwe = []
    for sbg__rlj, iux__nvqw in enumerate(join_node.right_keys):
        skkb__wowx = join_node.right_var_map[iux__nvqw]
        if not join_node.is_right_table:
            flv__rwwe.append(join_node.right_vars[skkb__wowx])
        if not join_node.vect_same_key[sbg__rlj] and not join_node.is_join:
            jaoe__gfc = 1
            if skkb__wowx not in join_node.right_to_output_map:
                jaoe__gfc = 0
            else:
                hhc__ixdq = join_node.right_to_output_map[skkb__wowx]
                if iux__nvqw == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        skkb__wowx):
                        out_physical_to_logical_list.append(hhc__ixdq)
                        right_used_key_nums.add(skkb__wowx)
                    else:
                        jaoe__gfc = 0
                elif hhc__ixdq not in join_node.out_used_cols:
                    jaoe__gfc = 0
                elif skkb__wowx in right_used_key_nums:
                    jaoe__gfc = 0
                else:
                    right_used_key_nums.add(skkb__wowx)
                    out_physical_to_logical_list.append(hhc__ixdq)
            right_key_in_output.append(jaoe__gfc)
        right_physical_to_logical_list.append(skkb__wowx)
        right_logical_physical_map[skkb__wowx] = mleb__erbc
        mleb__erbc += 1
    flv__rwwe = tuple(flv__rwwe)
    myo__esahe = []
    for sbg__rlj in range(len(join_node.right_col_names)):
        if (sbg__rlj not in join_node.right_dead_var_inds and sbg__rlj not in
            join_node.right_key_set):
            if not join_node.is_right_table:
                myo__esahe.append(join_node.right_vars[sbg__rlj])
            aape__qgcqg = 1
            ppvj__yiolb = 1
            hhc__ixdq = join_node.right_to_output_map[sbg__rlj]
            if sbg__rlj in join_node.right_cond_cols:
                if hhc__ixdq not in join_node.out_used_cols:
                    aape__qgcqg = 0
                right_key_in_output.append(aape__qgcqg)
            elif sbg__rlj in join_node.right_dead_var_inds:
                aape__qgcqg = 0
                ppvj__yiolb = 0
            if aape__qgcqg:
                out_physical_to_logical_list.append(hhc__ixdq)
            if ppvj__yiolb:
                right_physical_to_logical_list.append(sbg__rlj)
                right_logical_physical_map[sbg__rlj] = mleb__erbc
                mleb__erbc += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            myo__esahe.append(join_node.right_vars[join_node.index_col_num])
        hhc__ixdq = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(hhc__ixdq)
        right_physical_to_logical_list.append(join_node.index_col_num)
    myo__esahe = tuple(myo__esahe)
    if join_node.is_right_table:
        myo__esahe = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    btxf__vcb = hnraj__pcp + flv__rwwe + zxxs__vdn + myo__esahe
    porhr__bhw = tuple(typemap[nks__dzx.name] for nks__dzx in btxf__vcb)
    left_other_names = tuple('t1_c' + str(sbg__rlj) for sbg__rlj in range(
        len(zxxs__vdn)))
    right_other_names = tuple('t2_c' + str(sbg__rlj) for sbg__rlj in range(
        len(myo__esahe)))
    if join_node.is_left_table:
        wgtue__eld = ()
    else:
        wgtue__eld = tuple('t1_key' + str(sbg__rlj) for sbg__rlj in range(
            oimq__zav))
    if join_node.is_right_table:
        yxqr__zpw = ()
    else:
        yxqr__zpw = tuple('t2_key' + str(sbg__rlj) for sbg__rlj in range(
            oimq__zav))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(wgtue__eld + yxqr__zpw +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            syj__cuhol = typemap[join_node.left_vars[0].name]
        else:
            syj__cuhol = types.none
        for lro__mtwi in left_physical_to_logical_list:
            if lro__mtwi < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                jgulh__zrj = syj__cuhol.arr_types[lro__mtwi]
            else:
                jgulh__zrj = typemap[join_node.left_vars[-1].name]
            if lro__mtwi in join_node.left_key_set:
                left_key_types.append(jgulh__zrj)
            else:
                left_other_types.append(jgulh__zrj)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[nks__dzx.name] for nks__dzx in
            hnraj__pcp)
        left_other_types = tuple([typemap[iux__nvqw.name] for iux__nvqw in
            zxxs__vdn])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            syj__cuhol = typemap[join_node.right_vars[0].name]
        else:
            syj__cuhol = types.none
        for lro__mtwi in right_physical_to_logical_list:
            if lro__mtwi < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                jgulh__zrj = syj__cuhol.arr_types[lro__mtwi]
            else:
                jgulh__zrj = typemap[join_node.right_vars[-1].name]
            if lro__mtwi in join_node.right_key_set:
                right_key_types.append(jgulh__zrj)
            else:
                right_other_types.append(jgulh__zrj)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[nks__dzx.name] for nks__dzx in
            flv__rwwe)
        right_other_types = tuple([typemap[iux__nvqw.name] for iux__nvqw in
            myo__esahe])
    matched_key_types = []
    for sbg__rlj in range(oimq__zav):
        sknov__hfqkj = _match_join_key_types(left_key_types[sbg__rlj],
            right_key_types[sbg__rlj], loc)
        glbs[f'key_type_{sbg__rlj}'] = sknov__hfqkj
        matched_key_types.append(sknov__hfqkj)
    if join_node.is_left_table:
        wbv__nlakp = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if wbv__nlakp:
            kim__nff = False
            uaxdq__kbfmy = False
            alklt__ljbc = None
            if join_node.has_live_left_table_var:
                zfx__lxba = list(typemap[join_node.left_vars[0].name].arr_types
                    )
            else:
                zfx__lxba = None
            for ubfyw__bsx, jgulh__zrj in wbv__nlakp.items():
                if ubfyw__bsx < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    zfx__lxba[ubfyw__bsx] = jgulh__zrj
                    kim__nff = True
                else:
                    alklt__ljbc = jgulh__zrj
                    uaxdq__kbfmy = True
            if kim__nff:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(zfx__lxba))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if uaxdq__kbfmy:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = alklt__ljbc
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({wgtue__eld[sbg__rlj]}, key_type_{sbg__rlj})'
             if left_key_types[sbg__rlj] != matched_key_types[sbg__rlj] else
            f'{wgtue__eld[sbg__rlj]}' for sbg__rlj in range(oimq__zav)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        wbv__nlakp = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if wbv__nlakp:
            kim__nff = False
            uaxdq__kbfmy = False
            alklt__ljbc = None
            if join_node.has_live_right_table_var:
                zfx__lxba = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                zfx__lxba = None
            for ubfyw__bsx, jgulh__zrj in wbv__nlakp.items():
                if ubfyw__bsx < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    zfx__lxba[ubfyw__bsx] = jgulh__zrj
                    kim__nff = True
                else:
                    alklt__ljbc = jgulh__zrj
                    uaxdq__kbfmy = True
            if kim__nff:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(zfx__lxba))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if uaxdq__kbfmy:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = alklt__ljbc
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({yxqr__zpw[sbg__rlj]}, key_type_{sbg__rlj})'
             if right_key_types[sbg__rlj] != matched_key_types[sbg__rlj] else
            f'{yxqr__zpw[sbg__rlj]}' for sbg__rlj in range(oimq__zav)))
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
        for sbg__rlj in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(sbg__rlj,
                sbg__rlj)
        for sbg__rlj in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(sbg__rlj,
                sbg__rlj)
        for sbg__rlj in range(oimq__zav):
            func_text += f'    t1_keys_{sbg__rlj} = out_t1_keys[{sbg__rlj}]\n'
        for sbg__rlj in range(oimq__zav):
            func_text += f'    t2_keys_{sbg__rlj} = out_t2_keys[{sbg__rlj}]\n'
    ozetb__mip = {}
    exec(func_text, {}, ozetb__mip)
    ncp__avqo = ozetb__mip['f']
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
    rquk__vlsr = compile_to_numba_ir(ncp__avqo, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=porhr__bhw, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(rquk__vlsr, btxf__vcb)
    fgjqf__fng = rquk__vlsr.body[:-3]
    if join_node.has_live_out_index_var:
        fgjqf__fng[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        fgjqf__fng[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        fgjqf__fng.pop(-1)
    elif not join_node.has_live_out_table_var:
        fgjqf__fng.pop(-2)
    return fgjqf__fng


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    xbydv__qckmf = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{xbydv__qckmf}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    ozetb__mip = {}
    exec(func_text, table_getitem_funcs, ozetb__mip)
    bmn__rmyvt = ozetb__mip[f'bodo_join_gen_cond{xbydv__qckmf}']
    hoszx__qqwkp = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    mvkhv__gac = numba.cfunc(hoszx__qqwkp, nopython=True)(bmn__rmyvt)
    join_gen_cond_cfunc[mvkhv__gac.native_name] = mvkhv__gac
    join_gen_cond_cfunc_addr[mvkhv__gac.native_name] = mvkhv__gac.address
    return mvkhv__gac, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    lqmf__uvb = []
    for iux__nvqw, bjf__idexo in name_to_var_map.items():
        ewx__ezdud = f'({table_name}.{iux__nvqw})'
        if ewx__ezdud not in expr:
            continue
        undx__fjvj = f'getitem_{table_name}_val_{bjf__idexo}'
        fuz__hpazz = f'_bodo_{table_name}_val_{bjf__idexo}'
        if is_table_var:
            xav__egmy = typemap[col_vars[0].name].arr_types[bjf__idexo]
        else:
            xav__egmy = typemap[col_vars[bjf__idexo].name]
        if is_str_arr_type(xav__egmy) or xav__egmy == bodo.binary_array_type:
            func_text += f"""  {fuz__hpazz}, {fuz__hpazz}_size = {undx__fjvj}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {fuz__hpazz} = bodo.libs.str_arr_ext.decode_utf8({fuz__hpazz}, {fuz__hpazz}_size)
"""
        else:
            func_text += (
                f'  {fuz__hpazz} = {undx__fjvj}({table_name}_data1, {table_name}_ind)\n'
                )
        mzei__mqmh = logical_to_physical_ind[bjf__idexo]
        table_getitem_funcs[undx__fjvj
            ] = bodo.libs.array._gen_row_access_intrinsic(xav__egmy, mzei__mqmh
            )
        expr = expr.replace(ewx__ezdud, fuz__hpazz)
        otxc__uuy = f'({na_check_name}.{table_name}.{iux__nvqw})'
        if otxc__uuy in expr:
            sps__kkm = f'nacheck_{table_name}_val_{bjf__idexo}'
            rco__ajq = f'_bodo_isna_{table_name}_val_{bjf__idexo}'
            if isinstance(xav__egmy, bodo.libs.int_arr_ext.IntegerArrayType
                ) or xav__egmy in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(xav__egmy):
                func_text += f"""  {rco__ajq} = {sps__kkm}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {rco__ajq} = {sps__kkm}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[sps__kkm
                ] = bodo.libs.array._gen_row_na_check_intrinsic(xav__egmy,
                mzei__mqmh)
            expr = expr.replace(otxc__uuy, rco__ajq)
        if bjf__idexo not in key_set:
            lqmf__uvb.append(mzei__mqmh)
    return expr, func_text, lqmf__uvb


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as svbnz__ehjk:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    ktcfw__trpi = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[nks__dzx.name] in ktcfw__trpi for
        nks__dzx in join_node.get_live_left_vars())
    right_parallel = all(array_dists[nks__dzx.name] in ktcfw__trpi for
        nks__dzx in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[nks__dzx.name] in ktcfw__trpi for
            nks__dzx in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[nks__dzx.name] in ktcfw__trpi for
            nks__dzx in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[nks__dzx.name] in ktcfw__trpi for nks__dzx in
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
    qqtnt__xct = set(left_col_nums)
    hexes__fmryh = set(right_col_nums)
    pmxar__kzpek = join_node.vect_same_key
    nwih__wpro = []
    for sbg__rlj in range(len(left_key_types)):
        if left_key_in_output[sbg__rlj]:
            nwih__wpro.append(needs_typechange(matched_key_types[sbg__rlj],
                join_node.is_right, pmxar__kzpek[sbg__rlj]))
    ezlb__etlps = len(left_key_types)
    hlmo__psx = 0
    odu__hiekr = left_physical_to_logical_list[len(left_key_types):]
    for sbg__rlj, lro__mtwi in enumerate(odu__hiekr):
        qnx__rdbak = True
        if lro__mtwi in qqtnt__xct:
            qnx__rdbak = left_key_in_output[ezlb__etlps]
            ezlb__etlps += 1
        if qnx__rdbak:
            nwih__wpro.append(needs_typechange(left_other_types[sbg__rlj],
                join_node.is_right, False))
    for sbg__rlj in range(len(right_key_types)):
        if not pmxar__kzpek[sbg__rlj] and not join_node.is_join:
            if right_key_in_output[hlmo__psx]:
                nwih__wpro.append(needs_typechange(matched_key_types[
                    sbg__rlj], join_node.is_left, False))
            hlmo__psx += 1
    rwp__sajx = right_physical_to_logical_list[len(right_key_types):]
    for sbg__rlj, lro__mtwi in enumerate(rwp__sajx):
        qnx__rdbak = True
        if lro__mtwi in hexes__fmryh:
            qnx__rdbak = right_key_in_output[hlmo__psx]
            hlmo__psx += 1
        if qnx__rdbak:
            nwih__wpro.append(needs_typechange(right_other_types[sbg__rlj],
                join_node.is_left, False))
    oimq__zav = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            iztwy__rcwy = left_other_names[1:]
            vbr__inmd = left_other_names[0]
        else:
            iztwy__rcwy = left_other_names
            vbr__inmd = None
        tfwho__sdp = '()' if len(iztwy__rcwy) == 0 else f'({iztwy__rcwy[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({vbr__inmd}, {tfwho__sdp}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        dqlo__ukdg = []
        for sbg__rlj in range(oimq__zav):
            dqlo__ukdg.append('t1_keys[{}]'.format(sbg__rlj))
        for sbg__rlj in range(len(left_other_names)):
            dqlo__ukdg.append('data_left[{}]'.format(sbg__rlj))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(wou__tat) for wou__tat in dqlo__ukdg))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            dvs__wjy = right_other_names[1:]
            vbr__inmd = right_other_names[0]
        else:
            dvs__wjy = right_other_names
            vbr__inmd = None
        tfwho__sdp = '()' if len(dvs__wjy) == 0 else f'({dvs__wjy[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({vbr__inmd}, {tfwho__sdp}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        tjc__cyjpa = []
        for sbg__rlj in range(oimq__zav):
            tjc__cyjpa.append('t2_keys[{}]'.format(sbg__rlj))
        for sbg__rlj in range(len(right_other_names)):
            tjc__cyjpa.append('data_right[{}]'.format(sbg__rlj))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(wou__tat) for wou__tat in tjc__cyjpa))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(pmxar__kzpek, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(nwih__wpro, dtype=np.int64)
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
        .format(left_parallel, right_parallel, oimq__zav, len(odu__hiekr),
        len(rwp__sajx), join_node.is_left, join_node.is_right, join_node.
        is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    xedwa__putkk = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {xedwa__putkk}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        jzv__suq = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{jzv__suq}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        wbv__nlakp = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        wbv__nlakp.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        kim__nff = False
        uaxdq__kbfmy = False
        if join_node.has_live_out_table_var:
            zfx__lxba = list(out_table_type.arr_types)
        else:
            zfx__lxba = None
        for ubfyw__bsx, jgulh__zrj in wbv__nlakp.items():
            if ubfyw__bsx < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                zfx__lxba[ubfyw__bsx] = jgulh__zrj
                kim__nff = True
            else:
                alklt__ljbc = jgulh__zrj
                uaxdq__kbfmy = True
        if kim__nff:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            oezc__bdrlx = bodo.TableType(tuple(zfx__lxba))
            glbs['py_table_type'] = oezc__bdrlx
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if uaxdq__kbfmy:
            glbs['index_col_type'] = alklt__ljbc
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
    wbv__nlakp: Dict[int, types.Type] = {}
    oimq__zav = len(matched_key_types)
    for sbg__rlj in range(oimq__zav):
        if used_key_nums is None or sbg__rlj in used_key_nums:
            if matched_key_types[sbg__rlj] != key_types[sbg__rlj] and (
                convert_dict_col or key_types[sbg__rlj] != bodo.
                dict_str_arr_type):
                if output_map:
                    jzv__suq = output_map[sbg__rlj]
                else:
                    jzv__suq = sbg__rlj
                wbv__nlakp[jzv__suq] = matched_key_types[sbg__rlj]
    return wbv__nlakp


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    wxhqt__iiy = bodo.libs.distributed_api.get_size()
    encfj__edo = np.empty(wxhqt__iiy, left_key_arrs[0].dtype)
    rckhl__bsg = np.empty(wxhqt__iiy, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(encfj__edo, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(rckhl__bsg, left_key_arrs[0][-1])
    fuuf__uoxqy = np.zeros(wxhqt__iiy, np.int32)
    kzu__lzkbq = np.zeros(wxhqt__iiy, np.int32)
    zfazl__vganv = np.zeros(wxhqt__iiy, np.int32)
    gkft__jywbb = right_key_arrs[0][0]
    xajc__dvqco = right_key_arrs[0][-1]
    rbj__goulq = -1
    sbg__rlj = 0
    while sbg__rlj < wxhqt__iiy - 1 and rckhl__bsg[sbg__rlj] < gkft__jywbb:
        sbg__rlj += 1
    while sbg__rlj < wxhqt__iiy and encfj__edo[sbg__rlj] <= xajc__dvqco:
        rbj__goulq, izw__ffrs = _count_overlap(right_key_arrs[0],
            encfj__edo[sbg__rlj], rckhl__bsg[sbg__rlj])
        if rbj__goulq != 0:
            rbj__goulq -= 1
            izw__ffrs += 1
        fuuf__uoxqy[sbg__rlj] = izw__ffrs
        kzu__lzkbq[sbg__rlj] = rbj__goulq
        sbg__rlj += 1
    while sbg__rlj < wxhqt__iiy:
        fuuf__uoxqy[sbg__rlj] = 1
        kzu__lzkbq[sbg__rlj] = len(right_key_arrs[0]) - 1
        sbg__rlj += 1
    bodo.libs.distributed_api.alltoall(fuuf__uoxqy, zfazl__vganv, 1)
    jbsmt__ivsgl = zfazl__vganv.sum()
    iqeeh__zghha = np.empty(jbsmt__ivsgl, right_key_arrs[0].dtype)
    lxp__phr = alloc_arr_tup(jbsmt__ivsgl, right_data)
    qtr__fxkc = bodo.ir.join.calc_disp(zfazl__vganv)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], iqeeh__zghha,
        fuuf__uoxqy, zfazl__vganv, kzu__lzkbq, qtr__fxkc)
    bodo.libs.distributed_api.alltoallv_tup(right_data, lxp__phr,
        fuuf__uoxqy, zfazl__vganv, kzu__lzkbq, qtr__fxkc)
    return (iqeeh__zghha,), lxp__phr


@numba.njit
def _count_overlap(r_key_arr, start, end):
    izw__ffrs = 0
    rbj__goulq = 0
    mkwfp__rapxp = 0
    while mkwfp__rapxp < len(r_key_arr) and r_key_arr[mkwfp__rapxp] < start:
        rbj__goulq += 1
        mkwfp__rapxp += 1
    while mkwfp__rapxp < len(r_key_arr) and start <= r_key_arr[mkwfp__rapxp
        ] <= end:
        mkwfp__rapxp += 1
        izw__ffrs += 1
    return rbj__goulq, izw__ffrs


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    zzk__cccoh = np.empty_like(arr)
    zzk__cccoh[0] = 0
    for sbg__rlj in range(1, len(arr)):
        zzk__cccoh[sbg__rlj] = zzk__cccoh[sbg__rlj - 1] + arr[sbg__rlj - 1]
    return zzk__cccoh


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    bjmq__lgt = len(left_keys[0])
    czcn__sqz = len(right_keys[0])
    xejq__vlgi = alloc_arr_tup(bjmq__lgt, left_keys)
    rktud__mgew = alloc_arr_tup(bjmq__lgt, right_keys)
    vrl__rrgbz = alloc_arr_tup(bjmq__lgt, data_left)
    nhrg__ltk = alloc_arr_tup(bjmq__lgt, data_right)
    ragt__gkya = 0
    xmp__xjw = 0
    for ragt__gkya in range(bjmq__lgt):
        if xmp__xjw < 0:
            xmp__xjw = 0
        while xmp__xjw < czcn__sqz and getitem_arr_tup(right_keys, xmp__xjw
            ) <= getitem_arr_tup(left_keys, ragt__gkya):
            xmp__xjw += 1
        xmp__xjw -= 1
        setitem_arr_tup(xejq__vlgi, ragt__gkya, getitem_arr_tup(left_keys,
            ragt__gkya))
        setitem_arr_tup(vrl__rrgbz, ragt__gkya, getitem_arr_tup(data_left,
            ragt__gkya))
        if xmp__xjw >= 0:
            setitem_arr_tup(rktud__mgew, ragt__gkya, getitem_arr_tup(
                right_keys, xmp__xjw))
            setitem_arr_tup(nhrg__ltk, ragt__gkya, getitem_arr_tup(
                data_right, xmp__xjw))
        else:
            bodo.libs.array_kernels.setna_tup(rktud__mgew, ragt__gkya)
            bodo.libs.array_kernels.setna_tup(nhrg__ltk, ragt__gkya)
    return xejq__vlgi, rktud__mgew, vrl__rrgbz, nhrg__ltk
