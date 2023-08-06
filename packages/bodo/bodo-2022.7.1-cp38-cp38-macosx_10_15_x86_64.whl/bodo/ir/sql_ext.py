"""
Implementation of pd.read_sql in BODO.
We piggyback on the pandas implementation. Future plan is to have a faster
version for this task.
"""
from typing import List, Optional
from urllib.parse import urlparse
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.table import Table, TableType
from bodo.io.helpers import PyArrowTableSchemaType, is_nullable
from bodo.io.parquet_pio import ParquetPredicateType
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.distributed_api import bcast, bcast_scalar
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_and_propagate_cpp_exception
MPI_ROOT = 0


class SqlReader(ir.Stmt):

    def __init__(self, sql_request, connection, df_out, df_colnames,
        out_vars, out_types, converted_colnames, db_type, loc,
        unsupported_columns, unsupported_arrow_types, is_select_query,
        index_column_name, index_column_type, database_schema,
        pyarrow_table_schema=None):
        self.connector_typ = 'sql'
        self.sql_request = sql_request
        self.connection = connection
        self.df_out = df_out
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.converted_colnames = converted_colnames
        self.loc = loc
        self.limit = req_limit(sql_request)
        self.db_type = db_type
        self.filters = None
        self.unsupported_columns = unsupported_columns
        self.unsupported_arrow_types = unsupported_arrow_types
        self.is_select_query = is_select_query
        self.index_column_name = index_column_name
        self.index_column_type = index_column_type
        self.out_used_cols = list(range(len(df_colnames)))
        self.database_schema = database_schema
        self.pyarrow_table_schema = pyarrow_table_schema

    def __repr__(self):
        return (
            f'{self.df_out} = ReadSql(sql_request={self.sql_request}, connection={self.connection}, col_names={self.df_colnames}, types={self.out_types}, vars={self.out_vars}, limit={self.limit}, unsupported_columns={self.unsupported_columns}, unsupported_arrow_types={self.unsupported_arrow_types}, is_select_query={self.is_select_query}, index_column_name={self.index_column_name}, index_column_type={self.index_column_type}, out_used_cols={self.out_used_cols}, database_schema={self.database_schema}, pyarrow_table_schema={self.pyarrow_table_schema})'
            )


def parse_dbtype(con_str):
    imnk__dkovk = urlparse(con_str)
    db_type = imnk__dkovk.scheme
    stzus__ydd = imnk__dkovk.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', stzus__ydd
    if db_type == 'mysql+pymysql':
        return 'mysql', stzus__ydd
    if con_str == 'iceberg+glue' or imnk__dkovk.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', stzus__ydd
    return db_type, stzus__ydd


def remove_iceberg_prefix(con):
    import sys
    if sys.version_info.minor < 9:
        if con.startswith('iceberg+'):
            con = con[len('iceberg+'):]
        if con.startswith('iceberg://'):
            con = con[len('iceberg://'):]
    else:
        con = con.removeprefix('iceberg+').removeprefix('iceberg://')
    return con


