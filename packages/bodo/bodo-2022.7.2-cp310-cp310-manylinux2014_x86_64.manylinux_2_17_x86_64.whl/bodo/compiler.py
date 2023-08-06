"""
Defines Bodo's compiler pipeline.
"""
import os
import warnings
from collections import namedtuple
import numba
from numba.core import ir, ir_utils, types
from numba.core.compiler import DefaultPassBuilder
from numba.core.compiler_machinery import AnalysisPass, FunctionPass, register_pass
from numba.core.inline_closurecall import inline_closure_call
from numba.core.ir_utils import build_definitions, find_callname, get_definition, guard
from numba.core.registry import CPUDispatcher
from numba.core.typed_passes import DumpParforDiagnostics, InlineOverloads, IRLegalization, NopythonTypeInference, ParforPass, PreParforPass
from numba.core.untyped_passes import MakeFunctionToJitFunction, ReconstructSSA, WithLifting
import bodo
import bodo.hiframes.dataframe_indexing
import bodo.hiframes.datetime_datetime_ext
import bodo.hiframes.datetime_timedelta_ext
import bodo.io
import bodo.libs
import bodo.libs.array_kernels
import bodo.libs.int_arr_ext
import bodo.libs.re_ext
import bodo.libs.spark_extra
import bodo.transforms
import bodo.transforms.series_pass
import bodo.transforms.untyped_pass
import bodo.utils
import bodo.utils.table_utils
import bodo.utils.typing
from bodo.transforms.series_pass import SeriesPass
from bodo.transforms.table_column_del_pass import TableColumnDelPass
from bodo.transforms.typing_pass import BodoTypeInference
from bodo.transforms.untyped_pass import UntypedPass
from bodo.utils.utils import is_assign, is_call_assign, is_expr
numba.core.config.DISABLE_PERFORMANCE_WARNINGS = 1
from numba.core.errors import NumbaExperimentalFeatureWarning, NumbaPendingDeprecationWarning
warnings.simplefilter('ignore', category=NumbaExperimentalFeatureWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
inline_all_calls = False


class BodoCompiler(numba.core.compiler.CompilerBase):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=True,
            inline_calls_pass=inline_all_calls)

    def _create_bodo_pipeline(self, distributed=True, inline_calls_pass=
        False, udf_pipeline=False):
        ilsa__gksi = 'bodo' if distributed else 'bodo_seq'
        ilsa__gksi = (ilsa__gksi + '_inline' if inline_calls_pass else
            ilsa__gksi)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, ilsa__gksi
            )
        if inline_calls_pass:
            pm.add_pass_after(InlinePass, WithLifting)
        if udf_pipeline:
            pm.add_pass_after(ConvertCallsUDFPass, WithLifting)
        add_pass_before(pm, BodoUntypedPass, ReconstructSSA)
        replace_pass(pm, BodoTypeInference, NopythonTypeInference)
        remove_pass(pm, MakeFunctionToJitFunction)
        add_pass_before(pm, BodoSeriesPass, PreParforPass)
        if distributed:
            pm.add_pass_after(BodoDistributedPass, ParforPass)
        else:
            pm.add_pass_after(LowerParforSeq, ParforPass)
            pm.add_pass_after(LowerBodoIRExtSeq, LowerParforSeq)
        add_pass_before(pm, BodoTableColumnDelPass, IRLegalization)
        pm.add_pass_after(BodoDumpDistDiagnosticsPass, DumpParforDiagnostics)
        pm.finalize()
        return [pm]


