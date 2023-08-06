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
    ncerk__heh = urlparse(conn_str)
    opsl__aut = {}
    if ncerk__heh.username:
        opsl__aut['user'] = ncerk__heh.username
    if ncerk__heh.password:
        opsl__aut['password'] = ncerk__heh.password
    if ncerk__heh.hostname:
        opsl__aut['account'] = ncerk__heh.hostname
    if ncerk__heh.port:
        opsl__aut['port'] = ncerk__heh.port
    if ncerk__heh.path:
        btok__lpg = ncerk__heh.path
        if btok__lpg.startswith('/'):
            btok__lpg = btok__lpg[1:]
        pciim__lhl = btok__lpg.split('/')
        if len(pciim__lhl) == 2:
            lcr__vqfgn, schema = pciim__lhl
        elif len(pciim__lhl) == 1:
            lcr__vqfgn = pciim__lhl[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        opsl__aut['database'] = lcr__vqfgn
        if schema:
            opsl__aut['schema'] = schema
    if ncerk__heh.query:
        for tichb__zlf, gqxhf__aiq in parse_qsl(ncerk__heh.query):
            opsl__aut[tichb__zlf] = gqxhf__aiq
            if tichb__zlf == 'session_parameters':
                opsl__aut[tichb__zlf] = json.loads(gqxhf__aiq)
    opsl__aut['application'] = 'bodo'
    return opsl__aut


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for wnhok__thk in batches:
            wnhok__thk._bodo_num_rows = wnhok__thk.rowcount
            self._bodo_total_rows += wnhok__thk._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    jaaz__zfi = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    thp__hsgpk = MPI.COMM_WORLD
    fez__aap = tracing.Event('snowflake_connect', is_parallel=False)
    omre__wvigk = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**omre__wvigk)
    fez__aap.finalize()
    if bodo.get_rank() == 0:
        hndlw__cpbg = conn.cursor()
        byefq__oqau = tracing.Event('get_schema', is_parallel=False)
        ausqh__vpmax = f'select * from ({query}) x LIMIT {100}'
        vic__bbtwa = hndlw__cpbg.execute(ausqh__vpmax).fetch_arrow_all()
        if vic__bbtwa is None:
            ewrs__beqzf = hndlw__cpbg.describe(query)
            hgpfd__tvuer = [pa.field(rkdy__yfx.name, FIELD_TYPE_TO_PA_TYPE[
                rkdy__yfx.type_code]) for rkdy__yfx in ewrs__beqzf]
            schema = pa.schema(hgpfd__tvuer)
        else:
            schema = vic__bbtwa.schema
        byefq__oqau.finalize()
        vzr__pitih = tracing.Event('execute_query', is_parallel=False)
        hndlw__cpbg.execute(query)
        vzr__pitih.finalize()
        batches = hndlw__cpbg.get_result_batches()
        thp__hsgpk.bcast((batches, schema))
    else:
        batches, schema = thp__hsgpk.bcast(None)
    kmeg__zgh = SnowflakeDataset(batches, schema, conn)
    jaaz__zfi.finalize()
    return kmeg__zgh
