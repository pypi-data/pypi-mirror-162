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
    napy__wtbq = typemap[node.file_name.name]
    if types.unliteral(napy__wtbq) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {napy__wtbq}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        ynj__ivhwq = typemap[node.skiprows.name]
        if isinstance(ynj__ivhwq, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(ynj__ivhwq, types.Integer) and not (isinstance(
            ynj__ivhwq, (types.List, types.Tuple)) and isinstance(
            ynj__ivhwq.dtype, types.Integer)) and not isinstance(ynj__ivhwq,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {ynj__ivhwq}."
                , loc=node.skiprows.loc)
        elif isinstance(ynj__ivhwq, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        wheo__jwuh = typemap[node.nrows.name]
        if not isinstance(wheo__jwuh, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {wheo__jwuh}."
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
        mepmt__tzg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        vton__gbuhp = cgutils.get_or_insert_function(builder.module,
            mepmt__tzg, name='csv_file_chunk_reader')
        mzz__ldb = builder.call(vton__gbuhp, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        zpy__bfu = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        dxz__ltbqe = context.get_python_api(builder)
        zpy__bfu.meminfo = dxz__ltbqe.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), mzz__ldb)
        zpy__bfu.pyobj = mzz__ldb
        dxz__ltbqe.decref(mzz__ldb)
        return zpy__bfu._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        ifcyh__ykrwz = csv_node.out_vars[0]
        if ifcyh__ykrwz.name not in lives:
            return None
    else:
        geajk__yon = csv_node.out_vars[0]
        yyii__trlea = csv_node.out_vars[1]
        if geajk__yon.name not in lives and yyii__trlea.name not in lives:
            return None
        elif yyii__trlea.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif geajk__yon.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    ynj__ivhwq = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            gmtq__ebv = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            nsvk__jgrlz = csv_node.loc.strformat()
            thge__ptjee = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', gmtq__ebv,
                nsvk__jgrlz, thge__ptjee)
            twunz__japdc = csv_node.out_types[0].yield_type.data
            rmgsa__fry = [tnsr__xnwp for jwzr__nxt, tnsr__xnwp in enumerate
                (csv_node.df_colnames) if isinstance(twunz__japdc[jwzr__nxt
                ], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if rmgsa__fry:
                moh__yuyp = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    moh__yuyp, nsvk__jgrlz, rmgsa__fry)
        if array_dists is not None:
            mreig__usnl = csv_node.out_vars[0].name
            parallel = array_dists[mreig__usnl] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        utz__nszu = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        utz__nszu += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        utz__nszu += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        wpx__kcmvj = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(utz__nszu, {}, wpx__kcmvj)
        ikj__acckn = wpx__kcmvj['csv_iterator_impl']
        sblgd__bsv = 'def csv_reader_init(fname, nrows, skiprows):\n'
        sblgd__bsv += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        sblgd__bsv += '  return f_reader\n'
        exec(sblgd__bsv, globals(), wpx__kcmvj)
        jkrd__zqnf = wpx__kcmvj['csv_reader_init']
        hyzzv__uspdd = numba.njit(jkrd__zqnf)
        compiled_funcs.append(hyzzv__uspdd)
        iez__qocv = compile_to_numba_ir(ikj__acckn, {'_csv_reader_init':
            hyzzv__uspdd, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, ynj__ivhwq), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(iez__qocv, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        rmcab__qut = iez__qocv.body[:-3]
        rmcab__qut[-1].target = csv_node.out_vars[0]
        return rmcab__qut
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    utz__nszu = 'def csv_impl(fname, nrows, skiprows):\n'
    utz__nszu += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    wpx__kcmvj = {}
    exec(utz__nszu, {}, wpx__kcmvj)
    wodar__azyf = wpx__kcmvj['csv_impl']
    ujoib__mog = csv_node.usecols
    if ujoib__mog:
        ujoib__mog = [csv_node.usecols[jwzr__nxt] for jwzr__nxt in csv_node
            .out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        gmtq__ebv = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        nsvk__jgrlz = csv_node.loc.strformat()
        thge__ptjee = []
        rmgsa__fry = []
        if ujoib__mog:
            for jwzr__nxt in csv_node.out_used_cols:
                rhei__jcph = csv_node.df_colnames[jwzr__nxt]
                thge__ptjee.append(rhei__jcph)
                if isinstance(csv_node.out_types[jwzr__nxt], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    rmgsa__fry.append(rhei__jcph)
        bodo.user_logging.log_message('Column Pruning', gmtq__ebv,
            nsvk__jgrlz, thge__ptjee)
        if rmgsa__fry:
            moh__yuyp = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', moh__yuyp,
                nsvk__jgrlz, rmgsa__fry)
    kqgo__jjnwc = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, ujoib__mog, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    iez__qocv = compile_to_numba_ir(wodar__azyf, {'_csv_reader_py':
        kqgo__jjnwc}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, ynj__ivhwq), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(iez__qocv, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    rmcab__qut = iez__qocv.body[:-3]
    rmcab__qut[-1].target = csv_node.out_vars[1]
    rmcab__qut[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not ujoib__mog
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        rmcab__qut.pop(-1)
    elif not ujoib__mog:
        rmcab__qut.pop(-2)
    return rmcab__qut


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
    qqcjs__emwog = t.dtype
    if isinstance(qqcjs__emwog, PDCategoricalDtype):
        yot__bxph = CategoricalArrayType(qqcjs__emwog)
        eulz__aej = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, eulz__aej, yot__bxph)
        return eulz__aej
    if qqcjs__emwog == types.NPDatetime('ns'):
        qqcjs__emwog = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        rsz__xlr = 'int_arr_{}'.format(qqcjs__emwog)
        setattr(types, rsz__xlr, t)
        return rsz__xlr
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if qqcjs__emwog == types.bool_:
        qqcjs__emwog = 'bool_'
    if qqcjs__emwog == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(qqcjs__emwog, (
        StringArrayType, ArrayItemArrayType)):
        eotnj__ghgqq = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, eotnj__ghgqq, t)
        return eotnj__ghgqq
    return '{}[::1]'.format(qqcjs__emwog)


def _get_pd_dtype_str(t):
    qqcjs__emwog = t.dtype
    if isinstance(qqcjs__emwog, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(qqcjs__emwog.categories)
    if qqcjs__emwog == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if qqcjs__emwog.signed else 'U',
            qqcjs__emwog.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(qqcjs__emwog, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(qqcjs__emwog)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    xvk__ltdur = ''
    from collections import defaultdict
    dbdt__phz = defaultdict(list)
    for ytrdm__unv, yxv__bvvmd in typemap.items():
        dbdt__phz[yxv__bvvmd].append(ytrdm__unv)
    esj__qad = df.columns.to_list()
    qxizf__gjqv = []
    for yxv__bvvmd, xnu__elz in dbdt__phz.items():
        try:
            qxizf__gjqv.append(df.loc[:, xnu__elz].astype(yxv__bvvmd, copy=
                False))
            df = df.drop(xnu__elz, axis=1)
        except (ValueError, TypeError) as kjcu__wpqy:
            xvk__ltdur = (
                f"Caught the runtime error '{kjcu__wpqy}' on columns {xnu__elz}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    qyy__ryxhi = bool(xvk__ltdur)
    if parallel:
        bmgjz__gsrz = MPI.COMM_WORLD
        qyy__ryxhi = bmgjz__gsrz.allreduce(qyy__ryxhi, op=MPI.LOR)
    if qyy__ryxhi:
        oxnfx__lyplg = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if xvk__ltdur:
            raise TypeError(f'{oxnfx__lyplg}\n{xvk__ltdur}')
        else:
            raise TypeError(
                f'{oxnfx__lyplg}\nPlease refer to errors on other ranks.')
    df = pd.concat(qxizf__gjqv + [df], axis=1)
    mkg__kehmz = df.loc[:, esj__qad]
    return mkg__kehmz


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    lck__hbydf = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        utz__nszu = '  skiprows = sorted(set(skiprows))\n'
    else:
        utz__nszu = '  skiprows = [skiprows]\n'
    utz__nszu += '  skiprows_list_len = len(skiprows)\n'
    utz__nszu += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    utz__nszu += '  check_java_installation(fname)\n'
    utz__nszu += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    utz__nszu += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    utz__nszu += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    utz__nszu += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, lck__hbydf, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    utz__nszu += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    utz__nszu += "      raise FileNotFoundError('File does not exist')\n"
    return utz__nszu


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    wsw__slq = [str(jwzr__nxt) for jwzr__nxt, gmxe__sud in enumerate(
        usecols) if col_typs[out_used_cols[jwzr__nxt]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        wsw__slq.append(str(idx_col_index))
    slbm__zsfcv = ', '.join(wsw__slq)
    vkcv__qjna = _gen_parallel_flag_name(sanitized_cnames)
    dhvre__pcfsa = f"{vkcv__qjna}='bool_'" if check_parallel_runtime else ''
    cuwld__szor = [_get_pd_dtype_str(col_typs[out_used_cols[jwzr__nxt]]) for
        jwzr__nxt in range(len(usecols))]
    zsluq__ndj = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    gnn__opdtx = [gmxe__sud for jwzr__nxt, gmxe__sud in enumerate(usecols) if
        cuwld__szor[jwzr__nxt] == 'str']
    if idx_col_index is not None and zsluq__ndj == 'str':
        gnn__opdtx.append(idx_col_index)
    krwov__gsi = np.array(gnn__opdtx, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = krwov__gsi
    utz__nszu = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    rfug__ovioy = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = rfug__ovioy
    utz__nszu += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    dfpdj__wbew = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = dfpdj__wbew
        utz__nszu += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    jakjh__uhda = defaultdict(list)
    for jwzr__nxt, gmxe__sud in enumerate(usecols):
        if cuwld__szor[jwzr__nxt] == 'str':
            continue
        jakjh__uhda[cuwld__szor[jwzr__nxt]].append(gmxe__sud)
    if idx_col_index is not None and zsluq__ndj != 'str':
        jakjh__uhda[zsluq__ndj].append(idx_col_index)
    for jwzr__nxt, zaaqr__ufnk in enumerate(jakjh__uhda.values()):
        glbs[f't_arr_{jwzr__nxt}_{call_id}'] = np.asarray(zaaqr__ufnk)
        utz__nszu += (
            f'  t_arr_{jwzr__nxt}_{call_id}_2 = t_arr_{jwzr__nxt}_{call_id}\n')
    if idx_col_index != None:
        utz__nszu += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {dhvre__pcfsa}):
"""
    else:
        utz__nszu += (
            f'  with objmode(T=table_type_{call_id}, {dhvre__pcfsa}):\n')
    utz__nszu += f'    typemap = {{}}\n'
    for jwzr__nxt, fpx__hpk in enumerate(jakjh__uhda.keys()):
        utz__nszu += f"""    typemap.update({{i:{fpx__hpk} for i in t_arr_{jwzr__nxt}_{call_id}_2}})
"""
    utz__nszu += '    if f_reader.get_chunk_size() == 0:\n'
    utz__nszu += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    utz__nszu += '    else:\n'
    utz__nszu += '      df = pd.read_csv(f_reader,\n'
    utz__nszu += '        header=None,\n'
    utz__nszu += '        parse_dates=[{}],\n'.format(slbm__zsfcv)
    utz__nszu += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    utz__nszu += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        utz__nszu += f'    {vkcv__qjna} = f_reader.is_parallel()\n'
    else:
        utz__nszu += f'    {vkcv__qjna} = {parallel}\n'
    utz__nszu += f'    df = astype(df, typemap, {vkcv__qjna})\n'
    if idx_col_index != None:
        xlq__mpna = sorted(rfug__ovioy).index(idx_col_index)
        utz__nszu += f'    idx_arr = df.iloc[:, {xlq__mpna}].values\n'
        utz__nszu += (
            f'    df.drop(columns=df.columns[{xlq__mpna}], inplace=True)\n')
    if len(usecols) == 0:
        utz__nszu += f'    T = None\n'
    else:
        utz__nszu += f'    arrs = []\n'
        utz__nszu += f'    for i in range(df.shape[1]):\n'
        utz__nszu += f'      arrs.append(df.iloc[:, i].values)\n'
        utz__nszu += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return utz__nszu


def _gen_parallel_flag_name(sanitized_cnames):
    vkcv__qjna = '_parallel_value'
    while vkcv__qjna in sanitized_cnames:
        vkcv__qjna = '_' + vkcv__qjna
    return vkcv__qjna


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(tnsr__xnwp) for tnsr__xnwp in
        col_names]
    utz__nszu = 'def csv_reader_py(fname, nrows, skiprows):\n'
    utz__nszu += _gen_csv_file_reader_init(parallel, header, compression, -
        1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    qgy__jgzwg = globals()
    if idx_col_typ != types.none:
        qgy__jgzwg[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        qgy__jgzwg[f'table_type_{call_id}'] = types.none
    else:
        qgy__jgzwg[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    utz__nszu += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, qgy__jgzwg, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        utz__nszu += '  return (T, idx_arr)\n'
    else:
        utz__nszu += '  return (T, None)\n'
    wpx__kcmvj = {}
    qgy__jgzwg['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(utz__nszu, qgy__jgzwg, wpx__kcmvj)
    kqgo__jjnwc = wpx__kcmvj['csv_reader_py']
    hyzzv__uspdd = numba.njit(kqgo__jjnwc)
    compiled_funcs.append(hyzzv__uspdd)
    return hyzzv__uspdd
