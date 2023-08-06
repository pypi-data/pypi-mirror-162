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
    ctd__gqygd = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    ckue__mkvke = []
    for rqx__toz in node.out_vars:
        bmeqh__whth = typemap[rqx__toz.name]
        if bmeqh__whth == types.none:
            continue
        hdpkv__pte = array_analysis._gen_shape_call(equiv_set, rqx__toz,
            bmeqh__whth.ndim, None, ctd__gqygd)
        equiv_set.insert_equiv(rqx__toz, hdpkv__pte)
        ckue__mkvke.append(hdpkv__pte[0])
        equiv_set.define(rqx__toz, set())
    if len(ckue__mkvke) > 1:
        equiv_set.insert_equiv(*ckue__mkvke)
    return [], ctd__gqygd


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        mwojn__xqatw = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        mwojn__xqatw = Distribution.OneD_Var
    else:
        mwojn__xqatw = Distribution.OneD
    for kjf__qmgo in node.out_vars:
        if kjf__qmgo.name in array_dists:
            mwojn__xqatw = Distribution(min(mwojn__xqatw.value, array_dists
                [kjf__qmgo.name].value))
    for kjf__qmgo in node.out_vars:
        array_dists[kjf__qmgo.name] = mwojn__xqatw


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
    for rqx__toz, bmeqh__whth in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(rqx__toz.name, bmeqh__whth, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    lkong__xhykr = []
    for rqx__toz in node.out_vars:
        nizm__eeqm = visit_vars_inner(rqx__toz, callback, cbdata)
        lkong__xhykr.append(nizm__eeqm)
    node.out_vars = lkong__xhykr
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for tdfhf__rbn in node.filters:
            for als__etzxd in range(len(tdfhf__rbn)):
                kiod__tcq = tdfhf__rbn[als__etzxd]
                tdfhf__rbn[als__etzxd] = kiod__tcq[0], kiod__tcq[1
                    ], visit_vars_inner(kiod__tcq[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({kjf__qmgo.name for kjf__qmgo in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for tkkn__tjf in node.filters:
            for kjf__qmgo in tkkn__tjf:
                if isinstance(kjf__qmgo[2], ir.Var):
                    use_set.add(kjf__qmgo[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    ncxme__swxbf = set(kjf__qmgo.name for kjf__qmgo in node.out_vars)
    return set(), ncxme__swxbf


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    lkong__xhykr = []
    for rqx__toz in node.out_vars:
        nizm__eeqm = replace_vars_inner(rqx__toz, var_dict)
        lkong__xhykr.append(nizm__eeqm)
    node.out_vars = lkong__xhykr
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for tdfhf__rbn in node.filters:
            for als__etzxd in range(len(tdfhf__rbn)):
                kiod__tcq = tdfhf__rbn[als__etzxd]
                tdfhf__rbn[als__etzxd] = kiod__tcq[0], kiod__tcq[1
                    ], replace_vars_inner(kiod__tcq[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for rqx__toz in node.out_vars:
        xuo__uota = definitions[rqx__toz.name]
        if node not in xuo__uota:
            xuo__uota.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        mpbv__jwwnu = [kjf__qmgo[2] for tkkn__tjf in filters for kjf__qmgo in
            tkkn__tjf]
        rkx__rrts = set()
        for rvfav__xiz in mpbv__jwwnu:
            if isinstance(rvfav__xiz, ir.Var):
                if rvfav__xiz.name not in rkx__rrts:
                    filter_vars.append(rvfav__xiz)
                rkx__rrts.add(rvfav__xiz.name)
        return {kjf__qmgo.name: f'f{als__etzxd}' for als__etzxd, kjf__qmgo in
            enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {als__etzxd for als__etzxd in used_columns if als__etzxd <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    qkwz__kfrv = {}
    for als__etzxd, deg__riert in enumerate(df_type.data):
        if isinstance(deg__riert, bodo.IntegerArrayType):
            hjfv__uklqv = deg__riert.get_pandas_scalar_type_instance
            if hjfv__uklqv not in qkwz__kfrv:
                qkwz__kfrv[hjfv__uklqv] = []
            qkwz__kfrv[hjfv__uklqv].append(df.columns[als__etzxd])
    for bmeqh__whth, hgkj__ijp in qkwz__kfrv.items():
        df[hgkj__ijp] = df[hgkj__ijp].astype(bmeqh__whth)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    bfgeq__zjxoi = node.out_vars[0].name
    assert isinstance(typemap[bfgeq__zjxoi], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, ebnc__qckgf, ttzcu__gqk = get_live_column_nums_block(
            column_live_map, equiv_vars, bfgeq__zjxoi)
        if not (ebnc__qckgf or ttzcu__gqk):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    xkuw__lcw = False
    if array_dists is not None:
        bhk__knvu = node.out_vars[0].name
        xkuw__lcw = array_dists[bhk__knvu] in (Distribution.OneD,
            Distribution.OneD_Var)
        fblp__myl = node.out_vars[1].name
        assert typemap[fblp__myl
            ] == types.none or not xkuw__lcw or array_dists[fblp__myl] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return xkuw__lcw


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    dsxj__jsi = 'None'
    zifz__nev = 'None'
    if filters:
        lqb__tbr = []
        hfca__ectlw = []
        srn__hdph = False
        orig_colname_map = {qnnw__cpd: als__etzxd for als__etzxd, qnnw__cpd in
            enumerate(col_names)}
        for tdfhf__rbn in filters:
            zikzw__xhlu = []
            jpvo__ppyu = []
            for kjf__qmgo in tdfhf__rbn:
                if isinstance(kjf__qmgo[2], ir.Var):
                    iyh__yqvae, jsi__urnp = determine_filter_cast(
                        original_out_types, typemap, kjf__qmgo,
                        orig_colname_map, partition_names, source)
                    if kjf__qmgo[1] == 'in':
                        bkod__dre = (
                            f"(ds.field('{kjf__qmgo[0]}').isin({filter_map[kjf__qmgo[2].name]}))"
                            )
                    else:
                        bkod__dre = (
                            f"(ds.field('{kjf__qmgo[0]}'){iyh__yqvae} {kjf__qmgo[1]} ds.scalar({filter_map[kjf__qmgo[2].name]}){jsi__urnp})"
                            )
                else:
                    assert kjf__qmgo[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if kjf__qmgo[1] == 'is not':
                        tab__qvlq = '~'
                    else:
                        tab__qvlq = ''
                    bkod__dre = (
                        f"({tab__qvlq}ds.field('{kjf__qmgo[0]}').is_null())")
                jpvo__ppyu.append(bkod__dre)
                if not srn__hdph:
                    if kjf__qmgo[0] in partition_names and isinstance(kjf__qmgo
                        [2], ir.Var):
                        if output_dnf:
                            thns__zmp = (
                                f"('{kjf__qmgo[0]}', '{kjf__qmgo[1]}', {filter_map[kjf__qmgo[2].name]})"
                                )
                        else:
                            thns__zmp = bkod__dre
                        zikzw__xhlu.append(thns__zmp)
                    elif kjf__qmgo[0] in partition_names and not isinstance(
                        kjf__qmgo[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            thns__zmp = (
                                f"('{kjf__qmgo[0]}', '{kjf__qmgo[1]}', '{kjf__qmgo[2]}')"
                                )
                        else:
                            thns__zmp = bkod__dre
                        zikzw__xhlu.append(thns__zmp)
            czjh__ttd = ''
            if zikzw__xhlu:
                if output_dnf:
                    czjh__ttd = ', '.join(zikzw__xhlu)
                else:
                    czjh__ttd = ' & '.join(zikzw__xhlu)
            else:
                srn__hdph = True
            sdd__qad = ' & '.join(jpvo__ppyu)
            if czjh__ttd:
                if output_dnf:
                    lqb__tbr.append(f'[{czjh__ttd}]')
                else:
                    lqb__tbr.append(f'({czjh__ttd})')
            hfca__ectlw.append(f'({sdd__qad})')
        if output_dnf:
            saec__ash = ', '.join(lqb__tbr)
        else:
            saec__ash = ' | '.join(lqb__tbr)
        lsbn__iucwf = ' | '.join(hfca__ectlw)
        if saec__ash and not srn__hdph:
            if output_dnf:
                dsxj__jsi = f'[{saec__ash}]'
            else:
                dsxj__jsi = f'({saec__ash})'
        zifz__nev = f'({lsbn__iucwf})'
    return dsxj__jsi, zifz__nev


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    fii__cregs = filter_val[0]
    shggk__mszuh = col_types[orig_colname_map[fii__cregs]]
    xslxu__ofplz = bodo.utils.typing.element_type(shggk__mszuh)
    if source == 'parquet' and fii__cregs in partition_names:
        if xslxu__ofplz == types.unicode_type:
            qfby__kxq = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(xslxu__ofplz, types.Integer):
            qfby__kxq = f'.cast(pyarrow.{xslxu__ofplz.name}(), safe=False)'
        else:
            qfby__kxq = ''
    else:
        qfby__kxq = ''
    owlmb__xhimq = typemap[filter_val[2].name]
    if isinstance(owlmb__xhimq, (types.List, types.Set)):
        ulxst__qwxj = owlmb__xhimq.dtype
    else:
        ulxst__qwxj = owlmb__xhimq
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(xslxu__ofplz,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ulxst__qwxj,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([xslxu__ofplz, ulxst__qwxj]
        ):
        if not bodo.utils.typing.is_safe_arrow_cast(xslxu__ofplz, ulxst__qwxj):
            raise BodoError(
                f'Unsupported Arrow cast from {xslxu__ofplz} to {ulxst__qwxj} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if xslxu__ofplz == types.unicode_type and ulxst__qwxj in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif ulxst__qwxj == types.unicode_type and xslxu__ofplz in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(owlmb__xhimq, (types.List, types.Set)):
                rqmj__ywol = 'list' if isinstance(owlmb__xhimq, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {rqmj__ywol} values with isin filter pushdown.'
                    )
            return qfby__kxq, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif xslxu__ofplz == bodo.datetime_date_type and ulxst__qwxj in (bodo
            .datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif ulxst__qwxj == bodo.datetime_date_type and xslxu__ofplz in (bodo
            .datetime64ns, bodo.pd_timestamp_type):
            return qfby__kxq, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return qfby__kxq, ''
