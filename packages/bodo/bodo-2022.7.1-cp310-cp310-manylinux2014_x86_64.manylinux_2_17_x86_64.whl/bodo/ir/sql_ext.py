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
    mdjp__uhx = urlparse(con_str)
    db_type = mdjp__uhx.scheme
    dksjf__iwr = mdjp__uhx.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', dksjf__iwr
    if db_type == 'mysql+pymysql':
        return 'mysql', dksjf__iwr
    if con_str == 'iceberg+glue' or mdjp__uhx.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', dksjf__iwr
    return db_type, dksjf__iwr


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
    naa__pnpro = sql_node.out_vars[0].name
    zpg__cqorv = sql_node.out_vars[1].name
    if naa__pnpro not in lives and zpg__cqorv not in lives:
        return None
    elif naa__pnpro not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif zpg__cqorv not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        hgar__hvec = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        ydtdz__fzcr = []
        ebc__fws = []
        for bka__cpr in sql_node.out_used_cols:
            yxl__czbrx = sql_node.df_colnames[bka__cpr]
            ydtdz__fzcr.append(yxl__czbrx)
            if isinstance(sql_node.out_types[bka__cpr], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                ebc__fws.append(yxl__czbrx)
        if sql_node.index_column_name:
            ydtdz__fzcr.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                ebc__fws.append(sql_node.index_column_name)
        fidbr__xszr = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', hgar__hvec,
            fidbr__xszr, ydtdz__fzcr)
        if ebc__fws:
            amdoo__qzti = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                amdoo__qzti, fidbr__xszr, ebc__fws)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        qjed__jcu = set(sql_node.unsupported_columns)
        omrgl__eit = set(sql_node.out_used_cols)
        dnst__chas = omrgl__eit & qjed__jcu
        if dnst__chas:
            fsvof__bgf = sorted(dnst__chas)
            hvfc__mnex = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            dub__iou = 0
            for bxlln__mkwp in fsvof__bgf:
                while sql_node.unsupported_columns[dub__iou] != bxlln__mkwp:
                    dub__iou += 1
                hvfc__mnex.append(
                    f"Column '{sql_node.original_df_colnames[bxlln__mkwp]}' with unsupported arrow type {sql_node.unsupported_arrow_types[dub__iou]}"
                    )
                dub__iou += 1
            ssq__cuxhc = '\n'.join(hvfc__mnex)
            raise BodoError(ssq__cuxhc, loc=sql_node.loc)
    gorih__tme, sdhl__zpvi = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    kydh__hgagh = ', '.join(gorih__tme.values())
    stxo__lofz = (
        f'def sql_impl(sql_request, conn, database_schema, {kydh__hgagh}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        ixpz__felrz = []
        for benga__ygf in sql_node.filters:
            doiya__qeon = []
            for lfh__vavf in benga__ygf:
                yesxz__kii = '{' + gorih__tme[lfh__vavf[2].name
                    ] + '}' if isinstance(lfh__vavf[2], ir.Var) else lfh__vavf[
                    2]
                if lfh__vavf[1] in ('startswith', 'endswith'):
                    proo__fjpn = ['(', lfh__vavf[1], '(', lfh__vavf[0], ',',
                        yesxz__kii, ')', ')']
                else:
                    proo__fjpn = ['(', lfh__vavf[0], lfh__vavf[1],
                        yesxz__kii, ')']
                doiya__qeon.append(' '.join(proo__fjpn))
            ixpz__felrz.append(' ( ' + ' AND '.join(doiya__qeon) + ' ) ')
        gbbhf__wcgzb = ' WHERE ' + ' OR '.join(ixpz__felrz)
        for bka__cpr, tsaiv__axr in enumerate(gorih__tme.values()):
            stxo__lofz += f'    {tsaiv__axr} = get_sql_literal({tsaiv__axr})\n'
        stxo__lofz += f'    sql_request = f"{{sql_request}} {gbbhf__wcgzb}"\n'
    qqv__clivy = ''
    if sql_node.db_type == 'iceberg':
        qqv__clivy = kydh__hgagh
    stxo__lofz += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {qqv__clivy})
