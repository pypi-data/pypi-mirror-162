"""
Numba monkey patches to fix issues related to Bodo. Should be imported before any
other module in bodo package.
"""
import copy
import functools
import hashlib
import inspect
import itertools
import operator
import os
import re
import sys
import textwrap
import traceback
import types as pytypes
import warnings
from collections import OrderedDict
from collections.abc import Sequence
from contextlib import ExitStack
import numba
import numba.core.boxing
import numba.core.inline_closurecall
import numba.core.typing.listdecl
import numba.np.linalg
from numba.core import analysis, cgutils, errors, ir, ir_utils, types
from numba.core.compiler import Compiler
from numba.core.errors import ForceLiteralArg, LiteralTypingError, TypingError
from numba.core.ir_utils import GuardException, _create_function_from_code_obj, analysis, build_definitions, find_callname, get_definition, guard, has_no_side_effect, mk_unique_var, remove_dead_extensions, replace_vars_inner, require, visit_vars_extensions, visit_vars_inner
from numba.core.types import literal
from numba.core.types.functions import _bt_as_lines, _ResolutionFailures, _termcolor, _unlit_non_poison
from numba.core.typing.templates import AbstractTemplate, Signature, _EmptyImplementationEntry, _inline_info, _OverloadAttributeTemplate, infer_global, signature
from numba.core.typing.typeof import Purpose, typeof
from numba.experimental.jitclass import base as jitclass_base
from numba.experimental.jitclass import decorators as jitclass_decorators
from numba.extending import NativeValue, lower_builtin, typeof_impl
from numba.parfors.parfor import get_expr_args
from numba.parfors.array_analysis import ArrayAnalysis
from bodo.utils.python_310_bytecode_pass import Bodo310ByteCodePass, peep_hole_call_function_ex_to_call_function_kw, peep_hole_fuse_dict_add_updates, peep_hole_fuse_tuple_adds
from bodo.utils.typing import BodoError, get_overload_const_str, is_overload_constant_str, raise_bodo_error
_check_numba_change = False
numba.core.typing.templates._IntrinsicTemplate.prefer_literal = True


def run_frontend(func, inline_closures=False, emit_dels=False):
    from numba.core.utils import PYVERSION
    ysij__evz = numba.core.bytecode.FunctionIdentity.from_function(func)
    dbxfw__junvi = numba.core.interpreter.Interpreter(ysij__evz)
    pest__dtr = numba.core.bytecode.ByteCode(func_id=ysij__evz)
    func_ir = dbxfw__junvi.interpret(pest__dtr)
    if PYVERSION == (3, 10):
        func_ir = peep_hole_call_function_ex_to_call_function_kw(func_ir)
        func_ir = peep_hole_fuse_dict_add_updates(func_ir)
        func_ir = peep_hole_fuse_tuple_adds(func_ir)
    if inline_closures:
        from numba.core.inline_closurecall import InlineClosureCallPass


        class DummyPipeline:

            def __init__(self, f_ir):
                self.state = numba.core.compiler.StateDict()
                self.state.typingctx = None
                self.state.targetctx = None
                self.state.args = None
                self.state.func_ir = f_ir
                self.state.typemap = None
                self.state.return_type = None
                self.state.calltypes = None
        numba.core.rewrites.rewrite_registry.apply('before-inference',
            DummyPipeline(func_ir).state)
        tjuvl__xfobb = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        tjuvl__xfobb.run()
    xdtz__hozmv = numba.core.postproc.PostProcessor(func_ir)
    xdtz__hozmv.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, brm__lqly in visit_vars_extensions.items():
        if isinstance(stmt, t):
            brm__lqly(stmt, callback, cbdata)
            return
    if isinstance(stmt, ir.Assign):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Arg):
        stmt.name = visit_vars_inner(stmt.name, callback, cbdata)
    elif isinstance(stmt, ir.Return):
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Raise):
        stmt.exception = visit_vars_inner(stmt.exception, callback, cbdata)
    elif isinstance(stmt, ir.Branch):
        stmt.cond = visit_vars_inner(stmt.cond, callback, cbdata)
    elif isinstance(stmt, ir.Jump):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
    elif isinstance(stmt, ir.Del):
        var = ir.Var(None, stmt.value, stmt.loc)
        var = visit_vars_inner(var, callback, cbdata)
        stmt.value = var.name
    elif isinstance(stmt, ir.DelAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
    elif isinstance(stmt, ir.SetAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.DelItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
    elif isinstance(stmt, ir.StaticSetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index_var = visit_vars_inner(stmt.index_var, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.SetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Print):
        stmt.args = [visit_vars_inner(x, callback, cbdata) for x in stmt.args]
        stmt.vararg = visit_vars_inner(stmt.vararg, callback, cbdata)
    else:
        pass
    return


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.visit_vars_stmt)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '52b7b645ba65c35f3cf564f936e113261db16a2dff1e80fbee2459af58844117':
        warnings.warn('numba.core.ir_utils.visit_vars_stmt has changed')
numba.core.ir_utils.visit_vars_stmt = visit_vars_stmt
old_run_pass = numba.core.typed_passes.InlineOverloads.run_pass


def InlineOverloads_run_pass(self, state):
    import bodo
    bodo.compiler.bodo_overload_inline_pass(state.func_ir, state.typingctx,
        state.targetctx, state.typemap, state.calltypes)
    return old_run_pass(self, state)


numba.core.typed_passes.InlineOverloads.run_pass = InlineOverloads_run_pass
from numba.core.ir_utils import _add_alias, alias_analysis_extensions, alias_func_extensions
_immutable_type_class = (types.Number, types.scalars._NPDatetimeBase, types
    .iterators.RangeType, types.UnicodeType)


def is_immutable_type(var, typemap):
    if typemap is None or var not in typemap:
        return False
    typ = typemap[var]
    if isinstance(typ, _immutable_type_class):
        return True
    if isinstance(typ, types.BaseTuple) and all(isinstance(t,
        _immutable_type_class) for t in typ.types):
        return True
    return False


def find_potential_aliases(blocks, args, typemap, func_ir, alias_map=None,
    arg_aliases=None):
    if alias_map is None:
        alias_map = {}
    if arg_aliases is None:
        arg_aliases = set(a for a in args if not is_immutable_type(a, typemap))
    func_ir._definitions = build_definitions(func_ir.blocks)
    rmi__iczxs = ['ravel', 'transpose', 'reshape']
    for iwy__qcpej in blocks.values():
        for jgtpw__rfwf in iwy__qcpej.body:
            if type(jgtpw__rfwf) in alias_analysis_extensions:
                brm__lqly = alias_analysis_extensions[type(jgtpw__rfwf)]
                brm__lqly(jgtpw__rfwf, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(jgtpw__rfwf, ir.Assign):
                iphge__qztz = jgtpw__rfwf.value
                mey__aizw = jgtpw__rfwf.target.name
                if is_immutable_type(mey__aizw, typemap):
                    continue
                if isinstance(iphge__qztz, ir.Var
                    ) and mey__aizw != iphge__qztz.name:
                    _add_alias(mey__aizw, iphge__qztz.name, alias_map,
                        arg_aliases)
                if isinstance(iphge__qztz, ir.Expr) and (iphge__qztz.op ==
                    'cast' or iphge__qztz.op in ['getitem', 'static_getitem']):
                    _add_alias(mey__aizw, iphge__qztz.value.name, alias_map,
                        arg_aliases)
                if isinstance(iphge__qztz, ir.Expr
                    ) and iphge__qztz.op == 'inplace_binop':
                    _add_alias(mey__aizw, iphge__qztz.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(iphge__qztz, ir.Expr
                    ) and iphge__qztz.op == 'getattr' and iphge__qztz.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(mey__aizw, iphge__qztz.value.name, alias_map,
                        arg_aliases)
                if isinstance(iphge__qztz, ir.Expr
                    ) and iphge__qztz.op == 'getattr' and iphge__qztz.attr not in [
                    'shape'] and iphge__qztz.value.name in arg_aliases:
                    _add_alias(mey__aizw, iphge__qztz.value.name, alias_map,
                        arg_aliases)
                if isinstance(iphge__qztz, ir.Expr
                    ) and iphge__qztz.op == 'getattr' and iphge__qztz.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(mey__aizw, iphge__qztz.value.name, alias_map,
                        arg_aliases)
                if isinstance(iphge__qztz, ir.Expr) and iphge__qztz.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(mey__aizw, typemap):
                    for wug__wyq in iphge__qztz.items:
                        _add_alias(mey__aizw, wug__wyq.name, alias_map,
                            arg_aliases)
                if isinstance(iphge__qztz, ir.Expr
                    ) and iphge__qztz.op == 'call':
                    opmq__pkn = guard(find_callname, func_ir, iphge__qztz,
                        typemap)
                    if opmq__pkn is None:
                        continue
                    zamap__llm, aed__smqm = opmq__pkn
                    if opmq__pkn in alias_func_extensions:
                        gdjl__kwoku = alias_func_extensions[opmq__pkn]
                        gdjl__kwoku(mey__aizw, iphge__qztz.args, alias_map,
                            arg_aliases)
                    if aed__smqm == 'numpy' and zamap__llm in rmi__iczxs:
                        _add_alias(mey__aizw, iphge__qztz.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(aed__smqm, ir.Var
                        ) and zamap__llm in rmi__iczxs:
                        _add_alias(mey__aizw, aed__smqm.name, alias_map,
                            arg_aliases)
    ygco__fwg = copy.deepcopy(alias_map)
    for wug__wyq in ygco__fwg:
        for ljfq__okqsu in ygco__fwg[wug__wyq]:
            alias_map[wug__wyq] |= alias_map[ljfq__okqsu]
        for ljfq__okqsu in ygco__fwg[wug__wyq]:
            alias_map[ljfq__okqsu] = alias_map[wug__wyq]
    return alias_map, arg_aliases


if _check_numba_change:
    lines = inspect.getsource(ir_utils.find_potential_aliases)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e6cf3e0f502f903453eb98346fc6854f87dc4ea1ac62f65c2d6aef3bf690b6c5':
        warnings.warn('ir_utils.find_potential_aliases has changed')
ir_utils.find_potential_aliases = find_potential_aliases
numba.parfors.array_analysis.find_potential_aliases = find_potential_aliases
if _check_numba_change:
    lines = inspect.getsource(ir_utils.dead_code_elimination)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '40a8626300a1a17523944ec7842b093c91258bbc60844bbd72191a35a4c366bf':
        warnings.warn('ir_utils.dead_code_elimination has changed')


def mini_dce(func_ir, typemap=None, alias_map=None, arg_aliases=None):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    dezf__jxv = compute_cfg_from_blocks(func_ir.blocks)
    ctl__nxs = compute_use_defs(func_ir.blocks)
    uzyk__xqt = compute_live_map(dezf__jxv, func_ir.blocks, ctl__nxs.usemap,
        ctl__nxs.defmap)
    sly__nur = True
    while sly__nur:
        sly__nur = False
        for label, block in func_ir.blocks.items():
            lives = {wug__wyq.name for wug__wyq in block.terminator.list_vars()
                }
            for qysg__hae, faia__vxme in dezf__jxv.successors(label):
                lives |= uzyk__xqt[qysg__hae]
            smfx__eteh = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    mey__aizw = stmt.target
                    mpa__gnxtg = stmt.value
                    if mey__aizw.name not in lives:
                        if isinstance(mpa__gnxtg, ir.Expr
                            ) and mpa__gnxtg.op == 'make_function':
                            continue
                        if isinstance(mpa__gnxtg, ir.Expr
                            ) and mpa__gnxtg.op == 'getattr':
                            continue
                        if isinstance(mpa__gnxtg, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(mey__aizw,
                            None), types.Function):
                            continue
                        if isinstance(mpa__gnxtg, ir.Expr
                            ) and mpa__gnxtg.op == 'build_map':
                            continue
                        if isinstance(mpa__gnxtg, ir.Expr
                            ) and mpa__gnxtg.op == 'build_tuple':
                            continue
                    if isinstance(mpa__gnxtg, ir.Var
                        ) and mey__aizw.name == mpa__gnxtg.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    qtn__ossft = analysis.ir_extension_usedefs[type(stmt)]
                    liqsg__xgpux, ycnd__invob = qtn__ossft(stmt)
                    lives -= ycnd__invob
                    lives |= liqsg__xgpux
                else:
                    lives |= {wug__wyq.name for wug__wyq in stmt.list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(mey__aizw.name)
                smfx__eteh.append(stmt)
            smfx__eteh.reverse()
            if len(block.body) != len(smfx__eteh):
                sly__nur = True
            block.body = smfx__eteh


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    mdcp__snst = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (mdcp__snst,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    dek__qfhuv = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), dek__qfhuv)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '7f6974584cb10e49995b652827540cc6732e497c0b9f8231b44fd83fcc1c0a83':
        warnings.warn(
            'numba.core.typing.templates.make_overload_template has changed')
numba.core.typing.templates.make_overload_template = make_overload_template


def _resolve(self, typ, attr):
    if self._attr != attr:
        return None
    if isinstance(typ, types.TypeRef):
        assert typ == self.key
    else:
        assert isinstance(typ, self.key)


    class MethodTemplate(AbstractTemplate):
        key = self.key, attr
        _inline = self._inline
        _no_unliteral = getattr(self, '_no_unliteral', False)
        _overload_func = staticmethod(self._overload_func)
        _inline_overloads = self._inline_overloads
        prefer_literal = self.prefer_literal

        def generic(_, args, kws):
            args = (typ,) + tuple(args)
            fnty = self._get_function_type(self.context, typ)
            sig = self._get_signature(self.context, fnty, args, kws)
            sig = sig.replace(pysig=numba.core.utils.pysignature(self.
                _overload_func))
            for kxbnk__bmfra in fnty.templates:
                self._inline_overloads.update(kxbnk__bmfra._inline_overloads)
            if sig is not None:
                return sig.as_method()
    return types.BoundFunction(MethodTemplate, typ)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadMethodTemplate._resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ce8e0935dc939d0867ef969e1ed2975adb3533a58a4133fcc90ae13c4418e4d6':
        warnings.warn(
            'numba.core.typing.templates._OverloadMethodTemplate._resolve has changed'
            )
numba.core.typing.templates._OverloadMethodTemplate._resolve = _resolve


def make_overload_attribute_template(typ, attr, overload_func, inline,
    prefer_literal=False, base=_OverloadAttributeTemplate, **kwargs):
    assert isinstance(typ, types.Type) or issubclass(typ, types.Type)
    name = 'OverloadAttributeTemplate_%s_%s' % (typ, attr)
    no_unliteral = kwargs.pop('no_unliteral', False)
    dek__qfhuv = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), dek__qfhuv)
    return obj


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_attribute_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f066c38c482d6cf8bf5735a529c3264118ba9b52264b24e58aad12a6b1960f5d':
        warnings.warn(
            'numba.core.typing.templates.make_overload_attribute_template has changed'
            )
numba.core.typing.templates.make_overload_attribute_template = (
    make_overload_attribute_template)


def generic(self, args, kws):
    from numba.core.typed_passes import PreLowerStripPhis
    fwk__lkv, pol__zgm = self._get_impl(args, kws)
    if fwk__lkv is None:
        return
    ynupk__befsg = types.Dispatcher(fwk__lkv)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        wvb__zjrip = fwk__lkv._compiler
        flags = compiler.Flags()
        bkt__dyuzq = wvb__zjrip.targetdescr.typing_context
        vab__kqgaw = wvb__zjrip.targetdescr.target_context
        sgxf__nrp = wvb__zjrip.pipeline_class(bkt__dyuzq, vab__kqgaw, None,
            None, None, flags, None)
        xfl__pefb = InlineWorker(bkt__dyuzq, vab__kqgaw, wvb__zjrip.locals,
            sgxf__nrp, flags, None)
        upst__xogsg = ynupk__befsg.dispatcher.get_call_template
        kxbnk__bmfra, xzkz__kfj, iqsv__grpdh, kws = upst__xogsg(pol__zgm, kws)
        if iqsv__grpdh in self._inline_overloads:
            return self._inline_overloads[iqsv__grpdh]['iinfo'].signature
        ir = xfl__pefb.run_untyped_passes(ynupk__befsg.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, vab__kqgaw, ir, iqsv__grpdh, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, iqsv__grpdh, None)
        self._inline_overloads[sig.args] = {'folded_args': iqsv__grpdh}
        nbe__lpmuv = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = nbe__lpmuv
        if not self._inline.is_always_inline:
            sig = ynupk__befsg.get_call_type(self.context, pol__zgm, kws)
            self._compiled_overloads[sig.args] = ynupk__befsg.get_overload(sig)
        dalzw__pijxi = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': iqsv__grpdh,
            'iinfo': dalzw__pijxi}
    else:
        sig = ynupk__befsg.get_call_type(self.context, pol__zgm, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = ynupk__befsg.get_overload(sig)
    return sig


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5d453a6d0215ebf0bab1279ff59eb0040b34938623be99142ce20acc09cdeb64':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate.generic has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate.generic = generic


def bound_function(template_key, no_unliteral=False):

    def wrapper(method_resolver):

        @functools.wraps(method_resolver)
        def attribute_resolver(self, ty):


            class MethodTemplate(AbstractTemplate):
                key = template_key

                def generic(_, args, kws):
                    sig = method_resolver(self, ty, args, kws)
                    if sig is not None and sig.recvr is None:
                        sig = sig.replace(recvr=ty)
                    return sig
            MethodTemplate._no_unliteral = no_unliteral
            return types.BoundFunction(MethodTemplate, ty)
        return attribute_resolver
    return wrapper


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.bound_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a2feefe64eae6a15c56affc47bf0c1d04461f9566913442d539452b397103322':
        warnings.warn('numba.core.typing.templates.bound_function has changed')
numba.core.typing.templates.bound_function = bound_function


def get_call_type(self, context, args, kws):
    from numba.core import utils
    dar__fnh = [True, False]
    zfgs__xbfjs = [False, True]
    qchv__icur = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    vzjyy__rgb = get_local_target(context)
    tnhq__jri = utils.order_by_target_specificity(vzjyy__rgb, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for edvjp__xsfyb in tnhq__jri:
        wkcrk__aewy = edvjp__xsfyb(context)
        ytvp__ywlbp = dar__fnh if wkcrk__aewy.prefer_literal else zfgs__xbfjs
        ytvp__ywlbp = [True] if getattr(wkcrk__aewy, '_no_unliteral', False
            ) else ytvp__ywlbp
        for bql__wmax in ytvp__ywlbp:
            try:
                if bql__wmax:
                    sig = wkcrk__aewy.apply(args, kws)
                else:
                    zdv__tvsyr = tuple([_unlit_non_poison(a) for a in args])
                    enp__susw = {myok__jtrvx: _unlit_non_poison(wug__wyq) for
                        myok__jtrvx, wug__wyq in kws.items()}
                    sig = wkcrk__aewy.apply(zdv__tvsyr, enp__susw)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    qchv__icur.add_error(wkcrk__aewy, False, e, bql__wmax)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = wkcrk__aewy.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    diww__oztsp = getattr(wkcrk__aewy, 'cases', None)
                    if diww__oztsp is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            diww__oztsp)
                    else:
                        msg = 'No match.'
                    qchv__icur.add_error(wkcrk__aewy, True, msg, bql__wmax)
    qchv__icur.raise_error()


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BaseFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '25f038a7216f8e6f40068ea81e11fd9af8ad25d19888f7304a549941b01b7015':
        warnings.warn(
            'numba.core.types.functions.BaseFunction.get_call_type has changed'
            )
numba.core.types.functions.BaseFunction.get_call_type = get_call_type
bodo_typing_error_info = """
This is often caused by the use of unsupported features or typing issues.
See https://docs.bodo.ai/
"""


def get_call_type2(self, context, args, kws):
    kxbnk__bmfra = self.template(context)
    soav__eowp = None
    geagj__srjt = None
    pnurb__wmbt = None
    ytvp__ywlbp = [True, False] if kxbnk__bmfra.prefer_literal else [False,
        True]
    ytvp__ywlbp = [True] if getattr(kxbnk__bmfra, '_no_unliteral', False
        ) else ytvp__ywlbp
    for bql__wmax in ytvp__ywlbp:
        if bql__wmax:
            try:
                pnurb__wmbt = kxbnk__bmfra.apply(args, kws)
            except Exception as zwjov__hmavk:
                if isinstance(zwjov__hmavk, errors.ForceLiteralArg):
                    raise zwjov__hmavk
                soav__eowp = zwjov__hmavk
                pnurb__wmbt = None
            else:
                break
        else:
            vhc__ning = tuple([_unlit_non_poison(a) for a in args])
            ytwu__hoev = {myok__jtrvx: _unlit_non_poison(wug__wyq) for 
                myok__jtrvx, wug__wyq in kws.items()}
            ovjvh__lgsts = vhc__ning == args and kws == ytwu__hoev
            if not ovjvh__lgsts and pnurb__wmbt is None:
                try:
                    pnurb__wmbt = kxbnk__bmfra.apply(vhc__ning, ytwu__hoev)
                except Exception as zwjov__hmavk:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        zwjov__hmavk, errors.NumbaError):
                        raise zwjov__hmavk
                    if isinstance(zwjov__hmavk, errors.ForceLiteralArg):
                        if kxbnk__bmfra.prefer_literal:
                            raise zwjov__hmavk
                    geagj__srjt = zwjov__hmavk
                else:
                    break
    if pnurb__wmbt is None and (geagj__srjt is not None or soav__eowp is not
        None):
        caucf__umn = '- Resolution failure for {} arguments:\n{}\n'
        tjqra__ospj = _termcolor.highlight(caucf__umn)
        if numba.core.config.DEVELOPER_MODE:
            ejhp__pbqau = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    cgi__ssf = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    cgi__ssf = ['']
                fchxr__sxxes = '\n{}'.format(2 * ejhp__pbqau)
                otp__txafr = _termcolor.reset(fchxr__sxxes + fchxr__sxxes.
                    join(_bt_as_lines(cgi__ssf)))
                return _termcolor.reset(otp__txafr)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            ugzv__cdv = str(e)
            ugzv__cdv = ugzv__cdv if ugzv__cdv else str(repr(e)) + add_bt(e)
            exjk__qrm = errors.TypingError(textwrap.dedent(ugzv__cdv))
            return tjqra__ospj.format(literalness, str(exjk__qrm))
        import bodo
        if isinstance(soav__eowp, bodo.utils.typing.BodoError):
            raise soav__eowp
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', soav__eowp) +
                nested_msg('non-literal', geagj__srjt))
        else:
            if 'missing a required argument' in soav__eowp.msg:
                msg = 'missing a required argument'
            else:
                msg = 'Compilation error for '
                if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                    DataFrameType):
                    msg += 'DataFrame.'
                elif isinstance(self.this, bodo.hiframes.pd_series_ext.
                    SeriesType):
                    msg += 'Series.'
                msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg, loc=soav__eowp.loc)
    return pnurb__wmbt


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BoundFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '502cd77c0084452e903a45a0f1f8107550bfbde7179363b57dabd617ce135f4a':
        warnings.warn(
            'numba.core.types.functions.BoundFunction.get_call_type has changed'
            )
