import hashlib
import inspect
import warnings
import snowflake.sqlalchemy
import sqlalchemy.types as sqltypes
from sqlalchemy import exc as sa_exc
from sqlalchemy import util as sa_util
from sqlalchemy.sql import text
_check_snowflake_sqlalchemy_change = True


def _get_schema_columns(self, connection, schema, **kw):
    pgsw__wdg = {}
    brdd__aoq, bvb__rpqf = self._current_database_schema(connection, **kw)
    xnbgv__eaxa = self._denormalize_quote_join(brdd__aoq, schema)
    try:
        ctzat__yjncx = self._get_schema_primary_keys(connection,
            xnbgv__eaxa, **kw)
        rfl__wxjf = connection.execute(text(
            """
        SELECT /* sqlalchemy:_get_schema_columns */
                ic.table_name,
                ic.column_name,
                ic.data_type,
                ic.character_maximum_length,
                ic.numeric_precision,
                ic.numeric_scale,
                ic.is_nullable,
                ic.column_default,
                ic.is_identity,
                ic.comment
            FROM information_schema.columns ic
            WHERE ic.table_schema=:table_schema
            ORDER BY ic.ordinal_position"""
            ), {'table_schema': self.denormalize_name(schema)})
    except sa_exc.ProgrammingError as ymckx__pdpr:
        if ymckx__pdpr.orig.errno == 90030:
            return None
        raise
    for table_name, vmyv__ymh, jmn__hho, ncnxz__srrt, xfh__rch, wrc__cwnh, ergfb__pjzm, dbqn__gqg, mdwlp__ljd, jjn__guhye in rfl__wxjf:
        table_name = self.normalize_name(table_name)
        vmyv__ymh = self.normalize_name(vmyv__ymh)
        if table_name not in pgsw__wdg:
            pgsw__wdg[table_name] = list()
        if vmyv__ymh.startswith('sys_clustering_column'):
            continue
        nwr__ytkww = self.ischema_names.get(jmn__hho, None)
        uhjln__mhgnu = {}
        if nwr__ytkww is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(jmn__hho, vmyv__ymh))
            nwr__ytkww = sqltypes.NULLTYPE
        elif issubclass(nwr__ytkww, sqltypes.FLOAT):
            uhjln__mhgnu['precision'] = xfh__rch
            uhjln__mhgnu['decimal_return_scale'] = wrc__cwnh
        elif issubclass(nwr__ytkww, sqltypes.Numeric):
            uhjln__mhgnu['precision'] = xfh__rch
            uhjln__mhgnu['scale'] = wrc__cwnh
        elif issubclass(nwr__ytkww, (sqltypes.String, sqltypes.BINARY)):
            uhjln__mhgnu['length'] = ncnxz__srrt
        gnu__guy = nwr__ytkww if isinstance(nwr__ytkww, sqltypes.NullType
            ) else nwr__ytkww(**uhjln__mhgnu)
        xezon__xlx = ctzat__yjncx.get(table_name)
        pgsw__wdg[table_name].append({'name': vmyv__ymh, 'type': gnu__guy,
            'nullable': ergfb__pjzm == 'YES', 'default': dbqn__gqg,
            'autoincrement': mdwlp__ljd == 'YES', 'comment': jjn__guhye,
            'primary_key': vmyv__ymh in ctzat__yjncx[table_name][
            'constrained_columns'] if xezon__xlx else False})
    return pgsw__wdg


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_schema_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdf39af1ac165319d3b6074e8cf9296a090a21f0e2c05b644ff8ec0e56e2d769':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns = (
    _get_schema_columns)


def _get_table_columns(self, connection, table_name, schema=None, **kw):
    pgsw__wdg = []
    brdd__aoq, bvb__rpqf = self._current_database_schema(connection, **kw)
    xnbgv__eaxa = self._denormalize_quote_join(brdd__aoq, schema)
    ctzat__yjncx = self._get_schema_primary_keys(connection, xnbgv__eaxa, **kw)
    rfl__wxjf = connection.execute(text(
        """
    SELECT /* sqlalchemy:get_table_columns */
            ic.table_name,
            ic.column_name,
            ic.data_type,
            ic.character_maximum_length,
            ic.numeric_precision,
            ic.numeric_scale,
            ic.is_nullable,
            ic.column_default,
            ic.is_identity,
            ic.comment
        FROM information_schema.columns ic
        WHERE ic.table_schema=:table_schema
        AND ic.table_name=:table_name
        ORDER BY ic.ordinal_position"""
        ), {'table_schema': self.denormalize_name(schema), 'table_name':
        self.denormalize_name(table_name)})
    for table_name, vmyv__ymh, jmn__hho, ncnxz__srrt, xfh__rch, wrc__cwnh, ergfb__pjzm, dbqn__gqg, mdwlp__ljd, jjn__guhye in rfl__wxjf:
        table_name = self.normalize_name(table_name)
        vmyv__ymh = self.normalize_name(vmyv__ymh)
        if vmyv__ymh.startswith('sys_clustering_column'):
            continue
        nwr__ytkww = self.ischema_names.get(jmn__hho, None)
        uhjln__mhgnu = {}
        if nwr__ytkww is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(jmn__hho, vmyv__ymh))
            nwr__ytkww = sqltypes.NULLTYPE
        elif issubclass(nwr__ytkww, sqltypes.FLOAT):
            uhjln__mhgnu['precision'] = xfh__rch
            uhjln__mhgnu['decimal_return_scale'] = wrc__cwnh
        elif issubclass(nwr__ytkww, sqltypes.Numeric):
            uhjln__mhgnu['precision'] = xfh__rch
            uhjln__mhgnu['scale'] = wrc__cwnh
        elif issubclass(nwr__ytkww, (sqltypes.String, sqltypes.BINARY)):
            uhjln__mhgnu['length'] = ncnxz__srrt
        gnu__guy = nwr__ytkww if isinstance(nwr__ytkww, sqltypes.NullType
            ) else nwr__ytkww(**uhjln__mhgnu)
        xezon__xlx = ctzat__yjncx.get(table_name)
        pgsw__wdg.append({'name': vmyv__ymh, 'type': gnu__guy, 'nullable': 
            ergfb__pjzm == 'YES', 'default': dbqn__gqg, 'autoincrement': 
            mdwlp__ljd == 'YES', 'comment': jjn__guhye if jjn__guhye != '' else
            None, 'primary_key': vmyv__ymh in ctzat__yjncx[table_name][
            'constrained_columns'] if xezon__xlx else False})
    return pgsw__wdg


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_table_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9ecc8a2425c655836ade4008b1b98a8fd1819f3be43ba77b0fbbfc1f8740e2be':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns = (
    _get_table_columns)
