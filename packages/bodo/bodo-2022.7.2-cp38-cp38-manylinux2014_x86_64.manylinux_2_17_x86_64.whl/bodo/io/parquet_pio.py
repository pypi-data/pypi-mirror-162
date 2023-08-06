import os
import warnings
from collections import defaultdict
from glob import has_magic
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow
import pyarrow as pa
import pyarrow.dataset as ds
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, get_definition, guard, mk_unique_var, next_label, replace_arg_nodes
from numba.extending import NativeValue, box, intrinsic, models, overload, register_model, unbox
from pyarrow._fs import PyFileSystem
from pyarrow.fs import FSSpecHandler
import bodo
import bodo.ir.parquet_ext
import bodo.utils.tracing as tracing
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import TableType
from bodo.io.fs_io import get_hdfs_fs, get_s3_fs_from_path, get_storage_options_pyobject, storage_options_dict_type
from bodo.io.helpers import _get_numba_typ_from_pa_typ, is_nullable
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.distributed_api import get_end, get_start
from bodo.libs.str_ext import unicode_to_utf8
from bodo.transforms import distributed_pass
from bodo.utils.transform import get_const_value
from bodo.utils.typing import BodoError, BodoWarning, FileInfo, get_overload_const_str
from bodo.utils.utils import check_and_propagate_cpp_exception, numba_to_c_type, sanitize_varname
REMOTE_FILESYSTEMS = {'s3', 'gcs', 'gs', 'http', 'hdfs', 'abfs', 'abfss'}
READ_STR_AS_DICT_THRESHOLD = 1.0
list_of_files_error_msg = (
    '. Make sure the list/glob passed to read_parquet() only contains paths to files (no directories)'
    )


class ParquetPredicateType(types.Type):

    def __init__(self):
        super(ParquetPredicateType, self).__init__(name=
            'ParquetPredicateType()')


parquet_predicate_type = ParquetPredicateType()
types.parquet_predicate_type = parquet_predicate_type
register_model(ParquetPredicateType)(models.OpaqueModel)


@unbox(ParquetPredicateType)
def unbox_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


@box(ParquetPredicateType)
def box_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return val


class ReadParquetFilepathType(types.Opaque):

    def __init__(self):
        super(ReadParquetFilepathType, self).__init__(name=
            'ReadParquetFilepathType')


read_parquet_fpath_type = ReadParquetFilepathType()
types.read_parquet_fpath_type = read_parquet_fpath_type
register_model(ReadParquetFilepathType)(models.OpaqueModel)


