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
        ykq__ipc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        nuq__gst = cgutils.get_or_insert_function(builder.module, ykq__ipc,
            name='json_file_chunk_reader')
        gfn__yabhv = builder.call(nuq__gst, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        mqm__apo = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        ztvh__bjmr = context.get_python_api(builder)
        mqm__apo.meminfo = ztvh__bjmr.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), gfn__yabhv)
        mqm__apo.pyobj = gfn__yabhv
        ztvh__bjmr.decref(gfn__yabhv)
        return mqm__apo._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.bool_,
        types.int64, types.voidptr, types.voidptr, storage_options_dict_type
        ), codegen


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    nscu__lzlb = []
    ljyl__yjeh = []
    uuhxl__bve = []
    for dfwqo__npw, pfd__gtcge in enumerate(json_node.out_vars):
        if pfd__gtcge.name in lives:
            nscu__lzlb.append(json_node.df_colnames[dfwqo__npw])
            ljyl__yjeh.append(json_node.out_vars[dfwqo__npw])
            uuhxl__bve.append(json_node.out_types[dfwqo__npw])
    json_node.df_colnames = nscu__lzlb
    json_node.out_vars = ljyl__yjeh
    json_node.out_types = uuhxl__bve
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        ciney__lgd = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        gpw__qcv = json_node.loc.strformat()
        cei__oqg = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', ciney__lgd,
            gpw__qcv, cei__oqg)
        hxti__osbdr = [fdj__bchhn for dfwqo__npw, fdj__bchhn in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            dfwqo__npw], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if hxti__osbdr:
            qfhl__qslmz = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                qfhl__qslmz, gpw__qcv, hxti__osbdr)
    parallel = False
    if array_dists is not None:
        parallel = True
        for rcr__ydy in json_node.out_vars:
            if array_dists[rcr__ydy.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                rcr__ydy.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    yfzyw__zalz = len(json_node.out_vars)
    casx__tbmqx = ', '.join('arr' + str(dfwqo__npw) for dfwqo__npw in range
        (yfzyw__zalz))
    xoukv__nbf = 'def json_impl(fname):\n'
    xoukv__nbf += '    ({},) = _json_reader_py(fname)\n'.format(casx__tbmqx)
    zpvbe__mhtuv = {}
    exec(xoukv__nbf, {}, zpvbe__mhtuv)
    ojr__ipkcv = zpvbe__mhtuv['json_impl']
    jlk__rynvu = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    bcbl__koqaa = compile_to_numba_ir(ojr__ipkcv, {'_json_reader_py':
        jlk__rynvu}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(bcbl__koqaa, [json_node.file_name])
    ccxg__datgj = bcbl__koqaa.body[:-3]
    for dfwqo__npw in range(len(json_node.out_vars)):
        ccxg__datgj[-len(json_node.out_vars) + dfwqo__npw
            ].target = json_node.out_vars[dfwqo__npw]
    return ccxg__datgj


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
    ailtf__qcrkb = [sanitize_varname(fdj__bchhn) for fdj__bchhn in col_names]
    axhh__ahivm = ', '.join(str(dfwqo__npw) for dfwqo__npw, cpay__uhppe in
        enumerate(col_typs) if cpay__uhppe.dtype == types.NPDatetime('ns'))
    tquzz__zan = ', '.join(["{}='{}'".format(muowb__uac, bodo.ir.csv_ext.
        _get_dtype_str(cpay__uhppe)) for muowb__uac, cpay__uhppe in zip(
        ailtf__qcrkb, col_typs)])
    njt__uza = ', '.join(["'{}':{}".format(rfzbf__occi, bodo.ir.csv_ext.
        _get_pd_dtype_str(cpay__uhppe)) for rfzbf__occi, cpay__uhppe in zip
        (col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    xoukv__nbf = 'def json_reader_py(fname):\n'
    xoukv__nbf += '  df_typeref_2 = df_typeref\n'
    xoukv__nbf += '  check_java_installation(fname)\n'
    xoukv__nbf += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    xoukv__nbf += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    xoukv__nbf += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    xoukv__nbf += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    xoukv__nbf += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    xoukv__nbf += "      raise FileNotFoundError('File does not exist')\n"
    xoukv__nbf += f'  with objmode({tquzz__zan}):\n'
    xoukv__nbf += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    xoukv__nbf += f'       convert_dates = {convert_dates}, \n'
    xoukv__nbf += f'       precise_float={precise_float}, \n'
    xoukv__nbf += f'       lines={lines}, \n'
    xoukv__nbf += '       dtype={{{}}},\n'.format(njt__uza)
    xoukv__nbf += '       )\n'
    xoukv__nbf += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for muowb__uac, rfzbf__occi in zip(ailtf__qcrkb, col_names):
        xoukv__nbf += '    if len(df) > 0:\n'
        xoukv__nbf += "        {} = df['{}'].values\n".format(muowb__uac,
            rfzbf__occi)
        xoukv__nbf += '    else:\n'
        xoukv__nbf += '        {} = np.array([])\n'.format(muowb__uac)
    xoukv__nbf += '  return ({},)\n'.format(', '.join(kuuko__eafna for
        kuuko__eafna in ailtf__qcrkb))
    nide__usm = globals()
    nide__usm.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    zpvbe__mhtuv = {}
    exec(xoukv__nbf, nide__usm, zpvbe__mhtuv)
    jlk__rynvu = zpvbe__mhtuv['json_reader_py']
    szx__froml = numba.njit(jlk__rynvu)
    compiled_funcs.append(szx__froml)
    return szx__froml
