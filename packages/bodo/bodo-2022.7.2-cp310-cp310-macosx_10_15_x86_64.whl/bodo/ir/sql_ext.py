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
    jowyl__jeveb = urlparse(con_str)
    db_type = jowyl__jeveb.scheme
    aztij__lmi = jowyl__jeveb.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', aztij__lmi
    if db_type == 'mysql+pymysql':
        return 'mysql', aztij__lmi
    if con_str == 'iceberg+glue' or jowyl__jeveb.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', aztij__lmi
    return db_type, aztij__lmi


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
    xxgy__kkksp = sql_node.out_vars[0].name
    zwsy__trqpp = sql_node.out_vars[1].name
    if xxgy__kkksp not in lives and zwsy__trqpp not in lives:
        return None
    elif xxgy__kkksp not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif zwsy__trqpp not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx, meta_head_only_info=None):
    if bodo.user_logging.get_verbose_level() >= 1:
        npdv__ujb = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        eiqnp__mmb = []
        thu__ejztq = []
        for fps__hwcgo in sql_node.out_used_cols:
            pdy__toi = sql_node.df_colnames[fps__hwcgo]
            eiqnp__mmb.append(pdy__toi)
            if isinstance(sql_node.out_types[fps__hwcgo], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                thu__ejztq.append(pdy__toi)
        if sql_node.index_column_name:
            eiqnp__mmb.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                thu__ejztq.append(sql_node.index_column_name)
        hiqo__oyo = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', npdv__ujb,
            hiqo__oyo, eiqnp__mmb)
        if thu__ejztq:
            bzv__yax = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', bzv__yax,
                hiqo__oyo, thu__ejztq)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        asak__jfg = set(sql_node.unsupported_columns)
        dvrc__rpxtf = set(sql_node.out_used_cols)
        vctpz__yuwn = dvrc__rpxtf & asak__jfg
        if vctpz__yuwn:
            csns__gabsa = sorted(vctpz__yuwn)
            genxs__rdklj = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            fbc__jcz = 0
            for hjc__txvf in csns__gabsa:
                while sql_node.unsupported_columns[fbc__jcz] != hjc__txvf:
                    fbc__jcz += 1
                genxs__rdklj.append(
                    f"Column '{sql_node.original_df_colnames[hjc__txvf]}' with unsupported arrow type {sql_node.unsupported_arrow_types[fbc__jcz]}"
                    )
                fbc__jcz += 1
            tvk__apn = '\n'.join(genxs__rdklj)
            raise BodoError(tvk__apn, loc=sql_node.loc)
    nknxh__atiyg, wkvu__heqd = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    szt__zezzs = ', '.join(nknxh__atiyg.values())
    egsf__utw = (
        f'def sql_impl(sql_request, conn, database_schema, {szt__zezzs}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        clkp__asa = []
        for ifax__rmk in sql_node.filters:
            cinew__hgf = []
            for njjj__wvpni in ifax__rmk:
                hhmyg__ilrb = '{' + nknxh__atiyg[njjj__wvpni[2].name
                    ] + '}' if isinstance(njjj__wvpni[2], ir.Var
                    ) else njjj__wvpni[2]
                if njjj__wvpni[1] in ('startswith', 'endswith'):
                    ggx__hgvql = ['(', njjj__wvpni[1], '(', njjj__wvpni[0],
                        ',', hhmyg__ilrb, ')', ')']
                else:
                    ggx__hgvql = ['(', njjj__wvpni[0], njjj__wvpni[1],
                        hhmyg__ilrb, ')']
                cinew__hgf.append(' '.join(ggx__hgvql))
            clkp__asa.append(' ( ' + ' AND '.join(cinew__hgf) + ' ) ')
        xen__xyijj = ' WHERE ' + ' OR '.join(clkp__asa)
        for fps__hwcgo, kyx__ecsju in enumerate(nknxh__atiyg.values()):
            egsf__utw += f'    {kyx__ecsju} = get_sql_literal({kyx__ecsju})\n'
        egsf__utw += f'    sql_request = f"{{sql_request}} {xen__xyijj}"\n'
    qwslm__wenqs = ''
    if sql_node.db_type == 'iceberg':
        qwslm__wenqs = szt__zezzs
    egsf__utw += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {qwslm__wenqs})
