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
    wzhv__tnb = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    kqeqd__mus = []
    for evsgq__iqbdl in node.out_vars:
        vyzve__lns = typemap[evsgq__iqbdl.name]
        if vyzve__lns == types.none:
            continue
        dtu__yko = array_analysis._gen_shape_call(equiv_set, evsgq__iqbdl,
            vyzve__lns.ndim, None, wzhv__tnb)
        equiv_set.insert_equiv(evsgq__iqbdl, dtu__yko)
        kqeqd__mus.append(dtu__yko[0])
        equiv_set.define(evsgq__iqbdl, set())
    if len(kqeqd__mus) > 1:
        equiv_set.insert_equiv(*kqeqd__mus)
    return [], wzhv__tnb


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        lgv__rakat = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        lgv__rakat = Distribution.OneD_Var
    else:
        lgv__rakat = Distribution.OneD
    for vgtvb__ylal in node.out_vars:
        if vgtvb__ylal.name in array_dists:
            lgv__rakat = Distribution(min(lgv__rakat.value, array_dists[
                vgtvb__ylal.name].value))
    for vgtvb__ylal in node.out_vars:
        array_dists[vgtvb__ylal.name] = lgv__rakat


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
    for evsgq__iqbdl, vyzve__lns in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(evsgq__iqbdl.name, vyzve__lns, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    rcpm__mfj = []
    for evsgq__iqbdl in node.out_vars:
        hqu__dvpg = visit_vars_inner(evsgq__iqbdl, callback, cbdata)
        rcpm__mfj.append(hqu__dvpg)
    node.out_vars = rcpm__mfj
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for kusan__oanid in node.filters:
            for qra__uht in range(len(kusan__oanid)):
                vdnl__xlh = kusan__oanid[qra__uht]
                kusan__oanid[qra__uht] = vdnl__xlh[0], vdnl__xlh[1
                    ], visit_vars_inner(vdnl__xlh[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({vgtvb__ylal.name for vgtvb__ylal in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for odha__flwdg in node.filters:
            for vgtvb__ylal in odha__flwdg:
                if isinstance(vgtvb__ylal[2], ir.Var):
                    use_set.add(vgtvb__ylal[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    xbrgo__utpwq = set(vgtvb__ylal.name for vgtvb__ylal in node.out_vars)
    return set(), xbrgo__utpwq


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    rcpm__mfj = []
    for evsgq__iqbdl in node.out_vars:
        hqu__dvpg = replace_vars_inner(evsgq__iqbdl, var_dict)
        rcpm__mfj.append(hqu__dvpg)
    node.out_vars = rcpm__mfj
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for kusan__oanid in node.filters:
            for qra__uht in range(len(kusan__oanid)):
                vdnl__xlh = kusan__oanid[qra__uht]
                kusan__oanid[qra__uht] = vdnl__xlh[0], vdnl__xlh[1
                    ], replace_vars_inner(vdnl__xlh[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for evsgq__iqbdl in node.out_vars:
        fdg__wavw = definitions[evsgq__iqbdl.name]
        if node not in fdg__wavw:
            fdg__wavw.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        dwf__cwr = [vgtvb__ylal[2] for odha__flwdg in filters for
            vgtvb__ylal in odha__flwdg]
        viqn__rdlp = set()
        for kjs__etdqu in dwf__cwr:
            if isinstance(kjs__etdqu, ir.Var):
                if kjs__etdqu.name not in viqn__rdlp:
                    filter_vars.append(kjs__etdqu)
                viqn__rdlp.add(kjs__etdqu.name)
        return {vgtvb__ylal.name: f'f{qra__uht}' for qra__uht, vgtvb__ylal in
            enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {qra__uht for qra__uht in used_columns if qra__uht < num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    qtup__pldrm = {}
    for qra__uht, lsbup__cpeyt in enumerate(df_type.data):
        if isinstance(lsbup__cpeyt, bodo.IntegerArrayType):
            zaih__tyzxe = lsbup__cpeyt.get_pandas_scalar_type_instance
            if zaih__tyzxe not in qtup__pldrm:
                qtup__pldrm[zaih__tyzxe] = []
            qtup__pldrm[zaih__tyzxe].append(df.columns[qra__uht])
    for vyzve__lns, tview__yjo in qtup__pldrm.items():
        df[tview__yjo] = df[tview__yjo].astype(vyzve__lns)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    azhkm__gxlxw = node.out_vars[0].name
    assert isinstance(typemap[azhkm__gxlxw], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, tmi__wsi, inmg__ezpp = get_live_column_nums_block(
            column_live_map, equiv_vars, azhkm__gxlxw)
        if not (tmi__wsi or inmg__ezpp):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    dcys__xphwz = False
    if array_dists is not None:
        psvpa__cxa = node.out_vars[0].name
        dcys__xphwz = array_dists[psvpa__cxa] in (Distribution.OneD,
            Distribution.OneD_Var)
        zadll__lrojp = node.out_vars[1].name
        assert typemap[zadll__lrojp
            ] == types.none or not dcys__xphwz or array_dists[zadll__lrojp
            ] in (Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return dcys__xphwz


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    htkv__gepqe = 'None'
    zcpuh__edksk = 'None'
    if filters:
        irzkv__sfcyp = []
        qsb__zif = []
        qcgy__ewrjr = False
        orig_colname_map = {bwx__yqmbd: qra__uht for qra__uht, bwx__yqmbd in
            enumerate(col_names)}
        for kusan__oanid in filters:
            ada__bmsy = []
            wrqau__wdc = []
            for vgtvb__ylal in kusan__oanid:
                if isinstance(vgtvb__ylal[2], ir.Var):
                    jzpz__cxdvc, pyhr__zijb = determine_filter_cast(
                        original_out_types, typemap, vgtvb__ylal,
                        orig_colname_map, partition_names, source)
                    if vgtvb__ylal[1] == 'in':
                        hsru__aza = (
                            f"(ds.field('{vgtvb__ylal[0]}').isin({filter_map[vgtvb__ylal[2].name]}))"
                            )
                    else:
                        hsru__aza = (
                            f"(ds.field('{vgtvb__ylal[0]}'){jzpz__cxdvc} {vgtvb__ylal[1]} ds.scalar({filter_map[vgtvb__ylal[2].name]}){pyhr__zijb})"
                            )
                else:
                    assert vgtvb__ylal[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if vgtvb__ylal[1] == 'is not':
                        sjxpu__lctz = '~'
                    else:
                        sjxpu__lctz = ''
                    hsru__aza = (
                        f"({sjxpu__lctz}ds.field('{vgtvb__ylal[0]}').is_null())"
                        )
                wrqau__wdc.append(hsru__aza)
                if not qcgy__ewrjr:
                    if vgtvb__ylal[0] in partition_names and isinstance(
                        vgtvb__ylal[2], ir.Var):
                        if output_dnf:
                            pktx__scs = (
                                f"('{vgtvb__ylal[0]}', '{vgtvb__ylal[1]}', {filter_map[vgtvb__ylal[2].name]})"
                                )
                        else:
                            pktx__scs = hsru__aza
                        ada__bmsy.append(pktx__scs)
                    elif vgtvb__ylal[0] in partition_names and not isinstance(
                        vgtvb__ylal[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            pktx__scs = (
                                f"('{vgtvb__ylal[0]}', '{vgtvb__ylal[1]}', '{vgtvb__ylal[2]}')"
                                )
                        else:
                            pktx__scs = hsru__aza
                        ada__bmsy.append(pktx__scs)
            hhd__vmp = ''
            if ada__bmsy:
                if output_dnf:
                    hhd__vmp = ', '.join(ada__bmsy)
                else:
                    hhd__vmp = ' & '.join(ada__bmsy)
            else:
                qcgy__ewrjr = True
            euh__cpn = ' & '.join(wrqau__wdc)
            if hhd__vmp:
                if output_dnf:
                    irzkv__sfcyp.append(f'[{hhd__vmp}]')
                else:
                    irzkv__sfcyp.append(f'({hhd__vmp})')
            qsb__zif.append(f'({euh__cpn})')
        if output_dnf:
            ylmk__yixlj = ', '.join(irzkv__sfcyp)
        else:
            ylmk__yixlj = ' | '.join(irzkv__sfcyp)
        pwkk__nqra = ' | '.join(qsb__zif)
        if ylmk__yixlj and not qcgy__ewrjr:
            if output_dnf:
                htkv__gepqe = f'[{ylmk__yixlj}]'
            else:
                htkv__gepqe = f'({ylmk__yixlj})'
        zcpuh__edksk = f'({pwkk__nqra})'
    return htkv__gepqe, zcpuh__edksk


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    bmn__pouaw = filter_val[0]
    fszn__dyij = col_types[orig_colname_map[bmn__pouaw]]
    glkf__nprp = bodo.utils.typing.element_type(fszn__dyij)
    if source == 'parquet' and bmn__pouaw in partition_names:
        if glkf__nprp == types.unicode_type:
            mfm__goji = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(glkf__nprp, types.Integer):
            mfm__goji = f'.cast(pyarrow.{glkf__nprp.name}(), safe=False)'
        else:
            mfm__goji = ''
    else:
        mfm__goji = ''
    cle__zsgry = typemap[filter_val[2].name]
    if isinstance(cle__zsgry, (types.List, types.Set)):
        blxg__dtnf = cle__zsgry.dtype
    else:
        blxg__dtnf = cle__zsgry
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(glkf__nprp,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(blxg__dtnf,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([glkf__nprp, blxg__dtnf]):
        if not bodo.utils.typing.is_safe_arrow_cast(glkf__nprp, blxg__dtnf):
            raise BodoError(
                f'Unsupported Arrow cast from {glkf__nprp} to {blxg__dtnf} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if glkf__nprp == types.unicode_type and blxg__dtnf in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif blxg__dtnf == types.unicode_type and glkf__nprp in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(cle__zsgry, (types.List, types.Set)):
                hvseg__htney = 'list' if isinstance(cle__zsgry, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {hvseg__htney} values with isin filter pushdown.'
                    )
            return mfm__goji, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif glkf__nprp == bodo.datetime_date_type and blxg__dtnf in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif blxg__dtnf == bodo.datetime_date_type and glkf__nprp in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return mfm__goji, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return mfm__goji, ''
