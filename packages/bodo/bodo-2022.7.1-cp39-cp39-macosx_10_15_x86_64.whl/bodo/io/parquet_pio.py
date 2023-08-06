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
        except OSError as sicd__iqrbx:
            if 'non-file path' in str(sicd__iqrbx):
                raise FileNotFoundError(str(sicd__iqrbx))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        rmi__saf = lhs.scope
        qzz__crxa = lhs.loc
        nuldt__pnwsb = None
        if lhs.name in self.locals:
            nuldt__pnwsb = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        nzm__kssf = {}
        if lhs.name + ':convert' in self.locals:
            nzm__kssf = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if nuldt__pnwsb is None:
            blzii__akaty = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            ahey__iofn = get_const_value(file_name, self.func_ir,
                blzii__akaty, arg_types=self.args, file_info=
                ParquetFileInfo(columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            rym__reg = False
            zrcru__udtio = guard(get_definition, self.func_ir, file_name)
            if isinstance(zrcru__udtio, ir.Arg):
                typ = self.args[zrcru__udtio.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, svry__adt, pwn__tvp, col_indices,
                        partition_names, lmdtx__fre, jnh__gwa) = typ.schema
                    rym__reg = True
            if not rym__reg:
                (col_names, svry__adt, pwn__tvp, col_indices,
                    partition_names, lmdtx__fre, jnh__gwa) = (
                    parquet_file_schema(ahey__iofn, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            biub__xduj = list(nuldt__pnwsb.keys())
            tvek__wwvl = {c: lfip__ddzao for lfip__ddzao, c in enumerate(
                biub__xduj)}
            oidww__kpht = [uawy__qadz for uawy__qadz in nuldt__pnwsb.values()]
            pwn__tvp = 'index' if 'index' in tvek__wwvl else None
            if columns is None:
                selected_columns = biub__xduj
            else:
                selected_columns = columns
            col_indices = [tvek__wwvl[c] for c in selected_columns]
            svry__adt = [oidww__kpht[tvek__wwvl[c]] for c in selected_columns]
            col_names = selected_columns
            pwn__tvp = pwn__tvp if pwn__tvp in col_names else None
            partition_names = []
            lmdtx__fre = []
            jnh__gwa = []
        mme__mcs = None if isinstance(pwn__tvp, dict
            ) or pwn__tvp is None else pwn__tvp
        index_column_index = None
        index_column_type = types.none
        if mme__mcs:
            cukn__fgimx = col_names.index(mme__mcs)
            index_column_index = col_indices.pop(cukn__fgimx)
            index_column_type = svry__adt.pop(cukn__fgimx)
            col_names.pop(cukn__fgimx)
        for lfip__ddzao, c in enumerate(col_names):
            if c in nzm__kssf:
                svry__adt[lfip__ddzao] = nzm__kssf[c]
        gijx__lgsnm = [ir.Var(rmi__saf, mk_unique_var('pq_table'),
            qzz__crxa), ir.Var(rmi__saf, mk_unique_var('pq_index'), qzz__crxa)]
        cddf__embfk = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.
            name, col_names, col_indices, svry__adt, gijx__lgsnm, qzz__crxa,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, lmdtx__fre, jnh__gwa)]
        return (col_names, gijx__lgsnm, pwn__tvp, cddf__embfk, svry__adt,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    qnjh__sdhod = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    rku__cio, vib__uvc = bodo.ir.connector.generate_filter_map(pq_node.filters)
    extra_args = ', '.join(rku__cio.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, rku__cio, vib__uvc, pq_node.original_df_colnames,
        pq_node.partition_names, pq_node.original_out_types, typemap,
        'parquet', output_dnf=False)
    euobi__iyo = ', '.join(f'out{lfip__ddzao}' for lfip__ddzao in range(
        qnjh__sdhod))
    wua__yvq = f'def pq_impl(fname, {extra_args}):\n'
    wua__yvq += (
        f'    (total_rows, {euobi__iyo},) = _pq_reader_py(fname, {extra_args})\n'
        )
    wkk__rhlto = {}
    exec(wua__yvq, {}, wkk__rhlto)
    pupq__vqsq = wkk__rhlto['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        zuy__ttn = pq_node.loc.strformat()
        nhv__bpbgj = []
        cyu__eoy = []
        for lfip__ddzao in pq_node.out_used_cols:
            ugct__ddq = pq_node.df_colnames[lfip__ddzao]
            nhv__bpbgj.append(ugct__ddq)
            if isinstance(pq_node.out_types[lfip__ddzao], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                cyu__eoy.append(ugct__ddq)
        yltxv__mbduj = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', yltxv__mbduj,
            zuy__ttn, nhv__bpbgj)
        if cyu__eoy:
            jzlhy__uyd = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', jzlhy__uyd,
                zuy__ttn, cyu__eoy)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        qadp__clya = set(pq_node.out_used_cols)
        elvkn__efa = set(pq_node.unsupported_columns)
        cjl__gfj = qadp__clya & elvkn__efa
        if cjl__gfj:
            waizo__mxxeq = sorted(cjl__gfj)
            biui__bpn = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            kuhk__fahlj = 0
            for gxg__lvcdj in waizo__mxxeq:
                while pq_node.unsupported_columns[kuhk__fahlj] != gxg__lvcdj:
                    kuhk__fahlj += 1
                biui__bpn.append(
                    f"Column '{pq_node.df_colnames[gxg__lvcdj]}' with unsupported arrow type {pq_node.unsupported_arrow_types[kuhk__fahlj]}"
                    )
                kuhk__fahlj += 1
            mxchz__cwwv = '\n'.join(biui__bpn)
            raise BodoError(mxchz__cwwv, loc=pq_node.loc)
    aghbt__crvq = _gen_pq_reader_py(pq_node.df_colnames, pq_node.
        col_indices, pq_node.out_used_cols, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    yggr__yfav = typemap[pq_node.file_name.name]
    fps__jga = (yggr__yfav,) + tuple(typemap[ggrvn__ycs.name] for
        ggrvn__ycs in vib__uvc)
    glqnr__okcoz = compile_to_numba_ir(pupq__vqsq, {'_pq_reader_py':
        aghbt__crvq}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        fps__jga, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(glqnr__okcoz, [pq_node.file_name] + vib__uvc)
    cddf__embfk = glqnr__okcoz.body[:-3]
    if meta_head_only_info:
        cddf__embfk[-3].target = meta_head_only_info[1]
    cddf__embfk[-2].target = pq_node.out_vars[0]
    cddf__embfk[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        cddf__embfk.pop(-1)
    elif not pq_node.out_used_cols:
        cddf__embfk.pop(-2)
    return cddf__embfk


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    ggwgy__ddcn = get_overload_const_str(dnf_filter_str)
    tqgv__petqw = get_overload_const_str(expr_filter_str)
    jqtlb__blf = ', '.join(f'f{lfip__ddzao}' for lfip__ddzao in range(len(
        var_tup)))
    wua__yvq = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        wua__yvq += f'  {jqtlb__blf}, = var_tup\n'
    wua__yvq += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    wua__yvq += f'    dnf_filters_py = {ggwgy__ddcn}\n'
    wua__yvq += f'    expr_filters_py = {tqgv__petqw}\n'
    wua__yvq += '  return (dnf_filters_py, expr_filters_py)\n'
    wkk__rhlto = {}
    exec(wua__yvq, globals(), wkk__rhlto)
    return wkk__rhlto['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    yfl__cpcs = next_label()
    einmg__tpnt = ',' if extra_args else ''
    wua__yvq = f'def pq_reader_py(fname,{extra_args}):\n'
    wua__yvq += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    wua__yvq += f"    ev.add_attribute('g_fname', fname)\n"
    wua__yvq += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{einmg__tpnt}))
"""
    wua__yvq += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    wua__yvq += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    tjhf__yea = not out_used_cols
    qcs__zdkhd = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    tjtl__utsy = {c: lfip__ddzao for lfip__ddzao, c in enumerate(col_indices)}
    chvsv__boz = {c: lfip__ddzao for lfip__ddzao, c in enumerate(qcs__zdkhd)}
    osi__rzhl = []
    fso__clncc = set()
    ndqq__vttsu = partition_names + [input_file_name_col]
    for lfip__ddzao in out_used_cols:
        if qcs__zdkhd[lfip__ddzao] not in ndqq__vttsu:
            osi__rzhl.append(col_indices[lfip__ddzao])
        elif not input_file_name_col or qcs__zdkhd[lfip__ddzao
            ] != input_file_name_col:
            fso__clncc.add(col_indices[lfip__ddzao])
    if index_column_index is not None:
        osi__rzhl.append(index_column_index)
    osi__rzhl = sorted(osi__rzhl)
    qpk__zjqe = {c: lfip__ddzao for lfip__ddzao, c in enumerate(osi__rzhl)}
    ufo__nkk = [(int(is_nullable(out_types[tjtl__utsy[pdap__gcjwe]])) if 
        pdap__gcjwe != index_column_index else int(is_nullable(
        index_column_type))) for pdap__gcjwe in osi__rzhl]
    str_as_dict_cols = []
    for pdap__gcjwe in osi__rzhl:
        if pdap__gcjwe == index_column_index:
            uawy__qadz = index_column_type
        else:
            uawy__qadz = out_types[tjtl__utsy[pdap__gcjwe]]
        if uawy__qadz == dict_str_arr_type:
            str_as_dict_cols.append(pdap__gcjwe)
    oca__gcts = []
    wvtr__jafsk = {}
    umerx__xbpd = []
    boydw__idq = []
    for lfip__ddzao, syf__fpohv in enumerate(partition_names):
        try:
            ubwb__wxuoy = chvsv__boz[syf__fpohv]
            if col_indices[ubwb__wxuoy] not in fso__clncc:
                continue
        except (KeyError, ValueError) as cabti__pqgol:
            continue
        wvtr__jafsk[syf__fpohv] = len(oca__gcts)
        oca__gcts.append(syf__fpohv)
        umerx__xbpd.append(lfip__ddzao)
        cudng__aakg = out_types[ubwb__wxuoy].dtype
        miix__mjr = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            cudng__aakg)
        boydw__idq.append(numba_to_c_type(miix__mjr))
    wua__yvq += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    wua__yvq += f'    out_table = pq_read(\n'
    wua__yvq += f'        fname_py, {is_parallel},\n'
    wua__yvq += f'        dnf_filters, expr_filters,\n'
    wua__yvq += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{yfl__cpcs}.ctypes,
"""
    wua__yvq += f'        {len(osi__rzhl)},\n'
    wua__yvq += f'        nullable_cols_arr_{yfl__cpcs}.ctypes,\n'
    if len(umerx__xbpd) > 0:
        wua__yvq += (
            f'        np.array({umerx__xbpd}, dtype=np.int32).ctypes,\n')
        wua__yvq += f'        np.array({boydw__idq}, dtype=np.int32).ctypes,\n'
        wua__yvq += f'        {len(umerx__xbpd)},\n'
    else:
        wua__yvq += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        wua__yvq += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        wua__yvq += f'        0, 0,\n'
    wua__yvq += f'        total_rows_np.ctypes,\n'
    wua__yvq += f'        {input_file_name_col is not None},\n'
    wua__yvq += f'    )\n'
    wua__yvq += f'    check_and_propagate_cpp_exception()\n'
    oin__kmfl = 'None'
    jfg__udn = index_column_type
    lwyrv__qes = TableType(tuple(out_types))
    if tjhf__yea:
        lwyrv__qes = types.none
    if index_column_index is not None:
        fjkby__shct = qpk__zjqe[index_column_index]
        oin__kmfl = (
            f'info_to_array(info_from_table(out_table, {fjkby__shct}), index_arr_type)'
            )
    wua__yvq += f'    index_arr = {oin__kmfl}\n'
    if tjhf__yea:
        aho__bbt = None
    else:
        aho__bbt = []
        dtil__kihyw = 0
        nifr__sal = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for lfip__ddzao, gxg__lvcdj in enumerate(col_indices):
            if dtil__kihyw < len(out_used_cols
                ) and lfip__ddzao == out_used_cols[dtil__kihyw]:
                yqtju__hqszq = col_indices[lfip__ddzao]
                if nifr__sal and yqtju__hqszq == nifr__sal:
                    aho__bbt.append(len(osi__rzhl) + len(oca__gcts))
                elif yqtju__hqszq in fso__clncc:
                    zxo__fjjod = qcs__zdkhd[lfip__ddzao]
                    aho__bbt.append(len(osi__rzhl) + wvtr__jafsk[zxo__fjjod])
                else:
                    aho__bbt.append(qpk__zjqe[gxg__lvcdj])
                dtil__kihyw += 1
            else:
                aho__bbt.append(-1)
        aho__bbt = np.array(aho__bbt, dtype=np.int64)
    if tjhf__yea:
        wua__yvq += '    T = None\n'
    else:
        wua__yvq += f"""    T = cpp_table_to_py_table(out_table, table_idx_{yfl__cpcs}, py_table_type_{yfl__cpcs})
"""
    wua__yvq += f'    delete_table(out_table)\n'
    wua__yvq += f'    total_rows = total_rows_np[0]\n'
    wua__yvq += f'    ev.finalize()\n'
    wua__yvq += f'    return (total_rows, T, index_arr)\n'
    wkk__rhlto = {}
    myiug__oiien = {f'py_table_type_{yfl__cpcs}': lwyrv__qes,
        f'table_idx_{yfl__cpcs}': aho__bbt,
        f'selected_cols_arr_{yfl__cpcs}': np.array(osi__rzhl, np.int32),
        f'nullable_cols_arr_{yfl__cpcs}': np.array(ufo__nkk, np.int32),
        'index_arr_type': jfg__udn, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(wua__yvq, myiug__oiien, wkk__rhlto)
    aghbt__crvq = wkk__rhlto['pq_reader_py']
    iglvt__pjpp = numba.njit(aghbt__crvq, no_cpython_wrapper=True)
    return iglvt__pjpp


def unify_schemas(schemas):
    rykcb__zayw = []
    for schema in schemas:
        for lfip__ddzao in range(len(schema)):
            qoun__jslvw = schema.field(lfip__ddzao)
            if qoun__jslvw.type == pa.large_string():
                schema = schema.set(lfip__ddzao, qoun__jslvw.with_type(pa.
                    string()))
            elif qoun__jslvw.type == pa.large_binary():
                schema = schema.set(lfip__ddzao, qoun__jslvw.with_type(pa.
                    binary()))
            elif isinstance(qoun__jslvw.type, (pa.ListType, pa.LargeListType)
                ) and qoun__jslvw.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(lfip__ddzao, qoun__jslvw.with_type(pa.
                    list_(pa.field(qoun__jslvw.type.value_field.name, pa.
                    string()))))
            elif isinstance(qoun__jslvw.type, pa.LargeListType):
                schema = schema.set(lfip__ddzao, qoun__jslvw.with_type(pa.
                    list_(pa.field(qoun__jslvw.type.value_field.name,
                    qoun__jslvw.type.value_type))))
        rykcb__zayw.append(schema)
    return pa.unify_schemas(rykcb__zayw)


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
        for lfip__ddzao in range(len(self.schema)):
            qoun__jslvw = self.schema.field(lfip__ddzao)
            if qoun__jslvw.type == pa.large_string():
                self.schema = self.schema.set(lfip__ddzao, qoun__jslvw.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for gde__ckewp in self.pieces:
            gde__ckewp.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            xrcs__etsw = {gde__ckewp: self.partitioning_dictionaries[
                lfip__ddzao] for lfip__ddzao, gde__ckewp in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, xrcs__etsw)


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
            self.partition_keys = [(syf__fpohv, partitioning.dictionaries[
                lfip__ddzao].index(self.partition_keys[syf__fpohv]).as_py()
                ) for lfip__ddzao, syf__fpohv in enumerate(partition_names)]

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
        zwv__xofvw = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    oafpd__jhwzc = MPI.COMM_WORLD
    if isinstance(fpath, list):
        kif__mcg = urlparse(fpath[0])
        protocol = kif__mcg.scheme
        zlmg__ljlft = kif__mcg.netloc
        for lfip__ddzao in range(len(fpath)):
            qoun__jslvw = fpath[lfip__ddzao]
            zngb__axnsn = urlparse(qoun__jslvw)
            if zngb__axnsn.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if zngb__axnsn.netloc != zlmg__ljlft:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[lfip__ddzao] = qoun__jslvw.rstrip('/')
    else:
        kif__mcg = urlparse(fpath)
        protocol = kif__mcg.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as cabti__pqgol:
            vfsie__gsu = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(vfsie__gsu)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as cabti__pqgol:
            vfsie__gsu = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            wzje__mep = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(wzje__mep)))
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
            yrm__lru = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(yrm__lru) == 0:
            raise BodoError('No files found matching glob pattern')
        return yrm__lru
    lwqtu__vhtj = False
    if get_row_counts:
        tgd__jzom = getfs(parallel=True)
        lwqtu__vhtj = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        hkos__hqr = 1
        syjy__hqmp = os.cpu_count()
        if syjy__hqmp is not None and syjy__hqmp > 1:
            hkos__hqr = syjy__hqmp // 2
        try:
            if get_row_counts:
                gxyrl__tbn = tracing.Event('pq.ParquetDataset', is_parallel
                    =False)
                if tracing.is_tracing():
                    gxyrl__tbn.add_attribute('g_dnf_filter', str(dnf_filters))
            fov__nreu = pa.io_thread_count()
            pa.set_io_thread_count(hkos__hqr)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{kif__mcg.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    zlmwy__sjjxl = [qoun__jslvw[len(prefix):] for
                        qoun__jslvw in fpath]
                else:
                    zlmwy__sjjxl = fpath[len(prefix):]
            else:
                zlmwy__sjjxl = fpath
            if isinstance(zlmwy__sjjxl, list):
                zsjpz__ypys = []
                for gde__ckewp in zlmwy__sjjxl:
                    if has_magic(gde__ckewp):
                        zsjpz__ypys += glob(protocol, getfs(), gde__ckewp)
                    else:
                        zsjpz__ypys.append(gde__ckewp)
                zlmwy__sjjxl = zsjpz__ypys
            elif has_magic(zlmwy__sjjxl):
                zlmwy__sjjxl = glob(protocol, getfs(), zlmwy__sjjxl)
            pdah__diet = pq.ParquetDataset(zlmwy__sjjxl, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                pdah__diet._filters = dnf_filters
                pdah__diet._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            fhg__gshr = len(pdah__diet.files)
            pdah__diet = ParquetDataset(pdah__diet, prefix)
            pa.set_io_thread_count(fov__nreu)
            if typing_pa_schema:
                pdah__diet.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    gxyrl__tbn.add_attribute('num_pieces_before_filter',
                        fhg__gshr)
                    gxyrl__tbn.add_attribute('num_pieces_after_filter', len
                        (pdah__diet.pieces))
                gxyrl__tbn.finalize()
        except Exception as sicd__iqrbx:
            if isinstance(sicd__iqrbx, IsADirectoryError):
                sicd__iqrbx = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(sicd__iqrbx, (
                OSError, FileNotFoundError)):
                sicd__iqrbx = BodoError(str(sicd__iqrbx) +
                    list_of_files_error_msg)
            else:
                sicd__iqrbx = BodoError(
                    f"""error from pyarrow: {type(sicd__iqrbx).__name__}: {str(sicd__iqrbx)}
"""
                    )
            oafpd__jhwzc.bcast(sicd__iqrbx)
            raise sicd__iqrbx
        if get_row_counts:
            xatcl__iyzao = tracing.Event('bcast dataset')
        pdah__diet = oafpd__jhwzc.bcast(pdah__diet)
    else:
        if get_row_counts:
            xatcl__iyzao = tracing.Event('bcast dataset')
        pdah__diet = oafpd__jhwzc.bcast(None)
        if isinstance(pdah__diet, Exception):
            znmzp__bxb = pdah__diet
            raise znmzp__bxb
    pdah__diet.set_fs(getfs())
    if get_row_counts:
        xatcl__iyzao.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = lwqtu__vhtj = False
    if get_row_counts or lwqtu__vhtj:
        if get_row_counts and tracing.is_tracing():
            rak__dik = tracing.Event('get_row_counts')
            rak__dik.add_attribute('g_num_pieces', len(pdah__diet.pieces))
            rak__dik.add_attribute('g_expr_filters', str(expr_filters))
        ycac__fphkv = 0.0
        num_pieces = len(pdah__diet.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        lbjx__gjb = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        zwex__ndnbw = 0
        cgija__zdgxq = 0
        nnoa__oxes = 0
        dfz__bvs = True
        if expr_filters is not None:
            import random
            random.seed(37)
            njj__ptajj = random.sample(pdah__diet.pieces, k=len(pdah__diet.
                pieces))
        else:
            njj__ptajj = pdah__diet.pieces
        fpaths = [gde__ckewp.path for gde__ckewp in njj__ptajj[start:lbjx__gjb]
            ]
        hkos__hqr = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(hkos__hqr)
        pa.set_cpu_count(hkos__hqr)
        znmzp__bxb = None
        try:
            rmb__fev = ds.dataset(fpaths, filesystem=pdah__diet.filesystem,
                partitioning=pdah__diet.partitioning)
            for txrgq__udxr, frag in zip(njj__ptajj[start:lbjx__gjb],
                rmb__fev.get_fragments()):
                if lwqtu__vhtj:
                    xtof__fkbxl = frag.metadata.schema.to_arrow_schema()
                    lbmkp__dzk = set(xtof__fkbxl.names)
                    ogfp__ipm = set(pdah__diet.schema.names) - set(pdah__diet
                        .partition_names)
                    if ogfp__ipm != lbmkp__dzk:
                        ntnf__vshp = lbmkp__dzk - ogfp__ipm
                        rvmp__fot = ogfp__ipm - lbmkp__dzk
                        blzii__akaty = (
                            f'Schema in {txrgq__udxr} was different.\n')
                        if ntnf__vshp:
                            blzii__akaty += f"""File contains column(s) {ntnf__vshp} not found in other files in the dataset.
"""
                        if rvmp__fot:
                            blzii__akaty += f"""File missing column(s) {rvmp__fot} found in other files in the dataset.
"""
                        raise BodoError(blzii__akaty)
                    try:
                        pdah__diet.schema = unify_schemas([pdah__diet.
                            schema, xtof__fkbxl])
                    except Exception as sicd__iqrbx:
                        blzii__akaty = (
                            f'Schema in {txrgq__udxr} was different.\n' +
                            str(sicd__iqrbx))
                        raise BodoError(blzii__akaty)
                oslh__lvn = time.time()
                mcxnd__gjn = frag.scanner(schema=rmb__fev.schema, filter=
                    expr_filters, use_threads=True).count_rows()
                ycac__fphkv += time.time() - oslh__lvn
                txrgq__udxr._bodo_num_rows = mcxnd__gjn
                zwex__ndnbw += mcxnd__gjn
                cgija__zdgxq += frag.num_row_groups
                nnoa__oxes += sum(bic__mwyzo.total_byte_size for bic__mwyzo in
                    frag.row_groups)
        except Exception as sicd__iqrbx:
            znmzp__bxb = sicd__iqrbx
        if oafpd__jhwzc.allreduce(znmzp__bxb is not None, op=MPI.LOR):
            for znmzp__bxb in oafpd__jhwzc.allgather(znmzp__bxb):
                if znmzp__bxb:
                    if isinstance(fpath, list) and isinstance(znmzp__bxb, (
                        OSError, FileNotFoundError)):
                        raise BodoError(str(znmzp__bxb) +
                            list_of_files_error_msg)
                    raise znmzp__bxb
        if lwqtu__vhtj:
            dfz__bvs = oafpd__jhwzc.allreduce(dfz__bvs, op=MPI.LAND)
            if not dfz__bvs:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            pdah__diet._bodo_total_rows = oafpd__jhwzc.allreduce(zwex__ndnbw,
                op=MPI.SUM)
            czkqc__gahye = oafpd__jhwzc.allreduce(cgija__zdgxq, op=MPI.SUM)
            luu__fbzbb = oafpd__jhwzc.allreduce(nnoa__oxes, op=MPI.SUM)
            lwycw__zach = np.array([gde__ckewp._bodo_num_rows for
                gde__ckewp in pdah__diet.pieces])
            lwycw__zach = oafpd__jhwzc.allreduce(lwycw__zach, op=MPI.SUM)
            for gde__ckewp, oxixm__tmr in zip(pdah__diet.pieces, lwycw__zach):
                gde__ckewp._bodo_num_rows = oxixm__tmr
            if is_parallel and bodo.get_rank(
                ) == 0 and czkqc__gahye < bodo.get_size(
                ) and czkqc__gahye != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({czkqc__gahye}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if czkqc__gahye == 0:
                isrm__puz = 0
            else:
                isrm__puz = luu__fbzbb // czkqc__gahye
            if (bodo.get_rank() == 0 and luu__fbzbb >= 20 * 1048576 and 
                isrm__puz < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({isrm__puz} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                rak__dik.add_attribute('g_total_num_row_groups', czkqc__gahye)
                rak__dik.add_attribute('total_scan_time', ycac__fphkv)
                hsnj__wuca = np.array([gde__ckewp._bodo_num_rows for
                    gde__ckewp in pdah__diet.pieces])
                orzej__orah = np.percentile(hsnj__wuca, [25, 50, 75])
                rak__dik.add_attribute('g_row_counts_min', hsnj__wuca.min())
                rak__dik.add_attribute('g_row_counts_Q1', orzej__orah[0])
                rak__dik.add_attribute('g_row_counts_median', orzej__orah[1])
                rak__dik.add_attribute('g_row_counts_Q3', orzej__orah[2])
                rak__dik.add_attribute('g_row_counts_max', hsnj__wuca.max())
                rak__dik.add_attribute('g_row_counts_mean', hsnj__wuca.mean())
                rak__dik.add_attribute('g_row_counts_std', hsnj__wuca.std())
                rak__dik.add_attribute('g_row_counts_sum', hsnj__wuca.sum())
                rak__dik.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(pdah__diet)
    if get_row_counts:
        zwv__xofvw.finalize()
    if lwqtu__vhtj and is_parallel:
        if tracing.is_tracing():
            mzz__tyv = tracing.Event('unify_schemas_across_ranks')
        znmzp__bxb = None
        try:
            pdah__diet.schema = oafpd__jhwzc.allreduce(pdah__diet.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as sicd__iqrbx:
            znmzp__bxb = sicd__iqrbx
        if tracing.is_tracing():
            mzz__tyv.finalize()
        if oafpd__jhwzc.allreduce(znmzp__bxb is not None, op=MPI.LOR):
            for znmzp__bxb in oafpd__jhwzc.allgather(znmzp__bxb):
                if znmzp__bxb:
                    blzii__akaty = (
                        f'Schema in some files were different.\n' + str(
                        znmzp__bxb))
                    raise BodoError(blzii__akaty)
    return pdah__diet


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    syjy__hqmp = os.cpu_count()
    if syjy__hqmp is None or syjy__hqmp == 0:
        syjy__hqmp = 2
    ozbll__bems = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), syjy__hqmp
        )
    ufk__atqpv = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), syjy__hqmp
        )
    if is_parallel and len(fpaths) > ufk__atqpv and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(ufk__atqpv)
        pa.set_cpu_count(ufk__atqpv)
    else:
        pa.set_io_thread_count(ozbll__bems)
        pa.set_cpu_count(ozbll__bems)
    fxij__cqya = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    jmzq__kffn = set(str_as_dict_cols)
    for lfip__ddzao, name in enumerate(schema.names):
        if name in jmzq__kffn:
            revt__zqhq = schema.field(lfip__ddzao)
            qkde__nme = pa.field(name, pa.dictionary(pa.int32(), revt__zqhq
                .type), revt__zqhq.nullable)
            schema = schema.remove(lfip__ddzao).insert(lfip__ddzao, qkde__nme)
    pdah__diet = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=fxij__cqya)
    col_names = pdah__diet.schema.names
    jqa__rep = [col_names[wsp__sgi] for wsp__sgi in selected_fields]
    nmtpk__ugkq = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if nmtpk__ugkq and expr_filters is None:
        issru__dmwzj = []
        gyt__lzggj = 0
        orp__dov = 0
        for frag in pdah__diet.get_fragments():
            lkwvh__vyx = []
            for bic__mwyzo in frag.row_groups:
                oaajd__ixtmn = bic__mwyzo.num_rows
                if start_offset < gyt__lzggj + oaajd__ixtmn:
                    if orp__dov == 0:
                        yju__vxdgv = start_offset - gyt__lzggj
                        oyd__mrcji = min(oaajd__ixtmn - yju__vxdgv,
                            rows_to_read)
                    else:
                        oyd__mrcji = min(oaajd__ixtmn, rows_to_read - orp__dov)
                    orp__dov += oyd__mrcji
                    lkwvh__vyx.append(bic__mwyzo.id)
                gyt__lzggj += oaajd__ixtmn
                if orp__dov == rows_to_read:
                    break
            issru__dmwzj.append(frag.subset(row_group_ids=lkwvh__vyx))
            if orp__dov == rows_to_read:
                break
        pdah__diet = ds.FileSystemDataset(issru__dmwzj, pdah__diet.schema,
            fxij__cqya, filesystem=pdah__diet.filesystem)
        start_offset = yju__vxdgv
    bbkf__ije = pdah__diet.scanner(columns=jqa__rep, filter=expr_filters,
        use_threads=True).to_reader()
    return pdah__diet, bbkf__ije, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    fhon__fvor = [c for c in pa_schema.names if isinstance(pa_schema.field(
        c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(fhon__fvor) == 0:
        pq_dataset._category_info = {}
        return
    oafpd__jhwzc = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            ykjmu__mqqrf = pq_dataset.pieces[0].frag.head(100, columns=
                fhon__fvor)
            nhfjw__ywmc = {c: tuple(ykjmu__mqqrf.column(c).chunk(0).
                dictionary.to_pylist()) for c in fhon__fvor}
            del ykjmu__mqqrf
        except Exception as sicd__iqrbx:
            oafpd__jhwzc.bcast(sicd__iqrbx)
            raise sicd__iqrbx
        oafpd__jhwzc.bcast(nhfjw__ywmc)
    else:
        nhfjw__ywmc = oafpd__jhwzc.bcast(None)
        if isinstance(nhfjw__ywmc, Exception):
            znmzp__bxb = nhfjw__ywmc
            raise znmzp__bxb
    pq_dataset._category_info = nhfjw__ywmc


def get_pandas_metadata(schema, num_pieces):
    pwn__tvp = None
    flwt__nemg = defaultdict(lambda : None)
    lcgly__ezs = b'pandas'
    if schema.metadata is not None and lcgly__ezs in schema.metadata:
        import json
        bhzlg__foqz = json.loads(schema.metadata[lcgly__ezs].decode('utf8'))
        zlgj__zbdz = len(bhzlg__foqz['index_columns'])
        if zlgj__zbdz > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        pwn__tvp = bhzlg__foqz['index_columns'][0] if zlgj__zbdz else None
        if not isinstance(pwn__tvp, str) and not isinstance(pwn__tvp, dict):
            pwn__tvp = None
        for fhr__pbprl in bhzlg__foqz['columns']:
            kho__rlk = fhr__pbprl['name']
            if fhr__pbprl['pandas_type'].startswith('int'
                ) and kho__rlk is not None:
                if fhr__pbprl['numpy_type'].startswith('Int'):
                    flwt__nemg[kho__rlk] = True
                else:
                    flwt__nemg[kho__rlk] = False
    return pwn__tvp, flwt__nemg


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for kho__rlk in pa_schema.names:
        wbr__bzzi = pa_schema.field(kho__rlk)
        if wbr__bzzi.type in (pa.string(), pa.large_string()):
            str_columns.append(kho__rlk)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    oafpd__jhwzc = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        njj__ptajj = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        njj__ptajj = pq_dataset.pieces
    xay__gtxxs = np.zeros(len(str_columns), dtype=np.int64)
    yeq__sjre = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(njj__ptajj):
        txrgq__udxr = njj__ptajj[bodo.get_rank()]
        try:
            metadata = txrgq__udxr.metadata
            for lfip__ddzao in range(txrgq__udxr.num_row_groups):
                for dtil__kihyw, kho__rlk in enumerate(str_columns):
                    kuhk__fahlj = pa_schema.get_field_index(kho__rlk)
                    xay__gtxxs[dtil__kihyw] += metadata.row_group(lfip__ddzao
                        ).column(kuhk__fahlj).total_uncompressed_size
            ripay__yltpu = metadata.num_rows
        except Exception as sicd__iqrbx:
            if isinstance(sicd__iqrbx, (OSError, FileNotFoundError)):
                ripay__yltpu = 0
            else:
                raise
    else:
        ripay__yltpu = 0
    kah__cdxi = oafpd__jhwzc.allreduce(ripay__yltpu, op=MPI.SUM)
    if kah__cdxi == 0:
        return set()
    oafpd__jhwzc.Allreduce(xay__gtxxs, yeq__sjre, op=MPI.SUM)
    gkmzl__ylavq = yeq__sjre / kah__cdxi
    htjot__yqk = set()
    for lfip__ddzao, xjpg__zor in enumerate(gkmzl__ylavq):
        if xjpg__zor < READ_STR_AS_DICT_THRESHOLD:
            kho__rlk = str_columns[lfip__ddzao][0]
            htjot__yqk.add(kho__rlk)
    return htjot__yqk


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    svry__adt = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    jtlco__mxid = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    jbeox__wne = read_as_dict_cols - jtlco__mxid
    if len(jbeox__wne) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {jbeox__wne}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(jtlco__mxid)
    jtlco__mxid = jtlco__mxid - read_as_dict_cols
    str_columns = [imrpu__kgx for imrpu__kgx in str_columns if imrpu__kgx in
        jtlco__mxid]
    htjot__yqk: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    htjot__yqk.update(read_as_dict_cols)
    col_names = pa_schema.names
    pwn__tvp, flwt__nemg = get_pandas_metadata(pa_schema, num_pieces)
    oidww__kpht = []
    latd__bhodd = []
    cqlj__dof = []
    for lfip__ddzao, c in enumerate(col_names):
        if c in partition_names:
            continue
        wbr__bzzi = pa_schema.field(c)
        hlep__hlx, fjbwv__hdb = _get_numba_typ_from_pa_typ(wbr__bzzi, c ==
            pwn__tvp, flwt__nemg[c], pq_dataset._category_info, str_as_dict
            =c in htjot__yqk)
        oidww__kpht.append(hlep__hlx)
        latd__bhodd.append(fjbwv__hdb)
        cqlj__dof.append(wbr__bzzi.type)
    if partition_names:
        oidww__kpht += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[lfip__ddzao]) for lfip__ddzao in
            range(len(partition_names))]
        latd__bhodd.extend([True] * len(partition_names))
        cqlj__dof.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        oidww__kpht += [dict_str_arr_type]
        latd__bhodd.append(True)
        cqlj__dof.append(None)
    zasc__ridzl = {c: lfip__ddzao for lfip__ddzao, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in zasc__ridzl:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if pwn__tvp and not isinstance(pwn__tvp, dict
        ) and pwn__tvp not in selected_columns:
        selected_columns.append(pwn__tvp)
    col_names = selected_columns
    col_indices = []
    svry__adt = []
    lmdtx__fre = []
    jnh__gwa = []
    for lfip__ddzao, c in enumerate(col_names):
        yqtju__hqszq = zasc__ridzl[c]
        col_indices.append(yqtju__hqszq)
        svry__adt.append(oidww__kpht[yqtju__hqszq])
        if not latd__bhodd[yqtju__hqszq]:
            lmdtx__fre.append(lfip__ddzao)
            jnh__gwa.append(cqlj__dof[yqtju__hqszq])
    return (col_names, svry__adt, pwn__tvp, col_indices, partition_names,
        lmdtx__fre, jnh__gwa)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    ztrl__kack = dictionary.to_pandas()
    xxl__egx = bodo.typeof(ztrl__kack).dtype
    if isinstance(xxl__egx, types.Integer):
        snsw__aimg = PDCategoricalDtype(tuple(ztrl__kack), xxl__egx, False,
            int_type=xxl__egx)
    else:
        snsw__aimg = PDCategoricalDtype(tuple(ztrl__kack), xxl__egx, False)
    return CategoricalArrayType(snsw__aimg)


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
        vtb__ilz = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        wcyct__vfpr = cgutils.get_or_insert_function(builder.module,
            vtb__ilz, name='pq_write')
        rbqtm__hjxjp = builder.call(wcyct__vfpr, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return rbqtm__hjxjp
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
        vtb__ilz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        wcyct__vfpr = cgutils.get_or_insert_function(builder.module,
            vtb__ilz, name='pq_write_partitioned')
        builder.call(wcyct__vfpr, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
