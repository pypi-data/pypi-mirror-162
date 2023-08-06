"""
File that contains the main functionality for the Iceberg
integration within the Bodo repo. This does not contain the
main IR transformation.
"""
import os
import re
import sys
from typing import Any, Dict, List
from urllib.parse import urlparse
from uuid import uuid4
import numba
import numpy as np
import pyarrow as pa
from mpi4py import MPI
from numba.core import types
from numba.extending import intrinsic
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.io.fs_io import get_s3_bucket_region_njit
from bodo.io.helpers import is_nullable
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils import tracing
from bodo.utils.typing import BodoError, raise_bodo_error


def format_iceberg_conn(conn_str: str) ->str:
    cftjf__gito = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and cftjf__gito.scheme not in (
        'iceberg', 'iceberg+file', 'iceberg+s3', 'iceberg+thrift',
        'iceberg+http', 'iceberg+https'):
        raise BodoError(
            "'con' must start with one of the following: 'iceberg://', 'iceberg+file://', 'iceberg+s3://', 'iceberg+thrift://', 'iceberg+http://', 'iceberg+https://', 'iceberg+glue'"
            )
    if sys.version_info.minor < 9:
        if conn_str.startswith('iceberg+'):
            conn_str = conn_str[len('iceberg+'):]
        if conn_str.startswith('iceberg://'):
            conn_str = conn_str[len('iceberg://'):]
    else:
        conn_str = conn_str.removeprefix('iceberg+').removeprefix('iceberg://')
    return conn_str


@numba.njit
def format_iceberg_conn_njit(conn_str):
    with numba.objmode(conn_str='unicode_type'):
        conn_str = format_iceberg_conn(conn_str)
    return conn_str


