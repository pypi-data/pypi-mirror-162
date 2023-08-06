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
        gtl__jdxk = 'bodo' if distributed else 'bodo_seq'
        gtl__jdxk = gtl__jdxk + '_inline' if inline_calls_pass else gtl__jdxk
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, gtl__jdxk)
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
    for lkiaj__iii, (qztxl__jmxz, ozm__rnqf) in enumerate(pm.passes):
        if qztxl__jmxz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(lkiaj__iii, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for lkiaj__iii, (qztxl__jmxz, ozm__rnqf) in enumerate(pm.passes):
        if qztxl__jmxz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[lkiaj__iii] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for lkiaj__iii, (qztxl__jmxz, ozm__rnqf) in enumerate(pm.passes):
        if qztxl__jmxz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(lkiaj__iii)
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
    mnsa__wpr = guard(get_definition, func_ir, rhs.func)
    if isinstance(mnsa__wpr, (ir.Global, ir.FreeVar, ir.Const)):
        rfyn__ikjaz = mnsa__wpr.value
    else:
        zalld__bhrgc = guard(find_callname, func_ir, rhs)
        if not (zalld__bhrgc and isinstance(zalld__bhrgc[0], str) and
            isinstance(zalld__bhrgc[1], str)):
            return
        func_name, func_mod = zalld__bhrgc
        try:
            import importlib
            ilfq__pcd = importlib.import_module(func_mod)
            rfyn__ikjaz = getattr(ilfq__pcd, func_name)
        except:
            return
    if isinstance(rfyn__ikjaz, CPUDispatcher) and issubclass(rfyn__ikjaz.
        _compiler.pipeline_class, BodoCompiler
        ) and rfyn__ikjaz._compiler.pipeline_class != BodoCompilerUDF:
        rfyn__ikjaz._compiler.pipeline_class = BodoCompilerUDF
        rfyn__ikjaz.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for fmhqd__zgg in block.body:
                if is_call_assign(fmhqd__zgg):
                    _convert_bodo_dispatcher_to_udf(fmhqd__zgg.value, state
                        .func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        gcna__fuqzo = UntypedPass(state.func_ir, state.typingctx, state.
            args, state.locals, state.metadata, state.flags)
        gcna__fuqzo.run()
        return True


def _update_definitions(func_ir, node_list):
    ljvpp__aai = ir.Loc('', 0)
    yeh__rrie = ir.Block(ir.Scope(None, ljvpp__aai), ljvpp__aai)
    yeh__rrie.body = node_list
    build_definitions({(0): yeh__rrie}, func_ir._definitions)


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
        ello__dnr = 'overload_series_' + rhs.attr
        ojbo__oaw = getattr(bodo.hiframes.series_impl, ello__dnr)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        ello__dnr = 'overload_dataframe_' + rhs.attr
        ojbo__oaw = getattr(bodo.hiframes.dataframe_impl, ello__dnr)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    wefb__bgyz = ojbo__oaw(rhs_type)
    zlb__wlr = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    bowkl__xoc = compile_func_single_block(wefb__bgyz, (rhs.value,), stmt.
        target, zlb__wlr)
    _update_definitions(func_ir, bowkl__xoc)
    new_body += bowkl__xoc
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
        piub__byj = tuple(typemap[dikx__nyod.name] for dikx__nyod in rhs.args)
        dcnw__eqo = {gtl__jdxk: typemap[dikx__nyod.name] for gtl__jdxk,
            dikx__nyod in dict(rhs.kws).items()}
        wefb__bgyz = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*piub__byj, **dcnw__eqo)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        piub__byj = tuple(typemap[dikx__nyod.name] for dikx__nyod in rhs.args)
        dcnw__eqo = {gtl__jdxk: typemap[dikx__nyod.name] for gtl__jdxk,
            dikx__nyod in dict(rhs.kws).items()}
        wefb__bgyz = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*piub__byj, **dcnw__eqo)
    else:
        return False
    mut__tirs = replace_func(pass_info, wefb__bgyz, rhs.args, pysig=numba.
        core.utils.pysignature(wefb__bgyz), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    yhy__xlhno, ozm__rnqf = inline_closure_call(func_ir, mut__tirs.glbls,
        block, len(new_body), mut__tirs.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=mut__tirs.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for luo__vskew in yhy__xlhno.values():
        luo__vskew.loc = rhs.loc
        update_locs(luo__vskew.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    qtaao__tghm = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = qtaao__tghm(func_ir, typemap)
    ovll__cepk = func_ir.blocks
    work_list = list((emzo__icmt, ovll__cepk[emzo__icmt]) for emzo__icmt in
        reversed(ovll__cepk.keys()))
    while work_list:
        rol__kwiv, block = work_list.pop()
        new_body = []
        vzqb__thao = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                zalld__bhrgc = guard(find_callname, func_ir, rhs, typemap)
                if zalld__bhrgc is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = zalld__bhrgc
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    vzqb__thao = True
                    break
            new_body.append(stmt)
        if not vzqb__thao:
            ovll__cepk[rol__kwiv].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        hys__tmis = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = hys__tmis.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        znxqp__rura = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        ryg__byvr = znxqp__rura.run()
        wvi__dyhsp = ryg__byvr
        if wvi__dyhsp:
            wvi__dyhsp = znxqp__rura.run()
        if wvi__dyhsp:
            znxqp__rura.run()
        return ryg__byvr


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        mxu__zve = 0
        hcza__tqi = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            mxu__zve = int(os.environ[hcza__tqi])
        except:
            pass
        if mxu__zve > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(mxu__zve, state.
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
        zlb__wlr = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, zlb__wlr)
        for block in state.func_ir.blocks.values():
            new_body = []
            for fmhqd__zgg in block.body:
                if type(fmhqd__zgg) in distributed_run_extensions:
                    sas__bhd = distributed_run_extensions[type(fmhqd__zgg)]
                    spjp__ynwz = sas__bhd(fmhqd__zgg, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += spjp__ynwz
                elif is_call_assign(fmhqd__zgg):
                    rhs = fmhqd__zgg.value
                    zalld__bhrgc = guard(find_callname, state.func_ir, rhs)
                    if zalld__bhrgc == ('gatherv', 'bodo') or zalld__bhrgc == (
                        'allgatherv', 'bodo'):
                        ovlj__afrm = state.typemap[fmhqd__zgg.target.name]
                        tqsd__atf = state.typemap[rhs.args[0].name]
                        if isinstance(tqsd__atf, types.Array) and isinstance(
                            ovlj__afrm, types.Array):
                            uwoo__xmt = tqsd__atf.copy(readonly=False)
                            pbs__gxbjn = ovlj__afrm.copy(readonly=False)
                            if uwoo__xmt == pbs__gxbjn:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), fmhqd__zgg.target, zlb__wlr)
                                continue
                        if (ovlj__afrm != tqsd__atf and 
                            to_str_arr_if_dict_array(ovlj__afrm) ==
                            to_str_arr_if_dict_array(tqsd__atf)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), fmhqd__zgg.target, zlb__wlr,
                                extra_globals={'decode_if_dict_array':
                                decode_if_dict_array})
                            continue
                        else:
                            fmhqd__zgg.value = rhs.args[0]
                    new_body.append(fmhqd__zgg)
                else:
                    new_body.append(fmhqd__zgg)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        zaty__ujlka = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return zaty__ujlka.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    xys__eczn = set()
    while work_list:
        rol__kwiv, block = work_list.pop()
        xys__eczn.add(rol__kwiv)
        for i, imnib__uchw in enumerate(block.body):
            if isinstance(imnib__uchw, ir.Assign):
                uunr__nqu = imnib__uchw.value
                if isinstance(uunr__nqu, ir.Expr) and uunr__nqu.op == 'call':
                    mnsa__wpr = guard(get_definition, func_ir, uunr__nqu.func)
                    if isinstance(mnsa__wpr, (ir.Global, ir.FreeVar)
                        ) and isinstance(mnsa__wpr.value, CPUDispatcher
                        ) and issubclass(mnsa__wpr.value._compiler.
                        pipeline_class, BodoCompiler):
                        owfr__zsxq = mnsa__wpr.value.py_func
                        arg_types = None
                        if typingctx:
                            ovuk__gteh = dict(uunr__nqu.kws)
                            iuh__ltavx = tuple(typemap[dikx__nyod.name] for
                                dikx__nyod in uunr__nqu.args)
                            dik__midyq = {ieq__iel: typemap[dikx__nyod.name
                                ] for ieq__iel, dikx__nyod in ovuk__gteh.
                                items()}
                            ozm__rnqf, arg_types = (mnsa__wpr.value.
                                fold_argument_types(iuh__ltavx, dik__midyq))
                        ozm__rnqf, pfli__rhb = inline_closure_call(func_ir,
                            owfr__zsxq.__globals__, block, i, owfr__zsxq,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((pfli__rhb[ieq__iel].name,
                            dikx__nyod) for ieq__iel, dikx__nyod in
                            mnsa__wpr.value.locals.items() if ieq__iel in
                            pfli__rhb)
                        break
    return xys__eczn


def udf_jit(signature_or_function=None, **options):
    yzdvp__kwnxp = {'comprehension': True, 'setitem': False,
        'inplace_binop': False, 'reduction': True, 'numpy': True, 'stencil':
        False, 'fusion': True}
    return numba.njit(signature_or_function, parallel=yzdvp__kwnxp,
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
    for lkiaj__iii, (qztxl__jmxz, ozm__rnqf) in enumerate(pm.passes):
        if qztxl__jmxz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:lkiaj__iii + 1]
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
    bnohh__fiyap = None
    fnnlb__tvp = None
    _locals = {}
    dta__lno = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(dta__lno, arg_types,
        kw_types)
    gmpb__spyw = numba.core.compiler.Flags()
    ijlq__rmsh = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    els__cshx = {'nopython': True, 'boundscheck': False, 'parallel': ijlq__rmsh
        }
    numba.core.registry.cpu_target.options.parse_as_flags(gmpb__spyw, els__cshx
        )
    nii__icqec = TyperCompiler(typingctx, targetctx, bnohh__fiyap, args,
        fnnlb__tvp, gmpb__spyw, _locals)
    return nii__icqec.compile_extra(func)