numba.core.types.functions.BoundFunction.get_call_type = get_call_type2


def string_from_string_and_size(self, string, size):
    from llvmlite import ir as lir
    fnty = lir.FunctionType(self.pyobj, [self.cstring, self.py_ssize_t])
    zamap__llm = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=zamap__llm)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            ixw__hzpbu = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), ixw__hzpbu)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    fbdn__kvtv = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            fbdn__kvtv.append(types.Omitted(a.value))
        else:
            fbdn__kvtv.append(self.typeof_pyval(a))
    ghc__djx = None
    try:
        error = None
        ghc__djx = self.compile(tuple(fbdn__kvtv))
    except errors.ForceLiteralArg as e:
        sckr__nze = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if sckr__nze:
            giesq__mwetl = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            rewc__nik = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(sckr__nze))
            raise errors.CompilerError(giesq__mwetl.format(rewc__nik))
        pol__zgm = []
        try:
            for i, wug__wyq in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        pol__zgm.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        pol__zgm.append(types.literal(args[i]))
                else:
                    pol__zgm.append(args[i])
            args = pol__zgm
        except (OSError, FileNotFoundError) as pwl__lnyc:
            error = FileNotFoundError(str(pwl__lnyc) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                ghc__djx = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        kti__zmmzd = []
        for i, aes__barz in enumerate(args):
            val = aes__barz.value if isinstance(aes__barz, numba.core.
                dispatcher.OmittedArg) else aes__barz
            try:
                inar__ttzw = typeof(val, Purpose.argument)
            except ValueError as egs__trxi:
                kti__zmmzd.append((i, str(egs__trxi)))
            else:
                if inar__ttzw is None:
                    kti__zmmzd.append((i,
                        f'cannot determine Numba type of value {val}'))
        if kti__zmmzd:
            pilh__jes = '\n'.join(f'- argument {i}: {ukk__ekvd}' for i,
                ukk__ekvd in kti__zmmzd)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{pilh__jes}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                nea__tdry = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                eglie__lvv = False
                for anwtm__viezz in nea__tdry:
                    if anwtm__viezz in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        eglie__lvv = True
                        break
                if not eglie__lvv:
                    msg = f'{str(e)}'
                msg += '\n' + e.loc.strformat() + '\n'
                e.patch_message(msg)
        error_rewrite(e, 'typing')
    except errors.UnsupportedError as e:
        error_rewrite(e, 'unsupported_error')
    except (errors.NotDefinedError, errors.RedefinedError, errors.
        VerificationError) as e:
        error_rewrite(e, 'interpreter')
    except errors.ConstantInferenceError as e:
        error_rewrite(e, 'constant_inference')
    except bodo.utils.typing.BodoError as e:
        error = bodo.utils.typing.BodoError(str(e))
    except Exception as e:
        if numba.core.config.SHOW_HELP:
            if hasattr(e, 'patch_message'):
                ixw__hzpbu = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), ixw__hzpbu)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return ghc__djx


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher._DispatcherBase.
        _compile_for_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5cdfbf0b13a528abf9f0408e70f67207a03e81d610c26b1acab5b2dc1f79bf06':
        warnings.warn(
            'numba.core.dispatcher._DispatcherBase._compile_for_args has changed'
            )
numba.core.dispatcher._DispatcherBase._compile_for_args = _compile_for_args


def resolve_gb_agg_funcs(cres):
    from bodo.ir.aggregate import gb_agg_cfunc_addr
    for tgo__vkv in cres.library._codegen._engine._defined_symbols:
        if tgo__vkv.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in tgo__vkv and (
            'bodo_gb_udf_update_local' in tgo__vkv or 'bodo_gb_udf_combine' in
            tgo__vkv or 'bodo_gb_udf_eval' in tgo__vkv or 
            'bodo_gb_apply_general_udfs' in tgo__vkv):
            gb_agg_cfunc_addr[tgo__vkv] = cres.library.get_pointer_to_function(
                tgo__vkv)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for tgo__vkv in cres.library._codegen._engine._defined_symbols:
        if tgo__vkv.startswith('cfunc') and ('get_join_cond_addr' not in
            tgo__vkv or 'bodo_join_gen_cond' in tgo__vkv):
            join_gen_cond_cfunc_addr[tgo__vkv
                ] = cres.library.get_pointer_to_function(tgo__vkv)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    fwk__lkv = self._get_dispatcher_for_current_target()
    if fwk__lkv is not self:
        return fwk__lkv.compile(sig)
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        if not self._can_compile:
            raise RuntimeError('compilation disabled')
        with self._compiling_counter:
            args, return_type = sigutils.normalize_signature(sig)
            wtt__feosa = self.overloads.get(tuple(args))
            if wtt__feosa is not None:
                return wtt__feosa.entry_point
            cres = self._cache.load_overload(sig, self.targetctx)
            if cres is not None:
                resolve_gb_agg_funcs(cres)
                resolve_join_general_cond_funcs(cres)
                self._cache_hits[sig] += 1
                if not cres.objectmode:
                    self.targetctx.insert_user_function(cres.entry_point,
                        cres.fndesc, [cres.library])
                self.add_overload(cres)
                return cres.entry_point
            self._cache_misses[sig] += 1
            ytz__jjpij = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=ytz__jjpij):
                try:
                    cres = self._compiler.compile(args, return_type)
                except errors.ForceLiteralArg as e:

                    def folded(args, kws):
                        return self._compiler.fold_argument_types(args, kws)[1]
                    raise e.bind_fold_arguments(folded)
                self.add_overload(cres)
            if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
                if bodo.get_rank() == 0:
                    self._cache.save_overload(sig, cres)
            else:
                qju__suoe = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in qju__suoe:
                    self._cache.save_overload(sig, cres)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.Dispatcher.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '934ec993577ea3b1c7dd2181ac02728abf8559fd42c17062cc821541b092ff8f':
        warnings.warn('numba.core.dispatcher.Dispatcher.compile has changed')
numba.core.dispatcher.Dispatcher.compile = compile


def _get_module_for_linking(self):
    import llvmlite.binding as ll
    self._ensure_finalized()
    if self._shared_module is not None:
        return self._shared_module
    nsuau__mraz = self._final_module
    mrgqz__nodo = []
    pve__nacec = 0
    for fn in nsuau__mraz.functions:
        pve__nacec += 1
        if not fn.is_declaration and fn.linkage == ll.Linkage.external:
            if 'get_agg_udf_addr' not in fn.name:
                if 'bodo_gb_udf_update_local' in fn.name:
                    continue
                if 'bodo_gb_udf_combine' in fn.name:
                    continue
                if 'bodo_gb_udf_eval' in fn.name:
                    continue
                if 'bodo_gb_apply_general_udfs' in fn.name:
                    continue
            if 'get_join_cond_addr' not in fn.name:
                if 'bodo_join_gen_cond' in fn.name:
                    continue
            mrgqz__nodo.append(fn.name)
    if pve__nacec == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if mrgqz__nodo:
        nsuau__mraz = nsuau__mraz.clone()
        for name in mrgqz__nodo:
            nsuau__mraz.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = nsuau__mraz
    return nsuau__mraz


if _check_numba_change:
    lines = inspect.getsource(numba.core.codegen.CPUCodeLibrary.
        _get_module_for_linking)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '56dde0e0555b5ec85b93b97c81821bce60784515a1fbf99e4542e92d02ff0a73':
        warnings.warn(
            'numba.core.codegen.CPUCodeLibrary._get_module_for_linking has changed'
            )
numba.core.codegen.CPUCodeLibrary._get_module_for_linking = (
    _get_module_for_linking)


def propagate(self, typeinfer):
    import bodo
    errors = []
    for ektf__kult in self.constraints:
        loc = ektf__kult.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                ektf__kult(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                lau__bri = numba.core.errors.TypingError(str(e), loc=
                    ektf__kult.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(lau__bri, e))
            except bodo.utils.typing.BodoError as e:
                if loc not in e.locs_in_msg:
                    errors.append(bodo.utils.typing.BodoError(str(e.msg) +
                        '\n' + loc.strformat() + '\n', locs_in_msg=e.
                        locs_in_msg + [loc]))
                else:
                    errors.append(bodo.utils.typing.BodoError(e.msg,
                        locs_in_msg=e.locs_in_msg))
            except Exception as e:
                from numba.core import utils
                if utils.use_old_style_errors():
                    numba.core.typeinfer._logger.debug('captured error',
                        exc_info=e)
                    msg = """Internal error at {con}.
{err}
Enable logging at debug level for details."""
                    lau__bri = numba.core.errors.TypingError(msg.format(con
                        =ektf__kult, err=str(e)), loc=ektf__kult.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(lau__bri, e))
                elif utils.use_new_style_errors():
                    raise e
                else:
                    msg = (
                        f"Unknown CAPTURED_ERRORS style: '{numba.core.config.CAPTURED_ERRORS}'."
                        )
                    assert 0, msg
    return errors


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.ConstraintNetwork.propagate)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e73635eeba9ba43cb3372f395b747ae214ce73b729fb0adba0a55237a1cb063':
        warnings.warn(
            'numba.core.typeinfer.ConstraintNetwork.propagate has changed')
