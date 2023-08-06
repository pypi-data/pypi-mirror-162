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
    kofjb__hbj = urlparse(con_str)
    db_type = kofjb__hbj.scheme
    jcq__vbti = kofjb__hbj.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', jcq__vbti
    if db_type == 'mysql+pymysql':
        return 'mysql', jcq__vbti
    if con_str == 'iceberg+glue' or kofjb__hbj.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', jcq__vbti
    return db_type, jcq__vbti


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
    icq__woi = sql_node.out_vars[0].name
    crz__ajuy = sql_node.out_vars[1].name
    if icq__woi not in lives and crz__ajuy not in lives:
        return None
    elif icq__woi not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif crz__ajuy not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx, meta_head_only_info=None):
    if bodo.user_logging.get_verbose_level() >= 1:
        zhimt__dcowh = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        bdgge__hqbz = []
        kigqa__bifpx = []
        for sogac__ijb in sql_node.out_used_cols:
            vekn__hnvm = sql_node.df_colnames[sogac__ijb]
            bdgge__hqbz.append(vekn__hnvm)
            if isinstance(sql_node.out_types[sogac__ijb], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                kigqa__bifpx.append(vekn__hnvm)
        if sql_node.index_column_name:
            bdgge__hqbz.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                kigqa__bifpx.append(sql_node.index_column_name)
        ceaz__xvopg = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', zhimt__dcowh,
            ceaz__xvopg, bdgge__hqbz)
        if kigqa__bifpx:
            xpta__zxh = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', xpta__zxh,
                ceaz__xvopg, kigqa__bifpx)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        mctc__ftyml = set(sql_node.unsupported_columns)
        bfml__zzepn = set(sql_node.out_used_cols)
        bvvdi__tep = bfml__zzepn & mctc__ftyml
        if bvvdi__tep:
            aokci__cqdi = sorted(bvvdi__tep)
            jbya__hsbr = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            ehdz__gphe = 0
            for fal__unc in aokci__cqdi:
                while sql_node.unsupported_columns[ehdz__gphe] != fal__unc:
                    ehdz__gphe += 1
                jbya__hsbr.append(
                    f"Column '{sql_node.original_df_colnames[fal__unc]}' with unsupported arrow type {sql_node.unsupported_arrow_types[ehdz__gphe]}"
                    )
                ehdz__gphe += 1
            rbc__ahh = '\n'.join(jbya__hsbr)
            raise BodoError(rbc__ahh, loc=sql_node.loc)
    tdq__zdcvd, swhx__txhrs = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    twt__ekpw = ', '.join(tdq__zdcvd.values())
    xdq__hcwks = (
        f'def sql_impl(sql_request, conn, database_schema, {twt__ekpw}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        shgis__rkdav = []
        for bbzr__zpip in sql_node.filters:
            zyuf__zlubh = []
            for abm__tbxrw in bbzr__zpip:
                oldt__djm = '{' + tdq__zdcvd[abm__tbxrw[2].name
                    ] + '}' if isinstance(abm__tbxrw[2], ir.Var
                    ) else abm__tbxrw[2]
                if abm__tbxrw[1] in ('startswith', 'endswith'):
                    pqm__mgm = ['(', abm__tbxrw[1], '(', abm__tbxrw[0], ',',
                        oldt__djm, ')', ')']
                else:
                    pqm__mgm = ['(', abm__tbxrw[0], abm__tbxrw[1],
                        oldt__djm, ')']
                zyuf__zlubh.append(' '.join(pqm__mgm))
            shgis__rkdav.append(' ( ' + ' AND '.join(zyuf__zlubh) + ' ) ')
        vta__hmj = ' WHERE ' + ' OR '.join(shgis__rkdav)
        for sogac__ijb, jgoq__vbax in enumerate(tdq__zdcvd.values()):
            xdq__hcwks += f'    {jgoq__vbax} = get_sql_literal({jgoq__vbax})\n'
        xdq__hcwks += f'    sql_request = f"{{sql_request}} {vta__hmj}"\n'
    hsxuj__cxlfw = ''
    if sql_node.db_type == 'iceberg':
        hsxuj__cxlfw = twt__ekpw
    xdq__hcwks += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {hsxuj__cxlfw})
