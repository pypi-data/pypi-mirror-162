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
    ibxb__vmbqn = {}
    bsuaj__cpu, dms__quzwp = self._current_database_schema(connection, **kw)
    zvla__vun = self._denormalize_quote_join(bsuaj__cpu, schema)
    try:
        xka__feqd = self._get_schema_primary_keys(connection, zvla__vun, **kw)
        csz__qad = connection.execute(text(
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
    except sa_exc.ProgrammingError as pnwl__sxp:
        if pnwl__sxp.orig.errno == 90030:
            return None
        raise
    for table_name, voifo__djd, bwzuk__qnj, eqagc__phugj, ftyy__cfp, eso__ihcr, nvea__hdv, lmpjj__jlr, otr__irnp, xvdl__cubdt in csz__qad:
        table_name = self.normalize_name(table_name)
        voifo__djd = self.normalize_name(voifo__djd)
        if table_name not in ibxb__vmbqn:
            ibxb__vmbqn[table_name] = list()
        if voifo__djd.startswith('sys_clustering_column'):
            continue
        ivi__ogaxq = self.ischema_names.get(bwzuk__qnj, None)
        vud__qlzqu = {}
        if ivi__ogaxq is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(bwzuk__qnj, voifo__djd))
            ivi__ogaxq = sqltypes.NULLTYPE
        elif issubclass(ivi__ogaxq, sqltypes.FLOAT):
            vud__qlzqu['precision'] = ftyy__cfp
            vud__qlzqu['decimal_return_scale'] = eso__ihcr
        elif issubclass(ivi__ogaxq, sqltypes.Numeric):
            vud__qlzqu['precision'] = ftyy__cfp
            vud__qlzqu['scale'] = eso__ihcr
        elif issubclass(ivi__ogaxq, (sqltypes.String, sqltypes.BINARY)):
            vud__qlzqu['length'] = eqagc__phugj
        bermn__lsni = ivi__ogaxq if isinstance(ivi__ogaxq, sqltypes.NullType
            ) else ivi__ogaxq(**vud__qlzqu)
        uifse__fdvij = xka__feqd.get(table_name)
        ibxb__vmbqn[table_name].append({'name': voifo__djd, 'type':
            bermn__lsni, 'nullable': nvea__hdv == 'YES', 'default':
            lmpjj__jlr, 'autoincrement': otr__irnp == 'YES', 'comment':
            xvdl__cubdt, 'primary_key': voifo__djd in xka__feqd[table_name]
            ['constrained_columns'] if uifse__fdvij else False})
    return ibxb__vmbqn


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
    ibxb__vmbqn = []
    bsuaj__cpu, dms__quzwp = self._current_database_schema(connection, **kw)
    zvla__vun = self._denormalize_quote_join(bsuaj__cpu, schema)
    xka__feqd = self._get_schema_primary_keys(connection, zvla__vun, **kw)
    csz__qad = connection.execute(text(
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
    for table_name, voifo__djd, bwzuk__qnj, eqagc__phugj, ftyy__cfp, eso__ihcr, nvea__hdv, lmpjj__jlr, otr__irnp, xvdl__cubdt in csz__qad:
        table_name = self.normalize_name(table_name)
        voifo__djd = self.normalize_name(voifo__djd)
        if voifo__djd.startswith('sys_clustering_column'):
            continue
        ivi__ogaxq = self.ischema_names.get(bwzuk__qnj, None)
        vud__qlzqu = {}
        if ivi__ogaxq is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(bwzuk__qnj, voifo__djd))
            ivi__ogaxq = sqltypes.NULLTYPE
        elif issubclass(ivi__ogaxq, sqltypes.FLOAT):
            vud__qlzqu['precision'] = ftyy__cfp
            vud__qlzqu['decimal_return_scale'] = eso__ihcr
        elif issubclass(ivi__ogaxq, sqltypes.Numeric):
            vud__qlzqu['precision'] = ftyy__cfp
            vud__qlzqu['scale'] = eso__ihcr
        elif issubclass(ivi__ogaxq, (sqltypes.String, sqltypes.BINARY)):
            vud__qlzqu['length'] = eqagc__phugj
        bermn__lsni = ivi__ogaxq if isinstance(ivi__ogaxq, sqltypes.NullType
            ) else ivi__ogaxq(**vud__qlzqu)
        uifse__fdvij = xka__feqd.get(table_name)
        ibxb__vmbqn.append({'name': voifo__djd, 'type': bermn__lsni,
            'nullable': nvea__hdv == 'YES', 'default': lmpjj__jlr,
            'autoincrement': otr__irnp == 'YES', 'comment': xvdl__cubdt if 
            xvdl__cubdt != '' else None, 'primary_key': voifo__djd in
            xka__feqd[table_name]['constrained_columns'] if uifse__fdvij else
            False})
    return ibxb__vmbqn


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
