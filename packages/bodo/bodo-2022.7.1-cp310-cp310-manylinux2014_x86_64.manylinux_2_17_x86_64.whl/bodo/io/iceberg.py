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
    pvlc__nxt = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and pvlc__nxt.scheme not in (
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
    adije__ztntj = schema
    for ystg__jhb in range(len(schema)):
        xuv__cjoz = schema.field(ystg__jhb)
        if pa.types.is_floating(xuv__cjoz.type):
            adije__ztntj = adije__ztntj.set(ystg__jhb, xuv__cjoz.
                with_nullable(False))
        elif pa.types.is_list(xuv__cjoz.type):
            adije__ztntj = adije__ztntj.set(ystg__jhb, xuv__cjoz.with_type(
                pa.list_(pa.field('element', xuv__cjoz.type.value_type))))
    return adije__ztntj


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    scc__btjrt = _clean_schema(schema)
    hbg__dmlvo = _clean_schema(other)
    return scc__btjrt.equals(hbg__dmlvo)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    pdosl__suz = None
    qge__zwsy = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            pdosl__suz, qge__zwsy, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as kcibp__krynu:
            if isinstance(kcibp__krynu, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                pdosl__suz = BodoError(
                    f'{kcibp__krynu.message}: {kcibp__krynu.java_error}')
            else:
                pdosl__suz = BodoError(kcibp__krynu.message)
    rjw__hjd = MPI.COMM_WORLD
    pdosl__suz = rjw__hjd.bcast(pdosl__suz)
    if isinstance(pdosl__suz, Exception):
        raise pdosl__suz
    col_names = pdosl__suz
    qge__zwsy = rjw__hjd.bcast(qge__zwsy)
    pyarrow_schema = rjw__hjd.bcast(pyarrow_schema)
    wxpw__yjv = [_get_numba_typ_from_pa_typ(aon__blmz, False, True, None)[0
        ] for aon__blmz in qge__zwsy]
    return col_names, wxpw__yjv, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        wvbsk__rjek = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as kcibp__krynu:
        if isinstance(kcibp__krynu, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(
                f'{kcibp__krynu.message}:\n{kcibp__krynu.java_error}')
        else:
            raise BodoError(kcibp__krynu.message)
    return wvbsk__rjek


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
    yae__khi = tracing.Event('get_iceberg_pq_dataset')
    rjw__hjd = MPI.COMM_WORLD
    ulr__qbgcb = []
    if bodo.get_rank() == 0:
        kvr__tukp = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            ulr__qbgcb = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                foua__ebe = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                kvr__tukp.add_attribute('num_files', len(ulr__qbgcb))
                kvr__tukp.add_attribute(f'first_{foua__ebe}_files', ', '.
                    join(ulr__qbgcb[:foua__ebe]))
        except Exception as kcibp__krynu:
            ulr__qbgcb = kcibp__krynu
        kvr__tukp.finalize()
    ulr__qbgcb = rjw__hjd.bcast(ulr__qbgcb)
    if isinstance(ulr__qbgcb, Exception):
        wxmt__vhbh = ulr__qbgcb
        raise BodoError(
            f"""Error reading Iceberg Table: {type(wxmt__vhbh).__name__}: {str(wxmt__vhbh)}
"""
            )
    jlzcl__qafh: List[str] = ulr__qbgcb
    if len(jlzcl__qafh) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(jlzcl__qafh,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as kcibp__krynu:
            if re.search('Schema .* was different', str(kcibp__krynu), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{kcibp__krynu}"""
                    )
            else:
                raise
    vxb__ecu = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    yae__khi.finalize()
    return vxb__ecu


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        grefg__ymbfr = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        zoe__hph = []
        for iki__ggdlw, drf__ivk in zip(numba_type.names, numba_type.data):
            euuu__rsbgl, jvn__ejzrx = _numba_to_pyarrow_type(drf__ivk)
            zoe__hph.append(pa.field(iki__ggdlw, euuu__rsbgl, True))
        grefg__ymbfr = pa.struct(zoe__hph)
    elif isinstance(numba_type, DecimalArrayType):
        grefg__ymbfr = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        mplne__ego: PDCategoricalDtype = numba_type.dtype
        grefg__ymbfr = pa.dictionary(_numba_to_pyarrow_type(mplne__ego.
            int_type)[0], _numba_to_pyarrow_type(mplne__ego.elem_type)[0],
            ordered=False if mplne__ego.ordered is None else mplne__ego.ordered
            )
    elif numba_type == boolean_array:
        grefg__ymbfr = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        grefg__ymbfr = pa.string()
    elif numba_type == binary_array_type:
        grefg__ymbfr = pa.binary()
    elif numba_type == datetime_date_array_type:
        grefg__ymbfr = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        grefg__ymbfr = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        grefg__ymbfr = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return grefg__ymbfr, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    zoe__hph = []
    for iki__ggdlw, oeat__aang in zip(df.columns, df.data):
        try:
            oustg__pqwg, rnj__gvfaa = _numba_to_pyarrow_type(oeat__aang)
        except BodoError as kcibp__krynu:
            raise_bodo_error(kcibp__krynu.msg, kcibp__krynu.loc)
        zoe__hph.append(pa.field(iki__ggdlw, oustg__pqwg, rnj__gvfaa))
    return pa.schema(zoe__hph)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        rjw__hjd = MPI.COMM_WORLD
        vigx__zokyy = rjw__hjd.Get_rank()
        file_name = f'{vigx__zokyy:05}-{vigx__zokyy}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    rjw__hjd = MPI.COMM_WORLD
    bnw__icost = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if rjw__hjd.Get_rank() == 0:
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
        except connector.IcebergError as kcibp__krynu:
            if isinstance(kcibp__krynu, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                bnw__icost = BodoError(
                    f'{kcibp__krynu.message}: {kcibp__krynu.java_error}')
            else:
                bnw__icost = BodoError(kcibp__krynu.message)
        except Exception as kcibp__krynu:
            bnw__icost = kcibp__krynu
    bnw__icost = rjw__hjd.bcast(bnw__icost)
    if isinstance(bnw__icost, Exception):
        raise bnw__icost
    table_loc = rjw__hjd.bcast(table_loc)
    iceberg_schema_id = rjw__hjd.bcast(iceberg_schema_id)
    partition_spec = rjw__hjd.bcast(partition_spec)
    sort_order = rjw__hjd.bcast(sort_order)
    iceberg_schema_str = rjw__hjd.bcast(iceberg_schema_str)
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
    rjw__hjd = MPI.COMM_WORLD
    success = False
    if rjw__hjd.Get_rank() == 0:
        lykbg__lmjk = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, lykbg__lmjk,
            pa_schema, partition_spec, sort_order, mode)
    success = rjw__hjd.bcast(success)
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
    izt__hwqu = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    hvkz__uxr = 'snappy'
    cwxci__pcc = -1
    cehmt__ban = np.zeros(1, dtype=np.int64)
    cwm__abli = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(izt__hwqu),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(hvkz__uxr), is_parallel, unicode_to_utf8(
            bucket_region), cwxci__pcc, unicode_to_utf8(iceberg_schema_str),
            cehmt__ban.ctypes, cwm__abli.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        rjw__hjd = MPI.COMM_WORLD
        fnames = rjw__hjd.gather(izt__hwqu)
        if rjw__hjd.Get_rank() != 0:
            fnames = ['a', 'b']
    ddsmk__bhi = bodo.gatherv(cehmt__ban)
    jzb__cdshb = bodo.gatherv(cwm__abli)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': jzb__cdshb.tolist(), 'record_count':
            ddsmk__bhi.tolist()}, iceberg_schema_id, df_pyarrow_schema,
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
        ugyjw__pgpb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        uxzme__gzs = cgutils.get_or_insert_function(builder.module,
            ugyjw__pgpb, name='iceberg_pq_write')
        builder.call(uxzme__gzs, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
