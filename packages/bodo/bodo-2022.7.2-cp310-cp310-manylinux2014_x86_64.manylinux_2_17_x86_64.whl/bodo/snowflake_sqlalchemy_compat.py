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
    sfy__xrnx = {}
    onq__ijzv, rgx__prjl = self._current_database_schema(connection, **kw)
    bwg__quvey = self._denormalize_quote_join(onq__ijzv, schema)
    try:
        bzo__bpv = self._get_schema_primary_keys(connection, bwg__quvey, **kw)
        xwu__lesv = connection.execute(text(
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
    except sa_exc.ProgrammingError as fpqr__uam:
        if fpqr__uam.orig.errno == 90030:
            return None
        raise
    for table_name, qsmk__ink, nhsfo__ytn, bma__rcvb, zzn__hkc, antzn__wdzxp, nsgvu__syw, wwi__uuaf, fqkh__obn, bnl__cvgo in xwu__lesv:
        table_name = self.normalize_name(table_name)
        qsmk__ink = self.normalize_name(qsmk__ink)
        if table_name not in sfy__xrnx:
            sfy__xrnx[table_name] = list()
        if qsmk__ink.startswith('sys_clustering_column'):
            continue
        endlg__xfdtj = self.ischema_names.get(nhsfo__ytn, None)
        gzmuj__xjkgz = {}
        if endlg__xfdtj is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(nhsfo__ytn, qsmk__ink))
            endlg__xfdtj = sqltypes.NULLTYPE
        elif issubclass(endlg__xfdtj, sqltypes.FLOAT):
            gzmuj__xjkgz['precision'] = zzn__hkc
            gzmuj__xjkgz['decimal_return_scale'] = antzn__wdzxp
        elif issubclass(endlg__xfdtj, sqltypes.Numeric):
            gzmuj__xjkgz['precision'] = zzn__hkc
            gzmuj__xjkgz['scale'] = antzn__wdzxp
        elif issubclass(endlg__xfdtj, (sqltypes.String, sqltypes.BINARY)):
            gzmuj__xjkgz['length'] = bma__rcvb
        ltkg__utauz = endlg__xfdtj if isinstance(endlg__xfdtj, sqltypes.
            NullType) else endlg__xfdtj(**gzmuj__xjkgz)
        baqi__vrsu = bzo__bpv.get(table_name)
        sfy__xrnx[table_name].append({'name': qsmk__ink, 'type':
            ltkg__utauz, 'nullable': nsgvu__syw == 'YES', 'default':
            wwi__uuaf, 'autoincrement': fqkh__obn == 'YES', 'comment':
            bnl__cvgo, 'primary_key': qsmk__ink in bzo__bpv[table_name][
            'constrained_columns'] if baqi__vrsu else False})
    return sfy__xrnx


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
    sfy__xrnx = []
    onq__ijzv, rgx__prjl = self._current_database_schema(connection, **kw)
    bwg__quvey = self._denormalize_quote_join(onq__ijzv, schema)
    bzo__bpv = self._get_schema_primary_keys(connection, bwg__quvey, **kw)
    xwu__lesv = connection.execute(text(
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
    for table_name, qsmk__ink, nhsfo__ytn, bma__rcvb, zzn__hkc, antzn__wdzxp, nsgvu__syw, wwi__uuaf, fqkh__obn, bnl__cvgo in xwu__lesv:
        table_name = self.normalize_name(table_name)
        qsmk__ink = self.normalize_name(qsmk__ink)
        if qsmk__ink.startswith('sys_clustering_column'):
            continue
        endlg__xfdtj = self.ischema_names.get(nhsfo__ytn, None)
        gzmuj__xjkgz = {}
        if endlg__xfdtj is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(nhsfo__ytn, qsmk__ink))
            endlg__xfdtj = sqltypes.NULLTYPE
        elif issubclass(endlg__xfdtj, sqltypes.FLOAT):
            gzmuj__xjkgz['precision'] = zzn__hkc
            gzmuj__xjkgz['decimal_return_scale'] = antzn__wdzxp
        elif issubclass(endlg__xfdtj, sqltypes.Numeric):
            gzmuj__xjkgz['precision'] = zzn__hkc
            gzmuj__xjkgz['scale'] = antzn__wdzxp
        elif issubclass(endlg__xfdtj, (sqltypes.String, sqltypes.BINARY)):
            gzmuj__xjkgz['length'] = bma__rcvb
        ltkg__utauz = endlg__xfdtj if isinstance(endlg__xfdtj, sqltypes.
            NullType) else endlg__xfdtj(**gzmuj__xjkgz)
        baqi__vrsu = bzo__bpv.get(table_name)
        sfy__xrnx.append({'name': qsmk__ink, 'type': ltkg__utauz,
            'nullable': nsgvu__syw == 'YES', 'default': wwi__uuaf,
            'autoincrement': fqkh__obn == 'YES', 'comment': bnl__cvgo if 
            bnl__cvgo != '' else None, 'primary_key': qsmk__ink in bzo__bpv
            [table_name]['constrained_columns'] if baqi__vrsu else False})
    return sfy__xrnx


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