def add_pass_before(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for ojs__spmf, (ifa__otr, jlo__bwi) in enumerate(pm.passes):
        if ifa__otr == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(ojs__spmf, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for ojs__spmf, (ifa__otr, jlo__bwi) in enumerate(pm.passes):
        if ifa__otr == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[ojs__spmf] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for ojs__spmf, (ifa__otr, jlo__bwi) in enumerate(pm.passes):
        if ifa__otr == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(ojs__spmf)
    pm._finalized = False


@register_pass(mutates_CFG=True, analysis_only=False)
class InlinePass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        inline_calls(state.func_ir, state.locals)
        state.func_ir.blocks = ir_utils.simplify_CFG(state.func_ir.blocks)
        return True


def _convert_bodo_dispatcher_to_udf(rhs, func_ir):
    wbt__wio = guard(get_definition, func_ir, rhs.func)
    if isinstance(wbt__wio, (ir.Global, ir.FreeVar, ir.Const)):
        bvcal__rqo = wbt__wio.value
    else:
        dsj__whcjb = guard(find_callname, func_ir, rhs)
        if not (dsj__whcjb and isinstance(dsj__whcjb[0], str) and
            isinstance(dsj__whcjb[1], str)):
            return
        func_name, func_mod = dsj__whcjb
        try:
            import importlib
            emxjd__izbhk = importlib.import_module(func_mod)
            bvcal__rqo = getattr(emxjd__izbhk, func_name)
        except:
            return
    if isinstance(bvcal__rqo, CPUDispatcher) and issubclass(bvcal__rqo.
        _compiler.pipeline_class, BodoCompiler
        ) and bvcal__rqo._compiler.pipeline_class != BodoCompilerUDF:
        bvcal__rqo._compiler.pipeline_class = BodoCompilerUDF
        bvcal__rqo.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for vzn__gzev in block.body:
                if is_call_assign(vzn__gzev):
                    _convert_bodo_dispatcher_to_udf(vzn__gzev.value, state.
                        func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        ylq__conu = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        ylq__conu.run()
        return True


def _update_definitions(func_ir, node_list):
    elwu__ayhpb = ir.Loc('', 0)
    mluoj__gvrne = ir.Block(ir.Scope(None, elwu__ayhpb), elwu__ayhpb)
    mluoj__gvrne.body = node_list
    build_definitions({(0): mluoj__gvrne}, func_ir._definitions)


_series_inline_attrs = {'values', 'shape', 'size', 'empty', 'name', 'index',
    'dtype'}
_series_no_inline_methods = {'to_list', 'tolist', 'rolling', 'to_csv',
    'count', 'fillna', 'to_dict', 'map', 'apply', 'pipe', 'combine',
    'bfill', 'ffill', 'pad', 'backfill', 'mask', 'where'}
_series_method_alias = {'isnull': 'isna', 'product': 'prod', 'kurtosis':
    'kurt', 'is_monotonic': 'is_monotonic_increasing', 'notnull': 'notna'}
_dataframe_no_inline_methods = {'apply', 'itertuples', 'pipe', 'to_parquet',
    'to_sql', 'to_csv', 'to_json', 'assign', 'to_string', 'query',
    'rolling', 'mask', 'where'}
TypingInfo = namedtuple('TypingInfo', ['typingctx', 'targetctx', 'typemap',
    'calltypes', 'curr_loc'])


def _inline_bodo_getattr(stmt, rhs, rhs_type, new_body, func_ir, typingctx,
    targetctx, typemap, calltypes):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import compile_func_single_block
    if isinstance(rhs_type, SeriesType) and rhs.attr in _series_inline_attrs:
        oprbv__zhxfn = 'overload_series_' + rhs.attr
        epwbp__ool = getattr(bodo.hiframes.series_impl, oprbv__zhxfn)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        oprbv__zhxfn = 'overload_dataframe_' + rhs.attr
        epwbp__ool = getattr(bodo.hiframes.dataframe_impl, oprbv__zhxfn)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    flvz__ndb = epwbp__ool(rhs_type)
    cbfvb__xxk = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    neg__ihpvs = compile_func_single_block(flvz__ndb, (rhs.value,), stmt.
        target, cbfvb__xxk)
    _update_definitions(func_ir, neg__ihpvs)
    new_body += neg__ihpvs
    return True


def _inline_bodo_call(rhs, i, func_mod, func_name, pass_info, new_body,
    block, typingctx, targetctx, calltypes, work_list):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import replace_func, update_locs
    func_ir = pass_info.func_ir
    typemap = pass_info.typemap
    if isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        SeriesType) and func_name not in _series_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        if (func_name in bodo.hiframes.series_impl.explicit_binop_funcs or 
            func_name.startswith('r') and func_name[1:] in bodo.hiframes.
            series_impl.explicit_binop_funcs):
            return False
        rhs.args.insert(0, func_mod)
        ywtda__gnzis = tuple(typemap[hfd__ufi.name] for hfd__ufi in rhs.args)
        wde__kysez = {ilsa__gksi: typemap[hfd__ufi.name] for ilsa__gksi,
            hfd__ufi in dict(rhs.kws).items()}
        flvz__ndb = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*ywtda__gnzis, **wde__kysez)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        ywtda__gnzis = tuple(typemap[hfd__ufi.name] for hfd__ufi in rhs.args)
        wde__kysez = {ilsa__gksi: typemap[hfd__ufi.name] for ilsa__gksi,
            hfd__ufi in dict(rhs.kws).items()}
        flvz__ndb = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*ywtda__gnzis, **wde__kysez)
    else:
        return False
    jgk__udsxb = replace_func(pass_info, flvz__ndb, rhs.args, pysig=numba.
        core.utils.pysignature(flvz__ndb), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    pmqsf__tpx, jlo__bwi = inline_closure_call(func_ir, jgk__udsxb.glbls,
        block, len(new_body), jgk__udsxb.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=jgk__udsxb.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for csm__lst in pmqsf__tpx.values():
        csm__lst.loc = rhs.loc
        update_locs(csm__lst.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    usu__odkt = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = usu__odkt(func_ir, typemap)
    spd__nczvm = func_ir.blocks
    work_list = list((gaj__cjxs, spd__nczvm[gaj__cjxs]) for gaj__cjxs in
        reversed(spd__nczvm.keys()))
    while work_list:
        vxman__hrnei, block = work_list.pop()
        new_body = []
        ckh__dzyp = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                dsj__whcjb = guard(find_callname, func_ir, rhs, typemap)
                if dsj__whcjb is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = dsj__whcjb
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    ckh__dzyp = True
                    break
            new_body.append(stmt)
        if not ckh__dzyp:
            spd__nczvm[vxman__hrnei].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        aja__juzfu = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = aja__juzfu.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        itecc__zvpx = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        ljhbd__cbh = itecc__zvpx.run()
        kzu__girps = ljhbd__cbh
        if kzu__girps:
            kzu__girps = itecc__zvpx.run()
        if kzu__girps:
            itecc__zvpx.run()
        return ljhbd__cbh


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        gbk__fet = 0
        elz__ctefg = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            gbk__fet = int(os.environ[elz__ctefg])
        except:
            pass
        if gbk__fet > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(gbk__fet, state.
                metadata)
        return True


class BodoCompilerSeq(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False,
            inline_calls_pass=inline_all_calls)


class BodoCompilerUDF(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False, udf_pipeline=True)


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerParforSeq(FunctionPass):
    _name = 'bodo_lower_parfor_seq_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        bodo.transforms.distributed_pass.lower_parfor_sequential(state.
            typingctx, state.func_ir, state.typemap, state.calltypes, state
            .metadata)
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerBodoIRExtSeq(FunctionPass):
    _name = 'bodo_lower_ir_ext_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        from bodo.transforms.distributed_pass import distributed_run_extensions
        from bodo.transforms.table_column_del_pass import remove_dead_table_columns
        from bodo.utils.transform import compile_func_single_block
        from bodo.utils.typing import decode_if_dict_array, to_str_arr_if_dict_array
        state.func_ir._definitions = build_definitions(state.func_ir.blocks)
        cbfvb__xxk = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, cbfvb__xxk)
        for block in state.func_ir.blocks.values():
            new_body = []
            for vzn__gzev in block.body:
                if type(vzn__gzev) in distributed_run_extensions:
                    zoqb__pyyj = distributed_run_extensions[type(vzn__gzev)]
                    uwamr__xwu = zoqb__pyyj(vzn__gzev, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += uwamr__xwu
                elif is_call_assign(vzn__gzev):
                    rhs = vzn__gzev.value
                    dsj__whcjb = guard(find_callname, state.func_ir, rhs)
                    if dsj__whcjb == ('gatherv', 'bodo') or dsj__whcjb == (
                        'allgatherv', 'bodo'):
                        ulw__jkcvo = state.typemap[vzn__gzev.target.name]
                        fdl__jaf = state.typemap[rhs.args[0].name]
                        if isinstance(fdl__jaf, types.Array) and isinstance(
                            ulw__jkcvo, types.Array):
                            diwp__zhdvh = fdl__jaf.copy(readonly=False)
                            ech__mlqh = ulw__jkcvo.copy(readonly=False)
                            if diwp__zhdvh == ech__mlqh:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), vzn__gzev.target, cbfvb__xxk)
                                continue
                        if ulw__jkcvo != fdl__jaf and to_str_arr_if_dict_array(
                            ulw__jkcvo) == to_str_arr_if_dict_array(fdl__jaf):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), vzn__gzev.target,
                                cbfvb__xxk, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            vzn__gzev.value = rhs.args[0]
                    new_body.append(vzn__gzev)
                else:
                    new_body.append(vzn__gzev)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        wmzzl__zjrw = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return wmzzl__zjrw.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    htj__gfh = set()
    while work_list:
        vxman__hrnei, block = work_list.pop()
        htj__gfh.add(vxman__hrnei)
        for i, olbfc__rogjx in enumerate(block.body):
            if isinstance(olbfc__rogjx, ir.Assign):
                fxo__vms = olbfc__rogjx.value
                if isinstance(fxo__vms, ir.Expr) and fxo__vms.op == 'call':
                    wbt__wio = guard(get_definition, func_ir, fxo__vms.func)
                    if isinstance(wbt__wio, (ir.Global, ir.FreeVar)
                        ) and isinstance(wbt__wio.value, CPUDispatcher
                        ) and issubclass(wbt__wio.value._compiler.
                        pipeline_class, BodoCompiler):
                        dolwi__jifs = wbt__wio.value.py_func
                        arg_types = None
                        if typingctx:
                            yrwcv__sqyp = dict(fxo__vms.kws)
                            mep__oyeps = tuple(typemap[hfd__ufi.name] for
                                hfd__ufi in fxo__vms.args)
                            ohmys__hpvq = {fjgm__lsbn: typemap[hfd__ufi.
                                name] for fjgm__lsbn, hfd__ufi in
                                yrwcv__sqyp.items()}
                            jlo__bwi, arg_types = (wbt__wio.value.
                                fold_argument_types(mep__oyeps, ohmys__hpvq))
                        jlo__bwi, pbuaf__dmol = inline_closure_call(func_ir,
                            dolwi__jifs.__globals__, block, i, dolwi__jifs,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((pbuaf__dmol[fjgm__lsbn].name,
                            hfd__ufi) for fjgm__lsbn, hfd__ufi in wbt__wio.
                            value.locals.items() if fjgm__lsbn in pbuaf__dmol)
                        break
    return htj__gfh


def udf_jit(signature_or_function=None, **options):
    ojrzo__mjd = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=ojrzo__mjd,
        pipeline_class=bodo.compiler.BodoCompilerUDF, **options)


