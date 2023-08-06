from urllib.parse import parse_qsl, urlparse
import pyarrow as pa
import snowflake.connector
import bodo
from bodo.utils import tracing
from bodo.utils.typing import BodoError
FIELD_TYPE_TO_PA_TYPE = [pa.int64(), pa.float64(), pa.string(), pa.date32(),
    pa.timestamp('ns'), pa.string(), pa.timestamp('ns'), pa.timestamp('ns'),
    pa.timestamp('ns'), pa.string(), pa.string(), pa.binary(), pa.time64(
    'ns'), pa.bool_()]


def get_connection_params(conn_str):
    import json
    jvtzc__uee = urlparse(conn_str)
    qycq__zycdz = {}
    if jvtzc__uee.username:
        qycq__zycdz['user'] = jvtzc__uee.username
    if jvtzc__uee.password:
        qycq__zycdz['password'] = jvtzc__uee.password
    if jvtzc__uee.hostname:
        qycq__zycdz['account'] = jvtzc__uee.hostname
    if jvtzc__uee.port:
        qycq__zycdz['port'] = jvtzc__uee.port
    if jvtzc__uee.path:
        vwso__vgd = jvtzc__uee.path
        if vwso__vgd.startswith('/'):
            vwso__vgd = vwso__vgd[1:]
        ahm__kibc = vwso__vgd.split('/')
        if len(ahm__kibc) == 2:
            uhef__cmijm, schema = ahm__kibc
        elif len(ahm__kibc) == 1:
            uhef__cmijm = ahm__kibc[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        qycq__zycdz['database'] = uhef__cmijm
        if schema:
            qycq__zycdz['schema'] = schema
    if jvtzc__uee.query:
        for yhtx__ghq, zfbf__qkf in parse_qsl(jvtzc__uee.query):
            qycq__zycdz[yhtx__ghq] = zfbf__qkf
            if yhtx__ghq == 'session_parameters':
                qycq__zycdz[yhtx__ghq] = json.loads(zfbf__qkf)
    qycq__zycdz['application'] = 'bodo'
    return qycq__zycdz


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for tfwke__bis in batches:
            tfwke__bis._bodo_num_rows = tfwke__bis.rowcount
            self._bodo_total_rows += tfwke__bis._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    wee__tync = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    whriv__cju = MPI.COMM_WORLD
    fmjij__rzweb = tracing.Event('snowflake_connect', is_parallel=False)
    lgljy__cyong = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**lgljy__cyong)
    fmjij__rzweb.finalize()
    if bodo.get_rank() == 0:
        uvu__qmwd = conn.cursor()
        dckj__ejfl = tracing.Event('get_schema', is_parallel=False)
        ikjx__xxv = f'select * from ({query}) x LIMIT {100}'
        vccb__ttjzz = uvu__qmwd.execute(ikjx__xxv).fetch_arrow_all()
        if vccb__ttjzz is None:
            yqp__buegf = uvu__qmwd.describe(query)
            qke__uptdr = [pa.field(snwkc__syxo.name, FIELD_TYPE_TO_PA_TYPE[
                snwkc__syxo.type_code]) for snwkc__syxo in yqp__buegf]
            schema = pa.schema(qke__uptdr)
        else:
            schema = vccb__ttjzz.schema
        dckj__ejfl.finalize()
        wloe__roix = tracing.Event('execute_query', is_parallel=False)
        uvu__qmwd.execute(query)
        wloe__roix.finalize()
        batches = uvu__qmwd.get_result_batches()
        whriv__cju.bcast((batches, schema))
    else:
        batches, schema = whriv__cju.bcast(None)
    dihnz__vygru = SnowflakeDataset(batches, schema, conn)
    wee__tync.finalize()
    return dihnz__vygru