"""
    ztt__doqkt = {}
    exec(xdq__hcwks, {}, ztt__doqkt)
    oqy__sff = ztt__doqkt['sql_impl']
    if sql_node.limit is not None:
        limit = sql_node.limit
    elif meta_head_only_info and meta_head_only_info[0] is not None:
        limit = meta_head_only_info[0]
    else:
        limit = None
    suhv__qknyv = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    cague__hqhdj = (types.none if sql_node.database_schema is None else
        string_type)
    ifow__fjlq = compile_to_numba_ir(oqy__sff, {'_sql_reader_py':
        suhv__qknyv, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type,
        cague__hqhdj) + tuple(typemap[hnedu__bmyb.name] for hnedu__bmyb in
        swhx__txhrs), typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        qxjrr__okju = [sql_node.df_colnames[sogac__ijb] for sogac__ijb in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            qxjrr__okju.append(sql_node.index_column_name)
        bnrf__fkez = escape_column_names(qxjrr__okju, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            rho__gkji = ('SELECT ' + bnrf__fkez + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            rho__gkji = ('SELECT ' + bnrf__fkez + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        rho__gkji = sql_node.sql_request
    replace_arg_nodes(ifow__fjlq, [ir.Const(rho__gkji, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + swhx__txhrs)
    luz__kpja = ifow__fjlq.body[:-3]
    luz__kpja[-2].target = sql_node.out_vars[0]
    luz__kpja[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        luz__kpja.pop(-1)
    elif not sql_node.out_used_cols:
        luz__kpja.pop(-2)
    return luz__kpja


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        qxjrr__okju = [(suooz__qbx.upper() if suooz__qbx in
            converted_colnames else suooz__qbx) for suooz__qbx in col_names]
        bnrf__fkez = ', '.join([f'"{suooz__qbx}"' for suooz__qbx in
            qxjrr__okju])
    elif db_type == 'mysql':
        bnrf__fkez = ', '.join([f'`{suooz__qbx}`' for suooz__qbx in col_names])
    else:
        bnrf__fkez = ', '.join([f'"{suooz__qbx}"' for suooz__qbx in col_names])
    return bnrf__fkez


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    gcph__qtbn = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(gcph__qtbn,
        'Filter pushdown')
    if gcph__qtbn == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(gcph__qtbn, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif gcph__qtbn == bodo.pd_timestamp_type:

        def impl(filter_value):
            cxtpw__fuaen = filter_value.nanosecond
            zpbc__wejt = ''
            if cxtpw__fuaen < 10:
                zpbc__wejt = '00'
            elif cxtpw__fuaen < 100:
                zpbc__wejt = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{zpbc__wejt}{cxtpw__fuaen}'"
                )
        return impl
    elif gcph__qtbn == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {gcph__qtbn} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    smnvm__exgx = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    gcph__qtbn = types.unliteral(filter_value)
    if isinstance(gcph__qtbn, types.List) and (isinstance(gcph__qtbn.dtype,
        scalar_isinstance) or gcph__qtbn.dtype in smnvm__exgx):

        def impl(filter_value):
            sjko__yuer = ', '.join([_get_snowflake_sql_literal_scalar(
                suooz__qbx) for suooz__qbx in filter_value])
            return f'({sjko__yuer})'
        return impl
    elif isinstance(gcph__qtbn, scalar_isinstance
        ) or gcph__qtbn in smnvm__exgx:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {gcph__qtbn} used in filter pushdown.'
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
    except ImportError as hjwzo__diiaq:
        jflsq__rvmrq = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(jflsq__rvmrq)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as hjwzo__diiaq:
        jflsq__rvmrq = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(jflsq__rvmrq)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as hjwzo__diiaq:
        jflsq__rvmrq = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(jflsq__rvmrq)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as hjwzo__diiaq:
        jflsq__rvmrq = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(jflsq__rvmrq)


def req_limit(sql_request):
    import re
    zzti__mqww = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    oimb__hhl = zzti__mqww.search(sql_request)
    if oimb__hhl:
        return int(oimb__hhl.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type: str, limit: Optional[int], parallel, typemap, filters,
    pyarrow_table_schema: 'Optional[pyarrow.Schema]'):
    zotl__urxv = next_label()
    qxjrr__okju = [col_names[sogac__ijb] for sogac__ijb in out_used_cols]
    ptlqm__ban = [col_typs[sogac__ijb] for sogac__ijb in out_used_cols]
    if index_column_name:
        qxjrr__okju.append(index_column_name)
        ptlqm__ban.append(index_column_type)
    iid__clkk = None
    dfdoz__xzc = None
    qcfkt__gejjv = TableType(tuple(col_typs)) if out_used_cols else types.none
    hsxuj__cxlfw = ''
    tdq__zdcvd = {}
    swhx__txhrs = []
    if filters and db_type == 'iceberg':
        tdq__zdcvd, swhx__txhrs = bodo.ir.connector.generate_filter_map(filters
            )
        hsxuj__cxlfw = ', '.join(tdq__zdcvd.values())
    xdq__hcwks = (
        f'def sql_reader_py(sql_request, conn, database_schema, {hsxuj__cxlfw}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        vhr__whs, tbhl__qpzl = bodo.ir.connector.generate_arrow_filters(filters
            , tdq__zdcvd, swhx__txhrs, col_names, col_names, col_typs,
            typemap, 'iceberg')
        zmcgy__myytq: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[sogac__ijb]) for sogac__ijb in out_used_cols]
        zrz__nao = {pdia__xyk: sogac__ijb for sogac__ijb, pdia__xyk in
            enumerate(zmcgy__myytq)}
        shv__ggjvy = [int(is_nullable(col_typs[sogac__ijb])) for sogac__ijb in
            zmcgy__myytq]
        zbhkh__nwwk = ',' if hsxuj__cxlfw else ''
        xdq__hcwks += f"""  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})
  dnf_filters, expr_filters = get_filters_pyobject("{vhr__whs}", "{tbhl__qpzl}", ({hsxuj__cxlfw}{zbhkh__nwwk}))
  out_table = iceberg_read(
    unicode_to_utf8(conn),
    unicode_to_utf8(database_schema),
    unicode_to_utf8(sql_request),
    {parallel},
    {-1 if limit is None else limit},
    dnf_filters,
    expr_filters,
    selected_cols_arr_{zotl__urxv}.ctypes,
    {len(zmcgy__myytq)},
    nullable_cols_arr_{zotl__urxv}.ctypes,
    pyarrow_table_schema_{zotl__urxv},
  )
  check_and_propagate_cpp_exception()
