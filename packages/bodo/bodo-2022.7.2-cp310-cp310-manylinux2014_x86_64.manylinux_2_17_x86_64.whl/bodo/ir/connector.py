"""
Common IR extension functions for connectors such as CSV, Parquet and JSON readers.
"""
import sys
from collections import defaultdict
from typing import Literal, Set, Tuple
import numba
from numba.core import ir, types
from numba.core.ir_utils import replace_vars_inner, visit_vars_inner
from bodo.hiframes.table import TableType
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import get_live_column_nums_block
from bodo.utils.py_objs import install_py_obj_class
from bodo.utils.typing import BodoError
from bodo.utils.utils import debug_prints


def connector_array_analysis(node, equiv_set, typemap, array_analysis):
    evp__haerp = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    kre__zyad = []
    for qtbw__zodl in node.out_vars:
        gqmhz__ucqji = typemap[qtbw__zodl.name]
        if gqmhz__ucqji == types.none:
            continue
        ghl__rrt = array_analysis._gen_shape_call(equiv_set, qtbw__zodl,
            gqmhz__ucqji.ndim, None, evp__haerp)
        equiv_set.insert_equiv(qtbw__zodl, ghl__rrt)
        kre__zyad.append(ghl__rrt[0])
        equiv_set.define(qtbw__zodl, set())
    if len(kre__zyad) > 1:
        equiv_set.insert_equiv(*kre__zyad)
    return [], evp__haerp


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        eqld__fmuk = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        eqld__fmuk = Distribution.OneD_Var
    else:
        eqld__fmuk = Distribution.OneD
    for fscl__mey in node.out_vars:
        if fscl__mey.name in array_dists:
            eqld__fmuk = Distribution(min(eqld__fmuk.value, array_dists[
                fscl__mey.name].value))
    for fscl__mey in node.out_vars:
        array_dists[fscl__mey.name] = eqld__fmuk