def remove_dead_sql(sql_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    flyp__jwkkd = sql_node.out_vars[0].name
    osepv__cvb = sql_node.out_vars[1].name
    if flyp__jwkkd not in lives and osepv__cvb not in lives:
        return None
    elif flyp__jwkkd not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif osepv__cvb not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        edt__gnam = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        tfb__yhg = []
        zpkb__owup = []
        for abgg__izls in sql_node.out_used_cols:
            qghb__wqx = sql_node.df_colnames[abgg__izls]
            tfb__yhg.append(qghb__wqx)
            if isinstance(sql_node.out_types[abgg__izls], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                zpkb__owup.append(qghb__wqx)
        if sql_node.index_column_name:
            tfb__yhg.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                zpkb__owup.append(sql_node.index_column_name)
        ylayt__wbguo = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', edt__gnam,
            ylayt__wbguo, tfb__yhg)
        if zpkb__owup:
            rdgv__nde = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', rdgv__nde,
                ylayt__wbguo, zpkb__owup)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        lucoe__szu = set(sql_node.unsupported_columns)
        cwms__gch = set(sql_node.out_used_cols)
        rktus__wnxkd = cwms__gch & lucoe__szu
        if rktus__wnxkd:
            wno__hwta = sorted(rktus__wnxkd)
            ockoo__qjqtp = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            brk__lqz = 0
            for rgd__mtzu in wno__hwta:
                while sql_node.unsupported_columns[brk__lqz] != rgd__mtzu:
                    brk__lqz += 1
                ockoo__qjqtp.append(
                    f"Column '{sql_node.original_df_colnames[rgd__mtzu]}' with unsupported arrow type {sql_node.unsupported_arrow_types[brk__lqz]}"
                    )
                brk__lqz += 1
            nfvpr__shvf = '\n'.join(ockoo__qjqtp)
            raise BodoError(nfvpr__shvf, loc=sql_node.loc)
    kltai__eiwbn, iakx__lqlwk = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    lgwv__zqlz = ', '.join(kltai__eiwbn.values())
    ktg__zdvrw = (
        f'def sql_impl(sql_request, conn, database_schema, {lgwv__zqlz}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        rdin__icv = []
        for xul__kiu in sql_node.filters:
            jev__taphp = []
            for qtek__fodb in xul__kiu:
                zyyc__tpebu = '{' + kltai__eiwbn[qtek__fodb[2].name
                    ] + '}' if isinstance(qtek__fodb[2], ir.Var
                    ) else qtek__fodb[2]
                if qtek__fodb[1] in ('startswith', 'endswith'):
                    dkc__cst = ['(', qtek__fodb[1], '(', qtek__fodb[0], ',',
                        zyyc__tpebu, ')', ')']
                else:
                    dkc__cst = ['(', qtek__fodb[0], qtek__fodb[1],
                        zyyc__tpebu, ')']
                jev__taphp.append(' '.join(dkc__cst))
            rdin__icv.append(' ( ' + ' AND '.join(jev__taphp) + ' ) ')
        ecsx__wdadi = ' WHERE ' + ' OR '.join(rdin__icv)
        for abgg__izls, lpaya__kivj in enumerate(kltai__eiwbn.values()):
            ktg__zdvrw += (
                f'    {lpaya__kivj} = get_sql_literal({lpaya__kivj})\n')
        ktg__zdvrw += f'    sql_request = f"{{sql_request}} {ecsx__wdadi}"\n'
    yvsr__que = ''
    if sql_node.db_type == 'iceberg':
        yvsr__que = lgwv__zqlz
    ktg__zdvrw += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {yvsr__que})