"""
    kzwk__pibej = {}
    exec(stxo__lofz, {}, kzwk__pibej)
    kiufz__ewmva = kzwk__pibej['sql_impl']
    riqv__ajmor = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        sql_node.limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    pclmy__aqk = (types.none if sql_node.database_schema is None else
        string_type)
    ghhl__nxsap = compile_to_numba_ir(kiufz__ewmva, {'_sql_reader_py':
        riqv__ajmor, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, pclmy__aqk
        ) + tuple(typemap[twdel__fqd.name] for twdel__fqd in sdhl__zpvi),
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        amia__usf = [sql_node.df_colnames[bka__cpr] for bka__cpr in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            amia__usf.append(sql_node.index_column_name)
        oqmh__smjql = escape_column_names(amia__usf, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            ilv__dob = ('SELECT ' + oqmh__smjql + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            ilv__dob = ('SELECT ' + oqmh__smjql + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        ilv__dob = sql_node.sql_request
    replace_arg_nodes(ghhl__nxsap, [ir.Const(ilv__dob, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + sdhl__zpvi)
    kiv__uzjc = ghhl__nxsap.body[:-3]
    kiv__uzjc[-2].target = sql_node.out_vars[0]
    kiv__uzjc[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        kiv__uzjc.pop(-1)
    elif not sql_node.out_used_cols:
        kiv__uzjc.pop(-2)
    return kiv__uzjc


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        amia__usf = [(rgk__flywo.upper() if rgk__flywo in
            converted_colnames else rgk__flywo) for rgk__flywo in col_names]
        oqmh__smjql = ', '.join([f'"{rgk__flywo}"' for rgk__flywo in amia__usf]
            )
    elif db_type == 'mysql':
        oqmh__smjql = ', '.join([f'`{rgk__flywo}`' for rgk__flywo in col_names]
            )
    else:
        oqmh__smjql = ', '.join([f'"{rgk__flywo}"' for rgk__flywo in col_names]
            )
    return oqmh__smjql


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    zgeav__ssn = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(zgeav__ssn,
        'Filter pushdown')
    if zgeav__ssn == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(zgeav__ssn, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif zgeav__ssn == bodo.pd_timestamp_type:

        def impl(filter_value):
            nfgxj__kbs = filter_value.nanosecond
            yuda__mdcne = ''
            if nfgxj__kbs < 10:
                yuda__mdcne = '00'
            elif nfgxj__kbs < 100:
                yuda__mdcne = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{yuda__mdcne}{nfgxj__kbs}'"
                )
        return impl
    elif zgeav__ssn == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {zgeav__ssn} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    ofuq__uhin = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    zgeav__ssn = types.unliteral(filter_value)
    if isinstance(zgeav__ssn, types.List) and (isinstance(zgeav__ssn.dtype,
        scalar_isinstance) or zgeav__ssn.dtype in ofuq__uhin):

        def impl(filter_value):
            jri__snmiz = ', '.join([_get_snowflake_sql_literal_scalar(
                rgk__flywo) for rgk__flywo in filter_value])
            return f'({jri__snmiz})'
        return impl
    elif isinstance(zgeav__ssn, scalar_isinstance) or zgeav__ssn in ofuq__uhin:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {zgeav__ssn} used in filter pushdown.'
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
    except ImportError as rezi__baoc:
        cfr__lmti = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(cfr__lmti)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as rezi__baoc:
        cfr__lmti = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(cfr__lmti)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as rezi__baoc:
        cfr__lmti = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(cfr__lmti)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as rezi__baoc:
        cfr__lmti = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(cfr__lmti)


def req_limit(sql_request):
    import re
    nrm__nwpq = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    doxl__cuyc = nrm__nwpq.search(sql_request)
    if doxl__cuyc:
        return int(doxl__cuyc.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    kdq__qyl = next_label()
    amia__usf = [col_names[bka__cpr] for bka__cpr in out_used_cols]
    goawv__ytwjz = [col_typs[bka__cpr] for bka__cpr in out_used_cols]
    if index_column_name:
        amia__usf.append(index_column_name)
        goawv__ytwjz.append(index_column_type)
    nsrb__tlh = None
    drl__jen = None
    sqrla__xxz = TableType(tuple(col_typs)) if out_used_cols else types.none
    qqv__clivy = ''
    gorih__tme = {}
    sdhl__zpvi = []
    if filters and db_type == 'iceberg':
        gorih__tme, sdhl__zpvi = bodo.ir.connector.generate_filter_map(filters)
        qqv__clivy = ', '.join(gorih__tme.values())
    stxo__lofz = (
        f'def sql_reader_py(sql_request, conn, database_schema, {qqv__clivy}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        fzpos__suuer, ovro__zqxpr = bodo.ir.connector.generate_arrow_filters(
            filters, gorih__tme, sdhl__zpvi, col_names, col_names, col_typs,
            typemap, 'iceberg')
        zypg__dnn: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[bka__cpr]) for bka__cpr in out_used_cols]
        btfmn__orbm = {yui__mlwzj: bka__cpr for bka__cpr, yui__mlwzj in
            enumerate(zypg__dnn)}
        mlu__irf = [int(is_nullable(col_typs[bka__cpr])) for bka__cpr in
            zypg__dnn]
        kdq__gtef = ',' if qqv__clivy else ''
        stxo__lofz += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        stxo__lofz += f"""  dnf_filters, expr_filters = get_filters_pyobject("{fzpos__suuer}", "{ovro__zqxpr}", ({qqv__clivy}{kdq__gtef}))
