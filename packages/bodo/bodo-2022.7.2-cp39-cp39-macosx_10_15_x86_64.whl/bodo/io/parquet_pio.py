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
        except OSError as hhug__nbhap:
            if 'non-file path' in str(hhug__nbhap):
                raise FileNotFoundError(str(hhug__nbhap))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        vrsoc__auu = lhs.scope
        hyg__gwppk = lhs.loc
        oyqt__xzxo = None
        if lhs.name in self.locals:
            oyqt__xzxo = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        xtejd__vuxm = {}
        if lhs.name + ':convert' in self.locals:
            xtejd__vuxm = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if oyqt__xzxo is None:
            cfgy__ehh = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            mhgfq__wmmbr = get_const_value(file_name, self.func_ir,
                cfgy__ehh, arg_types=self.args, file_info=ParquetFileInfo(
                columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            lsj__iima = False
            plsz__qpmd = guard(get_definition, self.func_ir, file_name)
            if isinstance(plsz__qpmd, ir.Arg):
                typ = self.args[plsz__qpmd.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, pngb__yzurq, pvgmx__frx, col_indices,
                        partition_names, ltiid__ltgkl, viu__hxmen) = typ.schema
                    lsj__iima = True
            if not lsj__iima:
                (col_names, pngb__yzurq, pvgmx__frx, col_indices,
                    partition_names, ltiid__ltgkl, viu__hxmen) = (
                    parquet_file_schema(mhgfq__wmmbr, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            nico__liyk = list(oyqt__xzxo.keys())
            fqowf__mghob = {c: ponv__musz for ponv__musz, c in enumerate(
                nico__liyk)}
            mebpj__jkw = [fdqxr__vhu for fdqxr__vhu in oyqt__xzxo.values()]
            pvgmx__frx = 'index' if 'index' in fqowf__mghob else None
            if columns is None:
                selected_columns = nico__liyk
            else:
                selected_columns = columns
            col_indices = [fqowf__mghob[c] for c in selected_columns]
            pngb__yzurq = [mebpj__jkw[fqowf__mghob[c]] for c in
                selected_columns]
            col_names = selected_columns
            pvgmx__frx = pvgmx__frx if pvgmx__frx in col_names else None
            partition_names = []
            ltiid__ltgkl = []
            viu__hxmen = []
        yiav__kwlwl = None if isinstance(pvgmx__frx, dict
            ) or pvgmx__frx is None else pvgmx__frx
        index_column_index = None
        index_column_type = types.none
        if yiav__kwlwl:
            kldjb__ttk = col_names.index(yiav__kwlwl)
            index_column_index = col_indices.pop(kldjb__ttk)
            index_column_type = pngb__yzurq.pop(kldjb__ttk)
            col_names.pop(kldjb__ttk)
        for ponv__musz, c in enumerate(col_names):
            if c in xtejd__vuxm:
                pngb__yzurq[ponv__musz] = xtejd__vuxm[c]
        ixz__yfo = [ir.Var(vrsoc__auu, mk_unique_var('pq_table'),
            hyg__gwppk), ir.Var(vrsoc__auu, mk_unique_var('pq_index'),
            hyg__gwppk)]
        izdl__ovun = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, pngb__yzurq, ixz__yfo, hyg__gwppk,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, ltiid__ltgkl, viu__hxmen)]
        return (col_names, ixz__yfo, pvgmx__frx, izdl__ovun, pngb__yzurq,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    ooc__ayroe = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    gay__dcxp, ujz__tuxwb = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(gay__dcxp.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, gay__dcxp, ujz__tuxwb, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    axn__kori = ', '.join(f'out{ponv__musz}' for ponv__musz in range(
        ooc__ayroe))
    exvnl__vnhm = f'def pq_impl(fname, {extra_args}):\n'
    exvnl__vnhm += (
        f'    (total_rows, {axn__kori},) = _pq_reader_py(fname, {extra_args})\n'
        )
    sfsu__dbf = {}
    exec(exvnl__vnhm, {}, sfsu__dbf)
    litlm__xxm = sfsu__dbf['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        oao__nggr = pq_node.loc.strformat()
        din__ntr = []
        lwcdh__vfvy = []
        for ponv__musz in pq_node.out_used_cols:
            dvzs__kxpoq = pq_node.df_colnames[ponv__musz]
            din__ntr.append(dvzs__kxpoq)
            if isinstance(pq_node.out_types[ponv__musz], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                lwcdh__vfvy.append(dvzs__kxpoq)
        fmst__beaed = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', fmst__beaed,
            oao__nggr, din__ntr)
        if lwcdh__vfvy:
            ekevd__xthl = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                ekevd__xthl, oao__nggr, lwcdh__vfvy)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        roc__ffmc = set(pq_node.out_used_cols)
        doq__qog = set(pq_node.unsupported_columns)
        fogp__kjit = roc__ffmc & doq__qog
        if fogp__kjit:
            nhfc__zcfy = sorted(fogp__kjit)
            arz__psgd = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            uap__xta = 0
            for iir__ryuj in nhfc__zcfy:
                while pq_node.unsupported_columns[uap__xta] != iir__ryuj:
                    uap__xta += 1
                arz__psgd.append(
                    f"Column '{pq_node.df_colnames[iir__ryuj]}' with unsupported arrow type {pq_node.unsupported_arrow_types[uap__xta]}"
                    )
                uap__xta += 1
            oeedi__exc = '\n'.join(arz__psgd)
            raise BodoError(oeedi__exc, loc=pq_node.loc)
    nqap__miezs = _gen_pq_reader_py(pq_node.df_colnames, pq_node.
        col_indices, pq_node.out_used_cols, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    koei__hhb = typemap[pq_node.file_name.name]
    ozxn__cpgbs = (koei__hhb,) + tuple(typemap[lrye__jns.name] for
        lrye__jns in ujz__tuxwb)
    jzeiw__lkpc = compile_to_numba_ir(litlm__xxm, {'_pq_reader_py':
        nqap__miezs}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        ozxn__cpgbs, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(jzeiw__lkpc, [pq_node.file_name] + ujz__tuxwb)
    izdl__ovun = jzeiw__lkpc.body[:-3]
    if meta_head_only_info:
        izdl__ovun[-3].target = meta_head_only_info[1]
    izdl__ovun[-2].target = pq_node.out_vars[0]
    izdl__ovun[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        izdl__ovun.pop(-1)
    elif not pq_node.out_used_cols:
        izdl__ovun.pop(-2)
    return izdl__ovun


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    ujdy__pqhp = get_overload_const_str(dnf_filter_str)
    izrkt__tcbxc = get_overload_const_str(expr_filter_str)
    ran__wgokt = ', '.join(f'f{ponv__musz}' for ponv__musz in range(len(
        var_tup)))
    exvnl__vnhm = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        exvnl__vnhm += f'  {ran__wgokt}, = var_tup\n'
    exvnl__vnhm += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    exvnl__vnhm += f'    dnf_filters_py = {ujdy__pqhp}\n'
    exvnl__vnhm += f'    expr_filters_py = {izrkt__tcbxc}\n'
    exvnl__vnhm += '  return (dnf_filters_py, expr_filters_py)\n'
    sfsu__dbf = {}
    exec(exvnl__vnhm, globals(), sfsu__dbf)
    return sfsu__dbf['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    kli__wnc = next_label()
    zdon__aidw = ',' if extra_args else ''
    exvnl__vnhm = f'def pq_reader_py(fname,{extra_args}):\n'
    exvnl__vnhm += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    exvnl__vnhm += f"    ev.add_attribute('g_fname', fname)\n"
    exvnl__vnhm += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{zdon__aidw}))
"""
    exvnl__vnhm += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    exvnl__vnhm += f"""    storage_options_py = get_storage_options_pyobject({str(storage_options)})
"""
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    zoiw__pnn = not out_used_cols
    fhzvu__ixgq = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    qoqlk__kvf = {c: ponv__musz for ponv__musz, c in enumerate(col_indices)}
    ovvxp__cvzjv = {c: ponv__musz for ponv__musz, c in enumerate(fhzvu__ixgq)}
    zpfze__huaym = []
    bml__zft = set()
    zquth__uie = partition_names + [input_file_name_col]
    for ponv__musz in out_used_cols:
        if fhzvu__ixgq[ponv__musz] not in zquth__uie:
            zpfze__huaym.append(col_indices[ponv__musz])
        elif not input_file_name_col or fhzvu__ixgq[ponv__musz
            ] != input_file_name_col:
            bml__zft.add(col_indices[ponv__musz])
    if index_column_index is not None:
        zpfze__huaym.append(index_column_index)
    zpfze__huaym = sorted(zpfze__huaym)
    yitsg__tdak = {c: ponv__musz for ponv__musz, c in enumerate(zpfze__huaym)}
    bcvsc__nbu = [(int(is_nullable(out_types[qoqlk__kvf[nwygj__ygyr]])) if 
        nwygj__ygyr != index_column_index else int(is_nullable(
        index_column_type))) for nwygj__ygyr in zpfze__huaym]
    str_as_dict_cols = []
    for nwygj__ygyr in zpfze__huaym:
        if nwygj__ygyr == index_column_index:
            fdqxr__vhu = index_column_type
        else:
            fdqxr__vhu = out_types[qoqlk__kvf[nwygj__ygyr]]
        if fdqxr__vhu == dict_str_arr_type:
            str_as_dict_cols.append(nwygj__ygyr)
    mjae__zzf = []
    esijd__bhyd = {}
    agdl__laa = []
    xrah__iyjq = []
    for ponv__musz, ybhm__sgg in enumerate(partition_names):
        try:
            foi__qhr = ovvxp__cvzjv[ybhm__sgg]
            if col_indices[foi__qhr] not in bml__zft:
                continue
        except (KeyError, ValueError) as kskg__ijocy:
            continue
        esijd__bhyd[ybhm__sgg] = len(mjae__zzf)
        mjae__zzf.append(ybhm__sgg)
        agdl__laa.append(ponv__musz)
        xjbqi__qud = out_types[foi__qhr].dtype
        aqdh__rwe = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            xjbqi__qud)
        xrah__iyjq.append(numba_to_c_type(aqdh__rwe))
    exvnl__vnhm += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    exvnl__vnhm += f'    out_table = pq_read(\n'
    exvnl__vnhm += f'        fname_py, {is_parallel},\n'
    exvnl__vnhm += f'        dnf_filters, expr_filters,\n'
    exvnl__vnhm += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{kli__wnc}.ctypes,
"""
    exvnl__vnhm += f'        {len(zpfze__huaym)},\n'
    exvnl__vnhm += f'        nullable_cols_arr_{kli__wnc}.ctypes,\n'
    if len(agdl__laa) > 0:
        exvnl__vnhm += (
            f'        np.array({agdl__laa}, dtype=np.int32).ctypes,\n')
        exvnl__vnhm += (
            f'        np.array({xrah__iyjq}, dtype=np.int32).ctypes,\n')
        exvnl__vnhm += f'        {len(agdl__laa)},\n'
    else:
        exvnl__vnhm += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        exvnl__vnhm += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        exvnl__vnhm += f'        0, 0,\n'
    exvnl__vnhm += f'        total_rows_np.ctypes,\n'
    exvnl__vnhm += f'        {input_file_name_col is not None},\n'
    exvnl__vnhm += f'    )\n'
    exvnl__vnhm += f'    check_and_propagate_cpp_exception()\n'
    clhf__cbl = 'None'
    uij__aunp = index_column_type
    bns__fhjd = TableType(tuple(out_types))
    if zoiw__pnn:
        bns__fhjd = types.none
    if index_column_index is not None:
        mflp__zed = yitsg__tdak[index_column_index]
        clhf__cbl = (
            f'info_to_array(info_from_table(out_table, {mflp__zed}), index_arr_type)'
            )
    exvnl__vnhm += f'    index_arr = {clhf__cbl}\n'
    if zoiw__pnn:
        npww__zoydi = None
    else:
        npww__zoydi = []
        xwtni__paqs = 0
        ipxn__qeo = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for ponv__musz, iir__ryuj in enumerate(col_indices):
            if xwtni__paqs < len(out_used_cols
                ) and ponv__musz == out_used_cols[xwtni__paqs]:
                xxw__mfyy = col_indices[ponv__musz]
                if ipxn__qeo and xxw__mfyy == ipxn__qeo:
                    npww__zoydi.append(len(zpfze__huaym) + len(mjae__zzf))
                elif xxw__mfyy in bml__zft:
                    hmyz__qli = fhzvu__ixgq[ponv__musz]
                    npww__zoydi.append(len(zpfze__huaym) + esijd__bhyd[
                        hmyz__qli])
                else:
                    npww__zoydi.append(yitsg__tdak[iir__ryuj])
                xwtni__paqs += 1
            else:
                npww__zoydi.append(-1)
        npww__zoydi = np.array(npww__zoydi, dtype=np.int64)
    if zoiw__pnn:
        exvnl__vnhm += '    T = None\n'
    else:
        exvnl__vnhm += f"""    T = cpp_table_to_py_table(out_table, table_idx_{kli__wnc}, py_table_type_{kli__wnc})
"""
    exvnl__vnhm += f'    delete_table(out_table)\n'
    exvnl__vnhm += f'    total_rows = total_rows_np[0]\n'
    exvnl__vnhm += f'    ev.finalize()\n'
    exvnl__vnhm += f'    return (total_rows, T, index_arr)\n'
    sfsu__dbf = {}
    eejso__pxogk = {f'py_table_type_{kli__wnc}': bns__fhjd,
        f'table_idx_{kli__wnc}': npww__zoydi,
        f'selected_cols_arr_{kli__wnc}': np.array(zpfze__huaym, np.int32),
        f'nullable_cols_arr_{kli__wnc}': np.array(bcvsc__nbu, np.int32),
        'index_arr_type': uij__aunp, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(exvnl__vnhm, eejso__pxogk, sfsu__dbf)
    nqap__miezs = sfsu__dbf['pq_reader_py']
    xndm__thwf = numba.njit(nqap__miezs, no_cpython_wrapper=True)
    return xndm__thwf


def unify_schemas(schemas):
    vuqy__tjqmp = []
    for schema in schemas:
        for ponv__musz in range(len(schema)):
            bmo__szrmp = schema.field(ponv__musz)
            if bmo__szrmp.type == pa.large_string():
                schema = schema.set(ponv__musz, bmo__szrmp.with_type(pa.
                    string()))
            elif bmo__szrmp.type == pa.large_binary():
                schema = schema.set(ponv__musz, bmo__szrmp.with_type(pa.
                    binary()))
            elif isinstance(bmo__szrmp.type, (pa.ListType, pa.LargeListType)
                ) and bmo__szrmp.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(ponv__musz, bmo__szrmp.with_type(pa.
                    list_(pa.field(bmo__szrmp.type.value_field.name, pa.
                    string()))))
            elif isinstance(bmo__szrmp.type, pa.LargeListType):
                schema = schema.set(ponv__musz, bmo__szrmp.with_type(pa.
                    list_(pa.field(bmo__szrmp.type.value_field.name,
                    bmo__szrmp.type.value_type))))
        vuqy__tjqmp.append(schema)
    return pa.unify_schemas(vuqy__tjqmp)


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
        for ponv__musz in range(len(self.schema)):
            bmo__szrmp = self.schema.field(ponv__musz)
            if bmo__szrmp.type == pa.large_string():
                self.schema = self.schema.set(ponv__musz, bmo__szrmp.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for oyy__uuy in self.pieces:
            oyy__uuy.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            txqv__mdlmr = {oyy__uuy: self.partitioning_dictionaries[
                ponv__musz] for ponv__musz, oyy__uuy in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, txqv__mdlmr)


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
            self.partition_keys = [(ybhm__sgg, partitioning.dictionaries[
                ponv__musz].index(self.partition_keys[ybhm__sgg]).as_py()) for
                ponv__musz, ybhm__sgg in enumerate(partition_names)]

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
        ltxv__ztepv = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    kmh__nshkg = MPI.COMM_WORLD
    if isinstance(fpath, list):
        umjth__zgji = urlparse(fpath[0])
        protocol = umjth__zgji.scheme
        nmdp__hfhy = umjth__zgji.netloc
        for ponv__musz in range(len(fpath)):
            bmo__szrmp = fpath[ponv__musz]
            bkuc__fwqf = urlparse(bmo__szrmp)
            if bkuc__fwqf.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if bkuc__fwqf.netloc != nmdp__hfhy:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[ponv__musz] = bmo__szrmp.rstrip('/')
    else:
        umjth__zgji = urlparse(fpath)
        protocol = umjth__zgji.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as kskg__ijocy:
            dsgpn__qnr = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(dsgpn__qnr)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as kskg__ijocy:
            dsgpn__qnr = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            uwlya__qthns = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(uwlya__qthns)))
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
            ztz__fnbcu = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(ztz__fnbcu) == 0:
            raise BodoError('No files found matching glob pattern')
        return ztz__fnbcu
    sgdq__vtxs = False
    if get_row_counts:
        cdixw__xnnbr = getfs(parallel=True)
        sgdq__vtxs = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        acoi__rsd = 1
        qvzku__yeggz = os.cpu_count()
        if qvzku__yeggz is not None and qvzku__yeggz > 1:
            acoi__rsd = qvzku__yeggz // 2
        try:
            if get_row_counts:
                qxapv__qrr = tracing.Event('pq.ParquetDataset', is_parallel
                    =False)
                if tracing.is_tracing():
                    qxapv__qrr.add_attribute('g_dnf_filter', str(dnf_filters))
            lya__ais = pa.io_thread_count()
            pa.set_io_thread_count(acoi__rsd)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{umjth__zgji.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    uif__ofe = [bmo__szrmp[len(prefix):] for bmo__szrmp in
                        fpath]
                else:
                    uif__ofe = fpath[len(prefix):]
            else:
                uif__ofe = fpath
            if isinstance(uif__ofe, list):
                ztubw__bsy = []
                for oyy__uuy in uif__ofe:
                    if has_magic(oyy__uuy):
                        ztubw__bsy += glob(protocol, getfs(), oyy__uuy)
                    else:
                        ztubw__bsy.append(oyy__uuy)
                uif__ofe = ztubw__bsy
            elif has_magic(uif__ofe):
                uif__ofe = glob(protocol, getfs(), uif__ofe)
            cewd__huhon = pq.ParquetDataset(uif__ofe, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                cewd__huhon._filters = dnf_filters
                cewd__huhon._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            dhrw__gnpkw = len(cewd__huhon.files)
            cewd__huhon = ParquetDataset(cewd__huhon, prefix)
            pa.set_io_thread_count(lya__ais)
            if typing_pa_schema:
                cewd__huhon.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    qxapv__qrr.add_attribute('num_pieces_before_filter',
                        dhrw__gnpkw)
                    qxapv__qrr.add_attribute('num_pieces_after_filter', len
                        (cewd__huhon.pieces))
                qxapv__qrr.finalize()
        except Exception as hhug__nbhap:
            if isinstance(hhug__nbhap, IsADirectoryError):
                hhug__nbhap = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(hhug__nbhap, (
                OSError, FileNotFoundError)):
                hhug__nbhap = BodoError(str(hhug__nbhap) +
                    list_of_files_error_msg)
            else:
                hhug__nbhap = BodoError(
                    f"""error from pyarrow: {type(hhug__nbhap).__name__}: {str(hhug__nbhap)}
"""
                    )
            kmh__nshkg.bcast(hhug__nbhap)
            raise hhug__nbhap
        if get_row_counts:
            svtyn__lkv = tracing.Event('bcast dataset')
        cewd__huhon = kmh__nshkg.bcast(cewd__huhon)
    else:
        if get_row_counts:
            svtyn__lkv = tracing.Event('bcast dataset')
        cewd__huhon = kmh__nshkg.bcast(None)
        if isinstance(cewd__huhon, Exception):
            ifs__nit = cewd__huhon
            raise ifs__nit
    cewd__huhon.set_fs(getfs())
    if get_row_counts:
        svtyn__lkv.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = sgdq__vtxs = False
    if get_row_counts or sgdq__vtxs:
        if get_row_counts and tracing.is_tracing():
            idsu__azbz = tracing.Event('get_row_counts')
            idsu__azbz.add_attribute('g_num_pieces', len(cewd__huhon.pieces))
            idsu__azbz.add_attribute('g_expr_filters', str(expr_filters))
        qpkr__ezh = 0.0
        num_pieces = len(cewd__huhon.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        dehmn__dqf = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        zrtar__oegdq = 0
        ljpyr__srocz = 0
        qijwq__dzyl = 0
        lqz__ulon = True
        if expr_filters is not None:
            import random
            random.seed(37)
            dfn__eglq = random.sample(cewd__huhon.pieces, k=len(cewd__huhon
                .pieces))
        else:
            dfn__eglq = cewd__huhon.pieces
        fpaths = [oyy__uuy.path for oyy__uuy in dfn__eglq[start:dehmn__dqf]]
        acoi__rsd = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(acoi__rsd)
        pa.set_cpu_count(acoi__rsd)
        ifs__nit = None
        try:
            tbzhn__mgpxz = ds.dataset(fpaths, filesystem=cewd__huhon.
                filesystem, partitioning=cewd__huhon.partitioning)
            for fyg__inc, frag in zip(dfn__eglq[start:dehmn__dqf],
                tbzhn__mgpxz.get_fragments()):
                if sgdq__vtxs:
                    kwady__zmiio = frag.metadata.schema.to_arrow_schema()
                    gqk__wio = set(kwady__zmiio.names)
                    soj__imsq = set(cewd__huhon.schema.names) - set(cewd__huhon
                        .partition_names)
                    if soj__imsq != gqk__wio:
                        yzwxn__mjs = gqk__wio - soj__imsq
                        siowy__ptvkd = soj__imsq - gqk__wio
                        cfgy__ehh = f'Schema in {fyg__inc} was different.\n'
                        if yzwxn__mjs:
                            cfgy__ehh += f"""File contains column(s) {yzwxn__mjs} not found in other files in the dataset.
"""
                        if siowy__ptvkd:
                            cfgy__ehh += f"""File missing column(s) {siowy__ptvkd} found in other files in the dataset.
"""
                        raise BodoError(cfgy__ehh)
                    try:
                        cewd__huhon.schema = unify_schemas([cewd__huhon.
                            schema, kwady__zmiio])
                    except Exception as hhug__nbhap:
                        cfgy__ehh = (
                            f'Schema in {fyg__inc} was different.\n' + str(
                            hhug__nbhap))
                        raise BodoError(cfgy__ehh)
                frx__dnn = time.time()
                hslyh__wnv = frag.scanner(schema=tbzhn__mgpxz.schema,
                    filter=expr_filters, use_threads=True).count_rows()
                qpkr__ezh += time.time() - frx__dnn
                fyg__inc._bodo_num_rows = hslyh__wnv
                zrtar__oegdq += hslyh__wnv
                ljpyr__srocz += frag.num_row_groups
                qijwq__dzyl += sum(ezcv__yut.total_byte_size for ezcv__yut in
                    frag.row_groups)
        except Exception as hhug__nbhap:
            ifs__nit = hhug__nbhap
        if kmh__nshkg.allreduce(ifs__nit is not None, op=MPI.LOR):
            for ifs__nit in kmh__nshkg.allgather(ifs__nit):
                if ifs__nit:
                    if isinstance(fpath, list) and isinstance(ifs__nit, (
                        OSError, FileNotFoundError)):
                        raise BodoError(str(ifs__nit) + list_of_files_error_msg
                            )
                    raise ifs__nit
        if sgdq__vtxs:
            lqz__ulon = kmh__nshkg.allreduce(lqz__ulon, op=MPI.LAND)
            if not lqz__ulon:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            cewd__huhon._bodo_total_rows = kmh__nshkg.allreduce(zrtar__oegdq,
                op=MPI.SUM)
            yitps__thc = kmh__nshkg.allreduce(ljpyr__srocz, op=MPI.SUM)
            lgd__fcxlw = kmh__nshkg.allreduce(qijwq__dzyl, op=MPI.SUM)
            jwd__wnktg = np.array([oyy__uuy._bodo_num_rows for oyy__uuy in
                cewd__huhon.pieces])
            jwd__wnktg = kmh__nshkg.allreduce(jwd__wnktg, op=MPI.SUM)
            for oyy__uuy, asy__eqnj in zip(cewd__huhon.pieces, jwd__wnktg):
                oyy__uuy._bodo_num_rows = asy__eqnj
            if is_parallel and bodo.get_rank(
                ) == 0 and yitps__thc < bodo.get_size() and yitps__thc != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({yitps__thc}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if yitps__thc == 0:
                jzq__kgsml = 0
            else:
                jzq__kgsml = lgd__fcxlw // yitps__thc
            if (bodo.get_rank() == 0 and lgd__fcxlw >= 20 * 1048576 and 
                jzq__kgsml < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({jzq__kgsml} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                idsu__azbz.add_attribute('g_total_num_row_groups', yitps__thc)
                idsu__azbz.add_attribute('total_scan_time', qpkr__ezh)
                jit__fbsr = np.array([oyy__uuy._bodo_num_rows for oyy__uuy in
                    cewd__huhon.pieces])
                ctwve__jqvkq = np.percentile(jit__fbsr, [25, 50, 75])
                idsu__azbz.add_attribute('g_row_counts_min', jit__fbsr.min())
                idsu__azbz.add_attribute('g_row_counts_Q1', ctwve__jqvkq[0])
                idsu__azbz.add_attribute('g_row_counts_median', ctwve__jqvkq[1]
                    )
                idsu__azbz.add_attribute('g_row_counts_Q3', ctwve__jqvkq[2])
                idsu__azbz.add_attribute('g_row_counts_max', jit__fbsr.max())
                idsu__azbz.add_attribute('g_row_counts_mean', jit__fbsr.mean())
                idsu__azbz.add_attribute('g_row_counts_std', jit__fbsr.std())
                idsu__azbz.add_attribute('g_row_counts_sum', jit__fbsr.sum())
                idsu__azbz.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(cewd__huhon)
    if get_row_counts:
        ltxv__ztepv.finalize()
    if sgdq__vtxs and is_parallel:
        if tracing.is_tracing():
            aqb__zaet = tracing.Event('unify_schemas_across_ranks')
        ifs__nit = None
        try:
            cewd__huhon.schema = kmh__nshkg.allreduce(cewd__huhon.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as hhug__nbhap:
            ifs__nit = hhug__nbhap
        if tracing.is_tracing():
            aqb__zaet.finalize()
        if kmh__nshkg.allreduce(ifs__nit is not None, op=MPI.LOR):
            for ifs__nit in kmh__nshkg.allgather(ifs__nit):
                if ifs__nit:
                    cfgy__ehh = (f'Schema in some files were different.\n' +
                        str(ifs__nit))
                    raise BodoError(cfgy__ehh)
    return cewd__huhon


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    qvzku__yeggz = os.cpu_count()
    if qvzku__yeggz is None or qvzku__yeggz == 0:
        qvzku__yeggz = 2
    drl__jkxvd = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)),
        qvzku__yeggz)
    uow__evn = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), qvzku__yeggz
        )
    if is_parallel and len(fpaths) > uow__evn and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(uow__evn)
        pa.set_cpu_count(uow__evn)
    else:
        pa.set_io_thread_count(drl__jkxvd)
        pa.set_cpu_count(drl__jkxvd)
    ydwj__yrmrl = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    vdiny__svxse = set(str_as_dict_cols)
    for ponv__musz, name in enumerate(schema.names):
        if name in vdiny__svxse:
            gmpxh__bzuwc = schema.field(ponv__musz)
            bhbnn__xlv = pa.field(name, pa.dictionary(pa.int32(),
                gmpxh__bzuwc.type), gmpxh__bzuwc.nullable)
            schema = schema.remove(ponv__musz).insert(ponv__musz, bhbnn__xlv)
    cewd__huhon = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=ydwj__yrmrl)
    col_names = cewd__huhon.schema.names
    riec__cyh = [col_names[fza__tpxp] for fza__tpxp in selected_fields]
    otued__mkuie = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if otued__mkuie and expr_filters is None:
        uav__vokf = []
        zqh__csfhm = 0
        gcepm__apyo = 0
        for frag in cewd__huhon.get_fragments():
            sgl__yivtn = []
            for ezcv__yut in frag.row_groups:
                mqut__zcpa = ezcv__yut.num_rows
                if start_offset < zqh__csfhm + mqut__zcpa:
                    if gcepm__apyo == 0:
                        jkwk__koo = start_offset - zqh__csfhm
                        ndppl__ktl = min(mqut__zcpa - jkwk__koo, rows_to_read)
                    else:
                        ndppl__ktl = min(mqut__zcpa, rows_to_read - gcepm__apyo
                            )
                    gcepm__apyo += ndppl__ktl
                    sgl__yivtn.append(ezcv__yut.id)
                zqh__csfhm += mqut__zcpa
                if gcepm__apyo == rows_to_read:
                    break
            uav__vokf.append(frag.subset(row_group_ids=sgl__yivtn))
            if gcepm__apyo == rows_to_read:
                break
        cewd__huhon = ds.FileSystemDataset(uav__vokf, cewd__huhon.schema,
            ydwj__yrmrl, filesystem=cewd__huhon.filesystem)
        start_offset = jkwk__koo
    aqka__qnrz = cewd__huhon.scanner(columns=riec__cyh, filter=expr_filters,
        use_threads=True).to_reader()
    return cewd__huhon, aqka__qnrz, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    ntx__nrknr = [c for c in pa_schema.names if isinstance(pa_schema.field(
        c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(ntx__nrknr) == 0:
        pq_dataset._category_info = {}
        return
    kmh__nshkg = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            ushnt__xeoo = pq_dataset.pieces[0].frag.head(100, columns=
                ntx__nrknr)
            jyh__xry = {c: tuple(ushnt__xeoo.column(c).chunk(0).dictionary.
                to_pylist()) for c in ntx__nrknr}
            del ushnt__xeoo
        except Exception as hhug__nbhap:
            kmh__nshkg.bcast(hhug__nbhap)
            raise hhug__nbhap
        kmh__nshkg.bcast(jyh__xry)
    else:
        jyh__xry = kmh__nshkg.bcast(None)
        if isinstance(jyh__xry, Exception):
            ifs__nit = jyh__xry
            raise ifs__nit
    pq_dataset._category_info = jyh__xry


def get_pandas_metadata(schema, num_pieces):
    pvgmx__frx = None
    ezqqc__zffop = defaultdict(lambda : None)
    gncr__cgu = b'pandas'
    if schema.metadata is not None and gncr__cgu in schema.metadata:
        import json
        xho__ncnd = json.loads(schema.metadata[gncr__cgu].decode('utf8'))
        ocvt__zfcej = len(xho__ncnd['index_columns'])
        if ocvt__zfcej > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        pvgmx__frx = xho__ncnd['index_columns'][0] if ocvt__zfcej else None
        if not isinstance(pvgmx__frx, str) and not isinstance(pvgmx__frx, dict
            ):
            pvgmx__frx = None
        for bvo__gslu in xho__ncnd['columns']:
            rlf__dhsd = bvo__gslu['name']
            if bvo__gslu['pandas_type'].startswith('int'
                ) and rlf__dhsd is not None:
                if bvo__gslu['numpy_type'].startswith('Int'):
                    ezqqc__zffop[rlf__dhsd] = True
                else:
                    ezqqc__zffop[rlf__dhsd] = False
    return pvgmx__frx, ezqqc__zffop


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for rlf__dhsd in pa_schema.names:
        oajz__cvkt = pa_schema.field(rlf__dhsd)
        if oajz__cvkt.type in (pa.string(), pa.large_string()):
            str_columns.append(rlf__dhsd)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    kmh__nshkg = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        dfn__eglq = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        dfn__eglq = pq_dataset.pieces
    rll__nbhek = np.zeros(len(str_columns), dtype=np.int64)
    vwm__hoal = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(dfn__eglq):
        fyg__inc = dfn__eglq[bodo.get_rank()]
        try:
            metadata = fyg__inc.metadata
            for ponv__musz in range(fyg__inc.num_row_groups):
                for xwtni__paqs, rlf__dhsd in enumerate(str_columns):
                    uap__xta = pa_schema.get_field_index(rlf__dhsd)
                    rll__nbhek[xwtni__paqs] += metadata.row_group(ponv__musz
                        ).column(uap__xta).total_uncompressed_size
            jfrt__vyxl = metadata.num_rows
        except Exception as hhug__nbhap:
            if isinstance(hhug__nbhap, (OSError, FileNotFoundError)):
                jfrt__vyxl = 0
            else:
                raise
    else:
        jfrt__vyxl = 0
    jxq__kez = kmh__nshkg.allreduce(jfrt__vyxl, op=MPI.SUM)
    if jxq__kez == 0:
        return set()
    kmh__nshkg.Allreduce(rll__nbhek, vwm__hoal, op=MPI.SUM)
    khpiu__ttaav = vwm__hoal / jxq__kez
    nbd__tfm = set()
    for ponv__musz, pexui__qquky in enumerate(khpiu__ttaav):
        if pexui__qquky < READ_STR_AS_DICT_THRESHOLD:
            rlf__dhsd = str_columns[ponv__musz][0]
            nbd__tfm.add(rlf__dhsd)
    return nbd__tfm


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    pngb__yzurq = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    agr__nwvrn = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    xpvo__ulbns = read_as_dict_cols - agr__nwvrn
    if len(xpvo__ulbns) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {xpvo__ulbns}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(agr__nwvrn)
    agr__nwvrn = agr__nwvrn - read_as_dict_cols
    str_columns = [bgt__asaip for bgt__asaip in str_columns if bgt__asaip in
        agr__nwvrn]
    nbd__tfm: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    nbd__tfm.update(read_as_dict_cols)
    col_names = pa_schema.names
    pvgmx__frx, ezqqc__zffop = get_pandas_metadata(pa_schema, num_pieces)
    mebpj__jkw = []
    wfi__wunoc = []
    ghef__xrzq = []
    for ponv__musz, c in enumerate(col_names):
        if c in partition_names:
            continue
        oajz__cvkt = pa_schema.field(c)
        emp__llqq, qev__ujx = _get_numba_typ_from_pa_typ(oajz__cvkt, c ==
            pvgmx__frx, ezqqc__zffop[c], pq_dataset._category_info,
            str_as_dict=c in nbd__tfm)
        mebpj__jkw.append(emp__llqq)
        wfi__wunoc.append(qev__ujx)
        ghef__xrzq.append(oajz__cvkt.type)
    if partition_names:
        mebpj__jkw += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[ponv__musz]) for ponv__musz in range(
            len(partition_names))]
        wfi__wunoc.extend([True] * len(partition_names))
        ghef__xrzq.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        mebpj__jkw += [dict_str_arr_type]
        wfi__wunoc.append(True)
        ghef__xrzq.append(None)
    lho__jmv = {c: ponv__musz for ponv__musz, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in lho__jmv:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if pvgmx__frx and not isinstance(pvgmx__frx, dict
        ) and pvgmx__frx not in selected_columns:
        selected_columns.append(pvgmx__frx)
    col_names = selected_columns
    col_indices = []
    pngb__yzurq = []
    ltiid__ltgkl = []
    viu__hxmen = []
    for ponv__musz, c in enumerate(col_names):
        xxw__mfyy = lho__jmv[c]
        col_indices.append(xxw__mfyy)
        pngb__yzurq.append(mebpj__jkw[xxw__mfyy])
        if not wfi__wunoc[xxw__mfyy]:
            ltiid__ltgkl.append(ponv__musz)
            viu__hxmen.append(ghef__xrzq[xxw__mfyy])
    return (col_names, pngb__yzurq, pvgmx__frx, col_indices,
        partition_names, ltiid__ltgkl, viu__hxmen)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    bvrc__csle = dictionary.to_pandas()
    smgkf__wgd = bodo.typeof(bvrc__csle).dtype
    if isinstance(smgkf__wgd, types.Integer):
        bca__whh = PDCategoricalDtype(tuple(bvrc__csle), smgkf__wgd, False,
            int_type=smgkf__wgd)
    else:
        bca__whh = PDCategoricalDtype(tuple(bvrc__csle), smgkf__wgd, False)
    return CategoricalArrayType(bca__whh)


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
        qpdlv__txa = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        xcsgf__fig = cgutils.get_or_insert_function(builder.module,
            qpdlv__txa, name='pq_write')
        uppuh__fityl = builder.call(xcsgf__fig, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return uppuh__fityl
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
        qpdlv__txa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        xcsgf__fig = cgutils.get_or_insert_function(builder.module,
            qpdlv__txa, name='pq_write_partitioned')
        builder.call(xcsgf__fig, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