"""
    erei__mduv = {}
    exec(ktg__zdvrw, {}, erei__mduv)
    ogq__tmxjz = erei__mduv['sql_impl']
    mghz__gxasn = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        sql_node.limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    rgxa__inshl = (types.none if sql_node.database_schema is None else
        string_type)
    gff__tgr = compile_to_numba_ir(ogq__tmxjz, {'_sql_reader_py':
        mghz__gxasn, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type,
        rgxa__inshl) + tuple(typemap[ywh__lywbg.name] for ywh__lywbg in
        iakx__lqlwk), typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        txni__kaiv = [sql_node.df_colnames[abgg__izls] for abgg__izls in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            txni__kaiv.append(sql_node.index_column_name)
        mxxxb__thjs = escape_column_names(txni__kaiv, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            jae__opevj = ('SELECT ' + mxxxb__thjs + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            jae__opevj = ('SELECT ' + mxxxb__thjs + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        jae__opevj = sql_node.sql_request
    replace_arg_nodes(gff__tgr, [ir.Const(jae__opevj, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + iakx__lqlwk)
    fsdzc__itw = gff__tgr.body[:-3]
    fsdzc__itw[-2].target = sql_node.out_vars[0]
    fsdzc__itw[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        fsdzc__itw.pop(-1)
    elif not sql_node.out_used_cols:
        fsdzc__itw.pop(-2)
    return fsdzc__itw


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        txni__kaiv = [(xob__qwi.upper() if xob__qwi in converted_colnames else
            xob__qwi) for xob__qwi in col_names]
        mxxxb__thjs = ', '.join([f'"{xob__qwi}"' for xob__qwi in txni__kaiv])
    elif db_type == 'mysql':
        mxxxb__thjs = ', '.join([f'`{xob__qwi}`' for xob__qwi in col_names])
    else:
        mxxxb__thjs = ', '.join([f'"{xob__qwi}"' for xob__qwi in col_names])
    return mxxxb__thjs


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    tns__djfcn = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tns__djfcn,
        'Filter pushdown')
    if tns__djfcn == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(tns__djfcn, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif tns__djfcn == bodo.pd_timestamp_type:

        def impl(filter_value):
            hhp__hdsep = filter_value.nanosecond
            fuph__oaddj = ''
            if hhp__hdsep < 10:
                fuph__oaddj = '00'
            elif hhp__hdsep < 100:
                fuph__oaddj = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{fuph__oaddj}{hhp__hdsep}'"
                )
        return impl
    elif tns__djfcn == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {tns__djfcn} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    cet__zht = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    tns__djfcn = types.unliteral(filter_value)
    if isinstance(tns__djfcn, types.List) and (isinstance(tns__djfcn.dtype,
        scalar_isinstance) or tns__djfcn.dtype in cet__zht):

        def impl(filter_value):
            zhoni__bwz = ', '.join([_get_snowflake_sql_literal_scalar(
                xob__qwi) for xob__qwi in filter_value])
            return f'({zhoni__bwz})'
        return impl
    elif isinstance(tns__djfcn, scalar_isinstance) or tns__djfcn in cet__zht:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {tns__djfcn} used in filter pushdown.'
            )


def sql_remove_dead_column(sql_node, column_live_map, equiv_vars, typemap):
    return bodo.ir.connector.base_connector_remove_dead_columns(sql_node,
        column_live_map, equiv_vars, typemap, 'SQLReader', sql_node.df_colnames
        )


numba.parfors.array_analysis.array_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[SqlReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[SqlReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[SqlReader] = remove_dead_sql
numba.core.analysis.ir_extension_usedefs[SqlReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[SqlReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[SqlReader] = sql_distributed_run
remove_dead_column_extensions[SqlReader] = sql_remove_dead_column
ir_extension_table_column_use[SqlReader
    ] = bodo.ir.connector.connector_table_column_use
compiled_funcs = []


@numba.njit
def sqlalchemy_check():
    with numba.objmode():
        sqlalchemy_check_()


def sqlalchemy_check_():
    try:
        import sqlalchemy
    except ImportError as qzo__thxs:
        ekgm__svog = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(ekgm__svog)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as qzo__thxs:
        ekgm__svog = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(ekgm__svog)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as qzo__thxs:
        ekgm__svog = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(ekgm__svog)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as qzo__thxs:
        ekgm__svog = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(ekgm__svog)


def req_limit(sql_request):
    import re
    pta__qwjj = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    lzn__fapzw = pta__qwjj.search(sql_request)
    if lzn__fapzw:
        return int(lzn__fapzw.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    cdc__wmzq = next_label()
    txni__kaiv = [col_names[abgg__izls] for abgg__izls in out_used_cols]
    scasm__egmsz = [col_typs[abgg__izls] for abgg__izls in out_used_cols]
    if index_column_name:
        txni__kaiv.append(index_column_name)
        scasm__egmsz.append(index_column_type)
    zsq__dshp = None
    dpr__pbnsz = None
    bqboi__sry = TableType(tuple(col_typs)) if out_used_cols else types.none
    yvsr__que = ''
    kltai__eiwbn = {}
    iakx__lqlwk = []
    if filters and db_type == 'iceberg':
        kltai__eiwbn, iakx__lqlwk = bodo.ir.connector.generate_filter_map(
            filters)
        yvsr__que = ', '.join(kltai__eiwbn.values())
    ktg__zdvrw = (
        f'def sql_reader_py(sql_request, conn, database_schema, {yvsr__que}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        ilspx__ukj, znf__dqvcd = bodo.ir.connector.generate_arrow_filters(
            filters, kltai__eiwbn, iakx__lqlwk, col_names, col_names,
            col_typs, typemap, 'iceberg')
        iqriy__vsqxv: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[abgg__izls]) for abgg__izls in out_used_cols]
        zwodu__hqxsd = {nznlm__oyjnk: abgg__izls for abgg__izls,
            nznlm__oyjnk in enumerate(iqriy__vsqxv)}
        uvl__meser = [int(is_nullable(col_typs[abgg__izls])) for abgg__izls in
            iqriy__vsqxv]
        fjddk__nfe = ',' if yvsr__que else ''
        ktg__zdvrw += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        ktg__zdvrw += f"""  dnf_filters, expr_filters = get_filters_pyobject("{ilspx__ukj}", "{znf__dqvcd}", ({yvsr__que}{fjddk__nfe}))
