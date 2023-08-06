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
    nln__oxcqz = numba.core.bytecode.FunctionIdentity.from_function(func)
    ylg__pcr = numba.core.interpreter.Interpreter(nln__oxcqz)
    alvhl__uwz = numba.core.bytecode.ByteCode(func_id=nln__oxcqz)
    func_ir = ylg__pcr.interpret(alvhl__uwz)
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
        yfsf__chkai = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        yfsf__chkai.run()
    hkt__rpek = numba.core.postproc.PostProcessor(func_ir)
    hkt__rpek.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, aeo__ajjpa in visit_vars_extensions.items():
        if isinstance(stmt, t):
            aeo__ajjpa(stmt, callback, cbdata)
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
    edeb__ibhv = ['ravel', 'transpose', 'reshape']
    for cdz__acik in blocks.values():
        for dst__owat in cdz__acik.body:
            if type(dst__owat) in alias_analysis_extensions:
                aeo__ajjpa = alias_analysis_extensions[type(dst__owat)]
                aeo__ajjpa(dst__owat, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(dst__owat, ir.Assign):
                ezd__ltg = dst__owat.value
                clz__vcsyu = dst__owat.target.name
                if is_immutable_type(clz__vcsyu, typemap):
                    continue
                if isinstance(ezd__ltg, ir.Var
                    ) and clz__vcsyu != ezd__ltg.name:
                    _add_alias(clz__vcsyu, ezd__ltg.name, alias_map,
                        arg_aliases)
                if isinstance(ezd__ltg, ir.Expr) and (ezd__ltg.op == 'cast' or
                    ezd__ltg.op in ['getitem', 'static_getitem']):
                    _add_alias(clz__vcsyu, ezd__ltg.value.name, alias_map,
                        arg_aliases)
                if isinstance(ezd__ltg, ir.Expr
                    ) and ezd__ltg.op == 'inplace_binop':
                    _add_alias(clz__vcsyu, ezd__ltg.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(ezd__ltg, ir.Expr
                    ) and ezd__ltg.op == 'getattr' and ezd__ltg.attr in ['T',
                    'ctypes', 'flat']:
                    _add_alias(clz__vcsyu, ezd__ltg.value.name, alias_map,
                        arg_aliases)
                if isinstance(ezd__ltg, ir.Expr
                    ) and ezd__ltg.op == 'getattr' and ezd__ltg.attr not in [
                    'shape'] and ezd__ltg.value.name in arg_aliases:
                    _add_alias(clz__vcsyu, ezd__ltg.value.name, alias_map,
                        arg_aliases)
                if isinstance(ezd__ltg, ir.Expr
                    ) and ezd__ltg.op == 'getattr' and ezd__ltg.attr in ('loc',
                    'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(clz__vcsyu, ezd__ltg.value.name, alias_map,
                        arg_aliases)
                if isinstance(ezd__ltg, ir.Expr) and ezd__ltg.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(clz__vcsyu, typemap):
                    for aeu__ejw in ezd__ltg.items:
                        _add_alias(clz__vcsyu, aeu__ejw.name, alias_map,
                            arg_aliases)
                if isinstance(ezd__ltg, ir.Expr) and ezd__ltg.op == 'call':
                    ctbzn__niyru = guard(find_callname, func_ir, ezd__ltg,
                        typemap)
                    if ctbzn__niyru is None:
                        continue
                    akp__ggda, eufd__lkju = ctbzn__niyru
                    if ctbzn__niyru in alias_func_extensions:
                        rua__ougpp = alias_func_extensions[ctbzn__niyru]
                        rua__ougpp(clz__vcsyu, ezd__ltg.args, alias_map,
                            arg_aliases)
                    if eufd__lkju == 'numpy' and akp__ggda in edeb__ibhv:
                        _add_alias(clz__vcsyu, ezd__ltg.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(eufd__lkju, ir.Var
                        ) and akp__ggda in edeb__ibhv:
                        _add_alias(clz__vcsyu, eufd__lkju.name, alias_map,
                            arg_aliases)
    teoan__nus = copy.deepcopy(alias_map)
    for aeu__ejw in teoan__nus:
        for uegyc__qet in teoan__nus[aeu__ejw]:
            alias_map[aeu__ejw] |= alias_map[uegyc__qet]
        for uegyc__qet in teoan__nus[aeu__ejw]:
            alias_map[uegyc__qet] = alias_map[aeu__ejw]
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
    tazmc__omlyd = compute_cfg_from_blocks(func_ir.blocks)
    dmcgx__jfwy = compute_use_defs(func_ir.blocks)
    uyq__notfl = compute_live_map(tazmc__omlyd, func_ir.blocks, dmcgx__jfwy
        .usemap, dmcgx__jfwy.defmap)
    kpd__xxgki = True
    while kpd__xxgki:
        kpd__xxgki = False
        for label, block in func_ir.blocks.items():
            lives = {aeu__ejw.name for aeu__ejw in block.terminator.list_vars()
                }
            for hej__douwq, folv__nbl in tazmc__omlyd.successors(label):
                lives |= uyq__notfl[hej__douwq]
            bwaw__vkbhz = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    clz__vcsyu = stmt.target
                    jwk__brl = stmt.value
                    if clz__vcsyu.name not in lives:
                        if isinstance(jwk__brl, ir.Expr
                            ) and jwk__brl.op == 'make_function':
                            continue
                        if isinstance(jwk__brl, ir.Expr
                            ) and jwk__brl.op == 'getattr':
                            continue
                        if isinstance(jwk__brl, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(clz__vcsyu,
                            None), types.Function):
                            continue
                        if isinstance(jwk__brl, ir.Expr
                            ) and jwk__brl.op == 'build_map':
                            continue
                        if isinstance(jwk__brl, ir.Expr
                            ) and jwk__brl.op == 'build_tuple':
                            continue
                    if isinstance(jwk__brl, ir.Var
                        ) and clz__vcsyu.name == jwk__brl.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    tsuuy__jhul = analysis.ir_extension_usedefs[type(stmt)]
                    dpv__mjtik, pri__ewnyo = tsuuy__jhul(stmt)
                    lives -= pri__ewnyo
                    lives |= dpv__mjtik
                else:
                    lives |= {aeu__ejw.name for aeu__ejw in stmt.list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(clz__vcsyu.name)
                bwaw__vkbhz.append(stmt)
            bwaw__vkbhz.reverse()
            if len(block.body) != len(bwaw__vkbhz):
                kpd__xxgki = True
            block.body = bwaw__vkbhz


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    cib__smvzw = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (cib__smvzw,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    iezz__fakvd = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), iezz__fakvd)


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
            for kfvh__pqewq in fnty.templates:
                self._inline_overloads.update(kfvh__pqewq._inline_overloads)
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
    iezz__fakvd = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), iezz__fakvd)
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
    efzo__sdi, fot__kmi = self._get_impl(args, kws)
    if efzo__sdi is None:
        return
    xnh__yume = types.Dispatcher(efzo__sdi)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        reeb__jqm = efzo__sdi._compiler
        flags = compiler.Flags()
        hsp__rdxph = reeb__jqm.targetdescr.typing_context
        lwjm__lwgzc = reeb__jqm.targetdescr.target_context
        wzf__uzi = reeb__jqm.pipeline_class(hsp__rdxph, lwjm__lwgzc, None,
            None, None, flags, None)
        juieu__elhc = InlineWorker(hsp__rdxph, lwjm__lwgzc, reeb__jqm.
            locals, wzf__uzi, flags, None)
        edt__hvwmf = xnh__yume.dispatcher.get_call_template
        kfvh__pqewq, pumve__dqknx, plfzb__qceg, kws = edt__hvwmf(fot__kmi, kws)
        if plfzb__qceg in self._inline_overloads:
            return self._inline_overloads[plfzb__qceg]['iinfo'].signature
        ir = juieu__elhc.run_untyped_passes(xnh__yume.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, lwjm__lwgzc, ir, plfzb__qceg, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, plfzb__qceg, None)
        self._inline_overloads[sig.args] = {'folded_args': plfzb__qceg}
        cilqe__plumr = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = cilqe__plumr
        if not self._inline.is_always_inline:
            sig = xnh__yume.get_call_type(self.context, fot__kmi, kws)
            self._compiled_overloads[sig.args] = xnh__yume.get_overload(sig)
        zycv__ify = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': plfzb__qceg,
            'iinfo': zycv__ify}
    else:
        sig = xnh__yume.get_call_type(self.context, fot__kmi, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = xnh__yume.get_overload(sig)
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
    ovi__hla = [True, False]
    tzafr__ulww = [False, True]
    ohgf__yurwl = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    enzea__lgsck = get_local_target(context)
    ldfsu__krtl = utils.order_by_target_specificity(enzea__lgsck, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for qhesh__hugg in ldfsu__krtl:
        hev__chfw = qhesh__hugg(context)
        fprl__pdibc = ovi__hla if hev__chfw.prefer_literal else tzafr__ulww
        fprl__pdibc = [True] if getattr(hev__chfw, '_no_unliteral', False
            ) else fprl__pdibc
        for yjmo__miwq in fprl__pdibc:
            try:
                if yjmo__miwq:
                    sig = hev__chfw.apply(args, kws)
                else:
                    czlsw__swgs = tuple([_unlit_non_poison(a) for a in args])
                    mpki__osvmx = {nekm__xnq: _unlit_non_poison(aeu__ejw) for
                        nekm__xnq, aeu__ejw in kws.items()}
                    sig = hev__chfw.apply(czlsw__swgs, mpki__osvmx)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    ohgf__yurwl.add_error(hev__chfw, False, e, yjmo__miwq)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = hev__chfw.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    uogd__tmtuh = getattr(hev__chfw, 'cases', None)
                    if uogd__tmtuh is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            uogd__tmtuh)
                    else:
                        msg = 'No match.'
                    ohgf__yurwl.add_error(hev__chfw, True, msg, yjmo__miwq)
    ohgf__yurwl.raise_error()


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
    kfvh__pqewq = self.template(context)
    gdjxj__uurp = None
    qlp__ntz = None
    oaopl__rska = None
    fprl__pdibc = [True, False] if kfvh__pqewq.prefer_literal else [False, True
        ]
    fprl__pdibc = [True] if getattr(kfvh__pqewq, '_no_unliteral', False
        ) else fprl__pdibc
    for yjmo__miwq in fprl__pdibc:
        if yjmo__miwq:
            try:
                oaopl__rska = kfvh__pqewq.apply(args, kws)
            except Exception as xydjh__zrm:
                if isinstance(xydjh__zrm, errors.ForceLiteralArg):
                    raise xydjh__zrm
                gdjxj__uurp = xydjh__zrm
                oaopl__rska = None
            else:
                break
        else:
            ula__fxz = tuple([_unlit_non_poison(a) for a in args])
            qhczw__fowzv = {nekm__xnq: _unlit_non_poison(aeu__ejw) for 
                nekm__xnq, aeu__ejw in kws.items()}
            frfap__lya = ula__fxz == args and kws == qhczw__fowzv
            if not frfap__lya and oaopl__rska is None:
                try:
                    oaopl__rska = kfvh__pqewq.apply(ula__fxz, qhczw__fowzv)
                except Exception as xydjh__zrm:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        xydjh__zrm, errors.NumbaError):
                        raise xydjh__zrm
                    if isinstance(xydjh__zrm, errors.ForceLiteralArg):
                        if kfvh__pqewq.prefer_literal:
                            raise xydjh__zrm
                    qlp__ntz = xydjh__zrm
                else:
                    break
    if oaopl__rska is None and (qlp__ntz is not None or gdjxj__uurp is not None
        ):
        jgf__bou = '- Resolution failure for {} arguments:\n{}\n'
        wsx__zgi = _termcolor.highlight(jgf__bou)
        if numba.core.config.DEVELOPER_MODE:
            xbepe__ugv = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    otpxm__kbbui = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    otpxm__kbbui = ['']
                rzyeu__dmnkf = '\n{}'.format(2 * xbepe__ugv)
                lmz__pfd = _termcolor.reset(rzyeu__dmnkf + rzyeu__dmnkf.
                    join(_bt_as_lines(otpxm__kbbui)))
                return _termcolor.reset(lmz__pfd)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            jsi__dldt = str(e)
            jsi__dldt = jsi__dldt if jsi__dldt else str(repr(e)) + add_bt(e)
            lkzv__fhl = errors.TypingError(textwrap.dedent(jsi__dldt))
            return wsx__zgi.format(literalness, str(lkzv__fhl))
        import bodo
        if isinstance(gdjxj__uurp, bodo.utils.typing.BodoError):
            raise gdjxj__uurp
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', gdjxj__uurp) +
                nested_msg('non-literal', qlp__ntz))
        else:
            if 'missing a required argument' in gdjxj__uurp.msg:
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
            raise errors.TypingError(msg, loc=gdjxj__uurp.loc)
    return oaopl__rska


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
    akp__ggda = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=akp__ggda)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            fhs__jbpf = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), fhs__jbpf)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    kzikr__fkjp = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            kzikr__fkjp.append(types.Omitted(a.value))
        else:
            kzikr__fkjp.append(self.typeof_pyval(a))
    zgp__whyjd = None
    try:
        error = None
        zgp__whyjd = self.compile(tuple(kzikr__fkjp))
    except errors.ForceLiteralArg as e:
        fyhh__eslu = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if fyhh__eslu:
            aek__rhgj = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            xqe__biltd = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(fyhh__eslu))
            raise errors.CompilerError(aek__rhgj.format(xqe__biltd))
        fot__kmi = []
        try:
            for i, aeu__ejw in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        fot__kmi.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        fot__kmi.append(types.literal(args[i]))
                else:
                    fot__kmi.append(args[i])
            args = fot__kmi
        except (OSError, FileNotFoundError) as wstlj__wtlkm:
            error = FileNotFoundError(str(wstlj__wtlkm) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                zgp__whyjd = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        ryj__dex = []
        for i, ihiyp__vmhl in enumerate(args):
            val = ihiyp__vmhl.value if isinstance(ihiyp__vmhl, numba.core.
                dispatcher.OmittedArg) else ihiyp__vmhl
            try:
                elthh__gowrr = typeof(val, Purpose.argument)
            except ValueError as yrc__oyii:
                ryj__dex.append((i, str(yrc__oyii)))
            else:
                if elthh__gowrr is None:
                    ryj__dex.append((i,
                        f'cannot determine Numba type of value {val}'))
        if ryj__dex:
            gtisr__hrdvq = '\n'.join(f'- argument {i}: {qdhkb__ptn}' for i,
                qdhkb__ptn in ryj__dex)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{gtisr__hrdvq}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                ijq__dofpt = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                gzqrs__lyckn = False
                for dyovw__ljhau in ijq__dofpt:
                    if dyovw__ljhau in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        gzqrs__lyckn = True
                        break
                if not gzqrs__lyckn:
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
                fhs__jbpf = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), fhs__jbpf)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return zgp__whyjd


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
    for awx__ujcf in cres.library._codegen._engine._defined_symbols:
        if awx__ujcf.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in awx__ujcf and (
            'bodo_gb_udf_update_local' in awx__ujcf or 
            'bodo_gb_udf_combine' in awx__ujcf or 'bodo_gb_udf_eval' in
            awx__ujcf or 'bodo_gb_apply_general_udfs' in awx__ujcf):
            gb_agg_cfunc_addr[awx__ujcf
                ] = cres.library.get_pointer_to_function(awx__ujcf)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for awx__ujcf in cres.library._codegen._engine._defined_symbols:
        if awx__ujcf.startswith('cfunc') and ('get_join_cond_addr' not in
            awx__ujcf or 'bodo_join_gen_cond' in awx__ujcf):
            join_gen_cond_cfunc_addr[awx__ujcf
                ] = cres.library.get_pointer_to_function(awx__ujcf)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    efzo__sdi = self._get_dispatcher_for_current_target()
    if efzo__sdi is not self:
        return efzo__sdi.compile(sig)
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
            coc__eqmr = self.overloads.get(tuple(args))
            if coc__eqmr is not None:
                return coc__eqmr.entry_point
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
            ese__jacis = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=ese__jacis):
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
                spbtr__xkzv = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in spbtr__xkzv:
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
    voh__dmi = self._final_module
    khj__sgtp = []
    vokt__vqo = 0
    for fn in voh__dmi.functions:
        vokt__vqo += 1
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
            khj__sgtp.append(fn.name)
    if vokt__vqo == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if khj__sgtp:
        voh__dmi = voh__dmi.clone()
        for name in khj__sgtp:
            voh__dmi.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = voh__dmi
    return voh__dmi


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
    for fyv__gkqjz in self.constraints:
        loc = fyv__gkqjz.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                fyv__gkqjz(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                pojb__nxzoz = numba.core.errors.TypingError(str(e), loc=
                    fyv__gkqjz.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(pojb__nxzoz, e))
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
                    pojb__nxzoz = numba.core.errors.TypingError(msg.format(
                        con=fyv__gkqjz, err=str(e)), loc=fyv__gkqjz.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(pojb__nxzoz, e))
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
    for tekj__gvo in self._failures.values():
        for mmh__rft in tekj__gvo:
            if isinstance(mmh__rft.error, ForceLiteralArg):
                raise mmh__rft.error
            if isinstance(mmh__rft.error, bodo.utils.typing.BodoError):
                raise mmh__rft.error
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
    dafg__htb = False
    bwaw__vkbhz = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        tqgz__wka = set()
        jye__ejp = lives & alias_set
        for aeu__ejw in jye__ejp:
            tqgz__wka |= alias_map[aeu__ejw]
        lives_n_aliases = lives | tqgz__wka | arg_aliases
        if type(stmt) in remove_dead_extensions:
            aeo__ajjpa = remove_dead_extensions[type(stmt)]
            stmt = aeo__ajjpa(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                dafg__htb = True
                continue
        if isinstance(stmt, ir.Assign):
            clz__vcsyu = stmt.target
            jwk__brl = stmt.value
            if clz__vcsyu.name not in lives:
                if has_no_side_effect(jwk__brl, lives_n_aliases, call_table):
                    dafg__htb = True
                    continue
                if isinstance(jwk__brl, ir.Expr
                    ) and jwk__brl.op == 'call' and call_table[jwk__brl.
                    func.name] == ['astype']:
                    ytzu__zhjp = guard(get_definition, func_ir, jwk__brl.func)
                    if (ytzu__zhjp is not None and ytzu__zhjp.op ==
                        'getattr' and isinstance(typemap[ytzu__zhjp.value.
                        name], types.Array) and ytzu__zhjp.attr == 'astype'):
                        dafg__htb = True
                        continue
            if saved_array_analysis and clz__vcsyu.name in lives and is_expr(
                jwk__brl, 'getattr'
                ) and jwk__brl.attr == 'shape' and is_array_typ(typemap[
                jwk__brl.value.name]) and jwk__brl.value.name not in lives:
                gtt__hus = {aeu__ejw: nekm__xnq for nekm__xnq, aeu__ejw in
                    func_ir.blocks.items()}
                if block in gtt__hus:
                    label = gtt__hus[block]
                    gohgf__xzd = saved_array_analysis.get_equiv_set(label)
                    gbt__nqb = gohgf__xzd.get_equiv_set(jwk__brl.value)
                    if gbt__nqb is not None:
                        for aeu__ejw in gbt__nqb:
                            if aeu__ejw.endswith('#0'):
                                aeu__ejw = aeu__ejw[:-2]
                            if aeu__ejw in typemap and is_array_typ(typemap
                                [aeu__ejw]) and aeu__ejw in lives:
                                jwk__brl.value = ir.Var(jwk__brl.value.
                                    scope, aeu__ejw, jwk__brl.value.loc)
                                dafg__htb = True
                                break
            if isinstance(jwk__brl, ir.Var
                ) and clz__vcsyu.name == jwk__brl.name:
                dafg__htb = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                dafg__htb = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            tsuuy__jhul = analysis.ir_extension_usedefs[type(stmt)]
            dpv__mjtik, pri__ewnyo = tsuuy__jhul(stmt)
            lives -= pri__ewnyo
            lives |= dpv__mjtik
        else:
            lives |= {aeu__ejw.name for aeu__ejw in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                uft__dbusv = set()
                if isinstance(jwk__brl, ir.Expr):
                    uft__dbusv = {aeu__ejw.name for aeu__ejw in jwk__brl.
                        list_vars()}
                if clz__vcsyu.name not in uft__dbusv:
                    lives.remove(clz__vcsyu.name)
        bwaw__vkbhz.append(stmt)
    bwaw__vkbhz.reverse()
    block.body = bwaw__vkbhz
    return dafg__htb


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            mpu__oyc, = args
            if isinstance(mpu__oyc, types.IterableType):
                dtype = mpu__oyc.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), mpu__oyc)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    zuhzi__djc = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (zuhzi__djc, self.dtype)
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
        except LiteralTypingError as ocn__yfulb:
            return
    try:
        return literal(value)
    except LiteralTypingError as ocn__yfulb:
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
        lfp__exjf = py_func.__qualname__
    except AttributeError as ocn__yfulb:
        lfp__exjf = py_func.__name__
    mkrx__vfo = inspect.getfile(py_func)
    for cls in self._locator_classes:
        bqg__zzeh = cls.from_function(py_func, mkrx__vfo)
        if bqg__zzeh is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (lfp__exjf, mkrx__vfo))
    self._locator = bqg__zzeh
    lzhfj__dmu = inspect.getfile(py_func)
    vtg__urvjm = os.path.splitext(os.path.basename(lzhfj__dmu))[0]
    if mkrx__vfo.startswith('<ipython-'):
        dkko__efpbm = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', vtg__urvjm, count=1)
        if dkko__efpbm == vtg__urvjm:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        vtg__urvjm = dkko__efpbm
    fmc__ltw = '%s.%s' % (vtg__urvjm, lfp__exjf)
    nbpk__kanzs = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(fmc__ltw, nbpk__kanzs
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    bsyxq__shsi = list(filter(lambda a: self._istuple(a.name), args))
    if len(bsyxq__shsi) == 2 and fn.__name__ == 'add':
        pxb__krsvu = self.typemap[bsyxq__shsi[0].name]
        uvxnw__elnjo = self.typemap[bsyxq__shsi[1].name]
        if pxb__krsvu.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                bsyxq__shsi[1]))
        if uvxnw__elnjo.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                bsyxq__shsi[0]))
        try:
            ljxjp__gznt = [equiv_set.get_shape(x) for x in bsyxq__shsi]
            if None in ljxjp__gznt:
                return None
            uhkpl__ouixy = sum(ljxjp__gznt, ())
            return ArrayAnalysis.AnalyzeResult(shape=uhkpl__ouixy)
        except GuardException as ocn__yfulb:
            return None
    twq__mttby = list(filter(lambda a: self._isarray(a.name), args))
    require(len(twq__mttby) > 0)
    bok__edpaq = [x.name for x in twq__mttby]
    wvc__oweq = [self.typemap[x.name].ndim for x in twq__mttby]
    hlb__nvh = max(wvc__oweq)
    require(hlb__nvh > 0)
    ljxjp__gznt = [equiv_set.get_shape(x) for x in twq__mttby]
    if any(a is None for a in ljxjp__gznt):
        return ArrayAnalysis.AnalyzeResult(shape=twq__mttby[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, twq__mttby))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, ljxjp__gznt,
        bok__edpaq)


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
    yfsp__cin = code_obj.code
    qiblp__nnnj = len(yfsp__cin.co_freevars)
    jasmv__pru = yfsp__cin.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        psx__pnekb, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        jasmv__pru = [aeu__ejw.name for aeu__ejw in psx__pnekb]
    ptrnq__tkl = caller_ir.func_id.func.__globals__
    try:
        ptrnq__tkl = getattr(code_obj, 'globals', ptrnq__tkl)
    except KeyError as ocn__yfulb:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    raoo__lrabk = []
    for x in jasmv__pru:
        try:
            klceg__qvfzd = caller_ir.get_definition(x)
        except KeyError as ocn__yfulb:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(klceg__qvfzd, (ir.Const, ir.Global, ir.FreeVar)):
            val = klceg__qvfzd.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                cib__smvzw = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                ptrnq__tkl[cib__smvzw] = bodo.jit(distributed=False)(val)
                ptrnq__tkl[cib__smvzw].is_nested_func = True
                val = cib__smvzw
            if isinstance(val, CPUDispatcher):
                cib__smvzw = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                ptrnq__tkl[cib__smvzw] = val
                val = cib__smvzw
            raoo__lrabk.append(val)
        elif isinstance(klceg__qvfzd, ir.Expr
            ) and klceg__qvfzd.op == 'make_function':
            rpa__kiap = convert_code_obj_to_function(klceg__qvfzd, caller_ir)
            cib__smvzw = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            ptrnq__tkl[cib__smvzw] = bodo.jit(distributed=False)(rpa__kiap)
            ptrnq__tkl[cib__smvzw].is_nested_func = True
            raoo__lrabk.append(cib__smvzw)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    pzer__xwgf = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        raoo__lrabk)])
    znws__oiyzy = ','.join([('c_%d' % i) for i in range(qiblp__nnnj)])
    yqls__sqhbz = list(yfsp__cin.co_varnames)
    qyw__rlot = 0
    sncxe__zsa = yfsp__cin.co_argcount
    aflz__yax = caller_ir.get_definition(code_obj.defaults)
    if aflz__yax is not None:
        if isinstance(aflz__yax, tuple):
            d = [caller_ir.get_definition(x).value for x in aflz__yax]
            byh__xey = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in aflz__yax.items]
            byh__xey = tuple(d)
        qyw__rlot = len(byh__xey)
    seykb__grhd = sncxe__zsa - qyw__rlot
    gdll__cgjni = ','.join([('%s' % yqls__sqhbz[i]) for i in range(
        seykb__grhd)])
    if qyw__rlot:
        kkeoz__vsbup = [('%s = %s' % (yqls__sqhbz[i + seykb__grhd],
            byh__xey[i])) for i in range(qyw__rlot)]
        gdll__cgjni += ', '
        gdll__cgjni += ', '.join(kkeoz__vsbup)
    return _create_function_from_code_obj(yfsp__cin, pzer__xwgf,
        gdll__cgjni, znws__oiyzy, ptrnq__tkl)


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
    for kze__hghvg, (caysi__etd, rdfxu__mcky) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % rdfxu__mcky)
            mpn__xko = _pass_registry.get(caysi__etd).pass_inst
            if isinstance(mpn__xko, CompilerPass):
                self._runPass(kze__hghvg, mpn__xko, state)
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
                    pipeline_name, rdfxu__mcky)
                nein__hvlj = self._patch_error(msg, e)
                raise nein__hvlj
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
    eeojt__iybh = None
    pri__ewnyo = {}

    def lookup(var, already_seen, varonly=True):
        val = pri__ewnyo.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    xvm__xmnbr = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        clz__vcsyu = stmt.target
        jwk__brl = stmt.value
        pri__ewnyo[clz__vcsyu.name] = jwk__brl
        if isinstance(jwk__brl, ir.Var) and jwk__brl.name in pri__ewnyo:
            jwk__brl = lookup(jwk__brl, set())
        if isinstance(jwk__brl, ir.Expr):
            bqgs__gzz = set(lookup(aeu__ejw, set(), True).name for aeu__ejw in
                jwk__brl.list_vars())
            if name in bqgs__gzz:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(jwk__brl)]
                wbrx__lhdyi = [x for x, xxdq__srxzq in args if xxdq__srxzq.
                    name != name]
                args = [(x, xxdq__srxzq) for x, xxdq__srxzq in args if x !=
                    xxdq__srxzq.name]
                rgrk__bich = dict(args)
                if len(wbrx__lhdyi) == 1:
                    rgrk__bich[wbrx__lhdyi[0]] = ir.Var(clz__vcsyu.scope, 
                        name + '#init', clz__vcsyu.loc)
                replace_vars_inner(jwk__brl, rgrk__bich)
                eeojt__iybh = nodes[i:]
                break
    return eeojt__iybh


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
        fpffe__ajxgj = expand_aliases({aeu__ejw.name for aeu__ejw in stmt.
            list_vars()}, alias_map, arg_aliases)
        gpg__irf = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        opvlt__rndud = expand_aliases({aeu__ejw.name for aeu__ejw in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        kjl__zdrq = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(gpg__irf & opvlt__rndud | kjl__zdrq & fpffe__ajxgj) == 0:
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
    enjys__lrbcb = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            enjys__lrbcb.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                enjys__lrbcb.update(get_parfor_writes(stmt, func_ir))
    return enjys__lrbcb


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    enjys__lrbcb = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        enjys__lrbcb.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        enjys__lrbcb = {aeu__ejw.name for aeu__ejw in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        enjys__lrbcb = {aeu__ejw.name for aeu__ejw in stmt.get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            enjys__lrbcb.update({aeu__ejw.name for aeu__ejw in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        ctbzn__niyru = guard(find_callname, func_ir, stmt.value)
        if ctbzn__niyru in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'
            ), ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            enjys__lrbcb.add(stmt.value.args[0].name)
        if ctbzn__niyru == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            enjys__lrbcb.add(stmt.value.args[1].name)
    return enjys__lrbcb


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
        aeo__ajjpa = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        uazjd__ghpqn = aeo__ajjpa.format(self, msg)
        self.args = uazjd__ghpqn,
    else:
        aeo__ajjpa = _termcolor.errmsg('{0}')
        uazjd__ghpqn = aeo__ajjpa.format(self)
        self.args = uazjd__ghpqn,
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
        for obqm__vsf in options['distributed']:
            dist_spec[obqm__vsf] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for obqm__vsf in options['distributed_block']:
            dist_spec[obqm__vsf] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    fqp__two = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, yybl__elp in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(yybl__elp)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    yst__ndm = {}
    for icczr__rzm in reversed(inspect.getmro(cls)):
        yst__ndm.update(icczr__rzm.__dict__)
    int__bro, eirr__gyreu, nkgi__cnho, yty__dvsob = {}, {}, {}, {}
    for nekm__xnq, aeu__ejw in yst__ndm.items():
        if isinstance(aeu__ejw, pytypes.FunctionType):
            int__bro[nekm__xnq] = aeu__ejw
        elif isinstance(aeu__ejw, property):
            eirr__gyreu[nekm__xnq] = aeu__ejw
        elif isinstance(aeu__ejw, staticmethod):
            nkgi__cnho[nekm__xnq] = aeu__ejw
        else:
            yty__dvsob[nekm__xnq] = aeu__ejw
    npul__lvj = (set(int__bro) | set(eirr__gyreu) | set(nkgi__cnho)) & set(spec
        )
    if npul__lvj:
        raise NameError('name shadowing: {0}'.format(', '.join(npul__lvj)))
    zndag__vbbs = yty__dvsob.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(yty__dvsob)
    if yty__dvsob:
        msg = 'class members are not yet supported: {0}'
        zadj__nhp = ', '.join(yty__dvsob.keys())
        raise TypeError(msg.format(zadj__nhp))
    for nekm__xnq, aeu__ejw in eirr__gyreu.items():
        if aeu__ejw.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(nekm__xnq))
    jit_methods = {nekm__xnq: bodo.jit(returns_maybe_distributed=fqp__two)(
        aeu__ejw) for nekm__xnq, aeu__ejw in int__bro.items()}
    jit_props = {}
    for nekm__xnq, aeu__ejw in eirr__gyreu.items():
        iezz__fakvd = {}
        if aeu__ejw.fget:
            iezz__fakvd['get'] = bodo.jit(aeu__ejw.fget)
        if aeu__ejw.fset:
            iezz__fakvd['set'] = bodo.jit(aeu__ejw.fset)
        jit_props[nekm__xnq] = iezz__fakvd
    jit_static_methods = {nekm__xnq: bodo.jit(aeu__ejw.__func__) for 
        nekm__xnq, aeu__ejw in nkgi__cnho.items()}
    dgx__bjgtq = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    vzcp__hmnsj = dict(class_type=dgx__bjgtq, __doc__=zndag__vbbs)
    vzcp__hmnsj.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), vzcp__hmnsj)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, dgx__bjgtq)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(dgx__bjgtq, typingctx, targetctx).register()
    as_numba_type.register(cls, dgx__bjgtq.instance_type)
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
    nys__ltw = ','.join('{0}:{1}'.format(nekm__xnq, aeu__ejw) for nekm__xnq,
        aeu__ejw in struct.items())
    uubsa__hvj = ','.join('{0}:{1}'.format(nekm__xnq, aeu__ejw) for 
        nekm__xnq, aeu__ejw in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), nys__ltw, uubsa__hvj)
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
    ndzh__cyfqg = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if ndzh__cyfqg is None:
        return
    mon__udmc, pnaef__lvvi = ndzh__cyfqg
    for a in itertools.chain(mon__udmc, pnaef__lvvi.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, mon__udmc, pnaef__lvvi)
    except ForceLiteralArg as e:
        khgm__xzhm = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(khgm__xzhm, self.kws)
        layo__smlf = set()
        cssr__vzaa = set()
        ije__lmrq = {}
        for kze__hghvg in e.requested_args:
            nsswb__lxrnm = typeinfer.func_ir.get_definition(folded[kze__hghvg])
            if isinstance(nsswb__lxrnm, ir.Arg):
                layo__smlf.add(nsswb__lxrnm.index)
                if nsswb__lxrnm.index in e.file_infos:
                    ije__lmrq[nsswb__lxrnm.index] = e.file_infos[nsswb__lxrnm
                        .index]
            else:
                cssr__vzaa.add(kze__hghvg)
        if cssr__vzaa:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif layo__smlf:
            raise ForceLiteralArg(layo__smlf, loc=self.loc, file_infos=
                ije__lmrq)
    if sig is None:
        zhtu__hhqtc = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in mon__udmc]
        args += [('%s=%s' % (nekm__xnq, aeu__ejw)) for nekm__xnq, aeu__ejw in
            sorted(pnaef__lvvi.items())]
        hyydx__moa = zhtu__hhqtc.format(fnty, ', '.join(map(str, args)))
        dbkuz__cpe = context.explain_function_type(fnty)
        msg = '\n'.join([hyydx__moa, dbkuz__cpe])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        arl__pddw = context.unify_pairs(sig.recvr, fnty.this)
        if arl__pddw is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if arl__pddw is not None and arl__pddw.is_precise():
            zawhl__iysk = fnty.copy(this=arl__pddw)
            typeinfer.propagate_refined_type(self.func, zawhl__iysk)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            qjv__isvgo = target.getone()
            if context.unify_pairs(qjv__isvgo, sig.return_type) == qjv__isvgo:
                sig = sig.replace(return_type=qjv__isvgo)
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
        aek__rhgj = '*other* must be a {} but got a {} instead'
        raise TypeError(aek__rhgj.format(ForceLiteralArg, type(other)))
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
    jki__gcbij = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for nekm__xnq, aeu__ejw in kwargs.items():
        lsc__php = None
        try:
            djye__ollw = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var
                ('dummy'), loc)
            func_ir._definitions[djye__ollw.name] = [aeu__ejw]
            lsc__php = get_const_value_inner(func_ir, djye__ollw)
            func_ir._definitions.pop(djye__ollw.name)
            if isinstance(lsc__php, str):
                lsc__php = sigutils._parse_signature_string(lsc__php)
            if isinstance(lsc__php, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {nekm__xnq} is annotated as type class {lsc__php}."""
                    )
            assert isinstance(lsc__php, types.Type)
            if isinstance(lsc__php, (types.List, types.Set)):
                lsc__php = lsc__php.copy(reflected=False)
            jki__gcbij[nekm__xnq] = lsc__php
        except BodoError as ocn__yfulb:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(lsc__php, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(aeu__ejw, ir.Global):
                    msg = f'Global {aeu__ejw.name!r} is not defined.'
                if isinstance(aeu__ejw, ir.FreeVar):
                    msg = f'Freevar {aeu__ejw.name!r} is not defined.'
            if isinstance(aeu__ejw, ir.Expr) and aeu__ejw.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=nekm__xnq, msg=msg, loc=loc)
    for name, typ in jki__gcbij.items():
        self._legalize_arg_type(name, typ, loc)
    return jki__gcbij


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
    otm__wujp = inst.arg
    assert otm__wujp > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(otm__wujp)]))
    tmps = [state.make_temp() for _ in range(otm__wujp - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    rlre__sfm = ir.Global('format', format, loc=self.loc)
    self.store(value=rlre__sfm, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    iqwrv__aszs = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=iqwrv__aszs, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    otm__wujp = inst.arg
    assert otm__wujp > 0, 'invalid BUILD_STRING count'
    brwvz__liird = self.get(strings[0])
    for other, twhar__ekjhd in zip(strings[1:], tmps):
        other = self.get(other)
        ezd__ltg = ir.Expr.binop(operator.add, lhs=brwvz__liird, rhs=other,
            loc=self.loc)
        self.store(ezd__ltg, twhar__ekjhd)
        brwvz__liird = self.get(twhar__ekjhd)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    zxy__dvozv = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, zxy__dvozv])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    wkx__immg = mk_unique_var(f'{var_name}')
    rtrx__yhneh = wkx__immg.replace('<', '_').replace('>', '_')
    rtrx__yhneh = rtrx__yhneh.replace('.', '_').replace('$', '_v')
    return rtrx__yhneh


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
                prcz__iecrm = get_overload_const_str(val2)
                if prcz__iecrm != 'ns':
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
        wcc__vvo = states['defmap']
        if len(wcc__vvo) == 0:
            iar__tkwt = assign.target
            numba.core.ssa._logger.debug('first assign: %s', iar__tkwt)
            if iar__tkwt.name not in scope.localvars:
                iar__tkwt = scope.define(assign.target.name, loc=assign.loc)
        else:
            iar__tkwt = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=iar__tkwt, value=assign.value, loc=assign.loc
            )
        wcc__vvo[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    wist__uudq = []
    for nekm__xnq, aeu__ejw in typing.npydecl.registry.globals:
        if nekm__xnq == func:
            wist__uudq.append(aeu__ejw)
    for nekm__xnq, aeu__ejw in typing.templates.builtin_registry.globals:
        if nekm__xnq == func:
            wist__uudq.append(aeu__ejw)
    if len(wist__uudq) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return wist__uudq


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    kygui__irch = {}
    aqn__kxve = find_topo_order(blocks)
    seg__bpz = {}
    for label in aqn__kxve:
        block = blocks[label]
        bwaw__vkbhz = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                clz__vcsyu = stmt.target.name
                jwk__brl = stmt.value
                if (jwk__brl.op == 'getattr' and jwk__brl.attr in arr_math and
                    isinstance(typemap[jwk__brl.value.name], types.npytypes
                    .Array)):
                    jwk__brl = stmt.value
                    kvrq__dtpf = jwk__brl.value
                    kygui__irch[clz__vcsyu] = kvrq__dtpf
                    scope = kvrq__dtpf.scope
                    loc = kvrq__dtpf.loc
                    hczs__wnxtm = ir.Var(scope, mk_unique_var('$np_g_var'), loc
                        )
                    typemap[hczs__wnxtm.name] = types.misc.Module(numpy)
                    vfiyp__xtlma = ir.Global('np', numpy, loc)
                    ttg__fhpre = ir.Assign(vfiyp__xtlma, hczs__wnxtm, loc)
                    jwk__brl.value = hczs__wnxtm
                    bwaw__vkbhz.append(ttg__fhpre)
                    func_ir._definitions[hczs__wnxtm.name] = [vfiyp__xtlma]
                    func = getattr(numpy, jwk__brl.attr)
                    mqja__cga = get_np_ufunc_typ_lst(func)
                    seg__bpz[clz__vcsyu] = mqja__cga
                if jwk__brl.op == 'call' and jwk__brl.func.name in kygui__irch:
                    kvrq__dtpf = kygui__irch[jwk__brl.func.name]
                    rlqxp__ymuvm = calltypes.pop(jwk__brl)
                    txn__rnfop = rlqxp__ymuvm.args[:len(jwk__brl.args)]
                    ykjlm__waeq = {name: typemap[aeu__ejw.name] for name,
                        aeu__ejw in jwk__brl.kws}
                    kjm__yrq = seg__bpz[jwk__brl.func.name]
                    xgyqc__nigut = None
                    for tff__tqtfv in kjm__yrq:
                        try:
                            xgyqc__nigut = tff__tqtfv.get_call_type(typingctx,
                                [typemap[kvrq__dtpf.name]] + list(
                                txn__rnfop), ykjlm__waeq)
                            typemap.pop(jwk__brl.func.name)
                            typemap[jwk__brl.func.name] = tff__tqtfv
                            calltypes[jwk__brl] = xgyqc__nigut
                            break
                        except Exception as ocn__yfulb:
                            pass
                    if xgyqc__nigut is None:
                        raise TypeError(
                            f'No valid template found for {jwk__brl.func.name}'
                            )
                    jwk__brl.args = [kvrq__dtpf] + jwk__brl.args
            bwaw__vkbhz.append(stmt)
        block.body = bwaw__vkbhz


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    jte__qqo = ufunc.nin
    xppfs__sje = ufunc.nout
    seykb__grhd = ufunc.nargs
    assert seykb__grhd == jte__qqo + xppfs__sje
    if len(args) < jte__qqo:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), jte__qqo))
    if len(args) > seykb__grhd:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            seykb__grhd))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    mccqq__twyo = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    fvl__qwb = max(mccqq__twyo)
    xmf__djz = args[jte__qqo:]
    if not all(d == fvl__qwb for d in mccqq__twyo[jte__qqo:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(fzu__myy, types.ArrayCompatible) and not
        isinstance(fzu__myy, types.Bytes) for fzu__myy in xmf__djz):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(fzu__myy.mutable for fzu__myy in xmf__djz):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    ilts__qno = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    xyik__lcv = None
    if fvl__qwb > 0 and len(xmf__djz) < ufunc.nout:
        xyik__lcv = 'C'
        hmygm__cciz = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in hmygm__cciz and 'F' in hmygm__cciz:
            xyik__lcv = 'F'
    return ilts__qno, xmf__djz, fvl__qwb, xyik__lcv


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
        wzc__nfjxo = 'Dict.key_type cannot be of type {}'
        raise TypingError(wzc__nfjxo.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        wzc__nfjxo = 'Dict.value_type cannot be of type {}'
        raise TypingError(wzc__nfjxo.format(valty))
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
    zeaqw__akmcm = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[zeaqw__akmcm]
        return impl, args
    except KeyError as ocn__yfulb:
        pass
    impl, args = self._build_impl(zeaqw__akmcm, args, kws)
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
    kpd__xxgki = False
    blocks = parfor.loop_body.copy()
    for label, block in blocks.items():
        if len(block.body):
            qyoy__uxse = block.body[-1]
            if isinstance(qyoy__uxse, ir.Branch):
                if len(blocks[qyoy__uxse.truebr].body) == 1 and len(blocks[
                    qyoy__uxse.falsebr].body) == 1:
                    ttngs__vbe = blocks[qyoy__uxse.truebr].body[0]
                    xrek__fcfta = blocks[qyoy__uxse.falsebr].body[0]
                    if isinstance(ttngs__vbe, ir.Jump) and isinstance(
                        xrek__fcfta, ir.Jump
                        ) and ttngs__vbe.target == xrek__fcfta.target:
                        parfor.loop_body[label].body[-1] = ir.Jump(ttngs__vbe
                            .target, qyoy__uxse.loc)
                        kpd__xxgki = True
                elif len(blocks[qyoy__uxse.truebr].body) == 1:
                    ttngs__vbe = blocks[qyoy__uxse.truebr].body[0]
                    if isinstance(ttngs__vbe, ir.Jump
                        ) and ttngs__vbe.target == qyoy__uxse.falsebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(ttngs__vbe
                            .target, qyoy__uxse.loc)
                        kpd__xxgki = True
                elif len(blocks[qyoy__uxse.falsebr].body) == 1:
                    xrek__fcfta = blocks[qyoy__uxse.falsebr].body[0]
                    if isinstance(xrek__fcfta, ir.Jump
                        ) and xrek__fcfta.target == qyoy__uxse.truebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(xrek__fcfta
                            .target, qyoy__uxse.loc)
                        kpd__xxgki = True
    return kpd__xxgki


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        eurzf__tuqc = find_topo_order(parfor.loop_body)
    gciq__pxtan = eurzf__tuqc[0]
    qmexz__phlqz = {}
    _update_parfor_get_setitems(parfor.loop_body[gciq__pxtan].body, parfor.
        index_var, alias_map, qmexz__phlqz, lives_n_aliases)
    wsjqo__exhwg = set(qmexz__phlqz.keys())
    for yaydn__ijo in eurzf__tuqc:
        if yaydn__ijo == gciq__pxtan:
            continue
        for stmt in parfor.loop_body[yaydn__ijo].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            jho__tan = set(aeu__ejw.name for aeu__ejw in stmt.list_vars())
            lyhrc__ctbeb = jho__tan & wsjqo__exhwg
            for a in lyhrc__ctbeb:
                qmexz__phlqz.pop(a, None)
    for yaydn__ijo in eurzf__tuqc:
        if yaydn__ijo == gciq__pxtan:
            continue
        block = parfor.loop_body[yaydn__ijo]
        xhpot__dzdbl = qmexz__phlqz.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            xhpot__dzdbl, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    vnhy__fepew = max(blocks.keys())
    yxo__zvqn, bxa__hsb = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    fsy__xjtbo = ir.Jump(yxo__zvqn, ir.Loc('parfors_dummy', -1))
    blocks[vnhy__fepew].body.append(fsy__xjtbo)
    tazmc__omlyd = compute_cfg_from_blocks(blocks)
    dmcgx__jfwy = compute_use_defs(blocks)
    uyq__notfl = compute_live_map(tazmc__omlyd, blocks, dmcgx__jfwy.usemap,
        dmcgx__jfwy.defmap)
    alias_set = set(alias_map.keys())
    for label, block in blocks.items():
        bwaw__vkbhz = []
        ybvf__bjyf = {aeu__ejw.name for aeu__ejw in block.terminator.
            list_vars()}
        for hej__douwq, folv__nbl in tazmc__omlyd.successors(label):
            ybvf__bjyf |= uyq__notfl[hej__douwq]
        for stmt in reversed(block.body):
            tqgz__wka = ybvf__bjyf & alias_set
            for aeu__ejw in tqgz__wka:
                ybvf__bjyf |= alias_map[aeu__ejw]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in ybvf__bjyf and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                ctbzn__niyru = guard(find_callname, func_ir, stmt.value)
                if ctbzn__niyru == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in ybvf__bjyf and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            ybvf__bjyf |= {aeu__ejw.name for aeu__ejw in stmt.list_vars()}
            bwaw__vkbhz.append(stmt)
        bwaw__vkbhz.reverse()
        block.body = bwaw__vkbhz
    typemap.pop(bxa__hsb.name)
    blocks[vnhy__fepew].body.pop()
    kpd__xxgki = True
    while kpd__xxgki:
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
        kpd__xxgki = trim_empty_parfor_branches(parfor)
    qqm__pwgr = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        qqm__pwgr &= len(block.body) == 0
    if qqm__pwgr:
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
    bvedf__rrbxf = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                bvedf__rrbxf += 1
                parfor = stmt
                qkg__kui = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = qkg__kui.scope
                loc = ir.Loc('parfors_dummy', -1)
                pwm__cif = ir.Var(scope, mk_unique_var('$const'), loc)
                qkg__kui.body.append(ir.Assign(ir.Const(0, loc), pwm__cif, loc)
                    )
                qkg__kui.body.append(ir.Return(pwm__cif, loc))
                tazmc__omlyd = compute_cfg_from_blocks(parfor.loop_body)
                for dxom__bmgc in tazmc__omlyd.dead_nodes():
                    del parfor.loop_body[dxom__bmgc]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                qkg__kui = parfor.loop_body[max(parfor.loop_body.keys())]
                qkg__kui.body.pop()
                qkg__kui.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return bvedf__rrbxf


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def simplify_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import merge_adjacent_blocks, rename_labels
    tazmc__omlyd = compute_cfg_from_blocks(blocks)

    def find_single_branch(label):
        block = blocks[label]
        return len(block.body) == 1 and isinstance(block.body[0], ir.Branch
            ) and label != tazmc__omlyd.entry_point()
    nos__ime = list(filter(find_single_branch, blocks.keys()))
    fez__czwc = set()
    for label in nos__ime:
        inst = blocks[label].body[0]
        mch__smi = tazmc__omlyd.predecessors(label)
        duv__zdlhv = True
        for vame__rzn, ajywv__rgez in mch__smi:
            block = blocks[vame__rzn]
            if isinstance(block.body[-1], ir.Jump):
                block.body[-1] = copy.copy(inst)
            else:
                duv__zdlhv = False
        if duv__zdlhv:
            fez__czwc.add(label)
    for label in fez__czwc:
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
            coc__eqmr = self.overloads.get(tuple(args))
            if coc__eqmr is not None:
                return coc__eqmr.entry_point
            self._pre_compile(args, return_type, flags)
            ljd__mjyhu = self.func_ir
            ese__jacis = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=ese__jacis):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=ljd__mjyhu, args=args,
                    return_type=return_type, flags=flags, locals=self.
                    locals, lifted=(), lifted_from=self.lifted_from,
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
        hslhq__avett = copy.deepcopy(flags)
        hslhq__avett.no_rewrites = True

        def compile_local(the_ir, the_flags):
            wwrt__tufge = pipeline_class(typingctx, targetctx, library,
                args, return_type, the_flags, locals)
            return wwrt__tufge.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        vxn__knnp = compile_local(func_ir, hslhq__avett)
        mbwqb__jmeb = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    mbwqb__jmeb = compile_local(func_ir, flags)
                except Exception as ocn__yfulb:
                    pass
        if mbwqb__jmeb is not None:
            cres = mbwqb__jmeb
        else:
            cres = vxn__knnp
        return cres
    else:
        wwrt__tufge = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return wwrt__tufge.compile_ir(func_ir=func_ir, lifted=lifted,
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
    kuu__kvqta = self.get_data_type(typ.dtype)
    dxdr__riwv = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        dxdr__riwv):
        ifz__lhh = ary.ctypes.data
        jwjx__xeid = self.add_dynamic_addr(builder, ifz__lhh, info=str(type
            (ifz__lhh)))
        lrl__cpzjy = self.add_dynamic_addr(builder, id(ary), info=str(type(
            ary)))
        self.global_arrays.append(ary)
    else:
        hkjr__cydy = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            hkjr__cydy = hkjr__cydy.view('int64')
        val = bytearray(hkjr__cydy.data)
        zgy__dcvd = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        jwjx__xeid = cgutils.global_constant(builder, '.const.array.data',
            zgy__dcvd)
        jwjx__xeid.align = self.get_abi_alignment(kuu__kvqta)
        lrl__cpzjy = None
    fev__kac = self.get_value_type(types.intp)
    eurg__xbwk = [self.get_constant(types.intp, osekx__ygm) for osekx__ygm in
        ary.shape]
    gwv__erfsm = lir.Constant(lir.ArrayType(fev__kac, len(eurg__xbwk)),
        eurg__xbwk)
    iqazj__xmdj = [self.get_constant(types.intp, osekx__ygm) for osekx__ygm in
        ary.strides]
    jtx__kwcwn = lir.Constant(lir.ArrayType(fev__kac, len(iqazj__xmdj)),
        iqazj__xmdj)
    mstkk__joah = self.get_constant(types.intp, ary.dtype.itemsize)
    kjwwq__sbhrc = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        kjwwq__sbhrc, mstkk__joah, jwjx__xeid.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), gwv__erfsm, jtx__kwcwn])


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
    gvh__xhb = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    atnu__svrce = lir.Function(module, gvh__xhb, name='nrt_atomic_{0}'.
        format(op))
    [vor__hssh] = atnu__svrce.args
    hfayx__loiwm = atnu__svrce.append_basic_block()
    builder = lir.IRBuilder(hfayx__loiwm)
    qth__dlxy = lir.Constant(_word_type, 1)
    if False:
        xfw__udytc = builder.atomic_rmw(op, vor__hssh, qth__dlxy, ordering=
            ordering)
        res = getattr(builder, op)(xfw__udytc, qth__dlxy)
        builder.ret(res)
    else:
        xfw__udytc = builder.load(vor__hssh)
        mrfo__rlg = getattr(builder, op)(xfw__udytc, qth__dlxy)
        uhttk__hvg = builder.icmp_signed('!=', xfw__udytc, lir.Constant(
            xfw__udytc.type, -1))
        with cgutils.if_likely(builder, uhttk__hvg):
            builder.store(mrfo__rlg, vor__hssh)
        builder.ret(mrfo__rlg)
    return atnu__svrce


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
        bnae__sqxi = state.targetctx.codegen()
        state.library = bnae__sqxi.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    ylg__pcr = state.func_ir
    typemap = state.typemap
    hav__nxdqa = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    kyp__vwt = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            ylg__pcr, typemap, hav__nxdqa, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            qbva__jwzv = lowering.Lower(targetctx, library, fndesc,
                ylg__pcr, metadata=metadata)
            qbva__jwzv.lower()
            if not flags.no_cpython_wrapper:
                qbva__jwzv.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(hav__nxdqa, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        qbva__jwzv.create_cfunc_wrapper()
            env = qbva__jwzv.env
            jdyqm__ihcz = qbva__jwzv.call_helper
            del qbva__jwzv
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, jdyqm__ihcz, cfunc=None, env=env
                )
        else:
            slpdj__yyhj = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(slpdj__yyhj, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, jdyqm__ihcz, cfunc=
                slpdj__yyhj, env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        vvdc__pqv = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = vvdc__pqv - kyp__vwt
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
        sju__omelr = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, sju__omelr),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            vlct__rfkag.do_break()
        jejl__trf = c.builder.icmp_signed('!=', sju__omelr, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(jejl__trf, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, sju__omelr)
                c.pyapi.decref(sju__omelr)
                vlct__rfkag.do_break()
        c.pyapi.decref(sju__omelr)
    tkba__bgs, list = listobj.ListInstance.allocate_ex(c.context, c.builder,
        typ, size)
    with c.builder.if_else(tkba__bgs, likely=True) as (wpcek__cmpg, kpcck__bvy
        ):
        with wpcek__cmpg:
            list.size = size
            tmmfp__gmht = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                tmmfp__gmht), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        tmmfp__gmht))
                    with cgutils.for_range(c.builder, size) as vlct__rfkag:
                        itemobj = c.pyapi.list_getitem(obj, vlct__rfkag.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        tyvq__obyuw = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(tyvq__obyuw.is_error, likely
                            =False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            vlct__rfkag.do_break()
                        list.setitem(vlct__rfkag.index, tyvq__obyuw.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with kpcck__bvy:
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
    qhke__emydw, ncou__bvhoq, mnagl__jue, lbxv__epb, arqqr__argai = (
        compile_time_get_string_data(literal_string))
    voh__dmi = builder.module
    gv = context.insert_const_bytes(voh__dmi, qhke__emydw)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        ncou__bvhoq), context.get_constant(types.int32, mnagl__jue),
        context.get_constant(types.uint32, lbxv__epb), context.get_constant
        (_Py_hash_t, -1), context.get_constant_null(types.MemInfoPointer(
        types.voidptr)), context.get_constant_null(types.pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    iomuh__mdmm = None
    if isinstance(shape, types.Integer):
        iomuh__mdmm = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(osekx__ygm, (types.Integer, types.IntEnumMember)) for
            osekx__ygm in shape):
            iomuh__mdmm = len(shape)
    return iomuh__mdmm


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
            iomuh__mdmm = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if iomuh__mdmm == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(
                    iomuh__mdmm))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            bok__edpaq = self._get_names(x)
            if len(bok__edpaq) != 0:
                return bok__edpaq[0]
            return bok__edpaq
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    bok__edpaq = self._get_names(obj)
    if len(bok__edpaq) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(bok__edpaq[0])


def get_equiv_set(self, obj):
    bok__edpaq = self._get_names(obj)
    if len(bok__edpaq) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(bok__edpaq[0])


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
    wln__bewup = []
    for fuv__nuv in func_ir.arg_names:
        if fuv__nuv in typemap and isinstance(typemap[fuv__nuv], types.
            containers.UniTuple) and typemap[fuv__nuv].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(fuv__nuv))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for bnjvr__cpr in func_ir.blocks.values():
        for stmt in bnjvr__cpr.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    yoek__rbys = getattr(val, 'code', None)
                    if yoek__rbys is not None:
                        if getattr(val, 'closure', None) is not None:
                            yehnk__jumz = (
                                '<creating a function from a closure>')
                            ezd__ltg = ''
                        else:
                            yehnk__jumz = yoek__rbys.co_name
                            ezd__ltg = '(%s) ' % yehnk__jumz
                    else:
                        yehnk__jumz = '<could not ascertain use case>'
                        ezd__ltg = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (yehnk__jumz, ezd__ltg))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                kyget__bqg = False
                if isinstance(val, pytypes.FunctionType):
                    kyget__bqg = val in {numba.gdb, numba.gdb_init}
                if not kyget__bqg:
                    kyget__bqg = getattr(val, '_name', '') == 'gdb_internal'
                if kyget__bqg:
                    wln__bewup.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    lygt__eit = func_ir.get_definition(var)
                    nigp__pzj = guard(find_callname, func_ir, lygt__eit)
                    if nigp__pzj and nigp__pzj[1] == 'numpy':
                        ty = getattr(numpy, nigp__pzj[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    fiwfo__cwb = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(fiwfo__cwb), loc=stmt.loc)
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
    if len(wln__bewup) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        mwxbz__bhru = '\n'.join([x.strformat() for x in wln__bewup])
        raise errors.UnsupportedError(msg % mwxbz__bhru)


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
    nekm__xnq, aeu__ejw = next(iter(val.items()))
    xduir__fkng = typeof_impl(nekm__xnq, c)
    hiv__nkv = typeof_impl(aeu__ejw, c)
    if xduir__fkng is None or hiv__nkv is None:
        raise ValueError(
            f'Cannot type dict element type {type(nekm__xnq)}, {type(aeu__ejw)}'
            )
    return types.DictType(xduir__fkng, hiv__nkv)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    gtwf__zdibl = cgutils.alloca_once_value(c.builder, val)
    ofyrq__tuqsr = c.pyapi.object_hasattr_string(val, '_opaque')
    ljb__wys = c.builder.icmp_unsigned('==', ofyrq__tuqsr, lir.Constant(
        ofyrq__tuqsr.type, 0))
    aoa__ilri = typ.key_type
    vdt__klon = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(aoa__ilri, vdt__klon)

    def copy_dict(out_dict, in_dict):
        for nekm__xnq, aeu__ejw in in_dict.items():
            out_dict[nekm__xnq] = aeu__ejw
    with c.builder.if_then(ljb__wys):
        qmnti__umatm = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        vorsu__czct = c.pyapi.call_function_objargs(qmnti__umatm, [])
        cbn__dduns = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(cbn__dduns, [vorsu__czct, val])
        c.builder.store(vorsu__czct, gtwf__zdibl)
    val = c.builder.load(gtwf__zdibl)
    wrj__zwc = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    kbkzf__wxh = c.pyapi.object_type(val)
    zkocz__mnxgc = c.builder.icmp_unsigned('==', kbkzf__wxh, wrj__zwc)
    with c.builder.if_else(zkocz__mnxgc) as (ddl__vlfm, cpv__wpvj):
        with ddl__vlfm:
            maonc__acn = c.pyapi.object_getattr_string(val, '_opaque')
            mxsht__hdxxe = types.MemInfoPointer(types.voidptr)
            tyvq__obyuw = c.unbox(mxsht__hdxxe, maonc__acn)
            mi = tyvq__obyuw.value
            kzikr__fkjp = mxsht__hdxxe, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *kzikr__fkjp)
            bwqu__byiz = context.get_constant_null(kzikr__fkjp[1])
            args = mi, bwqu__byiz
            nwyx__dqj, souub__cyt = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, souub__cyt)
            c.pyapi.decref(maonc__acn)
            xghn__ykwpy = c.builder.basic_block
        with cpv__wpvj:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", kbkzf__wxh, wrj__zwc)
            lbqp__ayxxg = c.builder.basic_block
    nzsb__mwoo = c.builder.phi(souub__cyt.type)
    exjl__wsd = c.builder.phi(nwyx__dqj.type)
    nzsb__mwoo.add_incoming(souub__cyt, xghn__ykwpy)
    nzsb__mwoo.add_incoming(souub__cyt.type(None), lbqp__ayxxg)
    exjl__wsd.add_incoming(nwyx__dqj, xghn__ykwpy)
    exjl__wsd.add_incoming(cgutils.true_bit, lbqp__ayxxg)
    c.pyapi.decref(wrj__zwc)
    c.pyapi.decref(kbkzf__wxh)
    with c.builder.if_then(ljb__wys):
        c.pyapi.decref(val)
    return NativeValue(nzsb__mwoo, is_error=exjl__wsd)


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
    aqe__kddi = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=aqe__kddi, name=updatevar)
    spbfj__lxukr = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc
        )
    self.store(value=spbfj__lxukr, name=res)


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
        for nekm__xnq, aeu__ejw in other.items():
            d[nekm__xnq] = aeu__ejw
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
    ezd__ltg = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(ezd__ltg, res)


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
    ucw__kaoj = PassManager(name)
    if state.func_ir is None:
        ucw__kaoj.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            ucw__kaoj.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        ucw__kaoj.add_pass(FixupArgs, 'fix up args')
    ucw__kaoj.add_pass(IRProcessing, 'processing IR')
    ucw__kaoj.add_pass(WithLifting, 'Handle with contexts')
    ucw__kaoj.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        ucw__kaoj.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        ucw__kaoj.add_pass(DeadBranchPrune, 'dead branch pruning')
        ucw__kaoj.add_pass(GenericRewrites, 'nopython rewrites')
    ucw__kaoj.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    ucw__kaoj.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        ucw__kaoj.add_pass(DeadBranchPrune, 'dead branch pruning')
    ucw__kaoj.add_pass(FindLiterallyCalls, 'find literally calls')
    ucw__kaoj.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        ucw__kaoj.add_pass(ReconstructSSA, 'ssa')
    ucw__kaoj.add_pass(LiteralPropagationSubPipelinePass, 'Literal propagation'
        )
    ucw__kaoj.finalize()
    return ucw__kaoj


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
    a, ujo__tztmc = args
    if isinstance(a, types.List) and isinstance(ujo__tztmc, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(ujo__tztmc, types.List):
        return signature(ujo__tztmc, types.intp, ujo__tztmc)


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
        bczwy__hwct, ejv__ykqh = 0, 1
    else:
        bczwy__hwct, ejv__ykqh = 1, 0
    irjdw__ppobp = ListInstance(context, builder, sig.args[bczwy__hwct],
        args[bczwy__hwct])
    qcpu__swot = irjdw__ppobp.size
    axffz__fkc = args[ejv__ykqh]
    tmmfp__gmht = lir.Constant(axffz__fkc.type, 0)
    axffz__fkc = builder.select(cgutils.is_neg_int(builder, axffz__fkc),
        tmmfp__gmht, axffz__fkc)
    kjwwq__sbhrc = builder.mul(axffz__fkc, qcpu__swot)
    hien__krst = ListInstance.allocate(context, builder, sig.return_type,
        kjwwq__sbhrc)
    hien__krst.size = kjwwq__sbhrc
    with cgutils.for_range_slice(builder, tmmfp__gmht, kjwwq__sbhrc,
        qcpu__swot, inc=True) as (fia__sdhu, _):
        with cgutils.for_range(builder, qcpu__swot) as vlct__rfkag:
            value = irjdw__ppobp.getitem(vlct__rfkag.index)
            hien__krst.setitem(builder.add(vlct__rfkag.index, fia__sdhu),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, hien__krst.value
        )


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
    ylxmz__deldw = first.unify(self, second)
    if ylxmz__deldw is not None:
        return ylxmz__deldw
    ylxmz__deldw = second.unify(self, first)
    if ylxmz__deldw is not None:
        return ylxmz__deldw
    umf__cffq = self.can_convert(fromty=first, toty=second)
    if umf__cffq is not None and umf__cffq <= Conversion.safe:
        return second
    umf__cffq = self.can_convert(fromty=second, toty=first)
    if umf__cffq is not None and umf__cffq <= Conversion.safe:
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
    kjwwq__sbhrc = payload.used
    listobj = c.pyapi.list_new(kjwwq__sbhrc)
    tkba__bgs = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(tkba__bgs, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(
            kjwwq__sbhrc.type, 0))
        with payload._iterate() as vlct__rfkag:
            i = c.builder.load(index)
            item = vlct__rfkag.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return tkba__bgs, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    nxd__lfg = h.type
    onii__kda = self.mask
    dtype = self._ty.dtype
    hsp__rdxph = context.typing_context
    fnty = hsp__rdxph.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(hsp__rdxph, (dtype, dtype), {})
    ipykr__stssm = context.get_function(fnty, sig)
    ply__ydknx = ir.Constant(nxd__lfg, 1)
    zme__yyhlk = ir.Constant(nxd__lfg, 5)
    cfeqj__jyhx = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, onii__kda))
    if for_insert:
        txwa__giuuk = onii__kda.type(-1)
        tcb__mxdd = cgutils.alloca_once_value(builder, txwa__giuuk)
    hrg__atast = builder.append_basic_block('lookup.body')
    qxt__ntno = builder.append_basic_block('lookup.found')
    zcutj__ryhh = builder.append_basic_block('lookup.not_found')
    opmk__okaqq = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        rohfm__nizbr = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, rohfm__nizbr)):
            glce__efs = ipykr__stssm(builder, (item, entry.key))
            with builder.if_then(glce__efs):
                builder.branch(qxt__ntno)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, rohfm__nizbr)):
            builder.branch(zcutj__ryhh)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, rohfm__nizbr)):
                jto__pzc = builder.load(tcb__mxdd)
                jto__pzc = builder.select(builder.icmp_unsigned('==',
                    jto__pzc, txwa__giuuk), i, jto__pzc)
                builder.store(jto__pzc, tcb__mxdd)
    with cgutils.for_range(builder, ir.Constant(nxd__lfg, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, ply__ydknx)
        i = builder.and_(i, onii__kda)
        builder.store(i, index)
    builder.branch(hrg__atast)
    with builder.goto_block(hrg__atast):
        i = builder.load(index)
        check_entry(i)
        vame__rzn = builder.load(cfeqj__jyhx)
        vame__rzn = builder.lshr(vame__rzn, zme__yyhlk)
        i = builder.add(ply__ydknx, builder.mul(i, zme__yyhlk))
        i = builder.and_(onii__kda, builder.add(i, vame__rzn))
        builder.store(i, index)
        builder.store(vame__rzn, cfeqj__jyhx)
        builder.branch(hrg__atast)
    with builder.goto_block(zcutj__ryhh):
        if for_insert:
            i = builder.load(index)
            jto__pzc = builder.load(tcb__mxdd)
            i = builder.select(builder.icmp_unsigned('==', jto__pzc,
                txwa__giuuk), i, jto__pzc)
            builder.store(i, index)
        builder.branch(opmk__okaqq)
    with builder.goto_block(qxt__ntno):
        builder.branch(opmk__okaqq)
    builder.position_at_end(opmk__okaqq)
    kyget__bqg = builder.phi(ir.IntType(1), 'found')
    kyget__bqg.add_incoming(cgutils.true_bit, qxt__ntno)
    kyget__bqg.add_incoming(cgutils.false_bit, zcutj__ryhh)
    return kyget__bqg, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    ndv__myox = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    ssbdd__cjfmq = payload.used
    ply__ydknx = ir.Constant(ssbdd__cjfmq.type, 1)
    ssbdd__cjfmq = payload.used = builder.add(ssbdd__cjfmq, ply__ydknx)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, ndv__myox), likely=True):
        payload.fill = builder.add(payload.fill, ply__ydknx)
    if do_resize:
        self.upsize(ssbdd__cjfmq)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    kyget__bqg, i = payload._lookup(item, h, for_insert=True)
    bdr__cycz = builder.not_(kyget__bqg)
    with builder.if_then(bdr__cycz):
        entry = payload.get_entry(i)
        ndv__myox = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        ssbdd__cjfmq = payload.used
        ply__ydknx = ir.Constant(ssbdd__cjfmq.type, 1)
        ssbdd__cjfmq = payload.used = builder.add(ssbdd__cjfmq, ply__ydknx)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, ndv__myox), likely=True):
            payload.fill = builder.add(payload.fill, ply__ydknx)
        if do_resize:
            self.upsize(ssbdd__cjfmq)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    ssbdd__cjfmq = payload.used
    ply__ydknx = ir.Constant(ssbdd__cjfmq.type, 1)
    ssbdd__cjfmq = payload.used = self._builder.sub(ssbdd__cjfmq, ply__ydknx)
    if do_resize:
        self.downsize(ssbdd__cjfmq)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    wypwb__xtu = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, wypwb__xtu)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    cahv__hafx = payload
    tkba__bgs = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(tkba__bgs), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with cahv__hafx._iterate() as vlct__rfkag:
        entry = vlct__rfkag.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(cahv__hafx.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as vlct__rfkag:
        entry = vlct__rfkag.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    tkba__bgs = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(tkba__bgs), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    tkba__bgs = cgutils.alloca_once_value(builder, cgutils.true_bit)
    nxd__lfg = context.get_value_type(types.intp)
    tmmfp__gmht = ir.Constant(nxd__lfg, 0)
    ply__ydknx = ir.Constant(nxd__lfg, 1)
    wfchk__shsqz = context.get_data_type(types.SetPayload(self._ty))
    rwi__uhg = context.get_abi_sizeof(wfchk__shsqz)
    ylv__mbj = self._entrysize
    rwi__uhg -= ylv__mbj
    pws__xqxn, tshyv__gxk = cgutils.muladd_with_overflow(builder, nentries,
        ir.Constant(nxd__lfg, ylv__mbj), ir.Constant(nxd__lfg, rwi__uhg))
    with builder.if_then(tshyv__gxk, likely=False):
        builder.store(cgutils.false_bit, tkba__bgs)
    with builder.if_then(builder.load(tkba__bgs), likely=True):
        if realloc:
            mrers__zidz = self._set.meminfo
            vor__hssh = context.nrt.meminfo_varsize_alloc(builder,
                mrers__zidz, size=pws__xqxn)
            gfc__pfc = cgutils.is_null(builder, vor__hssh)
        else:
            tzkdc__lntal = _imp_dtor(context, builder.module, self._ty)
            mrers__zidz = context.nrt.meminfo_new_varsize_dtor(builder,
                pws__xqxn, builder.bitcast(tzkdc__lntal, cgutils.voidptr_t))
            gfc__pfc = cgutils.is_null(builder, mrers__zidz)
        with builder.if_else(gfc__pfc, likely=False) as (cott__adfg,
            wpcek__cmpg):
            with cott__adfg:
                builder.store(cgutils.false_bit, tkba__bgs)
            with wpcek__cmpg:
                if not realloc:
                    self._set.meminfo = mrers__zidz
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, pws__xqxn, 255)
                payload.used = tmmfp__gmht
                payload.fill = tmmfp__gmht
                payload.finger = tmmfp__gmht
                koesk__mnkxl = builder.sub(nentries, ply__ydknx)
                payload.mask = koesk__mnkxl
    return builder.load(tkba__bgs)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    tkba__bgs = cgutils.alloca_once_value(builder, cgutils.true_bit)
    nxd__lfg = context.get_value_type(types.intp)
    tmmfp__gmht = ir.Constant(nxd__lfg, 0)
    ply__ydknx = ir.Constant(nxd__lfg, 1)
    wfchk__shsqz = context.get_data_type(types.SetPayload(self._ty))
    rwi__uhg = context.get_abi_sizeof(wfchk__shsqz)
    ylv__mbj = self._entrysize
    rwi__uhg -= ylv__mbj
    onii__kda = src_payload.mask
    nentries = builder.add(ply__ydknx, onii__kda)
    pws__xqxn = builder.add(ir.Constant(nxd__lfg, rwi__uhg), builder.mul(ir
        .Constant(nxd__lfg, ylv__mbj), nentries))
    with builder.if_then(builder.load(tkba__bgs), likely=True):
        tzkdc__lntal = _imp_dtor(context, builder.module, self._ty)
        mrers__zidz = context.nrt.meminfo_new_varsize_dtor(builder,
            pws__xqxn, builder.bitcast(tzkdc__lntal, cgutils.voidptr_t))
        gfc__pfc = cgutils.is_null(builder, mrers__zidz)
        with builder.if_else(gfc__pfc, likely=False) as (cott__adfg,
            wpcek__cmpg):
            with cott__adfg:
                builder.store(cgutils.false_bit, tkba__bgs)
            with wpcek__cmpg:
                self._set.meminfo = mrers__zidz
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = tmmfp__gmht
                payload.mask = onii__kda
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, ylv__mbj)
                with src_payload._iterate() as vlct__rfkag:
                    context.nrt.incref(builder, self._ty.dtype, vlct__rfkag
                        .entry.key)
    return builder.load(tkba__bgs)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    rlldm__dvnm = context.get_value_type(types.voidptr)
    qnv__rxic = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [rlldm__dvnm, qnv__rxic, rlldm__dvnm]
        )
    akp__ggda = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=akp__ggda)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        afryu__zlthz = builder.bitcast(fn.args[0], cgutils.voidptr_t.
            as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, afryu__zlthz)
        with payload._iterate() as vlct__rfkag:
            entry = vlct__rfkag.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    hyjl__kkwqf, = sig.args
    psx__pnekb, = args
    cpb__jcybd = numba.core.imputils.call_len(context, builder, hyjl__kkwqf,
        psx__pnekb)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, cpb__jcybd)
    with numba.core.imputils.for_iter(context, builder, hyjl__kkwqf, psx__pnekb
        ) as vlct__rfkag:
        inst.add(vlct__rfkag.value)
        context.nrt.decref(builder, set_type.dtype, vlct__rfkag.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    hyjl__kkwqf = sig.args[1]
    psx__pnekb = args[1]
    cpb__jcybd = numba.core.imputils.call_len(context, builder, hyjl__kkwqf,
        psx__pnekb)
    if cpb__jcybd is not None:
        nii__smo = builder.add(inst.payload.used, cpb__jcybd)
        inst.upsize(nii__smo)
    with numba.core.imputils.for_iter(context, builder, hyjl__kkwqf, psx__pnekb
        ) as vlct__rfkag:
        hct__hmjr = context.cast(builder, vlct__rfkag.value, hyjl__kkwqf.
            dtype, inst.dtype)
        inst.add(hct__hmjr)
        context.nrt.decref(builder, hyjl__kkwqf.dtype, vlct__rfkag.value)
    if cpb__jcybd is not None:
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
    tyhy__gud = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, tyhy__gud, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    slpdj__yyhj = target_context.get_executable(library, fndesc, env)
    exl__ahi = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=slpdj__yyhj, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return exl__ahi


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
        nqpw__zsxuy = MPI.COMM_WORLD
        xydjh__zrm = None
        if nqpw__zsxuy.Get_rank() == 0:
            try:
                fbo__ndks = self.get_cache_path()
                os.makedirs(fbo__ndks, exist_ok=True)
                tempfile.TemporaryFile(dir=fbo__ndks).close()
            except Exception as e:
                xydjh__zrm = e
        xydjh__zrm = nqpw__zsxuy.bcast(xydjh__zrm)
        if isinstance(xydjh__zrm, Exception):
            raise xydjh__zrm
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
