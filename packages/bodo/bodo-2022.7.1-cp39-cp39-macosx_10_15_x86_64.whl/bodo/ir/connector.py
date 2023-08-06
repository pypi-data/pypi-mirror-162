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
    unrrg__fkb = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    eaenf__nhy = []
    for mxxt__uum in node.out_vars:
        gifmb__ycd = typemap[mxxt__uum.name]
        if gifmb__ycd == types.none:
            continue
        sptix__ohun = array_analysis._gen_shape_call(equiv_set, mxxt__uum,
            gifmb__ycd.ndim, None, unrrg__fkb)
        equiv_set.insert_equiv(mxxt__uum, sptix__ohun)
        eaenf__nhy.append(sptix__ohun[0])
        equiv_set.define(mxxt__uum, set())
    if len(eaenf__nhy) > 1:
        equiv_set.insert_equiv(*eaenf__nhy)
    return [], unrrg__fkb


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        ettie__lktay = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        ettie__lktay = Distribution.OneD_Var
    else:
        ettie__lktay = Distribution.OneD
    for lzcpp__aggar in node.out_vars:
        if lzcpp__aggar.name in array_dists:
            ettie__lktay = Distribution(min(ettie__lktay.value, array_dists
                [lzcpp__aggar.name].value))
    for lzcpp__aggar in node.out_vars:
        array_dists[lzcpp__aggar.name] = ettie__lktay


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
    for mxxt__uum, gifmb__ycd in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(mxxt__uum.name, gifmb__ycd, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    fzew__nuzb = []
    for mxxt__uum in node.out_vars:
        juacl__pqtqc = visit_vars_inner(mxxt__uum, callback, cbdata)
        fzew__nuzb.append(juacl__pqtqc)
    node.out_vars = fzew__nuzb
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for wopes__xuse in node.filters:
            for ebvhm__juh in range(len(wopes__xuse)):
                nrie__hmbye = wopes__xuse[ebvhm__juh]
                wopes__xuse[ebvhm__juh] = nrie__hmbye[0], nrie__hmbye[1
                    ], visit_vars_inner(nrie__hmbye[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({lzcpp__aggar.name for lzcpp__aggar in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for nnys__ulzmz in node.filters:
            for lzcpp__aggar in nnys__ulzmz:
                if isinstance(lzcpp__aggar[2], ir.Var):
                    use_set.add(lzcpp__aggar[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    zjs__xebvs = set(lzcpp__aggar.name for lzcpp__aggar in node.out_vars)
    return set(), zjs__xebvs


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    fzew__nuzb = []
    for mxxt__uum in node.out_vars:
        juacl__pqtqc = replace_vars_inner(mxxt__uum, var_dict)
        fzew__nuzb.append(juacl__pqtqc)
    node.out_vars = fzew__nuzb
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for wopes__xuse in node.filters:
            for ebvhm__juh in range(len(wopes__xuse)):
                nrie__hmbye = wopes__xuse[ebvhm__juh]
                wopes__xuse[ebvhm__juh] = nrie__hmbye[0], nrie__hmbye[1
                    ], replace_vars_inner(nrie__hmbye[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for mxxt__uum in node.out_vars:
        piuxi__ocsxj = definitions[mxxt__uum.name]
        if node not in piuxi__ocsxj:
            piuxi__ocsxj.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        ach__gxz = [lzcpp__aggar[2] for nnys__ulzmz in filters for
            lzcpp__aggar in nnys__ulzmz]
        hhgw__tlmaj = set()
        for runcf__rmh in ach__gxz:
            if isinstance(runcf__rmh, ir.Var):
                if runcf__rmh.name not in hhgw__tlmaj:
                    filter_vars.append(runcf__rmh)
                hhgw__tlmaj.add(runcf__rmh.name)
        return {lzcpp__aggar.name: f'f{ebvhm__juh}' for ebvhm__juh,
            lzcpp__aggar in enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {ebvhm__juh for ebvhm__juh in used_columns if ebvhm__juh <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    erb__tgpbd = {}
    for ebvhm__juh, alsgz__rxd in enumerate(df_type.data):
        if isinstance(alsgz__rxd, bodo.IntegerArrayType):
            xnen__rad = alsgz__rxd.get_pandas_scalar_type_instance
            if xnen__rad not in erb__tgpbd:
                erb__tgpbd[xnen__rad] = []
            erb__tgpbd[xnen__rad].append(df.columns[ebvhm__juh])
    for gifmb__ycd, swq__nttpc in erb__tgpbd.items():
        df[swq__nttpc] = df[swq__nttpc].astype(gifmb__ycd)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    tmyhf__fqlvq = node.out_vars[0].name
    assert isinstance(typemap[tmyhf__fqlvq], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, driy__kra, zldd__lsfqd = get_live_column_nums_block(
            column_live_map, equiv_vars, tmyhf__fqlvq)
        if not (driy__kra or zldd__lsfqd):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    jwv__lxhdg = False
    if array_dists is not None:
        ocxbz__nrp = node.out_vars[0].name
        jwv__lxhdg = array_dists[ocxbz__nrp] in (Distribution.OneD,
            Distribution.OneD_Var)
        qhfp__owp = node.out_vars[1].name
        assert typemap[qhfp__owp
            ] == types.none or not jwv__lxhdg or array_dists[qhfp__owp] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return jwv__lxhdg


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    zjep__slvil = 'None'
    abvm__kbm = 'None'
    if filters:
        dqwn__ozq = []
        fem__zqrl = []
        xgz__hhyro = False
        orig_colname_map = {rwnz__pfn: ebvhm__juh for ebvhm__juh, rwnz__pfn in
            enumerate(col_names)}
        for wopes__xuse in filters:
            olqi__lvlv = []
            asapo__nydc = []
            for lzcpp__aggar in wopes__xuse:
                if isinstance(lzcpp__aggar[2], ir.Var):
                    fzult__swut, efvy__inrs = determine_filter_cast(
                        original_out_types, typemap, lzcpp__aggar,
                        orig_colname_map, partition_names, source)
                    if lzcpp__aggar[1] == 'in':
                        ugbyt__yojfj = (
                            f"(ds.field('{lzcpp__aggar[0]}').isin({filter_map[lzcpp__aggar[2].name]}))"
                            )
                    else:
                        ugbyt__yojfj = (
                            f"(ds.field('{lzcpp__aggar[0]}'){fzult__swut} {lzcpp__aggar[1]} ds.scalar({filter_map[lzcpp__aggar[2].name]}){efvy__inrs})"
                            )
                else:
                    assert lzcpp__aggar[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if lzcpp__aggar[1] == 'is not':
                        ruas__pxy = '~'
                    else:
                        ruas__pxy = ''
                    ugbyt__yojfj = (
                        f"({ruas__pxy}ds.field('{lzcpp__aggar[0]}').is_null())"
                        )
                asapo__nydc.append(ugbyt__yojfj)
                if not xgz__hhyro:
                    if lzcpp__aggar[0] in partition_names and isinstance(
                        lzcpp__aggar[2], ir.Var):
                        if output_dnf:
                            bcr__loo = (
                                f"('{lzcpp__aggar[0]}', '{lzcpp__aggar[1]}', {filter_map[lzcpp__aggar[2].name]})"
                                )
                        else:
                            bcr__loo = ugbyt__yojfj
                        olqi__lvlv.append(bcr__loo)
                    elif lzcpp__aggar[0] in partition_names and not isinstance(
                        lzcpp__aggar[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            bcr__loo = (
                                f"('{lzcpp__aggar[0]}', '{lzcpp__aggar[1]}', '{lzcpp__aggar[2]}')"
                                )
                        else:
                            bcr__loo = ugbyt__yojfj
                        olqi__lvlv.append(bcr__loo)
            sqpcl__qtlbp = ''
            if olqi__lvlv:
                if output_dnf:
                    sqpcl__qtlbp = ', '.join(olqi__lvlv)
                else:
                    sqpcl__qtlbp = ' & '.join(olqi__lvlv)
            else:
                xgz__hhyro = True
            rise__ffca = ' & '.join(asapo__nydc)
            if sqpcl__qtlbp:
                if output_dnf:
                    dqwn__ozq.append(f'[{sqpcl__qtlbp}]')
                else:
                    dqwn__ozq.append(f'({sqpcl__qtlbp})')
            fem__zqrl.append(f'({rise__ffca})')
        if output_dnf:
            jnid__zxz = ', '.join(dqwn__ozq)
        else:
            jnid__zxz = ' | '.join(dqwn__ozq)
        ilrle__dxoxn = ' | '.join(fem__zqrl)
        if jnid__zxz and not xgz__hhyro:
            if output_dnf:
                zjep__slvil = f'[{jnid__zxz}]'
            else:
                zjep__slvil = f'({jnid__zxz})'
        abvm__kbm = f'({ilrle__dxoxn})'
    return zjep__slvil, abvm__kbm


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    ynlk__gjq = filter_val[0]
    tel__uhxbk = col_types[orig_colname_map[ynlk__gjq]]
    wjzpt__ner = bodo.utils.typing.element_type(tel__uhxbk)
    if source == 'parquet' and ynlk__gjq in partition_names:
        if wjzpt__ner == types.unicode_type:
            twrg__dlal = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(wjzpt__ner, types.Integer):
            twrg__dlal = f'.cast(pyarrow.{wjzpt__ner.name}(), safe=False)'
        else:
            twrg__dlal = ''
    else:
        twrg__dlal = ''
    pnfaw__mifd = typemap[filter_val[2].name]
    if isinstance(pnfaw__mifd, (types.List, types.Set)):
        cbolp__sgzu = pnfaw__mifd.dtype
    else:
        cbolp__sgzu = pnfaw__mifd
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(wjzpt__ner,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(cbolp__sgzu,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([wjzpt__ner, cbolp__sgzu]):
        if not bodo.utils.typing.is_safe_arrow_cast(wjzpt__ner, cbolp__sgzu):
            raise BodoError(
                f'Unsupported Arrow cast from {wjzpt__ner} to {cbolp__sgzu} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if wjzpt__ner == types.unicode_type and cbolp__sgzu in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif cbolp__sgzu == types.unicode_type and wjzpt__ner in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(pnfaw__mifd, (types.List, types.Set)):
                kiofl__bueaj = 'list' if isinstance(pnfaw__mifd, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {kiofl__bueaj} values with isin filter pushdown.'
                    )
            return twrg__dlal, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif wjzpt__ner == bodo.datetime_date_type and cbolp__sgzu in (bodo
            .datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif cbolp__sgzu == bodo.datetime_date_type and wjzpt__ner in (bodo
            .datetime64ns, bodo.pd_timestamp_type):
            return twrg__dlal, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return twrg__dlal, ''
