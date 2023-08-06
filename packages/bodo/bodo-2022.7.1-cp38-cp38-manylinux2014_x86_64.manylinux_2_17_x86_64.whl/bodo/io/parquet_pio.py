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
        except OSError as azlwj__zknh:
            if 'non-file path' in str(azlwj__zknh):
                raise FileNotFoundError(str(azlwj__zknh))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        pyox__gwz = lhs.scope
        ljd__sith = lhs.loc
        oln__hwx = None
        if lhs.name in self.locals:
            oln__hwx = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        nqjhm__phrok = {}
        if lhs.name + ':convert' in self.locals:
            nqjhm__phrok = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if oln__hwx is None:
            bbp__vttw = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            nuupa__dgu = get_const_value(file_name, self.func_ir, bbp__vttw,
                arg_types=self.args, file_info=ParquetFileInfo(columns,
                storage_options=storage_options, input_file_name_col=
                input_file_name_col, read_as_dict_cols=read_as_dict_cols))
            yklke__rwcw = False
            gvltp__qci = guard(get_definition, self.func_ir, file_name)
            if isinstance(gvltp__qci, ir.Arg):
                typ = self.args[gvltp__qci.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, ujpbu__zex, skb__tah, col_indices,
                        partition_names, yrh__wum, ocj__dtf) = typ.schema
                    yklke__rwcw = True
            if not yklke__rwcw:
                (col_names, ujpbu__zex, skb__tah, col_indices,
                    partition_names, yrh__wum, ocj__dtf) = (parquet_file_schema
                    (nuupa__dgu, columns, storage_options=storage_options,
                    input_file_name_col=input_file_name_col,
                    read_as_dict_cols=read_as_dict_cols))
        else:
            ogkog__pjpve = list(oln__hwx.keys())
            wgxvg__tpt = {c: zwht__vpwog for zwht__vpwog, c in enumerate(
                ogkog__pjpve)}
            jtya__ebpwo = [xvl__rub for xvl__rub in oln__hwx.values()]
            skb__tah = 'index' if 'index' in wgxvg__tpt else None
            if columns is None:
                selected_columns = ogkog__pjpve
            else:
                selected_columns = columns
            col_indices = [wgxvg__tpt[c] for c in selected_columns]
            ujpbu__zex = [jtya__ebpwo[wgxvg__tpt[c]] for c in selected_columns]
            col_names = selected_columns
            skb__tah = skb__tah if skb__tah in col_names else None
            partition_names = []
            yrh__wum = []
            ocj__dtf = []
        cip__kyv = None if isinstance(skb__tah, dict
            ) or skb__tah is None else skb__tah
        index_column_index = None
        index_column_type = types.none
        if cip__kyv:
            idz__xhs = col_names.index(cip__kyv)
            index_column_index = col_indices.pop(idz__xhs)
            index_column_type = ujpbu__zex.pop(idz__xhs)
            col_names.pop(idz__xhs)
        for zwht__vpwog, c in enumerate(col_names):
            if c in nqjhm__phrok:
                ujpbu__zex[zwht__vpwog] = nqjhm__phrok[c]
        uybyj__obg = [ir.Var(pyox__gwz, mk_unique_var('pq_table'),
            ljd__sith), ir.Var(pyox__gwz, mk_unique_var('pq_index'), ljd__sith)
            ]
        vqncc__lale = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.
            name, col_names, col_indices, ujpbu__zex, uybyj__obg, ljd__sith,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, yrh__wum, ocj__dtf)]
        return (col_names, uybyj__obg, skb__tah, vqncc__lale, ujpbu__zex,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    lks__dsxx = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    kudx__sdqt, kuwg__bknoa = bodo.ir.connector.generate_filter_map(pq_node
        .filters)
    extra_args = ', '.join(kudx__sdqt.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, kudx__sdqt, kuwg__bknoa, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    hacxc__jme = ', '.join(f'out{zwht__vpwog}' for zwht__vpwog in range(
        lks__dsxx))
    uqzcz__andgb = f'def pq_impl(fname, {extra_args}):\n'
    uqzcz__andgb += (
        f'    (total_rows, {hacxc__jme},) = _pq_reader_py(fname, {extra_args})\n'
        )
    vpi__yqd = {}
    exec(uqzcz__andgb, {}, vpi__yqd)
    umj__lxx = vpi__yqd['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        gqqur__wdui = pq_node.loc.strformat()
        jjm__lvl = []
        aqa__gdbs = []
        for zwht__vpwog in pq_node.out_used_cols:
            daipg__ppo = pq_node.df_colnames[zwht__vpwog]
            jjm__lvl.append(daipg__ppo)
            if isinstance(pq_node.out_types[zwht__vpwog], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                aqa__gdbs.append(daipg__ppo)
        vvnb__wom = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', vvnb__wom,
            gqqur__wdui, jjm__lvl)
        if aqa__gdbs:
            lqqk__koeit = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                lqqk__koeit, gqqur__wdui, aqa__gdbs)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        oafs__wpjy = set(pq_node.out_used_cols)
        laglt__usui = set(pq_node.unsupported_columns)
        dve__igj = oafs__wpjy & laglt__usui
        if dve__igj:
            ejz__mbg = sorted(dve__igj)
            eoep__glzz = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            vyj__zfdc = 0
            for spmhx__qin in ejz__mbg:
                while pq_node.unsupported_columns[vyj__zfdc] != spmhx__qin:
                    vyj__zfdc += 1
                eoep__glzz.append(
                    f"Column '{pq_node.df_colnames[spmhx__qin]}' with unsupported arrow type {pq_node.unsupported_arrow_types[vyj__zfdc]}"
                    )
                vyj__zfdc += 1
            yra__mhytr = '\n'.join(eoep__glzz)
            raise BodoError(yra__mhytr, loc=pq_node.loc)
    pxdi__iwy = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.out_used_cols, pq_node.out_types, pq_node.storage_options,
        pq_node.partition_names, dnf_filter_str, expr_filter_str,
        extra_args, parallel, meta_head_only_info, pq_node.
        index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    ioto__jucyb = typemap[pq_node.file_name.name]
    bee__gvk = (ioto__jucyb,) + tuple(typemap[rkl__isb.name] for rkl__isb in
        kuwg__bknoa)
    bqe__nod = compile_to_numba_ir(umj__lxx, {'_pq_reader_py': pxdi__iwy},
        typingctx=typingctx, targetctx=targetctx, arg_typs=bee__gvk,
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(bqe__nod, [pq_node.file_name] + kuwg__bknoa)
    vqncc__lale = bqe__nod.body[:-3]
    if meta_head_only_info:
        vqncc__lale[-3].target = meta_head_only_info[1]
    vqncc__lale[-2].target = pq_node.out_vars[0]
    vqncc__lale[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        vqncc__lale.pop(-1)
    elif not pq_node.out_used_cols:
        vqncc__lale.pop(-2)
    return vqncc__lale


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    ddwt__vgu = get_overload_const_str(dnf_filter_str)
    xghxg__btw = get_overload_const_str(expr_filter_str)
    erz__jfth = ', '.join(f'f{zwht__vpwog}' for zwht__vpwog in range(len(
        var_tup)))
    uqzcz__andgb = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        uqzcz__andgb += f'  {erz__jfth}, = var_tup\n'
    uqzcz__andgb += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    uqzcz__andgb += f'    dnf_filters_py = {ddwt__vgu}\n'
    uqzcz__andgb += f'    expr_filters_py = {xghxg__btw}\n'
    uqzcz__andgb += '  return (dnf_filters_py, expr_filters_py)\n'
    vpi__yqd = {}
    exec(uqzcz__andgb, globals(), vpi__yqd)
    return vpi__yqd['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    tpgxg__myqo = next_label()
    czjxl__ptj = ',' if extra_args else ''
    uqzcz__andgb = f'def pq_reader_py(fname,{extra_args}):\n'
    uqzcz__andgb += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    uqzcz__andgb += f"    ev.add_attribute('g_fname', fname)\n"
    uqzcz__andgb += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{czjxl__ptj}))
"""
    uqzcz__andgb += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    uqzcz__andgb += f"""    storage_options_py = get_storage_options_pyobject({str(storage_options)})
"""
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    vzk__wmv = not out_used_cols
    bnmdo__mxb = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    feefe__vmker = {c: zwht__vpwog for zwht__vpwog, c in enumerate(col_indices)
        }
    cecg__legkt = {c: zwht__vpwog for zwht__vpwog, c in enumerate(bnmdo__mxb)}
    wvm__twn = []
    xrg__ktuml = set()
    wwigp__mtum = partition_names + [input_file_name_col]
    for zwht__vpwog in out_used_cols:
        if bnmdo__mxb[zwht__vpwog] not in wwigp__mtum:
            wvm__twn.append(col_indices[zwht__vpwog])
        elif not input_file_name_col or bnmdo__mxb[zwht__vpwog
            ] != input_file_name_col:
            xrg__ktuml.add(col_indices[zwht__vpwog])
    if index_column_index is not None:
        wvm__twn.append(index_column_index)
    wvm__twn = sorted(wvm__twn)
    adeom__ybdw = {c: zwht__vpwog for zwht__vpwog, c in enumerate(wvm__twn)}
    tyn__wlj = [(int(is_nullable(out_types[feefe__vmker[agun__zkcg]])) if 
        agun__zkcg != index_column_index else int(is_nullable(
        index_column_type))) for agun__zkcg in wvm__twn]
    str_as_dict_cols = []
    for agun__zkcg in wvm__twn:
        if agun__zkcg == index_column_index:
            xvl__rub = index_column_type
        else:
            xvl__rub = out_types[feefe__vmker[agun__zkcg]]
        if xvl__rub == dict_str_arr_type:
            str_as_dict_cols.append(agun__zkcg)
    nluir__bwylg = []
    xvv__mbjjh = {}
    uvmzw__xjrb = []
    udwe__lujvg = []
    for zwht__vpwog, lgvor__dftm in enumerate(partition_names):
        try:
            gxc__omk = cecg__legkt[lgvor__dftm]
            if col_indices[gxc__omk] not in xrg__ktuml:
                continue
        except (KeyError, ValueError) as muctp__gfh:
            continue
        xvv__mbjjh[lgvor__dftm] = len(nluir__bwylg)
        nluir__bwylg.append(lgvor__dftm)
        uvmzw__xjrb.append(zwht__vpwog)
        fsb__gtv = out_types[gxc__omk].dtype
        uitv__xamol = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            fsb__gtv)
        udwe__lujvg.append(numba_to_c_type(uitv__xamol))
    uqzcz__andgb += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    uqzcz__andgb += f'    out_table = pq_read(\n'
    uqzcz__andgb += f'        fname_py, {is_parallel},\n'
    uqzcz__andgb += f'        dnf_filters, expr_filters,\n'
    uqzcz__andgb += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{tpgxg__myqo}.ctypes,
"""
    uqzcz__andgb += f'        {len(wvm__twn)},\n'
    uqzcz__andgb += f'        nullable_cols_arr_{tpgxg__myqo}.ctypes,\n'
    if len(uvmzw__xjrb) > 0:
        uqzcz__andgb += (
            f'        np.array({uvmzw__xjrb}, dtype=np.int32).ctypes,\n')
        uqzcz__andgb += (
            f'        np.array({udwe__lujvg}, dtype=np.int32).ctypes,\n')
        uqzcz__andgb += f'        {len(uvmzw__xjrb)},\n'
    else:
        uqzcz__andgb += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        uqzcz__andgb += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        uqzcz__andgb += f'        0, 0,\n'
    uqzcz__andgb += f'        total_rows_np.ctypes,\n'
    uqzcz__andgb += f'        {input_file_name_col is not None},\n'
    uqzcz__andgb += f'    )\n'
    uqzcz__andgb += f'    check_and_propagate_cpp_exception()\n'
    qsm__lkgue = 'None'
    jlha__qqyv = index_column_type
    terdk__qftk = TableType(tuple(out_types))
    if vzk__wmv:
        terdk__qftk = types.none
    if index_column_index is not None:
        gyl__jtvuw = adeom__ybdw[index_column_index]
        qsm__lkgue = (
            f'info_to_array(info_from_table(out_table, {gyl__jtvuw}), index_arr_type)'
            )
    uqzcz__andgb += f'    index_arr = {qsm__lkgue}\n'
    if vzk__wmv:
        tyf__frn = None
    else:
        tyf__frn = []
        bav__trsvf = 0
        noo__caa = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for zwht__vpwog, spmhx__qin in enumerate(col_indices):
            if bav__trsvf < len(out_used_cols
                ) and zwht__vpwog == out_used_cols[bav__trsvf]:
                nvzhp__zfaq = col_indices[zwht__vpwog]
                if noo__caa and nvzhp__zfaq == noo__caa:
                    tyf__frn.append(len(wvm__twn) + len(nluir__bwylg))
                elif nvzhp__zfaq in xrg__ktuml:
                    xbr__hrod = bnmdo__mxb[zwht__vpwog]
                    tyf__frn.append(len(wvm__twn) + xvv__mbjjh[xbr__hrod])
                else:
                    tyf__frn.append(adeom__ybdw[spmhx__qin])
                bav__trsvf += 1
            else:
                tyf__frn.append(-1)
        tyf__frn = np.array(tyf__frn, dtype=np.int64)
    if vzk__wmv:
        uqzcz__andgb += '    T = None\n'
    else:
        uqzcz__andgb += f"""    T = cpp_table_to_py_table(out_table, table_idx_{tpgxg__myqo}, py_table_type_{tpgxg__myqo})
"""
    uqzcz__andgb += f'    delete_table(out_table)\n'
    uqzcz__andgb += f'    total_rows = total_rows_np[0]\n'
    uqzcz__andgb += f'    ev.finalize()\n'
    uqzcz__andgb += f'    return (total_rows, T, index_arr)\n'
    vpi__yqd = {}
    hgcp__vvtkm = {f'py_table_type_{tpgxg__myqo}': terdk__qftk,
        f'table_idx_{tpgxg__myqo}': tyf__frn,
        f'selected_cols_arr_{tpgxg__myqo}': np.array(wvm__twn, np.int32),
        f'nullable_cols_arr_{tpgxg__myqo}': np.array(tyn__wlj, np.int32),
        'index_arr_type': jlha__qqyv, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(uqzcz__andgb, hgcp__vvtkm, vpi__yqd)
    pxdi__iwy = vpi__yqd['pq_reader_py']
    igt__noyx = numba.njit(pxdi__iwy, no_cpython_wrapper=True)
    return igt__noyx


def unify_schemas(schemas):
    qtevh__morne = []
    for schema in schemas:
        for zwht__vpwog in range(len(schema)):
            lwynl__mtah = schema.field(zwht__vpwog)
            if lwynl__mtah.type == pa.large_string():
                schema = schema.set(zwht__vpwog, lwynl__mtah.with_type(pa.
                    string()))
            elif lwynl__mtah.type == pa.large_binary():
                schema = schema.set(zwht__vpwog, lwynl__mtah.with_type(pa.
                    binary()))
            elif isinstance(lwynl__mtah.type, (pa.ListType, pa.LargeListType)
                ) and lwynl__mtah.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(zwht__vpwog, lwynl__mtah.with_type(pa.
                    list_(pa.field(lwynl__mtah.type.value_field.name, pa.
                    string()))))
            elif isinstance(lwynl__mtah.type, pa.LargeListType):
                schema = schema.set(zwht__vpwog, lwynl__mtah.with_type(pa.
                    list_(pa.field(lwynl__mtah.type.value_field.name,
                    lwynl__mtah.type.value_type))))
        qtevh__morne.append(schema)
    return pa.unify_schemas(qtevh__morne)


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
        for zwht__vpwog in range(len(self.schema)):
            lwynl__mtah = self.schema.field(zwht__vpwog)
            if lwynl__mtah.type == pa.large_string():
                self.schema = self.schema.set(zwht__vpwog, lwynl__mtah.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for azyc__hgn in self.pieces:
            azyc__hgn.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            khsy__oblgt = {azyc__hgn: self.partitioning_dictionaries[
                zwht__vpwog] for zwht__vpwog, azyc__hgn in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, khsy__oblgt)


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
            self.partition_keys = [(lgvor__dftm, partitioning.dictionaries[
                zwht__vpwog].index(self.partition_keys[lgvor__dftm]).as_py(
                )) for zwht__vpwog, lgvor__dftm in enumerate(partition_names)]

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
        tefi__ufgfz = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    qmorr__unp = MPI.COMM_WORLD
    if isinstance(fpath, list):
        esoas__xwfsu = urlparse(fpath[0])
        protocol = esoas__xwfsu.scheme
        rczpl__dwf = esoas__xwfsu.netloc
        for zwht__vpwog in range(len(fpath)):
            lwynl__mtah = fpath[zwht__vpwog]
            qdsd__uijtv = urlparse(lwynl__mtah)
            if qdsd__uijtv.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if qdsd__uijtv.netloc != rczpl__dwf:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[zwht__vpwog] = lwynl__mtah.rstrip('/')
    else:
        esoas__xwfsu = urlparse(fpath)
        protocol = esoas__xwfsu.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as muctp__gfh:
            jzaeh__vbvz = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(jzaeh__vbvz)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as muctp__gfh:
            jzaeh__vbvz = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            och__pozvz = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(och__pozvz)))
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
            qdb__skcpf = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(qdb__skcpf) == 0:
            raise BodoError('No files found matching glob pattern')
        return qdb__skcpf
    hnfsv__pijfa = False
    if get_row_counts:
        yalxw__huw = getfs(parallel=True)
        hnfsv__pijfa = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        zprnr__vpk = 1
        eodp__uvxbq = os.cpu_count()
        if eodp__uvxbq is not None and eodp__uvxbq > 1:
            zprnr__vpk = eodp__uvxbq // 2
        try:
            if get_row_counts:
                nlgcx__ijlve = tracing.Event('pq.ParquetDataset',
                    is_parallel=False)
                if tracing.is_tracing():
                    nlgcx__ijlve.add_attribute('g_dnf_filter', str(dnf_filters)
                        )
            evb__mlw = pa.io_thread_count()
            pa.set_io_thread_count(zprnr__vpk)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{esoas__xwfsu.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    dthm__zntlu = [lwynl__mtah[len(prefix):] for
                        lwynl__mtah in fpath]
                else:
                    dthm__zntlu = fpath[len(prefix):]
            else:
                dthm__zntlu = fpath
            if isinstance(dthm__zntlu, list):
                rnn__ksr = []
                for azyc__hgn in dthm__zntlu:
                    if has_magic(azyc__hgn):
                        rnn__ksr += glob(protocol, getfs(), azyc__hgn)
                    else:
                        rnn__ksr.append(azyc__hgn)
                dthm__zntlu = rnn__ksr
            elif has_magic(dthm__zntlu):
                dthm__zntlu = glob(protocol, getfs(), dthm__zntlu)
            lrzo__xcc = pq.ParquetDataset(dthm__zntlu, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                lrzo__xcc._filters = dnf_filters
                lrzo__xcc._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            zshei__nvj = len(lrzo__xcc.files)
            lrzo__xcc = ParquetDataset(lrzo__xcc, prefix)
            pa.set_io_thread_count(evb__mlw)
            if typing_pa_schema:
                lrzo__xcc.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    nlgcx__ijlve.add_attribute('num_pieces_before_filter',
                        zshei__nvj)
                    nlgcx__ijlve.add_attribute('num_pieces_after_filter',
                        len(lrzo__xcc.pieces))
                nlgcx__ijlve.finalize()
        except Exception as azlwj__zknh:
            if isinstance(azlwj__zknh, IsADirectoryError):
                azlwj__zknh = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(azlwj__zknh, (
                OSError, FileNotFoundError)):
                azlwj__zknh = BodoError(str(azlwj__zknh) +
                    list_of_files_error_msg)
            else:
                azlwj__zknh = BodoError(
                    f"""error from pyarrow: {type(azlwj__zknh).__name__}: {str(azlwj__zknh)}
"""
                    )
            qmorr__unp.bcast(azlwj__zknh)
            raise azlwj__zknh
        if get_row_counts:
            dpi__hbpww = tracing.Event('bcast dataset')
        lrzo__xcc = qmorr__unp.bcast(lrzo__xcc)
    else:
        if get_row_counts:
            dpi__hbpww = tracing.Event('bcast dataset')
        lrzo__xcc = qmorr__unp.bcast(None)
        if isinstance(lrzo__xcc, Exception):
            qruty__jtjs = lrzo__xcc
            raise qruty__jtjs
    lrzo__xcc.set_fs(getfs())
    if get_row_counts:
        dpi__hbpww.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = hnfsv__pijfa = False
    if get_row_counts or hnfsv__pijfa:
        if get_row_counts and tracing.is_tracing():
            ppq__bxzoj = tracing.Event('get_row_counts')
            ppq__bxzoj.add_attribute('g_num_pieces', len(lrzo__xcc.pieces))
            ppq__bxzoj.add_attribute('g_expr_filters', str(expr_filters))
        fnsat__xevnn = 0.0
        num_pieces = len(lrzo__xcc.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        jdoy__ssq = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        lqdjp__dgwmr = 0
        kxws__qyki = 0
        zapx__bvdt = 0
        fsmsc__yqkz = True
        if expr_filters is not None:
            import random
            random.seed(37)
            ovh__stt = random.sample(lrzo__xcc.pieces, k=len(lrzo__xcc.pieces))
        else:
            ovh__stt = lrzo__xcc.pieces
        fpaths = [azyc__hgn.path for azyc__hgn in ovh__stt[start:jdoy__ssq]]
        zprnr__vpk = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(zprnr__vpk)
        pa.set_cpu_count(zprnr__vpk)
        qruty__jtjs = None
        try:
            fcvtv__yiujw = ds.dataset(fpaths, filesystem=lrzo__xcc.
                filesystem, partitioning=lrzo__xcc.partitioning)
            for fymhc__dwk, frag in zip(ovh__stt[start:jdoy__ssq],
                fcvtv__yiujw.get_fragments()):
                if hnfsv__pijfa:
                    tgh__lovr = frag.metadata.schema.to_arrow_schema()
                    pscw__dens = set(tgh__lovr.names)
                    ksrgq__lor = set(lrzo__xcc.schema.names) - set(lrzo__xcc
                        .partition_names)
                    if ksrgq__lor != pscw__dens:
                        ttdx__bmle = pscw__dens - ksrgq__lor
                        evpn__bayyw = ksrgq__lor - pscw__dens
                        bbp__vttw = f'Schema in {fymhc__dwk} was different.\n'
                        if ttdx__bmle:
                            bbp__vttw += f"""File contains column(s) {ttdx__bmle} not found in other files in the dataset.
"""
                        if evpn__bayyw:
                            bbp__vttw += f"""File missing column(s) {evpn__bayyw} found in other files in the dataset.
"""
                        raise BodoError(bbp__vttw)
                    try:
                        lrzo__xcc.schema = unify_schemas([lrzo__xcc.schema,
                            tgh__lovr])
                    except Exception as azlwj__zknh:
                        bbp__vttw = (
                            f'Schema in {fymhc__dwk} was different.\n' +
                            str(azlwj__zknh))
                        raise BodoError(bbp__vttw)
                xeakb__biov = time.time()
                kswy__ifogf = frag.scanner(schema=fcvtv__yiujw.schema,
                    filter=expr_filters, use_threads=True).count_rows()
                fnsat__xevnn += time.time() - xeakb__biov
                fymhc__dwk._bodo_num_rows = kswy__ifogf
                lqdjp__dgwmr += kswy__ifogf
                kxws__qyki += frag.num_row_groups
                zapx__bvdt += sum(qfaoo__mlnsa.total_byte_size for
                    qfaoo__mlnsa in frag.row_groups)
        except Exception as azlwj__zknh:
            qruty__jtjs = azlwj__zknh
        if qmorr__unp.allreduce(qruty__jtjs is not None, op=MPI.LOR):
            for qruty__jtjs in qmorr__unp.allgather(qruty__jtjs):
                if qruty__jtjs:
                    if isinstance(fpath, list) and isinstance(qruty__jtjs,
                        (OSError, FileNotFoundError)):
                        raise BodoError(str(qruty__jtjs) +
                            list_of_files_error_msg)
                    raise qruty__jtjs
        if hnfsv__pijfa:
            fsmsc__yqkz = qmorr__unp.allreduce(fsmsc__yqkz, op=MPI.LAND)
            if not fsmsc__yqkz:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            lrzo__xcc._bodo_total_rows = qmorr__unp.allreduce(lqdjp__dgwmr,
                op=MPI.SUM)
            wlrp__biui = qmorr__unp.allreduce(kxws__qyki, op=MPI.SUM)
            nke__bxz = qmorr__unp.allreduce(zapx__bvdt, op=MPI.SUM)
            xzn__wez = np.array([azyc__hgn._bodo_num_rows for azyc__hgn in
                lrzo__xcc.pieces])
            xzn__wez = qmorr__unp.allreduce(xzn__wez, op=MPI.SUM)
            for azyc__hgn, gwh__vrgbo in zip(lrzo__xcc.pieces, xzn__wez):
                azyc__hgn._bodo_num_rows = gwh__vrgbo
            if is_parallel and bodo.get_rank(
                ) == 0 and wlrp__biui < bodo.get_size() and wlrp__biui != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({wlrp__biui}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if wlrp__biui == 0:
                htbv__qonw = 0
            else:
                htbv__qonw = nke__bxz // wlrp__biui
            if (bodo.get_rank() == 0 and nke__bxz >= 20 * 1048576 and 
                htbv__qonw < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({htbv__qonw} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                ppq__bxzoj.add_attribute('g_total_num_row_groups', wlrp__biui)
                ppq__bxzoj.add_attribute('total_scan_time', fnsat__xevnn)
                fdt__gsc = np.array([azyc__hgn._bodo_num_rows for azyc__hgn in
                    lrzo__xcc.pieces])
                xakjr__lclc = np.percentile(fdt__gsc, [25, 50, 75])
                ppq__bxzoj.add_attribute('g_row_counts_min', fdt__gsc.min())
                ppq__bxzoj.add_attribute('g_row_counts_Q1', xakjr__lclc[0])
                ppq__bxzoj.add_attribute('g_row_counts_median', xakjr__lclc[1])
                ppq__bxzoj.add_attribute('g_row_counts_Q3', xakjr__lclc[2])
                ppq__bxzoj.add_attribute('g_row_counts_max', fdt__gsc.max())
                ppq__bxzoj.add_attribute('g_row_counts_mean', fdt__gsc.mean())
                ppq__bxzoj.add_attribute('g_row_counts_std', fdt__gsc.std())
                ppq__bxzoj.add_attribute('g_row_counts_sum', fdt__gsc.sum())
                ppq__bxzoj.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(lrzo__xcc)
    if get_row_counts:
        tefi__ufgfz.finalize()
    if hnfsv__pijfa and is_parallel:
        if tracing.is_tracing():
            zyae__mwkm = tracing.Event('unify_schemas_across_ranks')
        qruty__jtjs = None
        try:
            lrzo__xcc.schema = qmorr__unp.allreduce(lrzo__xcc.schema, bodo.
                io.helpers.pa_schema_unify_mpi_op)
        except Exception as azlwj__zknh:
            qruty__jtjs = azlwj__zknh
        if tracing.is_tracing():
            zyae__mwkm.finalize()
        if qmorr__unp.allreduce(qruty__jtjs is not None, op=MPI.LOR):
            for qruty__jtjs in qmorr__unp.allgather(qruty__jtjs):
                if qruty__jtjs:
                    bbp__vttw = (f'Schema in some files were different.\n' +
                        str(qruty__jtjs))
                    raise BodoError(bbp__vttw)
    return lrzo__xcc


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    eodp__uvxbq = os.cpu_count()
    if eodp__uvxbq is None or eodp__uvxbq == 0:
        eodp__uvxbq = 2
    lrlvl__jcqpz = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)),
        eodp__uvxbq)
    ctzhz__ktvhh = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)),
        eodp__uvxbq)
    if is_parallel and len(fpaths) > ctzhz__ktvhh and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(ctzhz__ktvhh)
        pa.set_cpu_count(ctzhz__ktvhh)
    else:
        pa.set_io_thread_count(lrlvl__jcqpz)
        pa.set_cpu_count(lrlvl__jcqpz)
    jexhh__gmel = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    acvk__duj = set(str_as_dict_cols)
    for zwht__vpwog, name in enumerate(schema.names):
        if name in acvk__duj:
            vqsxb__wendj = schema.field(zwht__vpwog)
            grrq__aeane = pa.field(name, pa.dictionary(pa.int32(),
                vqsxb__wendj.type), vqsxb__wendj.nullable)
            schema = schema.remove(zwht__vpwog).insert(zwht__vpwog, grrq__aeane
                )
    lrzo__xcc = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=jexhh__gmel)
    col_names = lrzo__xcc.schema.names
    wsbd__die = [col_names[fzp__zyfcz] for fzp__zyfcz in selected_fields]
    olvuj__aciai = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if olvuj__aciai and expr_filters is None:
        xwcwt__dupz = []
        uko__fmxg = 0
        aun__txqi = 0
        for frag in lrzo__xcc.get_fragments():
            rfkwp__hovwe = []
            for qfaoo__mlnsa in frag.row_groups:
                sgu__ealv = qfaoo__mlnsa.num_rows
                if start_offset < uko__fmxg + sgu__ealv:
                    if aun__txqi == 0:
                        dgzvg__ncth = start_offset - uko__fmxg
                        nholw__wvlq = min(sgu__ealv - dgzvg__ncth, rows_to_read
                            )
                    else:
                        nholw__wvlq = min(sgu__ealv, rows_to_read - aun__txqi)
                    aun__txqi += nholw__wvlq
                    rfkwp__hovwe.append(qfaoo__mlnsa.id)
                uko__fmxg += sgu__ealv
                if aun__txqi == rows_to_read:
                    break
            xwcwt__dupz.append(frag.subset(row_group_ids=rfkwp__hovwe))
            if aun__txqi == rows_to_read:
                break
        lrzo__xcc = ds.FileSystemDataset(xwcwt__dupz, lrzo__xcc.schema,
            jexhh__gmel, filesystem=lrzo__xcc.filesystem)
        start_offset = dgzvg__ncth
    byln__sdyxt = lrzo__xcc.scanner(columns=wsbd__die, filter=expr_filters,
        use_threads=True).to_reader()
    return lrzo__xcc, byln__sdyxt, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    ragj__cpnkv = [c for c in pa_schema.names if isinstance(pa_schema.field
        (c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(ragj__cpnkv) == 0:
        pq_dataset._category_info = {}
        return
    qmorr__unp = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            qiog__uldu = pq_dataset.pieces[0].frag.head(100, columns=
                ragj__cpnkv)
            gpoz__plhnr = {c: tuple(qiog__uldu.column(c).chunk(0).
                dictionary.to_pylist()) for c in ragj__cpnkv}
            del qiog__uldu
        except Exception as azlwj__zknh:
            qmorr__unp.bcast(azlwj__zknh)
            raise azlwj__zknh
        qmorr__unp.bcast(gpoz__plhnr)
    else:
        gpoz__plhnr = qmorr__unp.bcast(None)
        if isinstance(gpoz__plhnr, Exception):
            qruty__jtjs = gpoz__plhnr
            raise qruty__jtjs
    pq_dataset._category_info = gpoz__plhnr


def get_pandas_metadata(schema, num_pieces):
    skb__tah = None
    kdllr__qbxaj = defaultdict(lambda : None)
    sfb__hud = b'pandas'
    if schema.metadata is not None and sfb__hud in schema.metadata:
        import json
        uiwhe__mwui = json.loads(schema.metadata[sfb__hud].decode('utf8'))
        fyveg__hwmq = len(uiwhe__mwui['index_columns'])
        if fyveg__hwmq > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        skb__tah = uiwhe__mwui['index_columns'][0] if fyveg__hwmq else None
        if not isinstance(skb__tah, str) and not isinstance(skb__tah, dict):
            skb__tah = None
        for vjca__cmq in uiwhe__mwui['columns']:
            ypubw__xvw = vjca__cmq['name']
            if vjca__cmq['pandas_type'].startswith('int'
                ) and ypubw__xvw is not None:
                if vjca__cmq['numpy_type'].startswith('Int'):
                    kdllr__qbxaj[ypubw__xvw] = True
                else:
                    kdllr__qbxaj[ypubw__xvw] = False
    return skb__tah, kdllr__qbxaj


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for ypubw__xvw in pa_schema.names:
        epup__xtr = pa_schema.field(ypubw__xvw)
        if epup__xtr.type in (pa.string(), pa.large_string()):
            str_columns.append(ypubw__xvw)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    qmorr__unp = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        ovh__stt = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        ovh__stt = pq_dataset.pieces
    xhlf__okk = np.zeros(len(str_columns), dtype=np.int64)
    gcr__czwj = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(ovh__stt):
        fymhc__dwk = ovh__stt[bodo.get_rank()]
        try:
            metadata = fymhc__dwk.metadata
            for zwht__vpwog in range(fymhc__dwk.num_row_groups):
                for bav__trsvf, ypubw__xvw in enumerate(str_columns):
                    vyj__zfdc = pa_schema.get_field_index(ypubw__xvw)
                    xhlf__okk[bav__trsvf] += metadata.row_group(zwht__vpwog
                        ).column(vyj__zfdc).total_uncompressed_size
            kxbl__rgsm = metadata.num_rows
        except Exception as azlwj__zknh:
            if isinstance(azlwj__zknh, (OSError, FileNotFoundError)):
                kxbl__rgsm = 0
            else:
                raise
    else:
        kxbl__rgsm = 0
    asx__piul = qmorr__unp.allreduce(kxbl__rgsm, op=MPI.SUM)
    if asx__piul == 0:
        return set()
    qmorr__unp.Allreduce(xhlf__okk, gcr__czwj, op=MPI.SUM)
    hpwfp__myv = gcr__czwj / asx__piul
    upnb__hsik = set()
    for zwht__vpwog, ggdm__mkoiv in enumerate(hpwfp__myv):
        if ggdm__mkoiv < READ_STR_AS_DICT_THRESHOLD:
            ypubw__xvw = str_columns[zwht__vpwog][0]
            upnb__hsik.add(ypubw__xvw)
    return upnb__hsik


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    ujpbu__zex = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    dvin__qfb = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    rii__amwxd = read_as_dict_cols - dvin__qfb
    if len(rii__amwxd) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {rii__amwxd}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(dvin__qfb)
    dvin__qfb = dvin__qfb - read_as_dict_cols
    str_columns = [jgj__cjhrt for jgj__cjhrt in str_columns if jgj__cjhrt in
        dvin__qfb]
    upnb__hsik: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    upnb__hsik.update(read_as_dict_cols)
    col_names = pa_schema.names
    skb__tah, kdllr__qbxaj = get_pandas_metadata(pa_schema, num_pieces)
    jtya__ebpwo = []
    hyszi__vyd = []
    trf__utjiv = []
    for zwht__vpwog, c in enumerate(col_names):
        if c in partition_names:
            continue
        epup__xtr = pa_schema.field(c)
        jdo__xrsj, ihxop__uam = _get_numba_typ_from_pa_typ(epup__xtr, c ==
            skb__tah, kdllr__qbxaj[c], pq_dataset._category_info,
            str_as_dict=c in upnb__hsik)
        jtya__ebpwo.append(jdo__xrsj)
        hyszi__vyd.append(ihxop__uam)
        trf__utjiv.append(epup__xtr.type)
    if partition_names:
        jtya__ebpwo += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[zwht__vpwog]) for zwht__vpwog in
            range(len(partition_names))]
        hyszi__vyd.extend([True] * len(partition_names))
        trf__utjiv.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        jtya__ebpwo += [dict_str_arr_type]
        hyszi__vyd.append(True)
        trf__utjiv.append(None)
    pflj__nzr = {c: zwht__vpwog for zwht__vpwog, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in pflj__nzr:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if skb__tah and not isinstance(skb__tah, dict
        ) and skb__tah not in selected_columns:
        selected_columns.append(skb__tah)
    col_names = selected_columns
    col_indices = []
    ujpbu__zex = []
    yrh__wum = []
    ocj__dtf = []
    for zwht__vpwog, c in enumerate(col_names):
        nvzhp__zfaq = pflj__nzr[c]
        col_indices.append(nvzhp__zfaq)
        ujpbu__zex.append(jtya__ebpwo[nvzhp__zfaq])
        if not hyszi__vyd[nvzhp__zfaq]:
            yrh__wum.append(zwht__vpwog)
            ocj__dtf.append(trf__utjiv[nvzhp__zfaq])
    return (col_names, ujpbu__zex, skb__tah, col_indices, partition_names,
        yrh__wum, ocj__dtf)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    nwdt__kzrvv = dictionary.to_pandas()
    iqtip__xnoz = bodo.typeof(nwdt__kzrvv).dtype
    if isinstance(iqtip__xnoz, types.Integer):
        kyao__pjenh = PDCategoricalDtype(tuple(nwdt__kzrvv), iqtip__xnoz, 
            False, int_type=iqtip__xnoz)
    else:
        kyao__pjenh = PDCategoricalDtype(tuple(nwdt__kzrvv), iqtip__xnoz, False
            )
    return CategoricalArrayType(kyao__pjenh)


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
        zqhds__gao = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        azdfq__cpno = cgutils.get_or_insert_function(builder.module,
            zqhds__gao, name='pq_write')
        pax__awt = builder.call(azdfq__cpno, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return pax__awt
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
        zqhds__gao = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        azdfq__cpno = cgutils.get_or_insert_function(builder.module,
            zqhds__gao, name='pq_write_partitioned')
        builder.call(azdfq__cpno, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
