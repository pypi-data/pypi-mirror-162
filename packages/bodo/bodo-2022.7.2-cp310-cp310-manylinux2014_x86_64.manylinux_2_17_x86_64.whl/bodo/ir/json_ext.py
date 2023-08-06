import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
from numba.extending import intrinsic
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.utils import check_and_propagate_cpp_exception, check_java_installation, sanitize_varname


class JsonReader(ir.Stmt):

    def __init__(self, df_out, loc, out_vars, out_types, file_name,
        df_colnames, orient, convert_dates, precise_float, lines,
        compression, storage_options):
        self.connector_typ = 'json'
        self.df_out = df_out
        self.loc = loc
        self.out_vars = out_vars
        self.out_types = out_types
        self.file_name = file_name
        self.df_colnames = df_colnames
        self.orient = orient
        self.convert_dates = convert_dates
        self.precise_float = precise_float
        self.lines = lines
        self.compression = compression
        self.storage_options = storage_options

    def __repr__(self):
        return ('{} = ReadJson(file={}, col_names={}, types={}, vars={})'.
            format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars))


import llvmlite.binding as ll
from bodo.io import json_cpp
ll.add_symbol('json_file_chunk_reader', json_cpp.json_file_chunk_reader)


@intrinsic
def json_file_chunk_reader(typingctx, fname_t, lines_t, is_parallel_t,
    nrows_t, compression_t, bucket_region_t, storage_options_t):
    assert storage_options_t == storage_options_dict_type, "Storage options don't match expected type"

    def codegen(context, builder, sig, args):
        yphzz__jnbw = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        iyw__avfjm = cgutils.get_or_insert_function(builder.module,
            yphzz__jnbw, name='json_file_chunk_reader')
        twayj__pjpl = builder.call(iyw__avfjm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ypbxb__ildij = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        raj__cst = context.get_python_api(builder)
        ypbxb__ildij.meminfo = raj__cst.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), twayj__pjpl)
        ypbxb__ildij.pyobj = twayj__pjpl
        raj__cst.decref(twayj__pjpl)
        return ypbxb__ildij._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.bool_,
        types.int64, types.voidptr, types.voidptr, storage_options_dict_type
        ), codegen


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    dcuce__wteo = []
    cbowz__okchh = []
    ufsef__dphl = []
    for bpebp__qiyp, naio__erpmk in enumerate(json_node.out_vars):
        if naio__erpmk.name in lives:
            dcuce__wteo.append(json_node.df_colnames[bpebp__qiyp])
            cbowz__okchh.append(json_node.out_vars[bpebp__qiyp])
            ufsef__dphl.append(json_node.out_types[bpebp__qiyp])
    json_node.df_colnames = dcuce__wteo
    json_node.out_vars = cbowz__okchh
    json_node.out_types = ufsef__dphl
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        gbv__zbue = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        hwlhw__eoisz = json_node.loc.strformat()
        dspjc__ftzv = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', gbv__zbue,
            hwlhw__eoisz, dspjc__ftzv)
        wyl__zinc = [tcx__razw for bpebp__qiyp, tcx__razw in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            bpebp__qiyp], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if wyl__zinc:
            avu__srxq = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', avu__srxq,
                hwlhw__eoisz, wyl__zinc)
    parallel = False
    if array_dists is not None:
        parallel = True
        for mzn__ggf in json_node.out_vars:
            if array_dists[mzn__ggf.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                mzn__ggf.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    sesvl__tidoy = len(json_node.out_vars)
    num__ocomn = ', '.join('arr' + str(bpebp__qiyp) for bpebp__qiyp in
        range(sesvl__tidoy))
    mxly__eehwv = 'def json_impl(fname):\n'
    mxly__eehwv += '    ({},) = _json_reader_py(fname)\n'.format(num__ocomn)
    nxamx__ssbn = {}
    exec(mxly__eehwv, {}, nxamx__ssbn)
    urkx__qpnj = nxamx__ssbn['json_impl']
    dwohx__bif = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    xuy__aasom = compile_to_numba_ir(urkx__qpnj, {'_json_reader_py':
        dwohx__bif}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(xuy__aasom, [json_node.file_name])
    vysf__rxmu = xuy__aasom.body[:-3]
    for bpebp__qiyp in range(len(json_node.out_vars)):
        vysf__rxmu[-len(json_node.out_vars) + bpebp__qiyp
            ].target = json_node.out_vars[bpebp__qiyp]
    return vysf__rxmu


numba.parfors.array_analysis.array_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[JsonReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[JsonReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[JsonReader] = remove_dead_json
numba.core.analysis.ir_extension_usedefs[JsonReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[JsonReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[JsonReader] = json_distributed_run
compiled_funcs = []


def _gen_json_reader_py(col_names, col_typs, typingctx, targetctx, parallel,
    orient, convert_dates, precise_float, lines, compression, storage_options):
    qic__jkt = [sanitize_varname(tcx__razw) for tcx__razw in col_names]
    isssl__ymm = ', '.join(str(bpebp__qiyp) for bpebp__qiyp, onv__nrcu in
        enumerate(col_typs) if onv__nrcu.dtype == types.NPDatetime('ns'))
    lip__rwv = ', '.join(["{}='{}'".format(fnnlb__suzrb, bodo.ir.csv_ext.
        _get_dtype_str(onv__nrcu)) for fnnlb__suzrb, onv__nrcu in zip(
        qic__jkt, col_typs)])
    deupe__heoin = ', '.join(["'{}':{}".format(inro__juh, bodo.ir.csv_ext.
        _get_pd_dtype_str(onv__nrcu)) for inro__juh, onv__nrcu in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    mxly__eehwv = 'def json_reader_py(fname):\n'
    mxly__eehwv += '  df_typeref_2 = df_typeref\n'
    mxly__eehwv += '  check_java_installation(fname)\n'
    mxly__eehwv += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    mxly__eehwv += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    mxly__eehwv += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    mxly__eehwv += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    mxly__eehwv += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    mxly__eehwv += "      raise FileNotFoundError('File does not exist')\n"
    mxly__eehwv += f'  with objmode({lip__rwv}):\n'
    mxly__eehwv += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    mxly__eehwv += f'       convert_dates = {convert_dates}, \n'
    mxly__eehwv += f'       precise_float={precise_float}, \n'
    mxly__eehwv += f'       lines={lines}, \n'
    mxly__eehwv += '       dtype={{{}}},\n'.format(deupe__heoin)
    mxly__eehwv += '       )\n'
    mxly__eehwv += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for fnnlb__suzrb, inro__juh in zip(qic__jkt, col_names):
        mxly__eehwv += '    if len(df) > 0:\n'
        mxly__eehwv += "        {} = df['{}'].values\n".format(fnnlb__suzrb,
            inro__juh)
        mxly__eehwv += '    else:\n'
        mxly__eehwv += '        {} = np.array([])\n'.format(fnnlb__suzrb)
    mxly__eehwv += '  return ({},)\n'.format(', '.join(bni__duzc for
        bni__duzc in qic__jkt))
    xty__sfmvy = globals()
    xty__sfmvy.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    nxamx__ssbn = {}
    exec(mxly__eehwv, xty__sfmvy, nxamx__ssbn)
    dwohx__bif = nxamx__ssbn['json_reader_py']
    hxs__ydif = numba.njit(dwohx__bif)
    compiled_funcs.append(hxs__ydif)
    return hxs__ydif