"""
    rfmj__ewjiv = {}
    exec(egsf__utw, {}, rfmj__ewjiv)
    sgfr__xan = rfmj__ewjiv['sql_impl']
    if sql_node.limit is not None:
        limit = sql_node.limit
    elif meta_head_only_info and meta_head_only_info[0] is not None:
        limit = meta_head_only_info[0]
    else:
        limit = None
    glzoj__umg = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    xdysp__onwo = (types.none if sql_node.database_schema is None else
        string_type)
    mji__knm = compile_to_numba_ir(sgfr__xan, {'_sql_reader_py': glzoj__umg,
        'bcast_scalar': bcast_scalar, 'bcast': bcast, 'get_sql_literal':
        _get_snowflake_sql_literal}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(string_type, string_type, xdysp__onwo) + tuple
        (typemap[xmyol__uaan.name] for xmyol__uaan in wkvu__heqd), typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        wnsm__eixjq = [sql_node.df_colnames[fps__hwcgo] for fps__hwcgo in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            wnsm__eixjq.append(sql_node.index_column_name)
        logws__kxd = escape_column_names(wnsm__eixjq, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            hiw__qxgc = ('SELECT ' + logws__kxd + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            hiw__qxgc = ('SELECT ' + logws__kxd + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        hiw__qxgc = sql_node.sql_request
    replace_arg_nodes(mji__knm, [ir.Const(hiw__qxgc, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + wkvu__heqd)
    rfaa__aknbe = mji__knm.body[:-3]
    rfaa__aknbe[-2].target = sql_node.out_vars[0]
    rfaa__aknbe[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        rfaa__aknbe.pop(-1)
    elif not sql_node.out_used_cols:
        rfaa__aknbe.pop(-2)
    return rfaa__aknbe


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        wnsm__eixjq = [(bhsz__ablqq.upper() if bhsz__ablqq in
            converted_colnames else bhsz__ablqq) for bhsz__ablqq in col_names]
        logws__kxd = ', '.join([f'"{bhsz__ablqq}"' for bhsz__ablqq in
            wnsm__eixjq])
    elif db_type == 'mysql':
        logws__kxd = ', '.join([f'`{bhsz__ablqq}`' for bhsz__ablqq in
            col_names])
    else:
        logws__kxd = ', '.join([f'"{bhsz__ablqq}"' for bhsz__ablqq in
            col_names])
    return logws__kxd


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    xmtsu__saxx = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(xmtsu__saxx,
        'Filter pushdown')
    if xmtsu__saxx == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(xmtsu__saxx, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif xmtsu__saxx == bodo.pd_timestamp_type:

        def impl(filter_value):
            ywch__qfsgv = filter_value.nanosecond
            ncq__omw = ''
            if ywch__qfsgv < 10:
                ncq__omw = '00'
            elif ywch__qfsgv < 100:
                ncq__omw = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{ncq__omw}{ywch__qfsgv}'"
                )
        return impl
    elif xmtsu__saxx == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {xmtsu__saxx} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    pjvb__sjol = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    xmtsu__saxx = types.unliteral(filter_value)
    if isinstance(xmtsu__saxx, types.List) and (isinstance(xmtsu__saxx.
        dtype, scalar_isinstance) or xmtsu__saxx.dtype in pjvb__sjol):

        def impl(filter_value):
            rcfjw__vvl = ', '.join([_get_snowflake_sql_literal_scalar(
                bhsz__ablqq) for bhsz__ablqq in filter_value])
            return f'({rcfjw__vvl})'
        return impl
    elif isinstance(xmtsu__saxx, scalar_isinstance
        ) or xmtsu__saxx in pjvb__sjol:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {xmtsu__saxx} used in filter pushdown.'
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
    except ImportError as bpxi__gyide:
        bbod__xskwu = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(bbod__xskwu)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as bpxi__gyide:
        bbod__xskwu = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(bbod__xskwu)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as bpxi__gyide:
        bbod__xskwu = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(bbod__xskwu)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as bpxi__gyide:
        bbod__xskwu = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(bbod__xskwu)


def req_limit(sql_request):
    import re
    ryrvj__ezv = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    qeb__jsdjx = ryrvj__ezv.search(sql_request)
    if qeb__jsdjx:
        return int(qeb__jsdjx.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type: str, limit: Optional[int], parallel, typemap, filters,
    pyarrow_table_schema: 'Optional[pyarrow.Schema]'):
    yjfr__nxw = next_label()
    wnsm__eixjq = [col_names[fps__hwcgo] for fps__hwcgo in out_used_cols]
    ohyat__hsfqj = [col_typs[fps__hwcgo] for fps__hwcgo in out_used_cols]
    if index_column_name:
        wnsm__eixjq.append(index_column_name)
        ohyat__hsfqj.append(index_column_type)
    rpcoq__oyar = None
    uff__ihz = None
    vdisa__cvruw = TableType(tuple(col_typs)) if out_used_cols else types.none
    qwslm__wenqs = ''
    nknxh__atiyg = {}
    wkvu__heqd = []
    if filters and db_type == 'iceberg':
        nknxh__atiyg, wkvu__heqd = bodo.ir.connector.generate_filter_map(
            filters)
        qwslm__wenqs = ', '.join(nknxh__atiyg.values())
    egsf__utw = (
        f'def sql_reader_py(sql_request, conn, database_schema, {qwslm__wenqs}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        opiwl__vbafq, mhfky__ykem = bodo.ir.connector.generate_arrow_filters(
            filters, nknxh__atiyg, wkvu__heqd, col_names, col_names,
            col_typs, typemap, 'iceberg')
        ndrd__dakz: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[fps__hwcgo]) for fps__hwcgo in out_used_cols]
        stwf__fibve = {xlujl__cuqat: fps__hwcgo for fps__hwcgo,
            xlujl__cuqat in enumerate(ndrd__dakz)}
        vbmvz__cvu = [int(is_nullable(col_typs[fps__hwcgo])) for fps__hwcgo in
            ndrd__dakz]
        ovrsb__hemq = ',' if qwslm__wenqs else ''
        egsf__utw += f"""  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})
  dnf_filters, expr_filters = get_filters_pyobject("{opiwl__vbafq}", "{mhfky__ykem}", ({qwslm__wenqs}{ovrsb__hemq}))
  out_table = iceberg_read(
    unicode_to_utf8(conn),
    unicode_to_utf8(database_schema),
    unicode_to_utf8(sql_request),
    {parallel},
    {-1 if limit is None else limit},
    dnf_filters,
    expr_filters,
    selected_cols_arr_{yjfr__nxw}.ctypes,
    {len(ndrd__dakz)},
    nullable_cols_arr_{yjfr__nxw}.ctypes,
    pyarrow_table_schema_{yjfr__nxw},
  )
  check_and_propagate_cpp_exception()
