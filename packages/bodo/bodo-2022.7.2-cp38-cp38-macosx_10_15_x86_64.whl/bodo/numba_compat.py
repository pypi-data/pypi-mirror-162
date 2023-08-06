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
from bodo.utils.python_310_bytecode_pass import Bodo310ByteCodePass, peep_hole_call_function_ex_to_call_function_kw, peep_hole_fuse_dict_add_updates, peep_hole_fuse_tuple_adds
from bodo.utils.typing import BodoError, get_overload_const_str, is_overload_constant_str, raise_bodo_error
_check_numba_change = False
numba.core.typing.templates._IntrinsicTemplate.prefer_literal = True


def run_frontend(func, inline_closures=False, emit_dels=False):
    from numba.core.utils import PYVERSION
    sfuv__divu = numba.core.bytecode.FunctionIdentity.from_function(func)
    merv__pwh = numba.core.interpreter.Interpreter(sfuv__divu)
    gkfrf__apln = numba.core.bytecode.ByteCode(func_id=sfuv__divu)
    func_ir = merv__pwh.interpret(gkfrf__apln)
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
        ttavo__oxc = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        ttavo__oxc.run()
    kyl__kvezh = numba.core.postproc.PostProcessor(func_ir)
    kyl__kvezh.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, ucl__zrce in visit_vars_extensions.items():
        if isinstance(stmt, t):
            ucl__zrce(stmt, callback, cbdata)
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
    smsw__fia = ['ravel', 'transpose', 'reshape']
    for iqody__xeh in blocks.values():
        for fwbv__bwlq in iqody__xeh.body:
            if type(fwbv__bwlq) in alias_analysis_extensions:
                ucl__zrce = alias_analysis_extensions[type(fwbv__bwlq)]
                ucl__zrce(fwbv__bwlq, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(fwbv__bwlq, ir.Assign):
                ouqg__hqhii = fwbv__bwlq.value
                ved__egaz = fwbv__bwlq.target.name
                if is_immutable_type(ved__egaz, typemap):
                    continue
                if isinstance(ouqg__hqhii, ir.Var
                    ) and ved__egaz != ouqg__hqhii.name:
                    _add_alias(ved__egaz, ouqg__hqhii.name, alias_map,
                        arg_aliases)
                if isinstance(ouqg__hqhii, ir.Expr) and (ouqg__hqhii.op ==
                    'cast' or ouqg__hqhii.op in ['getitem', 'static_getitem']):
                    _add_alias(ved__egaz, ouqg__hqhii.value.name, alias_map,
                        arg_aliases)
                if isinstance(ouqg__hqhii, ir.Expr
                    ) and ouqg__hqhii.op == 'inplace_binop':
                    _add_alias(ved__egaz, ouqg__hqhii.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(ouqg__hqhii, ir.Expr
                    ) and ouqg__hqhii.op == 'getattr' and ouqg__hqhii.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(ved__egaz, ouqg__hqhii.value.name, alias_map,
                        arg_aliases)
                if isinstance(ouqg__hqhii, ir.Expr
                    ) and ouqg__hqhii.op == 'getattr' and ouqg__hqhii.attr not in [
                    'shape'] and ouqg__hqhii.value.name in arg_aliases:
                    _add_alias(ved__egaz, ouqg__hqhii.value.name, alias_map,
                        arg_aliases)
                if isinstance(ouqg__hqhii, ir.Expr
                    ) and ouqg__hqhii.op == 'getattr' and ouqg__hqhii.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(ved__egaz, ouqg__hqhii.value.name, alias_map,
                        arg_aliases)
                if isinstance(ouqg__hqhii, ir.Expr) and ouqg__hqhii.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(ved__egaz, typemap):
                    for ads__ztcmq in ouqg__hqhii.items:
                        _add_alias(ved__egaz, ads__ztcmq.name, alias_map,
                            arg_aliases)
                if isinstance(ouqg__hqhii, ir.Expr
                    ) and ouqg__hqhii.op == 'call':
                    ajbt__peht = guard(find_callname, func_ir, ouqg__hqhii,
                        typemap)
                    if ajbt__peht is None:
                        continue
                    cjmmw__ghgs, fvu__yuxez = ajbt__peht
                    if ajbt__peht in alias_func_extensions:
                        sozim__scgi = alias_func_extensions[ajbt__peht]
                        sozim__scgi(ved__egaz, ouqg__hqhii.args, alias_map,
                            arg_aliases)
                    if fvu__yuxez == 'numpy' and cjmmw__ghgs in smsw__fia:
                        _add_alias(ved__egaz, ouqg__hqhii.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(fvu__yuxez, ir.Var
                        ) and cjmmw__ghgs in smsw__fia:
                        _add_alias(ved__egaz, fvu__yuxez.name, alias_map,
                            arg_aliases)
    brga__pspb = copy.deepcopy(alias_map)
    for ads__ztcmq in brga__pspb:
        for libj__xdlg in brga__pspb[ads__ztcmq]:
            alias_map[ads__ztcmq] |= alias_map[libj__xdlg]
        for libj__xdlg in brga__pspb[ads__ztcmq]:
            alias_map[libj__xdlg] = alias_map[ads__ztcmq]
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
    ninqb__qqwb = compute_cfg_from_blocks(func_ir.blocks)
    wdpos__ihhly = compute_use_defs(func_ir.blocks)
    dekac__zej = compute_live_map(ninqb__qqwb, func_ir.blocks, wdpos__ihhly
        .usemap, wdpos__ihhly.defmap)
    opkwf__rjzm = True
    while opkwf__rjzm:
        opkwf__rjzm = False
        for label, block in func_ir.blocks.items():
            lives = {ads__ztcmq.name for ads__ztcmq in block.terminator.
                list_vars()}
            for jjjnb__poaii, hvp__njqv in ninqb__qqwb.successors(label):
                lives |= dekac__zej[jjjnb__poaii]
            hlu__aecz = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    ved__egaz = stmt.target
                    mew__pro = stmt.value
                    if ved__egaz.name not in lives:
                        if isinstance(mew__pro, ir.Expr
                            ) and mew__pro.op == 'make_function':
                            continue
                        if isinstance(mew__pro, ir.Expr
                            ) and mew__pro.op == 'getattr':
                            continue
                        if isinstance(mew__pro, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(ved__egaz,
                            None), types.Function):
                            continue
                        if isinstance(mew__pro, ir.Expr
                            ) and mew__pro.op == 'build_map':
                            continue
                        if isinstance(mew__pro, ir.Expr
                            ) and mew__pro.op == 'build_tuple':
                            continue
                    if isinstance(mew__pro, ir.Var
                        ) and ved__egaz.name == mew__pro.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    pnamv__yhifg = analysis.ir_extension_usedefs[type(stmt)]
                    sxteb__dzwun, makcq__hgkl = pnamv__yhifg(stmt)
                    lives -= makcq__hgkl
                    lives |= sxteb__dzwun
                else:
                    lives |= {ads__ztcmq.name for ads__ztcmq in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(ved__egaz.name)
                hlu__aecz.append(stmt)
            hlu__aecz.reverse()
            if len(block.body) != len(hlu__aecz):
                opkwf__rjzm = True
            block.body = hlu__aecz


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    shydo__wcb = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (shydo__wcb,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    xsnde__iths = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), xsnde__iths)


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
            for lnlwm__zdmi in fnty.templates:
                self._inline_overloads.update(lnlwm__zdmi._inline_overloads)
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
    xsnde__iths = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), xsnde__iths)
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
    vdnub__oczmc, rehd__cbfco = self._get_impl(args, kws)
    if vdnub__oczmc is None:
        return
    vtwjy__sikz = types.Dispatcher(vdnub__oczmc)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        dnzij__jknqr = vdnub__oczmc._compiler
        flags = compiler.Flags()
        yqgk__ryg = dnzij__jknqr.targetdescr.typing_context
        qbi__fmwf = dnzij__jknqr.targetdescr.target_context
        ykk__cba = dnzij__jknqr.pipeline_class(yqgk__ryg, qbi__fmwf, None,
            None, None, flags, None)
        wfoa__yty = InlineWorker(yqgk__ryg, qbi__fmwf, dnzij__jknqr.locals,
            ykk__cba, flags, None)
        tnmn__mriaq = vtwjy__sikz.dispatcher.get_call_template
        lnlwm__zdmi, kztkm__xtab, drziw__fjytz, kws = tnmn__mriaq(rehd__cbfco,
            kws)
        if drziw__fjytz in self._inline_overloads:
            return self._inline_overloads[drziw__fjytz]['iinfo'].signature
        ir = wfoa__yty.run_untyped_passes(vtwjy__sikz.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, qbi__fmwf, ir, drziw__fjytz, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, drziw__fjytz, None)
        self._inline_overloads[sig.args] = {'folded_args': drziw__fjytz}
        jiwio__vmcyb = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = jiwio__vmcyb
        if not self._inline.is_always_inline:
            sig = vtwjy__sikz.get_call_type(self.context, rehd__cbfco, kws)
            self._compiled_overloads[sig.args] = vtwjy__sikz.get_overload(sig)
        ozco__fci = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': drziw__fjytz,
            'iinfo': ozco__fci}
    else:
        sig = vtwjy__sikz.get_call_type(self.context, rehd__cbfco, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = vtwjy__sikz.get_overload(sig)
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
    ugaef__grnut = [True, False]
    fos__dszni = [False, True]
    rhrc__wqalw = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    emb__bto = get_local_target(context)
    cigpa__mfl = utils.order_by_target_specificity(emb__bto, self.templates,
        fnkey=self.key[0])
    self._depth += 1
    for wshjm__fyx in cigpa__mfl:
        hbl__aqbcr = wshjm__fyx(context)
        qhoe__yttr = ugaef__grnut if hbl__aqbcr.prefer_literal else fos__dszni
        qhoe__yttr = [True] if getattr(hbl__aqbcr, '_no_unliteral', False
            ) else qhoe__yttr
        for qfmw__onv in qhoe__yttr:
            try:
                if qfmw__onv:
                    sig = hbl__aqbcr.apply(args, kws)
                else:
                    jdwm__cql = tuple([_unlit_non_poison(a) for a in args])
                    ihndr__ndh = {egor__fkca: _unlit_non_poison(ads__ztcmq) for
                        egor__fkca, ads__ztcmq in kws.items()}
                    sig = hbl__aqbcr.apply(jdwm__cql, ihndr__ndh)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    rhrc__wqalw.add_error(hbl__aqbcr, False, e, qfmw__onv)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = hbl__aqbcr.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    baox__xdxo = getattr(hbl__aqbcr, 'cases', None)
                    if baox__xdxo is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            baox__xdxo)
                    else:
                        msg = 'No match.'
                    rhrc__wqalw.add_error(hbl__aqbcr, True, msg, qfmw__onv)
    rhrc__wqalw.raise_error()


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
    lnlwm__zdmi = self.template(context)
    xje__jklqf = None
    gfdoh__mxtkj = None
    hgvs__quwr = None
    qhoe__yttr = [True, False] if lnlwm__zdmi.prefer_literal else [False, True]
    qhoe__yttr = [True] if getattr(lnlwm__zdmi, '_no_unliteral', False
        ) else qhoe__yttr
    for qfmw__onv in qhoe__yttr:
        if qfmw__onv:
            try:
                hgvs__quwr = lnlwm__zdmi.apply(args, kws)
            except Exception as lyth__vlwic:
                if isinstance(lyth__vlwic, errors.ForceLiteralArg):
                    raise lyth__vlwic
                xje__jklqf = lyth__vlwic
                hgvs__quwr = None
            else:
                break
        else:
            yeiwo__zft = tuple([_unlit_non_poison(a) for a in args])
            enm__cibul = {egor__fkca: _unlit_non_poison(ads__ztcmq) for 
                egor__fkca, ads__ztcmq in kws.items()}
            yhv__tfmuz = yeiwo__zft == args and kws == enm__cibul
            if not yhv__tfmuz and hgvs__quwr is None:
                try:
                    hgvs__quwr = lnlwm__zdmi.apply(yeiwo__zft, enm__cibul)
                except Exception as lyth__vlwic:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        lyth__vlwic, errors.NumbaError):
                        raise lyth__vlwic
                    if isinstance(lyth__vlwic, errors.ForceLiteralArg):
                        if lnlwm__zdmi.prefer_literal:
                            raise lyth__vlwic
                    gfdoh__mxtkj = lyth__vlwic
                else:
                    break
    if hgvs__quwr is None and (gfdoh__mxtkj is not None or xje__jklqf is not
        None):
        mxj__lht = '- Resolution failure for {} arguments:\n{}\n'
        pyy__dykpa = _termcolor.highlight(mxj__lht)
        if numba.core.config.DEVELOPER_MODE:
            sdpli__swxnh = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    hpwg__jvv = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    hpwg__jvv = ['']
                xys__zvg = '\n{}'.format(2 * sdpli__swxnh)
                vibl__dzzta = _termcolor.reset(xys__zvg + xys__zvg.join(
                    _bt_as_lines(hpwg__jvv)))
                return _termcolor.reset(vibl__dzzta)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            uji__amw = str(e)
            uji__amw = uji__amw if uji__amw else str(repr(e)) + add_bt(e)
            hvabz__xjxwp = errors.TypingError(textwrap.dedent(uji__amw))
            return pyy__dykpa.format(literalness, str(hvabz__xjxwp))
        import bodo
        if isinstance(xje__jklqf, bodo.utils.typing.BodoError):
            raise xje__jklqf
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', xje__jklqf) +
                nested_msg('non-literal', gfdoh__mxtkj))
        else:
            if 'missing a required argument' in xje__jklqf.msg:
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
            raise errors.TypingError(msg, loc=xje__jklqf.loc)
    return hgvs__quwr


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
    cjmmw__ghgs = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=cjmmw__ghgs)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            opckm__iiqaz = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), opckm__iiqaz)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    uzsb__fqbg = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            uzsb__fqbg.append(types.Omitted(a.value))
        else:
            uzsb__fqbg.append(self.typeof_pyval(a))
    uqv__epeba = None
    try:
        error = None
        uqv__epeba = self.compile(tuple(uzsb__fqbg))
    except errors.ForceLiteralArg as e:
        yvw__nrux = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if yvw__nrux:
            jnvt__cjgl = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            yzghj__asngx = ', '.join('Arg #{} is {}'.format(i, args[i]) for
                i in sorted(yvw__nrux))
            raise errors.CompilerError(jnvt__cjgl.format(yzghj__asngx))
        rehd__cbfco = []
        try:
            for i, ads__ztcmq in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        rehd__cbfco.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        rehd__cbfco.append(types.literal(args[i]))
                else:
                    rehd__cbfco.append(args[i])
            args = rehd__cbfco
        except (OSError, FileNotFoundError) as lisv__crd:
            error = FileNotFoundError(str(lisv__crd) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                uqv__epeba = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        reyp__bkyke = []
        for i, zpiqn__vzke in enumerate(args):
            val = zpiqn__vzke.value if isinstance(zpiqn__vzke, numba.core.
                dispatcher.OmittedArg) else zpiqn__vzke
            try:
                hvwym__tfcr = typeof(val, Purpose.argument)
            except ValueError as sxki__wop:
                reyp__bkyke.append((i, str(sxki__wop)))
            else:
                if hvwym__tfcr is None:
                    reyp__bkyke.append((i,
                        f'cannot determine Numba type of value {val}'))
        if reyp__bkyke:
            knt__wngt = '\n'.join(f'- argument {i}: {ohoc__liu}' for i,
                ohoc__liu in reyp__bkyke)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{knt__wngt}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                jnuq__gcug = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                bsorv__pptxi = False
                for rlxgb__dqn in jnuq__gcug:
                    if rlxgb__dqn in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        bsorv__pptxi = True
                        break
                if not bsorv__pptxi:
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
                opckm__iiqaz = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), opckm__iiqaz)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return uqv__epeba


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
    for hav__pzue in cres.library._codegen._engine._defined_symbols:
        if hav__pzue.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in hav__pzue and (
            'bodo_gb_udf_update_local' in hav__pzue or 
            'bodo_gb_udf_combine' in hav__pzue or 'bodo_gb_udf_eval' in
            hav__pzue or 'bodo_gb_apply_general_udfs' in hav__pzue):
            gb_agg_cfunc_addr[hav__pzue
                ] = cres.library.get_pointer_to_function(hav__pzue)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for hav__pzue in cres.library._codegen._engine._defined_symbols:
        if hav__pzue.startswith('cfunc') and ('get_join_cond_addr' not in
            hav__pzue or 'bodo_join_gen_cond' in hav__pzue):
            join_gen_cond_cfunc_addr[hav__pzue
                ] = cres.library.get_pointer_to_function(hav__pzue)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    vdnub__oczmc = self._get_dispatcher_for_current_target()
    if vdnub__oczmc is not self:
        return vdnub__oczmc.compile(sig)
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
            twl__odste = self.overloads.get(tuple(args))
            if twl__odste is not None:
                return twl__odste.entry_point
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
            ueue__yqcgk = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=ueue__yqcgk):
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
                pdpml__lww = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in pdpml__lww:
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
    jpf__qhq = self._final_module
    upydm__hvj = []
    qyon__ljhwv = 0
    for fn in jpf__qhq.functions:
        qyon__ljhwv += 1
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
            upydm__hvj.append(fn.name)
    if qyon__ljhwv == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if upydm__hvj:
        jpf__qhq = jpf__qhq.clone()
        for name in upydm__hvj:
            jpf__qhq.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = jpf__qhq
    return jpf__qhq


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
    for xhfb__kghs in self.constraints:
        loc = xhfb__kghs.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                xhfb__kghs(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                qhe__cdy = numba.core.errors.TypingError(str(e), loc=
                    xhfb__kghs.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(qhe__cdy, e))
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
                    qhe__cdy = numba.core.errors.TypingError(msg.format(con
                        =xhfb__kghs, err=str(e)), loc=xhfb__kghs.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(qhe__cdy, e))
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
    for okfrh__kqym in self._failures.values():
        for ipyu__gqtf in okfrh__kqym:
            if isinstance(ipyu__gqtf.error, ForceLiteralArg):
                raise ipyu__gqtf.error
            if isinstance(ipyu__gqtf.error, bodo.utils.typing.BodoError):
                raise ipyu__gqtf.error
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
    dabf__htxb = False
    hlu__aecz = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        hblh__zcbys = set()
        hdnku__emzf = lives & alias_set
        for ads__ztcmq in hdnku__emzf:
            hblh__zcbys |= alias_map[ads__ztcmq]
        lives_n_aliases = lives | hblh__zcbys | arg_aliases
        if type(stmt) in remove_dead_extensions:
            ucl__zrce = remove_dead_extensions[type(stmt)]
            stmt = ucl__zrce(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                dabf__htxb = True
                continue
        if isinstance(stmt, ir.Assign):
            ved__egaz = stmt.target
            mew__pro = stmt.value
            if ved__egaz.name not in lives:
                if has_no_side_effect(mew__pro, lives_n_aliases, call_table):
                    dabf__htxb = True
                    continue
                if isinstance(mew__pro, ir.Expr
                    ) and mew__pro.op == 'call' and call_table[mew__pro.
                    func.name] == ['astype']:
                    ukgfx__qiwl = guard(get_definition, func_ir, mew__pro.func)
                    if (ukgfx__qiwl is not None and ukgfx__qiwl.op ==
                        'getattr' and isinstance(typemap[ukgfx__qiwl.value.
                        name], types.Array) and ukgfx__qiwl.attr == 'astype'):
                        dabf__htxb = True
                        continue
            if saved_array_analysis and ved__egaz.name in lives and is_expr(
                mew__pro, 'getattr'
                ) and mew__pro.attr == 'shape' and is_array_typ(typemap[
                mew__pro.value.name]) and mew__pro.value.name not in lives:
                etffo__gaxe = {ads__ztcmq: egor__fkca for egor__fkca,
                    ads__ztcmq in func_ir.blocks.items()}
                if block in etffo__gaxe:
                    label = etffo__gaxe[block]
                    hwt__lps = saved_array_analysis.get_equiv_set(label)
                    ber__vajgo = hwt__lps.get_equiv_set(mew__pro.value)
                    if ber__vajgo is not None:
                        for ads__ztcmq in ber__vajgo:
                            if ads__ztcmq.endswith('#0'):
                                ads__ztcmq = ads__ztcmq[:-2]
                            if ads__ztcmq in typemap and is_array_typ(typemap
                                [ads__ztcmq]) and ads__ztcmq in lives:
                                mew__pro.value = ir.Var(mew__pro.value.
                                    scope, ads__ztcmq, mew__pro.value.loc)
                                dabf__htxb = True
                                break
            if isinstance(mew__pro, ir.Var
                ) and ved__egaz.name == mew__pro.name:
                dabf__htxb = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                dabf__htxb = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            pnamv__yhifg = analysis.ir_extension_usedefs[type(stmt)]
            sxteb__dzwun, makcq__hgkl = pnamv__yhifg(stmt)
            lives -= makcq__hgkl
            lives |= sxteb__dzwun
        else:
            lives |= {ads__ztcmq.name for ads__ztcmq in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                djh__qmzd = set()
                if isinstance(mew__pro, ir.Expr):
                    djh__qmzd = {ads__ztcmq.name for ads__ztcmq in mew__pro
                        .list_vars()}
                if ved__egaz.name not in djh__qmzd:
                    lives.remove(ved__egaz.name)
        hlu__aecz.append(stmt)
    hlu__aecz.reverse()
    block.body = hlu__aecz
    return dabf__htxb


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            aacic__yvng, = args
            if isinstance(aacic__yvng, types.IterableType):
                dtype = aacic__yvng.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), aacic__yvng)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    fpg__hrhb = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (fpg__hrhb, self.dtype)
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
        except LiteralTypingError as qal__pcfcl:
            return
    try:
        return literal(value)
    except LiteralTypingError as qal__pcfcl:
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
        nnzb__fowcm = py_func.__qualname__
    except AttributeError as qal__pcfcl:
        nnzb__fowcm = py_func.__name__
    dwits__quh = inspect.getfile(py_func)
    for cls in self._locator_classes:
        dkv__sqam = cls.from_function(py_func, dwits__quh)
        if dkv__sqam is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (nnzb__fowcm, dwits__quh))
    self._locator = dkv__sqam
    xplty__dihq = inspect.getfile(py_func)
    whwg__oydy = os.path.splitext(os.path.basename(xplty__dihq))[0]
    if dwits__quh.startswith('<ipython-'):
        kxw__wmnh = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', whwg__oydy, count=1)
        if kxw__wmnh == whwg__oydy:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        whwg__oydy = kxw__wmnh
    cruw__qsk = '%s.%s' % (whwg__oydy, nnzb__fowcm)
    tdhyx__mps = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(cruw__qsk, tdhyx__mps
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    llsc__xhq = list(filter(lambda a: self._istuple(a.name), args))
    if len(llsc__xhq) == 2 and fn.__name__ == 'add':
        yao__nbw = self.typemap[llsc__xhq[0].name]
        cfe__zxus = self.typemap[llsc__xhq[1].name]
        if yao__nbw.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                llsc__xhq[1]))
        if cfe__zxus.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                llsc__xhq[0]))
        try:
            mzajp__rfvjy = [equiv_set.get_shape(x) for x in llsc__xhq]
            if None in mzajp__rfvjy:
                return None
            gjpzl__cflzy = sum(mzajp__rfvjy, ())
            return ArrayAnalysis.AnalyzeResult(shape=gjpzl__cflzy)
        except GuardException as qal__pcfcl:
            return None
    smz__zqpos = list(filter(lambda a: self._isarray(a.name), args))
    require(len(smz__zqpos) > 0)
    pgbn__lux = [x.name for x in smz__zqpos]
    iuxfm__kjt = [self.typemap[x.name].ndim for x in smz__zqpos]
    dkv__bmiv = max(iuxfm__kjt)
    require(dkv__bmiv > 0)
    mzajp__rfvjy = [equiv_set.get_shape(x) for x in smz__zqpos]
    if any(a is None for a in mzajp__rfvjy):
        return ArrayAnalysis.AnalyzeResult(shape=smz__zqpos[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, smz__zqpos))
    return self._broadcast_assert_shapes(scope, equiv_set, loc,
        mzajp__rfvjy, pgbn__lux)


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
    gkud__sbulx = code_obj.code
    dzgt__vod = len(gkud__sbulx.co_freevars)
    ajv__jihu = gkud__sbulx.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        huop__exa, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        ajv__jihu = [ads__ztcmq.name for ads__ztcmq in huop__exa]
    iwj__spi = caller_ir.func_id.func.__globals__
    try:
        iwj__spi = getattr(code_obj, 'globals', iwj__spi)
    except KeyError as qal__pcfcl:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    reba__wue = []
    for x in ajv__jihu:
        try:
            xvo__xadhf = caller_ir.get_definition(x)
        except KeyError as qal__pcfcl:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(xvo__xadhf, (ir.Const, ir.Global, ir.FreeVar)):
            val = xvo__xadhf.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                shydo__wcb = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                iwj__spi[shydo__wcb] = bodo.jit(distributed=False)(val)
                iwj__spi[shydo__wcb].is_nested_func = True
                val = shydo__wcb
            if isinstance(val, CPUDispatcher):
                shydo__wcb = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                iwj__spi[shydo__wcb] = val
                val = shydo__wcb
            reba__wue.append(val)
        elif isinstance(xvo__xadhf, ir.Expr
            ) and xvo__xadhf.op == 'make_function':
            uubm__tzbe = convert_code_obj_to_function(xvo__xadhf, caller_ir)
            shydo__wcb = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            iwj__spi[shydo__wcb] = bodo.jit(distributed=False)(uubm__tzbe)
            iwj__spi[shydo__wcb].is_nested_func = True
            reba__wue.append(shydo__wcb)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    bprwu__hph = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        reba__wue)])
    ewnnb__bhvv = ','.join([('c_%d' % i) for i in range(dzgt__vod)])
    frni__lmvr = list(gkud__sbulx.co_varnames)
    dntdt__onnt = 0
    cjxga__hzux = gkud__sbulx.co_argcount
    umqr__umq = caller_ir.get_definition(code_obj.defaults)
    if umqr__umq is not None:
        if isinstance(umqr__umq, tuple):
            d = [caller_ir.get_definition(x).value for x in umqr__umq]
            zni__uvd = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in umqr__umq.items]
            zni__uvd = tuple(d)
        dntdt__onnt = len(zni__uvd)
    txa__pzuir = cjxga__hzux - dntdt__onnt
    ijaq__piwh = ','.join([('%s' % frni__lmvr[i]) for i in range(txa__pzuir)])
    if dntdt__onnt:
        wfirb__lexnk = [('%s = %s' % (frni__lmvr[i + txa__pzuir], zni__uvd[
            i])) for i in range(dntdt__onnt)]
        ijaq__piwh += ', '
        ijaq__piwh += ', '.join(wfirb__lexnk)
    return _create_function_from_code_obj(gkud__sbulx, bprwu__hph,
        ijaq__piwh, ewnnb__bhvv, iwj__spi)


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
    for dkapl__yyw, (gogr__fph, wgzjb__rmu) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % wgzjb__rmu)
            cqar__xdpup = _pass_registry.get(gogr__fph).pass_inst
            if isinstance(cqar__xdpup, CompilerPass):
                self._runPass(dkapl__yyw, cqar__xdpup, state)
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
                    pipeline_name, wgzjb__rmu)
                rjsh__cgt = self._patch_error(msg, e)
                raise rjsh__cgt
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
    qhdwg__galcx = None
    makcq__hgkl = {}

    def lookup(var, already_seen, varonly=True):
        val = makcq__hgkl.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    pfri__bsmi = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        ved__egaz = stmt.target
        mew__pro = stmt.value
        makcq__hgkl[ved__egaz.name] = mew__pro
        if isinstance(mew__pro, ir.Var) and mew__pro.name in makcq__hgkl:
            mew__pro = lookup(mew__pro, set())
        if isinstance(mew__pro, ir.Expr):
            mldnz__eczd = set(lookup(ads__ztcmq, set(), True).name for
                ads__ztcmq in mew__pro.list_vars())
            if name in mldnz__eczd:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(mew__pro)]
                gge__bunzb = [x for x, xij__dzs in args if xij__dzs.name !=
                    name]
                args = [(x, xij__dzs) for x, xij__dzs in args if x !=
                    xij__dzs.name]
                xkj__ppebg = dict(args)
                if len(gge__bunzb) == 1:
                    xkj__ppebg[gge__bunzb[0]] = ir.Var(ved__egaz.scope, 
                        name + '#init', ved__egaz.loc)
                replace_vars_inner(mew__pro, xkj__ppebg)
                qhdwg__galcx = nodes[i:]
                break
    return qhdwg__galcx


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
        edd__bod = expand_aliases({ads__ztcmq.name for ads__ztcmq in stmt.
            list_vars()}, alias_map, arg_aliases)
        kzfs__tby = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        evlpr__voeog = expand_aliases({ads__ztcmq.name for ads__ztcmq in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        skoq__gcuak = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(kzfs__tby & evlpr__voeog | skoq__gcuak & edd__bod) == 0:
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
    ligk__syxu = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            ligk__syxu.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                ligk__syxu.update(get_parfor_writes(stmt, func_ir))
    return ligk__syxu


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    ligk__syxu = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        ligk__syxu.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        ligk__syxu = {ads__ztcmq.name for ads__ztcmq in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        ligk__syxu = {ads__ztcmq.name for ads__ztcmq in stmt.
            get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            ligk__syxu.update({ads__ztcmq.name for ads__ztcmq in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        ajbt__peht = guard(find_callname, func_ir, stmt.value)
        if ajbt__peht in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            ligk__syxu.add(stmt.value.args[0].name)
        if ajbt__peht == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            ligk__syxu.add(stmt.value.args[1].name)
    return ligk__syxu


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
        ucl__zrce = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        iiqsg__cii = ucl__zrce.format(self, msg)
        self.args = iiqsg__cii,
    else:
        ucl__zrce = _termcolor.errmsg('{0}')
        iiqsg__cii = ucl__zrce.format(self)
        self.args = iiqsg__cii,
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
        for hszse__zkoc in options['distributed']:
            dist_spec[hszse__zkoc] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for hszse__zkoc in options['distributed_block']:
            dist_spec[hszse__zkoc] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    rwws__cgiop = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, uzn__xba in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(uzn__xba)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    kwbo__wjw = {}
    for qlpk__dft in reversed(inspect.getmro(cls)):
        kwbo__wjw.update(qlpk__dft.__dict__)
    scz__dua, nhz__knx, lziim__cvs, wlrfu__aaecg = {}, {}, {}, {}
    for egor__fkca, ads__ztcmq in kwbo__wjw.items():
        if isinstance(ads__ztcmq, pytypes.FunctionType):
            scz__dua[egor__fkca] = ads__ztcmq
        elif isinstance(ads__ztcmq, property):
            nhz__knx[egor__fkca] = ads__ztcmq
        elif isinstance(ads__ztcmq, staticmethod):
            lziim__cvs[egor__fkca] = ads__ztcmq
        else:
            wlrfu__aaecg[egor__fkca] = ads__ztcmq
    fsdcj__tzrs = (set(scz__dua) | set(nhz__knx) | set(lziim__cvs)) & set(spec)
    if fsdcj__tzrs:
        raise NameError('name shadowing: {0}'.format(', '.join(fsdcj__tzrs)))
    laxbi__drqv = wlrfu__aaecg.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(wlrfu__aaecg)
    if wlrfu__aaecg:
        msg = 'class members are not yet supported: {0}'
        biv__ufrr = ', '.join(wlrfu__aaecg.keys())
        raise TypeError(msg.format(biv__ufrr))
    for egor__fkca, ads__ztcmq in nhz__knx.items():
        if ads__ztcmq.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(egor__fkca))
    jit_methods = {egor__fkca: bodo.jit(returns_maybe_distributed=
        rwws__cgiop)(ads__ztcmq) for egor__fkca, ads__ztcmq in scz__dua.items()
        }
    jit_props = {}
    for egor__fkca, ads__ztcmq in nhz__knx.items():
        xsnde__iths = {}
        if ads__ztcmq.fget:
            xsnde__iths['get'] = bodo.jit(ads__ztcmq.fget)
        if ads__ztcmq.fset:
            xsnde__iths['set'] = bodo.jit(ads__ztcmq.fset)
        jit_props[egor__fkca] = xsnde__iths
    jit_static_methods = {egor__fkca: bodo.jit(ads__ztcmq.__func__) for 
        egor__fkca, ads__ztcmq in lziim__cvs.items()}
    gpa__ondbw = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    mqoy__dohh = dict(class_type=gpa__ondbw, __doc__=laxbi__drqv)
    mqoy__dohh.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), mqoy__dohh)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, gpa__ondbw)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(gpa__ondbw, typingctx, targetctx).register()
    as_numba_type.register(cls, gpa__ondbw.instance_type)
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
    qhe__kcoz = ','.join('{0}:{1}'.format(egor__fkca, ads__ztcmq) for 
        egor__fkca, ads__ztcmq in struct.items())
    vaow__qoit = ','.join('{0}:{1}'.format(egor__fkca, ads__ztcmq) for 
        egor__fkca, ads__ztcmq in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), qhe__kcoz, vaow__qoit)
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
    qrgzs__zns = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if qrgzs__zns is None:
        return
    ycjh__ciwq, qafbv__awrcj = qrgzs__zns
    for a in itertools.chain(ycjh__ciwq, qafbv__awrcj.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, ycjh__ciwq, qafbv__awrcj)
    except ForceLiteralArg as e:
        qjymm__sut = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(qjymm__sut, self.kws)
        ekkki__aaxu = set()
        etjw__gaeb = set()
        bpnf__vwga = {}
        for dkapl__yyw in e.requested_args:
            sqksp__xrz = typeinfer.func_ir.get_definition(folded[dkapl__yyw])
            if isinstance(sqksp__xrz, ir.Arg):
                ekkki__aaxu.add(sqksp__xrz.index)
                if sqksp__xrz.index in e.file_infos:
                    bpnf__vwga[sqksp__xrz.index] = e.file_infos[sqksp__xrz.
                        index]
            else:
                etjw__gaeb.add(dkapl__yyw)
        if etjw__gaeb:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif ekkki__aaxu:
            raise ForceLiteralArg(ekkki__aaxu, loc=self.loc, file_infos=
                bpnf__vwga)
    if sig is None:
        lgn__ztry = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in ycjh__ciwq]
        args += [('%s=%s' % (egor__fkca, ads__ztcmq)) for egor__fkca,
            ads__ztcmq in sorted(qafbv__awrcj.items())]
        axt__scsdd = lgn__ztry.format(fnty, ', '.join(map(str, args)))
        ezjl__yqfn = context.explain_function_type(fnty)
        msg = '\n'.join([axt__scsdd, ezjl__yqfn])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        gacon__ikokp = context.unify_pairs(sig.recvr, fnty.this)
        if gacon__ikokp is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if gacon__ikokp is not None and gacon__ikokp.is_precise():
            efd__sntf = fnty.copy(this=gacon__ikokp)
            typeinfer.propagate_refined_type(self.func, efd__sntf)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            dpbqr__nrfhw = target.getone()
            if context.unify_pairs(dpbqr__nrfhw, sig.return_type
                ) == dpbqr__nrfhw:
                sig = sig.replace(return_type=dpbqr__nrfhw)
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
        jnvt__cjgl = '*other* must be a {} but got a {} instead'
        raise TypeError(jnvt__cjgl.format(ForceLiteralArg, type(other)))
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
    bajx__jwpfq = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for egor__fkca, ads__ztcmq in kwargs.items():
        dofx__qfgyo = None
        try:
            sce__bsr = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var(
                'dummy'), loc)
            func_ir._definitions[sce__bsr.name] = [ads__ztcmq]
            dofx__qfgyo = get_const_value_inner(func_ir, sce__bsr)
            func_ir._definitions.pop(sce__bsr.name)
            if isinstance(dofx__qfgyo, str):
                dofx__qfgyo = sigutils._parse_signature_string(dofx__qfgyo)
            if isinstance(dofx__qfgyo, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {egor__fkca} is annotated as type class {dofx__qfgyo}."""
                    )
            assert isinstance(dofx__qfgyo, types.Type)
            if isinstance(dofx__qfgyo, (types.List, types.Set)):
                dofx__qfgyo = dofx__qfgyo.copy(reflected=False)
            bajx__jwpfq[egor__fkca] = dofx__qfgyo
        except BodoError as qal__pcfcl:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(dofx__qfgyo, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(ads__ztcmq, ir.Global):
                    msg = f'Global {ads__ztcmq.name!r} is not defined.'
                if isinstance(ads__ztcmq, ir.FreeVar):
                    msg = f'Freevar {ads__ztcmq.name!r} is not defined.'
            if isinstance(ads__ztcmq, ir.Expr) and ads__ztcmq.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=egor__fkca, msg=msg, loc=loc)
    for name, typ in bajx__jwpfq.items():
        self._legalize_arg_type(name, typ, loc)
    return bajx__jwpfq


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
    mzq__swp = inst.arg
    assert mzq__swp > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(mzq__swp)]))
    tmps = [state.make_temp() for _ in range(mzq__swp - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    nztg__hyad = ir.Global('format', format, loc=self.loc)
    self.store(value=nztg__hyad, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    ffmpa__nef = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=ffmpa__nef, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    mzq__swp = inst.arg
    assert mzq__swp > 0, 'invalid BUILD_STRING count'
    qycx__ftiv = self.get(strings[0])
    for other, vor__spx in zip(strings[1:], tmps):
        other = self.get(other)
        ouqg__hqhii = ir.Expr.binop(operator.add, lhs=qycx__ftiv, rhs=other,
            loc=self.loc)
        self.store(ouqg__hqhii, vor__spx)
        qycx__ftiv = self.get(vor__spx)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    nof__dag = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, nof__dag])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    zht__wsswj = mk_unique_var(f'{var_name}')
    cvwav__zvo = zht__wsswj.replace('<', '_').replace('>', '_')
    cvwav__zvo = cvwav__zvo.replace('.', '_').replace('$', '_v')
    return cvwav__zvo


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
                gzprv__jlahw = get_overload_const_str(val2)
                if gzprv__jlahw != 'ns':
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
        jna__tmat = states['defmap']
        if len(jna__tmat) == 0:
            bbzg__dery = assign.target
            numba.core.ssa._logger.debug('first assign: %s', bbzg__dery)
            if bbzg__dery.name not in scope.localvars:
                bbzg__dery = scope.define(assign.target.name, loc=assign.loc)
        else:
            bbzg__dery = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=bbzg__dery, value=assign.value, loc=
            assign.loc)
        jna__tmat[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    pbbe__uxfg = []
    for egor__fkca, ads__ztcmq in typing.npydecl.registry.globals:
        if egor__fkca == func:
            pbbe__uxfg.append(ads__ztcmq)
    for egor__fkca, ads__ztcmq in typing.templates.builtin_registry.globals:
        if egor__fkca == func:
            pbbe__uxfg.append(ads__ztcmq)
    if len(pbbe__uxfg) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return pbbe__uxfg


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    mco__vjdy = {}
    txopj__oofs = find_topo_order(blocks)
    aju__pba = {}
    for label in txopj__oofs:
        block = blocks[label]
        hlu__aecz = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                ved__egaz = stmt.target.name
                mew__pro = stmt.value
                if (mew__pro.op == 'getattr' and mew__pro.attr in arr_math and
                    isinstance(typemap[mew__pro.value.name], types.npytypes
                    .Array)):
                    mew__pro = stmt.value
                    vrh__jptwf = mew__pro.value
                    mco__vjdy[ved__egaz] = vrh__jptwf
                    scope = vrh__jptwf.scope
                    loc = vrh__jptwf.loc
                    cofta__ljyhk = ir.Var(scope, mk_unique_var('$np_g_var'),
                        loc)
                    typemap[cofta__ljyhk.name] = types.misc.Module(numpy)
                    wdgjg__amltq = ir.Global('np', numpy, loc)
                    srtd__arg = ir.Assign(wdgjg__amltq, cofta__ljyhk, loc)
                    mew__pro.value = cofta__ljyhk
                    hlu__aecz.append(srtd__arg)
                    func_ir._definitions[cofta__ljyhk.name] = [wdgjg__amltq]
                    func = getattr(numpy, mew__pro.attr)
                    pef__rao = get_np_ufunc_typ_lst(func)
                    aju__pba[ved__egaz] = pef__rao
                if mew__pro.op == 'call' and mew__pro.func.name in mco__vjdy:
                    vrh__jptwf = mco__vjdy[mew__pro.func.name]
                    fbd__legfl = calltypes.pop(mew__pro)
                    kvp__mca = fbd__legfl.args[:len(mew__pro.args)]
                    vazo__erpw = {name: typemap[ads__ztcmq.name] for name,
                        ads__ztcmq in mew__pro.kws}
                    genj__fmpkf = aju__pba[mew__pro.func.name]
                    juw__vayr = None
                    for dmnsu__somkq in genj__fmpkf:
                        try:
                            juw__vayr = dmnsu__somkq.get_call_type(typingctx,
                                [typemap[vrh__jptwf.name]] + list(kvp__mca),
                                vazo__erpw)
                            typemap.pop(mew__pro.func.name)
                            typemap[mew__pro.func.name] = dmnsu__somkq
                            calltypes[mew__pro] = juw__vayr
                            break
                        except Exception as qal__pcfcl:
                            pass
                    if juw__vayr is None:
                        raise TypeError(
                            f'No valid template found for {mew__pro.func.name}'
                            )
                    mew__pro.args = [vrh__jptwf] + mew__pro.args
            hlu__aecz.append(stmt)
        block.body = hlu__aecz


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    qjinc__dcnz = ufunc.nin
    cyl__cvdt = ufunc.nout
    txa__pzuir = ufunc.nargs
    assert txa__pzuir == qjinc__dcnz + cyl__cvdt
    if len(args) < qjinc__dcnz:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            qjinc__dcnz))
    if len(args) > txa__pzuir:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), txa__pzuir)
            )
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    gtkpc__kqtow = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    rfxe__tspp = max(gtkpc__kqtow)
    uyn__iapvq = args[qjinc__dcnz:]
    if not all(d == rfxe__tspp for d in gtkpc__kqtow[qjinc__dcnz:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(gpas__oslbx, types.ArrayCompatible) and not
        isinstance(gpas__oslbx, types.Bytes) for gpas__oslbx in uyn__iapvq):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(gpas__oslbx.mutable for gpas__oslbx in uyn__iapvq):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    xoqfe__avp = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    xws__kwj = None
    if rfxe__tspp > 0 and len(uyn__iapvq) < ufunc.nout:
        xws__kwj = 'C'
        axre__uzlr = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in axre__uzlr and 'F' in axre__uzlr:
            xws__kwj = 'F'
    return xoqfe__avp, uyn__iapvq, rfxe__tspp, xws__kwj


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
        dggp__ybo = 'Dict.key_type cannot be of type {}'
        raise TypingError(dggp__ybo.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        dggp__ybo = 'Dict.value_type cannot be of type {}'
        raise TypingError(dggp__ybo.format(valty))
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
    trm__bffkh = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[trm__bffkh]
        return impl, args
    except KeyError as qal__pcfcl:
        pass
    impl, args = self._build_impl(trm__bffkh, args, kws)
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
    opkwf__rjzm = False
    blocks = parfor.loop_body.copy()
    for label, block in blocks.items():
        if len(block.body):
            osoh__ozr = block.body[-1]
            if isinstance(osoh__ozr, ir.Branch):
                if len(blocks[osoh__ozr.truebr].body) == 1 and len(blocks[
                    osoh__ozr.falsebr].body) == 1:
                    hzs__vgpnl = blocks[osoh__ozr.truebr].body[0]
                    oocvv__fwxfn = blocks[osoh__ozr.falsebr].body[0]
                    if isinstance(hzs__vgpnl, ir.Jump) and isinstance(
                        oocvv__fwxfn, ir.Jump
                        ) and hzs__vgpnl.target == oocvv__fwxfn.target:
                        parfor.loop_body[label].body[-1] = ir.Jump(hzs__vgpnl
                            .target, osoh__ozr.loc)
                        opkwf__rjzm = True
                elif len(blocks[osoh__ozr.truebr].body) == 1:
                    hzs__vgpnl = blocks[osoh__ozr.truebr].body[0]
                    if isinstance(hzs__vgpnl, ir.Jump
                        ) and hzs__vgpnl.target == osoh__ozr.falsebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(hzs__vgpnl
                            .target, osoh__ozr.loc)
                        opkwf__rjzm = True
                elif len(blocks[osoh__ozr.falsebr].body) == 1:
                    oocvv__fwxfn = blocks[osoh__ozr.falsebr].body[0]
                    if isinstance(oocvv__fwxfn, ir.Jump
                        ) and oocvv__fwxfn.target == osoh__ozr.truebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(oocvv__fwxfn
                            .target, osoh__ozr.loc)
                        opkwf__rjzm = True
    return opkwf__rjzm


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        syvck__ypmxr = find_topo_order(parfor.loop_body)
    djud__rwi = syvck__ypmxr[0]
    inalb__zumj = {}
    _update_parfor_get_setitems(parfor.loop_body[djud__rwi].body, parfor.
        index_var, alias_map, inalb__zumj, lives_n_aliases)
    dggfv__dii = set(inalb__zumj.keys())
    for bupsm__gzimj in syvck__ypmxr:
        if bupsm__gzimj == djud__rwi:
            continue
        for stmt in parfor.loop_body[bupsm__gzimj].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            suksm__zhr = set(ads__ztcmq.name for ads__ztcmq in stmt.list_vars()
                )
            bsxvt__mvgh = suksm__zhr & dggfv__dii
            for a in bsxvt__mvgh:
                inalb__zumj.pop(a, None)
    for bupsm__gzimj in syvck__ypmxr:
        if bupsm__gzimj == djud__rwi:
            continue
        block = parfor.loop_body[bupsm__gzimj]
        tfdgt__pevqm = inalb__zumj.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            tfdgt__pevqm, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    pey__mkbf = max(blocks.keys())
    wlkxm__xoidd, vmi__ksgu = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    uzmby__vesqp = ir.Jump(wlkxm__xoidd, ir.Loc('parfors_dummy', -1))
    blocks[pey__mkbf].body.append(uzmby__vesqp)
    ninqb__qqwb = compute_cfg_from_blocks(blocks)
    wdpos__ihhly = compute_use_defs(blocks)
    dekac__zej = compute_live_map(ninqb__qqwb, blocks, wdpos__ihhly.usemap,
        wdpos__ihhly.defmap)
    alias_set = set(alias_map.keys())
    for label, block in blocks.items():
        hlu__aecz = []
        hfr__nmfj = {ads__ztcmq.name for ads__ztcmq in block.terminator.
            list_vars()}
        for jjjnb__poaii, hvp__njqv in ninqb__qqwb.successors(label):
            hfr__nmfj |= dekac__zej[jjjnb__poaii]
        for stmt in reversed(block.body):
            hblh__zcbys = hfr__nmfj & alias_set
            for ads__ztcmq in hblh__zcbys:
                hfr__nmfj |= alias_map[ads__ztcmq]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in hfr__nmfj and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                ajbt__peht = guard(find_callname, func_ir, stmt.value)
                if ajbt__peht == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in hfr__nmfj and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            hfr__nmfj |= {ads__ztcmq.name for ads__ztcmq in stmt.list_vars()}
            hlu__aecz.append(stmt)
        hlu__aecz.reverse()
        block.body = hlu__aecz
    typemap.pop(vmi__ksgu.name)
    blocks[pey__mkbf].body.pop()
    opkwf__rjzm = True
    while opkwf__rjzm:
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
        opkwf__rjzm = trim_empty_parfor_branches(parfor)
    uzg__yfo = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        uzg__yfo &= len(block.body) == 0
    if uzg__yfo:
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
    rsz__bgzy = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                rsz__bgzy += 1
                parfor = stmt
                igm__bnusa = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = igm__bnusa.scope
                loc = ir.Loc('parfors_dummy', -1)
                gygkk__mdb = ir.Var(scope, mk_unique_var('$const'), loc)
                igm__bnusa.body.append(ir.Assign(ir.Const(0, loc),
                    gygkk__mdb, loc))
                igm__bnusa.body.append(ir.Return(gygkk__mdb, loc))
                ninqb__qqwb = compute_cfg_from_blocks(parfor.loop_body)
                for gshfi__kasf in ninqb__qqwb.dead_nodes():
                    del parfor.loop_body[gshfi__kasf]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                igm__bnusa = parfor.loop_body[max(parfor.loop_body.keys())]
                igm__bnusa.body.pop()
                igm__bnusa.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return rsz__bgzy


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def simplify_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import merge_adjacent_blocks, rename_labels
    ninqb__qqwb = compute_cfg_from_blocks(blocks)

    def find_single_branch(label):
        block = blocks[label]
        return len(block.body) == 1 and isinstance(block.body[0], ir.Branch
            ) and label != ninqb__qqwb.entry_point()
    gcx__tnbn = list(filter(find_single_branch, blocks.keys()))
    egsh__munou = set()
    for label in gcx__tnbn:
        inst = blocks[label].body[0]
        wwbib__mqif = ninqb__qqwb.predecessors(label)
        nkp__rtc = True
        for sufi__vew, obin__qtky in wwbib__mqif:
            block = blocks[sufi__vew]
            if isinstance(block.body[-1], ir.Jump):
                block.body[-1] = copy.copy(inst)
            else:
                nkp__rtc = False
        if nkp__rtc:
            egsh__munou.add(label)
    for label in egsh__munou:
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
            twl__odste = self.overloads.get(tuple(args))
            if twl__odste is not None:
                return twl__odste.entry_point
            self._pre_compile(args, return_type, flags)
            gpseu__tfdj = self.func_ir
            ueue__yqcgk = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=ueue__yqcgk):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=gpseu__tfdj, args=
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
        oxgtj__jrhqv = copy.deepcopy(flags)
        oxgtj__jrhqv.no_rewrites = True

        def compile_local(the_ir, the_flags):
            qgw__hufig = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return qgw__hufig.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        zqdk__yye = compile_local(func_ir, oxgtj__jrhqv)
        newsi__axzna = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    newsi__axzna = compile_local(func_ir, flags)
                except Exception as qal__pcfcl:
                    pass
        if newsi__axzna is not None:
            cres = newsi__axzna
        else:
            cres = zqdk__yye
        return cres
    else:
        qgw__hufig = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return qgw__hufig.compile_ir(func_ir=func_ir, lifted=lifted,
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
    eofh__xxozo = self.get_data_type(typ.dtype)
    zhgj__rue = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        zhgj__rue):
        fvgkd__ubjob = ary.ctypes.data
        ozdnj__lgda = self.add_dynamic_addr(builder, fvgkd__ubjob, info=str
            (type(fvgkd__ubjob)))
        pntg__eiq = self.add_dynamic_addr(builder, id(ary), info=str(type(ary))
            )
        self.global_arrays.append(ary)
    else:
        ixqnr__qws = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            ixqnr__qws = ixqnr__qws.view('int64')
        val = bytearray(ixqnr__qws.data)
        sfz__gux = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        ozdnj__lgda = cgutils.global_constant(builder, '.const.array.data',
            sfz__gux)
        ozdnj__lgda.align = self.get_abi_alignment(eofh__xxozo)
        pntg__eiq = None
    hcmr__agyih = self.get_value_type(types.intp)
    evj__wup = [self.get_constant(types.intp, ppha__iik) for ppha__iik in
        ary.shape]
    ntu__rtjr = lir.Constant(lir.ArrayType(hcmr__agyih, len(evj__wup)),
        evj__wup)
    cslr__aptm = [self.get_constant(types.intp, ppha__iik) for ppha__iik in
        ary.strides]
    eayk__vbvqj = lir.Constant(lir.ArrayType(hcmr__agyih, len(cslr__aptm)),
        cslr__aptm)
    aqey__fuhoc = self.get_constant(types.intp, ary.dtype.itemsize)
    owcx__yyif = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        owcx__yyif, aqey__fuhoc, ozdnj__lgda.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), ntu__rtjr, eayk__vbvqj])


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
    cuqj__ijm = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    gcg__egst = lir.Function(module, cuqj__ijm, name='nrt_atomic_{0}'.
        format(op))
    [mlkvs__bvecr] = gcg__egst.args
    bjq__kvew = gcg__egst.append_basic_block()
    builder = lir.IRBuilder(bjq__kvew)
    ufjum__dbxe = lir.Constant(_word_type, 1)
    if False:
        dddu__ilbor = builder.atomic_rmw(op, mlkvs__bvecr, ufjum__dbxe,
            ordering=ordering)
        res = getattr(builder, op)(dddu__ilbor, ufjum__dbxe)
        builder.ret(res)
    else:
        dddu__ilbor = builder.load(mlkvs__bvecr)
        eyi__nkwf = getattr(builder, op)(dddu__ilbor, ufjum__dbxe)
        tuvfh__mlbpx = builder.icmp_signed('!=', dddu__ilbor, lir.Constant(
            dddu__ilbor.type, -1))
        with cgutils.if_likely(builder, tuvfh__mlbpx):
            builder.store(eyi__nkwf, mlkvs__bvecr)
        builder.ret(eyi__nkwf)
    return gcg__egst


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
        banfk__lzyob = state.targetctx.codegen()
        state.library = banfk__lzyob.create_library(state.func_id.func_qualname
            )
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    merv__pwh = state.func_ir
    typemap = state.typemap
    mbhng__sgel = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    zjn__dwnnv = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            merv__pwh, typemap, mbhng__sgel, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            yqbqi__dcpzq = lowering.Lower(targetctx, library, fndesc,
                merv__pwh, metadata=metadata)
            yqbqi__dcpzq.lower()
            if not flags.no_cpython_wrapper:
                yqbqi__dcpzq.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(mbhng__sgel, (types.Optional, types.
                        Generator)):
                        pass
                    else:
                        yqbqi__dcpzq.create_cfunc_wrapper()
            env = yqbqi__dcpzq.env
            lqqud__upk = yqbqi__dcpzq.call_helper
            del yqbqi__dcpzq
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, lqqud__upk, cfunc=None, env=env)
        else:
            afj__amugq = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(afj__amugq, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, lqqud__upk, cfunc=afj__amugq,
                env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        fsnvg__ovvi = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = fsnvg__ovvi - zjn__dwnnv
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
        lsyd__acedu = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, lsyd__acedu),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            bfq__xlcc.do_break()
        wni__arm = c.builder.icmp_signed('!=', lsyd__acedu, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(wni__arm, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, lsyd__acedu)
                c.pyapi.decref(lsyd__acedu)
                bfq__xlcc.do_break()
        c.pyapi.decref(lsyd__acedu)
    qux__ncaba, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(qux__ncaba, likely=True) as (qdpdd__xcvf,
        wpul__phokm):
        with qdpdd__xcvf:
            list.size = size
            kdo__lwesi = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                kdo__lwesi), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        kdo__lwesi))
                    with cgutils.for_range(c.builder, size) as bfq__xlcc:
                        itemobj = c.pyapi.list_getitem(obj, bfq__xlcc.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        zpme__znmoe = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(zpme__znmoe.is_error, likely
                            =False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            bfq__xlcc.do_break()
                        list.setitem(bfq__xlcc.index, zpme__znmoe.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with wpul__phokm:
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
    kaur__pqe, udmqr__jxqjw, aky__vjt, uxcvs__dhza, cfz__ueev = (
        compile_time_get_string_data(literal_string))
    jpf__qhq = builder.module
    gv = context.insert_const_bytes(jpf__qhq, kaur__pqe)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        udmqr__jxqjw), context.get_constant(types.int32, aky__vjt), context
        .get_constant(types.uint32, uxcvs__dhza), context.get_constant(
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
    olz__qrlmo = None
    if isinstance(shape, types.Integer):
        olz__qrlmo = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(ppha__iik, (types.Integer, types.IntEnumMember)) for
            ppha__iik in shape):
            olz__qrlmo = len(shape)
    return olz__qrlmo


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
            olz__qrlmo = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if olz__qrlmo == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(olz__qrlmo)
                    )
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            pgbn__lux = self._get_names(x)
            if len(pgbn__lux) != 0:
                return pgbn__lux[0]
            return pgbn__lux
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    pgbn__lux = self._get_names(obj)
    if len(pgbn__lux) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(pgbn__lux[0])


def get_equiv_set(self, obj):
    pgbn__lux = self._get_names(obj)
    if len(pgbn__lux) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(pgbn__lux[0])


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
    cwji__hti = []
    for oskl__vdntp in func_ir.arg_names:
        if oskl__vdntp in typemap and isinstance(typemap[oskl__vdntp],
            types.containers.UniTuple) and typemap[oskl__vdntp].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(oskl__vdntp))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for crpn__tpzuk in func_ir.blocks.values():
        for stmt in crpn__tpzuk.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    owf__bxsgo = getattr(val, 'code', None)
                    if owf__bxsgo is not None:
                        if getattr(val, 'closure', None) is not None:
                            mdeeo__ksk = '<creating a function from a closure>'
                            ouqg__hqhii = ''
                        else:
                            mdeeo__ksk = owf__bxsgo.co_name
                            ouqg__hqhii = '(%s) ' % mdeeo__ksk
                    else:
                        mdeeo__ksk = '<could not ascertain use case>'
                        ouqg__hqhii = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (mdeeo__ksk, ouqg__hqhii))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                cvi__cjpj = False
                if isinstance(val, pytypes.FunctionType):
                    cvi__cjpj = val in {numba.gdb, numba.gdb_init}
                if not cvi__cjpj:
                    cvi__cjpj = getattr(val, '_name', '') == 'gdb_internal'
                if cvi__cjpj:
                    cwji__hti.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    ilupt__ltfve = func_ir.get_definition(var)
                    kpqm__ajh = guard(find_callname, func_ir, ilupt__ltfve)
                    if kpqm__ajh and kpqm__ajh[1] == 'numpy':
                        ty = getattr(numpy, kpqm__ajh[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    gmhtp__nvcqy = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(gmhtp__nvcqy), loc=stmt.loc)
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
    if len(cwji__hti) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        xyn__wdq = '\n'.join([x.strformat() for x in cwji__hti])
        raise errors.UnsupportedError(msg % xyn__wdq)


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
    egor__fkca, ads__ztcmq = next(iter(val.items()))
    rdp__vui = typeof_impl(egor__fkca, c)
    ztr__vacg = typeof_impl(ads__ztcmq, c)
    if rdp__vui is None or ztr__vacg is None:
        raise ValueError(
            f'Cannot type dict element type {type(egor__fkca)}, {type(ads__ztcmq)}'
            )
    return types.DictType(rdp__vui, ztr__vacg)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    tiu__iwyc = cgutils.alloca_once_value(c.builder, val)
    zdqom__hlfyc = c.pyapi.object_hasattr_string(val, '_opaque')
    iuio__alzrz = c.builder.icmp_unsigned('==', zdqom__hlfyc, lir.Constant(
        zdqom__hlfyc.type, 0))
    uguh__yyf = typ.key_type
    ejr__ojg = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(uguh__yyf, ejr__ojg)

    def copy_dict(out_dict, in_dict):
        for egor__fkca, ads__ztcmq in in_dict.items():
            out_dict[egor__fkca] = ads__ztcmq
    with c.builder.if_then(iuio__alzrz):
        qjh__cxwu = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        bfqs__ptdkt = c.pyapi.call_function_objargs(qjh__cxwu, [])
        givff__awtnn = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(givff__awtnn, [bfqs__ptdkt, val])
        c.builder.store(bfqs__ptdkt, tiu__iwyc)
    val = c.builder.load(tiu__iwyc)
    lbzi__xorw = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    kbd__whtky = c.pyapi.object_type(val)
    mlof__qddc = c.builder.icmp_unsigned('==', kbd__whtky, lbzi__xorw)
    with c.builder.if_else(mlof__qddc) as (scuw__zbyo, ejhri__rhnjy):
        with scuw__zbyo:
            fjx__nugg = c.pyapi.object_getattr_string(val, '_opaque')
            kcolu__ert = types.MemInfoPointer(types.voidptr)
            zpme__znmoe = c.unbox(kcolu__ert, fjx__nugg)
            mi = zpme__znmoe.value
            uzsb__fqbg = kcolu__ert, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *uzsb__fqbg)
            ucyrz__dwnvk = context.get_constant_null(uzsb__fqbg[1])
            args = mi, ucyrz__dwnvk
            wbcon__gtbod, kqwh__zoj = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, kqwh__zoj)
            c.pyapi.decref(fjx__nugg)
            owa__xkgk = c.builder.basic_block
        with ejhri__rhnjy:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", kbd__whtky, lbzi__xorw)
            jttsj__qsoa = c.builder.basic_block
    ifvg__iscei = c.builder.phi(kqwh__zoj.type)
    lwan__qhpom = c.builder.phi(wbcon__gtbod.type)
    ifvg__iscei.add_incoming(kqwh__zoj, owa__xkgk)
    ifvg__iscei.add_incoming(kqwh__zoj.type(None), jttsj__qsoa)
    lwan__qhpom.add_incoming(wbcon__gtbod, owa__xkgk)
    lwan__qhpom.add_incoming(cgutils.true_bit, jttsj__qsoa)
    c.pyapi.decref(lbzi__xorw)
    c.pyapi.decref(kbd__whtky)
    with c.builder.if_then(iuio__alzrz):
        c.pyapi.decref(val)
    return NativeValue(ifvg__iscei, is_error=lwan__qhpom)


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
    hsx__gra = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=hsx__gra, name=updatevar)
    rfx__qql = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=rfx__qql, name=res)


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
        for egor__fkca, ads__ztcmq in other.items():
            d[egor__fkca] = ads__ztcmq
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
    ouqg__hqhii = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(ouqg__hqhii, res)


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
    unb__koq = PassManager(name)
    if state.func_ir is None:
        unb__koq.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            unb__koq.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        unb__koq.add_pass(FixupArgs, 'fix up args')
    unb__koq.add_pass(IRProcessing, 'processing IR')
    unb__koq.add_pass(WithLifting, 'Handle with contexts')
    unb__koq.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        unb__koq.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        unb__koq.add_pass(DeadBranchPrune, 'dead branch pruning')
        unb__koq.add_pass(GenericRewrites, 'nopython rewrites')
    unb__koq.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    unb__koq.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        unb__koq.add_pass(DeadBranchPrune, 'dead branch pruning')
    unb__koq.add_pass(FindLiterallyCalls, 'find literally calls')
    unb__koq.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        unb__koq.add_pass(ReconstructSSA, 'ssa')
    unb__koq.add_pass(LiteralPropagationSubPipelinePass, 'Literal propagation')
    unb__koq.finalize()
    return unb__koq


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
    a, fjrn__egrh = args
    if isinstance(a, types.List) and isinstance(fjrn__egrh, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(fjrn__egrh, types.List):
        return signature(fjrn__egrh, types.intp, fjrn__egrh)


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
        rtm__wkyrw, rqhc__faobm = 0, 1
    else:
        rtm__wkyrw, rqhc__faobm = 1, 0
    sfw__dmrsj = ListInstance(context, builder, sig.args[rtm__wkyrw], args[
        rtm__wkyrw])
    fkz__zcps = sfw__dmrsj.size
    yavd__purb = args[rqhc__faobm]
    kdo__lwesi = lir.Constant(yavd__purb.type, 0)
    yavd__purb = builder.select(cgutils.is_neg_int(builder, yavd__purb),
        kdo__lwesi, yavd__purb)
    owcx__yyif = builder.mul(yavd__purb, fkz__zcps)
    tes__xstj = ListInstance.allocate(context, builder, sig.return_type,
        owcx__yyif)
    tes__xstj.size = owcx__yyif
    with cgutils.for_range_slice(builder, kdo__lwesi, owcx__yyif, fkz__zcps,
        inc=True) as (snjwy__fef, _):
        with cgutils.for_range(builder, fkz__zcps) as bfq__xlcc:
            value = sfw__dmrsj.getitem(bfq__xlcc.index)
            tes__xstj.setitem(builder.add(bfq__xlcc.index, snjwy__fef),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, tes__xstj.value)


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
    bovhu__cxrc = first.unify(self, second)
    if bovhu__cxrc is not None:
        return bovhu__cxrc
    bovhu__cxrc = second.unify(self, first)
    if bovhu__cxrc is not None:
        return bovhu__cxrc
    ibseo__rglb = self.can_convert(fromty=first, toty=second)
    if ibseo__rglb is not None and ibseo__rglb <= Conversion.safe:
        return second
    ibseo__rglb = self.can_convert(fromty=second, toty=first)
    if ibseo__rglb is not None and ibseo__rglb <= Conversion.safe:
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
    owcx__yyif = payload.used
    listobj = c.pyapi.list_new(owcx__yyif)
    qux__ncaba = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(qux__ncaba, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(owcx__yyif
            .type, 0))
        with payload._iterate() as bfq__xlcc:
            i = c.builder.load(index)
            item = bfq__xlcc.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return qux__ncaba, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    hmp__kkq = h.type
    aazx__zpnv = self.mask
    dtype = self._ty.dtype
    yqgk__ryg = context.typing_context
    fnty = yqgk__ryg.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(yqgk__ryg, (dtype, dtype), {})
    rze__zpsen = context.get_function(fnty, sig)
    dqeg__yovit = ir.Constant(hmp__kkq, 1)
    qrvnn__yfhdk = ir.Constant(hmp__kkq, 5)
    tcv__myfsf = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, aazx__zpnv))
    if for_insert:
        pjum__lzo = aazx__zpnv.type(-1)
        wch__ffr = cgutils.alloca_once_value(builder, pjum__lzo)
    ycn__cyyz = builder.append_basic_block('lookup.body')
    nia__afb = builder.append_basic_block('lookup.found')
    ssze__vuw = builder.append_basic_block('lookup.not_found')
    znxs__rtfi = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        unxp__vsjlu = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, unxp__vsjlu)):
            qezw__idej = rze__zpsen(builder, (item, entry.key))
            with builder.if_then(qezw__idej):
                builder.branch(nia__afb)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, unxp__vsjlu)):
            builder.branch(ssze__vuw)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, unxp__vsjlu)):
                pflev__owkcd = builder.load(wch__ffr)
                pflev__owkcd = builder.select(builder.icmp_unsigned('==',
                    pflev__owkcd, pjum__lzo), i, pflev__owkcd)
                builder.store(pflev__owkcd, wch__ffr)
    with cgutils.for_range(builder, ir.Constant(hmp__kkq, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, dqeg__yovit)
        i = builder.and_(i, aazx__zpnv)
        builder.store(i, index)
    builder.branch(ycn__cyyz)
    with builder.goto_block(ycn__cyyz):
        i = builder.load(index)
        check_entry(i)
        sufi__vew = builder.load(tcv__myfsf)
        sufi__vew = builder.lshr(sufi__vew, qrvnn__yfhdk)
        i = builder.add(dqeg__yovit, builder.mul(i, qrvnn__yfhdk))
        i = builder.and_(aazx__zpnv, builder.add(i, sufi__vew))
        builder.store(i, index)
        builder.store(sufi__vew, tcv__myfsf)
        builder.branch(ycn__cyyz)
    with builder.goto_block(ssze__vuw):
        if for_insert:
            i = builder.load(index)
            pflev__owkcd = builder.load(wch__ffr)
            i = builder.select(builder.icmp_unsigned('==', pflev__owkcd,
                pjum__lzo), i, pflev__owkcd)
            builder.store(i, index)
        builder.branch(znxs__rtfi)
    with builder.goto_block(nia__afb):
        builder.branch(znxs__rtfi)
    builder.position_at_end(znxs__rtfi)
    cvi__cjpj = builder.phi(ir.IntType(1), 'found')
    cvi__cjpj.add_incoming(cgutils.true_bit, nia__afb)
    cvi__cjpj.add_incoming(cgutils.false_bit, ssze__vuw)
    return cvi__cjpj, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    qzwjf__bhg = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    cdcml__nqa = payload.used
    dqeg__yovit = ir.Constant(cdcml__nqa.type, 1)
    cdcml__nqa = payload.used = builder.add(cdcml__nqa, dqeg__yovit)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, qzwjf__bhg), likely=True):
        payload.fill = builder.add(payload.fill, dqeg__yovit)
    if do_resize:
        self.upsize(cdcml__nqa)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    cvi__cjpj, i = payload._lookup(item, h, for_insert=True)
    fjan__svgvj = builder.not_(cvi__cjpj)
    with builder.if_then(fjan__svgvj):
        entry = payload.get_entry(i)
        qzwjf__bhg = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        cdcml__nqa = payload.used
        dqeg__yovit = ir.Constant(cdcml__nqa.type, 1)
        cdcml__nqa = payload.used = builder.add(cdcml__nqa, dqeg__yovit)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, qzwjf__bhg), likely=True):
            payload.fill = builder.add(payload.fill, dqeg__yovit)
        if do_resize:
            self.upsize(cdcml__nqa)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    cdcml__nqa = payload.used
    dqeg__yovit = ir.Constant(cdcml__nqa.type, 1)
    cdcml__nqa = payload.used = self._builder.sub(cdcml__nqa, dqeg__yovit)
    if do_resize:
        self.downsize(cdcml__nqa)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    adtqh__qrdk = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, adtqh__qrdk)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    dxygk__nczu = payload
    qux__ncaba = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(qux__ncaba), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with dxygk__nczu._iterate() as bfq__xlcc:
        entry = bfq__xlcc.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(dxygk__nczu.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as bfq__xlcc:
        entry = bfq__xlcc.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    qux__ncaba = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(qux__ncaba), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    qux__ncaba = cgutils.alloca_once_value(builder, cgutils.true_bit)
    hmp__kkq = context.get_value_type(types.intp)
    kdo__lwesi = ir.Constant(hmp__kkq, 0)
    dqeg__yovit = ir.Constant(hmp__kkq, 1)
    pkwmq__podbr = context.get_data_type(types.SetPayload(self._ty))
    lef__vnsmb = context.get_abi_sizeof(pkwmq__podbr)
    rijov__dsjj = self._entrysize
    lef__vnsmb -= rijov__dsjj
    bwf__nzi, zroyz__pmmt = cgutils.muladd_with_overflow(builder, nentries,
        ir.Constant(hmp__kkq, rijov__dsjj), ir.Constant(hmp__kkq, lef__vnsmb))
    with builder.if_then(zroyz__pmmt, likely=False):
        builder.store(cgutils.false_bit, qux__ncaba)
    with builder.if_then(builder.load(qux__ncaba), likely=True):
        if realloc:
            nzlg__sgg = self._set.meminfo
            mlkvs__bvecr = context.nrt.meminfo_varsize_alloc(builder,
                nzlg__sgg, size=bwf__nzi)
            sxitj__lda = cgutils.is_null(builder, mlkvs__bvecr)
        else:
            fbj__dzlax = _imp_dtor(context, builder.module, self._ty)
            nzlg__sgg = context.nrt.meminfo_new_varsize_dtor(builder,
                bwf__nzi, builder.bitcast(fbj__dzlax, cgutils.voidptr_t))
            sxitj__lda = cgutils.is_null(builder, nzlg__sgg)
        with builder.if_else(sxitj__lda, likely=False) as (zcdwh__mncs,
            qdpdd__xcvf):
            with zcdwh__mncs:
                builder.store(cgutils.false_bit, qux__ncaba)
            with qdpdd__xcvf:
                if not realloc:
                    self._set.meminfo = nzlg__sgg
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, bwf__nzi, 255)
                payload.used = kdo__lwesi
                payload.fill = kdo__lwesi
                payload.finger = kdo__lwesi
                dgk__hiixs = builder.sub(nentries, dqeg__yovit)
                payload.mask = dgk__hiixs
    return builder.load(qux__ncaba)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    qux__ncaba = cgutils.alloca_once_value(builder, cgutils.true_bit)
    hmp__kkq = context.get_value_type(types.intp)
    kdo__lwesi = ir.Constant(hmp__kkq, 0)
    dqeg__yovit = ir.Constant(hmp__kkq, 1)
    pkwmq__podbr = context.get_data_type(types.SetPayload(self._ty))
    lef__vnsmb = context.get_abi_sizeof(pkwmq__podbr)
    rijov__dsjj = self._entrysize
    lef__vnsmb -= rijov__dsjj
    aazx__zpnv = src_payload.mask
    nentries = builder.add(dqeg__yovit, aazx__zpnv)
    bwf__nzi = builder.add(ir.Constant(hmp__kkq, lef__vnsmb), builder.mul(
        ir.Constant(hmp__kkq, rijov__dsjj), nentries))
    with builder.if_then(builder.load(qux__ncaba), likely=True):
        fbj__dzlax = _imp_dtor(context, builder.module, self._ty)
        nzlg__sgg = context.nrt.meminfo_new_varsize_dtor(builder, bwf__nzi,
            builder.bitcast(fbj__dzlax, cgutils.voidptr_t))
        sxitj__lda = cgutils.is_null(builder, nzlg__sgg)
        with builder.if_else(sxitj__lda, likely=False) as (zcdwh__mncs,
            qdpdd__xcvf):
            with zcdwh__mncs:
                builder.store(cgutils.false_bit, qux__ncaba)
            with qdpdd__xcvf:
                self._set.meminfo = nzlg__sgg
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = kdo__lwesi
                payload.mask = aazx__zpnv
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, rijov__dsjj)
                with src_payload._iterate() as bfq__xlcc:
                    context.nrt.incref(builder, self._ty.dtype, bfq__xlcc.
                        entry.key)
    return builder.load(qux__ncaba)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    atl__ylt = context.get_value_type(types.voidptr)
    zzfp__lkd = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [atl__ylt, zzfp__lkd, atl__ylt])
    cjmmw__ghgs = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=cjmmw__ghgs)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        ioaun__aseq = builder.bitcast(fn.args[0], cgutils.voidptr_t.
            as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, ioaun__aseq)
        with payload._iterate() as bfq__xlcc:
            entry = bfq__xlcc.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    fgh__lum, = sig.args
    huop__exa, = args
    xhv__rige = numba.core.imputils.call_len(context, builder, fgh__lum,
        huop__exa)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, xhv__rige)
    with numba.core.imputils.for_iter(context, builder, fgh__lum, huop__exa
        ) as bfq__xlcc:
        inst.add(bfq__xlcc.value)
        context.nrt.decref(builder, set_type.dtype, bfq__xlcc.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    fgh__lum = sig.args[1]
    huop__exa = args[1]
    xhv__rige = numba.core.imputils.call_len(context, builder, fgh__lum,
        huop__exa)
    if xhv__rige is not None:
        nimbi__lzxz = builder.add(inst.payload.used, xhv__rige)
        inst.upsize(nimbi__lzxz)
    with numba.core.imputils.for_iter(context, builder, fgh__lum, huop__exa
        ) as bfq__xlcc:
        jofba__wgqv = context.cast(builder, bfq__xlcc.value, fgh__lum.dtype,
            inst.dtype)
        inst.add(jofba__wgqv)
        context.nrt.decref(builder, fgh__lum.dtype, bfq__xlcc.value)
    if xhv__rige is not None:
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
    rdzu__xiwt = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, rdzu__xiwt, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    afj__amugq = target_context.get_executable(library, fndesc, env)
    epng__easbe = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=afj__amugq, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return epng__easbe


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
    lines = inspect.getsource(numba.core.types.containers.Bytes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '977423d833eeb4b8fd0c87f55dce7251c107d8d10793fe5723de6e5452da32e2':
        warnings.warn('numba.core.types.containers.Bytes has changed')
numba.core.types.containers.Bytes.slice_is_copy = True
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
        bzuz__iofp = MPI.COMM_WORLD
        lyth__vlwic = None
        if bzuz__iofp.Get_rank() == 0:
            try:
                rvpz__ygpbd = self.get_cache_path()
                os.makedirs(rvpz__ygpbd, exist_ok=True)
                tempfile.TemporaryFile(dir=rvpz__ygpbd).close()
            except Exception as e:
                lyth__vlwic = e
        lyth__vlwic = bzuz__iofp.bcast(lyth__vlwic)
        if isinstance(lyth__vlwic, Exception):
            raise lyth__vlwic
    numba.core.caching._CacheLocator.ensure_cache_path = _ensure_cache_path


def _analyze_op_call_builtins_len(self, scope, equiv_set, loc, args, kws):
    from numba.parfors.array_analysis import ArrayAnalysis
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


def generic(self, args, kws):
    assert not kws
    val, = args
    if isinstance(val, (types.Buffer, types.BaseTuple)) and not isinstance(val,
        types.Bytes):
        return signature(types.intp, val)
    elif isinstance(val, types.RangeType):
        return signature(val.dtype, val)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.builtins.Len.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '88d54238ebe0896f4s69b7347105a6a68dec443036a61f9e494c1630c62b0fa76':
        warnings.warn('numba.core.typing.builtins.Len.generic has changed')
numba.core.typing.builtins.Len.generic = generic
from numba.cpython import charseq


def _make_constant_bytes(context, builder, nbytes):
    from llvmlite import ir
    vrl__poew = cgutils.create_struct_proxy(charseq.bytes_type)
    ypp__fwvzi = vrl__poew(context, builder)
    if isinstance(nbytes, int):
        nbytes = ir.Constant(ypp__fwvzi.nitems.type, nbytes)
    ypp__fwvzi.meminfo = context.nrt.meminfo_alloc(builder, nbytes)
    ypp__fwvzi.nitems = nbytes
    ypp__fwvzi.itemsize = ir.Constant(ypp__fwvzi.itemsize.type, 1)
    ypp__fwvzi.data = context.nrt.meminfo_data(builder, ypp__fwvzi.meminfo)
    ypp__fwvzi.parent = cgutils.get_null_value(ypp__fwvzi.parent.type)
    ypp__fwvzi.shape = cgutils.pack_array(builder, [ypp__fwvzi.nitems],
        context.get_value_type(types.intp))
    ypp__fwvzi.strides = cgutils.pack_array(builder, [ir.Constant(
        ypp__fwvzi.strides.type.element, 1)], context.get_value_type(types.
        intp))
    return ypp__fwvzi


if _check_numba_change:
    lines = inspect.getsource(charseq._make_constant_bytes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b3ed23ad58baff7b935912e3e22f4d8af67423d8fd0e5f1836ba0b3028a6eb18':
        warnings.warn('charseq._make_constant_bytes has changed')
charseq._make_constant_bytes = _make_constant_bytes