numba.core.typeinfer.ConstraintNetwork.propagate = propagate


def raise_error(self):
    import bodo
    for lxd__epak in self._failures.values():
        for lmeiw__cijfs in lxd__epak:
            if isinstance(lmeiw__cijfs.error, ForceLiteralArg):
                raise lmeiw__cijfs.error
            if isinstance(lmeiw__cijfs.error, bodo.utils.typing.BodoError):
                raise lmeiw__cijfs.error
    raise TypingError(self.format())


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.
        _ResolutionFailures.raise_error)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84b89430f5c8b46cfc684804e6037f00a0f170005cd128ad245551787b2568ea':
        warnings.warn(
            'numba.core.types.functions._ResolutionFailures.raise_error has changed'
            )
numba.core.types.functions._ResolutionFailures.raise_error = raise_error


def bodo_remove_dead_block(block, lives, call_table, arg_aliases, alias_map,
    alias_set, func_ir, typemap):
    from bodo.transforms.distributed_pass import saved_array_analysis
    from bodo.utils.utils import is_array_typ, is_expr
    vvye__wtr = False
    smfx__eteh = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        hcuf__mlt = set()
        ooz__vjpn = lives & alias_set
        for wug__wyq in ooz__vjpn:
            hcuf__mlt |= alias_map[wug__wyq]
        lives_n_aliases = lives | hcuf__mlt | arg_aliases
        if type(stmt) in remove_dead_extensions:
            brm__lqly = remove_dead_extensions[type(stmt)]
            stmt = brm__lqly(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                vvye__wtr = True
                continue
        if isinstance(stmt, ir.Assign):
            mey__aizw = stmt.target
            mpa__gnxtg = stmt.value
            if mey__aizw.name not in lives:
                if has_no_side_effect(mpa__gnxtg, lives_n_aliases, call_table):
                    vvye__wtr = True
                    continue
                if isinstance(mpa__gnxtg, ir.Expr
                    ) and mpa__gnxtg.op == 'call' and call_table[mpa__gnxtg
                    .func.name] == ['astype']:
                    knqah__zwukz = guard(get_definition, func_ir,
                        mpa__gnxtg.func)
                    if (knqah__zwukz is not None and knqah__zwukz.op ==
                        'getattr' and isinstance(typemap[knqah__zwukz.value
                        .name], types.Array) and knqah__zwukz.attr == 'astype'
                        ):
                        vvye__wtr = True
                        continue
            if saved_array_analysis and mey__aizw.name in lives and is_expr(
                mpa__gnxtg, 'getattr'
                ) and mpa__gnxtg.attr == 'shape' and is_array_typ(typemap[
                mpa__gnxtg.value.name]) and mpa__gnxtg.value.name not in lives:
                tdesv__fgu = {wug__wyq: myok__jtrvx for myok__jtrvx,
                    wug__wyq in func_ir.blocks.items()}
                if block in tdesv__fgu:
                    label = tdesv__fgu[block]
                    ygnzl__gbpx = saved_array_analysis.get_equiv_set(label)
                    mgwzw__bexd = ygnzl__gbpx.get_equiv_set(mpa__gnxtg.value)
                    if mgwzw__bexd is not None:
                        for wug__wyq in mgwzw__bexd:
                            if wug__wyq.endswith('#0'):
                                wug__wyq = wug__wyq[:-2]
                            if wug__wyq in typemap and is_array_typ(typemap
                                [wug__wyq]) and wug__wyq in lives:
                                mpa__gnxtg.value = ir.Var(mpa__gnxtg.value.
                                    scope, wug__wyq, mpa__gnxtg.value.loc)
                                vvye__wtr = True
                                break
            if isinstance(mpa__gnxtg, ir.Var
                ) and mey__aizw.name == mpa__gnxtg.name:
                vvye__wtr = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                vvye__wtr = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            qtn__ossft = analysis.ir_extension_usedefs[type(stmt)]
            liqsg__xgpux, ycnd__invob = qtn__ossft(stmt)
            lives -= ycnd__invob
            lives |= liqsg__xgpux
        else:
            lives |= {wug__wyq.name for wug__wyq in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                nsy__omv = set()
                if isinstance(mpa__gnxtg, ir.Expr):
                    nsy__omv = {wug__wyq.name for wug__wyq in mpa__gnxtg.
                        list_vars()}
                if mey__aizw.name not in nsy__omv:
                    lives.remove(mey__aizw.name)
        smfx__eteh.append(stmt)
    smfx__eteh.reverse()
    block.body = smfx__eteh
    return vvye__wtr


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            cah__pnm, = args
            if isinstance(cah__pnm, types.IterableType):
                dtype = cah__pnm.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), cah__pnm)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    ryac__orlp = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (ryac__orlp, self.dtype)
    super(types.Set, self).__init__(name=name)


types.Set.__init__ = Set__init__


@lower_builtin(operator.eq, types.UnicodeType, types.UnicodeType)
def eq_str(context, builder, sig, args):
    func = numba.cpython.unicode.unicode_eq(*sig.args)
    return context.compile_internal(builder, func, sig, args)


numba.parfors.parfor.push_call_vars = (lambda blocks, saved_globals,
    saved_getattrs, typemap, nested=False: None)


def maybe_literal(value):
    if isinstance(value, (list, dict, pytypes.FunctionType)):
        return
    if isinstance(value, tuple):
        try:
            return types.Tuple([literal(x) for x in value])
        except LiteralTypingError as qfeu__tir:
            return
    try:
        return literal(value)
    except LiteralTypingError as qfeu__tir:
        return


if _check_numba_change:
    lines = inspect.getsource(types.maybe_literal)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8fb2fd93acf214b28e33e37d19dc2f7290a42792ec59b650553ac278854b5081':
        warnings.warn('types.maybe_literal has changed')
types.maybe_literal = maybe_literal
types.misc.maybe_literal = maybe_literal


def CacheImpl__init__(self, py_func):
    self._lineno = py_func.__code__.co_firstlineno
    try:
        jgple__uyptl = py_func.__qualname__
    except AttributeError as qfeu__tir:
        jgple__uyptl = py_func.__name__
    vbch__djxoi = inspect.getfile(py_func)
    for cls in self._locator_classes:
        jrdk__kztgm = cls.from_function(py_func, vbch__djxoi)
        if jrdk__kztgm is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (jgple__uyptl, vbch__djxoi))
    self._locator = jrdk__kztgm
    whwvj__ukvqs = inspect.getfile(py_func)
    ybve__rhsh = os.path.splitext(os.path.basename(whwvj__ukvqs))[0]
    if vbch__djxoi.startswith('<ipython-'):
        qau__odr = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)', '\\1\\3',
            ybve__rhsh, count=1)
        if qau__odr == ybve__rhsh:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        ybve__rhsh = qau__odr
    rnown__moudn = '%s.%s' % (ybve__rhsh, jgple__uyptl)
    lkktb__mwlg = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(rnown__moudn, lkktb__mwlg
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    wme__kfvd = list(filter(lambda a: self._istuple(a.name), args))
    if len(wme__kfvd) == 2 and fn.__name__ == 'add':
        gvsn__fabay = self.typemap[wme__kfvd[0].name]
        oim__mgano = self.typemap[wme__kfvd[1].name]
        if gvsn__fabay.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                wme__kfvd[1]))
        if oim__mgano.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                wme__kfvd[0]))
        try:
            ovk__cqj = [equiv_set.get_shape(x) for x in wme__kfvd]
            if None in ovk__cqj:
                return None
            xdkb__ujdsg = sum(ovk__cqj, ())
            return ArrayAnalysis.AnalyzeResult(shape=xdkb__ujdsg)
        except GuardException as qfeu__tir:
            return None
    zwer__kagut = list(filter(lambda a: self._isarray(a.name), args))
    require(len(zwer__kagut) > 0)
    tetf__cktc = [x.name for x in zwer__kagut]
    zelxn__iwk = [self.typemap[x.name].ndim for x in zwer__kagut]
    ijd__fntii = max(zelxn__iwk)
    require(ijd__fntii > 0)
    ovk__cqj = [equiv_set.get_shape(x) for x in zwer__kagut]
    if any(a is None for a in ovk__cqj):
        return ArrayAnalysis.AnalyzeResult(shape=zwer__kagut[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, zwer__kagut))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, ovk__cqj,
        tetf__cktc)


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.array_analysis.ArrayAnalysis.
        _analyze_broadcast)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6c91fec038f56111338ea2b08f5f0e7f61ebdab1c81fb811fe26658cc354e40f':
        warnings.warn(
            'numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast has changed'
            )
numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast = (
    _analyze_broadcast)


def slice_size(self, index, dsize, equiv_set, scope, stmts):
    return None, None


numba.parfors.array_analysis.ArrayAnalysis.slice_size = slice_size


def convert_code_obj_to_function(code_obj, caller_ir):
    import bodo
    olh__nrxy = code_obj.code
    xgom__nie = len(olh__nrxy.co_freevars)
    dvsxz__ulgc = olh__nrxy.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        jpi__epq, op = ir_utils.find_build_sequence(caller_ir, code_obj.closure
            )
        assert op == 'build_tuple'
        dvsxz__ulgc = [wug__wyq.name for wug__wyq in jpi__epq]
    hxu__norpk = caller_ir.func_id.func.__globals__
    try:
        hxu__norpk = getattr(code_obj, 'globals', hxu__norpk)
    except KeyError as qfeu__tir:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    mscd__svi = []
    for x in dvsxz__ulgc:
        try:
            gabd__zys = caller_ir.get_definition(x)
        except KeyError as qfeu__tir:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(gabd__zys, (ir.Const, ir.Global, ir.FreeVar)):
            val = gabd__zys.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                mdcp__snst = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                hxu__norpk[mdcp__snst] = bodo.jit(distributed=False)(val)
                hxu__norpk[mdcp__snst].is_nested_func = True
                val = mdcp__snst
            if isinstance(val, CPUDispatcher):
                mdcp__snst = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                hxu__norpk[mdcp__snst] = val
                val = mdcp__snst
            mscd__svi.append(val)
        elif isinstance(gabd__zys, ir.Expr
            ) and gabd__zys.op == 'make_function':
            jvobl__wqr = convert_code_obj_to_function(gabd__zys, caller_ir)
            mdcp__snst = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            hxu__norpk[mdcp__snst] = bodo.jit(distributed=False)(jvobl__wqr)
            hxu__norpk[mdcp__snst].is_nested_func = True
            mscd__svi.append(mdcp__snst)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    tiv__tsdd = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        mscd__svi)])
    mcrxu__ahlv = ','.join([('c_%d' % i) for i in range(xgom__nie)])
    carjp__zuvc = list(olh__nrxy.co_varnames)
    fjo__hom = 0
    wqmjz__gbod = olh__nrxy.co_argcount
    xhoub__oefko = caller_ir.get_definition(code_obj.defaults)
    if xhoub__oefko is not None:
        if isinstance(xhoub__oefko, tuple):
            d = [caller_ir.get_definition(x).value for x in xhoub__oefko]
            rkq__dxtwe = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in xhoub__oefko.items]
            rkq__dxtwe = tuple(d)
        fjo__hom = len(rkq__dxtwe)
    kwkk__axr = wqmjz__gbod - fjo__hom
    irfp__jgebp = ','.join([('%s' % carjp__zuvc[i]) for i in range(kwkk__axr)])
    if fjo__hom:
        yik__enw = [('%s = %s' % (carjp__zuvc[i + kwkk__axr], rkq__dxtwe[i]
            )) for i in range(fjo__hom)]
        irfp__jgebp += ', '
        irfp__jgebp += ', '.join(yik__enw)
    return _create_function_from_code_obj(olh__nrxy, tiv__tsdd, irfp__jgebp,
        mcrxu__ahlv, hxu__norpk)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.convert_code_obj_to_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b840769812418d589460e924a15477e83e7919aac8a3dcb0188ff447344aa8ac':
        warnings.warn(
            'numba.core.ir_utils.convert_code_obj_to_function has changed')
numba.core.ir_utils.convert_code_obj_to_function = convert_code_obj_to_function
numba.core.untyped_passes.convert_code_obj_to_function = (
    convert_code_obj_to_function)


def passmanager_run(self, state):
    from numba.core.compiler import _EarlyPipelineCompletion
    if not self.finalized:
        raise RuntimeError('Cannot run non-finalised pipeline')
    from numba.core.compiler_machinery import CompilerPass, _pass_registry
    import bodo
    for urkc__daus, (bbou__fveeo, sbna__mevzl) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % sbna__mevzl)
            yakdd__ytwoa = _pass_registry.get(bbou__fveeo).pass_inst
            if isinstance(yakdd__ytwoa, CompilerPass):
                self._runPass(urkc__daus, yakdd__ytwoa, state)
            else:
                raise BaseException('Legacy pass in use')
        except _EarlyPipelineCompletion as e:
            raise e
        except bodo.utils.typing.BodoError as e:
            raise
        except Exception as e:
            if numba.core.config.DEVELOPER_MODE:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                msg = 'Failed in %s mode pipeline (step: %s)' % (self.
                    pipeline_name, sbna__mevzl)
                rysjd__ivrd = self._patch_error(msg, e)
                raise rysjd__ivrd
            else:
                raise e


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler_machinery.PassManager.run)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '43505782e15e690fd2d7e53ea716543bec37aa0633502956864edf649e790cdb':
        warnings.warn(
            'numba.core.compiler_machinery.PassManager.run has changed')
numba.core.compiler_machinery.PassManager.run = passmanager_run
if _check_numba_change:
    lines = inspect.getsource(numba.np.ufunc.parallel._launch_threads)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a57ef28c4168fdd436a5513bba4351ebc6d9fba76c5819f44046431a79b9030f':
        warnings.warn('numba.np.ufunc.parallel._launch_threads has changed')
numba.np.ufunc.parallel._launch_threads = lambda : None


def get_reduce_nodes(reduction_node, nodes, func_ir):
    ktyo__mpnkx = None
    ycnd__invob = {}

    def lookup(var, already_seen, varonly=True):
        val = ycnd__invob.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    kyjn__xjeif = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        mey__aizw = stmt.target
        mpa__gnxtg = stmt.value
        ycnd__invob[mey__aizw.name] = mpa__gnxtg
        if isinstance(mpa__gnxtg, ir.Var) and mpa__gnxtg.name in ycnd__invob:
            mpa__gnxtg = lookup(mpa__gnxtg, set())
        if isinstance(mpa__gnxtg, ir.Expr):
            voj__pern = set(lookup(wug__wyq, set(), True).name for wug__wyq in
                mpa__gnxtg.list_vars())
            if name in voj__pern:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(mpa__gnxtg)]
                geuts__lufc = [x for x, twv__kkll in args if twv__kkll.name !=
                    name]
                args = [(x, twv__kkll) for x, twv__kkll in args if x !=
                    twv__kkll.name]
                ibvli__vlxxi = dict(args)
                if len(geuts__lufc) == 1:
                    ibvli__vlxxi[geuts__lufc[0]] = ir.Var(mey__aizw.scope, 
                        name + '#init', mey__aizw.loc)
                replace_vars_inner(mpa__gnxtg, ibvli__vlxxi)
                ktyo__mpnkx = nodes[i:]
                break
    return ktyo__mpnkx


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_reduce_nodes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a05b52aff9cb02e595a510cd34e973857303a71097fc5530567cb70ca183ef3b':
        warnings.warn('numba.parfors.parfor.get_reduce_nodes has changed')