"""
        ktg__zdvrw += f'  out_table = iceberg_read(\n'
        ktg__zdvrw += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        ktg__zdvrw += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        ktg__zdvrw += (
            f'    expr_filters, selected_cols_arr_{cdc__wmzq}.ctypes,\n')
        ktg__zdvrw += (
            f'    {len(iqriy__vsqxv)}, nullable_cols_arr_{cdc__wmzq}.ctypes,\n'
            )
        ktg__zdvrw += f'    pyarrow_table_schema_{cdc__wmzq},\n'
        ktg__zdvrw += f'  )\n'
        ktg__zdvrw += f'  check_and_propagate_cpp_exception()\n'
        zhvj__utmkg = not out_used_cols
        bqboi__sry = TableType(tuple(col_typs))
        if zhvj__utmkg:
            bqboi__sry = types.none
        osepv__cvb = 'None'
        if index_column_name is not None:
            xaqcv__msuj = len(out_used_cols) + 1 if not zhvj__utmkg else 0
            osepv__cvb = (
                f'info_to_array(info_from_table(out_table, {xaqcv__msuj}), index_col_typ)'
                )
        ktg__zdvrw += f'  index_var = {osepv__cvb}\n'
        zsq__dshp = None
        if not zhvj__utmkg:
            zsq__dshp = []
            flvky__eox = 0
            for abgg__izls in range(len(col_names)):
                if flvky__eox < len(out_used_cols
                    ) and abgg__izls == out_used_cols[flvky__eox]:
                    zsq__dshp.append(zwodu__hqxsd[abgg__izls])
                    flvky__eox += 1
                else:
                    zsq__dshp.append(-1)
            zsq__dshp = np.array(zsq__dshp, dtype=np.int64)
        if zhvj__utmkg:
            ktg__zdvrw += '  table_var = None\n'
        else:
            ktg__zdvrw += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{cdc__wmzq}, py_table_type_{cdc__wmzq})
"""
        ktg__zdvrw += f'  delete_table(out_table)\n'
        ktg__zdvrw += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        ktg__zdvrw += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        uvl__meser = [int(is_nullable(col_typs[abgg__izls])) for abgg__izls in
            out_used_cols]
        if index_column_name:
            uvl__meser.append(int(is_nullable(index_column_type)))
        ktg__zdvrw += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(uvl__meser)}, np.array({uvl__meser}, dtype=np.int32).ctypes)
