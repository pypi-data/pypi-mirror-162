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
        ucf__ozmp = func.signature
        wqtcx__yse = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        vxmwm__rhmgk = cgutils.get_or_insert_function(builder.module,
            wqtcx__yse, sym._literal_value)
        builder.call(vxmwm__rhmgk, [context.get_constant_null(ucf__ozmp.
            args[0]), context.get_constant_null(ucf__ozmp.args[1]), context
            .get_constant_null(ucf__ozmp.args[2]), context.
            get_constant_null(ucf__ozmp.args[3]), context.get_constant_null
            (ucf__ozmp.args[4]), context.get_constant_null(ucf__ozmp.args[5
            ]), context.get_constant(types.int64, 0), context.get_constant(
            types.int64, 0)])
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
        qrixe__aen = left_df_type.columns
        jvhbl__kpiab = right_df_type.columns
        self.left_col_names = qrixe__aen
        self.right_col_names = jvhbl__kpiab
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(qrixe__aen) if self.is_left_table else 0
        self.n_right_table_cols = len(jvhbl__kpiab
            ) if self.is_right_table else 0
        nyog__yha = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        xkhq__dxc = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(nyog__yha)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(xkhq__dxc)
        self.left_var_map = {exe__kxrdy: aun__axqg for aun__axqg,
            exe__kxrdy in enumerate(qrixe__aen)}
        self.right_var_map = {exe__kxrdy: aun__axqg for aun__axqg,
            exe__kxrdy in enumerate(jvhbl__kpiab)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = nyog__yha
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = xkhq__dxc
        self.left_key_set = set(self.left_var_map[exe__kxrdy] for
            exe__kxrdy in left_keys)
        self.right_key_set = set(self.right_var_map[exe__kxrdy] for
            exe__kxrdy in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[exe__kxrdy] for
                exe__kxrdy in qrixe__aen if f'(left.{exe__kxrdy})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[exe__kxrdy] for
                exe__kxrdy in jvhbl__kpiab if f'(right.{exe__kxrdy})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        vizl__qvfx: int = -1
        ccclj__mspxw = set(left_keys) & set(right_keys)
        zofh__bvzyy = set(qrixe__aen) & set(jvhbl__kpiab)
        sel__vcq = zofh__bvzyy - ccclj__mspxw
        qai__ukh: Dict[int, (Literal['left', 'right'], int)] = {}
        qwpn__nwxbi: Dict[int, int] = {}
        dbtyo__rhg: Dict[int, int] = {}
        for aun__axqg, exe__kxrdy in enumerate(qrixe__aen):
            if exe__kxrdy in sel__vcq:
                wzwf__ltppr = str(exe__kxrdy) + suffix_left
                qgso__iuc = out_df_type.column_index[wzwf__ltppr]
                if (right_index and not left_index and aun__axqg in self.
                    left_key_set):
                    vizl__qvfx = out_df_type.column_index[exe__kxrdy]
                    qai__ukh[vizl__qvfx] = 'left', aun__axqg
            else:
                qgso__iuc = out_df_type.column_index[exe__kxrdy]
            qai__ukh[qgso__iuc] = 'left', aun__axqg
            qwpn__nwxbi[aun__axqg] = qgso__iuc
        for aun__axqg, exe__kxrdy in enumerate(jvhbl__kpiab):
            if exe__kxrdy not in ccclj__mspxw:
                if exe__kxrdy in sel__vcq:
                    sfni__pwxs = str(exe__kxrdy) + suffix_right
                    qgso__iuc = out_df_type.column_index[sfni__pwxs]
                    if (left_index and not right_index and aun__axqg in
                        self.right_key_set):
                        vizl__qvfx = out_df_type.column_index[exe__kxrdy]
                        qai__ukh[vizl__qvfx] = 'right', aun__axqg
                else:
                    qgso__iuc = out_df_type.column_index[exe__kxrdy]
                qai__ukh[qgso__iuc] = 'right', aun__axqg
                dbtyo__rhg[aun__axqg] = qgso__iuc
        if self.left_vars[-1] is not None:
            qwpn__nwxbi[nyog__yha] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            dbtyo__rhg[xkhq__dxc] = self.n_out_table_cols
        self.out_to_input_col_map = qai__ukh
        self.left_to_output_map = qwpn__nwxbi
        self.right_to_output_map = dbtyo__rhg
        self.extra_data_col_num = vizl__qvfx
        if len(out_data_vars) > 1:
            znyt__rjais = 'left' if right_index else 'right'
            if znyt__rjais == 'left':
                war__zsum = nyog__yha
            elif znyt__rjais == 'right':
                war__zsum = xkhq__dxc
        else:
            znyt__rjais = None
            war__zsum = -1
        self.index_source = znyt__rjais
        self.index_col_num = war__zsum
        yss__omcm = []
        zkz__cys = len(left_keys)
        for ymcpf__gig in range(zkz__cys):
            oav__mrs = left_keys[ymcpf__gig]
            hhzd__dix = right_keys[ymcpf__gig]
            yss__omcm.append(oav__mrs == hhzd__dix)
        self.vect_same_key = yss__omcm

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
        for talb__jxoq in self.left_vars:
            if talb__jxoq is not None:
                vars.append(talb__jxoq)
        return vars

    def get_live_right_vars(self):
        vars = []
        for talb__jxoq in self.right_vars:
            if talb__jxoq is not None:
                vars.append(talb__jxoq)
        return vars

    def get_live_out_vars(self):
        vars = []
        for talb__jxoq in self.out_data_vars:
            if talb__jxoq is not None:
                vars.append(talb__jxoq)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        ebjp__aenp = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[ebjp__aenp])
                ebjp__aenp += 1
            else:
                left_vars.append(None)
            start = 1
        fnol__vkz = max(self.n_left_table_cols - 1, 0)
        for aun__axqg in range(start, len(self.left_vars)):
            if aun__axqg + fnol__vkz in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[ebjp__aenp])
                ebjp__aenp += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        ebjp__aenp = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[ebjp__aenp])
                ebjp__aenp += 1
            else:
                right_vars.append(None)
            start = 1
        fnol__vkz = max(self.n_right_table_cols - 1, 0)
        for aun__axqg in range(start, len(self.right_vars)):
            if aun__axqg + fnol__vkz in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[ebjp__aenp])
                ebjp__aenp += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        tmc__lsn = [self.has_live_out_table_var, self.has_live_out_index_var]
        ebjp__aenp = 0
        for aun__axqg in range(len(self.out_data_vars)):
            if not tmc__lsn[aun__axqg]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[ebjp__aenp])
                ebjp__aenp += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {aun__axqg for aun__axqg in self.out_used_cols if aun__axqg <
            self.n_out_table_cols}

    def __repr__(self):
        fni__wzsi = ', '.join([f'{exe__kxrdy}' for exe__kxrdy in self.
            left_col_names])
        nzn__bgm = f'left={{{fni__wzsi}}}'
        fni__wzsi = ', '.join([f'{exe__kxrdy}' for exe__kxrdy in self.
            right_col_names])
        rjrtq__vfh = f'right={{{fni__wzsi}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, nzn__bgm, rjrtq__vfh)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    htyg__vjyse = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    hmqau__elj = []
    ramjc__qfpn = join_node.get_live_left_vars()
    for kpcum__xim in ramjc__qfpn:
        thz__llwm = typemap[kpcum__xim.name]
        hdftr__gjmqp = equiv_set.get_shape(kpcum__xim)
        if hdftr__gjmqp:
            hmqau__elj.append(hdftr__gjmqp[0])
    if len(hmqau__elj) > 1:
        equiv_set.insert_equiv(*hmqau__elj)
    hmqau__elj = []
    ramjc__qfpn = list(join_node.get_live_right_vars())
    for kpcum__xim in ramjc__qfpn:
        thz__llwm = typemap[kpcum__xim.name]
        hdftr__gjmqp = equiv_set.get_shape(kpcum__xim)
        if hdftr__gjmqp:
            hmqau__elj.append(hdftr__gjmqp[0])
    if len(hmqau__elj) > 1:
        equiv_set.insert_equiv(*hmqau__elj)
    hmqau__elj = []
    for tqpy__uxd in join_node.get_live_out_vars():
        thz__llwm = typemap[tqpy__uxd.name]
        bcxn__yelrv = array_analysis._gen_shape_call(equiv_set, tqpy__uxd,
            thz__llwm.ndim, None, htyg__vjyse)
        equiv_set.insert_equiv(tqpy__uxd, bcxn__yelrv)
        hmqau__elj.append(bcxn__yelrv[0])
        equiv_set.define(tqpy__uxd, set())
    if len(hmqau__elj) > 1:
        equiv_set.insert_equiv(*hmqau__elj)
    return [], htyg__vjyse


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    noq__qqhpu = Distribution.OneD
    ngv__rbz = Distribution.OneD
    for kpcum__xim in join_node.get_live_left_vars():
        noq__qqhpu = Distribution(min(noq__qqhpu.value, array_dists[
            kpcum__xim.name].value))
    for kpcum__xim in join_node.get_live_right_vars():
        ngv__rbz = Distribution(min(ngv__rbz.value, array_dists[kpcum__xim.
            name].value))
    sdpcz__toaj = Distribution.OneD_Var
    for tqpy__uxd in join_node.get_live_out_vars():
        if tqpy__uxd.name in array_dists:
            sdpcz__toaj = Distribution(min(sdpcz__toaj.value, array_dists[
                tqpy__uxd.name].value))
    uau__fftut = Distribution(min(sdpcz__toaj.value, noq__qqhpu.value))
    grjiz__viaqw = Distribution(min(sdpcz__toaj.value, ngv__rbz.value))
    sdpcz__toaj = Distribution(max(uau__fftut.value, grjiz__viaqw.value))
    for tqpy__uxd in join_node.get_live_out_vars():
        array_dists[tqpy__uxd.name] = sdpcz__toaj
    if sdpcz__toaj != Distribution.OneD_Var:
        noq__qqhpu = sdpcz__toaj
        ngv__rbz = sdpcz__toaj
    for kpcum__xim in join_node.get_live_left_vars():
        array_dists[kpcum__xim.name] = noq__qqhpu
    for kpcum__xim in join_node.get_live_right_vars():
        array_dists[kpcum__xim.name] = ngv__rbz
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(talb__jxoq, callback,
        cbdata) for talb__jxoq in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(talb__jxoq, callback,
        cbdata) for talb__jxoq in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(talb__jxoq, callback,
        cbdata) for talb__jxoq in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        lgp__lqm = []
        mfgtm__ggh = join_node.get_out_table_var()
        if mfgtm__ggh.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for kzsnb__jwkm in join_node.out_to_input_col_map.keys():
            if kzsnb__jwkm in join_node.out_used_cols:
                continue
            lgp__lqm.append(kzsnb__jwkm)
            if join_node.indicator_col_num == kzsnb__jwkm:
                join_node.indicator_col_num = -1
                continue
            if kzsnb__jwkm == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            wrhll__kjvea, kzsnb__jwkm = join_node.out_to_input_col_map[
                kzsnb__jwkm]
            if wrhll__kjvea == 'left':
                if (kzsnb__jwkm not in join_node.left_key_set and 
                    kzsnb__jwkm not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(kzsnb__jwkm)
                    if not join_node.is_left_table:
                        join_node.left_vars[kzsnb__jwkm] = None
            elif wrhll__kjvea == 'right':
                if (kzsnb__jwkm not in join_node.right_key_set and 
                    kzsnb__jwkm not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(kzsnb__jwkm)
                    if not join_node.is_right_table:
                        join_node.right_vars[kzsnb__jwkm] = None
        for aun__axqg in lgp__lqm:
            del join_node.out_to_input_col_map[aun__axqg]
        if join_node.is_left_table:
            aaa__hawh = set(range(join_node.n_left_table_cols))
            gjfho__eyt = not bool(aaa__hawh - join_node.left_dead_var_inds)
            if gjfho__eyt:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            aaa__hawh = set(range(join_node.n_right_table_cols))
            gjfho__eyt = not bool(aaa__hawh - join_node.right_dead_var_inds)
            if gjfho__eyt:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        ioiu__zcb = join_node.get_out_index_var()
        if ioiu__zcb.name not in lives:
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
    xtgr__qubo = False
    if join_node.has_live_out_table_var:
        rdbxu__zkya = join_node.get_out_table_var().name
        jbhr__szrx, kfrw__evogy, pmul__twvx = get_live_column_nums_block(
            column_live_map, equiv_vars, rdbxu__zkya)
        if not (kfrw__evogy or pmul__twvx):
            jbhr__szrx = trim_extra_used_columns(jbhr__szrx, join_node.
                n_out_table_cols)
            bpldd__qdb = join_node.get_out_table_used_cols()
            if len(jbhr__szrx) != len(bpldd__qdb):
                xtgr__qubo = not (join_node.is_left_table and join_node.
                    is_right_table)
                pce__sxfff = bpldd__qdb - jbhr__szrx
                join_node.out_used_cols = join_node.out_used_cols - pce__sxfff
    return xtgr__qubo


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        lon__mmg = join_node.get_out_table_var()
        actle__ofqx, kfrw__evogy, pmul__twvx = _compute_table_column_uses(
            lon__mmg.name, table_col_use_map, equiv_vars)
    else:
        actle__ofqx, kfrw__evogy, pmul__twvx = set(), False, False
    if join_node.has_live_left_table_var:
        czo__ssve = join_node.left_vars[0].name
        dxfd__enk, wdgu__jdyn, qwk__ddrh = block_use_map[czo__ssve]
        if not (wdgu__jdyn or qwk__ddrh):
            bjm__izplx = set([join_node.out_to_input_col_map[aun__axqg][1] for
                aun__axqg in actle__ofqx if join_node.out_to_input_col_map[
                aun__axqg][0] == 'left'])
            hxqeg__eew = set(aun__axqg for aun__axqg in join_node.
                left_key_set | join_node.left_cond_cols if aun__axqg <
                join_node.n_left_table_cols)
            if not (kfrw__evogy or pmul__twvx):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (bjm__izplx | hxqeg__eew)
            block_use_map[czo__ssve] = (dxfd__enk | bjm__izplx | hxqeg__eew,
                kfrw__evogy or pmul__twvx, False)
    if join_node.has_live_right_table_var:
        csetz__gqgci = join_node.right_vars[0].name
        dxfd__enk, wdgu__jdyn, qwk__ddrh = block_use_map[csetz__gqgci]
        if not (wdgu__jdyn or qwk__ddrh):
            whfm__hqp = set([join_node.out_to_input_col_map[aun__axqg][1] for
                aun__axqg in actle__ofqx if join_node.out_to_input_col_map[
                aun__axqg][0] == 'right'])
            jmqfp__vyvle = set(aun__axqg for aun__axqg in join_node.
                right_key_set | join_node.right_cond_cols if aun__axqg <
                join_node.n_right_table_cols)
            if not (kfrw__evogy or pmul__twvx):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (whfm__hqp | jmqfp__vyvle)
            block_use_map[csetz__gqgci] = (dxfd__enk | whfm__hqp |
                jmqfp__vyvle, kfrw__evogy or pmul__twvx, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({ugb__zpltu.name for ugb__zpltu in join_node.
        get_live_left_vars()})
    use_set.update({ugb__zpltu.name for ugb__zpltu in join_node.
        get_live_right_vars()})
    def_set.update({ugb__zpltu.name for ugb__zpltu in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    ekhhk__tifba = set(ugb__zpltu.name for ugb__zpltu in join_node.
        get_live_out_vars())
    return set(), ekhhk__tifba


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(talb__jxoq, var_dict) for
        talb__jxoq in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(talb__jxoq, var_dict) for
        talb__jxoq in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(talb__jxoq,
        var_dict) for talb__jxoq in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for kpcum__xim in join_node.get_live_out_vars():
        definitions[kpcum__xim.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        kcum__frqn = join_node.loc.strformat()
        ufk__sbpmn = [join_node.left_col_names[aun__axqg] for aun__axqg in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        ffv__ptfqn = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', ffv__ptfqn,
            kcum__frqn, ufk__sbpmn)
        kdrqy__vxrct = [join_node.right_col_names[aun__axqg] for aun__axqg in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        ffv__ptfqn = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', ffv__ptfqn,
            kcum__frqn, kdrqy__vxrct)
        eyvo__hsrbv = [join_node.out_col_names[aun__axqg] for aun__axqg in
            sorted(join_node.get_out_table_used_cols())]
        ffv__ptfqn = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', ffv__ptfqn,
            kcum__frqn, eyvo__hsrbv)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    zkz__cys = len(join_node.left_keys)
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
    plsb__qst = 0
    onqc__qeonp = 0
    gazj__ekt = []
    for exe__kxrdy in join_node.left_keys:
        mgch__yogcf = join_node.left_var_map[exe__kxrdy]
        if not join_node.is_left_table:
            gazj__ekt.append(join_node.left_vars[mgch__yogcf])
        tmc__lsn = 1
        qgso__iuc = join_node.left_to_output_map[mgch__yogcf]
        if exe__kxrdy == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == mgch__yogcf):
                out_physical_to_logical_list.append(qgso__iuc)
                left_used_key_nums.add(mgch__yogcf)
            else:
                tmc__lsn = 0
        elif qgso__iuc not in join_node.out_used_cols:
            tmc__lsn = 0
        elif mgch__yogcf in left_used_key_nums:
            tmc__lsn = 0
        else:
            left_used_key_nums.add(mgch__yogcf)
            out_physical_to_logical_list.append(qgso__iuc)
        left_physical_to_logical_list.append(mgch__yogcf)
        left_logical_physical_map[mgch__yogcf] = plsb__qst
        plsb__qst += 1
        left_key_in_output.append(tmc__lsn)
    gazj__ekt = tuple(gazj__ekt)
    hniy__nurvt = []
    for aun__axqg in range(len(join_node.left_col_names)):
        if (aun__axqg not in join_node.left_dead_var_inds and aun__axqg not in
            join_node.left_key_set):
            if not join_node.is_left_table:
                ugb__zpltu = join_node.left_vars[aun__axqg]
                hniy__nurvt.append(ugb__zpltu)
            kqrv__ocgcz = 1
            avyi__wqx = 1
            qgso__iuc = join_node.left_to_output_map[aun__axqg]
            if aun__axqg in join_node.left_cond_cols:
                if qgso__iuc not in join_node.out_used_cols:
                    kqrv__ocgcz = 0
                left_key_in_output.append(kqrv__ocgcz)
            elif aun__axqg in join_node.left_dead_var_inds:
                kqrv__ocgcz = 0
                avyi__wqx = 0
            if kqrv__ocgcz:
                out_physical_to_logical_list.append(qgso__iuc)
            if avyi__wqx:
                left_physical_to_logical_list.append(aun__axqg)
                left_logical_physical_map[aun__axqg] = plsb__qst
                plsb__qst += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            hniy__nurvt.append(join_node.left_vars[join_node.index_col_num])
        qgso__iuc = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(qgso__iuc)
        left_physical_to_logical_list.append(join_node.index_col_num)
    hniy__nurvt = tuple(hniy__nurvt)
    if join_node.is_left_table:
        hniy__nurvt = tuple(join_node.get_live_left_vars())
    wbnzi__fmyqj = []
    for aun__axqg, exe__kxrdy in enumerate(join_node.right_keys):
        mgch__yogcf = join_node.right_var_map[exe__kxrdy]
        if not join_node.is_right_table:
            wbnzi__fmyqj.append(join_node.right_vars[mgch__yogcf])
        if not join_node.vect_same_key[aun__axqg] and not join_node.is_join:
            tmc__lsn = 1
            if mgch__yogcf not in join_node.right_to_output_map:
                tmc__lsn = 0
            else:
                qgso__iuc = join_node.right_to_output_map[mgch__yogcf]
                if exe__kxrdy == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        mgch__yogcf):
                        out_physical_to_logical_list.append(qgso__iuc)
                        right_used_key_nums.add(mgch__yogcf)
                    else:
                        tmc__lsn = 0
                elif qgso__iuc not in join_node.out_used_cols:
                    tmc__lsn = 0
                elif mgch__yogcf in right_used_key_nums:
                    tmc__lsn = 0
                else:
                    right_used_key_nums.add(mgch__yogcf)
                    out_physical_to_logical_list.append(qgso__iuc)
            right_key_in_output.append(tmc__lsn)
        right_physical_to_logical_list.append(mgch__yogcf)
        right_logical_physical_map[mgch__yogcf] = onqc__qeonp
        onqc__qeonp += 1
    wbnzi__fmyqj = tuple(wbnzi__fmyqj)
    olcb__ifsn = []
    for aun__axqg in range(len(join_node.right_col_names)):
        if (aun__axqg not in join_node.right_dead_var_inds and aun__axqg not in
            join_node.right_key_set):
            if not join_node.is_right_table:
                olcb__ifsn.append(join_node.right_vars[aun__axqg])
            kqrv__ocgcz = 1
            avyi__wqx = 1
            qgso__iuc = join_node.right_to_output_map[aun__axqg]
            if aun__axqg in join_node.right_cond_cols:
                if qgso__iuc not in join_node.out_used_cols:
                    kqrv__ocgcz = 0
                right_key_in_output.append(kqrv__ocgcz)
            elif aun__axqg in join_node.right_dead_var_inds:
                kqrv__ocgcz = 0
                avyi__wqx = 0
            if kqrv__ocgcz:
                out_physical_to_logical_list.append(qgso__iuc)
            if avyi__wqx:
                right_physical_to_logical_list.append(aun__axqg)
                right_logical_physical_map[aun__axqg] = onqc__qeonp
                onqc__qeonp += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            olcb__ifsn.append(join_node.right_vars[join_node.index_col_num])
        qgso__iuc = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(qgso__iuc)
        right_physical_to_logical_list.append(join_node.index_col_num)
    olcb__ifsn = tuple(olcb__ifsn)
    if join_node.is_right_table:
        olcb__ifsn = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    txhgv__fka = gazj__ekt + wbnzi__fmyqj + hniy__nurvt + olcb__ifsn
    uapa__zlkk = tuple(typemap[ugb__zpltu.name] for ugb__zpltu in txhgv__fka)
    left_other_names = tuple('t1_c' + str(aun__axqg) for aun__axqg in range
        (len(hniy__nurvt)))
    right_other_names = tuple('t2_c' + str(aun__axqg) for aun__axqg in
        range(len(olcb__ifsn)))
    if join_node.is_left_table:
        lgbc__wbkix = ()
    else:
        lgbc__wbkix = tuple('t1_key' + str(aun__axqg) for aun__axqg in
            range(zkz__cys))
    if join_node.is_right_table:
        dbfkg__wua = ()
    else:
        dbfkg__wua = tuple('t2_key' + str(aun__axqg) for aun__axqg in range
            (zkz__cys))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(lgbc__wbkix + dbfkg__wua +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            xuwka__puzy = typemap[join_node.left_vars[0].name]
        else:
            xuwka__puzy = types.none
        for noj__wim in left_physical_to_logical_list:
            if noj__wim < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                thz__llwm = xuwka__puzy.arr_types[noj__wim]
            else:
                thz__llwm = typemap[join_node.left_vars[-1].name]
            if noj__wim in join_node.left_key_set:
                left_key_types.append(thz__llwm)
            else:
                left_other_types.append(thz__llwm)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[ugb__zpltu.name] for ugb__zpltu in
            gazj__ekt)
        left_other_types = tuple([typemap[exe__kxrdy.name] for exe__kxrdy in
            hniy__nurvt])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            xuwka__puzy = typemap[join_node.right_vars[0].name]
        else:
            xuwka__puzy = types.none
        for noj__wim in right_physical_to_logical_list:
            if noj__wim < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                thz__llwm = xuwka__puzy.arr_types[noj__wim]
            else:
                thz__llwm = typemap[join_node.right_vars[-1].name]
            if noj__wim in join_node.right_key_set:
                right_key_types.append(thz__llwm)
            else:
                right_other_types.append(thz__llwm)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[ugb__zpltu.name] for ugb__zpltu in
            wbnzi__fmyqj)
        right_other_types = tuple([typemap[exe__kxrdy.name] for exe__kxrdy in
            olcb__ifsn])
    matched_key_types = []
    for aun__axqg in range(zkz__cys):
        nty__rjo = _match_join_key_types(left_key_types[aun__axqg],
            right_key_types[aun__axqg], loc)
        glbs[f'key_type_{aun__axqg}'] = nty__rjo
        matched_key_types.append(nty__rjo)
    if join_node.is_left_table:
        zlhkk__xtr = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if zlhkk__xtr:
            jve__ary = False
            ieg__nyy = False
            xol__lgf = None
            if join_node.has_live_left_table_var:
                xbn__hur = list(typemap[join_node.left_vars[0].name].arr_types)
            else:
                xbn__hur = None
            for kzsnb__jwkm, thz__llwm in zlhkk__xtr.items():
                if kzsnb__jwkm < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    xbn__hur[kzsnb__jwkm] = thz__llwm
                    jve__ary = True
                else:
                    xol__lgf = thz__llwm
                    ieg__nyy = True
            if jve__ary:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(xbn__hur))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if ieg__nyy:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = xol__lgf
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({lgbc__wbkix[aun__axqg]}, key_type_{aun__axqg})'
             if left_key_types[aun__axqg] != matched_key_types[aun__axqg] else
            f'{lgbc__wbkix[aun__axqg]}' for aun__axqg in range(zkz__cys)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        zlhkk__xtr = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if zlhkk__xtr:
            jve__ary = False
            ieg__nyy = False
            xol__lgf = None
            if join_node.has_live_right_table_var:
                xbn__hur = list(typemap[join_node.right_vars[0].name].arr_types
                    )
            else:
                xbn__hur = None
            for kzsnb__jwkm, thz__llwm in zlhkk__xtr.items():
                if kzsnb__jwkm < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    xbn__hur[kzsnb__jwkm] = thz__llwm
                    jve__ary = True
                else:
                    xol__lgf = thz__llwm
                    ieg__nyy = True
            if jve__ary:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(xbn__hur))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if ieg__nyy:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = xol__lgf
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({dbfkg__wua[aun__axqg]}, key_type_{aun__axqg})'
             if right_key_types[aun__axqg] != matched_key_types[aun__axqg] else
            f'{dbfkg__wua[aun__axqg]}' for aun__axqg in range(zkz__cys)))
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
        for aun__axqg in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(aun__axqg,
                aun__axqg)
        for aun__axqg in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(aun__axqg
                , aun__axqg)
        for aun__axqg in range(zkz__cys):
            func_text += (
                f'    t1_keys_{aun__axqg} = out_t1_keys[{aun__axqg}]\n')
        for aun__axqg in range(zkz__cys):
            func_text += (
                f'    t2_keys_{aun__axqg} = out_t2_keys[{aun__axqg}]\n')
    gllib__cicvb = {}
    exec(func_text, {}, gllib__cicvb)
    vozjw__nnfk = gllib__cicvb['f']
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
    ydan__yobl = compile_to_numba_ir(vozjw__nnfk, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=uapa__zlkk, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(ydan__yobl, txhgv__fka)
    bsgnb__rdrwb = ydan__yobl.body[:-3]
    if join_node.has_live_out_index_var:
        bsgnb__rdrwb[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        bsgnb__rdrwb[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        bsgnb__rdrwb.pop(-1)
    elif not join_node.has_live_out_table_var:
        bsgnb__rdrwb.pop(-2)
    return bsgnb__rdrwb


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    ftm__yerm = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{ftm__yerm}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    gllib__cicvb = {}
    exec(func_text, table_getitem_funcs, gllib__cicvb)
    bzv__jrj = gllib__cicvb[f'bodo_join_gen_cond{ftm__yerm}']
    cekb__ooj = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    jqwav__zbz = numba.cfunc(cekb__ooj, nopython=True)(bzv__jrj)
    join_gen_cond_cfunc[jqwav__zbz.native_name] = jqwav__zbz
    join_gen_cond_cfunc_addr[jqwav__zbz.native_name] = jqwav__zbz.address
    return jqwav__zbz, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    jlvsi__zli = []
    for exe__kxrdy, etzl__uvfbl in name_to_var_map.items():
        ski__ehi = f'({table_name}.{exe__kxrdy})'
        if ski__ehi not in expr:
            continue
        fjdw__jqpbb = f'getitem_{table_name}_val_{etzl__uvfbl}'
        vddf__nfk = f'_bodo_{table_name}_val_{etzl__uvfbl}'
        if is_table_var:
            mxti__ilngy = typemap[col_vars[0].name].arr_types[etzl__uvfbl]
        else:
            mxti__ilngy = typemap[col_vars[etzl__uvfbl].name]
        if is_str_arr_type(mxti__ilngy
            ) or mxti__ilngy == bodo.binary_array_type:
            func_text += f"""  {vddf__nfk}, {vddf__nfk}_size = {fjdw__jqpbb}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {vddf__nfk} = bodo.libs.str_arr_ext.decode_utf8({vddf__nfk}, {vddf__nfk}_size)
"""
        else:
            func_text += (
                f'  {vddf__nfk} = {fjdw__jqpbb}({table_name}_data1, {table_name}_ind)\n'
                )
        eqxm__fesmy = logical_to_physical_ind[etzl__uvfbl]
        table_getitem_funcs[fjdw__jqpbb
            ] = bodo.libs.array._gen_row_access_intrinsic(mxti__ilngy,
            eqxm__fesmy)
        expr = expr.replace(ski__ehi, vddf__nfk)
        tow__ialwq = f'({na_check_name}.{table_name}.{exe__kxrdy})'
        if tow__ialwq in expr:
            vplbt__wbdvh = f'nacheck_{table_name}_val_{etzl__uvfbl}'
            lcoz__lmyg = f'_bodo_isna_{table_name}_val_{etzl__uvfbl}'
            if isinstance(mxti__ilngy, bodo.libs.int_arr_ext.IntegerArrayType
                ) or mxti__ilngy in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(mxti__ilngy):
                func_text += f"""  {lcoz__lmyg} = {vplbt__wbdvh}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {lcoz__lmyg} = {vplbt__wbdvh}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[vplbt__wbdvh
                ] = bodo.libs.array._gen_row_na_check_intrinsic(mxti__ilngy,
                eqxm__fesmy)
            expr = expr.replace(tow__ialwq, lcoz__lmyg)
        if etzl__uvfbl not in key_set:
            jlvsi__zli.append(eqxm__fesmy)
    return expr, func_text, jlvsi__zli


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as mead__zmk:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    ajvzk__zfx = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[ugb__zpltu.name] in ajvzk__zfx for
        ugb__zpltu in join_node.get_live_left_vars())
    right_parallel = all(array_dists[ugb__zpltu.name] in ajvzk__zfx for
        ugb__zpltu in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[ugb__zpltu.name] in ajvzk__zfx for
            ugb__zpltu in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[ugb__zpltu.name] in ajvzk__zfx for
            ugb__zpltu in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[ugb__zpltu.name] in ajvzk__zfx for
            ugb__zpltu in join_node.get_live_out_vars())
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
    rysos__tsqy = set(left_col_nums)
    buoq__pzqbu = set(right_col_nums)
    yss__omcm = join_node.vect_same_key
    ihojc__kfcj = []
    for aun__axqg in range(len(left_key_types)):
        if left_key_in_output[aun__axqg]:
            ihojc__kfcj.append(needs_typechange(matched_key_types[aun__axqg
                ], join_node.is_right, yss__omcm[aun__axqg]))
    kise__qvtj = len(left_key_types)
    cseuh__ywlot = 0
    ayrwq__moe = left_physical_to_logical_list[len(left_key_types):]
    for aun__axqg, noj__wim in enumerate(ayrwq__moe):
        zebkc__wrm = True
        if noj__wim in rysos__tsqy:
            zebkc__wrm = left_key_in_output[kise__qvtj]
            kise__qvtj += 1
        if zebkc__wrm:
            ihojc__kfcj.append(needs_typechange(left_other_types[aun__axqg],
                join_node.is_right, False))
    for aun__axqg in range(len(right_key_types)):
        if not yss__omcm[aun__axqg] and not join_node.is_join:
            if right_key_in_output[cseuh__ywlot]:
                ihojc__kfcj.append(needs_typechange(matched_key_types[
                    aun__axqg], join_node.is_left, False))
            cseuh__ywlot += 1
    zcczy__erknx = right_physical_to_logical_list[len(right_key_types):]
    for aun__axqg, noj__wim in enumerate(zcczy__erknx):
        zebkc__wrm = True
        if noj__wim in buoq__pzqbu:
            zebkc__wrm = right_key_in_output[cseuh__ywlot]
            cseuh__ywlot += 1
        if zebkc__wrm:
            ihojc__kfcj.append(needs_typechange(right_other_types[aun__axqg
                ], join_node.is_left, False))
    zkz__cys = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            ezjm__ader = left_other_names[1:]
            mfgtm__ggh = left_other_names[0]
        else:
            ezjm__ader = left_other_names
            mfgtm__ggh = None
        dqyzs__kvx = '()' if len(ezjm__ader) == 0 else f'({ezjm__ader[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({mfgtm__ggh}, {dqyzs__kvx}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        vbmm__hupj = []
        for aun__axqg in range(zkz__cys):
            vbmm__hupj.append('t1_keys[{}]'.format(aun__axqg))
        for aun__axqg in range(len(left_other_names)):
            vbmm__hupj.append('data_left[{}]'.format(aun__axqg))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(yiur__zdmxm) for yiur__zdmxm in
            vbmm__hupj))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            lnq__hfdbp = right_other_names[1:]
            mfgtm__ggh = right_other_names[0]
        else:
            lnq__hfdbp = right_other_names
            mfgtm__ggh = None
        dqyzs__kvx = '()' if len(lnq__hfdbp) == 0 else f'({lnq__hfdbp[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({mfgtm__ggh}, {dqyzs__kvx}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        jlv__rener = []
        for aun__axqg in range(zkz__cys):
            jlv__rener.append('t2_keys[{}]'.format(aun__axqg))
        for aun__axqg in range(len(right_other_names)):
            jlv__rener.append('data_right[{}]'.format(aun__axqg))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(yiur__zdmxm) for yiur__zdmxm in
            jlv__rener))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(yss__omcm, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(ihojc__kfcj, dtype=np.int64)
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
        .format(left_parallel, right_parallel, zkz__cys, len(ayrwq__moe),
        len(zcczy__erknx), join_node.is_left, join_node.is_right, join_node
        .is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    drot__dtcf = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {drot__dtcf}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        ebjp__aenp = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{ebjp__aenp}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        zlhkk__xtr = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        zlhkk__xtr.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        jve__ary = False
        ieg__nyy = False
        if join_node.has_live_out_table_var:
            xbn__hur = list(out_table_type.arr_types)
        else:
            xbn__hur = None
        for kzsnb__jwkm, thz__llwm in zlhkk__xtr.items():
            if kzsnb__jwkm < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                xbn__hur[kzsnb__jwkm] = thz__llwm
                jve__ary = True
            else:
                xol__lgf = thz__llwm
                ieg__nyy = True
        if jve__ary:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            tlgh__vqr = bodo.TableType(tuple(xbn__hur))
            glbs['py_table_type'] = tlgh__vqr
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if ieg__nyy:
            glbs['index_col_type'] = xol__lgf
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
    zlhkk__xtr: Dict[int, types.Type] = {}
    zkz__cys = len(matched_key_types)
    for aun__axqg in range(zkz__cys):
        if used_key_nums is None or aun__axqg in used_key_nums:
            if matched_key_types[aun__axqg] != key_types[aun__axqg] and (
                convert_dict_col or key_types[aun__axqg] != bodo.
                dict_str_arr_type):
                if output_map:
                    ebjp__aenp = output_map[aun__axqg]
                else:
                    ebjp__aenp = aun__axqg
                zlhkk__xtr[ebjp__aenp] = matched_key_types[aun__axqg]
    return zlhkk__xtr


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    vsb__sta = bodo.libs.distributed_api.get_size()
    evz__cafhl = np.empty(vsb__sta, left_key_arrs[0].dtype)
    ysl__nhfc = np.empty(vsb__sta, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(evz__cafhl, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(ysl__nhfc, left_key_arrs[0][-1])
    zlha__ejl = np.zeros(vsb__sta, np.int32)
    mcey__ontun = np.zeros(vsb__sta, np.int32)
    suga__nfjgd = np.zeros(vsb__sta, np.int32)
    gbemg__liqb = right_key_arrs[0][0]
    qkrwb__qoim = right_key_arrs[0][-1]
    fnol__vkz = -1
    aun__axqg = 0
    while aun__axqg < vsb__sta - 1 and ysl__nhfc[aun__axqg] < gbemg__liqb:
        aun__axqg += 1
    while aun__axqg < vsb__sta and evz__cafhl[aun__axqg] <= qkrwb__qoim:
        fnol__vkz, gyj__npd = _count_overlap(right_key_arrs[0], evz__cafhl[
            aun__axqg], ysl__nhfc[aun__axqg])
        if fnol__vkz != 0:
            fnol__vkz -= 1
            gyj__npd += 1
        zlha__ejl[aun__axqg] = gyj__npd
        mcey__ontun[aun__axqg] = fnol__vkz
        aun__axqg += 1
    while aun__axqg < vsb__sta:
        zlha__ejl[aun__axqg] = 1
        mcey__ontun[aun__axqg] = len(right_key_arrs[0]) - 1
        aun__axqg += 1
    bodo.libs.distributed_api.alltoall(zlha__ejl, suga__nfjgd, 1)
    ibrpp__bqsqb = suga__nfjgd.sum()
    hqlqk__nis = np.empty(ibrpp__bqsqb, right_key_arrs[0].dtype)
    tcuvr__hygpt = alloc_arr_tup(ibrpp__bqsqb, right_data)
    bnrl__ahfp = bodo.ir.join.calc_disp(suga__nfjgd)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], hqlqk__nis,
        zlha__ejl, suga__nfjgd, mcey__ontun, bnrl__ahfp)
    bodo.libs.distributed_api.alltoallv_tup(right_data, tcuvr__hygpt,
        zlha__ejl, suga__nfjgd, mcey__ontun, bnrl__ahfp)
    return (hqlqk__nis,), tcuvr__hygpt


@numba.njit
def _count_overlap(r_key_arr, start, end):
    gyj__npd = 0
    fnol__vkz = 0
    lzk__esvf = 0
    while lzk__esvf < len(r_key_arr) and r_key_arr[lzk__esvf] < start:
        fnol__vkz += 1
        lzk__esvf += 1
    while lzk__esvf < len(r_key_arr) and start <= r_key_arr[lzk__esvf] <= end:
        lzk__esvf += 1
        gyj__npd += 1
    return fnol__vkz, gyj__npd


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    fhbj__mtkhx = np.empty_like(arr)
    fhbj__mtkhx[0] = 0
    for aun__axqg in range(1, len(arr)):
        fhbj__mtkhx[aun__axqg] = fhbj__mtkhx[aun__axqg - 1] + arr[aun__axqg - 1
            ]
    return fhbj__mtkhx


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    jll__oni = len(left_keys[0])
    elf__cwvo = len(right_keys[0])
    dbr__gcnr = alloc_arr_tup(jll__oni, left_keys)
    kky__otznr = alloc_arr_tup(jll__oni, right_keys)
    jfeu__hvq = alloc_arr_tup(jll__oni, data_left)
    ynex__inh = alloc_arr_tup(jll__oni, data_right)
    oloch__smxz = 0
    ujzx__hndn = 0
    for oloch__smxz in range(jll__oni):
        if ujzx__hndn < 0:
            ujzx__hndn = 0
        while ujzx__hndn < elf__cwvo and getitem_arr_tup(right_keys, ujzx__hndn
            ) <= getitem_arr_tup(left_keys, oloch__smxz):
            ujzx__hndn += 1
        ujzx__hndn -= 1
        setitem_arr_tup(dbr__gcnr, oloch__smxz, getitem_arr_tup(left_keys,
            oloch__smxz))
        setitem_arr_tup(jfeu__hvq, oloch__smxz, getitem_arr_tup(data_left,
            oloch__smxz))
        if ujzx__hndn >= 0:
            setitem_arr_tup(kky__otznr, oloch__smxz, getitem_arr_tup(
                right_keys, ujzx__hndn))
            setitem_arr_tup(ynex__inh, oloch__smxz, getitem_arr_tup(
                data_right, ujzx__hndn))
        else:
            bodo.libs.array_kernels.setna_tup(kky__otznr, oloch__smxz)
            bodo.libs.array_kernels.setna_tup(ynex__inh, oloch__smxz)
    return dbr__gcnr, kky__otznr, jfeu__hvq, ynex__inh