"""
        rqo__fyl = not out_used_cols
        qcfkt__gejjv = TableType(tuple(col_typs))
        if rqo__fyl:
            qcfkt__gejjv = types.none
        crz__ajuy = 'None'
        if index_column_name is not None:
            yhp__ndqcy = len(out_used_cols) + 1 if not rqo__fyl else 0
            crz__ajuy = (
                f'info_to_array(info_from_table(out_table, {yhp__ndqcy}), index_col_typ)'
                )
        xdq__hcwks += f'  index_var = {crz__ajuy}\n'
        iid__clkk = None
        if not rqo__fyl:
            iid__clkk = []
            steuy__nuxor = 0
            for sogac__ijb in range(len(col_names)):
                if steuy__nuxor < len(out_used_cols
                    ) and sogac__ijb == out_used_cols[steuy__nuxor]:
                    iid__clkk.append(zrz__nao[sogac__ijb])
                    steuy__nuxor += 1
                else:
                    iid__clkk.append(-1)
            iid__clkk = np.array(iid__clkk, dtype=np.int64)
        if rqo__fyl:
            xdq__hcwks += '  table_var = None\n'
        else:
            xdq__hcwks += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{zotl__urxv}, py_table_type_{zotl__urxv})
"""
        xdq__hcwks += f'  delete_table(out_table)\n'
        xdq__hcwks += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        xdq__hcwks += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        shv__ggjvy = [int(is_nullable(col_typs[sogac__ijb])) for sogac__ijb in
            out_used_cols]
        if index_column_name:
            shv__ggjvy.append(int(is_nullable(index_column_type)))
        xdq__hcwks += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(shv__ggjvy)}, np.array({shv__ggjvy}, dtype=np.int32).ctypes)
