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
    zplxh__wwg = urlparse(conn_str)
    omiw__sqcc = {}
    if zplxh__wwg.username:
        omiw__sqcc['user'] = zplxh__wwg.username
    if zplxh__wwg.password:
        omiw__sqcc['password'] = zplxh__wwg.password
    if zplxh__wwg.hostname:
        omiw__sqcc['account'] = zplxh__wwg.hostname
    if zplxh__wwg.port:
        omiw__sqcc['port'] = zplxh__wwg.port
    if zplxh__wwg.path:
        hcy__ukung = zplxh__wwg.path
        if hcy__ukung.startswith('/'):
            hcy__ukung = hcy__ukung[1:]
        lvjp__qgwgl = hcy__ukung.split('/')
        if len(lvjp__qgwgl) == 2:
            rkfy__ovzb, schema = lvjp__qgwgl
        elif len(lvjp__qgwgl) == 1:
            rkfy__ovzb = lvjp__qgwgl[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        omiw__sqcc['database'] = rkfy__ovzb
        if schema:
            omiw__sqcc['schema'] = schema
    if zplxh__wwg.query:
        for hfbka__uteyw, qinyl__oumrz in parse_qsl(zplxh__wwg.query):
            omiw__sqcc[hfbka__uteyw] = qinyl__oumrz
            if hfbka__uteyw == 'session_parameters':
                omiw__sqcc[hfbka__uteyw] = json.loads(qinyl__oumrz)
    omiw__sqcc['application'] = 'bodo'
    return omiw__sqcc


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for cbei__cpc in batches:
            cbei__cpc._bodo_num_rows = cbei__cpc.rowcount
            self._bodo_total_rows += cbei__cpc._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    eemuf__dzrng = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    qyfbb__ecxes = MPI.COMM_WORLD
    frd__kog = tracing.Event('snowflake_connect', is_parallel=False)
    dxwgv__boal = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**dxwgv__boal)
    frd__kog.finalize()
    if bodo.get_rank() == 0:
        ogup__kzzd = conn.cursor()
        eurui__uau = tracing.Event('get_schema', is_parallel=False)
        gapo__lge = f'select * from ({query}) x LIMIT {100}'
        tsc__hgjn = ogup__kzzd.execute(gapo__lge).fetch_arrow_all()
        if tsc__hgjn is None:
            xza__lsy = ogup__kzzd.describe(query)
            ahzv__ljjtw = [pa.field(gzq__hao.name, FIELD_TYPE_TO_PA_TYPE[
                gzq__hao.type_code]) for gzq__hao in xza__lsy]
            schema = pa.schema(ahzv__ljjtw)
        else:
            schema = tsc__hgjn.schema
        eurui__uau.finalize()
        vugd__drrv = tracing.Event('execute_query', is_parallel=False)
        ogup__kzzd.execute(query)
        vugd__drrv.finalize()
        batches = ogup__kzzd.get_result_batches()
        qyfbb__ecxes.bcast((batches, schema))
    else:
        batches, schema = qyfbb__ecxes.bcast(None)
    tomy__vlxp = SnowflakeDataset(batches, schema, conn)
    eemuf__dzrng.finalize()
    return tomy__vlxp
