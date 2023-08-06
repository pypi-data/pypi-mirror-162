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
    rkobw__hyo = {}
    kzm__vila, xqdwo__qnrs = self._current_database_schema(connection, **kw)
    htx__noeo = self._denormalize_quote_join(kzm__vila, schema)
    try:
        calp__glwm = self._get_schema_primary_keys(connection, htx__noeo, **kw)
        dead__chgot = connection.execute(text(
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
    except sa_exc.ProgrammingError as jyd__xcgbz:
        if jyd__xcgbz.orig.errno == 90030:
            return None
        raise
    for table_name, qsa__svowt, rbqu__ijbrt, gfizx__iwixv, ufpm__sojl, gsa__xxe, hka__gxyrm, lcehw__vhmed, nqrzt__nkgoo, wjywr__mhpix in dead__chgot:
        table_name = self.normalize_name(table_name)
        qsa__svowt = self.normalize_name(qsa__svowt)
        if table_name not in rkobw__hyo:
            rkobw__hyo[table_name] = list()
        if qsa__svowt.startswith('sys_clustering_column'):
            continue
        mnqzu__dbxs = self.ischema_names.get(rbqu__ijbrt, None)
        teouw__fub = {}
        if mnqzu__dbxs is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(rbqu__ijbrt, qsa__svowt))
            mnqzu__dbxs = sqltypes.NULLTYPE
        elif issubclass(mnqzu__dbxs, sqltypes.FLOAT):
            teouw__fub['precision'] = ufpm__sojl
            teouw__fub['decimal_return_scale'] = gsa__xxe
        elif issubclass(mnqzu__dbxs, sqltypes.Numeric):
            teouw__fub['precision'] = ufpm__sojl
            teouw__fub['scale'] = gsa__xxe
        elif issubclass(mnqzu__dbxs, (sqltypes.String, sqltypes.BINARY)):
            teouw__fub['length'] = gfizx__iwixv
        gygw__wfhop = mnqzu__dbxs if isinstance(mnqzu__dbxs, sqltypes.NullType
            ) else mnqzu__dbxs(**teouw__fub)
        rmyz__vonv = calp__glwm.get(table_name)
        rkobw__hyo[table_name].append({'name': qsa__svowt, 'type':
            gygw__wfhop, 'nullable': hka__gxyrm == 'YES', 'default':
            lcehw__vhmed, 'autoincrement': nqrzt__nkgoo == 'YES', 'comment':
            wjywr__mhpix, 'primary_key': qsa__svowt in calp__glwm[
            table_name]['constrained_columns'] if rmyz__vonv else False})
    return rkobw__hyo


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
    rkobw__hyo = []
    kzm__vila, xqdwo__qnrs = self._current_database_schema(connection, **kw)
    htx__noeo = self._denormalize_quote_join(kzm__vila, schema)
    calp__glwm = self._get_schema_primary_keys(connection, htx__noeo, **kw)
    dead__chgot = connection.execute(text(
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
    for table_name, qsa__svowt, rbqu__ijbrt, gfizx__iwixv, ufpm__sojl, gsa__xxe, hka__gxyrm, lcehw__vhmed, nqrzt__nkgoo, wjywr__mhpix in dead__chgot:
        table_name = self.normalize_name(table_name)
        qsa__svowt = self.normalize_name(qsa__svowt)
        if qsa__svowt.startswith('sys_clustering_column'):
            continue
        mnqzu__dbxs = self.ischema_names.get(rbqu__ijbrt, None)
        teouw__fub = {}
        if mnqzu__dbxs is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(rbqu__ijbrt, qsa__svowt))
            mnqzu__dbxs = sqltypes.NULLTYPE
        elif issubclass(mnqzu__dbxs, sqltypes.FLOAT):
            teouw__fub['precision'] = ufpm__sojl
            teouw__fub['decimal_return_scale'] = gsa__xxe
        elif issubclass(mnqzu__dbxs, sqltypes.Numeric):
            teouw__fub['precision'] = ufpm__sojl
            teouw__fub['scale'] = gsa__xxe
        elif issubclass(mnqzu__dbxs, (sqltypes.String, sqltypes.BINARY)):
            teouw__fub['length'] = gfizx__iwixv
        gygw__wfhop = mnqzu__dbxs if isinstance(mnqzu__dbxs, sqltypes.NullType
            ) else mnqzu__dbxs(**teouw__fub)
        rmyz__vonv = calp__glwm.get(table_name)
        rkobw__hyo.append({'name': qsa__svowt, 'type': gygw__wfhop,
            'nullable': hka__gxyrm == 'YES', 'default': lcehw__vhmed,
            'autoincrement': nqrzt__nkgoo == 'YES', 'comment': wjywr__mhpix if
            wjywr__mhpix != '' else None, 'primary_key': qsa__svowt in
            calp__glwm[table_name]['constrained_columns'] if rmyz__vonv else
            False})
    return rkobw__hyo


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
