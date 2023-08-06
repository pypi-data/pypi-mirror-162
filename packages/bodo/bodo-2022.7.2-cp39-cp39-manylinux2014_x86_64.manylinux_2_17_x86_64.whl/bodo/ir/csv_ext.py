from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
from numba.extending import intrinsic
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import Table, TableType
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import check_and_propagate_cpp_exception, sanitize_varname


class CsvReader(ir.Stmt):

    def __init__(self, file_name, df_out, sep, df_colnames, out_vars,
        out_types, usecols, loc, header, compression, nrows, skiprows,
        chunksize, is_skiprows_list, low_memory, escapechar,
        storage_options=None, index_column_index=None, index_column_typ=
        types.none):
        self.connector_typ = 'csv'
        self.file_name = file_name
        self.df_out = df_out
        self.sep = sep
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.usecols = usecols
        self.loc = loc
        self.skiprows = skiprows
        self.nrows = nrows
        self.header = header
        self.compression = compression
        self.chunksize = chunksize
        self.is_skiprows_list = is_skiprows_list
        self.pd_low_memory = low_memory
        self.escapechar = escapechar
        self.storage_options = storage_options
        self.index_column_index = index_column_index
        self.index_column_typ = index_column_typ
        self.out_used_cols = list(range(len(usecols)))

    def __repr__(self):
        return (
            '{} = ReadCsv(file={}, col_names={}, types={}, vars={}, nrows={}, skiprows={}, chunksize={}, is_skiprows_list={}, pd_low_memory={}, escapechar={}, storage_options={}, index_column_index={}, index_colum_typ = {}, out_used_colss={})'
            .format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars, self.nrows, self.skiprows, self.
            chunksize, self.is_skiprows_list, self.pd_low_memory, self.
            escapechar, self.storage_options, self.index_column_index, self
            .index_column_typ, self.out_used_cols))