def _clean_schema(schema: pa.Schema) ->pa.Schema:
    vvx__zru = schema
    for yiyc__sryu in range(len(schema)):
        wpwm__grl = schema.field(yiyc__sryu)
        if pa.types.is_floating(wpwm__grl.type):
            vvx__zru = vvx__zru.set(yiyc__sryu, wpwm__grl.with_nullable(False))
        elif pa.types.is_list(wpwm__grl.type):
            vvx__zru = vvx__zru.set(yiyc__sryu, wpwm__grl.with_type(pa.
                list_(pa.field('element', wpwm__grl.type.value_type))))
    return vvx__zru


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    ckoae__vxd = _clean_schema(schema)
    vnac__pdp = _clean_schema(other)
    return ckoae__vxd.equals(vnac__pdp)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    mjj__looy = None
    ucyes__nlus = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            mjj__looy, ucyes__nlus, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as naxhq__bokzi:
            if isinstance(naxhq__bokzi, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                mjj__looy = BodoError(
                    f'{naxhq__bokzi.message}: {naxhq__bokzi.java_error}')
            else:
                mjj__looy = BodoError(naxhq__bokzi.message)
    hspfq__xqm = MPI.COMM_WORLD
    mjj__looy = hspfq__xqm.bcast(mjj__looy)
    if isinstance(mjj__looy, Exception):
        raise mjj__looy
    col_names = mjj__looy
    ucyes__nlus = hspfq__xqm.bcast(ucyes__nlus)
    pyarrow_schema = hspfq__xqm.bcast(pyarrow_schema)
    dxwxc__vmbwy = [_get_numba_typ_from_pa_typ(bph__fcg, False, True, None)
        [0] for bph__fcg in ucyes__nlus]
    return col_names, dxwxc__vmbwy, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        wiqs__rfqp = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as naxhq__bokzi:
        if isinstance(naxhq__bokzi, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(
                f'{naxhq__bokzi.message}:\n{naxhq__bokzi.java_error}')
        else:
            raise BodoError(naxhq__bokzi.message)
    return wiqs__rfqp


class IcebergParquetDataset(object):

    def __init__(self, conn, database_schema, table_name, pa_table_schema,
        pq_dataset=None):
        self.pq_dataset = pq_dataset
        self.conn = conn
        self.database_schema = database_schema
        self.table_name = table_name
        self.schema = pa_table_schema
        self.pieces = []
        self._bodo_total_rows = 0
        self._prefix = ''
        self.filesystem = None
        if pq_dataset is not None:
            self.pieces = pq_dataset.pieces
            self._bodo_total_rows = pq_dataset._bodo_total_rows
            self._prefix = pq_dataset._prefix
            self.filesystem = pq_dataset.filesystem


def get_iceberg_pq_dataset(conn, database_schema, table_name,
    typing_pa_table_schema, dnf_filters=None, expr_filters=None,
    is_parallel=False):
    pgvbs__awra = tracing.Event('get_iceberg_pq_dataset')
    hspfq__xqm = MPI.COMM_WORLD
    skvx__bgdg = []
    if bodo.get_rank() == 0:
        dcs__npl = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            skvx__bgdg = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                jqb__bwdov = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                dcs__npl.add_attribute('num_files', len(skvx__bgdg))
                dcs__npl.add_attribute(f'first_{jqb__bwdov}_files', ', '.
                    join(skvx__bgdg[:jqb__bwdov]))
        except Exception as naxhq__bokzi:
            skvx__bgdg = naxhq__bokzi
        dcs__npl.finalize()
    skvx__bgdg = hspfq__xqm.bcast(skvx__bgdg)
    if isinstance(skvx__bgdg, Exception):
        uubcm__wxajf = skvx__bgdg
        raise BodoError(
            f"""Error reading Iceberg Table: {type(uubcm__wxajf).__name__}: {str(uubcm__wxajf)}
"""
            )
    lcdlo__xpjgz: List[str] = skvx__bgdg
    if len(lcdlo__xpjgz) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(lcdlo__xpjgz,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as naxhq__bokzi:
            if re.search('Schema .* was different', str(naxhq__bokzi), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{naxhq__bokzi}"""
                    )
            else:
                raise
    nuyzh__nmjl = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    pgvbs__awra.finalize()
    return nuyzh__nmjl


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        wlwvl__vyz = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        yzzw__kqxd = []
        for nweic__lpmta, nsl__poyj in zip(numba_type.names, numba_type.data):
            ovr__czwi, ywvbc__kihnf = _numba_to_pyarrow_type(nsl__poyj)
            yzzw__kqxd.append(pa.field(nweic__lpmta, ovr__czwi, True))
        wlwvl__vyz = pa.struct(yzzw__kqxd)
    elif isinstance(numba_type, DecimalArrayType):
        wlwvl__vyz = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        upcop__moj: PDCategoricalDtype = numba_type.dtype
        wlwvl__vyz = pa.dictionary(_numba_to_pyarrow_type(upcop__moj.
            int_type)[0], _numba_to_pyarrow_type(upcop__moj.elem_type)[0],
            ordered=False if upcop__moj.ordered is None else upcop__moj.ordered
            )
    elif numba_type == boolean_array:
        wlwvl__vyz = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        wlwvl__vyz = pa.string()
    elif numba_type == binary_array_type:
        wlwvl__vyz = pa.binary()
    elif numba_type == datetime_date_array_type:
        wlwvl__vyz = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        wlwvl__vyz = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        wlwvl__vyz = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return wlwvl__vyz, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    yzzw__kqxd = []
    for nweic__lpmta, tnuvc__fwcw in zip(df.columns, df.data):
        try:
            nxkv__unl, zkpax__xio = _numba_to_pyarrow_type(tnuvc__fwcw)
        except BodoError as naxhq__bokzi:
            raise_bodo_error(naxhq__bokzi.msg, naxhq__bokzi.loc)
        yzzw__kqxd.append(pa.field(nweic__lpmta, nxkv__unl, zkpax__xio))
    return pa.schema(yzzw__kqxd)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        hspfq__xqm = MPI.COMM_WORLD
        lcm__jvtdn = hspfq__xqm.Get_rank()
        file_name = f'{lcm__jvtdn:05}-{lcm__jvtdn}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    hspfq__xqm = MPI.COMM_WORLD
    fetp__rrfs = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if hspfq__xqm.Get_rank() == 0:
        try:
            (table_loc, iceberg_schema_id, pa_schema, iceberg_schema_str,
                partition_spec, sort_order) = (connector.get_typing_info(
                conn, database_schema, table_name))
            if (if_exists == 'append' and pa_schema is not None and not
                _schemas_equal(pa_schema, df_pyarrow_schema)):
                if numba.core.config.DEVELOPER_MODE:
                    raise BodoError(
                        f"""Iceberg Table and DataFrame Schemas Need to be Equal for Append

Iceberg:
{pa_schema}

DataFrame:
{df_pyarrow_schema}
"""
                        )
                else:
                    raise BodoError(
                        'Iceberg Table and DataFrame Schemas Need to be Equal for Append'
                        )
            if iceberg_schema_id is None:
                iceberg_schema_str = connector.pyarrow_to_iceberg_schema_str(
                    df_pyarrow_schema)
        except connector.IcebergError as naxhq__bokzi:
            if isinstance(naxhq__bokzi, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                fetp__rrfs = BodoError(
                    f'{naxhq__bokzi.message}: {naxhq__bokzi.java_error}')
            else:
                fetp__rrfs = BodoError(naxhq__bokzi.message)
        except Exception as naxhq__bokzi:
            fetp__rrfs = naxhq__bokzi
    fetp__rrfs = hspfq__xqm.bcast(fetp__rrfs)
    if isinstance(fetp__rrfs, Exception):
        raise fetp__rrfs
    table_loc = hspfq__xqm.bcast(table_loc)
    iceberg_schema_id = hspfq__xqm.bcast(iceberg_schema_id)
    partition_spec = hspfq__xqm.bcast(partition_spec)
    sort_order = hspfq__xqm.bcast(sort_order)
    iceberg_schema_str = hspfq__xqm.bcast(iceberg_schema_str)
    if iceberg_schema_id is None:
        already_exists = False
        iceberg_schema_id = -1
    else:
        already_exists = True
    return (already_exists, table_loc, iceberg_schema_id, partition_spec,
        sort_order, iceberg_schema_str)


def register_table_write(conn_str: str, db_name: str, table_name: str,
    table_loc: str, fnames: List[str], all_metrics: Dict[str, List[Any]],
    iceberg_schema_id: int, pa_schema, partition_spec, sort_order, mode: str):
    import bodo_iceberg_connector
    hspfq__xqm = MPI.COMM_WORLD
    success = False
    if hspfq__xqm.Get_rank() == 0:
        mieg__ajux = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, mieg__ajux,
            pa_schema, partition_spec, sort_order, mode)
    success = hspfq__xqm.bcast(success)
    return success


@numba.njit()
def iceberg_write(table_name, conn, database_schema, bodo_table, col_names,
    if_exists, is_parallel, df_pyarrow_schema):
    assert is_parallel, 'Iceberg Write only supported for distributed dataframes'
    with numba.objmode(already_exists='bool_', table_loc='unicode_type',
        iceberg_schema_id='i8', partition_spec='unicode_type', sort_order=
        'unicode_type', iceberg_schema_str='unicode_type'):
        (already_exists, table_loc, iceberg_schema_id, partition_spec,
            sort_order, iceberg_schema_str) = (get_table_details_before_write
            (table_name, conn, database_schema, df_pyarrow_schema, if_exists))
    if already_exists and if_exists == 'fail':
        raise ValueError(f'Table already exists.')
    if already_exists:
        mode = if_exists
    else:
        mode = 'create'
    zclgb__tmgz = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    cktb__hxi = 'snappy'
    loeeo__ilbw = -1
    cuwwk__sro = np.zeros(1, dtype=np.int64)
    mmr__vsj = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(zclgb__tmgz),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(cktb__hxi), is_parallel, unicode_to_utf8(
            bucket_region), loeeo__ilbw, unicode_to_utf8(iceberg_schema_str
            ), cuwwk__sro.ctypes, mmr__vsj.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        hspfq__xqm = MPI.COMM_WORLD
        fnames = hspfq__xqm.gather(zclgb__tmgz)
        if hspfq__xqm.Get_rank() != 0:
            fnames = ['a', 'b']
    pqpa__mdsnh = bodo.gatherv(cuwwk__sro)
    elwh__jwu = bodo.gatherv(mmr__vsj)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': elwh__jwu.tolist(), 'record_count':
            pqpa__mdsnh.tolist()}, iceberg_schema_id, df_pyarrow_schema,
            partition_spec, sort_order, mode)
    if not success:
        raise BodoError('Iceberg write failed.')


import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('iceberg_pq_write', arrow_cpp.iceberg_pq_write)


@intrinsic
def iceberg_pq_write_table_cpp(typingctx, fname_t, path_name_t, table_t,
    col_names_t, compression_t, is_parallel_t, bucket_region,
    row_group_size, iceberg_metadata_t, record_count_t, file_size_in_bytes_t):

    def codegen(context, builder, sig, args):
        whn__kquvs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        jraxd__ngegt = cgutils.get_or_insert_function(builder.module,
            whn__kquvs, name='iceberg_pq_write')
        builder.call(jraxd__ngegt, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