"""
        xdq__hcwks += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            xdq__hcwks += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            xdq__hcwks += '  index_var = None\n'
        if out_used_cols:
            ehdz__gphe = []
            steuy__nuxor = 0
            for sogac__ijb in range(len(col_names)):
                if steuy__nuxor < len(out_used_cols
                    ) and sogac__ijb == out_used_cols[steuy__nuxor]:
                    ehdz__gphe.append(steuy__nuxor)
                    steuy__nuxor += 1
                else:
                    ehdz__gphe.append(-1)
            iid__clkk = np.array(ehdz__gphe, dtype=np.int64)
            xdq__hcwks += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{zotl__urxv}, py_table_type_{zotl__urxv})
"""
        else:
            xdq__hcwks += '  table_var = None\n'
        xdq__hcwks += '  delete_table(out_table)\n'
        xdq__hcwks += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            xdq__hcwks += f"""  type_usecols_offsets_arr_{zotl__urxv}_2 = type_usecols_offsets_arr_{zotl__urxv}
"""
            dfdoz__xzc = np.array(out_used_cols, dtype=np.int64)
        xdq__hcwks += '  df_typeref_2 = df_typeref\n'
        xdq__hcwks += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            xdq__hcwks += '  pymysql_check()\n'
        elif db_type == 'oracle':
            xdq__hcwks += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            xdq__hcwks += '  psycopg2_check()\n'
        if parallel:
            xdq__hcwks += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                xdq__hcwks += f'  nb_row = {limit}\n'
            else:
                xdq__hcwks += '  with objmode(nb_row="int64"):\n'
                xdq__hcwks += f'     if rank == {MPI_ROOT}:\n'
                xdq__hcwks += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                xdq__hcwks += '         frame = pd.read_sql(sql_cons, conn)\n'
                xdq__hcwks += '         nb_row = frame.iat[0,0]\n'
                xdq__hcwks += '     else:\n'
                xdq__hcwks += '         nb_row = 0\n'
                xdq__hcwks += '  nb_row = bcast_scalar(nb_row)\n'
            xdq__hcwks += f"""  with objmode(table_var=py_table_type_{zotl__urxv}, index_var=index_col_typ):
"""
            xdq__hcwks += (
                '    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)\n'
                )
            if db_type == 'oracle':
                xdq__hcwks += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                xdq__hcwks += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            xdq__hcwks += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            xdq__hcwks += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            xdq__hcwks += f"""  with objmode(table_var=py_table_type_{zotl__urxv}, index_var=index_col_typ):
"""
            xdq__hcwks += '    df_ret = pd.read_sql(sql_request, conn)\n'
            xdq__hcwks += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            xdq__hcwks += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            xdq__hcwks += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            xdq__hcwks += '    index_var = None\n'
        if out_used_cols:
            xdq__hcwks += f'    arrs = []\n'
            xdq__hcwks += f'    for i in range(df_ret.shape[1]):\n'
            xdq__hcwks += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            xdq__hcwks += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{zotl__urxv}_2, {len(col_names)})
"""
        else:
            xdq__hcwks += '    table_var = None\n'
    xdq__hcwks += '  return (table_var, index_var)\n'
    gsij__ffqz = globals()
    gsij__ffqz.update({'bodo': bodo, f'py_table_type_{zotl__urxv}':
        qcfkt__gejjv, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        gsij__ffqz.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{zotl__urxv}': iid__clkk})
    if db_type == 'iceberg':
        gsij__ffqz.update({f'selected_cols_arr_{zotl__urxv}': np.array(
            zmcgy__myytq, np.int32), f'nullable_cols_arr_{zotl__urxv}': np.
            array(shv__ggjvy, np.int32), f'py_table_type_{zotl__urxv}':
            qcfkt__gejjv, f'pyarrow_table_schema_{zotl__urxv}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        gsij__ffqz.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        gsij__ffqz.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(ptlqm__ban), bodo.RangeIndexType(None),
            tuple(qxjrr__okju)), 'Table': Table,
            f'type_usecols_offsets_arr_{zotl__urxv}': dfdoz__xzc})
    ztt__doqkt = {}
    exec(xdq__hcwks, gsij__ffqz, ztt__doqkt)
    suhv__qknyv = ztt__doqkt['sql_reader_py']
    dpskx__kondx = numba.njit(suhv__qknyv)
    compiled_funcs.append(dpskx__kondx)
    return dpskx__kondx


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
parquet_predicate_type = ParquetPredicateType()
pyarrow_table_schema_type = PyArrowTableSchemaType()
_iceberg_read = types.ExternalFunction('iceberg_pq_read', table_type(types.
    voidptr, types.voidptr, types.voidptr, types.boolean, types.int32,
    parquet_predicate_type, parquet_predicate_type, types.voidptr, types.
    int32, types.voidptr, pyarrow_table_schema_type))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
ll.add_symbol('iceberg_pq_read', arrow_cpp.iceberg_pq_read)