def check_node_typing(node, typemap):
    lkun__edtvx = typemap[node.file_name.name]
    if types.unliteral(lkun__edtvx) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {lkun__edtvx}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        depe__nbkn = typemap[node.skiprows.name]
        if isinstance(depe__nbkn, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(depe__nbkn, types.Integer) and not (isinstance(
            depe__nbkn, (types.List, types.Tuple)) and isinstance(
            depe__nbkn.dtype, types.Integer)) and not isinstance(depe__nbkn,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {depe__nbkn}."
                , loc=node.skiprows.loc)
        elif isinstance(depe__nbkn, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        zvp__adwts = typemap[node.nrows.name]
        if not isinstance(zvp__adwts, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {zvp__adwts}."
                , loc=node.nrows.loc)


import llvmlite.binding as ll
from bodo.io import csv_cpp
ll.add_symbol('csv_file_chunk_reader', csv_cpp.csv_file_chunk_reader)


@intrinsic
def csv_file_chunk_reader(typingctx, fname_t, is_parallel_t, skiprows_t,
    nrows_t, header_t, compression_t, bucket_region_t, storage_options_t,
    chunksize_t, is_skiprows_list_t, skiprows_list_len_t, pd_low_memory_t):
    assert storage_options_t == storage_options_dict_type, "Storage options don't match expected type"

    def codegen(context, builder, sig, args):
        lboz__twg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        jtwy__cwepp = cgutils.get_or_insert_function(builder.module,
            lboz__twg, name='csv_file_chunk_reader')
        kzvw__msjtf = builder.call(jtwy__cwepp, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        fqb__nrcw = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        ylpo__cpgia = context.get_python_api(builder)
        fqb__nrcw.meminfo = ylpo__cpgia.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), kzvw__msjtf)
        fqb__nrcw.pyobj = kzvw__msjtf
        ylpo__cpgia.decref(kzvw__msjtf)
        return fqb__nrcw._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        rfrhh__lna = csv_node.out_vars[0]
        if rfrhh__lna.name not in lives:
            return None
    else:
        ngu__wdeq = csv_node.out_vars[0]
        txlsf__ywixb = csv_node.out_vars[1]
        if ngu__wdeq.name not in lives and txlsf__ywixb.name not in lives:
            return None
        elif txlsf__ywixb.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif ngu__wdeq.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    depe__nbkn = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            qdazi__rlvmu = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            xxpu__nau = csv_node.loc.strformat()
            jlyp__gnz = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', qdazi__rlvmu,
                xxpu__nau, jlyp__gnz)
            uenz__cbp = csv_node.out_types[0].yield_type.data
            tini__zxjzx = [hhyoz__frxm for paj__bpuk, hhyoz__frxm in
                enumerate(csv_node.df_colnames) if isinstance(uenz__cbp[
                paj__bpuk], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if tini__zxjzx:
                ssv__mko = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    ssv__mko, xxpu__nau, tini__zxjzx)
        if array_dists is not None:
            bzixg__bakh = csv_node.out_vars[0].name
            parallel = array_dists[bzixg__bakh] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        iezo__ypb = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        iezo__ypb += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        iezo__ypb += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        etub__dqa = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(iezo__ypb, {}, etub__dqa)
        uhtls__onyam = etub__dqa['csv_iterator_impl']
        hxxe__aorh = 'def csv_reader_init(fname, nrows, skiprows):\n'
        hxxe__aorh += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        hxxe__aorh += '  return f_reader\n'
        exec(hxxe__aorh, globals(), etub__dqa)
        aoogz__ysmn = etub__dqa['csv_reader_init']
        iwhzb__kdmyb = numba.njit(aoogz__ysmn)
        compiled_funcs.append(iwhzb__kdmyb)
        eob__xeii = compile_to_numba_ir(uhtls__onyam, {'_csv_reader_init':
            iwhzb__kdmyb, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, depe__nbkn), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(eob__xeii, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        bitd__ebf = eob__xeii.body[:-3]
        bitd__ebf[-1].target = csv_node.out_vars[0]
        return bitd__ebf
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    iezo__ypb = 'def csv_impl(fname, nrows, skiprows):\n'
    iezo__ypb += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    etub__dqa = {}
    exec(iezo__ypb, {}, etub__dqa)
    wwx__wzu = etub__dqa['csv_impl']
    yug__rei = csv_node.usecols
    if yug__rei:
        yug__rei = [csv_node.usecols[paj__bpuk] for paj__bpuk in csv_node.
            out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        qdazi__rlvmu = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        xxpu__nau = csv_node.loc.strformat()
        jlyp__gnz = []
        tini__zxjzx = []
        if yug__rei:
            for paj__bpuk in csv_node.out_used_cols:
                dshqe__lrf = csv_node.df_colnames[paj__bpuk]
                jlyp__gnz.append(dshqe__lrf)
                if isinstance(csv_node.out_types[paj__bpuk], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    tini__zxjzx.append(dshqe__lrf)
        bodo.user_logging.log_message('Column Pruning', qdazi__rlvmu,
            xxpu__nau, jlyp__gnz)
        if tini__zxjzx:
            ssv__mko = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', ssv__mko,
                xxpu__nau, tini__zxjzx)
    tne__agr = _gen_csv_reader_py(csv_node.df_colnames, csv_node.out_types,
        yug__rei, csv_node.out_used_cols, csv_node.sep, parallel, csv_node.
        header, csv_node.compression, csv_node.is_skiprows_list, csv_node.
        pd_low_memory, csv_node.escapechar, csv_node.storage_options,
        idx_col_index=csv_node.index_column_index, idx_col_typ=csv_node.
        index_column_typ)
    eob__xeii = compile_to_numba_ir(wwx__wzu, {'_csv_reader_py': tne__agr},
        typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
        types.int64, depe__nbkn), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(eob__xeii, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    bitd__ebf = eob__xeii.body[:-3]
    bitd__ebf[-1].target = csv_node.out_vars[1]
    bitd__ebf[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not yug__rei
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        bitd__ebf.pop(-1)
    elif not yug__rei:
        bitd__ebf.pop(-2)
    return bitd__ebf


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    return bodo.ir.connector.base_connector_remove_dead_columns(csv_node,
        column_live_map, equiv_vars, typemap, 'CSVReader', csv_node.usecols)


numba.parfors.array_analysis.array_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[CsvReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[CsvReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[CsvReader] = remove_dead_csv
numba.core.analysis.ir_extension_usedefs[CsvReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[CsvReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[CsvReader] = csv_distributed_run
remove_dead_column_extensions[CsvReader] = csv_remove_dead_column
ir_extension_table_column_use[CsvReader
    ] = bodo.ir.connector.connector_table_column_use


def _get_dtype_str(t):
    enghv__ntzcy = t.dtype
    if isinstance(enghv__ntzcy, PDCategoricalDtype):
        bxn__bhsb = CategoricalArrayType(enghv__ntzcy)
        dohn__vrlj = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, dohn__vrlj, bxn__bhsb)
        return dohn__vrlj
    if enghv__ntzcy == types.NPDatetime('ns'):
        enghv__ntzcy = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        fec__fip = 'int_arr_{}'.format(enghv__ntzcy)
        setattr(types, fec__fip, t)
        return fec__fip
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if enghv__ntzcy == types.bool_:
        enghv__ntzcy = 'bool_'
    if enghv__ntzcy == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(enghv__ntzcy, (
        StringArrayType, ArrayItemArrayType)):
        fnwza__jizw = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, fnwza__jizw, t)
        return fnwza__jizw
    return '{}[::1]'.format(enghv__ntzcy)


def _get_pd_dtype_str(t):
    enghv__ntzcy = t.dtype
    if isinstance(enghv__ntzcy, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(enghv__ntzcy.categories)
    if enghv__ntzcy == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if enghv__ntzcy.signed else 'U',
            enghv__ntzcy.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(enghv__ntzcy, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(enghv__ntzcy)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    qjejx__fvnbs = ''
    from collections import defaultdict
    bqkrg__maj = defaultdict(list)
    for lsspo__exn, fkkvl__mqf in typemap.items():
        bqkrg__maj[fkkvl__mqf].append(lsspo__exn)
    twyc__lqiqb = df.columns.to_list()
    wgio__dgo = []
    for fkkvl__mqf, dpzbp__egnc in bqkrg__maj.items():
        try:
            wgio__dgo.append(df.loc[:, dpzbp__egnc].astype(fkkvl__mqf, copy
                =False))
            df = df.drop(dpzbp__egnc, axis=1)
        except (ValueError, TypeError) as gsg__tbj:
            qjejx__fvnbs = (
                f"Caught the runtime error '{gsg__tbj}' on columns {dpzbp__egnc}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    dtyj__wzety = bool(qjejx__fvnbs)
    if parallel:
        msu__zxsg = MPI.COMM_WORLD
        dtyj__wzety = msu__zxsg.allreduce(dtyj__wzety, op=MPI.LOR)
    if dtyj__wzety:
        sbgs__ravn = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if qjejx__fvnbs:
            raise TypeError(f'{sbgs__ravn}\n{qjejx__fvnbs}')
        else:
            raise TypeError(
                f'{sbgs__ravn}\nPlease refer to errors on other ranks.')
    df = pd.concat(wgio__dgo + [df], axis=1)
    tnkbf__novcz = df.loc[:, twyc__lqiqb]
    return tnkbf__novcz


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    egr__willy = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        iezo__ypb = '  skiprows = sorted(set(skiprows))\n'
    else:
        iezo__ypb = '  skiprows = [skiprows]\n'
    iezo__ypb += '  skiprows_list_len = len(skiprows)\n'
    iezo__ypb += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    iezo__ypb += '  check_java_installation(fname)\n'
    iezo__ypb += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    iezo__ypb += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    iezo__ypb += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    iezo__ypb += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, egr__willy, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    iezo__ypb += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    iezo__ypb += "      raise FileNotFoundError('File does not exist')\n"
    return iezo__ypb


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    zkcgu__mnp = [str(paj__bpuk) for paj__bpuk, ywyw__ojpwa in enumerate(
        usecols) if col_typs[out_used_cols[paj__bpuk]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        zkcgu__mnp.append(str(idx_col_index))
    rylml__whzq = ', '.join(zkcgu__mnp)
    bsn__anhu = _gen_parallel_flag_name(sanitized_cnames)
    ouhv__nhr = f"{bsn__anhu}='bool_'" if check_parallel_runtime else ''
    hll__nze = [_get_pd_dtype_str(col_typs[out_used_cols[paj__bpuk]]) for
        paj__bpuk in range(len(usecols))]
    iln__nbdhn = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    hfma__hayt = [ywyw__ojpwa for paj__bpuk, ywyw__ojpwa in enumerate(
        usecols) if hll__nze[paj__bpuk] == 'str']
    if idx_col_index is not None and iln__nbdhn == 'str':
        hfma__hayt.append(idx_col_index)
    jnqax__yhus = np.array(hfma__hayt, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = jnqax__yhus
    iezo__ypb = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    urg__ztx = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = urg__ztx
    iezo__ypb += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    qzb__qrhf = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = qzb__qrhf
        iezo__ypb += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    etkt__ada = defaultdict(list)
    for paj__bpuk, ywyw__ojpwa in enumerate(usecols):
        if hll__nze[paj__bpuk] == 'str':
            continue
        etkt__ada[hll__nze[paj__bpuk]].append(ywyw__ojpwa)
    if idx_col_index is not None and iln__nbdhn != 'str':
        etkt__ada[iln__nbdhn].append(idx_col_index)
    for paj__bpuk, snfq__pchoz in enumerate(etkt__ada.values()):
        glbs[f't_arr_{paj__bpuk}_{call_id}'] = np.asarray(snfq__pchoz)
        iezo__ypb += (
            f'  t_arr_{paj__bpuk}_{call_id}_2 = t_arr_{paj__bpuk}_{call_id}\n')
    if idx_col_index != None:
        iezo__ypb += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {ouhv__nhr}):
"""
    else:
        iezo__ypb += f'  with objmode(T=table_type_{call_id}, {ouhv__nhr}):\n'
    iezo__ypb += f'    typemap = {{}}\n'
    for paj__bpuk, znlos__jkvpc in enumerate(etkt__ada.keys()):
        iezo__ypb += f"""    typemap.update({{i:{znlos__jkvpc} for i in t_arr_{paj__bpuk}_{call_id}_2}})
"""
    iezo__ypb += '    if f_reader.get_chunk_size() == 0:\n'
    iezo__ypb += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    iezo__ypb += '    else:\n'
    iezo__ypb += '      df = pd.read_csv(f_reader,\n'
    iezo__ypb += '        header=None,\n'
    iezo__ypb += '        parse_dates=[{}],\n'.format(rylml__whzq)
    iezo__ypb += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    iezo__ypb += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        iezo__ypb += f'    {bsn__anhu} = f_reader.is_parallel()\n'
    else:
        iezo__ypb += f'    {bsn__anhu} = {parallel}\n'
    iezo__ypb += f'    df = astype(df, typemap, {bsn__anhu})\n'
    if idx_col_index != None:
        ybf__aha = sorted(urg__ztx).index(idx_col_index)
        iezo__ypb += f'    idx_arr = df.iloc[:, {ybf__aha}].values\n'
        iezo__ypb += (
            f'    df.drop(columns=df.columns[{ybf__aha}], inplace=True)\n')
    if len(usecols) == 0:
        iezo__ypb += f'    T = None\n'
    else:
        iezo__ypb += f'    arrs = []\n'
        iezo__ypb += f'    for i in range(df.shape[1]):\n'
        iezo__ypb += f'      arrs.append(df.iloc[:, i].values)\n'
        iezo__ypb += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return iezo__ypb


def _gen_parallel_flag_name(sanitized_cnames):
    bsn__anhu = '_parallel_value'
    while bsn__anhu in sanitized_cnames:
        bsn__anhu = '_' + bsn__anhu
    return bsn__anhu


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(hhyoz__frxm) for hhyoz__frxm in
        col_names]
    iezo__ypb = 'def csv_reader_py(fname, nrows, skiprows):\n'
    iezo__ypb += _gen_csv_file_reader_init(parallel, header, compression, -
        1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    knn__eqpl = globals()
    if idx_col_typ != types.none:
        knn__eqpl[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        knn__eqpl[f'table_type_{call_id}'] = types.none
    else:
        knn__eqpl[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    iezo__ypb += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, knn__eqpl, parallel=parallel, check_parallel_runtime=False,
        idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        iezo__ypb += '  return (T, idx_arr)\n'
    else:
        iezo__ypb += '  return (T, None)\n'
    etub__dqa = {}
    knn__eqpl['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(iezo__ypb, knn__eqpl, etub__dqa)
    tne__agr = etub__dqa['csv_reader_py']
    iwhzb__kdmyb = numba.njit(tne__agr)
    compiled_funcs.append(iwhzb__kdmyb)
    return iwhzb__kdmyb