"""
        vaja__vbv = not out_used_cols
        vdisa__cvruw = TableType(tuple(col_typs))
        if vaja__vbv:
            vdisa__cvruw = types.none
        zwsy__trqpp = 'None'
        if index_column_name is not None:
            rzbez__vnqa = len(out_used_cols) + 1 if not vaja__vbv else 0
            zwsy__trqpp = (
                f'info_to_array(info_from_table(out_table, {rzbez__vnqa}), index_col_typ)'
                )
        egsf__utw += f'  index_var = {zwsy__trqpp}\n'
        rpcoq__oyar = None
        if not vaja__vbv:
            rpcoq__oyar = []
            socij__klk = 0
            for fps__hwcgo in range(len(col_names)):
                if socij__klk < len(out_used_cols
                    ) and fps__hwcgo == out_used_cols[socij__klk]:
                    rpcoq__oyar.append(stwf__fibve[fps__hwcgo])
                    socij__klk += 1
                else:
                    rpcoq__oyar.append(-1)
            rpcoq__oyar = np.array(rpcoq__oyar, dtype=np.int64)
        if vaja__vbv:
            egsf__utw += '  table_var = None\n'
        else:
            egsf__utw += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{yjfr__nxw}, py_table_type_{yjfr__nxw})
"""
        egsf__utw += f'  delete_table(out_table)\n'
        egsf__utw += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        egsf__utw += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        vbmvz__cvu = [int(is_nullable(col_typs[fps__hwcgo])) for fps__hwcgo in
            out_used_cols]
        if index_column_name:
            vbmvz__cvu.append(int(is_nullable(index_column_type)))
        egsf__utw += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(vbmvz__cvu)}, np.array({vbmvz__cvu}, dtype=np.int32).ctypes)