"""
        stxo__lofz += f'  out_table = iceberg_read(\n'
        stxo__lofz += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        stxo__lofz += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        stxo__lofz += (
            f'    expr_filters, selected_cols_arr_{kdq__qyl}.ctypes,\n')
        stxo__lofz += (
            f'    {len(zypg__dnn)}, nullable_cols_arr_{kdq__qyl}.ctypes,\n')
        stxo__lofz += f'    pyarrow_table_schema_{kdq__qyl},\n'
        stxo__lofz += f'  )\n'
        stxo__lofz += f'  check_and_propagate_cpp_exception()\n'
        mkqxb__rhc = not out_used_cols
        sqrla__xxz = TableType(tuple(col_typs))
        if mkqxb__rhc:
            sqrla__xxz = types.none
        zpg__cqorv = 'None'
        if index_column_name is not None:
            ixs__dvrtr = len(out_used_cols) + 1 if not mkqxb__rhc else 0
            zpg__cqorv = (
                f'info_to_array(info_from_table(out_table, {ixs__dvrtr}), index_col_typ)'
                )
        stxo__lofz += f'  index_var = {zpg__cqorv}\n'
        nsrb__tlh = None
        if not mkqxb__rhc:
            nsrb__tlh = []
            yrf__kyf = 0
            for bka__cpr in range(len(col_names)):
                if yrf__kyf < len(out_used_cols) and bka__cpr == out_used_cols[
                    yrf__kyf]:
                    nsrb__tlh.append(btfmn__orbm[bka__cpr])
                    yrf__kyf += 1
                else:
                    nsrb__tlh.append(-1)
            nsrb__tlh = np.array(nsrb__tlh, dtype=np.int64)
        if mkqxb__rhc:
            stxo__lofz += '  table_var = None\n'
        else:
            stxo__lofz += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{kdq__qyl}, py_table_type_{kdq__qyl})
"""
        stxo__lofz += f'  delete_table(out_table)\n'
        stxo__lofz += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        stxo__lofz += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        mlu__irf = [int(is_nullable(col_typs[bka__cpr])) for bka__cpr in
            out_used_cols]
        if index_column_name:
            mlu__irf.append(int(is_nullable(index_column_type)))
        stxo__lofz += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(mlu__irf)}, np.array({mlu__irf}, dtype=np.int32).ctypes)
