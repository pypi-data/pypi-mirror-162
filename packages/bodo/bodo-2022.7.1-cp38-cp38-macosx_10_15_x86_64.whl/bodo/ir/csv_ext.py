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
    map__twvy = typemap[node.file_name.name]
    if types.unliteral(map__twvy) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {map__twvy}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        zgg__diui = typemap[node.skiprows.name]
        if isinstance(zgg__diui, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(zgg__diui, types.Integer) and not (isinstance(
            zgg__diui, (types.List, types.Tuple)) and isinstance(zgg__diui.
            dtype, types.Integer)) and not isinstance(zgg__diui, (types.
            LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {zgg__diui}."
                , loc=node.skiprows.loc)
        elif isinstance(zgg__diui, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        wfwid__qdsld = typemap[node.nrows.name]
        if not isinstance(wfwid__qdsld, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {wfwid__qdsld}."
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
        xjufj__ffmbj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        oop__ngzuw = cgutils.get_or_insert_function(builder.module,
            xjufj__ffmbj, name='csv_file_chunk_reader')
        jya__xvwwh = builder.call(oop__ngzuw, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        gmg__lops = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        bpiiv__cglo = context.get_python_api(builder)
        gmg__lops.meminfo = bpiiv__cglo.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), jya__xvwwh)
        gmg__lops.pyobj = jya__xvwwh
        bpiiv__cglo.decref(jya__xvwwh)
        return gmg__lops._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        fdyb__lrcm = csv_node.out_vars[0]
        if fdyb__lrcm.name not in lives:
            return None
    else:
        vraa__cfum = csv_node.out_vars[0]
        jlm__gmq = csv_node.out_vars[1]
        if vraa__cfum.name not in lives and jlm__gmq.name not in lives:
            return None
        elif jlm__gmq.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif vraa__cfum.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    zgg__diui = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            olc__ygl = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            ttilc__zbwte = csv_node.loc.strformat()
            kkqya__wilkm = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', olc__ygl,
                ttilc__zbwte, kkqya__wilkm)
            ekly__ekvto = csv_node.out_types[0].yield_type.data
            vanm__vkqkk = [tutzl__fetx for fvcon__smyki, tutzl__fetx in
                enumerate(csv_node.df_colnames) if isinstance(ekly__ekvto[
                fvcon__smyki], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if vanm__vkqkk:
                lwcn__xltfl = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    lwcn__xltfl, ttilc__zbwte, vanm__vkqkk)
        if array_dists is not None:
            amq__pxyh = csv_node.out_vars[0].name
            parallel = array_dists[amq__pxyh] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        lnl__nnmgm = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        lnl__nnmgm += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        lnl__nnmgm += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        cyopz__fopn = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(lnl__nnmgm, {}, cyopz__fopn)
        bozb__wex = cyopz__fopn['csv_iterator_impl']
        yxw__otz = 'def csv_reader_init(fname, nrows, skiprows):\n'
        yxw__otz += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        yxw__otz += '  return f_reader\n'
        exec(yxw__otz, globals(), cyopz__fopn)
        mbna__bjuzd = cyopz__fopn['csv_reader_init']
        qfmgz__pgkzq = numba.njit(mbna__bjuzd)
        compiled_funcs.append(qfmgz__pgkzq)
        xry__bsjb = compile_to_numba_ir(bozb__wex, {'_csv_reader_init':
            qfmgz__pgkzq, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, zgg__diui), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(xry__bsjb, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        cyu__rgxjn = xry__bsjb.body[:-3]
        cyu__rgxjn[-1].target = csv_node.out_vars[0]
        return cyu__rgxjn
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    lnl__nnmgm = 'def csv_impl(fname, nrows, skiprows):\n'
    lnl__nnmgm += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    cyopz__fopn = {}
    exec(lnl__nnmgm, {}, cyopz__fopn)
    ebg__wdgnd = cyopz__fopn['csv_impl']
    kau__vuik = csv_node.usecols
    if kau__vuik:
        kau__vuik = [csv_node.usecols[fvcon__smyki] for fvcon__smyki in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        olc__ygl = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        ttilc__zbwte = csv_node.loc.strformat()
        kkqya__wilkm = []
        vanm__vkqkk = []
        if kau__vuik:
            for fvcon__smyki in csv_node.out_used_cols:
                loky__kwtjy = csv_node.df_colnames[fvcon__smyki]
                kkqya__wilkm.append(loky__kwtjy)
                if isinstance(csv_node.out_types[fvcon__smyki], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    vanm__vkqkk.append(loky__kwtjy)
        bodo.user_logging.log_message('Column Pruning', olc__ygl,
            ttilc__zbwte, kkqya__wilkm)
        if vanm__vkqkk:
            lwcn__xltfl = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                lwcn__xltfl, ttilc__zbwte, vanm__vkqkk)
    rjmm__fpaty = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, kau__vuik, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    xry__bsjb = compile_to_numba_ir(ebg__wdgnd, {'_csv_reader_py':
        rjmm__fpaty}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, zgg__diui), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(xry__bsjb, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    cyu__rgxjn = xry__bsjb.body[:-3]
    cyu__rgxjn[-1].target = csv_node.out_vars[1]
    cyu__rgxjn[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not kau__vuik
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        cyu__rgxjn.pop(-1)
    elif not kau__vuik:
        cyu__rgxjn.pop(-2)
    return cyu__rgxjn


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
    moyh__ufie = t.dtype
    if isinstance(moyh__ufie, PDCategoricalDtype):
        zal__ryvri = CategoricalArrayType(moyh__ufie)
        jpgmz__kqnc = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, jpgmz__kqnc, zal__ryvri)
        return jpgmz__kqnc
    if moyh__ufie == types.NPDatetime('ns'):
        moyh__ufie = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        odeu__fsr = 'int_arr_{}'.format(moyh__ufie)
        setattr(types, odeu__fsr, t)
        return odeu__fsr
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if moyh__ufie == types.bool_:
        moyh__ufie = 'bool_'
    if moyh__ufie == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(moyh__ufie, (
        StringArrayType, ArrayItemArrayType)):
        lytnw__rthia = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, lytnw__rthia, t)
        return lytnw__rthia
    return '{}[::1]'.format(moyh__ufie)


def _get_pd_dtype_str(t):
    moyh__ufie = t.dtype
    if isinstance(moyh__ufie, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(moyh__ufie.categories)
    if moyh__ufie == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if moyh__ufie.signed else 'U',
            moyh__ufie.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(moyh__ufie, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(moyh__ufie)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    fctgq__pcdp = ''
    from collections import defaultdict
    xjg__riuc = defaultdict(list)
    for kuwz__kjf, fwy__gqv in typemap.items():
        xjg__riuc[fwy__gqv].append(kuwz__kjf)
    reyqx__wrxgk = df.columns.to_list()
    bfp__syqsy = []
    for fwy__gqv, iue__mqp in xjg__riuc.items():
        try:
            bfp__syqsy.append(df.loc[:, iue__mqp].astype(fwy__gqv, copy=False))
            df = df.drop(iue__mqp, axis=1)
        except (ValueError, TypeError) as wwpqq__cfjw:
            fctgq__pcdp = (
                f"Caught the runtime error '{wwpqq__cfjw}' on columns {iue__mqp}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    oxx__whn = bool(fctgq__pcdp)
    if parallel:
        elczm__qlb = MPI.COMM_WORLD
        oxx__whn = elczm__qlb.allreduce(oxx__whn, op=MPI.LOR)
    if oxx__whn:
        hmnvq__ddks = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if fctgq__pcdp:
            raise TypeError(f'{hmnvq__ddks}\n{fctgq__pcdp}')
        else:
            raise TypeError(
                f'{hmnvq__ddks}\nPlease refer to errors on other ranks.')
    df = pd.concat(bfp__syqsy + [df], axis=1)
    ufev__vdnk = df.loc[:, reyqx__wrxgk]
    return ufev__vdnk


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    jwp__tey = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        lnl__nnmgm = '  skiprows = sorted(set(skiprows))\n'
    else:
        lnl__nnmgm = '  skiprows = [skiprows]\n'
    lnl__nnmgm += '  skiprows_list_len = len(skiprows)\n'
    lnl__nnmgm += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    lnl__nnmgm += '  check_java_installation(fname)\n'
    lnl__nnmgm += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    lnl__nnmgm += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    lnl__nnmgm += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    lnl__nnmgm += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, jwp__tey, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    lnl__nnmgm += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    lnl__nnmgm += "      raise FileNotFoundError('File does not exist')\n"
    return lnl__nnmgm


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    uzoh__twjj = [str(fvcon__smyki) for fvcon__smyki, wudoq__yamm in
        enumerate(usecols) if col_typs[out_used_cols[fvcon__smyki]].dtype ==
        types.NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        uzoh__twjj.append(str(idx_col_index))
    ykg__unk = ', '.join(uzoh__twjj)
    xijv__gszlt = _gen_parallel_flag_name(sanitized_cnames)
    tic__svumj = f"{xijv__gszlt}='bool_'" if check_parallel_runtime else ''
    hfyr__amq = [_get_pd_dtype_str(col_typs[out_used_cols[fvcon__smyki]]) for
        fvcon__smyki in range(len(usecols))]
    ycsko__jdb = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    jkfok__shxd = [wudoq__yamm for fvcon__smyki, wudoq__yamm in enumerate(
        usecols) if hfyr__amq[fvcon__smyki] == 'str']
    if idx_col_index is not None and ycsko__jdb == 'str':
        jkfok__shxd.append(idx_col_index)
    itfbs__fcg = np.array(jkfok__shxd, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = itfbs__fcg
    lnl__nnmgm = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    hbe__vruoj = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = hbe__vruoj
    lnl__nnmgm += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    ktc__fta = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = ktc__fta
        lnl__nnmgm += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    erjck__riiox = defaultdict(list)
    for fvcon__smyki, wudoq__yamm in enumerate(usecols):
        if hfyr__amq[fvcon__smyki] == 'str':
            continue
        erjck__riiox[hfyr__amq[fvcon__smyki]].append(wudoq__yamm)
    if idx_col_index is not None and ycsko__jdb != 'str':
        erjck__riiox[ycsko__jdb].append(idx_col_index)
    for fvcon__smyki, jnjut__blbes in enumerate(erjck__riiox.values()):
        glbs[f't_arr_{fvcon__smyki}_{call_id}'] = np.asarray(jnjut__blbes)
        lnl__nnmgm += (
            f'  t_arr_{fvcon__smyki}_{call_id}_2 = t_arr_{fvcon__smyki}_{call_id}\n'
            )
    if idx_col_index != None:
        lnl__nnmgm += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {tic__svumj}):
"""
    else:
        lnl__nnmgm += (
            f'  with objmode(T=table_type_{call_id}, {tic__svumj}):\n')
    lnl__nnmgm += f'    typemap = {{}}\n'
    for fvcon__smyki, idx__qoaon in enumerate(erjck__riiox.keys()):
        lnl__nnmgm += f"""    typemap.update({{i:{idx__qoaon} for i in t_arr_{fvcon__smyki}_{call_id}_2}})
"""
    lnl__nnmgm += '    if f_reader.get_chunk_size() == 0:\n'
    lnl__nnmgm += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    lnl__nnmgm += '    else:\n'
    lnl__nnmgm += '      df = pd.read_csv(f_reader,\n'
    lnl__nnmgm += '        header=None,\n'
    lnl__nnmgm += '        parse_dates=[{}],\n'.format(ykg__unk)
    lnl__nnmgm += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    lnl__nnmgm += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        lnl__nnmgm += f'    {xijv__gszlt} = f_reader.is_parallel()\n'
    else:
        lnl__nnmgm += f'    {xijv__gszlt} = {parallel}\n'
    lnl__nnmgm += f'    df = astype(df, typemap, {xijv__gszlt})\n'
    if idx_col_index != None:
        mkm__qjnr = sorted(hbe__vruoj).index(idx_col_index)
        lnl__nnmgm += f'    idx_arr = df.iloc[:, {mkm__qjnr}].values\n'
        lnl__nnmgm += (
            f'    df.drop(columns=df.columns[{mkm__qjnr}], inplace=True)\n')
    if len(usecols) == 0:
        lnl__nnmgm += f'    T = None\n'
    else:
        lnl__nnmgm += f'    arrs = []\n'
        lnl__nnmgm += f'    for i in range(df.shape[1]):\n'
        lnl__nnmgm += f'      arrs.append(df.iloc[:, i].values)\n'
        lnl__nnmgm += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return lnl__nnmgm


def _gen_parallel_flag_name(sanitized_cnames):
    xijv__gszlt = '_parallel_value'
    while xijv__gszlt in sanitized_cnames:
        xijv__gszlt = '_' + xijv__gszlt
    return xijv__gszlt


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(tutzl__fetx) for tutzl__fetx in
        col_names]
    lnl__nnmgm = 'def csv_reader_py(fname, nrows, skiprows):\n'
    lnl__nnmgm += _gen_csv_file_reader_init(parallel, header, compression, 
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    svlqi__nmuvr = globals()
    if idx_col_typ != types.none:
        svlqi__nmuvr[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        svlqi__nmuvr[f'table_type_{call_id}'] = types.none
    else:
        svlqi__nmuvr[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    lnl__nnmgm += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, svlqi__nmuvr, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        lnl__nnmgm += '  return (T, idx_arr)\n'
    else:
        lnl__nnmgm += '  return (T, None)\n'
    cyopz__fopn = {}
    svlqi__nmuvr['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(lnl__nnmgm, svlqi__nmuvr, cyopz__fopn)
    rjmm__fpaty = cyopz__fopn['csv_reader_py']
    qfmgz__pgkzq = numba.njit(rjmm__fpaty)
    compiled_funcs.append(qfmgz__pgkzq)
    return qfmgz__pgkzq