numba.parfors.parfor.get_reduce_nodes = get_reduce_nodes


def _can_reorder_stmts(stmt, next_stmt, func_ir, call_table, alias_map,
    arg_aliases):
    from numba.parfors.parfor import Parfor, expand_aliases, is_assert_equiv
    if isinstance(stmt, Parfor) and not isinstance(next_stmt, Parfor
        ) and not isinstance(next_stmt, ir.Print) and (not isinstance(
        next_stmt, ir.Assign) or has_no_side_effect(next_stmt.value, set(),
        call_table) or guard(is_assert_equiv, func_ir, next_stmt.value)):
        afk__exi = expand_aliases({wug__wyq.name for wug__wyq in stmt.
            list_vars()}, alias_map, arg_aliases)
        yjr__dkz = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        bbrup__qysj = expand_aliases({wug__wyq.name for wug__wyq in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        rtz__pyyk = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(yjr__dkz & bbrup__qysj | rtz__pyyk & afk__exi) == 0:
            return True
    return False


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor._can_reorder_stmts)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '18caa9a01b21ab92b4f79f164cfdbc8574f15ea29deedf7bafdf9b0e755d777c':
        warnings.warn('numba.parfors.parfor._can_reorder_stmts has changed')
numba.parfors.parfor._can_reorder_stmts = _can_reorder_stmts


def get_parfor_writes(parfor, func_ir):
    from numba.parfors.parfor import Parfor
    assert isinstance(parfor, Parfor)
    yyjqo__bgxc = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            yyjqo__bgxc.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                yyjqo__bgxc.update(get_parfor_writes(stmt, func_ir))
    return yyjqo__bgxc


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    yyjqo__bgxc = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        yyjqo__bgxc.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        yyjqo__bgxc = {wug__wyq.name for wug__wyq in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        yyjqo__bgxc = {wug__wyq.name for wug__wyq in stmt.get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            yyjqo__bgxc.update({wug__wyq.name for wug__wyq in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        opmq__pkn = guard(find_callname, func_ir, stmt.value)
        if opmq__pkn in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            yyjqo__bgxc.add(stmt.value.args[0].name)
        if opmq__pkn == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            yyjqo__bgxc.add(stmt.value.args[1].name)
    return yyjqo__bgxc


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.get_stmt_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1a7a80b64c9a0eb27e99dc8eaae187bde379d4da0b74c84fbf87296d87939974':
        warnings.warn('numba.core.ir_utils.get_stmt_writes has changed')


def patch_message(self, new_message):
    self.msg = new_message
    self.args = (new_message,) + self.args[1:]


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.patch_message)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ed189a428a7305837e76573596d767b6e840e99f75c05af6941192e0214fa899':
        warnings.warn('numba.core.errors.NumbaError.patch_message has changed')
numba.core.errors.NumbaError.patch_message = patch_message


def add_context(self, msg):
    if numba.core.config.DEVELOPER_MODE:
        self.contexts.append(msg)
        brm__lqly = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        ufcqz__wqir = brm__lqly.format(self, msg)
        self.args = ufcqz__wqir,
    else:
        brm__lqly = _termcolor.errmsg('{0}')
        ufcqz__wqir = brm__lqly.format(self)
        self.args = ufcqz__wqir,
    return self


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.add_context)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6a388d87788f8432c2152ac55ca9acaa94dbc3b55be973b2cf22dd4ee7179ab8':
        warnings.warn('numba.core.errors.NumbaError.add_context has changed')
numba.core.errors.NumbaError.add_context = add_context


def _get_dist_spec_from_options(spec, **options):
    from bodo.transforms.distributed_analysis import Distribution
    dist_spec = {}
    if 'distributed' in options:
        for drz__amzyd in options['distributed']:
            dist_spec[drz__amzyd] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for drz__amzyd in options['distributed_block']:
            dist_spec[drz__amzyd] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    yjxtp__mvgg = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, zwfpr__ffcl in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(zwfpr__ffcl)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    pqes__aphed = {}
    for rhgb__kkgo in reversed(inspect.getmro(cls)):
        pqes__aphed.update(rhgb__kkgo.__dict__)
    wce__ruh, soawq__atg, cllne__ktlrs, syrq__rnjb = {}, {}, {}, {}
    for myok__jtrvx, wug__wyq in pqes__aphed.items():
        if isinstance(wug__wyq, pytypes.FunctionType):
            wce__ruh[myok__jtrvx] = wug__wyq
        elif isinstance(wug__wyq, property):
            soawq__atg[myok__jtrvx] = wug__wyq
        elif isinstance(wug__wyq, staticmethod):
            cllne__ktlrs[myok__jtrvx] = wug__wyq
        else:
            syrq__rnjb[myok__jtrvx] = wug__wyq
    wttfg__tllki = (set(wce__ruh) | set(soawq__atg) | set(cllne__ktlrs)) & set(
        spec)
    if wttfg__tllki:
        raise NameError('name shadowing: {0}'.format(', '.join(wttfg__tllki)))
    jejh__hjrj = syrq__rnjb.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(syrq__rnjb)
    if syrq__rnjb:
        msg = 'class members are not yet supported: {0}'
        ckwah__gwt = ', '.join(syrq__rnjb.keys())
        raise TypeError(msg.format(ckwah__gwt))
    for myok__jtrvx, wug__wyq in soawq__atg.items():
        if wug__wyq.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(myok__jtrvx)
                )
    jit_methods = {myok__jtrvx: bodo.jit(returns_maybe_distributed=
        yjxtp__mvgg)(wug__wyq) for myok__jtrvx, wug__wyq in wce__ruh.items()}
    jit_props = {}
    for myok__jtrvx, wug__wyq in soawq__atg.items():
        dek__qfhuv = {}
        if wug__wyq.fget:
            dek__qfhuv['get'] = bodo.jit(wug__wyq.fget)
        if wug__wyq.fset:
            dek__qfhuv['set'] = bodo.jit(wug__wyq.fset)
        jit_props[myok__jtrvx] = dek__qfhuv
    jit_static_methods = {myok__jtrvx: bodo.jit(wug__wyq.__func__) for 
        myok__jtrvx, wug__wyq in cllne__ktlrs.items()}
    ktppx__ycqaq = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    dilr__ylo = dict(class_type=ktppx__ycqaq, __doc__=jejh__hjrj)
    dilr__ylo.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), dilr__ylo)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, ktppx__ycqaq)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(ktppx__ycqaq, typingctx, targetctx).register()
    as_numba_type.register(cls, ktppx__ycqaq.instance_type)
    return cls


if _check_numba_change:
    lines = inspect.getsource(jitclass_base.register_class_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '005e6e2e89a47f77a19ba86305565050d4dbc2412fc4717395adf2da348671a9':
        warnings.warn('jitclass_base.register_class_type has changed')
jitclass_base.register_class_type = register_class_type


def ClassType__init__(self, class_def, ctor_template_cls, struct,
    jit_methods, jit_props, jit_static_methods, dist_spec=None):
    if dist_spec is None:
        dist_spec = {}
    self.class_name = class_def.__name__
    self.class_doc = class_def.__doc__
    self._ctor_template_class = ctor_template_cls
    self.jit_methods = jit_methods
    self.jit_props = jit_props
    self.jit_static_methods = jit_static_methods
    self.struct = struct
    self.dist_spec = dist_spec
    ghima__aqbvn = ','.join('{0}:{1}'.format(myok__jtrvx, wug__wyq) for 
        myok__jtrvx, wug__wyq in struct.items())
    lelp__rnhum = ','.join('{0}:{1}'.format(myok__jtrvx, wug__wyq) for 
        myok__jtrvx, wug__wyq in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), ghima__aqbvn, lelp__rnhum)
    super(types.misc.ClassType, self).__init__(name)


if _check_numba_change:
    lines = inspect.getsource(types.misc.ClassType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '2b848ea82946c88f540e81f93ba95dfa7cd66045d944152a337fe2fc43451c30':
        warnings.warn('types.misc.ClassType.__init__ has changed')
types.misc.ClassType.__init__ = ClassType__init__


def jitclass(cls_or_spec=None, spec=None, **options):
    if cls_or_spec is not None and spec is None and not isinstance(cls_or_spec,
        type):
        spec = cls_or_spec
        cls_or_spec = None

    def wrap(cls):
        if numba.core.config.DISABLE_JIT:
            return cls
        else:
            from numba.experimental.jitclass.base import ClassBuilder
            return register_class_type(cls, spec, types.ClassType,
                ClassBuilder, **options)
    if cls_or_spec is None:
        return wrap
    else:
        return wrap(cls_or_spec)


if _check_numba_change:
    lines = inspect.getsource(jitclass_decorators.jitclass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '265f1953ee5881d1a5d90238d3c932cd300732e41495657e65bf51e59f7f4af5':
        warnings.warn('jitclass_decorators.jitclass has changed')


def CallConstraint_resolve(self, typeinfer, typevars, fnty):
    assert fnty
    context = typeinfer.context
    curh__fdxh = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if curh__fdxh is None:
        return
    lnvt__tzdk, bhey__wemui = curh__fdxh
    for a in itertools.chain(lnvt__tzdk, bhey__wemui.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, lnvt__tzdk, bhey__wemui)
    except ForceLiteralArg as e:
        ffjvg__puhr = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(ffjvg__puhr, self.kws)
        sdn__gaygv = set()
        sloo__epyw = set()
        hnau__wyg = {}
        for urkc__daus in e.requested_args:
            zip__clz = typeinfer.func_ir.get_definition(folded[urkc__daus])
            if isinstance(zip__clz, ir.Arg):
                sdn__gaygv.add(zip__clz.index)
                if zip__clz.index in e.file_infos:
                    hnau__wyg[zip__clz.index] = e.file_infos[zip__clz.index]
            else:
                sloo__epyw.add(urkc__daus)
        if sloo__epyw:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif sdn__gaygv:
            raise ForceLiteralArg(sdn__gaygv, loc=self.loc, file_infos=
                hnau__wyg)
    if sig is None:
        iml__pqi = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in lnvt__tzdk]
        args += [('%s=%s' % (myok__jtrvx, wug__wyq)) for myok__jtrvx,
            wug__wyq in sorted(bhey__wemui.items())]
        hyn__pmnc = iml__pqi.format(fnty, ', '.join(map(str, args)))
        gzhtz__hqij = context.explain_function_type(fnty)
        msg = '\n'.join([hyn__pmnc, gzhtz__hqij])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        pfdij__jnpo = context.unify_pairs(sig.recvr, fnty.this)
        if pfdij__jnpo is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if pfdij__jnpo is not None and pfdij__jnpo.is_precise():
            cck__bqq = fnty.copy(this=pfdij__jnpo)
            typeinfer.propagate_refined_type(self.func, cck__bqq)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            ggbm__dao = target.getone()
            if context.unify_pairs(ggbm__dao, sig.return_type) == ggbm__dao:
                sig = sig.replace(return_type=ggbm__dao)
    self.signature = sig
    self._add_refine_map(typeinfer, typevars, sig)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.CallConstraint.resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c78cd8ffc64b836a6a2ddf0362d481b52b9d380c5249920a87ff4da052ce081f':
        warnings.warn('numba.core.typeinfer.CallConstraint.resolve has changed'
            )
numba.core.typeinfer.CallConstraint.resolve = CallConstraint_resolve


def ForceLiteralArg__init__(self, arg_indices, fold_arguments=None, loc=
    None, file_infos=None):
    super(ForceLiteralArg, self).__init__(
        'Pseudo-exception to force literal arguments in the dispatcher',
        loc=loc)
    self.requested_args = frozenset(arg_indices)
    self.fold_arguments = fold_arguments
    if file_infos is None:
        self.file_infos = {}
    else:
        self.file_infos = file_infos


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b241d5e36a4cf7f4c73a7ad3238693612926606c7a278cad1978070b82fb55ef':
        warnings.warn('numba.core.errors.ForceLiteralArg.__init__ has changed')
numba.core.errors.ForceLiteralArg.__init__ = ForceLiteralArg__init__


def ForceLiteralArg_bind_fold_arguments(self, fold_arguments):
    e = ForceLiteralArg(self.requested_args, fold_arguments, loc=self.loc,
        file_infos=self.file_infos)
    return numba.core.utils.chain_exception(e, self)


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.
        bind_fold_arguments)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e93cca558f7c604a47214a8f2ec33ee994104cb3e5051166f16d7cc9315141d':
        warnings.warn(
            'numba.core.errors.ForceLiteralArg.bind_fold_arguments has changed'
            )
numba.core.errors.ForceLiteralArg.bind_fold_arguments = (
    ForceLiteralArg_bind_fold_arguments)


def ForceLiteralArg_combine(self, other):
    if not isinstance(other, ForceLiteralArg):
        giesq__mwetl = '*other* must be a {} but got a {} instead'
        raise TypeError(giesq__mwetl.format(ForceLiteralArg, type(other)))
    return ForceLiteralArg(self.requested_args | other.requested_args,
        file_infos={**self.file_infos, **other.file_infos})


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.combine)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '49bf06612776f5d755c1c7d1c5eb91831a57665a8fed88b5651935f3bf33e899':
        warnings.warn('numba.core.errors.ForceLiteralArg.combine has changed')
numba.core.errors.ForceLiteralArg.combine = ForceLiteralArg_combine


def _get_global_type(self, gv):
    from bodo.utils.typing import FunctionLiteral
    ty = self._lookup_global(gv)
    if ty is not None:
        return ty
    if isinstance(gv, pytypes.ModuleType):
        return types.Module(gv)
    if isinstance(gv, pytypes.FunctionType):
        return FunctionLiteral(gv)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.
        _get_global_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8ffe6b81175d1eecd62a37639b5005514b4477d88f35f5b5395041ac8c945a4a':
        warnings.warn(
            'numba.core.typing.context.BaseContext._get_global_type has changed'
            )
numba.core.typing.context.BaseContext._get_global_type = _get_global_type


