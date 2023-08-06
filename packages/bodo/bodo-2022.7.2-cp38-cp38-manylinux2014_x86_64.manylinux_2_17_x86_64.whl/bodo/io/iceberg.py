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
    mhe__mvvl = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and mhe__mvvl.scheme not in (
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
    crju__sewd = schema
    for scpqe__nft in range(len(schema)):
        brrxb__tfch = schema.field(scpqe__nft)
        if pa.types.is_floating(brrxb__tfch.type):
            crju__sewd = crju__sewd.set(scpqe__nft, brrxb__tfch.
                with_nullable(False))
        elif pa.types.is_list(brrxb__tfch.type):
            crju__sewd = crju__sewd.set(scpqe__nft, brrxb__tfch.with_type(
                pa.list_(pa.field('element', brrxb__tfch.type.value_type))))
    return crju__sewd


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    mys__vrgt = _clean_schema(schema)
    qgg__zmew = _clean_schema(other)
    return mys__vrgt.equals(qgg__zmew)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    qyq__ngp = None
    fhuly__ccss = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            qyq__ngp, fhuly__ccss, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as bphy__volj:
            if isinstance(bphy__volj, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                qyq__ngp = BodoError(
                    f'{bphy__volj.message}: {bphy__volj.java_error}')
            else:
                qyq__ngp = BodoError(bphy__volj.message)
    ftx__qqur = MPI.COMM_WORLD
    qyq__ngp = ftx__qqur.bcast(qyq__ngp)
    if isinstance(qyq__ngp, Exception):
        raise qyq__ngp
    col_names = qyq__ngp
    fhuly__ccss = ftx__qqur.bcast(fhuly__ccss)
    pyarrow_schema = ftx__qqur.bcast(pyarrow_schema)
    mklu__znlvh = [_get_numba_typ_from_pa_typ(bhmlh__auve, False, True,
        None)[0] for bhmlh__auve in fhuly__ccss]
    return col_names, mklu__znlvh, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        nplk__jbo = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as bphy__volj:
        if isinstance(bphy__volj, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{bphy__volj.message}:\n{bphy__volj.java_error}')
        else:
            raise BodoError(bphy__volj.message)
    return nplk__jbo


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
    mybf__azjpe = tracing.Event('get_iceberg_pq_dataset')
    ftx__qqur = MPI.COMM_WORLD
    vyhzh__witvt = []
    if bodo.get_rank() == 0:
        rpwwa__ssw = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            vyhzh__witvt = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                tqk__nhpev = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                rpwwa__ssw.add_attribute('num_files', len(vyhzh__witvt))
                rpwwa__ssw.add_attribute(f'first_{tqk__nhpev}_files', ', '.
                    join(vyhzh__witvt[:tqk__nhpev]))
        except Exception as bphy__volj:
            vyhzh__witvt = bphy__volj
        rpwwa__ssw.finalize()
    vyhzh__witvt = ftx__qqur.bcast(vyhzh__witvt)
    if isinstance(vyhzh__witvt, Exception):
        mdm__wvwn = vyhzh__witvt
        raise BodoError(
            f"""Error reading Iceberg Table: {type(mdm__wvwn).__name__}: {str(mdm__wvwn)}
"""
            )
    uxvmo__kcvf: List[str] = vyhzh__witvt
    if len(uxvmo__kcvf) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(uxvmo__kcvf,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as bphy__volj:
            if re.search('Schema .* was different', str(bphy__volj), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{bphy__volj}"""
                    )
            else:
                raise
    ivza__stf = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    mybf__azjpe.finalize()
    return ivza__stf


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        frrx__btdt = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        wrt__jbzpx = []
        for jaw__tyxv, eith__nry in zip(numba_type.names, numba_type.data):
            wmp__cbxwj, iks__dpce = _numba_to_pyarrow_type(eith__nry)
            wrt__jbzpx.append(pa.field(jaw__tyxv, wmp__cbxwj, True))
        frrx__btdt = pa.struct(wrt__jbzpx)
    elif isinstance(numba_type, DecimalArrayType):
        frrx__btdt = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        alkp__gqt: PDCategoricalDtype = numba_type.dtype
        frrx__btdt = pa.dictionary(_numba_to_pyarrow_type(alkp__gqt.
            int_type)[0], _numba_to_pyarrow_type(alkp__gqt.elem_type)[0],
            ordered=False if alkp__gqt.ordered is None else alkp__gqt.ordered)
    elif numba_type == boolean_array:
        frrx__btdt = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        frrx__btdt = pa.string()
    elif numba_type == binary_array_type:
        frrx__btdt = pa.binary()
    elif numba_type == datetime_date_array_type:
        frrx__btdt = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        frrx__btdt = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        frrx__btdt = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return frrx__btdt, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    wrt__jbzpx = []
    for jaw__tyxv, wkhay__mlcod in zip(df.columns, df.data):
        try:
            bddi__tcz, spxmi__kpap = _numba_to_pyarrow_type(wkhay__mlcod)
        except BodoError as bphy__volj:
            raise_bodo_error(bphy__volj.msg, bphy__volj.loc)
        wrt__jbzpx.append(pa.field(jaw__tyxv, bddi__tcz, spxmi__kpap))
    return pa.schema(wrt__jbzpx)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        ftx__qqur = MPI.COMM_WORLD
        jsxv__hsq = ftx__qqur.Get_rank()
        file_name = f'{jsxv__hsq:05}-{jsxv__hsq}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    ftx__qqur = MPI.COMM_WORLD
    khtpp__kgoh = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if ftx__qqur.Get_rank() == 0:
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
        except connector.IcebergError as bphy__volj:
            if isinstance(bphy__volj, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                khtpp__kgoh = BodoError(
                    f'{bphy__volj.message}: {bphy__volj.java_error}')
            else:
                khtpp__kgoh = BodoError(bphy__volj.message)
        except Exception as bphy__volj:
            khtpp__kgoh = bphy__volj
    khtpp__kgoh = ftx__qqur.bcast(khtpp__kgoh)
    if isinstance(khtpp__kgoh, Exception):
        raise khtpp__kgoh
    table_loc = ftx__qqur.bcast(table_loc)
    iceberg_schema_id = ftx__qqur.bcast(iceberg_schema_id)
    partition_spec = ftx__qqur.bcast(partition_spec)
    sort_order = ftx__qqur.bcast(sort_order)
    iceberg_schema_str = ftx__qqur.bcast(iceberg_schema_str)
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
    ftx__qqur = MPI.COMM_WORLD
    success = False
    if ftx__qqur.Get_rank() == 0:
        iltiy__hft = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, iltiy__hft,
            pa_schema, partition_spec, sort_order, mode)
    success = ftx__qqur.bcast(success)
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
    dspv__bgumd = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    xic__hbw = 'snappy'
    wist__ibci = -1
    lnm__eqg = np.zeros(1, dtype=np.int64)
    hjk__tkatt = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(dspv__bgumd),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(xic__hbw), is_parallel, unicode_to_utf8(
            bucket_region), wist__ibci, unicode_to_utf8(iceberg_schema_str),
            lnm__eqg.ctypes, hjk__tkatt.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        ftx__qqur = MPI.COMM_WORLD
        fnames = ftx__qqur.gather(dspv__bgumd)
        if ftx__qqur.Get_rank() != 0:
            fnames = ['a', 'b']
    nuvp__ozm = bodo.gatherv(lnm__eqg)
    toi__gna = bodo.gatherv(hjk__tkatt)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': toi__gna.tolist(), 'record_count':
            nuvp__ozm.tolist()}, iceberg_schema_id, df_pyarrow_schema,
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
        atlwe__ble = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        rua__aulo = cgutils.get_or_insert_function(builder.module,
            atlwe__ble, name='iceberg_pq_write')
        builder.call(rua__aulo, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