def connector_typeinfer(node, typeinferer):
    if node.connector_typ == 'csv':
        if node.chunksize is not None:
            typeinferer.lock_type(node.out_vars[0].name, node.out_types[0],
                loc=node.loc)
        else:
            typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(
                node.out_types)), loc=node.loc)
            typeinferer.lock_type(node.out_vars[1].name, node.
                index_column_typ, loc=node.loc)
        return
    if node.connector_typ in ('parquet', 'sql'):
        typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(node.
            out_types)), loc=node.loc)
        typeinferer.lock_type(node.out_vars[1].name, node.index_column_type,
            loc=node.loc)
        return
    for qtbw__zodl, gqmhz__ucqji in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(qtbw__zodl.name, gqmhz__ucqji, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    tin__zmz = []
    for qtbw__zodl in node.out_vars:
        mzl__kwp = visit_vars_inner(qtbw__zodl, callback, cbdata)
        tin__zmz.append(mzl__kwp)
    node.out_vars = tin__zmz
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for lth__wlv in node.filters:
            for bzgop__jehf in range(len(lth__wlv)):
                ctt__kon = lth__wlv[bzgop__jehf]
                lth__wlv[bzgop__jehf] = ctt__kon[0], ctt__kon[1
                    ], visit_vars_inner(ctt__kon[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({fscl__mey.name for fscl__mey in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for aubj__atbp in node.filters:
            for fscl__mey in aubj__atbp:
                if isinstance(fscl__mey[2], ir.Var):
                    use_set.add(fscl__mey[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    smj__ykfug = set(fscl__mey.name for fscl__mey in node.out_vars)
    return set(), smj__ykfug


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    tin__zmz = []
    for qtbw__zodl in node.out_vars:
        mzl__kwp = replace_vars_inner(qtbw__zodl, var_dict)
        tin__zmz.append(mzl__kwp)
    node.out_vars = tin__zmz
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for lth__wlv in node.filters:
            for bzgop__jehf in range(len(lth__wlv)):
                ctt__kon = lth__wlv[bzgop__jehf]
                lth__wlv[bzgop__jehf] = ctt__kon[0], ctt__kon[1
                    ], replace_vars_inner(ctt__kon[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for qtbw__zodl in node.out_vars:
        gunl__tfmdy = definitions[qtbw__zodl.name]
        if node not in gunl__tfmdy:
            gunl__tfmdy.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        enuq__sinrp = [fscl__mey[2] for aubj__atbp in filters for fscl__mey in
            aubj__atbp]
        optyg__fwbo = set()
        for euq__segjd in enuq__sinrp:
            if isinstance(euq__segjd, ir.Var):
                if euq__segjd.name not in optyg__fwbo:
                    filter_vars.append(euq__segjd)
                optyg__fwbo.add(euq__segjd.name)
        return {fscl__mey.name: f'f{bzgop__jehf}' for bzgop__jehf,
            fscl__mey in enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {bzgop__jehf for bzgop__jehf in used_columns if bzgop__jehf <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    ttvpg__dag = {}
    for bzgop__jehf, ette__mryye in enumerate(df_type.data):
        if isinstance(ette__mryye, bodo.IntegerArrayType):
            bnw__wjxr = ette__mryye.get_pandas_scalar_type_instance
            if bnw__wjxr not in ttvpg__dag:
                ttvpg__dag[bnw__wjxr] = []
            ttvpg__dag[bnw__wjxr].append(df.columns[bzgop__jehf])
    for gqmhz__ucqji, ktc__qihkx in ttvpg__dag.items():
        df[ktc__qihkx] = df[ktc__qihkx].astype(gqmhz__ucqji)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    vzm__joy = node.out_vars[0].name
    assert isinstance(typemap[vzm__joy], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, kcw__qqpha, zaiqn__cbsd = get_live_column_nums_block(
            column_live_map, equiv_vars, vzm__joy)
        if not (kcw__qqpha or zaiqn__cbsd):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    wuezc__oullw = False
    if array_dists is not None:
        sujdy__sjkfq = node.out_vars[0].name
        wuezc__oullw = array_dists[sujdy__sjkfq] in (Distribution.OneD,
            Distribution.OneD_Var)
        akyc__agrji = node.out_vars[1].name
        assert typemap[akyc__agrji
            ] == types.none or not wuezc__oullw or array_dists[akyc__agrji
            ] in (Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return wuezc__oullw


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    cyfwk__mwmat = 'None'
    qnnaa__psv = 'None'
    if filters:
        yjw__liqz = []
        oad__mufpq = []
        jowim__wjvz = False
        orig_colname_map = {worwv__psl: bzgop__jehf for bzgop__jehf,
            worwv__psl in enumerate(col_names)}
        for lth__wlv in filters:
            xha__stegt = []
            phn__nbxzh = []
            for fscl__mey in lth__wlv:
                if isinstance(fscl__mey[2], ir.Var):
                    vxwsu__urjw, slwlm__ewdxv = determine_filter_cast(
                        original_out_types, typemap, fscl__mey,
                        orig_colname_map, partition_names, source)
                    if fscl__mey[1] == 'in':
                        jkx__wrxg = (
                            f"(ds.field('{fscl__mey[0]}').isin({filter_map[fscl__mey[2].name]}))"
                            )
                    else:
                        jkx__wrxg = (
                            f"(ds.field('{fscl__mey[0]}'){vxwsu__urjw} {fscl__mey[1]} ds.scalar({filter_map[fscl__mey[2].name]}){slwlm__ewdxv})"
                            )
                else:
                    assert fscl__mey[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if fscl__mey[1] == 'is not':
                        jbt__wcg = '~'
                    else:
                        jbt__wcg = ''
                    jkx__wrxg = (
                        f"({jbt__wcg}ds.field('{fscl__mey[0]}').is_null())")
                phn__nbxzh.append(jkx__wrxg)
                if not jowim__wjvz:
                    if fscl__mey[0] in partition_names and isinstance(fscl__mey
                        [2], ir.Var):
                        if output_dnf:
                            sxb__ijnm = (
                                f"('{fscl__mey[0]}', '{fscl__mey[1]}', {filter_map[fscl__mey[2].name]})"
                                )
                        else:
                            sxb__ijnm = jkx__wrxg
                        xha__stegt.append(sxb__ijnm)
                    elif fscl__mey[0] in partition_names and not isinstance(
                        fscl__mey[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            sxb__ijnm = (
                                f"('{fscl__mey[0]}', '{fscl__mey[1]}', '{fscl__mey[2]}')"
                                )
                        else:
                            sxb__ijnm = jkx__wrxg
                        xha__stegt.append(sxb__ijnm)
            wmvb__kjb = ''
            if xha__stegt:
                if output_dnf:
                    wmvb__kjb = ', '.join(xha__stegt)
                else:
                    wmvb__kjb = ' & '.join(xha__stegt)
            else:
                jowim__wjvz = True
            xww__hrbr = ' & '.join(phn__nbxzh)
            if wmvb__kjb:
                if output_dnf:
                    yjw__liqz.append(f'[{wmvb__kjb}]')
                else:
                    yjw__liqz.append(f'({wmvb__kjb})')
            oad__mufpq.append(f'({xww__hrbr})')
        if output_dnf:
            bqh__vggad = ', '.join(yjw__liqz)
        else:
            bqh__vggad = ' | '.join(yjw__liqz)
        bybd__rfx = ' | '.join(oad__mufpq)
        if bqh__vggad and not jowim__wjvz:
            if output_dnf:
                cyfwk__mwmat = f'[{bqh__vggad}]'
            else:
                cyfwk__mwmat = f'({bqh__vggad})'
        qnnaa__psv = f'({bybd__rfx})'
    return cyfwk__mwmat, qnnaa__psv


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    bprv__cpd = filter_val[0]
    ckoxi__bxg = col_types[orig_colname_map[bprv__cpd]]
    qzjg__ohjn = bodo.utils.typing.element_type(ckoxi__bxg)
    if source == 'parquet' and bprv__cpd in partition_names:
        if qzjg__ohjn == types.unicode_type:
            vpzmt__wcbtc = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(qzjg__ohjn, types.Integer):
            vpzmt__wcbtc = f'.cast(pyarrow.{qzjg__ohjn.name}(), safe=False)'
        else:
            vpzmt__wcbtc = ''
    else:
        vpzmt__wcbtc = ''
    dkdan__ssbpc = typemap[filter_val[2].name]
    if isinstance(dkdan__ssbpc, (types.List, types.Set)):
        gglv__zjp = dkdan__ssbpc.dtype
    else:
        gglv__zjp = dkdan__ssbpc
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(qzjg__ohjn,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(gglv__zjp,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([qzjg__ohjn, gglv__zjp]):
        if not bodo.utils.typing.is_safe_arrow_cast(qzjg__ohjn, gglv__zjp):
            raise BodoError(
                f'Unsupported Arrow cast from {qzjg__ohjn} to {gglv__zjp} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if qzjg__ohjn == types.unicode_type and gglv__zjp in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif gglv__zjp == types.unicode_type and qzjg__ohjn in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(dkdan__ssbpc, (types.List, types.Set)):
                olhz__bto = 'list' if isinstance(dkdan__ssbpc, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {olhz__bto} values with isin filter pushdown.'
                    )
            return vpzmt__wcbtc, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif qzjg__ohjn == bodo.datetime_date_type and gglv__zjp in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif gglv__zjp == bodo.datetime_date_type and qzjg__ohjn in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return vpzmt__wcbtc, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return vpzmt__wcbtc, ''