"""
        egsf__utw += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            egsf__utw += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            egsf__utw += '  index_var = None\n'
        if out_used_cols:
            fbc__jcz = []
            socij__klk = 0
            for fps__hwcgo in range(len(col_names)):
                if socij__klk < len(out_used_cols
                    ) and fps__hwcgo == out_used_cols[socij__klk]:
                    fbc__jcz.append(socij__klk)
                    socij__klk += 1
                else:
                    fbc__jcz.append(-1)
            rpcoq__oyar = np.array(fbc__jcz, dtype=np.int64)
            egsf__utw += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{yjfr__nxw}, py_table_type_{yjfr__nxw})
"""
        else:
            egsf__utw += '  table_var = None\n'
        egsf__utw += '  delete_table(out_table)\n'
        egsf__utw += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            egsf__utw += f"""  type_usecols_offsets_arr_{yjfr__nxw}_2 = type_usecols_offsets_arr_{yjfr__nxw}
"""
            uff__ihz = np.array(out_used_cols, dtype=np.int64)
        egsf__utw += '  df_typeref_2 = df_typeref\n'
        egsf__utw += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            egsf__utw += '  pymysql_check()\n'
        elif db_type == 'oracle':
            egsf__utw += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            egsf__utw += '  psycopg2_check()\n'
        if parallel:
            egsf__utw += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                egsf__utw += f'  nb_row = {limit}\n'
            else:
                egsf__utw += '  with objmode(nb_row="int64"):\n'
                egsf__utw += f'     if rank == {MPI_ROOT}:\n'
                egsf__utw += (
                    "         sql_cons = 'select count(*) from (' + sql_request + ') x'\n"
                    )
                egsf__utw += '         frame = pd.read_sql(sql_cons, conn)\n'
                egsf__utw += '         nb_row = frame.iat[0,0]\n'
                egsf__utw += '     else:\n'
                egsf__utw += '         nb_row = 0\n'
                egsf__utw += '  nb_row = bcast_scalar(nb_row)\n'
            egsf__utw += f"""  with objmode(table_var=py_table_type_{yjfr__nxw}, index_var=index_col_typ):
"""
            egsf__utw += (
                '    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)\n'
                )
            if db_type == 'oracle':
                egsf__utw += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                egsf__utw += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            egsf__utw += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            egsf__utw += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            egsf__utw += f"""  with objmode(table_var=py_table_type_{yjfr__nxw}, index_var=index_col_typ):
"""
            egsf__utw += '    df_ret = pd.read_sql(sql_request, conn)\n'
            egsf__utw += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            egsf__utw += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            egsf__utw += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            egsf__utw += '    index_var = None\n'
        if out_used_cols:
            egsf__utw += f'    arrs = []\n'
            egsf__utw += f'    for i in range(df_ret.shape[1]):\n'
            egsf__utw += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            egsf__utw += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{yjfr__nxw}_2, {len(col_names)})
"""
        else:
            egsf__utw += '    table_var = None\n'
    egsf__utw += '  return (table_var, index_var)\n'
    xuaml__axhou = globals()
    xuaml__axhou.update({'bodo': bodo, f'py_table_type_{yjfr__nxw}':
        vdisa__cvruw, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        xuaml__axhou.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{yjfr__nxw}': rpcoq__oyar})
    if db_type == 'iceberg':
        xuaml__axhou.update({f'selected_cols_arr_{yjfr__nxw}': np.array(
            ndrd__dakz, np.int32), f'nullable_cols_arr_{yjfr__nxw}': np.
            array(vbmvz__cvu, np.int32), f'py_table_type_{yjfr__nxw}':
            vdisa__cvruw, f'pyarrow_table_schema_{yjfr__nxw}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        xuaml__axhou.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        xuaml__axhou.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(ohyat__hsfqj), bodo.RangeIndexType(
            None), tuple(wnsm__eixjq)), 'Table': Table,
            f'type_usecols_offsets_arr_{yjfr__nxw}': uff__ihz})
    rfmj__ewjiv = {}
    exec(egsf__utw, xuaml__axhou, rfmj__ewjiv)
    glzoj__umg = rfmj__ewjiv['sql_reader_py']
    vlawe__napi = numba.njit(glzoj__umg)
    compiled_funcs.append(vlawe__napi)
    return vlawe__napi


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
