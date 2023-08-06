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
    mbty__dyfrf = urlparse(conn_str)
    yzdp__kuvy = {}
    if mbty__dyfrf.username:
        yzdp__kuvy['user'] = mbty__dyfrf.username
    if mbty__dyfrf.password:
        yzdp__kuvy['password'] = mbty__dyfrf.password
    if mbty__dyfrf.hostname:
        yzdp__kuvy['account'] = mbty__dyfrf.hostname
    if mbty__dyfrf.port:
        yzdp__kuvy['port'] = mbty__dyfrf.port
    if mbty__dyfrf.path:
        eajki__giyg = mbty__dyfrf.path
        if eajki__giyg.startswith('/'):
            eajki__giyg = eajki__giyg[1:]
        zopz__gjoyb = eajki__giyg.split('/')
        if len(zopz__gjoyb) == 2:
            ilyr__ykh, schema = zopz__gjoyb
        elif len(zopz__gjoyb) == 1:
            ilyr__ykh = zopz__gjoyb[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        yzdp__kuvy['database'] = ilyr__ykh
        if schema:
            yzdp__kuvy['schema'] = schema
    if mbty__dyfrf.query:
        for peeuu__bccu, qofy__fsb in parse_qsl(mbty__dyfrf.query):
            yzdp__kuvy[peeuu__bccu] = qofy__fsb
            if peeuu__bccu == 'session_parameters':
                yzdp__kuvy[peeuu__bccu] = json.loads(qofy__fsb)
    yzdp__kuvy['application'] = 'bodo'
    return yzdp__kuvy


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for urz__tkio in batches:
            urz__tkio._bodo_num_rows = urz__tkio.rowcount
            self._bodo_total_rows += urz__tkio._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    qsmbh__kxok = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    zopum__grei = MPI.COMM_WORLD
    ylvn__wfye = tracing.Event('snowflake_connect', is_parallel=False)
    npcf__ller = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**npcf__ller)
    ylvn__wfye.finalize()
    if bodo.get_rank() == 0:
        bllal__lbl = conn.cursor()
        xnh__gfjd = tracing.Event('get_schema', is_parallel=False)
        gsy__qsb = f'select * from ({query}) x LIMIT {100}'
        czfv__hzrkt = bllal__lbl.execute(gsy__qsb).fetch_arrow_all()
        if czfv__hzrkt is None:
            qbq__nxr = bllal__lbl.describe(query)
            navif__szorm = [pa.field(vzkc__wdh.name, FIELD_TYPE_TO_PA_TYPE[
                vzkc__wdh.type_code]) for vzkc__wdh in qbq__nxr]
            schema = pa.schema(navif__szorm)
        else:
            schema = czfv__hzrkt.schema
        xnh__gfjd.finalize()
        ctoxt__jvinj = tracing.Event('execute_query', is_parallel=False)
        bllal__lbl.execute(query)
        ctoxt__jvinj.finalize()
        batches = bllal__lbl.get_result_batches()
        zopum__grei.bcast((batches, schema))
    else:
        batches, schema = zopum__grei.bcast(None)
    nvo__wfhjn = SnowflakeDataset(batches, schema, conn)
    qsmbh__kxok.finalize()
    return nvo__wfhjn
