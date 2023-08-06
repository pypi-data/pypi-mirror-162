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
        wxrcf__csa = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        rhpt__ktkio = cgutils.get_or_insert_function(builder.module,
            wxrcf__csa, name='json_file_chunk_reader')
        lnaw__mygf = builder.call(rhpt__ktkio, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        dwvvs__conto = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        ysj__nbdts = context.get_python_api(builder)
        dwvvs__conto.meminfo = ysj__nbdts.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), lnaw__mygf)
        dwvvs__conto.pyobj = lnaw__mygf
        ysj__nbdts.decref(lnaw__mygf)
        return dwvvs__conto._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.bool_,
        types.int64, types.voidptr, types.voidptr, storage_options_dict_type
        ), codegen


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    nylh__ntydg = []
    xauhz__rqrjb = []
    zgpjt__ybe = []
    for bfwq__gsh, xjlcx__ynaiw in enumerate(json_node.out_vars):
        if xjlcx__ynaiw.name in lives:
            nylh__ntydg.append(json_node.df_colnames[bfwq__gsh])
            xauhz__rqrjb.append(json_node.out_vars[bfwq__gsh])
            zgpjt__ybe.append(json_node.out_types[bfwq__gsh])
    json_node.df_colnames = nylh__ntydg
    json_node.out_vars = xauhz__rqrjb
    json_node.out_types = zgpjt__ybe
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        vfbdh__uhc = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        sjz__jozqu = json_node.loc.strformat()
        mfzx__sxxlp = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', vfbdh__uhc,
            sjz__jozqu, mfzx__sxxlp)
        wlhv__fgf = [aoq__jsu for bfwq__gsh, aoq__jsu in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            bfwq__gsh], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if wlhv__fgf:
            xvob__geky = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', xvob__geky,
                sjz__jozqu, wlhv__fgf)
    parallel = False
    if array_dists is not None:
        parallel = True
        for ihlbq__kqnmt in json_node.out_vars:
            if array_dists[ihlbq__kqnmt.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                ihlbq__kqnmt.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    fnijd__phgxx = len(json_node.out_vars)
    wtfu__ggc = ', '.join('arr' + str(bfwq__gsh) for bfwq__gsh in range(
        fnijd__phgxx))
    bmn__oba = 'def json_impl(fname):\n'
    bmn__oba += '    ({},) = _json_reader_py(fname)\n'.format(wtfu__ggc)
    fagpt__pnh = {}
    exec(bmn__oba, {}, fagpt__pnh)
    pveg__zcsp = fagpt__pnh['json_impl']
    uhyt__zbd = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    nns__rszqo = compile_to_numba_ir(pveg__zcsp, {'_json_reader_py':
        uhyt__zbd}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(nns__rszqo, [json_node.file_name])
    gxmx__xee = nns__rszqo.body[:-3]
    for bfwq__gsh in range(len(json_node.out_vars)):
        gxmx__xee[-len(json_node.out_vars) + bfwq__gsh
            ].target = json_node.out_vars[bfwq__gsh]
    return gxmx__xee


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
    zkdz__njstl = [sanitize_varname(aoq__jsu) for aoq__jsu in col_names]
    dtw__ntxzi = ', '.join(str(bfwq__gsh) for bfwq__gsh, sbz__usp in
        enumerate(col_typs) if sbz__usp.dtype == types.NPDatetime('ns'))
    iynd__cdfm = ', '.join(["{}='{}'".format(bskc__xaeuq, bodo.ir.csv_ext.
        _get_dtype_str(sbz__usp)) for bskc__xaeuq, sbz__usp in zip(
        zkdz__njstl, col_typs)])
    andb__nfof = ', '.join(["'{}':{}".format(sie__ioj, bodo.ir.csv_ext.
        _get_pd_dtype_str(sbz__usp)) for sie__ioj, sbz__usp in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    bmn__oba = 'def json_reader_py(fname):\n'
    bmn__oba += '  df_typeref_2 = df_typeref\n'
    bmn__oba += '  check_java_installation(fname)\n'
    bmn__oba += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    bmn__oba += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    bmn__oba += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    bmn__oba += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    bmn__oba += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    bmn__oba += "      raise FileNotFoundError('File does not exist')\n"
    bmn__oba += f'  with objmode({iynd__cdfm}):\n'
    bmn__oba += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    bmn__oba += f'       convert_dates = {convert_dates}, \n'
    bmn__oba += f'       precise_float={precise_float}, \n'
    bmn__oba += f'       lines={lines}, \n'
    bmn__oba += '       dtype={{{}}},\n'.format(andb__nfof)
    bmn__oba += '       )\n'
    bmn__oba += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for bskc__xaeuq, sie__ioj in zip(zkdz__njstl, col_names):
        bmn__oba += '    if len(df) > 0:\n'
        bmn__oba += "        {} = df['{}'].values\n".format(bskc__xaeuq,
            sie__ioj)
        bmn__oba += '    else:\n'
        bmn__oba += '        {} = np.array([])\n'.format(bskc__xaeuq)
    bmn__oba += '  return ({},)\n'.format(', '.join(gqw__mtut for gqw__mtut in
        zkdz__njstl))
    aas__bra = globals()
    aas__bra.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    fagpt__pnh = {}
    exec(bmn__oba, aas__bra, fagpt__pnh)
    uhyt__zbd = fagpt__pnh['json_reader_py']
    bpmh__rrlfz = numba.njit(uhyt__zbd)
    compiled_funcs.append(bpmh__rrlfz)
    return bpmh__rrlfz
