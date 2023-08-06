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
    magpl__edwnj = typemap[node.file_name.name]
    if types.unliteral(magpl__edwnj) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {magpl__edwnj}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        oos__mmg = typemap[node.skiprows.name]
        if isinstance(oos__mmg, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(oos__mmg, types.Integer) and not (isinstance(
            oos__mmg, (types.List, types.Tuple)) and isinstance(oos__mmg.
            dtype, types.Integer)) and not isinstance(oos__mmg, (types.
            LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {oos__mmg}."
                , loc=node.skiprows.loc)
        elif isinstance(oos__mmg, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        ccmix__jsdf = typemap[node.nrows.name]
        if not isinstance(ccmix__jsdf, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {ccmix__jsdf}."
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
        sby__wkdsu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        ecur__wfhs = cgutils.get_or_insert_function(builder.module,
            sby__wkdsu, name='csv_file_chunk_reader')
        qfpi__xvqmw = builder.call(ecur__wfhs, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        noe__hjfjm = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        vsyrn__ewb = context.get_python_api(builder)
        noe__hjfjm.meminfo = vsyrn__ewb.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), qfpi__xvqmw)
        noe__hjfjm.pyobj = qfpi__xvqmw
        vsyrn__ewb.decref(qfpi__xvqmw)
        return noe__hjfjm._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        gudvq__qxka = csv_node.out_vars[0]
        if gudvq__qxka.name not in lives:
            return None
    else:
        qvjj__lvp = csv_node.out_vars[0]
        qvdlu__rnm = csv_node.out_vars[1]
        if qvjj__lvp.name not in lives and qvdlu__rnm.name not in lives:
            return None
        elif qvdlu__rnm.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif qvjj__lvp.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    oos__mmg = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            odv__wns = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            gbpat__cntgd = csv_node.loc.strformat()
            udhvm__dik = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', odv__wns,
                gbpat__cntgd, udhvm__dik)
            fanzt__buym = csv_node.out_types[0].yield_type.data
            pcz__fuw = [xtnb__zjxhb for vqp__gvzrb, xtnb__zjxhb in
                enumerate(csv_node.df_colnames) if isinstance(fanzt__buym[
                vqp__gvzrb], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if pcz__fuw:
                lgv__mifkw = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    lgv__mifkw, gbpat__cntgd, pcz__fuw)
        if array_dists is not None:
            ixuhv__mxvq = csv_node.out_vars[0].name
            parallel = array_dists[ixuhv__mxvq] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        bjqgr__jrwq = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        bjqgr__jrwq += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        bjqgr__jrwq += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        bhrcu__cgncz = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(bjqgr__jrwq, {}, bhrcu__cgncz)
        bic__xxvxt = bhrcu__cgncz['csv_iterator_impl']
        gel__qwt = 'def csv_reader_init(fname, nrows, skiprows):\n'
        gel__qwt += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        gel__qwt += '  return f_reader\n'
        exec(gel__qwt, globals(), bhrcu__cgncz)
        dksxo__urcv = bhrcu__cgncz['csv_reader_init']
        xvc__qwu = numba.njit(dksxo__urcv)
        compiled_funcs.append(xvc__qwu)
        kouy__txx = compile_to_numba_ir(bic__xxvxt, {'_csv_reader_init':
            xvc__qwu, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, oos__mmg), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(kouy__txx, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        mty__kppzc = kouy__txx.body[:-3]
        mty__kppzc[-1].target = csv_node.out_vars[0]
        return mty__kppzc
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    bjqgr__jrwq = 'def csv_impl(fname, nrows, skiprows):\n'
    bjqgr__jrwq += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    bhrcu__cgncz = {}
    exec(bjqgr__jrwq, {}, bhrcu__cgncz)
    mpvzq__mbnbu = bhrcu__cgncz['csv_impl']
    eqr__gzbfg = csv_node.usecols
    if eqr__gzbfg:
        eqr__gzbfg = [csv_node.usecols[vqp__gvzrb] for vqp__gvzrb in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        odv__wns = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        gbpat__cntgd = csv_node.loc.strformat()
        udhvm__dik = []
        pcz__fuw = []
        if eqr__gzbfg:
            for vqp__gvzrb in csv_node.out_used_cols:
                oxvm__huvns = csv_node.df_colnames[vqp__gvzrb]
                udhvm__dik.append(oxvm__huvns)
                if isinstance(csv_node.out_types[vqp__gvzrb], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    pcz__fuw.append(oxvm__huvns)
        bodo.user_logging.log_message('Column Pruning', odv__wns,
            gbpat__cntgd, udhvm__dik)
        if pcz__fuw:
            lgv__mifkw = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', lgv__mifkw,
                gbpat__cntgd, pcz__fuw)
    spexv__yqw = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, eqr__gzbfg, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    kouy__txx = compile_to_numba_ir(mpvzq__mbnbu, {'_csv_reader_py':
        spexv__yqw}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, oos__mmg), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(kouy__txx, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    mty__kppzc = kouy__txx.body[:-3]
    mty__kppzc[-1].target = csv_node.out_vars[1]
    mty__kppzc[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not eqr__gzbfg
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        mty__kppzc.pop(-1)
    elif not eqr__gzbfg:
        mty__kppzc.pop(-2)
    return mty__kppzc


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
    mpek__ejme = t.dtype
    if isinstance(mpek__ejme, PDCategoricalDtype):
        nyur__ihtst = CategoricalArrayType(mpek__ejme)
        qmk__uoop = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, qmk__uoop, nyur__ihtst)
        return qmk__uoop
    if mpek__ejme == types.NPDatetime('ns'):
        mpek__ejme = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        qfk__igj = 'int_arr_{}'.format(mpek__ejme)
        setattr(types, qfk__igj, t)
        return qfk__igj
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if mpek__ejme == types.bool_:
        mpek__ejme = 'bool_'
    if mpek__ejme == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(mpek__ejme, (
        StringArrayType, ArrayItemArrayType)):
        akx__brp = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, akx__brp, t)
        return akx__brp
    return '{}[::1]'.format(mpek__ejme)


def _get_pd_dtype_str(t):
    mpek__ejme = t.dtype
    if isinstance(mpek__ejme, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(mpek__ejme.categories)
    if mpek__ejme == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if mpek__ejme.signed else 'U',
            mpek__ejme.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(mpek__ejme, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(mpek__ejme)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    ysklq__yitcc = ''
    from collections import defaultdict
    qvr__rht = defaultdict(list)
    for ybhp__alnor, tkrf__eymo in typemap.items():
        qvr__rht[tkrf__eymo].append(ybhp__alnor)
    phf__zgkt = df.columns.to_list()
    vvof__gqb = []
    for tkrf__eymo, vtxs__tgcib in qvr__rht.items():
        try:
            vvof__gqb.append(df.loc[:, vtxs__tgcib].astype(tkrf__eymo, copy
                =False))
            df = df.drop(vtxs__tgcib, axis=1)
        except (ValueError, TypeError) as wtjdm__iwg:
            ysklq__yitcc = (
                f"Caught the runtime error '{wtjdm__iwg}' on columns {vtxs__tgcib}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    ooqz__ter = bool(ysklq__yitcc)
    if parallel:
        hhjp__xjko = MPI.COMM_WORLD
        ooqz__ter = hhjp__xjko.allreduce(ooqz__ter, op=MPI.LOR)
    if ooqz__ter:
        awcs__pzn = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if ysklq__yitcc:
            raise TypeError(f'{awcs__pzn}\n{ysklq__yitcc}')
        else:
            raise TypeError(
                f'{awcs__pzn}\nPlease refer to errors on other ranks.')
    df = pd.concat(vvof__gqb + [df], axis=1)
    yvsed__dkw = df.loc[:, phf__zgkt]
    return yvsed__dkw


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    pep__niaqk = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        bjqgr__jrwq = '  skiprows = sorted(set(skiprows))\n'
    else:
        bjqgr__jrwq = '  skiprows = [skiprows]\n'
    bjqgr__jrwq += '  skiprows_list_len = len(skiprows)\n'
    bjqgr__jrwq += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    bjqgr__jrwq += '  check_java_installation(fname)\n'
    bjqgr__jrwq += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    bjqgr__jrwq += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    bjqgr__jrwq += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    bjqgr__jrwq += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, pep__niaqk, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    bjqgr__jrwq += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    bjqgr__jrwq += "      raise FileNotFoundError('File does not exist')\n"
    return bjqgr__jrwq


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    ggls__dery = [str(vqp__gvzrb) for vqp__gvzrb, cknj__znyj in enumerate(
        usecols) if col_typs[out_used_cols[vqp__gvzrb]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        ggls__dery.append(str(idx_col_index))
    rtrht__ybr = ', '.join(ggls__dery)
    oqyh__skxo = _gen_parallel_flag_name(sanitized_cnames)
    lkccc__jwsm = f"{oqyh__skxo}='bool_'" if check_parallel_runtime else ''
    krynr__ooaz = [_get_pd_dtype_str(col_typs[out_used_cols[vqp__gvzrb]]) for
        vqp__gvzrb in range(len(usecols))]
    mxpzk__dods = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    pywbm__qzpkz = [cknj__znyj for vqp__gvzrb, cknj__znyj in enumerate(
        usecols) if krynr__ooaz[vqp__gvzrb] == 'str']
    if idx_col_index is not None and mxpzk__dods == 'str':
        pywbm__qzpkz.append(idx_col_index)
    zmkpt__dowt = np.array(pywbm__qzpkz, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = zmkpt__dowt
    bjqgr__jrwq = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    tbpj__shopq = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = tbpj__shopq
    bjqgr__jrwq += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    vizx__ebv = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = vizx__ebv
        bjqgr__jrwq += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    edqd__laomk = defaultdict(list)
    for vqp__gvzrb, cknj__znyj in enumerate(usecols):
        if krynr__ooaz[vqp__gvzrb] == 'str':
            continue
        edqd__laomk[krynr__ooaz[vqp__gvzrb]].append(cknj__znyj)
    if idx_col_index is not None and mxpzk__dods != 'str':
        edqd__laomk[mxpzk__dods].append(idx_col_index)
    for vqp__gvzrb, wng__wwt in enumerate(edqd__laomk.values()):
        glbs[f't_arr_{vqp__gvzrb}_{call_id}'] = np.asarray(wng__wwt)
        bjqgr__jrwq += (
            f'  t_arr_{vqp__gvzrb}_{call_id}_2 = t_arr_{vqp__gvzrb}_{call_id}\n'
            )
    if idx_col_index != None:
        bjqgr__jrwq += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {lkccc__jwsm}):
"""
    else:
        bjqgr__jrwq += (
            f'  with objmode(T=table_type_{call_id}, {lkccc__jwsm}):\n')
    bjqgr__jrwq += f'    typemap = {{}}\n'
    for vqp__gvzrb, uxp__gjpgj in enumerate(edqd__laomk.keys()):
        bjqgr__jrwq += f"""    typemap.update({{i:{uxp__gjpgj} for i in t_arr_{vqp__gvzrb}_{call_id}_2}})
"""
    bjqgr__jrwq += '    if f_reader.get_chunk_size() == 0:\n'
    bjqgr__jrwq += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    bjqgr__jrwq += '    else:\n'
    bjqgr__jrwq += '      df = pd.read_csv(f_reader,\n'
    bjqgr__jrwq += '        header=None,\n'
    bjqgr__jrwq += '        parse_dates=[{}],\n'.format(rtrht__ybr)
    bjqgr__jrwq += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    bjqgr__jrwq += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        bjqgr__jrwq += f'    {oqyh__skxo} = f_reader.is_parallel()\n'
    else:
        bjqgr__jrwq += f'    {oqyh__skxo} = {parallel}\n'
    bjqgr__jrwq += f'    df = astype(df, typemap, {oqyh__skxo})\n'
    if idx_col_index != None:
        vfw__aulo = sorted(tbpj__shopq).index(idx_col_index)
        bjqgr__jrwq += f'    idx_arr = df.iloc[:, {vfw__aulo}].values\n'
        bjqgr__jrwq += (
            f'    df.drop(columns=df.columns[{vfw__aulo}], inplace=True)\n')
    if len(usecols) == 0:
        bjqgr__jrwq += f'    T = None\n'
    else:
        bjqgr__jrwq += f'    arrs = []\n'
        bjqgr__jrwq += f'    for i in range(df.shape[1]):\n'
        bjqgr__jrwq += f'      arrs.append(df.iloc[:, i].values)\n'
        bjqgr__jrwq += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return bjqgr__jrwq


def _gen_parallel_flag_name(sanitized_cnames):
    oqyh__skxo = '_parallel_value'
    while oqyh__skxo in sanitized_cnames:
        oqyh__skxo = '_' + oqyh__skxo
    return oqyh__skxo


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(xtnb__zjxhb) for xtnb__zjxhb in
        col_names]
    bjqgr__jrwq = 'def csv_reader_py(fname, nrows, skiprows):\n'
    bjqgr__jrwq += _gen_csv_file_reader_init(parallel, header, compression,
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    cldk__iuy = globals()
    if idx_col_typ != types.none:
        cldk__iuy[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        cldk__iuy[f'table_type_{call_id}'] = types.none
    else:
        cldk__iuy[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    bjqgr__jrwq += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, cldk__iuy, parallel=parallel, check_parallel_runtime=False,
        idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        bjqgr__jrwq += '  return (T, idx_arr)\n'
    else:
        bjqgr__jrwq += '  return (T, None)\n'
    bhrcu__cgncz = {}
    cldk__iuy['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(bjqgr__jrwq, cldk__iuy, bhrcu__cgncz)
    spexv__yqw = bhrcu__cgncz['csv_reader_py']
    xvc__qwu = numba.njit(spexv__yqw)
    compiled_funcs.append(xvc__qwu)
    return xvc__qwu