"""
        stxo__lofz += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            stxo__lofz += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            stxo__lofz += '  index_var = None\n'
        if out_used_cols:
            dub__iou = []
            yrf__kyf = 0
            for bka__cpr in range(len(col_names)):
                if yrf__kyf < len(out_used_cols) and bka__cpr == out_used_cols[
                    yrf__kyf]:
                    dub__iou.append(yrf__kyf)
                    yrf__kyf += 1
                else:
                    dub__iou.append(-1)
            nsrb__tlh = np.array(dub__iou, dtype=np.int64)
            stxo__lofz += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{kdq__qyl}, py_table_type_{kdq__qyl})
"""
        else:
            stxo__lofz += '  table_var = None\n'
        stxo__lofz += '  delete_table(out_table)\n'
        stxo__lofz += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            stxo__lofz += f"""  type_usecols_offsets_arr_{kdq__qyl}_2 = type_usecols_offsets_arr_{kdq__qyl}
"""
            drl__jen = np.array(out_used_cols, dtype=np.int64)
        stxo__lofz += '  df_typeref_2 = df_typeref\n'
        stxo__lofz += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            stxo__lofz += '  pymysql_check()\n'
        elif db_type == 'oracle':
            stxo__lofz += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            stxo__lofz += '  psycopg2_check()\n'
        if parallel:
            stxo__lofz += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                stxo__lofz += f'  nb_row = {limit}\n'
            else:
                stxo__lofz += '  with objmode(nb_row="int64"):\n'
                stxo__lofz += f'     if rank == {MPI_ROOT}:\n'
                stxo__lofz += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                stxo__lofz += '         frame = pd.read_sql(sql_cons, conn)\n'
                stxo__lofz += '         nb_row = frame.iat[0,0]\n'
                stxo__lofz += '     else:\n'
                stxo__lofz += '         nb_row = 0\n'
                stxo__lofz += '  nb_row = bcast_scalar(nb_row)\n'
            stxo__lofz += f"""  with objmode(table_var=py_table_type_{kdq__qyl}, index_var=index_col_typ):
"""
            stxo__lofz += (
                '    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)\n'
                )
            if db_type == 'oracle':
                stxo__lofz += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                stxo__lofz += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            stxo__lofz += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            stxo__lofz += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            stxo__lofz += f"""  with objmode(table_var=py_table_type_{kdq__qyl}, index_var=index_col_typ):
"""
            stxo__lofz += '    df_ret = pd.read_sql(sql_request, conn)\n'
            stxo__lofz += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            stxo__lofz += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            stxo__lofz += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            stxo__lofz += '    index_var = None\n'
        if out_used_cols:
            stxo__lofz += f'    arrs = []\n'
            stxo__lofz += f'    for i in range(df_ret.shape[1]):\n'
            stxo__lofz += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            stxo__lofz += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{kdq__qyl}_2, {len(col_names)})
"""
        else:
            stxo__lofz += '    table_var = None\n'
    stxo__lofz += '  return (table_var, index_var)\n'
    atmbf__dphdk = globals()
    atmbf__dphdk.update({'bodo': bodo, f'py_table_type_{kdq__qyl}':
        sqrla__xxz, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        atmbf__dphdk.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{kdq__qyl}': nsrb__tlh})
    if db_type == 'iceberg':
        atmbf__dphdk.update({f'selected_cols_arr_{kdq__qyl}': np.array(
            zypg__dnn, np.int32), f'nullable_cols_arr_{kdq__qyl}': np.array
            (mlu__irf, np.int32), f'py_table_type_{kdq__qyl}': sqrla__xxz,
            f'pyarrow_table_schema_{kdq__qyl}': pyarrow_table_schema,
            'get_filters_pyobject': bodo.io.parquet_pio.
            get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        atmbf__dphdk.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        atmbf__dphdk.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(goawv__ytwjz), bodo.RangeIndexType(
            None), tuple(amia__usf)), 'Table': Table,
            f'type_usecols_offsets_arr_{kdq__qyl}': drl__jen})
    kzwk__pibej = {}
    exec(stxo__lofz, atmbf__dphdk, kzwk__pibej)
    riqv__ajmor = kzwk__pibej['sql_reader_py']
    kgx__nfhe = numba.njit(riqv__ajmor)
    compiled_funcs.append(kgx__nfhe)
    return kgx__nfhe


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