def _legalize_args(self, func_ir, args, kwargs, loc, func_globals,
    func_closures):
    from numba.core import sigutils
    from bodo.utils.transform import get_const_value_inner
    if args:
        raise errors.CompilerError(
            "objectmode context doesn't take any positional arguments")
    sjzra__ojmg = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for myok__jtrvx, wug__wyq in kwargs.items():
        wmii__ttx = None
        try:
            zoe__sdklo = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var
                ('dummy'), loc)
            func_ir._definitions[zoe__sdklo.name] = [wug__wyq]
            wmii__ttx = get_const_value_inner(func_ir, zoe__sdklo)
            func_ir._definitions.pop(zoe__sdklo.name)
            if isinstance(wmii__ttx, str):
                wmii__ttx = sigutils._parse_signature_string(wmii__ttx)
            if isinstance(wmii__ttx, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {myok__jtrvx} is annotated as type class {wmii__ttx}."""
                    )
            assert isinstance(wmii__ttx, types.Type)
            if isinstance(wmii__ttx, (types.List, types.Set)):
                wmii__ttx = wmii__ttx.copy(reflected=False)
            sjzra__ojmg[myok__jtrvx] = wmii__ttx
        except BodoError as qfeu__tir:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(wmii__ttx, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(wug__wyq, ir.Global):
                    msg = f'Global {wug__wyq.name!r} is not defined.'
                if isinstance(wug__wyq, ir.FreeVar):
                    msg = f'Freevar {wug__wyq.name!r} is not defined.'
            if isinstance(wug__wyq, ir.Expr) and wug__wyq.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=myok__jtrvx, msg=msg, loc=loc)
    for name, typ in sjzra__ojmg.items():
        self._legalize_arg_type(name, typ, loc)
    return sjzra__ojmg


if _check_numba_change:
    lines = inspect.getsource(numba.core.withcontexts._ObjModeContextType.
        _legalize_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '867c9ba7f1bcf438be56c38e26906bb551f59a99f853a9f68b71208b107c880e':
        warnings.warn(
            'numba.core.withcontexts._ObjModeContextType._legalize_args has changed'
            )
numba.core.withcontexts._ObjModeContextType._legalize_args = _legalize_args


def op_FORMAT_VALUE_byteflow(self, state, inst):
    flags = inst.arg
    if flags & 3 != 0:
        msg = 'str/repr/ascii conversion in f-strings not supported yet'
        raise errors.UnsupportedError(msg, loc=self.get_debug_loc(inst.lineno))
    format_spec = None
    if flags & 4 == 4:
        format_spec = state.pop()
    value = state.pop()
    fmtvar = state.make_temp()
    res = state.make_temp()
    state.append(inst, value=value, res=res, fmtvar=fmtvar, format_spec=
        format_spec)
    state.push(res)


def op_BUILD_STRING_byteflow(self, state, inst):
    oddcr__slzcw = inst.arg
    assert oddcr__slzcw > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(oddcr__slzcw)]))
    tmps = [state.make_temp() for _ in range(oddcr__slzcw - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    wwn__lujeh = ir.Global('format', format, loc=self.loc)
    self.store(value=wwn__lujeh, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    nsifd__kwvet = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=nsifd__kwvet, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    oddcr__slzcw = inst.arg
    assert oddcr__slzcw > 0, 'invalid BUILD_STRING count'
    mjan__xlp = self.get(strings[0])
    for other, qydl__nbqr in zip(strings[1:], tmps):
        other = self.get(other)
        iphge__qztz = ir.Expr.binop(operator.add, lhs=mjan__xlp, rhs=other,
            loc=self.loc)
        self.store(iphge__qztz, qydl__nbqr)
        mjan__xlp = self.get(qydl__nbqr)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    nyvog__zjuyi = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, nyvog__zjuyi])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    cdtl__dfik = mk_unique_var(f'{var_name}')
    suped__bbaoo = cdtl__dfik.replace('<', '_').replace('>', '_')
    suped__bbaoo = suped__bbaoo.replace('.', '_').replace('$', '_v')
    return suped__bbaoo


if _check_numba_change:
    lines = inspect.getsource(numba.core.inline_closurecall.
        _created_inlined_var_name)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '0d91aac55cd0243e58809afe9d252562f9ae2899cde1112cc01a46804e01821e':
        warnings.warn(
            'numba.core.inline_closurecall._created_inlined_var_name has changed'
            )
numba.core.inline_closurecall._created_inlined_var_name = (
    _created_inlined_var_name)


def resolve_number___call__(self, classty):
    import numpy as np
    from numba.core.typing.templates import make_callable_template
    import bodo
    ty = classty.instance_type
    if isinstance(ty, types.NPDatetime):

        def typer(val1, val2):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(val1,
                'numpy.datetime64')
            if val1 == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
                if not is_overload_constant_str(val2):
                    raise_bodo_error(
                        "datetime64(): 'units' must be a 'str' specifying 'ns'"
                        )
                fpdrz__lsm = get_overload_const_str(val2)
                if fpdrz__lsm != 'ns':
                    raise BodoError("datetime64(): 'units' must be 'ns'")
                return types.NPDatetime('ns')
    else:

        def typer(val):
            if isinstance(val, (types.BaseTuple, types.Sequence)):
                fnty = self.context.resolve_value_type(np.array)
                sig = fnty.get_call_type(self.context, (val, types.DType(ty
                    )), {})
                return sig.return_type
            elif isinstance(val, (types.Number, types.Boolean, types.
                IntEnumMember)):
                return ty
            elif val == types.unicode_type:
                return ty
            elif isinstance(val, (types.NPDatetime, types.NPTimedelta)):
                if ty.bitwidth == 64:
                    return ty
                else:
                    msg = (
                        f'Cannot cast {val} to {ty} as {ty} is not 64 bits wide.'
                        )
                    raise errors.TypingError(msg)
            elif isinstance(val, types.Array
                ) and val.ndim == 0 and val.dtype == ty:
                return ty
            else:
                msg = f'Casting {val} to {ty} directly is unsupported.'
                if isinstance(val, types.Array):
                    msg += f" Try doing '<array>.astype(np.{ty})' instead"
                raise errors.TypingError(msg)
    return types.Function(make_callable_template(key=ty, typer=typer))


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.builtins.
        NumberClassAttribute.resolve___call__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdaf0c7d0820130481bb2bd922985257b9281b670f0bafffe10e51cabf0d5081':
        warnings.warn(
            'numba.core.typing.builtins.NumberClassAttribute.resolve___call__ has changed'
            )
numba.core.typing.builtins.NumberClassAttribute.resolve___call__ = (
    resolve_number___call__)


def on_assign(self, states, assign):
    if assign.target.name == states['varname']:
        scope = states['scope']
        ppjyr__rckg = states['defmap']
        if len(ppjyr__rckg) == 0:
            zijz__mdo = assign.target
            numba.core.ssa._logger.debug('first assign: %s', zijz__mdo)
            if zijz__mdo.name not in scope.localvars:
                zijz__mdo = scope.define(assign.target.name, loc=assign.loc)
        else:
            zijz__mdo = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=zijz__mdo, value=assign.value, loc=assign.loc
            )
        ppjyr__rckg[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    pjnjs__xeuq = []
    for myok__jtrvx, wug__wyq in typing.npydecl.registry.globals:
        if myok__jtrvx == func:
            pjnjs__xeuq.append(wug__wyq)
    for myok__jtrvx, wug__wyq in typing.templates.builtin_registry.globals:
        if myok__jtrvx == func:
            pjnjs__xeuq.append(wug__wyq)
    if len(pjnjs__xeuq) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return pjnjs__xeuq


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    kmzgt__neoie = {}
    alpx__yajp = find_topo_order(blocks)
    lakg__eetck = {}
    for label in alpx__yajp:
        block = blocks[label]
        smfx__eteh = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                mey__aizw = stmt.target.name
                mpa__gnxtg = stmt.value
                if (mpa__gnxtg.op == 'getattr' and mpa__gnxtg.attr in
                    arr_math and isinstance(typemap[mpa__gnxtg.value.name],
                    types.npytypes.Array)):
                    mpa__gnxtg = stmt.value
                    sbci__xgbba = mpa__gnxtg.value
                    kmzgt__neoie[mey__aizw] = sbci__xgbba
                    scope = sbci__xgbba.scope
                    loc = sbci__xgbba.loc
                    ypeym__tafa = ir.Var(scope, mk_unique_var('$np_g_var'), loc
                        )
                    typemap[ypeym__tafa.name] = types.misc.Module(numpy)
                    hhh__pnhu = ir.Global('np', numpy, loc)
                    leb__thbbx = ir.Assign(hhh__pnhu, ypeym__tafa, loc)
                    mpa__gnxtg.value = ypeym__tafa
                    smfx__eteh.append(leb__thbbx)
                    func_ir._definitions[ypeym__tafa.name] = [hhh__pnhu]
                    func = getattr(numpy, mpa__gnxtg.attr)
                    qrgan__caiz = get_np_ufunc_typ_lst(func)
                    lakg__eetck[mey__aizw] = qrgan__caiz
                if (mpa__gnxtg.op == 'call' and mpa__gnxtg.func.name in
                    kmzgt__neoie):
                    sbci__xgbba = kmzgt__neoie[mpa__gnxtg.func.name]
                    mir__bnjm = calltypes.pop(mpa__gnxtg)
                    dsoi__eaawi = mir__bnjm.args[:len(mpa__gnxtg.args)]
                    ohpml__qylf = {name: typemap[wug__wyq.name] for name,
                        wug__wyq in mpa__gnxtg.kws}
                    arqiv__ubz = lakg__eetck[mpa__gnxtg.func.name]
                    yuw__pvbw = None
                    for lwabh__zki in arqiv__ubz:
                        try:
                            yuw__pvbw = lwabh__zki.get_call_type(typingctx,
                                [typemap[sbci__xgbba.name]] + list(
                                dsoi__eaawi), ohpml__qylf)
                            typemap.pop(mpa__gnxtg.func.name)
                            typemap[mpa__gnxtg.func.name] = lwabh__zki
                            calltypes[mpa__gnxtg] = yuw__pvbw
                            break
                        except Exception as qfeu__tir:
                            pass
                    if yuw__pvbw is None:
                        raise TypeError(
                            f'No valid template found for {mpa__gnxtg.func.name}'
                            )
                    mpa__gnxtg.args = [sbci__xgbba] + mpa__gnxtg.args
            smfx__eteh.append(stmt)
        block.body = smfx__eteh


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    aulmc__yppuk = ufunc.nin
    rkund__dcwya = ufunc.nout
    kwkk__axr = ufunc.nargs
    assert kwkk__axr == aulmc__yppuk + rkund__dcwya
    if len(args) < aulmc__yppuk:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            aulmc__yppuk))
    if len(args) > kwkk__axr:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), kwkk__axr))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    zvmbh__ulvm = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    umm__ahb = max(zvmbh__ulvm)
    tmte__slg = args[aulmc__yppuk:]
    if not all(d == umm__ahb for d in zvmbh__ulvm[aulmc__yppuk:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(sjh__ygwfd, types.ArrayCompatible) and not
        isinstance(sjh__ygwfd, types.Bytes) for sjh__ygwfd in tmte__slg):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(sjh__ygwfd.mutable for sjh__ygwfd in tmte__slg):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    zkt__tmbyk = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    sdmju__tuier = None
    if umm__ahb > 0 and len(tmte__slg) < ufunc.nout:
        sdmju__tuier = 'C'
        jlv__zdusr = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in jlv__zdusr and 'F' in jlv__zdusr:
            sdmju__tuier = 'F'
    return zkt__tmbyk, tmte__slg, umm__ahb, sdmju__tuier


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.Numpy_rules_ufunc.
        _handle_inputs)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4b97c64ad9c3d50e082538795054f35cf6d2fe962c3ca40e8377a4601b344d5c':
        warnings.warn('Numpy_rules_ufunc._handle_inputs has changed')
numba.core.typing.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)
numba.np.ufunc.dufunc.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)


def DictType__init__(self, keyty, valty, initial_value=None):
    from numba.types import DictType, InitialValue, NoneType, Optional, Tuple, TypeRef, unliteral
    assert not isinstance(keyty, TypeRef)
    assert not isinstance(valty, TypeRef)
    keyty = unliteral(keyty)
    valty = unliteral(valty)
    if isinstance(keyty, (Optional, NoneType)):
        wkcgl__jijzi = 'Dict.key_type cannot be of type {}'
        raise TypingError(wkcgl__jijzi.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        wkcgl__jijzi = 'Dict.value_type cannot be of type {}'
        raise TypingError(wkcgl__jijzi.format(valty))
    self.key_type = keyty
    self.value_type = valty
    self.keyvalue_type = Tuple([keyty, valty])
    name = '{}[{},{}]<iv={}>'.format(self.__class__.__name__, keyty, valty,
        initial_value)
    super(DictType, self).__init__(name)
    InitialValue.__init__(self, initial_value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.containers.DictType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '475acd71224bd51526750343246e064ff071320c0d10c17b8b8ac81d5070d094':
        warnings.warn('DictType.__init__ has changed')
numba.core.types.containers.DictType.__init__ = DictType__init__


def _legalize_arg_types(self, args):
    for i, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(i))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    dzn__fenod = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[dzn__fenod]
        return impl, args
    except KeyError as qfeu__tir:
        pass
    impl, args = self._build_impl(dzn__fenod, args, kws)
    return impl, args


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate._get_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4e27d07b214ca16d6e8ed88f70d886b6b095e160d8f77f8df369dd4ed2eb3fae':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate._get_impl has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate._get_impl = (
    _overload_template_get_impl)


def trim_empty_parfor_branches(parfor):
    sly__nur = False
    blocks = parfor.loop_body.copy()
    for label, block in blocks.items():
        if len(block.body):
            kbxo__jnov = block.body[-1]
            if isinstance(kbxo__jnov, ir.Branch):
                if len(blocks[kbxo__jnov.truebr].body) == 1 and len(blocks[
                    kbxo__jnov.falsebr].body) == 1:
                    fyvcf__dywcu = blocks[kbxo__jnov.truebr].body[0]
                    qyzl__uokeq = blocks[kbxo__jnov.falsebr].body[0]
                    if isinstance(fyvcf__dywcu, ir.Jump) and isinstance(
                        qyzl__uokeq, ir.Jump
                        ) and fyvcf__dywcu.target == qyzl__uokeq.target:
                        parfor.loop_body[label].body[-1] = ir.Jump(fyvcf__dywcu
                            .target, kbxo__jnov.loc)
                        sly__nur = True
                elif len(blocks[kbxo__jnov.truebr].body) == 1:
                    fyvcf__dywcu = blocks[kbxo__jnov.truebr].body[0]
                    if isinstance(fyvcf__dywcu, ir.Jump
                        ) and fyvcf__dywcu.target == kbxo__jnov.falsebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(fyvcf__dywcu
                            .target, kbxo__jnov.loc)
                        sly__nur = True
                elif len(blocks[kbxo__jnov.falsebr].body) == 1:
                    qyzl__uokeq = blocks[kbxo__jnov.falsebr].body[0]
                    if isinstance(qyzl__uokeq, ir.Jump
                        ) and qyzl__uokeq.target == kbxo__jnov.truebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(qyzl__uokeq
                            .target, kbxo__jnov.loc)
                        sly__nur = True
    return sly__nur


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        mstsx__xba = find_topo_order(parfor.loop_body)
    rqlbw__ptptw = mstsx__xba[0]
    eksr__wxeo = {}
    _update_parfor_get_setitems(parfor.loop_body[rqlbw__ptptw].body, parfor
        .index_var, alias_map, eksr__wxeo, lives_n_aliases)
    viypx__jsl = set(eksr__wxeo.keys())
    for rnf__jvvs in mstsx__xba:
        if rnf__jvvs == rqlbw__ptptw:
            continue
        for stmt in parfor.loop_body[rnf__jvvs].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            nfeyh__lrcu = set(wug__wyq.name for wug__wyq in stmt.list_vars())
            irjel__viv = nfeyh__lrcu & viypx__jsl
            for a in irjel__viv:
                eksr__wxeo.pop(a, None)
    for rnf__jvvs in mstsx__xba:
        if rnf__jvvs == rqlbw__ptptw:
            continue
        block = parfor.loop_body[rnf__jvvs]
        jfinq__zea = eksr__wxeo.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            jfinq__zea, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    ghir__zfnxj = max(blocks.keys())
    sjhm__dgw, zim__fxh = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    pyag__zvb = ir.Jump(sjhm__dgw, ir.Loc('parfors_dummy', -1))
    blocks[ghir__zfnxj].body.append(pyag__zvb)
    dezf__jxv = compute_cfg_from_blocks(blocks)
    ctl__nxs = compute_use_defs(blocks)
    uzyk__xqt = compute_live_map(dezf__jxv, blocks, ctl__nxs.usemap,
        ctl__nxs.defmap)
    alias_set = set(alias_map.keys())
    for label, block in blocks.items():
        smfx__eteh = []
        jmc__joio = {wug__wyq.name for wug__wyq in block.terminator.list_vars()
            }
        for qysg__hae, faia__vxme in dezf__jxv.successors(label):
            jmc__joio |= uzyk__xqt[qysg__hae]
        for stmt in reversed(block.body):
            hcuf__mlt = jmc__joio & alias_set
            for wug__wyq in hcuf__mlt:
                jmc__joio |= alias_map[wug__wyq]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in jmc__joio and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                opmq__pkn = guard(find_callname, func_ir, stmt.value)
                if opmq__pkn == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in jmc__joio and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            jmc__joio |= {wug__wyq.name for wug__wyq in stmt.list_vars()}
            smfx__eteh.append(stmt)
        smfx__eteh.reverse()
        block.body = smfx__eteh
    typemap.pop(zim__fxh.name)
    blocks[ghir__zfnxj].body.pop()
    sly__nur = True
    while sly__nur:
        """
        Process parfor body recursively.
        Note that this is the only place in this function that uses the
        argument lives instead of lives_n_aliases.  The former does not
        include the aliases of live variables but only the live variable
        names themselves.  See a comment in this function for how that
        is used.
        """
        remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map,
            func_ir, typemap)
        simplify_parfor_body_CFG(func_ir.blocks)
        sly__nur = trim_empty_parfor_branches(parfor)
    ijzy__nwmin = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        ijzy__nwmin &= len(block.body) == 0
    if ijzy__nwmin:
        return None
    return parfor


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.remove_dead_parfor)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1c9b008a7ead13e988e1efe67618d8f87f0b9f3d092cc2cd6bfcd806b1fdb859':
        warnings.warn('remove_dead_parfor has changed')
numba.parfors.parfor.remove_dead_parfor = remove_dead_parfor
numba.core.ir_utils.remove_dead_extensions[numba.parfors.parfor.Parfor
    ] = remove_dead_parfor


def simplify_parfor_body_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.parfors.parfor import Parfor
    teoxv__ryw = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                teoxv__ryw += 1
                parfor = stmt
                iibq__kap = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = iibq__kap.scope
                loc = ir.Loc('parfors_dummy', -1)
                jvsl__rpgg = ir.Var(scope, mk_unique_var('$const'), loc)
                iibq__kap.body.append(ir.Assign(ir.Const(0, loc),
                    jvsl__rpgg, loc))
                iibq__kap.body.append(ir.Return(jvsl__rpgg, loc))
                dezf__jxv = compute_cfg_from_blocks(parfor.loop_body)
                for cal__cyrf in dezf__jxv.dead_nodes():
                    del parfor.loop_body[cal__cyrf]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                iibq__kap = parfor.loop_body[max(parfor.loop_body.keys())]
                iibq__kap.body.pop()
                iibq__kap.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return teoxv__ryw


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def simplify_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import merge_adjacent_blocks, rename_labels
    dezf__jxv = compute_cfg_from_blocks(blocks)

    def find_single_branch(label):
        block = blocks[label]
        return len(block.body) == 1 and isinstance(block.body[0], ir.Branch
            ) and label != dezf__jxv.entry_point()
    dii__wlm = list(filter(find_single_branch, blocks.keys()))
    cyh__dviw = set()
    for label in dii__wlm:
        inst = blocks[label].body[0]
        ygm__ubo = dezf__jxv.predecessors(label)
        rxlf__wgtd = True
        for pxus__nkn, rrdxv__lsvl in ygm__ubo:
            block = blocks[pxus__nkn]
            if isinstance(block.body[-1], ir.Jump):
                block.body[-1] = copy.copy(inst)
            else:
                rxlf__wgtd = False
        if rxlf__wgtd:
            cyh__dviw.add(label)
    for label in cyh__dviw:
        del blocks[label]
    merge_adjacent_blocks(blocks)
    return rename_labels(blocks)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.simplify_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '0b3f2add05e5691155f08fc5945956d5cca5e068247d52cff8efb161b76388b7':
        warnings.warn('numba.core.ir_utils.simplify_CFG has changed')
numba.core.ir_utils.simplify_CFG = simplify_CFG


def _lifted_compile(self, sig):
    import numba.core.event as ev
    from numba.core import compiler, sigutils
    from numba.core.compiler_lock import global_compiler_lock
    from numba.core.ir_utils import remove_dels
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        with self._compiling_counter:
            flags = self.flags
            args, return_type = sigutils.normalize_signature(sig)
            wtt__feosa = self.overloads.get(tuple(args))
            if wtt__feosa is not None:
                return wtt__feosa.entry_point
            self._pre_compile(args, return_type, flags)
            jstva__vhtcg = self.func_ir
            ytz__jjpij = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=ytz__jjpij):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=jstva__vhtcg, args=
                    args, return_type=return_type, flags=flags, locals=self
                    .locals, lifted=(), lifted_from=self.lifted_from,
                    is_lifted_loop=True)
                if cres.typing_error is not None and not flags.enable_pyobject:
                    raise cres.typing_error
                self.add_overload(cres)
            remove_dels(self.func_ir.blocks)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.LiftedCode.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1351ebc5d8812dc8da167b30dad30eafb2ca9bf191b49aaed6241c21e03afff1':
        warnings.warn('numba.core.dispatcher.LiftedCode.compile has changed')
numba.core.dispatcher.LiftedCode.compile = _lifted_compile


def compile_ir(typingctx, targetctx, func_ir, args, return_type, flags,
    locals, lifted=(), lifted_from=None, is_lifted_loop=False, library=None,
    pipeline_class=Compiler):
    if is_lifted_loop:
        wgrsr__nptsa = copy.deepcopy(flags)
        wgrsr__nptsa.no_rewrites = True

        def compile_local(the_ir, the_flags):
            lxfi__dkq = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return lxfi__dkq.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        jtu__gjl = compile_local(func_ir, wgrsr__nptsa)
        wfytg__uuuqu = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    wfytg__uuuqu = compile_local(func_ir, flags)
                except Exception as qfeu__tir:
                    pass
        if wfytg__uuuqu is not None:
            cres = wfytg__uuuqu
        else:
            cres = jtu__gjl
        return cres
    else:
        lxfi__dkq = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return lxfi__dkq.compile_ir(func_ir=func_ir, lifted=lifted,
            lifted_from=lifted_from)


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.compile_ir)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c48ce5493f4c43326e8cbdd46f3ea038b2b9045352d9d25894244798388e5e5b':
        warnings.warn('numba.core.compiler.compile_ir has changed')
numba.core.compiler.compile_ir = compile_ir


def make_constant_array(self, builder, typ, ary):
    import math
    from llvmlite import ir as lir
    lid__pnvvr = self.get_data_type(typ.dtype)
    uid__ohbxn = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        uid__ohbxn):
        bow__ubbfd = ary.ctypes.data
        deqs__uli = self.add_dynamic_addr(builder, bow__ubbfd, info=str(
            type(bow__ubbfd)))
        ykfv__sul = self.add_dynamic_addr(builder, id(ary), info=str(type(ary))
            )
        self.global_arrays.append(ary)
    else:
        pwxd__dsnn = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            pwxd__dsnn = pwxd__dsnn.view('int64')
        val = bytearray(pwxd__dsnn.data)
        rsldc__tbhxp = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)),
            val)
        deqs__uli = cgutils.global_constant(builder, '.const.array.data',
            rsldc__tbhxp)
        deqs__uli.align = self.get_abi_alignment(lid__pnvvr)
        ykfv__sul = None
    fbgl__ycj = self.get_value_type(types.intp)
    qim__phoz = [self.get_constant(types.intp, gst__ftb) for gst__ftb in
        ary.shape]
    zxsdu__wev = lir.Constant(lir.ArrayType(fbgl__ycj, len(qim__phoz)),
        qim__phoz)
    yms__nlsq = [self.get_constant(types.intp, gst__ftb) for gst__ftb in
        ary.strides]
    yrj__iuh = lir.Constant(lir.ArrayType(fbgl__ycj, len(yms__nlsq)), yms__nlsq
        )
    dvrkb__axb = self.get_constant(types.intp, ary.dtype.itemsize)
    xkpjx__xkfql = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        xkpjx__xkfql, dvrkb__axb, deqs__uli.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), zxsdu__wev, yrj__iuh])


if _check_numba_change:
    lines = inspect.getsource(numba.core.base.BaseContext.make_constant_array)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5721b5360b51f782f79bd794f7bf4d48657911ecdc05c30db22fd55f15dad821':
        warnings.warn(
            'numba.core.base.BaseContext.make_constant_array has changed')
numba.core.base.BaseContext.make_constant_array = make_constant_array


def _define_atomic_inc_dec(module, op, ordering):
    from llvmlite import ir as lir
    from numba.core.runtime.nrtdynmod import _word_type
    ylig__eta = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    ceetf__rcs = lir.Function(module, ylig__eta, name='nrt_atomic_{0}'.
        format(op))
    [vcss__fspx] = ceetf__rcs.args
    ycd__mkwna = ceetf__rcs.append_basic_block()
    builder = lir.IRBuilder(ycd__mkwna)
    pjnxq__oytu = lir.Constant(_word_type, 1)
    if False:
        kmwk__gall = builder.atomic_rmw(op, vcss__fspx, pjnxq__oytu,
            ordering=ordering)
        res = getattr(builder, op)(kmwk__gall, pjnxq__oytu)
        builder.ret(res)
    else:
        kmwk__gall = builder.load(vcss__fspx)
        bqj__tanxk = getattr(builder, op)(kmwk__gall, pjnxq__oytu)
        mrbo__qzdnp = builder.icmp_signed('!=', kmwk__gall, lir.Constant(
            kmwk__gall.type, -1))
        with cgutils.if_likely(builder, mrbo__qzdnp):
            builder.store(bqj__tanxk, vcss__fspx)
        builder.ret(bqj__tanxk)
    return ceetf__rcs


if _check_numba_change:
    lines = inspect.getsource(numba.core.runtime.nrtdynmod.
        _define_atomic_inc_dec)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9cc02c532b2980b6537b702f5608ea603a1ff93c6d3c785ae2cf48bace273f48':
        warnings.warn(
            'numba.core.runtime.nrtdynmod._define_atomic_inc_dec has changed')
numba.core.runtime.nrtdynmod._define_atomic_inc_dec = _define_atomic_inc_dec


def NativeLowering_run_pass(self, state):
    from llvmlite import binding as llvm
    from numba.core import funcdesc, lowering
    from numba.core.typed_passes import fallback_context
    if state.library is None:
        zdg__qiox = state.targetctx.codegen()
        state.library = zdg__qiox.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    dbxfw__junvi = state.func_ir
    typemap = state.typemap
    oqesc__mvun = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    ards__ldk = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            dbxfw__junvi, typemap, oqesc__mvun, calltypes, mangler=
            targetctx.mangler, inline=flags.forceinline, noalias=flags.
            noalias, abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            fvkyb__fmwk = lowering.Lower(targetctx, library, fndesc,
                dbxfw__junvi, metadata=metadata)
            fvkyb__fmwk.lower()
            if not flags.no_cpython_wrapper:
                fvkyb__fmwk.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(oqesc__mvun, (types.Optional, types.
                        Generator)):
                        pass
                    else:
                        fvkyb__fmwk.create_cfunc_wrapper()
            env = fvkyb__fmwk.env
            jei__geww = fvkyb__fmwk.call_helper
            del fvkyb__fmwk
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, jei__geww, cfunc=None, env=env)
        else:
            xgtqm__tby = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(xgtqm__tby, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, jei__geww, cfunc=xgtqm__tby,
                env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        cjbi__lmz = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = cjbi__lmz - ards__ldk
        metadata['llvm_pass_timings'] = library.recorded_timings
    return True


if _check_numba_change:
    lines = inspect.getsource(numba.core.typed_passes.NativeLowering.run_pass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a777ce6ce1bb2b1cbaa3ac6c2c0e2adab69a9c23888dff5f1cbb67bfb176b5de':
        warnings.warn(
            'numba.core.typed_passes.NativeLowering.run_pass has changed')
numba.core.typed_passes.NativeLowering.run_pass = NativeLowering_run_pass


def _python_list_to_native(typ, obj, c, size, listptr, errorptr):
    from llvmlite import ir as lir
    from numba.core.boxing import _NumbaTypeHelper
    from numba.cpython import listobj

    def check_element_type(nth, itemobj, expected_typobj):
        hkro__qqltt = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, hkro__qqltt),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            sifl__hzp.do_break()
        wfuzf__fqnm = c.builder.icmp_signed('!=', hkro__qqltt, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(wfuzf__fqnm, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, hkro__qqltt)
                c.pyapi.decref(hkro__qqltt)
                sifl__hzp.do_break()
        c.pyapi.decref(hkro__qqltt)
    iqtb__ksf, list = listobj.ListInstance.allocate_ex(c.context, c.builder,
        typ, size)
    with c.builder.if_else(iqtb__ksf, likely=True) as (xctt__txg, kzq__qxi):
        with xctt__txg:
            list.size = size
            jzbma__xbfu = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                jzbma__xbfu), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        jzbma__xbfu))
                    with cgutils.for_range(c.builder, size) as sifl__hzp:
                        itemobj = c.pyapi.list_getitem(obj, sifl__hzp.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        kxnk__mfsj = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(kxnk__mfsj.is_error, likely=
                            False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            sifl__hzp.do_break()
                        list.setitem(sifl__hzp.index, kxnk__mfsj.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with kzq__qxi:
            c.builder.store(cgutils.true_bit, errorptr)
    with c.builder.if_then(c.builder.load(errorptr)):
        c.context.nrt.decref(c.builder, typ, list.value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.boxing._python_list_to_native)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f8e546df8b07adfe74a16b6aafb1d4fddbae7d3516d7944b3247cc7c9b7ea88a':
        warnings.warn('numba.core.boxing._python_list_to_native has changed')
numba.core.boxing._python_list_to_native = _python_list_to_native


def make_string_from_constant(context, builder, typ, literal_string):
    from llvmlite import ir as lir
    from numba.cpython.hashing import _Py_hash_t
    from numba.cpython.unicode import compile_time_get_string_data
    nyld__wwzqy, ijjm__rbvt, zhru__ewo, ozt__hnx, eur__cxvi = (
        compile_time_get_string_data(literal_string))
    nsuau__mraz = builder.module
    gv = context.insert_const_bytes(nsuau__mraz, nyld__wwzqy)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        ijjm__rbvt), context.get_constant(types.int32, zhru__ewo), context.
        get_constant(types.uint32, ozt__hnx), context.get_constant(
        _Py_hash_t, -1), context.get_constant_null(types.MemInfoPointer(
        types.voidptr)), context.get_constant_null(types.pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    veu__zovx = None
    if isinstance(shape, types.Integer):
        veu__zovx = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(gst__ftb, (types.Integer, types.IntEnumMember)) for
            gst__ftb in shape):
            veu__zovx = len(shape)
    return veu__zovx


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.parse_shape)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e62e3ff09d36df5ac9374055947d6a8be27160ce32960d3ef6cb67f89bd16429':
        warnings.warn('numba.core.typing.npydecl.parse_shape has changed')
numba.core.typing.npydecl.parse_shape = parse_shape


def _get_names(self, obj):
    if isinstance(obj, ir.Var) or isinstance(obj, str):
        name = obj if isinstance(obj, str) else obj.name
        if name not in self.typemap:
            return name,
        typ = self.typemap[name]
        if isinstance(typ, (types.BaseTuple, types.ArrayCompatible)):
            veu__zovx = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if veu__zovx == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(veu__zovx))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            tetf__cktc = self._get_names(x)
            if len(tetf__cktc) != 0:
                return tetf__cktc[0]
            return tetf__cktc
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    tetf__cktc = self._get_names(obj)
    if len(tetf__cktc) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(tetf__cktc[0])


def get_equiv_set(self, obj):
    tetf__cktc = self._get_names(obj)
    if len(tetf__cktc) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(tetf__cktc[0])


if _check_numba_change:
    for name, orig, new, hash in ((
        'numba.parfors.array_analysis.ShapeEquivSet._get_names', numba.
        parfors.array_analysis.ShapeEquivSet._get_names, _get_names,
        '8c9bf136109028d5445fd0a82387b6abeb70c23b20b41e2b50c34ba5359516ee'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const',
        numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const,
        get_equiv_const,
        'bef410ca31a9e29df9ee74a4a27d339cc332564e4a237828b8a4decf625ce44e'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set', numba.
        parfors.array_analysis.ShapeEquivSet.get_equiv_set, get_equiv_set,
        'ec936d340c488461122eb74f28a28b88227cb1f1bca2b9ba3c19258cfe1eb40a')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
numba.parfors.array_analysis.ShapeEquivSet._get_names = _get_names
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const = get_equiv_const
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set = get_equiv_set


def raise_on_unsupported_feature(func_ir, typemap):
    import numpy
    tmu__qms = []
    for gopa__egm in func_ir.arg_names:
        if gopa__egm in typemap and isinstance(typemap[gopa__egm], types.
            containers.UniTuple) and typemap[gopa__egm].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(gopa__egm))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for fss__dmr in func_ir.blocks.values():
        for stmt in fss__dmr.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    ulo__alax = getattr(val, 'code', None)
                    if ulo__alax is not None:
                        if getattr(val, 'closure', None) is not None:
                            tnvwa__pxvik = (
                                '<creating a function from a closure>')
                            iphge__qztz = ''
                        else:
                            tnvwa__pxvik = ulo__alax.co_name
                            iphge__qztz = '(%s) ' % tnvwa__pxvik
                    else:
                        tnvwa__pxvik = '<could not ascertain use case>'
                        iphge__qztz = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (tnvwa__pxvik, iphge__qztz))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                rak__mziw = False
                if isinstance(val, pytypes.FunctionType):
                    rak__mziw = val in {numba.gdb, numba.gdb_init}
                if not rak__mziw:
                    rak__mziw = getattr(val, '_name', '') == 'gdb_internal'
                if rak__mziw:
                    tmu__qms.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    sox__jjzot = func_ir.get_definition(var)
                    zrl__vfd = guard(find_callname, func_ir, sox__jjzot)
                    if zrl__vfd and zrl__vfd[1] == 'numpy':
                        ty = getattr(numpy, zrl__vfd[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    kzog__vwc = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(kzog__vwc), loc=stmt.loc)
            if isinstance(stmt.value, ir.Global):
                ty = typemap[stmt.target.name]
                msg = (
                    "The use of a %s type, assigned to variable '%s' in globals, is not supported as globals are considered compile-time constants and there is no known way to compile a %s type as a constant."
                    )
                if isinstance(ty, types.ListType):
                    raise TypingError(msg % (ty, stmt.value.name, ty), loc=
                        stmt.loc)
            if isinstance(stmt.value, ir.Yield) and not func_ir.is_generator:
                msg = 'The use of generator expressions is unsupported.'
                raise errors.UnsupportedError(msg, loc=stmt.loc)
    if len(tmu__qms) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        vsgz__hrsmj = '\n'.join([x.strformat() for x in tmu__qms])
        raise errors.UnsupportedError(msg % vsgz__hrsmj)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.raise_on_unsupported_feature)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '237a4fe8395a40899279c718bc3754102cd2577463ef2f48daceea78d79b2d5e':
        warnings.warn(
            'numba.core.ir_utils.raise_on_unsupported_feature has changed')
numba.core.ir_utils.raise_on_unsupported_feature = raise_on_unsupported_feature
numba.core.typed_passes.raise_on_unsupported_feature = (
    raise_on_unsupported_feature)


@typeof_impl.register(dict)
def _typeof_dict(val, c):
    if len(val) == 0:
        raise ValueError('Cannot type empty dict')
    myok__jtrvx, wug__wyq = next(iter(val.items()))
    ggjbp__ldvr = typeof_impl(myok__jtrvx, c)
    vqzbm__eab = typeof_impl(wug__wyq, c)
    if ggjbp__ldvr is None or vqzbm__eab is None:
        raise ValueError(
            f'Cannot type dict element type {type(myok__jtrvx)}, {type(wug__wyq)}'
            )
    return types.DictType(ggjbp__ldvr, vqzbm__eab)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    ldz__iuk = cgutils.alloca_once_value(c.builder, val)
    fzq__yftfo = c.pyapi.object_hasattr_string(val, '_opaque')
    jngg__gtcb = c.builder.icmp_unsigned('==', fzq__yftfo, lir.Constant(
        fzq__yftfo.type, 0))
    skaai__zwbh = typ.key_type
    eamny__bxjou = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(skaai__zwbh, eamny__bxjou)

    def copy_dict(out_dict, in_dict):
        for myok__jtrvx, wug__wyq in in_dict.items():
            out_dict[myok__jtrvx] = wug__wyq
    with c.builder.if_then(jngg__gtcb):
        qeh__zioat = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        suf__vygx = c.pyapi.call_function_objargs(qeh__zioat, [])
        nrbz__aevym = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(nrbz__aevym, [suf__vygx, val])
        c.builder.store(suf__vygx, ldz__iuk)
    val = c.builder.load(ldz__iuk)
    yexng__sccs = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    opuwz__lxywd = c.pyapi.object_type(val)
    mnfx__qcydz = c.builder.icmp_unsigned('==', opuwz__lxywd, yexng__sccs)
    with c.builder.if_else(mnfx__qcydz) as (bqqo__yxfr, hlxko__zal):
        with bqqo__yxfr:
            wlgn__gip = c.pyapi.object_getattr_string(val, '_opaque')
            pmbkz__fwar = types.MemInfoPointer(types.voidptr)
            kxnk__mfsj = c.unbox(pmbkz__fwar, wlgn__gip)
            mi = kxnk__mfsj.value
            fbdn__kvtv = pmbkz__fwar, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *fbdn__kvtv)
            zdb__xmqd = context.get_constant_null(fbdn__kvtv[1])
            args = mi, zdb__xmqd
            kiqo__dxz, mtxwb__tfxd = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, mtxwb__tfxd)
            c.pyapi.decref(wlgn__gip)
            bjn__lem = c.builder.basic_block
        with hlxko__zal:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", opuwz__lxywd, yexng__sccs)
            eso__ndk = c.builder.basic_block
    pomd__cabn = c.builder.phi(mtxwb__tfxd.type)
    adi__jwfq = c.builder.phi(kiqo__dxz.type)
    pomd__cabn.add_incoming(mtxwb__tfxd, bjn__lem)
    pomd__cabn.add_incoming(mtxwb__tfxd.type(None), eso__ndk)
    adi__jwfq.add_incoming(kiqo__dxz, bjn__lem)
    adi__jwfq.add_incoming(cgutils.true_bit, eso__ndk)
    c.pyapi.decref(yexng__sccs)
    c.pyapi.decref(opuwz__lxywd)
    with c.builder.if_then(jngg__gtcb):
        c.pyapi.decref(val)
    return NativeValue(pomd__cabn, is_error=adi__jwfq)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype


def op_DICT_UPDATE_byteflow(self, state, inst):
    value = state.pop()
    index = inst.arg
    target = state.peek(index)
    updatevar = state.make_temp()
    res = state.make_temp()
    state.append(inst, target=target, value=value, updatevar=updatevar, res=res
        )


if _check_numba_change:
    if hasattr(numba.core.byteflow.TraceRunner, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_DICT_UPDATE has changed')
numba.core.byteflow.TraceRunner.op_DICT_UPDATE = op_DICT_UPDATE_byteflow


def op_DICT_UPDATE_interpreter(self, inst, target, value, updatevar, res):
    from numba.core import ir
    target = self.get(target)
    value = self.get(value)
    axlzv__ifun = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=axlzv__ifun, name=updatevar)
    zarrr__rmenj = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc
        )
    self.store(value=zarrr__rmenj, name=res)


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_DICT_UPDATE has changed')
numba.core.interpreter.Interpreter.op_DICT_UPDATE = op_DICT_UPDATE_interpreter


@numba.extending.overload_method(numba.core.types.DictType, 'update')
def ol_dict_update(d, other):
    if not isinstance(d, numba.core.types.DictType):
        return
    if not isinstance(other, numba.core.types.DictType):
        return

    def impl(d, other):
        for myok__jtrvx, wug__wyq in other.items():
            d[myok__jtrvx] = wug__wyq
    return impl


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'ol_dict_update'):
        warnings.warn('numba.typed.dictobject.ol_dict_update has changed')


def op_CALL_FUNCTION_EX_byteflow(self, state, inst):
    from numba.core.utils import PYVERSION
    if inst.arg & 1 and PYVERSION != (3, 10):
        errmsg = 'CALL_FUNCTION_EX with **kwargs not supported'
        raise errors.UnsupportedError(errmsg)
    if inst.arg & 1:
        varkwarg = state.pop()
    else:
        varkwarg = None
    vararg = state.pop()
    func = state.pop()
    res = state.make_temp()
    state.append(inst, func=func, vararg=vararg, varkwarg=varkwarg, res=res)
    state.push(res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.byteflow.TraceRunner.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '349e7cfd27f5dab80fe15a7728c5f098f3f225ba8512d84331e39d01e863c6d4':
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX has changed')
numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_byteflow)


def op_CALL_FUNCTION_EX_interpreter(self, inst, func, vararg, varkwarg, res):
    func = self.get(func)
    vararg = self.get(vararg)
    if varkwarg is not None:
        varkwarg = self.get(varkwarg)
    iphge__qztz = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(iphge__qztz, res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.interpreter.Interpreter.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84846e5318ab7ccc8f9abaae6ab9e0ca879362648196f9d4b0ffb91cf2e01f5d':
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX has changed'
            )
numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_interpreter)


@classmethod
def ir_expr_call(cls, func, args, kws, loc, vararg=None, varkwarg=None,
    target=None):
    assert isinstance(func, ir.Var)
    assert isinstance(loc, ir.Loc)
    op = 'call'
    return cls(op=op, loc=loc, func=func, args=args, kws=kws, vararg=vararg,
        varkwarg=varkwarg, target=target)


if _check_numba_change:
    lines = inspect.getsource(ir.Expr.call)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '665601d0548d4f648d454492e542cb8aa241107a8df6bc68d0eec664c9ada738':
        warnings.warn('ir.Expr.call has changed')
ir.Expr.call = ir_expr_call


@staticmethod
def define_untyped_pipeline(state, name='untyped'):
    from numba.core.compiler_machinery import PassManager
    from numba.core.untyped_passes import DeadBranchPrune, FindLiterallyCalls, FixupArgs, GenericRewrites, InlineClosureLikes, InlineInlinables, IRProcessing, LiteralPropagationSubPipelinePass, LiteralUnroll, MakeFunctionToJitFunction, ReconstructSSA, RewriteSemanticConstants, TranslateByteCode, WithLifting
    from numba.core.utils import PYVERSION
    oubh__afncw = PassManager(name)
    if state.func_ir is None:
        oubh__afncw.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            oubh__afncw.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        oubh__afncw.add_pass(FixupArgs, 'fix up args')
    oubh__afncw.add_pass(IRProcessing, 'processing IR')
    oubh__afncw.add_pass(WithLifting, 'Handle with contexts')
    oubh__afncw.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        oubh__afncw.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        oubh__afncw.add_pass(DeadBranchPrune, 'dead branch pruning')
        oubh__afncw.add_pass(GenericRewrites, 'nopython rewrites')
    oubh__afncw.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    oubh__afncw.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        oubh__afncw.add_pass(DeadBranchPrune, 'dead branch pruning')
    oubh__afncw.add_pass(FindLiterallyCalls, 'find literally calls')
    oubh__afncw.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        oubh__afncw.add_pass(ReconstructSSA, 'ssa')
    oubh__afncw.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    oubh__afncw.finalize()
    return oubh__afncw


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fc5a0665658cc30588a78aca984ac2d323d5d3a45dce538cc62688530c772896':
        warnings.warn(
            'numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline has changed'
            )
numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline = (
    define_untyped_pipeline)


def mul_list_generic(self, args, kws):
    a, droq__lpvq = args
    if isinstance(a, types.List) and isinstance(droq__lpvq, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(droq__lpvq, types.List):
        return signature(droq__lpvq, types.intp, droq__lpvq)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.listdecl.MulList.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '95882385a8ffa67aa576e8169b9ee6b3197e0ad3d5def4b47fa65ce8cd0f1575':
        warnings.warn('numba.core.typing.listdecl.MulList.generic has changed')
numba.core.typing.listdecl.MulList.generic = mul_list_generic


@lower_builtin(operator.mul, types.Integer, types.List)
def list_mul(context, builder, sig, args):
    from llvmlite import ir as lir
    from numba.core.imputils import impl_ret_new_ref
    from numba.cpython.listobj import ListInstance
    if isinstance(sig.args[0], types.List):
        fddxi__xdth, tywp__noorb = 0, 1
    else:
        fddxi__xdth, tywp__noorb = 1, 0
    rwzv__zluk = ListInstance(context, builder, sig.args[fddxi__xdth], args
        [fddxi__xdth])
    jdlvs__uth = rwzv__zluk.size
    zkm__sbjg = args[tywp__noorb]
    jzbma__xbfu = lir.Constant(zkm__sbjg.type, 0)
    zkm__sbjg = builder.select(cgutils.is_neg_int(builder, zkm__sbjg),
        jzbma__xbfu, zkm__sbjg)
    xkpjx__xkfql = builder.mul(zkm__sbjg, jdlvs__uth)
    yeglx__qksde = ListInstance.allocate(context, builder, sig.return_type,
        xkpjx__xkfql)
    yeglx__qksde.size = xkpjx__xkfql
    with cgutils.for_range_slice(builder, jzbma__xbfu, xkpjx__xkfql,
        jdlvs__uth, inc=True) as (cepil__zqw, _):
        with cgutils.for_range(builder, jdlvs__uth) as sifl__hzp:
            value = rwzv__zluk.getitem(sifl__hzp.index)
            yeglx__qksde.setitem(builder.add(sifl__hzp.index, cepil__zqw),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, yeglx__qksde
        .value)


def unify_pairs(self, first, second):
    from numba.core.typeconv import Conversion
    if first == second:
        return first
    if first is types.undefined:
        return second
    elif second is types.undefined:
        return first
    if first is types.unknown or second is types.unknown:
        return types.unknown
    glqr__sopr = first.unify(self, second)
    if glqr__sopr is not None:
        return glqr__sopr
    glqr__sopr = second.unify(self, first)
    if glqr__sopr is not None:
        return glqr__sopr
    aylny__bbr = self.can_convert(fromty=first, toty=second)
    if aylny__bbr is not None and aylny__bbr <= Conversion.safe:
        return second
    aylny__bbr = self.can_convert(fromty=second, toty=first)
    if aylny__bbr is not None and aylny__bbr <= Conversion.safe:
        return first
    if isinstance(first, types.Literal) or isinstance(second, types.Literal):
        first = types.unliteral(first)
        second = types.unliteral(second)
        return self.unify_pairs(first, second)
    return None


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.unify_pairs
        )
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f0eaf4cfdf1537691de26efd24d7e320f7c3f10d35e9aefe70cb946b3be0008c':
        warnings.warn(
            'numba.core.typing.context.BaseContext.unify_pairs has changed')
numba.core.typing.context.BaseContext.unify_pairs = unify_pairs


def _native_set_to_python_list(typ, payload, c):
    from llvmlite import ir
    xkpjx__xkfql = payload.used
    listobj = c.pyapi.list_new(xkpjx__xkfql)
    iqtb__ksf = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(iqtb__ksf, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(
            xkpjx__xkfql.type, 0))
        with payload._iterate() as sifl__hzp:
            i = c.builder.load(index)
            item = sifl__hzp.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return iqtb__ksf, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    kxb__mkd = h.type
    rbw__ojpv = self.mask
    dtype = self._ty.dtype
    bkt__dyuzq = context.typing_context
    fnty = bkt__dyuzq.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(bkt__dyuzq, (dtype, dtype), {})
    kowm__xxms = context.get_function(fnty, sig)
    oucp__qiv = ir.Constant(kxb__mkd, 1)
    dot__arip = ir.Constant(kxb__mkd, 5)
    wbetg__gdyj = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, rbw__ojpv))
    if for_insert:
        pzdfj__ocao = rbw__ojpv.type(-1)
        afqz__prwe = cgutils.alloca_once_value(builder, pzdfj__ocao)
    qczpa__wlki = builder.append_basic_block('lookup.body')
    rhy__tzxej = builder.append_basic_block('lookup.found')
    zbi__crk = builder.append_basic_block('lookup.not_found')
    kksb__cyeb = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        vucb__wslce = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, vucb__wslce)):
            odr__nht = kowm__xxms(builder, (item, entry.key))
            with builder.if_then(odr__nht):
                builder.branch(rhy__tzxej)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, vucb__wslce)):
            builder.branch(zbi__crk)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, vucb__wslce)):
                fpnac__scv = builder.load(afqz__prwe)
                fpnac__scv = builder.select(builder.icmp_unsigned('==',
                    fpnac__scv, pzdfj__ocao), i, fpnac__scv)
                builder.store(fpnac__scv, afqz__prwe)
    with cgutils.for_range(builder, ir.Constant(kxb__mkd, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, oucp__qiv)
        i = builder.and_(i, rbw__ojpv)
        builder.store(i, index)
    builder.branch(qczpa__wlki)
    with builder.goto_block(qczpa__wlki):
        i = builder.load(index)
        check_entry(i)
        pxus__nkn = builder.load(wbetg__gdyj)
        pxus__nkn = builder.lshr(pxus__nkn, dot__arip)
        i = builder.add(oucp__qiv, builder.mul(i, dot__arip))
        i = builder.and_(rbw__ojpv, builder.add(i, pxus__nkn))
        builder.store(i, index)
        builder.store(pxus__nkn, wbetg__gdyj)
        builder.branch(qczpa__wlki)
    with builder.goto_block(zbi__crk):
        if for_insert:
            i = builder.load(index)
            fpnac__scv = builder.load(afqz__prwe)
            i = builder.select(builder.icmp_unsigned('==', fpnac__scv,
                pzdfj__ocao), i, fpnac__scv)
            builder.store(i, index)
        builder.branch(kksb__cyeb)
    with builder.goto_block(rhy__tzxej):
        builder.branch(kksb__cyeb)
    builder.position_at_end(kksb__cyeb)
    rak__mziw = builder.phi(ir.IntType(1), 'found')
    rak__mziw.add_incoming(cgutils.true_bit, rhy__tzxej)
    rak__mziw.add_incoming(cgutils.false_bit, zbi__crk)
    return rak__mziw, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    sns__qkh = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    ovqag__xmbpn = payload.used
    oucp__qiv = ir.Constant(ovqag__xmbpn.type, 1)
    ovqag__xmbpn = payload.used = builder.add(ovqag__xmbpn, oucp__qiv)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, sns__qkh), likely=True):
        payload.fill = builder.add(payload.fill, oucp__qiv)
    if do_resize:
        self.upsize(ovqag__xmbpn)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    rak__mziw, i = payload._lookup(item, h, for_insert=True)
    ant__bnxab = builder.not_(rak__mziw)
    with builder.if_then(ant__bnxab):
        entry = payload.get_entry(i)
        sns__qkh = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        ovqag__xmbpn = payload.used
        oucp__qiv = ir.Constant(ovqag__xmbpn.type, 1)
        ovqag__xmbpn = payload.used = builder.add(ovqag__xmbpn, oucp__qiv)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, sns__qkh), likely=True):
            payload.fill = builder.add(payload.fill, oucp__qiv)
        if do_resize:
            self.upsize(ovqag__xmbpn)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    ovqag__xmbpn = payload.used
    oucp__qiv = ir.Constant(ovqag__xmbpn.type, 1)
    ovqag__xmbpn = payload.used = self._builder.sub(ovqag__xmbpn, oucp__qiv)
    if do_resize:
        self.downsize(ovqag__xmbpn)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    sxjaz__kqmt = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, sxjaz__kqmt)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    nhhp__netr = payload
    iqtb__ksf = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(iqtb__ksf), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with nhhp__netr._iterate() as sifl__hzp:
        entry = sifl__hzp.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(nhhp__netr.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as sifl__hzp:
        entry = sifl__hzp.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    iqtb__ksf = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(iqtb__ksf), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    iqtb__ksf = cgutils.alloca_once_value(builder, cgutils.true_bit)
    kxb__mkd = context.get_value_type(types.intp)
    jzbma__xbfu = ir.Constant(kxb__mkd, 0)
    oucp__qiv = ir.Constant(kxb__mkd, 1)
    hismg__nefl = context.get_data_type(types.SetPayload(self._ty))
    eyu__eanco = context.get_abi_sizeof(hismg__nefl)
    lzic__uggs = self._entrysize
    eyu__eanco -= lzic__uggs
    shkdf__smls, fpanx__utgl = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(kxb__mkd, lzic__uggs), ir.Constant(kxb__mkd,
        eyu__eanco))
    with builder.if_then(fpanx__utgl, likely=False):
        builder.store(cgutils.false_bit, iqtb__ksf)
    with builder.if_then(builder.load(iqtb__ksf), likely=True):
        if realloc:
            lbjan__gmt = self._set.meminfo
            vcss__fspx = context.nrt.meminfo_varsize_alloc(builder,
                lbjan__gmt, size=shkdf__smls)
            qjjgh__fsd = cgutils.is_null(builder, vcss__fspx)
        else:
            jmy__zwcn = _imp_dtor(context, builder.module, self._ty)
            lbjan__gmt = context.nrt.meminfo_new_varsize_dtor(builder,
                shkdf__smls, builder.bitcast(jmy__zwcn, cgutils.voidptr_t))
            qjjgh__fsd = cgutils.is_null(builder, lbjan__gmt)
        with builder.if_else(qjjgh__fsd, likely=False) as (tdwtw__atty,
            xctt__txg):
            with tdwtw__atty:
                builder.store(cgutils.false_bit, iqtb__ksf)
            with xctt__txg:
                if not realloc:
                    self._set.meminfo = lbjan__gmt
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, shkdf__smls, 255)
                payload.used = jzbma__xbfu
                payload.fill = jzbma__xbfu
                payload.finger = jzbma__xbfu
                fzrph__lwna = builder.sub(nentries, oucp__qiv)
                payload.mask = fzrph__lwna
    return builder.load(iqtb__ksf)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    iqtb__ksf = cgutils.alloca_once_value(builder, cgutils.true_bit)
    kxb__mkd = context.get_value_type(types.intp)
    jzbma__xbfu = ir.Constant(kxb__mkd, 0)
    oucp__qiv = ir.Constant(kxb__mkd, 1)
    hismg__nefl = context.get_data_type(types.SetPayload(self._ty))
    eyu__eanco = context.get_abi_sizeof(hismg__nefl)
    lzic__uggs = self._entrysize
    eyu__eanco -= lzic__uggs
    rbw__ojpv = src_payload.mask
    nentries = builder.add(oucp__qiv, rbw__ojpv)
    shkdf__smls = builder.add(ir.Constant(kxb__mkd, eyu__eanco), builder.
        mul(ir.Constant(kxb__mkd, lzic__uggs), nentries))
    with builder.if_then(builder.load(iqtb__ksf), likely=True):
        jmy__zwcn = _imp_dtor(context, builder.module, self._ty)
        lbjan__gmt = context.nrt.meminfo_new_varsize_dtor(builder,
            shkdf__smls, builder.bitcast(jmy__zwcn, cgutils.voidptr_t))
        qjjgh__fsd = cgutils.is_null(builder, lbjan__gmt)
        with builder.if_else(qjjgh__fsd, likely=False) as (tdwtw__atty,
            xctt__txg):
            with tdwtw__atty:
                builder.store(cgutils.false_bit, iqtb__ksf)
            with xctt__txg:
                self._set.meminfo = lbjan__gmt
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = jzbma__xbfu
                payload.mask = rbw__ojpv
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, lzic__uggs)
                with src_payload._iterate() as sifl__hzp:
                    context.nrt.incref(builder, self._ty.dtype, sifl__hzp.
                        entry.key)
    return builder.load(iqtb__ksf)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    opti__toplu = context.get_value_type(types.voidptr)
    gdao__zzird = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [opti__toplu, gdao__zzird,
        opti__toplu])
    zamap__llm = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=zamap__llm)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        uxb__hukrf = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer()
            )
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, uxb__hukrf)
        with payload._iterate() as sifl__hzp:
            entry = sifl__hzp.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    bhl__qjuk, = sig.args
    jpi__epq, = args
    shocr__vrd = numba.core.imputils.call_len(context, builder, bhl__qjuk,
        jpi__epq)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, shocr__vrd)
    with numba.core.imputils.for_iter(context, builder, bhl__qjuk, jpi__epq
        ) as sifl__hzp:
        inst.add(sifl__hzp.value)
        context.nrt.decref(builder, set_type.dtype, sifl__hzp.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    bhl__qjuk = sig.args[1]
    jpi__epq = args[1]
    shocr__vrd = numba.core.imputils.call_len(context, builder, bhl__qjuk,
        jpi__epq)
    if shocr__vrd is not None:
        mey__issh = builder.add(inst.payload.used, shocr__vrd)
        inst.upsize(mey__issh)
    with numba.core.imputils.for_iter(context, builder, bhl__qjuk, jpi__epq
        ) as sifl__hzp:
        oyg__hpaqe = context.cast(builder, sifl__hzp.value, bhl__qjuk.dtype,
            inst.dtype)
        inst.add(oyg__hpaqe)
        context.nrt.decref(builder, bhl__qjuk.dtype, sifl__hzp.value)
    if shocr__vrd is not None:
        inst.downsize(inst.payload.used)
    return context.get_dummy_value()


if _check_numba_change:
    for name, orig, hash in ((
        'numba.core.boxing._native_set_to_python_list', numba.core.boxing.
        _native_set_to_python_list,
        'b47f3d5e582c05d80899ee73e1c009a7e5121e7a660d42cb518bb86933f3c06f'),
        ('numba.cpython.setobj._SetPayload._lookup', numba.cpython.setobj.
        _SetPayload._lookup,
        'c797b5399d7b227fe4eea3a058b3d3103f59345699388afb125ae47124bee395'),
        ('numba.cpython.setobj.SetInstance._add_entry', numba.cpython.
        setobj.SetInstance._add_entry,
        'c5ed28a5fdb453f242e41907cb792b66da2df63282c17abe0b68fc46782a7f94'),
        ('numba.cpython.setobj.SetInstance._add_key', numba.cpython.setobj.
        SetInstance._add_key,
        '324d6172638d02a361cfa0ca7f86e241e5a56a008d4ab581a305f9ae5ea4a75f'),
        ('numba.cpython.setobj.SetInstance._remove_entry', numba.cpython.
        setobj.SetInstance._remove_entry,
        '2c441b00daac61976e673c0e738e8e76982669bd2851951890dd40526fa14da1'),
        ('numba.cpython.setobj.SetInstance.pop', numba.cpython.setobj.
        SetInstance.pop,
        '1a7b7464cbe0577f2a38f3af9acfef6d4d25d049b1e216157275fbadaab41d1b'),
        ('numba.cpython.setobj.SetInstance._resize', numba.cpython.setobj.
        SetInstance._resize,
        '5ca5c2ba4f8c4bf546fde106b9c2656d4b22a16d16e163fb64c5d85ea4d88746'),
        ('numba.cpython.setobj.SetInstance._replace_payload', numba.cpython
        .setobj.SetInstance._replace_payload,
        'ada75a6c85828bff69c8469538c1979801f560a43fb726221a9c21bf208ae78d'),
        ('numba.cpython.setobj.SetInstance._allocate_payload', numba.
        cpython.setobj.SetInstance._allocate_payload,
        '2e80c419df43ebc71075b4f97fc1701c10dbc576aed248845e176b8d5829e61b'),
        ('numba.cpython.setobj.SetInstance._copy_payload', numba.cpython.
        setobj.SetInstance._copy_payload,
        '0885ac36e1eb5a0a0fc4f5d91e54b2102b69e536091fed9f2610a71d225193ec'),
        ('numba.cpython.setobj.set_constructor', numba.cpython.setobj.
        set_constructor,
        '3d521a60c3b8eaf70aa0f7267427475dfddd8f5e5053b5bfe309bb5f1891b0ce'),
        ('numba.cpython.setobj.set_update', numba.cpython.setobj.set_update,
        '965c4f7f7abcea5cbe0491b602e6d4bcb1800fa1ec39b1ffccf07e1bc56051c3')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.boxing._native_set_to_python_list = _native_set_to_python_list
numba.cpython.setobj._SetPayload._lookup = _lookup
numba.cpython.setobj.SetInstance._add_entry = _add_entry
numba.cpython.setobj.SetInstance._add_key = _add_key
numba.cpython.setobj.SetInstance._remove_entry = _remove_entry
numba.cpython.setobj.SetInstance.pop = pop
numba.cpython.setobj.SetInstance._resize = _resize
numba.cpython.setobj.SetInstance._replace_payload = _replace_payload
numba.cpython.setobj.SetInstance._allocate_payload = _allocate_payload
numba.cpython.setobj.SetInstance._copy_payload = _copy_payload


def _reduce(self):
    libdata = self.library.serialize_using_object_code()
    typeann = str(self.type_annotation)
    fndesc = self.fndesc
    fndesc.typemap = fndesc.calltypes = None
    referenced_envs = self._find_referenced_environments()
    lllkh__swrb = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, lllkh__swrb, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    xgtqm__tby = target_context.get_executable(library, fndesc, env)
    lfxa__mvhky = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=xgtqm__tby, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return lfxa__mvhky


if _check_numba_change:
    for name, orig, hash in (('numba.core.compiler.CompileResult._reduce',
        numba.core.compiler.CompileResult._reduce,
        '5f86eacfa5202c202b3dc200f1a7a9b6d3f9d1ec16d43a52cb2d580c34fbfa82'),
        ('numba.core.compiler.CompileResult._rebuild', numba.core.compiler.
        CompileResult._rebuild,
        '44fa9dc2255883ab49195d18c3cca8c0ad715d0dd02033bd7e2376152edc4e84')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.compiler.CompileResult._reduce = _reduce
numba.core.compiler.CompileResult._rebuild = _rebuild
if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._IPythonCacheLocator.
        get_cache_path)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'eb33b7198697b8ef78edddcf69e58973c44744ff2cb2f54d4015611ad43baed0':
        warnings.warn(
            'numba.core.caching._IPythonCacheLocator.get_cache_path has changed'
            )
if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:

    def _get_cache_path(self):
        return numba.config.CACHE_DIR
    numba.core.caching._IPythonCacheLocator.get_cache_path = _get_cache_path
if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheLocator.
        ensure_cache_path)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '906b6f516f76927dfbe69602c335fa151b9f33d40dfe171a9190c0d11627bc03':
        warnings.warn(
            'numba.core.caching._CacheLocator.ensure_cache_path has changed')
if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
    import tempfile

    def _ensure_cache_path(self):
        from mpi4py import MPI
        sqwmn__aibm = MPI.COMM_WORLD
        zwjov__hmavk = None
        if sqwmn__aibm.Get_rank() == 0:
            try:
                hqsdi__sui = self.get_cache_path()
                os.makedirs(hqsdi__sui, exist_ok=True)
                tempfile.TemporaryFile(dir=hqsdi__sui).close()
            except Exception as e:
                zwjov__hmavk = e
        zwjov__hmavk = sqwmn__aibm.bcast(zwjov__hmavk)
        if isinstance(zwjov__hmavk, Exception):
            raise zwjov__hmavk
    numba.core.caching._CacheLocator.ensure_cache_path = _ensure_cache_path


def _analyze_op_call_builtins_len(self, scope, equiv_set, loc, args, kws):
    require(len(args) == 1)
    var = args[0]
    typ = self.typemap[var.name]
    require(isinstance(typ, types.ArrayCompatible))
    require(not isinstance(typ, types.Bytes))
    shape = equiv_set._get_shape(var)
    return ArrayAnalysis.AnalyzeResult(shape=shape[0], rhs=shape[0])


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.array_analysis.ArrayAnalysis.
        _analyze_op_call_builtins_len)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '612cbc67e8e462f25f348b2a5dd55595f4201a6af826cffcd38b16cd85fc70f7':
        warnings.warn(
            'numba.parfors.array_analysis.ArrayAnalysis._analyze_op_call_builtins_len has changed'
            )
(numba.parfors.array_analysis.ArrayAnalysis._analyze_op_call_builtins_len
    ) = _analyze_op_call_builtins_len
