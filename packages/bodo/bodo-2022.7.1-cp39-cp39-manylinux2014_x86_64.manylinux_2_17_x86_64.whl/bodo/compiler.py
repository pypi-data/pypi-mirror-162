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
        kynr__srph = 'bodo' if distributed else 'bodo_seq'
        kynr__srph = (kynr__srph + '_inline' if inline_calls_pass else
            kynr__srph)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, kynr__srph
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
    for rfor__srtom, (khiv__weto, zhqpy__kfkwc) in enumerate(pm.passes):
        if khiv__weto == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(rfor__srtom, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for rfor__srtom, (khiv__weto, zhqpy__kfkwc) in enumerate(pm.passes):
        if khiv__weto == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[rfor__srtom] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for rfor__srtom, (khiv__weto, zhqpy__kfkwc) in enumerate(pm.passes):
        if khiv__weto == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(rfor__srtom)
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
    tsd__wcrh = guard(get_definition, func_ir, rhs.func)
    if isinstance(tsd__wcrh, (ir.Global, ir.FreeVar, ir.Const)):
        xuk__dhipk = tsd__wcrh.value
    else:
        dte__btw = guard(find_callname, func_ir, rhs)
        if not (dte__btw and isinstance(dte__btw[0], str) and isinstance(
            dte__btw[1], str)):
            return
        func_name, func_mod = dte__btw
        try:
            import importlib
            olm__etg = importlib.import_module(func_mod)
            xuk__dhipk = getattr(olm__etg, func_name)
        except:
            return
    if isinstance(xuk__dhipk, CPUDispatcher) and issubclass(xuk__dhipk.
        _compiler.pipeline_class, BodoCompiler
        ) and xuk__dhipk._compiler.pipeline_class != BodoCompilerUDF:
        xuk__dhipk._compiler.pipeline_class = BodoCompilerUDF
        xuk__dhipk.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for xnbe__unx in block.body:
                if is_call_assign(xnbe__unx):
                    _convert_bodo_dispatcher_to_udf(xnbe__unx.value, state.
                        func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        pwoe__ddha = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        pwoe__ddha.run()
        return True


def _update_definitions(func_ir, node_list):
    qwasp__jyhd = ir.Loc('', 0)
    mqvk__nyf = ir.Block(ir.Scope(None, qwasp__jyhd), qwasp__jyhd)
    mqvk__nyf.body = node_list
    build_definitions({(0): mqvk__nyf}, func_ir._definitions)


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
        kxu__tghp = 'overload_series_' + rhs.attr
        gqyf__zpog = getattr(bodo.hiframes.series_impl, kxu__tghp)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        kxu__tghp = 'overload_dataframe_' + rhs.attr
        gqyf__zpog = getattr(bodo.hiframes.dataframe_impl, kxu__tghp)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    hgp__dwz = gqyf__zpog(rhs_type)
    zwmbw__swax = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc
        )
    fbez__mbmj = compile_func_single_block(hgp__dwz, (rhs.value,), stmt.
        target, zwmbw__swax)
    _update_definitions(func_ir, fbez__mbmj)
    new_body += fbez__mbmj
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
        erk__hzmj = tuple(typemap[ewbav__iffxd.name] for ewbav__iffxd in
            rhs.args)
        yaho__ooj = {kynr__srph: typemap[ewbav__iffxd.name] for kynr__srph,
            ewbav__iffxd in dict(rhs.kws).items()}
        hgp__dwz = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*erk__hzmj, **yaho__ooj)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        erk__hzmj = tuple(typemap[ewbav__iffxd.name] for ewbav__iffxd in
            rhs.args)
        yaho__ooj = {kynr__srph: typemap[ewbav__iffxd.name] for kynr__srph,
            ewbav__iffxd in dict(rhs.kws).items()}
        hgp__dwz = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*erk__hzmj, **yaho__ooj)
    else:
        return False
    hvxeo__fbc = replace_func(pass_info, hgp__dwz, rhs.args, pysig=numba.
        core.utils.pysignature(hgp__dwz), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    zor__wqvc, zhqpy__kfkwc = inline_closure_call(func_ir, hvxeo__fbc.glbls,
        block, len(new_body), hvxeo__fbc.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=hvxeo__fbc.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for iuj__spak in zor__wqvc.values():
        iuj__spak.loc = rhs.loc
        update_locs(iuj__spak.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    mdn__eyptw = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = mdn__eyptw(func_ir, typemap)
    sqaw__nnd = func_ir.blocks
    work_list = list((crcea__pfx, sqaw__nnd[crcea__pfx]) for crcea__pfx in
        reversed(sqaw__nnd.keys()))
    while work_list:
        fmb__efvlv, block = work_list.pop()
        new_body = []
        wwolb__xyzh = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                dte__btw = guard(find_callname, func_ir, rhs, typemap)
                if dte__btw is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = dte__btw
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    wwolb__xyzh = True
                    break
            new_body.append(stmt)
        if not wwolb__xyzh:
            sqaw__nnd[fmb__efvlv].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        fgw__mexqz = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = fgw__mexqz.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        ffya__ddkjw = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        buhch__tubr = ffya__ddkjw.run()
        vvmj__xruo = buhch__tubr
        if vvmj__xruo:
            vvmj__xruo = ffya__ddkjw.run()
        if vvmj__xruo:
            ffya__ddkjw.run()
        return buhch__tubr


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        bkrgu__rik = 0
        mrhku__nig = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            bkrgu__rik = int(os.environ[mrhku__nig])
        except:
            pass
        if bkrgu__rik > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(bkrgu__rik,
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
        zwmbw__swax = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, zwmbw__swax)
        for block in state.func_ir.blocks.values():
            new_body = []
            for xnbe__unx in block.body:
                if type(xnbe__unx) in distributed_run_extensions:
                    kguk__qhwwc = distributed_run_extensions[type(xnbe__unx)]
                    oijj__vkkt = kguk__qhwwc(xnbe__unx, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += oijj__vkkt
                elif is_call_assign(xnbe__unx):
                    rhs = xnbe__unx.value
                    dte__btw = guard(find_callname, state.func_ir, rhs)
                    if dte__btw == ('gatherv', 'bodo') or dte__btw == (
                        'allgatherv', 'bodo'):
                        rlzpj__drtg = state.typemap[xnbe__unx.target.name]
                        mzg__kuo = state.typemap[rhs.args[0].name]
                        if isinstance(mzg__kuo, types.Array) and isinstance(
                            rlzpj__drtg, types.Array):
                            huzs__ensuc = mzg__kuo.copy(readonly=False)
                            utkqu__wpzwe = rlzpj__drtg.copy(readonly=False)
                            if huzs__ensuc == utkqu__wpzwe:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), xnbe__unx.target, zwmbw__swax)
                                continue
                        if (rlzpj__drtg != mzg__kuo and 
                            to_str_arr_if_dict_array(rlzpj__drtg) ==
                            to_str_arr_if_dict_array(mzg__kuo)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), xnbe__unx.target,
                                zwmbw__swax, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            xnbe__unx.value = rhs.args[0]
                    new_body.append(xnbe__unx)
                else:
                    new_body.append(xnbe__unx)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        mor__hwf = TableColumnDelPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes)
        return mor__hwf.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    wpiu__mqgn = set()
    while work_list:
        fmb__efvlv, block = work_list.pop()
        wpiu__mqgn.add(fmb__efvlv)
        for i, pbjhy__uoyl in enumerate(block.body):
            if isinstance(pbjhy__uoyl, ir.Assign):
                uzxg__jbgge = pbjhy__uoyl.value
                if isinstance(uzxg__jbgge, ir.Expr
                    ) and uzxg__jbgge.op == 'call':
                    tsd__wcrh = guard(get_definition, func_ir, uzxg__jbgge.func
                        )
                    if isinstance(tsd__wcrh, (ir.Global, ir.FreeVar)
                        ) and isinstance(tsd__wcrh.value, CPUDispatcher
                        ) and issubclass(tsd__wcrh.value._compiler.
                        pipeline_class, BodoCompiler):
                        ckc__dnys = tsd__wcrh.value.py_func
                        arg_types = None
                        if typingctx:
                            vnpx__nevhz = dict(uzxg__jbgge.kws)
                            eoo__ybnq = tuple(typemap[ewbav__iffxd.name] for
                                ewbav__iffxd in uzxg__jbgge.args)
                            hiljd__wkrpe = {addos__azd: typemap[
                                ewbav__iffxd.name] for addos__azd,
                                ewbav__iffxd in vnpx__nevhz.items()}
                            zhqpy__kfkwc, arg_types = (tsd__wcrh.value.
                                fold_argument_types(eoo__ybnq, hiljd__wkrpe))
                        zhqpy__kfkwc, ygjhe__hmclh = inline_closure_call(
                            func_ir, ckc__dnys.__globals__, block, i,
                            ckc__dnys, typingctx=typingctx, targetctx=
                            targetctx, arg_typs=arg_types, typemap=typemap,
                            calltypes=calltypes, work_list=work_list)
                        _locals.update((ygjhe__hmclh[addos__azd].name,
                            ewbav__iffxd) for addos__azd, ewbav__iffxd in
                            tsd__wcrh.value.locals.items() if addos__azd in
                            ygjhe__hmclh)
                        break
    return wpiu__mqgn


def udf_jit(signature_or_function=None, **options):
    xgm__qpy = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=xgm__qpy,
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
    for rfor__srtom, (khiv__weto, zhqpy__kfkwc) in enumerate(pm.passes):
        if khiv__weto == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:rfor__srtom + 1]
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
    aaws__nkln = None
    ave__bxy = None
    _locals = {}
    iclqf__feluh = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(iclqf__feluh, arg_types,
        kw_types)
    nduqy__jch = numba.core.compiler.Flags()
    swy__hzdec = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    had__idk = {'nopython': True, 'boundscheck': False, 'parallel': swy__hzdec}
    numba.core.registry.cpu_target.options.parse_as_flags(nduqy__jch, had__idk)
    njlye__fgt = TyperCompiler(typingctx, targetctx, aaws__nkln, args,
        ave__bxy, nduqy__jch, _locals)
    return njlye__fgt.compile_extra(func)