@unbox(ReadParquetFilepathType)
def unbox_read_parquet_fpath_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ParquetFileInfo(FileInfo):

    def __init__(self, columns, storage_options=None, input_file_name_col=
        None, read_as_dict_cols=None):
        self.columns = columns
        self.storage_options = storage_options
        self.input_file_name_col = input_file_name_col
        self.read_as_dict_cols = read_as_dict_cols
        super().__init__()

    def _get_schema(self, fname):
        try:
            return parquet_file_schema(fname, selected_columns=self.columns,
                storage_options=self.storage_options, input_file_name_col=
                self.input_file_name_col, read_as_dict_cols=self.
                read_as_dict_cols)
        except OSError as nzo__kht:
            if 'non-file path' in str(nzo__kht):
                raise FileNotFoundError(str(nzo__kht))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        bdj__omhgj = lhs.scope
        femtk__uplt = lhs.loc
        odtxa__kypxi = None
        if lhs.name in self.locals:
            odtxa__kypxi = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        uwbzj__giz = {}
        if lhs.name + ':convert' in self.locals:
            uwbzj__giz = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if odtxa__kypxi is None:
            iiuup__atavo = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            gjcxw__boxo = get_const_value(file_name, self.func_ir,
                iiuup__atavo, arg_types=self.args, file_info=
                ParquetFileInfo(columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            ltljl__zedls = False
            kdwz__mor = guard(get_definition, self.func_ir, file_name)
            if isinstance(kdwz__mor, ir.Arg):
                typ = self.args[kdwz__mor.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, iwybd__whsh, shc__rsmv, col_indices,
                        partition_names, epeh__hti, kmym__fsn) = typ.schema
                    ltljl__zedls = True
            if not ltljl__zedls:
                (col_names, iwybd__whsh, shc__rsmv, col_indices,
                    partition_names, epeh__hti, kmym__fsn) = (
                    parquet_file_schema(gjcxw__boxo, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            timaf__hroit = list(odtxa__kypxi.keys())
            rhu__focj = {c: zkb__jplkv for zkb__jplkv, c in enumerate(
                timaf__hroit)}
            ehe__clg = [vedft__cnytj for vedft__cnytj in odtxa__kypxi.values()]
            shc__rsmv = 'index' if 'index' in rhu__focj else None
            if columns is None:
                selected_columns = timaf__hroit
            else:
                selected_columns = columns
            col_indices = [rhu__focj[c] for c in selected_columns]
            iwybd__whsh = [ehe__clg[rhu__focj[c]] for c in selected_columns]
            col_names = selected_columns
            shc__rsmv = shc__rsmv if shc__rsmv in col_names else None
            partition_names = []
            epeh__hti = []
            kmym__fsn = []
        yjz__gtd = None if isinstance(shc__rsmv, dict
            ) or shc__rsmv is None else shc__rsmv
        index_column_index = None
        index_column_type = types.none
        if yjz__gtd:
            jtr__gji = col_names.index(yjz__gtd)
            index_column_index = col_indices.pop(jtr__gji)
            index_column_type = iwybd__whsh.pop(jtr__gji)
            col_names.pop(jtr__gji)
        for zkb__jplkv, c in enumerate(col_names):
            if c in uwbzj__giz:
                iwybd__whsh[zkb__jplkv] = uwbzj__giz[c]
        eaywo__ivqs = [ir.Var(bdj__omhgj, mk_unique_var('pq_table'),
            femtk__uplt), ir.Var(bdj__omhgj, mk_unique_var('pq_index'),
            femtk__uplt)]
        yvxuw__wpa = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, iwybd__whsh, eaywo__ivqs, femtk__uplt,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, epeh__hti, kmym__fsn)]
        return (col_names, eaywo__ivqs, shc__rsmv, yvxuw__wpa, iwybd__whsh,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    nykw__csj = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    nprd__vrm, bmar__csfnd = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(nprd__vrm.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, nprd__vrm, bmar__csfnd, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    tvpru__ter = ', '.join(f'out{zkb__jplkv}' for zkb__jplkv in range(
        nykw__csj))
    iac__vlcm = f'def pq_impl(fname, {extra_args}):\n'
    iac__vlcm += (
        f'    (total_rows, {tvpru__ter},) = _pq_reader_py(fname, {extra_args})\n'
        )
    orbwm__fnzcb = {}
    exec(iac__vlcm, {}, orbwm__fnzcb)
    czu__igy = orbwm__fnzcb['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        tnh__tunok = pq_node.loc.strformat()
        moxd__omphb = []
        nod__shaw = []
        for zkb__jplkv in pq_node.out_used_cols:
            abbh__cxqmv = pq_node.df_colnames[zkb__jplkv]
            moxd__omphb.append(abbh__cxqmv)
            if isinstance(pq_node.out_types[zkb__jplkv], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                nod__shaw.append(abbh__cxqmv)
        wdoz__ryxm = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', wdoz__ryxm,
            tnh__tunok, moxd__omphb)
        if nod__shaw:
            kims__nryr = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', kims__nryr,
                tnh__tunok, nod__shaw)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        flqu__kvuhl = set(pq_node.out_used_cols)
        ovk__vsp = set(pq_node.unsupported_columns)
        tmnws__qsf = flqu__kvuhl & ovk__vsp
        if tmnws__qsf:
            omb__govu = sorted(tmnws__qsf)
            lou__nqy = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            xwzqr__uhlgh = 0
            for mjav__eda in omb__govu:
                while pq_node.unsupported_columns[xwzqr__uhlgh] != mjav__eda:
                    xwzqr__uhlgh += 1
                lou__nqy.append(
                    f"Column '{pq_node.df_colnames[mjav__eda]}' with unsupported arrow type {pq_node.unsupported_arrow_types[xwzqr__uhlgh]}"
                    )
                xwzqr__uhlgh += 1
            dap__agd = '\n'.join(lou__nqy)
            raise BodoError(dap__agd, loc=pq_node.loc)
    qyn__thuuh = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.out_used_cols, pq_node.out_types, pq_node.storage_options,
        pq_node.partition_names, dnf_filter_str, expr_filter_str,
        extra_args, parallel, meta_head_only_info, pq_node.
        index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    kmfro__fsd = typemap[pq_node.file_name.name]
    bcjh__wer = (kmfro__fsd,) + tuple(typemap[wkjta__zuet.name] for
        wkjta__zuet in bmar__csfnd)
    puzdc__wln = compile_to_numba_ir(czu__igy, {'_pq_reader_py': qyn__thuuh
        }, typingctx=typingctx, targetctx=targetctx, arg_typs=bcjh__wer,
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(puzdc__wln, [pq_node.file_name] + bmar__csfnd)
    yvxuw__wpa = puzdc__wln.body[:-3]
    if meta_head_only_info:
        yvxuw__wpa[-3].target = meta_head_only_info[1]
    yvxuw__wpa[-2].target = pq_node.out_vars[0]
    yvxuw__wpa[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        yvxuw__wpa.pop(-1)
    elif not pq_node.out_used_cols:
        yvxuw__wpa.pop(-2)
    return yvxuw__wpa


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    yncp__ixqok = get_overload_const_str(dnf_filter_str)
    mzald__rmhow = get_overload_const_str(expr_filter_str)
    maenv__gcl = ', '.join(f'f{zkb__jplkv}' for zkb__jplkv in range(len(
        var_tup)))
    iac__vlcm = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        iac__vlcm += f'  {maenv__gcl}, = var_tup\n'
    iac__vlcm += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    iac__vlcm += f'    dnf_filters_py = {yncp__ixqok}\n'
    iac__vlcm += f'    expr_filters_py = {mzald__rmhow}\n'
    iac__vlcm += '  return (dnf_filters_py, expr_filters_py)\n'
    orbwm__fnzcb = {}
    exec(iac__vlcm, globals(), orbwm__fnzcb)
    return orbwm__fnzcb['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    ltl__iaan = next_label()
    pwcc__hdtv = ',' if extra_args else ''
    iac__vlcm = f'def pq_reader_py(fname,{extra_args}):\n'
    iac__vlcm += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    iac__vlcm += f"    ev.add_attribute('g_fname', fname)\n"
    iac__vlcm += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{pwcc__hdtv}))
"""
    iac__vlcm += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    iac__vlcm += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    dtddl__nmwo = not out_used_cols
    mbdus__dgt = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    xsgip__eoj = {c: zkb__jplkv for zkb__jplkv, c in enumerate(col_indices)}
    cgw__voh = {c: zkb__jplkv for zkb__jplkv, c in enumerate(mbdus__dgt)}
    wgpuv__ivpc = []
    ffpei__kys = set()
    bxtua__pmiqz = partition_names + [input_file_name_col]
    for zkb__jplkv in out_used_cols:
        if mbdus__dgt[zkb__jplkv] not in bxtua__pmiqz:
            wgpuv__ivpc.append(col_indices[zkb__jplkv])
        elif not input_file_name_col or mbdus__dgt[zkb__jplkv
            ] != input_file_name_col:
            ffpei__kys.add(col_indices[zkb__jplkv])
    if index_column_index is not None:
        wgpuv__ivpc.append(index_column_index)
    wgpuv__ivpc = sorted(wgpuv__ivpc)
    hygx__uynt = {c: zkb__jplkv for zkb__jplkv, c in enumerate(wgpuv__ivpc)}
    iodze__rduj = [(int(is_nullable(out_types[xsgip__eoj[npige__wwrid]])) if
        npige__wwrid != index_column_index else int(is_nullable(
        index_column_type))) for npige__wwrid in wgpuv__ivpc]
    str_as_dict_cols = []
    for npige__wwrid in wgpuv__ivpc:
        if npige__wwrid == index_column_index:
            vedft__cnytj = index_column_type
        else:
            vedft__cnytj = out_types[xsgip__eoj[npige__wwrid]]
        if vedft__cnytj == dict_str_arr_type:
            str_as_dict_cols.append(npige__wwrid)
    ymjin__senu = []
    jmyeo__lgejv = {}
    itexg__ivi = []
    ieamr__tlqz = []
    for zkb__jplkv, itr__zqx in enumerate(partition_names):
        try:
            zlt__xjir = cgw__voh[itr__zqx]
            if col_indices[zlt__xjir] not in ffpei__kys:
                continue
        except (KeyError, ValueError) as tlbw__vpfoj:
            continue
        jmyeo__lgejv[itr__zqx] = len(ymjin__senu)
        ymjin__senu.append(itr__zqx)
        itexg__ivi.append(zkb__jplkv)
        xjosp__zuzt = out_types[zlt__xjir].dtype
        nzl__djh = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            xjosp__zuzt)
        ieamr__tlqz.append(numba_to_c_type(nzl__djh))
    iac__vlcm += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    iac__vlcm += f'    out_table = pq_read(\n'
    iac__vlcm += f'        fname_py, {is_parallel},\n'
    iac__vlcm += f'        dnf_filters, expr_filters,\n'
    iac__vlcm += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{ltl__iaan}.ctypes,
"""
    iac__vlcm += f'        {len(wgpuv__ivpc)},\n'
    iac__vlcm += f'        nullable_cols_arr_{ltl__iaan}.ctypes,\n'
    if len(itexg__ivi) > 0:
        iac__vlcm += (
            f'        np.array({itexg__ivi}, dtype=np.int32).ctypes,\n')
        iac__vlcm += (
            f'        np.array({ieamr__tlqz}, dtype=np.int32).ctypes,\n')
        iac__vlcm += f'        {len(itexg__ivi)},\n'
    else:
        iac__vlcm += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        iac__vlcm += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        iac__vlcm += f'        0, 0,\n'
    iac__vlcm += f'        total_rows_np.ctypes,\n'
    iac__vlcm += f'        {input_file_name_col is not None},\n'
    iac__vlcm += f'    )\n'
    iac__vlcm += f'    check_and_propagate_cpp_exception()\n'
    gtfd__lcki = 'None'
    mfj__rxa = index_column_type
    jrk__kspqc = TableType(tuple(out_types))
    if dtddl__nmwo:
        jrk__kspqc = types.none
    if index_column_index is not None:
        olwml__upt = hygx__uynt[index_column_index]
        gtfd__lcki = (
            f'info_to_array(info_from_table(out_table, {olwml__upt}), index_arr_type)'
            )
    iac__vlcm += f'    index_arr = {gtfd__lcki}\n'
    if dtddl__nmwo:
        pydta__jew = None
    else:
        pydta__jew = []
        jlf__lss = 0
        bwvif__sxfqw = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for zkb__jplkv, mjav__eda in enumerate(col_indices):
            if jlf__lss < len(out_used_cols) and zkb__jplkv == out_used_cols[
                jlf__lss]:
                lvcu__qaxy = col_indices[zkb__jplkv]
                if bwvif__sxfqw and lvcu__qaxy == bwvif__sxfqw:
                    pydta__jew.append(len(wgpuv__ivpc) + len(ymjin__senu))
                elif lvcu__qaxy in ffpei__kys:
                    njctq__vwuy = mbdus__dgt[zkb__jplkv]
                    pydta__jew.append(len(wgpuv__ivpc) + jmyeo__lgejv[
                        njctq__vwuy])
                else:
                    pydta__jew.append(hygx__uynt[mjav__eda])
                jlf__lss += 1
            else:
                pydta__jew.append(-1)
        pydta__jew = np.array(pydta__jew, dtype=np.int64)
    if dtddl__nmwo:
        iac__vlcm += '    T = None\n'
    else:
        iac__vlcm += f"""    T = cpp_table_to_py_table(out_table, table_idx_{ltl__iaan}, py_table_type_{ltl__iaan})
"""
    iac__vlcm += f'    delete_table(out_table)\n'
    iac__vlcm += f'    total_rows = total_rows_np[0]\n'
    iac__vlcm += f'    ev.finalize()\n'
    iac__vlcm += f'    return (total_rows, T, index_arr)\n'
    orbwm__fnzcb = {}
    eodmy__jsk = {f'py_table_type_{ltl__iaan}': jrk__kspqc,
        f'table_idx_{ltl__iaan}': pydta__jew,
        f'selected_cols_arr_{ltl__iaan}': np.array(wgpuv__ivpc, np.int32),
        f'nullable_cols_arr_{ltl__iaan}': np.array(iodze__rduj, np.int32),
        'index_arr_type': mfj__rxa, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(iac__vlcm, eodmy__jsk, orbwm__fnzcb)
    qyn__thuuh = orbwm__fnzcb['pq_reader_py']
    lplj__cmm = numba.njit(qyn__thuuh, no_cpython_wrapper=True)
    return lplj__cmm


def unify_schemas(schemas):
    beqr__wmyip = []
    for schema in schemas:
        for zkb__jplkv in range(len(schema)):
            lldt__ambp = schema.field(zkb__jplkv)
            if lldt__ambp.type == pa.large_string():
                schema = schema.set(zkb__jplkv, lldt__ambp.with_type(pa.
                    string()))
            elif lldt__ambp.type == pa.large_binary():
                schema = schema.set(zkb__jplkv, lldt__ambp.with_type(pa.
                    binary()))
            elif isinstance(lldt__ambp.type, (pa.ListType, pa.LargeListType)
                ) and lldt__ambp.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(zkb__jplkv, lldt__ambp.with_type(pa.
                    list_(pa.field(lldt__ambp.type.value_field.name, pa.
                    string()))))
            elif isinstance(lldt__ambp.type, pa.LargeListType):
                schema = schema.set(zkb__jplkv, lldt__ambp.with_type(pa.
                    list_(pa.field(lldt__ambp.type.value_field.name,
                    lldt__ambp.type.value_type))))
        beqr__wmyip.append(schema)
    return pa.unify_schemas(beqr__wmyip)


class ParquetDataset(object):

    def __init__(self, pa_pq_dataset, prefix=''):
        self.schema = pa_pq_dataset.schema
        self.filesystem = None
        self._bodo_total_rows = 0
        self._prefix = prefix
        self.partitioning = None
        partitioning = pa_pq_dataset.partitioning
        self.partition_names = ([] if partitioning is None or partitioning.
            schema == pa_pq_dataset.schema else list(partitioning.schema.names)
            )
        if self.partition_names:
            self.partitioning_dictionaries = partitioning.dictionaries
            self.partitioning_cls = partitioning.__class__
            self.partitioning_schema = partitioning.schema
        else:
            self.partitioning_dictionaries = {}
        for zkb__jplkv in range(len(self.schema)):
            lldt__ambp = self.schema.field(zkb__jplkv)
            if lldt__ambp.type == pa.large_string():
                self.schema = self.schema.set(zkb__jplkv, lldt__ambp.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for hcm__ngmo in self.pieces:
            hcm__ngmo.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            fsg__cqno = {hcm__ngmo: self.partitioning_dictionaries[
                zkb__jplkv] for zkb__jplkv, hcm__ngmo in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, fsg__cqno)


class ParquetPiece(object):

    def __init__(self, frag, partitioning, partition_names):
        self._frag = None
        self.format = frag.format
        self.path = frag.path
        self._bodo_num_rows = 0
        self.partition_keys = []
        if partitioning is not None:
            self.partition_keys = ds._get_partition_keys(frag.
                partition_expression)
            self.partition_keys = [(itr__zqx, partitioning.dictionaries[
                zkb__jplkv].index(self.partition_keys[itr__zqx]).as_py()) for
                zkb__jplkv, itr__zqx in enumerate(partition_names)]

    @property
    def frag(self):
        if self._frag is None:
            self._frag = self.format.make_fragment(self.path, self.filesystem)
            del self.format
        return self._frag

    @property
    def metadata(self):
        return self.frag.metadata

    @property
    def num_row_groups(self):
        return self.frag.num_row_groups


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None, typing_pa_schema=None,
    partitioning='hive'):
    if get_row_counts:
        fist__ckd = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    ydijh__xpzf = MPI.COMM_WORLD
    if isinstance(fpath, list):
        cgah__kib = urlparse(fpath[0])
        protocol = cgah__kib.scheme
        jmgj__susj = cgah__kib.netloc
        for zkb__jplkv in range(len(fpath)):
            lldt__ambp = fpath[zkb__jplkv]
            hgn__jnqkp = urlparse(lldt__ambp)
            if hgn__jnqkp.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if hgn__jnqkp.netloc != jmgj__susj:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[zkb__jplkv] = lldt__ambp.rstrip('/')
    else:
        cgah__kib = urlparse(fpath)
        protocol = cgah__kib.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as tlbw__vpfoj:
            ukx__qngg = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(ukx__qngg)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as tlbw__vpfoj:
            ukx__qngg = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
"""
    fs = []

    def getfs(parallel=False):
        if len(fs) == 1:
            return fs[0]
        if protocol == 's3':
            fs.append(get_s3_fs_from_path(fpath, parallel=parallel,
                storage_options=storage_options) if not isinstance(fpath,
                list) else get_s3_fs_from_path(fpath[0], parallel=parallel,
                storage_options=storage_options))
        elif protocol in {'gcs', 'gs'}:
            zcn__rzicj = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(zcn__rzicj)))
        elif protocol == 'http':
            fs.append(PyFileSystem(FSSpecHandler(fsspec.filesystem('http'))))
        elif protocol in {'hdfs', 'abfs', 'abfss'}:
            fs.append(get_hdfs_fs(fpath) if not isinstance(fpath, list) else
                get_hdfs_fs(fpath[0]))
        else:
            fs.append(pa.fs.LocalFileSystem())
        return fs[0]

    def glob(protocol, fs, path):
        if not protocol and fs is None:
            from fsspec.implementations.local import LocalFileSystem
            fs = LocalFileSystem()
        if isinstance(fs, pa.fs.FileSystem):
            from fsspec.implementations.arrow import ArrowFSWrapper
            fs = ArrowFSWrapper(fs)
        try:
            hfx__mepd = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(hfx__mepd) == 0:
            raise BodoError('No files found matching glob pattern')
        return hfx__mepd
    iza__pao = False
    if get_row_counts:
        emu__oxbu = getfs(parallel=True)
        iza__pao = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        qflv__fwlg = 1
        hgj__byqu = os.cpu_count()
        if hgj__byqu is not None and hgj__byqu > 1:
            qflv__fwlg = hgj__byqu // 2
        try:
            if get_row_counts:
                xde__ujmiv = tracing.Event('pq.ParquetDataset', is_parallel
                    =False)
                if tracing.is_tracing():
                    xde__ujmiv.add_attribute('g_dnf_filter', str(dnf_filters))
            clev__mkl = pa.io_thread_count()
            pa.set_io_thread_count(qflv__fwlg)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{cgah__kib.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    mqn__oaf = [lldt__ambp[len(prefix):] for lldt__ambp in
                        fpath]
                else:
                    mqn__oaf = fpath[len(prefix):]
            else:
                mqn__oaf = fpath
            if isinstance(mqn__oaf, list):
                bdu__yge = []
                for hcm__ngmo in mqn__oaf:
                    if has_magic(hcm__ngmo):
                        bdu__yge += glob(protocol, getfs(), hcm__ngmo)
                    else:
                        bdu__yge.append(hcm__ngmo)
                mqn__oaf = bdu__yge
            elif has_magic(mqn__oaf):
                mqn__oaf = glob(protocol, getfs(), mqn__oaf)
            xrrc__wpncd = pq.ParquetDataset(mqn__oaf, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                xrrc__wpncd._filters = dnf_filters
                xrrc__wpncd._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            ocfp__fgx = len(xrrc__wpncd.files)
            xrrc__wpncd = ParquetDataset(xrrc__wpncd, prefix)
            pa.set_io_thread_count(clev__mkl)
            if typing_pa_schema:
                xrrc__wpncd.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    xde__ujmiv.add_attribute('num_pieces_before_filter',
                        ocfp__fgx)
                    xde__ujmiv.add_attribute('num_pieces_after_filter', len
                        (xrrc__wpncd.pieces))
                xde__ujmiv.finalize()
        except Exception as nzo__kht:
            if isinstance(nzo__kht, IsADirectoryError):
                nzo__kht = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(nzo__kht, (OSError,
                FileNotFoundError)):
                nzo__kht = BodoError(str(nzo__kht) + list_of_files_error_msg)
            else:
                nzo__kht = BodoError(
                    f"""error from pyarrow: {type(nzo__kht).__name__}: {str(nzo__kht)}
"""
                    )
            ydijh__xpzf.bcast(nzo__kht)
            raise nzo__kht
        if get_row_counts:
            fnh__zvv = tracing.Event('bcast dataset')
        xrrc__wpncd = ydijh__xpzf.bcast(xrrc__wpncd)
    else:
        if get_row_counts:
            fnh__zvv = tracing.Event('bcast dataset')
        xrrc__wpncd = ydijh__xpzf.bcast(None)
        if isinstance(xrrc__wpncd, Exception):
            ply__qtxv = xrrc__wpncd
            raise ply__qtxv
    xrrc__wpncd.set_fs(getfs())
    if get_row_counts:
        fnh__zvv.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = iza__pao = False
    if get_row_counts or iza__pao:
        if get_row_counts and tracing.is_tracing():
            bnltz__rzje = tracing.Event('get_row_counts')
            bnltz__rzje.add_attribute('g_num_pieces', len(xrrc__wpncd.pieces))
            bnltz__rzje.add_attribute('g_expr_filters', str(expr_filters))
        dap__xsuif = 0.0
        num_pieces = len(xrrc__wpncd.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        opfk__sozx = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        mgr__sqg = 0
        xizjw__kav = 0
        nyvqw__sjrz = 0
        xgjgj__ukn = True
        if expr_filters is not None:
            import random
            random.seed(37)
            tub__ivws = random.sample(xrrc__wpncd.pieces, k=len(xrrc__wpncd
                .pieces))
        else:
            tub__ivws = xrrc__wpncd.pieces
        fpaths = [hcm__ngmo.path for hcm__ngmo in tub__ivws[start:opfk__sozx]]
        qflv__fwlg = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(qflv__fwlg)
        pa.set_cpu_count(qflv__fwlg)
        ply__qtxv = None
        try:
            ixse__wuisg = ds.dataset(fpaths, filesystem=xrrc__wpncd.
                filesystem, partitioning=xrrc__wpncd.partitioning)
            for gbm__lkgt, frag in zip(tub__ivws[start:opfk__sozx],
                ixse__wuisg.get_fragments()):
                if iza__pao:
                    oml__vspea = frag.metadata.schema.to_arrow_schema()
                    cpeiw__ilc = set(oml__vspea.names)
                    dvsb__ukkf = set(xrrc__wpncd.schema.names) - set(
                        xrrc__wpncd.partition_names)
                    if dvsb__ukkf != cpeiw__ilc:
                        wcecs__klwp = cpeiw__ilc - dvsb__ukkf
                        lnkop__sdorg = dvsb__ukkf - cpeiw__ilc
                        iiuup__atavo = (
                            f'Schema in {gbm__lkgt} was different.\n')
                        if wcecs__klwp:
                            iiuup__atavo += f"""File contains column(s) {wcecs__klwp} not found in other files in the dataset.
"""
                        if lnkop__sdorg:
                            iiuup__atavo += f"""File missing column(s) {lnkop__sdorg} found in other files in the dataset.
"""
                        raise BodoError(iiuup__atavo)
                    try:
                        xrrc__wpncd.schema = unify_schemas([xrrc__wpncd.
                            schema, oml__vspea])
                    except Exception as nzo__kht:
                        iiuup__atavo = (
                            f'Schema in {gbm__lkgt} was different.\n' + str
                            (nzo__kht))
                        raise BodoError(iiuup__atavo)
                urhfd__wpbpf = time.time()
                ixyj__mbax = frag.scanner(schema=ixse__wuisg.schema, filter
                    =expr_filters, use_threads=True).count_rows()
                dap__xsuif += time.time() - urhfd__wpbpf
                gbm__lkgt._bodo_num_rows = ixyj__mbax
                mgr__sqg += ixyj__mbax
                xizjw__kav += frag.num_row_groups
                nyvqw__sjrz += sum(tqbx__kxqyt.total_byte_size for
                    tqbx__kxqyt in frag.row_groups)
        except Exception as nzo__kht:
            ply__qtxv = nzo__kht
        if ydijh__xpzf.allreduce(ply__qtxv is not None, op=MPI.LOR):
            for ply__qtxv in ydijh__xpzf.allgather(ply__qtxv):
                if ply__qtxv:
                    if isinstance(fpath, list) and isinstance(ply__qtxv, (
                        OSError, FileNotFoundError)):
                        raise BodoError(str(ply__qtxv) +
                            list_of_files_error_msg)
                    raise ply__qtxv
        if iza__pao:
            xgjgj__ukn = ydijh__xpzf.allreduce(xgjgj__ukn, op=MPI.LAND)
            if not xgjgj__ukn:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            xrrc__wpncd._bodo_total_rows = ydijh__xpzf.allreduce(mgr__sqg,
                op=MPI.SUM)
            lzl__wucln = ydijh__xpzf.allreduce(xizjw__kav, op=MPI.SUM)
            gpafw__sdzlh = ydijh__xpzf.allreduce(nyvqw__sjrz, op=MPI.SUM)
            ptd__ivnm = np.array([hcm__ngmo._bodo_num_rows for hcm__ngmo in
                xrrc__wpncd.pieces])
            ptd__ivnm = ydijh__xpzf.allreduce(ptd__ivnm, op=MPI.SUM)
            for hcm__ngmo, cfxs__vrjkt in zip(xrrc__wpncd.pieces, ptd__ivnm):
                hcm__ngmo._bodo_num_rows = cfxs__vrjkt
            if is_parallel and bodo.get_rank(
                ) == 0 and lzl__wucln < bodo.get_size() and lzl__wucln != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({lzl__wucln}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if lzl__wucln == 0:
                nhheb__inx = 0
            else:
                nhheb__inx = gpafw__sdzlh // lzl__wucln
            if (bodo.get_rank() == 0 and gpafw__sdzlh >= 20 * 1048576 and 
                nhheb__inx < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({nhheb__inx} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                bnltz__rzje.add_attribute('g_total_num_row_groups', lzl__wucln)
                bnltz__rzje.add_attribute('total_scan_time', dap__xsuif)
                pic__vedde = np.array([hcm__ngmo._bodo_num_rows for
                    hcm__ngmo in xrrc__wpncd.pieces])
                foym__zqamo = np.percentile(pic__vedde, [25, 50, 75])
                bnltz__rzje.add_attribute('g_row_counts_min', pic__vedde.min())
                bnltz__rzje.add_attribute('g_row_counts_Q1', foym__zqamo[0])
                bnltz__rzje.add_attribute('g_row_counts_median', foym__zqamo[1]
                    )
                bnltz__rzje.add_attribute('g_row_counts_Q3', foym__zqamo[2])
                bnltz__rzje.add_attribute('g_row_counts_max', pic__vedde.max())
                bnltz__rzje.add_attribute('g_row_counts_mean', pic__vedde.
                    mean())
                bnltz__rzje.add_attribute('g_row_counts_std', pic__vedde.std())
                bnltz__rzje.add_attribute('g_row_counts_sum', pic__vedde.sum())
                bnltz__rzje.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(xrrc__wpncd)
    if get_row_counts:
        fist__ckd.finalize()
    if iza__pao and is_parallel:
        if tracing.is_tracing():
            ukj__lka = tracing.Event('unify_schemas_across_ranks')
        ply__qtxv = None
        try:
            xrrc__wpncd.schema = ydijh__xpzf.allreduce(xrrc__wpncd.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as nzo__kht:
            ply__qtxv = nzo__kht
        if tracing.is_tracing():
            ukj__lka.finalize()
        if ydijh__xpzf.allreduce(ply__qtxv is not None, op=MPI.LOR):
            for ply__qtxv in ydijh__xpzf.allgather(ply__qtxv):
                if ply__qtxv:
                    iiuup__atavo = (
                        f'Schema in some files were different.\n' + str(
                        ply__qtxv))
                    raise BodoError(iiuup__atavo)
    return xrrc__wpncd


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    hgj__byqu = os.cpu_count()
    if hgj__byqu is None or hgj__byqu == 0:
        hgj__byqu = 2
    ahfw__dgus = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), hgj__byqu)
    oit__vbhli = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), hgj__byqu)
    if is_parallel and len(fpaths) > oit__vbhli and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(oit__vbhli)
        pa.set_cpu_count(oit__vbhli)
    else:
        pa.set_io_thread_count(ahfw__dgus)
        pa.set_cpu_count(ahfw__dgus)
    ngc__uuetf = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    fov__eeon = set(str_as_dict_cols)
    for zkb__jplkv, name in enumerate(schema.names):
        if name in fov__eeon:
            qcnlu__fhho = schema.field(zkb__jplkv)
            govcr__xen = pa.field(name, pa.dictionary(pa.int32(),
                qcnlu__fhho.type), qcnlu__fhho.nullable)
            schema = schema.remove(zkb__jplkv).insert(zkb__jplkv, govcr__xen)
    xrrc__wpncd = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=ngc__uuetf)
    col_names = xrrc__wpncd.schema.names
    kxz__jwylk = [col_names[prze__vkj] for prze__vkj in selected_fields]
    fqwf__juga = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if fqwf__juga and expr_filters is None:
        btch__oqg = []
        pwv__mgf = 0
        hou__lui = 0
        for frag in xrrc__wpncd.get_fragments():
            kroa__nwolt = []
            for tqbx__kxqyt in frag.row_groups:
                uzn__wowxb = tqbx__kxqyt.num_rows
                if start_offset < pwv__mgf + uzn__wowxb:
                    if hou__lui == 0:
                        luojs__lctku = start_offset - pwv__mgf
                        ttu__nqto = min(uzn__wowxb - luojs__lctku, rows_to_read
                            )
                    else:
                        ttu__nqto = min(uzn__wowxb, rows_to_read - hou__lui)
                    hou__lui += ttu__nqto
                    kroa__nwolt.append(tqbx__kxqyt.id)
                pwv__mgf += uzn__wowxb
                if hou__lui == rows_to_read:
                    break
            btch__oqg.append(frag.subset(row_group_ids=kroa__nwolt))
            if hou__lui == rows_to_read:
                break
        xrrc__wpncd = ds.FileSystemDataset(btch__oqg, xrrc__wpncd.schema,
            ngc__uuetf, filesystem=xrrc__wpncd.filesystem)
        start_offset = luojs__lctku
    rcpsm__chl = xrrc__wpncd.scanner(columns=kxz__jwylk, filter=
        expr_filters, use_threads=True).to_reader()
    return xrrc__wpncd, rcpsm__chl, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    gfewm__gtsaf = [c for c in pa_schema.names if isinstance(pa_schema.
        field(c).type, pa.DictionaryType) and c not in pq_dataset.
        partition_names]
    if len(gfewm__gtsaf) == 0:
        pq_dataset._category_info = {}
        return
    ydijh__xpzf = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            ttu__pzrk = pq_dataset.pieces[0].frag.head(100, columns=
                gfewm__gtsaf)
            aztvm__whduu = {c: tuple(ttu__pzrk.column(c).chunk(0).
                dictionary.to_pylist()) for c in gfewm__gtsaf}
            del ttu__pzrk
        except Exception as nzo__kht:
            ydijh__xpzf.bcast(nzo__kht)
            raise nzo__kht
        ydijh__xpzf.bcast(aztvm__whduu)
    else:
        aztvm__whduu = ydijh__xpzf.bcast(None)
        if isinstance(aztvm__whduu, Exception):
            ply__qtxv = aztvm__whduu
            raise ply__qtxv
    pq_dataset._category_info = aztvm__whduu


def get_pandas_metadata(schema, num_pieces):
    shc__rsmv = None
    qdd__aojy = defaultdict(lambda : None)
    hqs__jrar = b'pandas'
    if schema.metadata is not None and hqs__jrar in schema.metadata:
        import json
        bgj__qaviz = json.loads(schema.metadata[hqs__jrar].decode('utf8'))
        iyif__cxzne = len(bgj__qaviz['index_columns'])
        if iyif__cxzne > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        shc__rsmv = bgj__qaviz['index_columns'][0] if iyif__cxzne else None
        if not isinstance(shc__rsmv, str) and not isinstance(shc__rsmv, dict):
            shc__rsmv = None
        for axoz__kvg in bgj__qaviz['columns']:
            nmj__fsg = axoz__kvg['name']
            if axoz__kvg['pandas_type'].startswith('int'
                ) and nmj__fsg is not None:
                if axoz__kvg['numpy_type'].startswith('Int'):
                    qdd__aojy[nmj__fsg] = True
                else:
                    qdd__aojy[nmj__fsg] = False
    return shc__rsmv, qdd__aojy


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for nmj__fsg in pa_schema.names:
        hgkif__nkvdq = pa_schema.field(nmj__fsg)
        if hgkif__nkvdq.type in (pa.string(), pa.large_string()):
            str_columns.append(nmj__fsg)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    ydijh__xpzf = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        tub__ivws = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        tub__ivws = pq_dataset.pieces
    isoq__ilq = np.zeros(len(str_columns), dtype=np.int64)
    kbgo__vfjso = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(tub__ivws):
        gbm__lkgt = tub__ivws[bodo.get_rank()]
        try:
            metadata = gbm__lkgt.metadata
            for zkb__jplkv in range(gbm__lkgt.num_row_groups):
                for jlf__lss, nmj__fsg in enumerate(str_columns):
                    xwzqr__uhlgh = pa_schema.get_field_index(nmj__fsg)
                    isoq__ilq[jlf__lss] += metadata.row_group(zkb__jplkv
                        ).column(xwzqr__uhlgh).total_uncompressed_size
            sbrp__jvbhq = metadata.num_rows
        except Exception as nzo__kht:
            if isinstance(nzo__kht, (OSError, FileNotFoundError)):
                sbrp__jvbhq = 0
            else:
                raise
    else:
        sbrp__jvbhq = 0
    ekrr__ccl = ydijh__xpzf.allreduce(sbrp__jvbhq, op=MPI.SUM)
    if ekrr__ccl == 0:
        return set()
    ydijh__xpzf.Allreduce(isoq__ilq, kbgo__vfjso, op=MPI.SUM)
    ifd__jwz = kbgo__vfjso / ekrr__ccl
    tvfl__rxxje = set()
    for zkb__jplkv, nbc__tlnzg in enumerate(ifd__jwz):
        if nbc__tlnzg < READ_STR_AS_DICT_THRESHOLD:
            nmj__fsg = str_columns[zkb__jplkv][0]
            tvfl__rxxje.add(nmj__fsg)
    return tvfl__rxxje


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    iwybd__whsh = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    tvveb__gmgmd = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    frhdk__wmx = read_as_dict_cols - tvveb__gmgmd
    if len(frhdk__wmx) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {frhdk__wmx}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(tvveb__gmgmd)
    tvveb__gmgmd = tvveb__gmgmd - read_as_dict_cols
    str_columns = [alru__gbx for alru__gbx in str_columns if alru__gbx in
        tvveb__gmgmd]
    tvfl__rxxje: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    tvfl__rxxje.update(read_as_dict_cols)
    col_names = pa_schema.names
    shc__rsmv, qdd__aojy = get_pandas_metadata(pa_schema, num_pieces)
    ehe__clg = []
    ftq__fafj = []
    opnx__iicm = []
    for zkb__jplkv, c in enumerate(col_names):
        if c in partition_names:
            continue
        hgkif__nkvdq = pa_schema.field(c)
        pcctz__slzo, fenc__wwce = _get_numba_typ_from_pa_typ(hgkif__nkvdq, 
            c == shc__rsmv, qdd__aojy[c], pq_dataset._category_info,
            str_as_dict=c in tvfl__rxxje)
        ehe__clg.append(pcctz__slzo)
        ftq__fafj.append(fenc__wwce)
        opnx__iicm.append(hgkif__nkvdq.type)
    if partition_names:
        ehe__clg += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[zkb__jplkv]) for zkb__jplkv in range(
            len(partition_names))]
        ftq__fafj.extend([True] * len(partition_names))
        opnx__iicm.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        ehe__clg += [dict_str_arr_type]
        ftq__fafj.append(True)
        opnx__iicm.append(None)
    ycm__cpz = {c: zkb__jplkv for zkb__jplkv, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in ycm__cpz:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if shc__rsmv and not isinstance(shc__rsmv, dict
        ) and shc__rsmv not in selected_columns:
        selected_columns.append(shc__rsmv)
    col_names = selected_columns
    col_indices = []
    iwybd__whsh = []
    epeh__hti = []
    kmym__fsn = []
    for zkb__jplkv, c in enumerate(col_names):
        lvcu__qaxy = ycm__cpz[c]
        col_indices.append(lvcu__qaxy)
        iwybd__whsh.append(ehe__clg[lvcu__qaxy])
        if not ftq__fafj[lvcu__qaxy]:
            epeh__hti.append(zkb__jplkv)
            kmym__fsn.append(opnx__iicm[lvcu__qaxy])
    return (col_names, iwybd__whsh, shc__rsmv, col_indices, partition_names,
        epeh__hti, kmym__fsn)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    jph__upxf = dictionary.to_pandas()
    jzcfa__riqz = bodo.typeof(jph__upxf).dtype
    if isinstance(jzcfa__riqz, types.Integer):
        yrtpm__gczig = PDCategoricalDtype(tuple(jph__upxf), jzcfa__riqz, 
            False, int_type=jzcfa__riqz)
    else:
        yrtpm__gczig = PDCategoricalDtype(tuple(jph__upxf), jzcfa__riqz, False)
    return CategoricalArrayType(yrtpm__gczig)


_pq_read = types.ExternalFunction('pq_read', table_type(
    read_parquet_fpath_type, types.boolean, parquet_predicate_type,
    parquet_predicate_type, storage_options_dict_type, types.int64, types.
    voidptr, types.int32, types.voidptr, types.voidptr, types.voidptr,
    types.int32, types.voidptr, types.int32, types.voidptr, types.boolean))
from llvmlite import ir as lir
from numba.core import cgutils
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('pq_read', arrow_cpp.pq_read)
    ll.add_symbol('pq_write', arrow_cpp.pq_write)
    ll.add_symbol('pq_write_partitioned', arrow_cpp.pq_write_partitioned)


@intrinsic
def parquet_write_table_cpp(typingctx, filename_t, table_t, col_names_t,
    index_t, write_index, metadata_t, compression_t, is_parallel_t,
    write_range_index, start, stop, step, name, bucket_region,
    row_group_size, file_prefix):

    def codegen(context, builder, sig, args):
        rmo__avd = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        blgyh__fdbx = cgutils.get_or_insert_function(builder.module,
            rmo__avd, name='pq_write')
        cqg__ifs = builder.call(blgyh__fdbx, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return cqg__ifs
    return types.int64(types.voidptr, table_t, col_names_t, index_t, types.
        boolean, types.voidptr, types.voidptr, types.boolean, types.boolean,
        types.int32, types.int32, types.int32, types.voidptr, types.voidptr,
        types.int64, types.voidptr), codegen


@intrinsic
def parquet_write_table_partitioned_cpp(typingctx, filename_t, data_table_t,
    col_names_t, col_names_no_partitions_t, cat_table_t, part_col_idxs_t,
    num_part_col_t, compression_t, is_parallel_t, bucket_region,
    row_group_size, file_prefix):

    def codegen(context, builder, sig, args):
        rmo__avd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        blgyh__fdbx = cgutils.get_or_insert_function(builder.module,
            rmo__avd, name='pq_write_partitioned')
        builder.call(blgyh__fdbx, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
