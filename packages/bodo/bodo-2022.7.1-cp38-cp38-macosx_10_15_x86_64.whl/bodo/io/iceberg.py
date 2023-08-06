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
    phedp__vvh = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and phedp__vvh.scheme not in (
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
    zwmr__ewi = schema
    for yejs__rryk in range(len(schema)):
        iaey__almd = schema.field(yejs__rryk)
        if pa.types.is_floating(iaey__almd.type):
            zwmr__ewi = zwmr__ewi.set(yejs__rryk, iaey__almd.with_nullable(
                False))
        elif pa.types.is_list(iaey__almd.type):
            zwmr__ewi = zwmr__ewi.set(yejs__rryk, iaey__almd.with_type(pa.
                list_(pa.field('element', iaey__almd.type.value_type))))
    return zwmr__ewi


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    mwt__pnu = _clean_schema(schema)
    zgjz__mfhhd = _clean_schema(other)
    return mwt__pnu.equals(zgjz__mfhhd)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    dsrth__votr = None
    yva__jpfn = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            dsrth__votr, yva__jpfn, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as gzk__knu:
            if isinstance(gzk__knu, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                dsrth__votr = BodoError(
                    f'{gzk__knu.message}: {gzk__knu.java_error}')
            else:
                dsrth__votr = BodoError(gzk__knu.message)
    kao__dfuy = MPI.COMM_WORLD
    dsrth__votr = kao__dfuy.bcast(dsrth__votr)
    if isinstance(dsrth__votr, Exception):
        raise dsrth__votr
    col_names = dsrth__votr
    yva__jpfn = kao__dfuy.bcast(yva__jpfn)
    pyarrow_schema = kao__dfuy.bcast(pyarrow_schema)
    ehr__cqw = [_get_numba_typ_from_pa_typ(livp__efl, False, True, None)[0] for
        livp__efl in yva__jpfn]
    return col_names, ehr__cqw, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        ooap__khzrf = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as gzk__knu:
        if isinstance(gzk__knu, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{gzk__knu.message}:\n{gzk__knu.java_error}')
        else:
            raise BodoError(gzk__knu.message)
    return ooap__khzrf


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
    cqiw__jwm = tracing.Event('get_iceberg_pq_dataset')
    kao__dfuy = MPI.COMM_WORLD
    mcf__xipcg = []
    if bodo.get_rank() == 0:
        gbsc__turar = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            mcf__xipcg = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                xsx__wtnx = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                gbsc__turar.add_attribute('num_files', len(mcf__xipcg))
                gbsc__turar.add_attribute(f'first_{xsx__wtnx}_files', ', '.
                    join(mcf__xipcg[:xsx__wtnx]))
        except Exception as gzk__knu:
            mcf__xipcg = gzk__knu
        gbsc__turar.finalize()
    mcf__xipcg = kao__dfuy.bcast(mcf__xipcg)
    if isinstance(mcf__xipcg, Exception):
        bzfn__wyyi = mcf__xipcg
        raise BodoError(
            f"""Error reading Iceberg Table: {type(bzfn__wyyi).__name__}: {str(bzfn__wyyi)}
"""
            )
    gwxuq__wfxu: List[str] = mcf__xipcg
    if len(gwxuq__wfxu) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(gwxuq__wfxu,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as gzk__knu:
            if re.search('Schema .* was different', str(gzk__knu), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{gzk__knu}"""
                    )
            else:
                raise
    tkzig__qcpy = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    cqiw__jwm.finalize()
    return tkzig__qcpy


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        tkg__cun = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        uhagp__qolq = []
        for zylyp__fnjzb, ius__tkvh in zip(numba_type.names, numba_type.data):
            rst__vkq, fneqh__moln = _numba_to_pyarrow_type(ius__tkvh)
            uhagp__qolq.append(pa.field(zylyp__fnjzb, rst__vkq, True))
        tkg__cun = pa.struct(uhagp__qolq)
    elif isinstance(numba_type, DecimalArrayType):
        tkg__cun = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        oxcne__cbjb: PDCategoricalDtype = numba_type.dtype
        tkg__cun = pa.dictionary(_numba_to_pyarrow_type(oxcne__cbjb.
            int_type)[0], _numba_to_pyarrow_type(oxcne__cbjb.elem_type)[0],
            ordered=False if oxcne__cbjb.ordered is None else oxcne__cbjb.
            ordered)
    elif numba_type == boolean_array:
        tkg__cun = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        tkg__cun = pa.string()
    elif numba_type == binary_array_type:
        tkg__cun = pa.binary()
    elif numba_type == datetime_date_array_type:
        tkg__cun = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        tkg__cun = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        tkg__cun = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return tkg__cun, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    uhagp__qolq = []
    for zylyp__fnjzb, sfgq__iesqj in zip(df.columns, df.data):
        try:
            hof__vwxyl, sosnf__rrac = _numba_to_pyarrow_type(sfgq__iesqj)
        except BodoError as gzk__knu:
            raise_bodo_error(gzk__knu.msg, gzk__knu.loc)
        uhagp__qolq.append(pa.field(zylyp__fnjzb, hof__vwxyl, sosnf__rrac))
    return pa.schema(uhagp__qolq)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        kao__dfuy = MPI.COMM_WORLD
        xmw__jvz = kao__dfuy.Get_rank()
        file_name = f'{xmw__jvz:05}-{xmw__jvz}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    kao__dfuy = MPI.COMM_WORLD
    nwv__uvprc = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if kao__dfuy.Get_rank() == 0:
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
        except connector.IcebergError as gzk__knu:
            if isinstance(gzk__knu, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                nwv__uvprc = BodoError(
                    f'{gzk__knu.message}: {gzk__knu.java_error}')
            else:
                nwv__uvprc = BodoError(gzk__knu.message)
        except Exception as gzk__knu:
            nwv__uvprc = gzk__knu
    nwv__uvprc = kao__dfuy.bcast(nwv__uvprc)
    if isinstance(nwv__uvprc, Exception):
        raise nwv__uvprc
    table_loc = kao__dfuy.bcast(table_loc)
    iceberg_schema_id = kao__dfuy.bcast(iceberg_schema_id)
    partition_spec = kao__dfuy.bcast(partition_spec)
    sort_order = kao__dfuy.bcast(sort_order)
    iceberg_schema_str = kao__dfuy.bcast(iceberg_schema_str)
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
    kao__dfuy = MPI.COMM_WORLD
    success = False
    if kao__dfuy.Get_rank() == 0:
        cwcai__poy = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, cwcai__poy,
            pa_schema, partition_spec, sort_order, mode)
    success = kao__dfuy.bcast(success)
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
    pudx__tswkl = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    cdru__ixv = 'snappy'
    ustv__bbpyg = -1
    fvw__pxq = np.zeros(1, dtype=np.int64)
    cdmrc__npziq = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(pudx__tswkl),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(cdru__ixv), is_parallel, unicode_to_utf8(
            bucket_region), ustv__bbpyg, unicode_to_utf8(iceberg_schema_str
            ), fvw__pxq.ctypes, cdmrc__npziq.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        kao__dfuy = MPI.COMM_WORLD
        fnames = kao__dfuy.gather(pudx__tswkl)
        if kao__dfuy.Get_rank() != 0:
            fnames = ['a', 'b']
    cbsfa__yjld = bodo.gatherv(fvw__pxq)
    lee__pax = bodo.gatherv(cdmrc__npziq)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': lee__pax.tolist(), 'record_count':
            cbsfa__yjld.tolist()}, iceberg_schema_id, df_pyarrow_schema,
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
        qflu__bzdrq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        was__hyb = cgutils.get_or_insert_function(builder.module,
            qflu__bzdrq, name='iceberg_pq_write')
        builder.call(was__hyb, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