"""
        ktg__zdvrw += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            ktg__zdvrw += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            ktg__zdvrw += '  index_var = None\n'
        if out_used_cols:
            brk__lqz = []
            flvky__eox = 0
            for abgg__izls in range(len(col_names)):
                if flvky__eox < len(out_used_cols
                    ) and abgg__izls == out_used_cols[flvky__eox]:
                    brk__lqz.append(flvky__eox)
                    flvky__eox += 1
                else:
                    brk__lqz.append(-1)
            zsq__dshp = np.array(brk__lqz, dtype=np.int64)
            ktg__zdvrw += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{cdc__wmzq}, py_table_type_{cdc__wmzq})
"""
        else:
            ktg__zdvrw += '  table_var = None\n'
        ktg__zdvrw += '  delete_table(out_table)\n'
        ktg__zdvrw += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            ktg__zdvrw += f"""  type_usecols_offsets_arr_{cdc__wmzq}_2 = type_usecols_offsets_arr_{cdc__wmzq}
"""
            dpr__pbnsz = np.array(out_used_cols, dtype=np.int64)
        ktg__zdvrw += '  df_typeref_2 = df_typeref\n'
        ktg__zdvrw += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            ktg__zdvrw += '  pymysql_check()\n'
        elif db_type == 'oracle':
            ktg__zdvrw += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            ktg__zdvrw += '  psycopg2_check()\n'
        if parallel:
            ktg__zdvrw += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                ktg__zdvrw += f'  nb_row = {limit}\n'
            else:
                ktg__zdvrw += '  with objmode(nb_row="int64"):\n'
                ktg__zdvrw += f'     if rank == {MPI_ROOT}:\n'
                ktg__zdvrw += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                ktg__zdvrw += '         frame = pd.read_sql(sql_cons, conn)\n'
                ktg__zdvrw += '         nb_row = frame.iat[0,0]\n'
                ktg__zdvrw += '     else:\n'
                ktg__zdvrw += '         nb_row = 0\n'
                ktg__zdvrw += '  nb_row = bcast_scalar(nb_row)\n'
            ktg__zdvrw += f"""  with objmode(table_var=py_table_type_{cdc__wmzq}, index_var=index_col_typ):
"""
            ktg__zdvrw += (
                '    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)\n'
                )
            if db_type == 'oracle':
                ktg__zdvrw += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                ktg__zdvrw += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            ktg__zdvrw += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            ktg__zdvrw += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            ktg__zdvrw += f"""  with objmode(table_var=py_table_type_{cdc__wmzq}, index_var=index_col_typ):
"""
            ktg__zdvrw += '    df_ret = pd.read_sql(sql_request, conn)\n'
            ktg__zdvrw += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            ktg__zdvrw += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            ktg__zdvrw += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            ktg__zdvrw += '    index_var = None\n'
        if out_used_cols:
            ktg__zdvrw += f'    arrs = []\n'
            ktg__zdvrw += f'    for i in range(df_ret.shape[1]):\n'
            ktg__zdvrw += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            ktg__zdvrw += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{cdc__wmzq}_2, {len(col_names)})
"""
        else:
            ktg__zdvrw += '    table_var = None\n'
    ktg__zdvrw += '  return (table_var, index_var)\n'
    sotk__etrl = globals()
    sotk__etrl.update({'bodo': bodo, f'py_table_type_{cdc__wmzq}':
        bqboi__sry, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        sotk__etrl.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{cdc__wmzq}': zsq__dshp})
    if db_type == 'iceberg':
        sotk__etrl.update({f'selected_cols_arr_{cdc__wmzq}': np.array(
            iqriy__vsqxv, np.int32), f'nullable_cols_arr_{cdc__wmzq}': np.
            array(uvl__meser, np.int32), f'py_table_type_{cdc__wmzq}':
            bqboi__sry, f'pyarrow_table_schema_{cdc__wmzq}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        sotk__etrl.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        sotk__etrl.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(scasm__egmsz), bodo.RangeIndexType(
            None), tuple(txni__kaiv)), 'Table': Table,
            f'type_usecols_offsets_arr_{cdc__wmzq}': dpr__pbnsz})
    erei__mduv = {}
    exec(ktg__zdvrw, sotk__etrl, erei__mduv)
    mghz__gxasn = erei__mduv['sql_reader_py']
    pom__hbtpi = numba.njit(mghz__gxasn)
    compiled_funcs.append(pom__hbtpi)
    return pom__hbtpi


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
parquet_predicate_type = ParquetPredicateType()
pyarrow_table_schema_type = PyArrowTableSchemaType()
_iceberg_read = types.ExternalFunction('iceberg_pq_read', table_type(types.
    voidptr, types.voidptr, types.voidptr, types.boolean,
    parquet_predicate_type, parquet_predicate_type, types.voidptr, types.
    int32, types.voidptr, pyarrow_table_schema_type))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
ll.add_symbol('iceberg_pq_read', arrow_cpp.iceberg_pq_read)