def is_udf_call(func_type):
    return isinstance(func_type, numba.core.types.Dispatcher
        ) and func_type.dispatcher._compiler.pipeline_class == BodoCompilerUDF


def is_user_dispatcher(func_type):
    return isinstance(func_type, numba.core.types.functions.ObjModeDispatcher
        ) or isinstance(func_type, numba.core.types.Dispatcher) and issubclass(
        func_type.dispatcher._compiler.pipeline_class, BodoCompiler)


@register_pass(mutates_CFG=False, analysis_only=True)
class DummyCR(FunctionPass):
    _name = 'bodo_dummy_cr'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        state.cr = (state.func_ir, state.typemap, state.calltypes, state.
            return_type)
        return True


def remove_passes_after(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for ojs__spmf, (ifa__otr, jlo__bwi) in enumerate(pm.passes):
        if ifa__otr == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:ojs__spmf + 1]
    pm._finalized = False


class TyperCompiler(BodoCompiler):

    def define_pipelines(self):
        [pm] = self._create_bodo_pipeline()
        remove_passes_after(pm, InlineOverloads)
        pm.add_pass_after(DummyCR, InlineOverloads)
        pm.finalize()
        return [pm]


def get_func_type_info(func, arg_types, kw_types):
    typingctx = numba.core.registry.cpu_target.typing_context
    targetctx = numba.core.registry.cpu_target.target_context
    ffh__hvyz = None
    dyhib__mds = None
    _locals = {}
    ohw__jcjcc = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(ohw__jcjcc, arg_types,
        kw_types)
    bdzbp__tzc = numba.core.compiler.Flags()
    bifw__rfm = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    zrf__fcxoy = {'nopython': True, 'boundscheck': False, 'parallel': bifw__rfm
        }
    numba.core.registry.cpu_target.options.parse_as_flags(bdzbp__tzc,
        zrf__fcxoy)
    luyg__qdng = TyperCompiler(typingctx, targetctx, ffh__hvyz, args,
        dyhib__mds, bdzbp__tzc, _locals)
    return luyg__qdng.compile_extra(func)
