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
        zfl__haty = 'bodo' if distributed else 'bodo_seq'
        zfl__haty = zfl__haty + '_inline' if inline_calls_pass else zfl__haty
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, zfl__haty)
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
    for jojb__ktt, (bvmfh__sggco, lmoh__ndhvm) in enumerate(pm.passes):
        if bvmfh__sggco == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(jojb__ktt, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for jojb__ktt, (bvmfh__sggco, lmoh__ndhvm) in enumerate(pm.passes):
        if bvmfh__sggco == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[jojb__ktt] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for jojb__ktt, (bvmfh__sggco, lmoh__ndhvm) in enumerate(pm.passes):
        if bvmfh__sggco == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(jojb__ktt)
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
    xsidw__oliit = guard(get_definition, func_ir, rhs.func)
    if isinstance(xsidw__oliit, (ir.Global, ir.FreeVar, ir.Const)):
        sbi__gqb = xsidw__oliit.value
    else:
        bmv__jhxfg = guard(find_callname, func_ir, rhs)
        if not (bmv__jhxfg and isinstance(bmv__jhxfg[0], str) and
            isinstance(bmv__jhxfg[1], str)):
            return
        func_name, func_mod = bmv__jhxfg
        try:
            import importlib
            svvff__sbk = importlib.import_module(func_mod)
            sbi__gqb = getattr(svvff__sbk, func_name)
        except:
            return
    if isinstance(sbi__gqb, CPUDispatcher) and issubclass(sbi__gqb.
        _compiler.pipeline_class, BodoCompiler
        ) and sbi__gqb._compiler.pipeline_class != BodoCompilerUDF:
        sbi__gqb._compiler.pipeline_class = BodoCompilerUDF
        sbi__gqb.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for besdq__fuuq in block.body:
                if is_call_assign(besdq__fuuq):
                    _convert_bodo_dispatcher_to_udf(besdq__fuuq.value,
                        state.func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        btn__vwz = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        btn__vwz.run()
        return True


def _update_definitions(func_ir, node_list):
    rbit__cohh = ir.Loc('', 0)
    zrsf__mtd = ir.Block(ir.Scope(None, rbit__cohh), rbit__cohh)
    zrsf__mtd.body = node_list
    build_definitions({(0): zrsf__mtd}, func_ir._definitions)


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
        qgh__ctnr = 'overload_series_' + rhs.attr
        bhivy__srzzn = getattr(bodo.hiframes.series_impl, qgh__ctnr)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        qgh__ctnr = 'overload_dataframe_' + rhs.attr
        bhivy__srzzn = getattr(bodo.hiframes.dataframe_impl, qgh__ctnr)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    fgf__zsfo = bhivy__srzzn(rhs_type)
    mxcaa__zwqn = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc
        )
    gxlis__wbtv = compile_func_single_block(fgf__zsfo, (rhs.value,), stmt.
        target, mxcaa__zwqn)
    _update_definitions(func_ir, gxlis__wbtv)
    new_body += gxlis__wbtv
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
        gwzpj__xyqn = tuple(typemap[gpihf__hfm.name] for gpihf__hfm in rhs.args
            )
        pnyy__nsz = {zfl__haty: typemap[gpihf__hfm.name] for zfl__haty,
            gpihf__hfm in dict(rhs.kws).items()}
        fgf__zsfo = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*gwzpj__xyqn, **pnyy__nsz)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        gwzpj__xyqn = tuple(typemap[gpihf__hfm.name] for gpihf__hfm in rhs.args
            )
        pnyy__nsz = {zfl__haty: typemap[gpihf__hfm.name] for zfl__haty,
            gpihf__hfm in dict(rhs.kws).items()}
        fgf__zsfo = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*gwzpj__xyqn, **pnyy__nsz)
    else:
        return False
    fcahy__ltrqa = replace_func(pass_info, fgf__zsfo, rhs.args, pysig=numba
        .core.utils.pysignature(fgf__zsfo), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    ydemn__hmst, lmoh__ndhvm = inline_closure_call(func_ir, fcahy__ltrqa.
        glbls, block, len(new_body), fcahy__ltrqa.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=fcahy__ltrqa.arg_types, typemap=
        typemap, calltypes=calltypes, work_list=work_list)
    for ujnjc__vhsn in ydemn__hmst.values():
        ujnjc__vhsn.loc = rhs.loc
        update_locs(ujnjc__vhsn.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    evka__xsirb = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = evka__xsirb(func_ir, typemap)
    ieip__tzcn = func_ir.blocks
    work_list = list((uuox__nfo, ieip__tzcn[uuox__nfo]) for uuox__nfo in
        reversed(ieip__tzcn.keys()))
    while work_list:
        futak__vywql, block = work_list.pop()
        new_body = []
        ltj__kge = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                bmv__jhxfg = guard(find_callname, func_ir, rhs, typemap)
                if bmv__jhxfg is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = bmv__jhxfg
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    ltj__kge = True
                    break
            new_body.append(stmt)
        if not ltj__kge:
            ieip__tzcn[futak__vywql].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        bhr__upppl = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = bhr__upppl.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        kxrj__qswhm = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        chh__wub = kxrj__qswhm.run()
        txtia__pwheg = chh__wub
        if txtia__pwheg:
            txtia__pwheg = kxrj__qswhm.run()
        if txtia__pwheg:
            kxrj__qswhm.run()
        return chh__wub


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        xnw__nrrcm = 0
        npvpt__gseif = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            xnw__nrrcm = int(os.environ[npvpt__gseif])
        except:
            pass
        if xnw__nrrcm > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(xnw__nrrcm,
                state.metadata)
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
        mxcaa__zwqn = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, mxcaa__zwqn)
        for block in state.func_ir.blocks.values():
            new_body = []
            for besdq__fuuq in block.body:
                if type(besdq__fuuq) in distributed_run_extensions:
                    ijen__apo = distributed_run_extensions[type(besdq__fuuq)]
                    nmrt__kym = ijen__apo(besdq__fuuq, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += nmrt__kym
                elif is_call_assign(besdq__fuuq):
                    rhs = besdq__fuuq.value
                    bmv__jhxfg = guard(find_callname, state.func_ir, rhs)
                    if bmv__jhxfg == ('gatherv', 'bodo') or bmv__jhxfg == (
                        'allgatherv', 'bodo'):
                        wml__byclc = state.typemap[besdq__fuuq.target.name]
                        ivw__ecjp = state.typemap[rhs.args[0].name]
                        if isinstance(ivw__ecjp, types.Array) and isinstance(
                            wml__byclc, types.Array):
                            qua__ffpa = ivw__ecjp.copy(readonly=False)
                            fxunf__ofpo = wml__byclc.copy(readonly=False)
                            if qua__ffpa == fxunf__ofpo:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), besdq__fuuq.target, mxcaa__zwqn)
                                continue
                        if (wml__byclc != ivw__ecjp and 
                            to_str_arr_if_dict_array(wml__byclc) ==
                            to_str_arr_if_dict_array(ivw__ecjp)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), besdq__fuuq.target,
                                mxcaa__zwqn, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            besdq__fuuq.value = rhs.args[0]
                    new_body.append(besdq__fuuq)
                else:
                    new_body.append(besdq__fuuq)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        pcnv__mlw = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return pcnv__mlw.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    dpn__fvb = set()
    while work_list:
        futak__vywql, block = work_list.pop()
        dpn__fvb.add(futak__vywql)
        for i, febk__ujlmc in enumerate(block.body):
            if isinstance(febk__ujlmc, ir.Assign):
                iow__capfe = febk__ujlmc.value
                if isinstance(iow__capfe, ir.Expr) and iow__capfe.op == 'call':
                    xsidw__oliit = guard(get_definition, func_ir,
                        iow__capfe.func)
                    if isinstance(xsidw__oliit, (ir.Global, ir.FreeVar)
                        ) and isinstance(xsidw__oliit.value, CPUDispatcher
                        ) and issubclass(xsidw__oliit.value._compiler.
                        pipeline_class, BodoCompiler):
                        hpow__chit = xsidw__oliit.value.py_func
                        arg_types = None
                        if typingctx:
                            ovmxh__kyjpz = dict(iow__capfe.kws)
                            yibo__usdop = tuple(typemap[gpihf__hfm.name] for
                                gpihf__hfm in iow__capfe.args)
                            ebfq__idhw = {iksg__tryy: typemap[gpihf__hfm.
                                name] for iksg__tryy, gpihf__hfm in
                                ovmxh__kyjpz.items()}
                            lmoh__ndhvm, arg_types = (xsidw__oliit.value.
                                fold_argument_types(yibo__usdop, ebfq__idhw))
                        lmoh__ndhvm, hjc__qla = inline_closure_call(func_ir,
                            hpow__chit.__globals__, block, i, hpow__chit,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((hjc__qla[iksg__tryy].name,
                            gpihf__hfm) for iksg__tryy, gpihf__hfm in
                            xsidw__oliit.value.locals.items() if iksg__tryy in
                            hjc__qla)
                        break
    return dpn__fvb


def udf_jit(signature_or_function=None, **options):
    khxg__vuhch = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=khxg__vuhch,
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
    for jojb__ktt, (bvmfh__sggco, lmoh__ndhvm) in enumerate(pm.passes):
        if bvmfh__sggco == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:jojb__ktt + 1]
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
    gnl__kfofm = None
    wlcu__knjd = None
    _locals = {}
    hpsc__zmyp = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(hpsc__zmyp, arg_types,
        kw_types)
    bprv__iatck = numba.core.compiler.Flags()
    sau__zwz = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    ulpr__bsil = {'nopython': True, 'boundscheck': False, 'parallel': sau__zwz}
    numba.core.registry.cpu_target.options.parse_as_flags(bprv__iatck,
        ulpr__bsil)
    urwb__olsh = TyperCompiler(typingctx, targetctx, gnl__kfofm, args,
        wlcu__knjd, bprv__iatck, _locals)
    return urwb__olsh.compile_extra(func)
