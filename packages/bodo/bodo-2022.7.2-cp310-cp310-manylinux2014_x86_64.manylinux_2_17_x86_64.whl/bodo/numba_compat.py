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
    grij__gcoef = numba.core.bytecode.FunctionIdentity.from_function(func)
    rco__udrw = numba.core.interpreter.Interpreter(grij__gcoef)
    hug__rqh = numba.core.bytecode.ByteCode(func_id=grij__gcoef)
    func_ir = rco__udrw.interpret(hug__rqh)
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
        gyw__yudnw = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        gyw__yudnw.run()
    dcifx__wrnsb = numba.core.postproc.PostProcessor(func_ir)
    dcifx__wrnsb.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, fcie__gxfy in visit_vars_extensions.items():
        if isinstance(stmt, t):
            fcie__gxfy(stmt, callback, cbdata)
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
    gzpy__qrgex = ['ravel', 'transpose', 'reshape']
    for puvc__zrs in blocks.values():
        for olngj__jcns in puvc__zrs.body:
            if type(olngj__jcns) in alias_analysis_extensions:
                fcie__gxfy = alias_analysis_extensions[type(olngj__jcns)]
                fcie__gxfy(olngj__jcns, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(olngj__jcns, ir.Assign):
                xojy__rjn = olngj__jcns.value
                fcgc__zrer = olngj__jcns.target.name
                if is_immutable_type(fcgc__zrer, typemap):
                    continue
                if isinstance(xojy__rjn, ir.Var
                    ) and fcgc__zrer != xojy__rjn.name:
                    _add_alias(fcgc__zrer, xojy__rjn.name, alias_map,
                        arg_aliases)
                if isinstance(xojy__rjn, ir.Expr) and (xojy__rjn.op ==
                    'cast' or xojy__rjn.op in ['getitem', 'static_getitem']):
                    _add_alias(fcgc__zrer, xojy__rjn.value.name, alias_map,
                        arg_aliases)
                if isinstance(xojy__rjn, ir.Expr
                    ) and xojy__rjn.op == 'inplace_binop':
                    _add_alias(fcgc__zrer, xojy__rjn.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(xojy__rjn, ir.Expr
                    ) and xojy__rjn.op == 'getattr' and xojy__rjn.attr in ['T',
                    'ctypes', 'flat']:
                    _add_alias(fcgc__zrer, xojy__rjn.value.name, alias_map,
                        arg_aliases)
                if isinstance(xojy__rjn, ir.Expr
                    ) and xojy__rjn.op == 'getattr' and xojy__rjn.attr not in [
                    'shape'] and xojy__rjn.value.name in arg_aliases:
                    _add_alias(fcgc__zrer, xojy__rjn.value.name, alias_map,
                        arg_aliases)
                if isinstance(xojy__rjn, ir.Expr
                    ) and xojy__rjn.op == 'getattr' and xojy__rjn.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(fcgc__zrer, xojy__rjn.value.name, alias_map,
                        arg_aliases)
                if isinstance(xojy__rjn, ir.Expr) and xojy__rjn.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(fcgc__zrer, typemap):
                    for jpbp__qhjsb in xojy__rjn.items:
                        _add_alias(fcgc__zrer, jpbp__qhjsb.name, alias_map,
                            arg_aliases)
                if isinstance(xojy__rjn, ir.Expr) and xojy__rjn.op == 'call':
                    ldgpe__ezjca = guard(find_callname, func_ir, xojy__rjn,
                        typemap)
                    if ldgpe__ezjca is None:
                        continue
                    boxzn__hhq, fbyj__gbr = ldgpe__ezjca
                    if ldgpe__ezjca in alias_func_extensions:
                        giiu__hzjtw = alias_func_extensions[ldgpe__ezjca]
                        giiu__hzjtw(fcgc__zrer, xojy__rjn.args, alias_map,
                            arg_aliases)
                    if fbyj__gbr == 'numpy' and boxzn__hhq in gzpy__qrgex:
                        _add_alias(fcgc__zrer, xojy__rjn.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(fbyj__gbr, ir.Var
                        ) and boxzn__hhq in gzpy__qrgex:
                        _add_alias(fcgc__zrer, fbyj__gbr.name, alias_map,
                            arg_aliases)
    ynpz__zkjfq = copy.deepcopy(alias_map)
    for jpbp__qhjsb in ynpz__zkjfq:
        for hiqu__aixm in ynpz__zkjfq[jpbp__qhjsb]:
            alias_map[jpbp__qhjsb] |= alias_map[hiqu__aixm]
        for hiqu__aixm in ynpz__zkjfq[jpbp__qhjsb]:
            alias_map[hiqu__aixm] = alias_map[jpbp__qhjsb]
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
    pbtr__wqzll = compute_cfg_from_blocks(func_ir.blocks)
    vrgxj__krtrt = compute_use_defs(func_ir.blocks)
    xss__xxr = compute_live_map(pbtr__wqzll, func_ir.blocks, vrgxj__krtrt.
        usemap, vrgxj__krtrt.defmap)
    gdyw__jewnu = True
    while gdyw__jewnu:
        gdyw__jewnu = False
        for label, block in func_ir.blocks.items():
            lives = {jpbp__qhjsb.name for jpbp__qhjsb in block.terminator.
                list_vars()}
            for flg__zuhlw, inb__ptmj in pbtr__wqzll.successors(label):
                lives |= xss__xxr[flg__zuhlw]
            monpi__jsoh = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    fcgc__zrer = stmt.target
                    axg__ncl = stmt.value
                    if fcgc__zrer.name not in lives:
                        if isinstance(axg__ncl, ir.Expr
                            ) and axg__ncl.op == 'make_function':
                            continue
                        if isinstance(axg__ncl, ir.Expr
                            ) and axg__ncl.op == 'getattr':
                            continue
                        if isinstance(axg__ncl, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(fcgc__zrer,
                            None), types.Function):
                            continue
                        if isinstance(axg__ncl, ir.Expr
                            ) and axg__ncl.op == 'build_map':
                            continue
                        if isinstance(axg__ncl, ir.Expr
                            ) and axg__ncl.op == 'build_tuple':
                            continue
                    if isinstance(axg__ncl, ir.Var
                        ) and fcgc__zrer.name == axg__ncl.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    zmv__xqdjg = analysis.ir_extension_usedefs[type(stmt)]
                    rimn__ndzua, yszmb__torv = zmv__xqdjg(stmt)
                    lives -= yszmb__torv
                    lives |= rimn__ndzua
                else:
                    lives |= {jpbp__qhjsb.name for jpbp__qhjsb in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(fcgc__zrer.name)
                monpi__jsoh.append(stmt)
            monpi__jsoh.reverse()
            if len(block.body) != len(monpi__jsoh):
                gdyw__jewnu = True
            block.body = monpi__jsoh


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    wcqze__ixo = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (wcqze__ixo,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    alj__ibct = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), alj__ibct)


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
            for mro__jcaq in fnty.templates:
                self._inline_overloads.update(mro__jcaq._inline_overloads)
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
    alj__ibct = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), alj__ibct)
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
    ikxxs__sfyl, pglhr__rrd = self._get_impl(args, kws)
    if ikxxs__sfyl is None:
        return
    ywyo__dkvgz = types.Dispatcher(ikxxs__sfyl)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        iwyms__khjkx = ikxxs__sfyl._compiler
        flags = compiler.Flags()
        oztu__vaqu = iwyms__khjkx.targetdescr.typing_context
        aapea__ssbt = iwyms__khjkx.targetdescr.target_context
        ktjqp__lcu = iwyms__khjkx.pipeline_class(oztu__vaqu, aapea__ssbt,
            None, None, None, flags, None)
        cvwt__pdfx = InlineWorker(oztu__vaqu, aapea__ssbt, iwyms__khjkx.
            locals, ktjqp__lcu, flags, None)
        kza__bdgcd = ywyo__dkvgz.dispatcher.get_call_template
        mro__jcaq, gogw__wacs, zxz__dlm, kws = kza__bdgcd(pglhr__rrd, kws)
        if zxz__dlm in self._inline_overloads:
            return self._inline_overloads[zxz__dlm]['iinfo'].signature
        ir = cvwt__pdfx.run_untyped_passes(ywyo__dkvgz.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, aapea__ssbt, ir, zxz__dlm, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, zxz__dlm, None)
        self._inline_overloads[sig.args] = {'folded_args': zxz__dlm}
        aun__bsjex = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = aun__bsjex
        if not self._inline.is_always_inline:
            sig = ywyo__dkvgz.get_call_type(self.context, pglhr__rrd, kws)
            self._compiled_overloads[sig.args] = ywyo__dkvgz.get_overload(sig)
        cyhc__zykj = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': zxz__dlm,
            'iinfo': cyhc__zykj}
    else:
        sig = ywyo__dkvgz.get_call_type(self.context, pglhr__rrd, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = ywyo__dkvgz.get_overload(sig)
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
    drpya__tbrp = [True, False]
    zmb__tmge = [False, True]
    sgopx__dbivc = _ResolutionFailures(context, self, args, kws, depth=self
        ._depth)
    from numba.core.target_extension import get_local_target
    tlq__rmpxe = get_local_target(context)
    wof__msn = utils.order_by_target_specificity(tlq__rmpxe, self.templates,
        fnkey=self.key[0])
    self._depth += 1
    for qbyu__lml in wof__msn:
        ervx__dfz = qbyu__lml(context)
        igle__vuz = drpya__tbrp if ervx__dfz.prefer_literal else zmb__tmge
        igle__vuz = [True] if getattr(ervx__dfz, '_no_unliteral', False
            ) else igle__vuz
        for teh__pimua in igle__vuz:
            try:
                if teh__pimua:
                    sig = ervx__dfz.apply(args, kws)
                else:
                    pfwl__ava = tuple([_unlit_non_poison(a) for a in args])
                    zvgay__aivci = {iurfy__nltp: _unlit_non_poison(
                        jpbp__qhjsb) for iurfy__nltp, jpbp__qhjsb in kws.
                        items()}
                    sig = ervx__dfz.apply(pfwl__ava, zvgay__aivci)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    sgopx__dbivc.add_error(ervx__dfz, False, e, teh__pimua)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = ervx__dfz.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    gac__mmpyj = getattr(ervx__dfz, 'cases', None)
                    if gac__mmpyj is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            gac__mmpyj)
                    else:
                        msg = 'No match.'
                    sgopx__dbivc.add_error(ervx__dfz, True, msg, teh__pimua)
    sgopx__dbivc.raise_error()


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
    mro__jcaq = self.template(context)
    kxc__ejxyw = None
    ueri__nvh = None
    sto__bgn = None
    igle__vuz = [True, False] if mro__jcaq.prefer_literal else [False, True]
    igle__vuz = [True] if getattr(mro__jcaq, '_no_unliteral', False
        ) else igle__vuz
    for teh__pimua in igle__vuz:
        if teh__pimua:
            try:
                sto__bgn = mro__jcaq.apply(args, kws)
            except Exception as gts__vmn:
                if isinstance(gts__vmn, errors.ForceLiteralArg):
                    raise gts__vmn
                kxc__ejxyw = gts__vmn
                sto__bgn = None
            else:
                break
        else:
            iswig__elas = tuple([_unlit_non_poison(a) for a in args])
            kyncc__mrphv = {iurfy__nltp: _unlit_non_poison(jpbp__qhjsb) for
                iurfy__nltp, jpbp__qhjsb in kws.items()}
            rqwe__bhqpx = iswig__elas == args and kws == kyncc__mrphv
            if not rqwe__bhqpx and sto__bgn is None:
                try:
                    sto__bgn = mro__jcaq.apply(iswig__elas, kyncc__mrphv)
                except Exception as gts__vmn:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(gts__vmn
                        , errors.NumbaError):
                        raise gts__vmn
                    if isinstance(gts__vmn, errors.ForceLiteralArg):
                        if mro__jcaq.prefer_literal:
                            raise gts__vmn
                    ueri__nvh = gts__vmn
                else:
                    break
    if sto__bgn is None and (ueri__nvh is not None or kxc__ejxyw is not None):
        bnq__igmq = '- Resolution failure for {} arguments:\n{}\n'
        rexwp__tmev = _termcolor.highlight(bnq__igmq)
        if numba.core.config.DEVELOPER_MODE:
            vgzp__mxj = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    entj__nhdkf = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    entj__nhdkf = ['']
                uehj__zdl = '\n{}'.format(2 * vgzp__mxj)
                lroo__jyh = _termcolor.reset(uehj__zdl + uehj__zdl.join(
                    _bt_as_lines(entj__nhdkf)))
                return _termcolor.reset(lroo__jyh)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            koxoe__szc = str(e)
            koxoe__szc = koxoe__szc if koxoe__szc else str(repr(e)) + add_bt(e)
            oxeo__mfjg = errors.TypingError(textwrap.dedent(koxoe__szc))
            return rexwp__tmev.format(literalness, str(oxeo__mfjg))
        import bodo
        if isinstance(kxc__ejxyw, bodo.utils.typing.BodoError):
            raise kxc__ejxyw
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', kxc__ejxyw) +
                nested_msg('non-literal', ueri__nvh))
        else:
            if 'missing a required argument' in kxc__ejxyw.msg:
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
            raise errors.TypingError(msg, loc=kxc__ejxyw.loc)
    return sto__bgn


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
    boxzn__hhq = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=boxzn__hhq)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            ilm__lxd = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), ilm__lxd)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    maxx__zfmu = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            maxx__zfmu.append(types.Omitted(a.value))
        else:
            maxx__zfmu.append(self.typeof_pyval(a))
    zhtl__pcy = None
    try:
        error = None
        zhtl__pcy = self.compile(tuple(maxx__zfmu))
    except errors.ForceLiteralArg as e:
        ccic__eiit = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if ccic__eiit:
            vljbt__hhnyr = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            yrss__yjx = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(ccic__eiit))
            raise errors.CompilerError(vljbt__hhnyr.format(yrss__yjx))
        pglhr__rrd = []
        try:
            for i, jpbp__qhjsb in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        pglhr__rrd.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        pglhr__rrd.append(types.literal(args[i]))
                else:
                    pglhr__rrd.append(args[i])
            args = pglhr__rrd
        except (OSError, FileNotFoundError) as sqnfw__xccwd:
            error = FileNotFoundError(str(sqnfw__xccwd) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                zhtl__pcy = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        bpe__wgti = []
        for i, cupwz__jtit in enumerate(args):
            val = cupwz__jtit.value if isinstance(cupwz__jtit, numba.core.
                dispatcher.OmittedArg) else cupwz__jtit
            try:
                wlcw__qudcz = typeof(val, Purpose.argument)
            except ValueError as cxrl__vuru:
                bpe__wgti.append((i, str(cxrl__vuru)))
            else:
                if wlcw__qudcz is None:
                    bpe__wgti.append((i,
                        f'cannot determine Numba type of value {val}'))
        if bpe__wgti:
            cnbd__ganr = '\n'.join(f'- argument {i}: {ttgyv__xjzpp}' for i,
                ttgyv__xjzpp in bpe__wgti)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{cnbd__ganr}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                kba__xhe = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                suovl__fmp = False
                for msmr__oohi in kba__xhe:
                    if msmr__oohi in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        suovl__fmp = True
                        break
                if not suovl__fmp:
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
                ilm__lxd = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), ilm__lxd)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return zhtl__pcy


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
    for vmxv__kmm in cres.library._codegen._engine._defined_symbols:
        if vmxv__kmm.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in vmxv__kmm and (
            'bodo_gb_udf_update_local' in vmxv__kmm or 
            'bodo_gb_udf_combine' in vmxv__kmm or 'bodo_gb_udf_eval' in
            vmxv__kmm or 'bodo_gb_apply_general_udfs' in vmxv__kmm):
            gb_agg_cfunc_addr[vmxv__kmm
                ] = cres.library.get_pointer_to_function(vmxv__kmm)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for vmxv__kmm in cres.library._codegen._engine._defined_symbols:
        if vmxv__kmm.startswith('cfunc') and ('get_join_cond_addr' not in
            vmxv__kmm or 'bodo_join_gen_cond' in vmxv__kmm):
            join_gen_cond_cfunc_addr[vmxv__kmm
                ] = cres.library.get_pointer_to_function(vmxv__kmm)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    ikxxs__sfyl = self._get_dispatcher_for_current_target()
    if ikxxs__sfyl is not self:
        return ikxxs__sfyl.compile(sig)
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
            aahk__tpjf = self.overloads.get(tuple(args))
            if aahk__tpjf is not None:
                return aahk__tpjf.entry_point
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
            wbjzi__jpybw = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=wbjzi__jpybw):
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
                brq__xdth = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in brq__xdth:
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
    yaal__utc = self._final_module
    gefh__svgy = []
    keed__hewz = 0
    for fn in yaal__utc.functions:
        keed__hewz += 1
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
            gefh__svgy.append(fn.name)
    if keed__hewz == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if gefh__svgy:
        yaal__utc = yaal__utc.clone()
        for name in gefh__svgy:
            yaal__utc.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = yaal__utc
    return yaal__utc


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
    for knvy__vsx in self.constraints:
        loc = knvy__vsx.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                knvy__vsx(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                dtok__aolo = numba.core.errors.TypingError(str(e), loc=
                    knvy__vsx.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(dtok__aolo, e))
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
                    dtok__aolo = numba.core.errors.TypingError(msg.format(
                        con=knvy__vsx, err=str(e)), loc=knvy__vsx.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(dtok__aolo, e))
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
    for bwiv__ezvbp in self._failures.values():
        for xfvgj__zurp in bwiv__ezvbp:
            if isinstance(xfvgj__zurp.error, ForceLiteralArg):
                raise xfvgj__zurp.error
            if isinstance(xfvgj__zurp.error, bodo.utils.typing.BodoError):
                raise xfvgj__zurp.error
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
    ejsz__wfubq = False
    monpi__jsoh = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        nvjw__erdfn = set()
        oldg__fny = lives & alias_set
        for jpbp__qhjsb in oldg__fny:
            nvjw__erdfn |= alias_map[jpbp__qhjsb]
        lives_n_aliases = lives | nvjw__erdfn | arg_aliases
        if type(stmt) in remove_dead_extensions:
            fcie__gxfy = remove_dead_extensions[type(stmt)]
            stmt = fcie__gxfy(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                ejsz__wfubq = True
                continue
        if isinstance(stmt, ir.Assign):
            fcgc__zrer = stmt.target
            axg__ncl = stmt.value
            if fcgc__zrer.name not in lives:
                if has_no_side_effect(axg__ncl, lives_n_aliases, call_table):
                    ejsz__wfubq = True
                    continue
                if isinstance(axg__ncl, ir.Expr
                    ) and axg__ncl.op == 'call' and call_table[axg__ncl.
                    func.name] == ['astype']:
                    zawty__cxgct = guard(get_definition, func_ir, axg__ncl.func
                        )
                    if (zawty__cxgct is not None and zawty__cxgct.op ==
                        'getattr' and isinstance(typemap[zawty__cxgct.value
                        .name], types.Array) and zawty__cxgct.attr == 'astype'
                        ):
                        ejsz__wfubq = True
                        continue
            if saved_array_analysis and fcgc__zrer.name in lives and is_expr(
                axg__ncl, 'getattr'
                ) and axg__ncl.attr == 'shape' and is_array_typ(typemap[
                axg__ncl.value.name]) and axg__ncl.value.name not in lives:
                ghu__oud = {jpbp__qhjsb: iurfy__nltp for iurfy__nltp,
                    jpbp__qhjsb in func_ir.blocks.items()}
                if block in ghu__oud:
                    label = ghu__oud[block]
                    xqcd__tkh = saved_array_analysis.get_equiv_set(label)
                    ihtw__xsc = xqcd__tkh.get_equiv_set(axg__ncl.value)
                    if ihtw__xsc is not None:
                        for jpbp__qhjsb in ihtw__xsc:
                            if jpbp__qhjsb.endswith('#0'):
                                jpbp__qhjsb = jpbp__qhjsb[:-2]
                            if jpbp__qhjsb in typemap and is_array_typ(typemap
                                [jpbp__qhjsb]) and jpbp__qhjsb in lives:
                                axg__ncl.value = ir.Var(axg__ncl.value.
                                    scope, jpbp__qhjsb, axg__ncl.value.loc)
                                ejsz__wfubq = True
                                break
            if isinstance(axg__ncl, ir.Var
                ) and fcgc__zrer.name == axg__ncl.name:
                ejsz__wfubq = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                ejsz__wfubq = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            zmv__xqdjg = analysis.ir_extension_usedefs[type(stmt)]
            rimn__ndzua, yszmb__torv = zmv__xqdjg(stmt)
            lives -= yszmb__torv
            lives |= rimn__ndzua
        else:
            lives |= {jpbp__qhjsb.name for jpbp__qhjsb in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                qade__gam = set()
                if isinstance(axg__ncl, ir.Expr):
                    qade__gam = {jpbp__qhjsb.name for jpbp__qhjsb in
                        axg__ncl.list_vars()}
                if fcgc__zrer.name not in qade__gam:
                    lives.remove(fcgc__zrer.name)
        monpi__jsoh.append(stmt)
    monpi__jsoh.reverse()
    block.body = monpi__jsoh
    return ejsz__wfubq


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            fbio__owh, = args
            if isinstance(fbio__owh, types.IterableType):
                dtype = fbio__owh.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), fbio__owh)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    enqcq__pbz = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (enqcq__pbz, self.dtype)
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
        except LiteralTypingError as rzt__vekay:
            return
    try:
        return literal(value)
    except LiteralTypingError as rzt__vekay:
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
        zelmj__keiwx = py_func.__qualname__
    except AttributeError as rzt__vekay:
        zelmj__keiwx = py_func.__name__
    atibj__ato = inspect.getfile(py_func)
    for cls in self._locator_classes:
        jzwx__bcfq = cls.from_function(py_func, atibj__ato)
        if jzwx__bcfq is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (zelmj__keiwx, atibj__ato))
    self._locator = jzwx__bcfq
    lfgqv__xdc = inspect.getfile(py_func)
    slgh__ojl = os.path.splitext(os.path.basename(lfgqv__xdc))[0]
    if atibj__ato.startswith('<ipython-'):
        hmv__ityd = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', slgh__ojl, count=1)
        if hmv__ityd == slgh__ojl:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        slgh__ojl = hmv__ityd
    sbmd__fjuk = '%s.%s' % (slgh__ojl, zelmj__keiwx)
    noc__utwm = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(sbmd__fjuk, noc__utwm
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    xtiuy__ijb = list(filter(lambda a: self._istuple(a.name), args))
    if len(xtiuy__ijb) == 2 and fn.__name__ == 'add':
        tsbk__yrdkh = self.typemap[xtiuy__ijb[0].name]
        ptjj__ttg = self.typemap[xtiuy__ijb[1].name]
        if tsbk__yrdkh.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                xtiuy__ijb[1]))
        if ptjj__ttg.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                xtiuy__ijb[0]))
        try:
            rysto__suyn = [equiv_set.get_shape(x) for x in xtiuy__ijb]
            if None in rysto__suyn:
                return None
            ujspt__epk = sum(rysto__suyn, ())
            return ArrayAnalysis.AnalyzeResult(shape=ujspt__epk)
        except GuardException as rzt__vekay:
            return None
    zssl__zkb = list(filter(lambda a: self._isarray(a.name), args))
    require(len(zssl__zkb) > 0)
    azk__mkh = [x.name for x in zssl__zkb]
    zgqnj__xtx = [self.typemap[x.name].ndim for x in zssl__zkb]
    oki__tcz = max(zgqnj__xtx)
    require(oki__tcz > 0)
    rysto__suyn = [equiv_set.get_shape(x) for x in zssl__zkb]
    if any(a is None for a in rysto__suyn):
        return ArrayAnalysis.AnalyzeResult(shape=zssl__zkb[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, zssl__zkb))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, rysto__suyn,
        azk__mkh)


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
    rcg__ctlsx = code_obj.code
    lyekv__gjos = len(rcg__ctlsx.co_freevars)
    ugbfq__alk = rcg__ctlsx.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        kvm__tuoae, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        ugbfq__alk = [jpbp__qhjsb.name for jpbp__qhjsb in kvm__tuoae]
    gck__pce = caller_ir.func_id.func.__globals__
    try:
        gck__pce = getattr(code_obj, 'globals', gck__pce)
    except KeyError as rzt__vekay:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    voh__zwnk = []
    for x in ugbfq__alk:
        try:
            mvvl__gsck = caller_ir.get_definition(x)
        except KeyError as rzt__vekay:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(mvvl__gsck, (ir.Const, ir.Global, ir.FreeVar)):
            val = mvvl__gsck.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                wcqze__ixo = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                gck__pce[wcqze__ixo] = bodo.jit(distributed=False)(val)
                gck__pce[wcqze__ixo].is_nested_func = True
                val = wcqze__ixo
            if isinstance(val, CPUDispatcher):
                wcqze__ixo = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                gck__pce[wcqze__ixo] = val
                val = wcqze__ixo
            voh__zwnk.append(val)
        elif isinstance(mvvl__gsck, ir.Expr
            ) and mvvl__gsck.op == 'make_function':
            xkdq__aysbn = convert_code_obj_to_function(mvvl__gsck, caller_ir)
            wcqze__ixo = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            gck__pce[wcqze__ixo] = bodo.jit(distributed=False)(xkdq__aysbn)
            gck__pce[wcqze__ixo].is_nested_func = True
            voh__zwnk.append(wcqze__ixo)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    mlpzd__ned = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        voh__zwnk)])
    avl__tfi = ','.join([('c_%d' % i) for i in range(lyekv__gjos)])
    tob__gxp = list(rcg__ctlsx.co_varnames)
    mpjg__isctn = 0
    ciqo__fxx = rcg__ctlsx.co_argcount
    bjq__tsmn = caller_ir.get_definition(code_obj.defaults)
    if bjq__tsmn is not None:
        if isinstance(bjq__tsmn, tuple):
            d = [caller_ir.get_definition(x).value for x in bjq__tsmn]
            bke__vegln = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in bjq__tsmn.items]
            bke__vegln = tuple(d)
        mpjg__isctn = len(bke__vegln)
    vdugz__wlzd = ciqo__fxx - mpjg__isctn
    jrlcc__ifptp = ','.join([('%s' % tob__gxp[i]) for i in range(vdugz__wlzd)])
    if mpjg__isctn:
        bwqi__jozm = [('%s = %s' % (tob__gxp[i + vdugz__wlzd], bke__vegln[i
            ])) for i in range(mpjg__isctn)]
        jrlcc__ifptp += ', '
        jrlcc__ifptp += ', '.join(bwqi__jozm)
    return _create_function_from_code_obj(rcg__ctlsx, mlpzd__ned,
        jrlcc__ifptp, avl__tfi, gck__pce)


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
    for jtmaq__zhajs, (gmg__uli, pffqf__wgauy) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % pffqf__wgauy)
            qfeoh__pika = _pass_registry.get(gmg__uli).pass_inst
            if isinstance(qfeoh__pika, CompilerPass):
                self._runPass(jtmaq__zhajs, qfeoh__pika, state)
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
                    pipeline_name, pffqf__wgauy)
                ycgq__prm = self._patch_error(msg, e)
                raise ycgq__prm
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
    wteb__uolyj = None
    yszmb__torv = {}

    def lookup(var, already_seen, varonly=True):
        val = yszmb__torv.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    luvdj__sunsm = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        fcgc__zrer = stmt.target
        axg__ncl = stmt.value
        yszmb__torv[fcgc__zrer.name] = axg__ncl
        if isinstance(axg__ncl, ir.Var) and axg__ncl.name in yszmb__torv:
            axg__ncl = lookup(axg__ncl, set())
        if isinstance(axg__ncl, ir.Expr):
            wtk__xbnxt = set(lookup(jpbp__qhjsb, set(), True).name for
                jpbp__qhjsb in axg__ncl.list_vars())
            if name in wtk__xbnxt:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(axg__ncl)]
                vnnt__ehrg = [x for x, ojo__yfu in args if ojo__yfu.name !=
                    name]
                args = [(x, ojo__yfu) for x, ojo__yfu in args if x !=
                    ojo__yfu.name]
                jpvm__vzqr = dict(args)
                if len(vnnt__ehrg) == 1:
                    jpvm__vzqr[vnnt__ehrg[0]] = ir.Var(fcgc__zrer.scope, 
                        name + '#init', fcgc__zrer.loc)
                replace_vars_inner(axg__ncl, jpvm__vzqr)
                wteb__uolyj = nodes[i:]
                break
    return wteb__uolyj


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
        hztg__lghbg = expand_aliases({jpbp__qhjsb.name for jpbp__qhjsb in
            stmt.list_vars()}, alias_map, arg_aliases)
        szf__jqgu = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        vyaef__hvprf = expand_aliases({jpbp__qhjsb.name for jpbp__qhjsb in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        injpp__jvu = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(szf__jqgu & vyaef__hvprf | injpp__jvu & hztg__lghbg) == 0:
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
    qiwv__zodm = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            qiwv__zodm.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                qiwv__zodm.update(get_parfor_writes(stmt, func_ir))
    return qiwv__zodm


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    qiwv__zodm = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        qiwv__zodm.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        qiwv__zodm = {jpbp__qhjsb.name for jpbp__qhjsb in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        qiwv__zodm = {jpbp__qhjsb.name for jpbp__qhjsb in stmt.
            get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            qiwv__zodm.update({jpbp__qhjsb.name for jpbp__qhjsb in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        ldgpe__ezjca = guard(find_callname, func_ir, stmt.value)
        if ldgpe__ezjca in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'
            ), ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            qiwv__zodm.add(stmt.value.args[0].name)
        if ldgpe__ezjca == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            qiwv__zodm.add(stmt.value.args[1].name)
    return qiwv__zodm


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
        fcie__gxfy = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        sxjqz__xilu = fcie__gxfy.format(self, msg)
        self.args = sxjqz__xilu,
    else:
        fcie__gxfy = _termcolor.errmsg('{0}')
        sxjqz__xilu = fcie__gxfy.format(self)
        self.args = sxjqz__xilu,
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
        for zwes__rxv in options['distributed']:
            dist_spec[zwes__rxv] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for zwes__rxv in options['distributed_block']:
            dist_spec[zwes__rxv] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    hss__stzs = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, bwqg__tvi in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(bwqg__tvi)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    cfseu__ypo = {}
    for ygi__kzkj in reversed(inspect.getmro(cls)):
        cfseu__ypo.update(ygi__kzkj.__dict__)
    kee__bgdy, jfezj__mjqo, aegm__xaa, cvjep__fdijr = {}, {}, {}, {}
    for iurfy__nltp, jpbp__qhjsb in cfseu__ypo.items():
        if isinstance(jpbp__qhjsb, pytypes.FunctionType):
            kee__bgdy[iurfy__nltp] = jpbp__qhjsb
        elif isinstance(jpbp__qhjsb, property):
            jfezj__mjqo[iurfy__nltp] = jpbp__qhjsb
        elif isinstance(jpbp__qhjsb, staticmethod):
            aegm__xaa[iurfy__nltp] = jpbp__qhjsb
        else:
            cvjep__fdijr[iurfy__nltp] = jpbp__qhjsb
    aqltg__djvs = (set(kee__bgdy) | set(jfezj__mjqo) | set(aegm__xaa)) & set(
        spec)
    if aqltg__djvs:
        raise NameError('name shadowing: {0}'.format(', '.join(aqltg__djvs)))
    qech__qbmp = cvjep__fdijr.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(cvjep__fdijr)
    if cvjep__fdijr:
        msg = 'class members are not yet supported: {0}'
        daalq__vqr = ', '.join(cvjep__fdijr.keys())
        raise TypeError(msg.format(daalq__vqr))
    for iurfy__nltp, jpbp__qhjsb in jfezj__mjqo.items():
        if jpbp__qhjsb.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(iurfy__nltp)
                )
    jit_methods = {iurfy__nltp: bodo.jit(returns_maybe_distributed=
        hss__stzs)(jpbp__qhjsb) for iurfy__nltp, jpbp__qhjsb in kee__bgdy.
        items()}
    jit_props = {}
    for iurfy__nltp, jpbp__qhjsb in jfezj__mjqo.items():
        alj__ibct = {}
        if jpbp__qhjsb.fget:
            alj__ibct['get'] = bodo.jit(jpbp__qhjsb.fget)
        if jpbp__qhjsb.fset:
            alj__ibct['set'] = bodo.jit(jpbp__qhjsb.fset)
        jit_props[iurfy__nltp] = alj__ibct
    jit_static_methods = {iurfy__nltp: bodo.jit(jpbp__qhjsb.__func__) for 
        iurfy__nltp, jpbp__qhjsb in aegm__xaa.items()}
    rgyvm__ocllr = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    objx__oug = dict(class_type=rgyvm__ocllr, __doc__=qech__qbmp)
    objx__oug.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), objx__oug)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, rgyvm__ocllr)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(rgyvm__ocllr, typingctx, targetctx).register()
    as_numba_type.register(cls, rgyvm__ocllr.instance_type)
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
    cck__mgsz = ','.join('{0}:{1}'.format(iurfy__nltp, jpbp__qhjsb) for 
        iurfy__nltp, jpbp__qhjsb in struct.items())
    yvrya__wqau = ','.join('{0}:{1}'.format(iurfy__nltp, jpbp__qhjsb) for 
        iurfy__nltp, jpbp__qhjsb in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), cck__mgsz, yvrya__wqau)
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
    rzl__cws = numba.core.typeinfer.fold_arg_vars(typevars, self.args, self
        .vararg, self.kws)
    if rzl__cws is None:
        return
    xknnc__mitz, aewnv__zun = rzl__cws
    for a in itertools.chain(xknnc__mitz, aewnv__zun.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, xknnc__mitz, aewnv__zun)
    except ForceLiteralArg as e:
        yuvca__pkm = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(yuvca__pkm, self.kws)
        wbb__afteh = set()
        oksho__bhu = set()
        qqhf__ktnjk = {}
        for jtmaq__zhajs in e.requested_args:
            jgqxj__kercr = typeinfer.func_ir.get_definition(folded[
                jtmaq__zhajs])
            if isinstance(jgqxj__kercr, ir.Arg):
                wbb__afteh.add(jgqxj__kercr.index)
                if jgqxj__kercr.index in e.file_infos:
                    qqhf__ktnjk[jgqxj__kercr.index] = e.file_infos[jgqxj__kercr
                        .index]
            else:
                oksho__bhu.add(jtmaq__zhajs)
        if oksho__bhu:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif wbb__afteh:
            raise ForceLiteralArg(wbb__afteh, loc=self.loc, file_infos=
                qqhf__ktnjk)
    if sig is None:
        pubhv__iygc = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in xknnc__mitz]
        args += [('%s=%s' % (iurfy__nltp, jpbp__qhjsb)) for iurfy__nltp,
            jpbp__qhjsb in sorted(aewnv__zun.items())]
        whz__vvm = pubhv__iygc.format(fnty, ', '.join(map(str, args)))
        xoxbr__wtl = context.explain_function_type(fnty)
        msg = '\n'.join([whz__vvm, xoxbr__wtl])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        oext__eplkh = context.unify_pairs(sig.recvr, fnty.this)
        if oext__eplkh is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if oext__eplkh is not None and oext__eplkh.is_precise():
            mnj__oue = fnty.copy(this=oext__eplkh)
            typeinfer.propagate_refined_type(self.func, mnj__oue)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            fzwl__ppmk = target.getone()
            if context.unify_pairs(fzwl__ppmk, sig.return_type) == fzwl__ppmk:
                sig = sig.replace(return_type=fzwl__ppmk)
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
        vljbt__hhnyr = '*other* must be a {} but got a {} instead'
        raise TypeError(vljbt__hhnyr.format(ForceLiteralArg, type(other)))
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
    kbpxv__nndbl = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for iurfy__nltp, jpbp__qhjsb in kwargs.items():
        pqwwr__aeivb = None
        try:
            uolh__gstu = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var
                ('dummy'), loc)
            func_ir._definitions[uolh__gstu.name] = [jpbp__qhjsb]
            pqwwr__aeivb = get_const_value_inner(func_ir, uolh__gstu)
            func_ir._definitions.pop(uolh__gstu.name)
            if isinstance(pqwwr__aeivb, str):
                pqwwr__aeivb = sigutils._parse_signature_string(pqwwr__aeivb)
            if isinstance(pqwwr__aeivb, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {iurfy__nltp} is annotated as type class {pqwwr__aeivb}."""
                    )
            assert isinstance(pqwwr__aeivb, types.Type)
            if isinstance(pqwwr__aeivb, (types.List, types.Set)):
                pqwwr__aeivb = pqwwr__aeivb.copy(reflected=False)
            kbpxv__nndbl[iurfy__nltp] = pqwwr__aeivb
        except BodoError as rzt__vekay:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(pqwwr__aeivb, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(jpbp__qhjsb, ir.Global):
                    msg = f'Global {jpbp__qhjsb.name!r} is not defined.'
                if isinstance(jpbp__qhjsb, ir.FreeVar):
                    msg = f'Freevar {jpbp__qhjsb.name!r} is not defined.'
            if isinstance(jpbp__qhjsb, ir.Expr
                ) and jpbp__qhjsb.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=iurfy__nltp, msg=msg, loc=loc)
    for name, typ in kbpxv__nndbl.items():
        self._legalize_arg_type(name, typ, loc)
    return kbpxv__nndbl


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
    ljm__wdjez = inst.arg
    assert ljm__wdjez > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(ljm__wdjez)]))
    tmps = [state.make_temp() for _ in range(ljm__wdjez - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    oao__cbd = ir.Global('format', format, loc=self.loc)
    self.store(value=oao__cbd, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    fbl__drty = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=fbl__drty, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    ljm__wdjez = inst.arg
    assert ljm__wdjez > 0, 'invalid BUILD_STRING count'
    pzsyr__mtb = self.get(strings[0])
    for other, kebvk__pcbsf in zip(strings[1:], tmps):
        other = self.get(other)
        xojy__rjn = ir.Expr.binop(operator.add, lhs=pzsyr__mtb, rhs=other,
            loc=self.loc)
        self.store(xojy__rjn, kebvk__pcbsf)
        pzsyr__mtb = self.get(kebvk__pcbsf)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    mgnhl__occ = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, mgnhl__occ])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    gwcr__yqa = mk_unique_var(f'{var_name}')
    godil__rso = gwcr__yqa.replace('<', '_').replace('>', '_')
    godil__rso = godil__rso.replace('.', '_').replace('$', '_v')
    return godil__rso


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
                zyf__tlac = get_overload_const_str(val2)
                if zyf__tlac != 'ns':
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
        uxwk__fbhqy = states['defmap']
        if len(uxwk__fbhqy) == 0:
            licro__xjmq = assign.target
            numba.core.ssa._logger.debug('first assign: %s', licro__xjmq)
            if licro__xjmq.name not in scope.localvars:
                licro__xjmq = scope.define(assign.target.name, loc=assign.loc)
        else:
            licro__xjmq = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=licro__xjmq, value=assign.value, loc=
            assign.loc)
        uxwk__fbhqy[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    dlat__tiqr = []
    for iurfy__nltp, jpbp__qhjsb in typing.npydecl.registry.globals:
        if iurfy__nltp == func:
            dlat__tiqr.append(jpbp__qhjsb)
    for iurfy__nltp, jpbp__qhjsb in typing.templates.builtin_registry.globals:
        if iurfy__nltp == func:
            dlat__tiqr.append(jpbp__qhjsb)
    if len(dlat__tiqr) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return dlat__tiqr


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    btrj__efbz = {}
    okggf__str = find_topo_order(blocks)
    gctu__xxgb = {}
    for label in okggf__str:
        block = blocks[label]
        monpi__jsoh = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                fcgc__zrer = stmt.target.name
                axg__ncl = stmt.value
                if (axg__ncl.op == 'getattr' and axg__ncl.attr in arr_math and
                    isinstance(typemap[axg__ncl.value.name], types.npytypes
                    .Array)):
                    axg__ncl = stmt.value
                    jfzh__toe = axg__ncl.value
                    btrj__efbz[fcgc__zrer] = jfzh__toe
                    scope = jfzh__toe.scope
                    loc = jfzh__toe.loc
                    saub__wpca = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[saub__wpca.name] = types.misc.Module(numpy)
                    adcjk__xio = ir.Global('np', numpy, loc)
                    htiz__kbowh = ir.Assign(adcjk__xio, saub__wpca, loc)
                    axg__ncl.value = saub__wpca
                    monpi__jsoh.append(htiz__kbowh)
                    func_ir._definitions[saub__wpca.name] = [adcjk__xio]
                    func = getattr(numpy, axg__ncl.attr)
                    cfcwt__ffwct = get_np_ufunc_typ_lst(func)
                    gctu__xxgb[fcgc__zrer] = cfcwt__ffwct
                if axg__ncl.op == 'call' and axg__ncl.func.name in btrj__efbz:
                    jfzh__toe = btrj__efbz[axg__ncl.func.name]
                    rtdw__znxm = calltypes.pop(axg__ncl)
                    stqcz__ifkl = rtdw__znxm.args[:len(axg__ncl.args)]
                    xlsib__ucob = {name: typemap[jpbp__qhjsb.name] for name,
                        jpbp__qhjsb in axg__ncl.kws}
                    mtst__kgdn = gctu__xxgb[axg__ncl.func.name]
                    nltu__yfew = None
                    for grrv__egl in mtst__kgdn:
                        try:
                            nltu__yfew = grrv__egl.get_call_type(typingctx,
                                [typemap[jfzh__toe.name]] + list(
                                stqcz__ifkl), xlsib__ucob)
                            typemap.pop(axg__ncl.func.name)
                            typemap[axg__ncl.func.name] = grrv__egl
                            calltypes[axg__ncl] = nltu__yfew
                            break
                        except Exception as rzt__vekay:
                            pass
                    if nltu__yfew is None:
                        raise TypeError(
                            f'No valid template found for {axg__ncl.func.name}'
                            )
                    axg__ncl.args = [jfzh__toe] + axg__ncl.args
            monpi__jsoh.append(stmt)
        block.body = monpi__jsoh


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    kfkl__vxqcy = ufunc.nin
    htve__reb = ufunc.nout
    vdugz__wlzd = ufunc.nargs
    assert vdugz__wlzd == kfkl__vxqcy + htve__reb
    if len(args) < kfkl__vxqcy:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            kfkl__vxqcy))
    if len(args) > vdugz__wlzd:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            vdugz__wlzd))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    dkdng__rrow = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    ygxb__mpv = max(dkdng__rrow)
    irhvs__scs = args[kfkl__vxqcy:]
    if not all(d == ygxb__mpv for d in dkdng__rrow[kfkl__vxqcy:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(qhznr__xpklf, types.ArrayCompatible) and not
        isinstance(qhznr__xpklf, types.Bytes) for qhznr__xpklf in irhvs__scs):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(qhznr__xpklf.mutable for qhznr__xpklf in irhvs__scs):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    sube__itz = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    mnapi__klaaz = None
    if ygxb__mpv > 0 and len(irhvs__scs) < ufunc.nout:
        mnapi__klaaz = 'C'
        eodc__qamg = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in eodc__qamg and 'F' in eodc__qamg:
            mnapi__klaaz = 'F'
    return sube__itz, irhvs__scs, ygxb__mpv, mnapi__klaaz


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
        ybd__olwkv = 'Dict.key_type cannot be of type {}'
        raise TypingError(ybd__olwkv.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        ybd__olwkv = 'Dict.value_type cannot be of type {}'
        raise TypingError(ybd__olwkv.format(valty))
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
    aut__maj = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[aut__maj]
        return impl, args
    except KeyError as rzt__vekay:
        pass
    impl, args = self._build_impl(aut__maj, args, kws)
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
    gdyw__jewnu = False
    blocks = parfor.loop_body.copy()
    for label, block in blocks.items():
        if len(block.body):
            tpplw__yhal = block.body[-1]
            if isinstance(tpplw__yhal, ir.Branch):
                if len(blocks[tpplw__yhal.truebr].body) == 1 and len(blocks
                    [tpplw__yhal.falsebr].body) == 1:
                    qwr__png = blocks[tpplw__yhal.truebr].body[0]
                    ccd__sgf = blocks[tpplw__yhal.falsebr].body[0]
                    if isinstance(qwr__png, ir.Jump) and isinstance(ccd__sgf,
                        ir.Jump) and qwr__png.target == ccd__sgf.target:
                        parfor.loop_body[label].body[-1] = ir.Jump(qwr__png
                            .target, tpplw__yhal.loc)
                        gdyw__jewnu = True
                elif len(blocks[tpplw__yhal.truebr].body) == 1:
                    qwr__png = blocks[tpplw__yhal.truebr].body[0]
                    if isinstance(qwr__png, ir.Jump
                        ) and qwr__png.target == tpplw__yhal.falsebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(qwr__png
                            .target, tpplw__yhal.loc)
                        gdyw__jewnu = True
                elif len(blocks[tpplw__yhal.falsebr].body) == 1:
                    ccd__sgf = blocks[tpplw__yhal.falsebr].body[0]
                    if isinstance(ccd__sgf, ir.Jump
                        ) and ccd__sgf.target == tpplw__yhal.truebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(ccd__sgf
                            .target, tpplw__yhal.loc)
                        gdyw__jewnu = True
    return gdyw__jewnu


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        iise__zgdo = find_topo_order(parfor.loop_body)
    xktzr__aywcf = iise__zgdo[0]
    gwmrh__kgry = {}
    _update_parfor_get_setitems(parfor.loop_body[xktzr__aywcf].body, parfor
        .index_var, alias_map, gwmrh__kgry, lives_n_aliases)
    uwdir__oorm = set(gwmrh__kgry.keys())
    for ijz__zyq in iise__zgdo:
        if ijz__zyq == xktzr__aywcf:
            continue
        for stmt in parfor.loop_body[ijz__zyq].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            sog__epbzg = set(jpbp__qhjsb.name for jpbp__qhjsb in stmt.
                list_vars())
            hqtr__ueq = sog__epbzg & uwdir__oorm
            for a in hqtr__ueq:
                gwmrh__kgry.pop(a, None)
    for ijz__zyq in iise__zgdo:
        if ijz__zyq == xktzr__aywcf:
            continue
        block = parfor.loop_body[ijz__zyq]
        qibqt__udu = gwmrh__kgry.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            qibqt__udu, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    glr__pojjh = max(blocks.keys())
    pazy__grjl, qmy__ldp = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    jknio__pttzl = ir.Jump(pazy__grjl, ir.Loc('parfors_dummy', -1))
    blocks[glr__pojjh].body.append(jknio__pttzl)
    pbtr__wqzll = compute_cfg_from_blocks(blocks)
    vrgxj__krtrt = compute_use_defs(blocks)
    xss__xxr = compute_live_map(pbtr__wqzll, blocks, vrgxj__krtrt.usemap,
        vrgxj__krtrt.defmap)
    alias_set = set(alias_map.keys())
    for label, block in blocks.items():
        monpi__jsoh = []
        rjwr__sfrn = {jpbp__qhjsb.name for jpbp__qhjsb in block.terminator.
            list_vars()}
        for flg__zuhlw, inb__ptmj in pbtr__wqzll.successors(label):
            rjwr__sfrn |= xss__xxr[flg__zuhlw]
        for stmt in reversed(block.body):
            nvjw__erdfn = rjwr__sfrn & alias_set
            for jpbp__qhjsb in nvjw__erdfn:
                rjwr__sfrn |= alias_map[jpbp__qhjsb]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in rjwr__sfrn and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                ldgpe__ezjca = guard(find_callname, func_ir, stmt.value)
                if ldgpe__ezjca == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in rjwr__sfrn and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            rjwr__sfrn |= {jpbp__qhjsb.name for jpbp__qhjsb in stmt.list_vars()
                }
            monpi__jsoh.append(stmt)
        monpi__jsoh.reverse()
        block.body = monpi__jsoh
    typemap.pop(qmy__ldp.name)
    blocks[glr__pojjh].body.pop()
    gdyw__jewnu = True
    while gdyw__jewnu:
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
        gdyw__jewnu = trim_empty_parfor_branches(parfor)
    yxsy__bldx = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        yxsy__bldx &= len(block.body) == 0
    if yxsy__bldx:
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
    tik__ixajj = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                tik__ixajj += 1
                parfor = stmt
                dvo__gvsl = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = dvo__gvsl.scope
                loc = ir.Loc('parfors_dummy', -1)
                qjjb__ziex = ir.Var(scope, mk_unique_var('$const'), loc)
                dvo__gvsl.body.append(ir.Assign(ir.Const(0, loc),
                    qjjb__ziex, loc))
                dvo__gvsl.body.append(ir.Return(qjjb__ziex, loc))
                pbtr__wqzll = compute_cfg_from_blocks(parfor.loop_body)
                for duex__ngtoc in pbtr__wqzll.dead_nodes():
                    del parfor.loop_body[duex__ngtoc]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                dvo__gvsl = parfor.loop_body[max(parfor.loop_body.keys())]
                dvo__gvsl.body.pop()
                dvo__gvsl.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return tik__ixajj


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def simplify_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import merge_adjacent_blocks, rename_labels
    pbtr__wqzll = compute_cfg_from_blocks(blocks)

    def find_single_branch(label):
        block = blocks[label]
        return len(block.body) == 1 and isinstance(block.body[0], ir.Branch
            ) and label != pbtr__wqzll.entry_point()
    tnbq__qis = list(filter(find_single_branch, blocks.keys()))
    hqqg__eoi = set()
    for label in tnbq__qis:
        inst = blocks[label].body[0]
        cre__ikh = pbtr__wqzll.predecessors(label)
        obozj__lqoq = True
        for uhq__veov, rlf__wzm in cre__ikh:
            block = blocks[uhq__veov]
            if isinstance(block.body[-1], ir.Jump):
                block.body[-1] = copy.copy(inst)
            else:
                obozj__lqoq = False
        if obozj__lqoq:
            hqqg__eoi.add(label)
    for label in hqqg__eoi:
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
            aahk__tpjf = self.overloads.get(tuple(args))
            if aahk__tpjf is not None:
                return aahk__tpjf.entry_point
            self._pre_compile(args, return_type, flags)
            oyc__wae = self.func_ir
            wbjzi__jpybw = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=wbjzi__jpybw):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=oyc__wae, args=args,
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
        bwav__vkr = copy.deepcopy(flags)
        bwav__vkr.no_rewrites = True

        def compile_local(the_ir, the_flags):
            uiyu__tiu = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return uiyu__tiu.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        nwrd__wgys = compile_local(func_ir, bwav__vkr)
        ipv__ygxta = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    ipv__ygxta = compile_local(func_ir, flags)
                except Exception as rzt__vekay:
                    pass
        if ipv__ygxta is not None:
            cres = ipv__ygxta
        else:
            cres = nwrd__wgys
        return cres
    else:
        uiyu__tiu = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return uiyu__tiu.compile_ir(func_ir=func_ir, lifted=lifted,
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
    wqe__cqjpy = self.get_data_type(typ.dtype)
    dnvd__jeeop = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        dnvd__jeeop):
        eoseu__bcgw = ary.ctypes.data
        vphg__xarhz = self.add_dynamic_addr(builder, eoseu__bcgw, info=str(
            type(eoseu__bcgw)))
        ciadt__czu = self.add_dynamic_addr(builder, id(ary), info=str(type(
            ary)))
        self.global_arrays.append(ary)
    else:
        drj__sjbz = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            drj__sjbz = drj__sjbz.view('int64')
        val = bytearray(drj__sjbz.data)
        nmc__xgu = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        vphg__xarhz = cgutils.global_constant(builder, '.const.array.data',
            nmc__xgu)
        vphg__xarhz.align = self.get_abi_alignment(wqe__cqjpy)
        ciadt__czu = None
    nfv__mij = self.get_value_type(types.intp)
    ykqbe__ekz = [self.get_constant(types.intp, agnbf__wmhx) for
        agnbf__wmhx in ary.shape]
    nsvyf__adxlh = lir.Constant(lir.ArrayType(nfv__mij, len(ykqbe__ekz)),
        ykqbe__ekz)
    mpjde__dslop = [self.get_constant(types.intp, agnbf__wmhx) for
        agnbf__wmhx in ary.strides]
    bfhb__qln = lir.Constant(lir.ArrayType(nfv__mij, len(mpjde__dslop)),
        mpjde__dslop)
    ekxqa__rcbu = self.get_constant(types.intp, ary.dtype.itemsize)
    vwc__vasp = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        vwc__vasp, ekxqa__rcbu, vphg__xarhz.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), nsvyf__adxlh, bfhb__qln])


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
    qvhnq__hoio = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    ytt__ujl = lir.Function(module, qvhnq__hoio, name='nrt_atomic_{0}'.
        format(op))
    [fzsgc__jstz] = ytt__ujl.args
    ozr__jspu = ytt__ujl.append_basic_block()
    builder = lir.IRBuilder(ozr__jspu)
    uyrzi__wesr = lir.Constant(_word_type, 1)
    if False:
        acrn__sdkmz = builder.atomic_rmw(op, fzsgc__jstz, uyrzi__wesr,
            ordering=ordering)
        res = getattr(builder, op)(acrn__sdkmz, uyrzi__wesr)
        builder.ret(res)
    else:
        acrn__sdkmz = builder.load(fzsgc__jstz)
        gnc__dpmm = getattr(builder, op)(acrn__sdkmz, uyrzi__wesr)
        flwo__aqq = builder.icmp_signed('!=', acrn__sdkmz, lir.Constant(
            acrn__sdkmz.type, -1))
        with cgutils.if_likely(builder, flwo__aqq):
            builder.store(gnc__dpmm, fzsgc__jstz)
        builder.ret(gnc__dpmm)
    return ytt__ujl


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
        fheou__aqsb = state.targetctx.codegen()
        state.library = fheou__aqsb.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    rco__udrw = state.func_ir
    typemap = state.typemap
    aknu__tijw = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    fpcxh__iqet = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            rco__udrw, typemap, aknu__tijw, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            ppr__bixjh = lowering.Lower(targetctx, library, fndesc,
                rco__udrw, metadata=metadata)
            ppr__bixjh.lower()
            if not flags.no_cpython_wrapper:
                ppr__bixjh.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(aknu__tijw, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        ppr__bixjh.create_cfunc_wrapper()
            env = ppr__bixjh.env
            tmtsl__dfo = ppr__bixjh.call_helper
            del ppr__bixjh
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, tmtsl__dfo, cfunc=None, env=env)
        else:
            mcsn__gckbz = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(mcsn__gckbz, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, tmtsl__dfo, cfunc=
                mcsn__gckbz, env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        fdbhj__wpqvp = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = fdbhj__wpqvp - fpcxh__iqet
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
        vxei__nltuk = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, vxei__nltuk),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            ftv__ddxdk.do_break()
        ryc__bikku = c.builder.icmp_signed('!=', vxei__nltuk, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(ryc__bikku, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, vxei__nltuk)
                c.pyapi.decref(vxei__nltuk)
                ftv__ddxdk.do_break()
        c.pyapi.decref(vxei__nltuk)
    krn__eyb, list = listobj.ListInstance.allocate_ex(c.context, c.builder,
        typ, size)
    with c.builder.if_else(krn__eyb, likely=True) as (pndq__syry, lswt__clnih):
        with pndq__syry:
            list.size = size
            lzw__plez = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                lzw__plez), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        lzw__plez))
                    with cgutils.for_range(c.builder, size) as ftv__ddxdk:
                        itemobj = c.pyapi.list_getitem(obj, ftv__ddxdk.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        zzlyy__eylm = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(zzlyy__eylm.is_error, likely
                            =False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            ftv__ddxdk.do_break()
                        list.setitem(ftv__ddxdk.index, zzlyy__eylm.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with lswt__clnih:
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
    eujr__gbki, agupb__rxoaj, iojgk__hfa, ftmv__nxnqn, elrri__slco = (
        compile_time_get_string_data(literal_string))
    yaal__utc = builder.module
    gv = context.insert_const_bytes(yaal__utc, eujr__gbki)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        agupb__rxoaj), context.get_constant(types.int32, iojgk__hfa),
        context.get_constant(types.uint32, ftmv__nxnqn), context.
        get_constant(_Py_hash_t, -1), context.get_constant_null(types.
        MemInfoPointer(types.voidptr)), context.get_constant_null(types.
        pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    fpff__rdb = None
    if isinstance(shape, types.Integer):
        fpff__rdb = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(agnbf__wmhx, (types.Integer, types.IntEnumMember)
            ) for agnbf__wmhx in shape):
            fpff__rdb = len(shape)
    return fpff__rdb


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
            fpff__rdb = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if fpff__rdb == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(fpff__rdb))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            azk__mkh = self._get_names(x)
            if len(azk__mkh) != 0:
                return azk__mkh[0]
            return azk__mkh
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    azk__mkh = self._get_names(obj)
    if len(azk__mkh) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(azk__mkh[0])


def get_equiv_set(self, obj):
    azk__mkh = self._get_names(obj)
    if len(azk__mkh) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(azk__mkh[0])


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
    eirhu__svkab = []
    for enpxj__zdjn in func_ir.arg_names:
        if enpxj__zdjn in typemap and isinstance(typemap[enpxj__zdjn],
            types.containers.UniTuple) and typemap[enpxj__zdjn].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(enpxj__zdjn))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for uom__rponz in func_ir.blocks.values():
        for stmt in uom__rponz.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    axune__knhfq = getattr(val, 'code', None)
                    if axune__knhfq is not None:
                        if getattr(val, 'closure', None) is not None:
                            ncsxt__siyuu = (
                                '<creating a function from a closure>')
                            xojy__rjn = ''
                        else:
                            ncsxt__siyuu = axune__knhfq.co_name
                            xojy__rjn = '(%s) ' % ncsxt__siyuu
                    else:
                        ncsxt__siyuu = '<could not ascertain use case>'
                        xojy__rjn = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (ncsxt__siyuu, xojy__rjn))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                jlxu__nau = False
                if isinstance(val, pytypes.FunctionType):
                    jlxu__nau = val in {numba.gdb, numba.gdb_init}
                if not jlxu__nau:
                    jlxu__nau = getattr(val, '_name', '') == 'gdb_internal'
                if jlxu__nau:
                    eirhu__svkab.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    tts__zvfnn = func_ir.get_definition(var)
                    ngns__fgfmv = guard(find_callname, func_ir, tts__zvfnn)
                    if ngns__fgfmv and ngns__fgfmv[1] == 'numpy':
                        ty = getattr(numpy, ngns__fgfmv[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    tkq__xnjuy = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(tkq__xnjuy), loc=stmt.loc)
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
    if len(eirhu__svkab) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        ivn__qcbca = '\n'.join([x.strformat() for x in eirhu__svkab])
        raise errors.UnsupportedError(msg % ivn__qcbca)


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
    iurfy__nltp, jpbp__qhjsb = next(iter(val.items()))
    bhixp__ulpo = typeof_impl(iurfy__nltp, c)
    qds__xpjv = typeof_impl(jpbp__qhjsb, c)
    if bhixp__ulpo is None or qds__xpjv is None:
        raise ValueError(
            f'Cannot type dict element type {type(iurfy__nltp)}, {type(jpbp__qhjsb)}'
            )
    return types.DictType(bhixp__ulpo, qds__xpjv)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    iiwn__yofzl = cgutils.alloca_once_value(c.builder, val)
    zmmxg__yufce = c.pyapi.object_hasattr_string(val, '_opaque')
    qhkq__yytw = c.builder.icmp_unsigned('==', zmmxg__yufce, lir.Constant(
        zmmxg__yufce.type, 0))
    lst__skytd = typ.key_type
    zwxnv__lveb = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(lst__skytd, zwxnv__lveb)

    def copy_dict(out_dict, in_dict):
        for iurfy__nltp, jpbp__qhjsb in in_dict.items():
            out_dict[iurfy__nltp] = jpbp__qhjsb
    with c.builder.if_then(qhkq__yytw):
        zrkg__oby = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        dgbg__yfgna = c.pyapi.call_function_objargs(zrkg__oby, [])
        dlsaw__nmk = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(dlsaw__nmk, [dgbg__yfgna, val])
        c.builder.store(dgbg__yfgna, iiwn__yofzl)
    val = c.builder.load(iiwn__yofzl)
    orpa__esop = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    mij__tpkd = c.pyapi.object_type(val)
    zln__thq = c.builder.icmp_unsigned('==', mij__tpkd, orpa__esop)
    with c.builder.if_else(zln__thq) as (qxlwt__mima, luk__iyip):
        with qxlwt__mima:
            uptz__milk = c.pyapi.object_getattr_string(val, '_opaque')
            ryvze__zfl = types.MemInfoPointer(types.voidptr)
            zzlyy__eylm = c.unbox(ryvze__zfl, uptz__milk)
            mi = zzlyy__eylm.value
            maxx__zfmu = ryvze__zfl, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *maxx__zfmu)
            rnmw__bke = context.get_constant_null(maxx__zfmu[1])
            args = mi, rnmw__bke
            rogm__lyqs, nykwl__upsmh = c.pyapi.call_jit_code(convert, sig, args
                )
            c.context.nrt.decref(c.builder, typ, nykwl__upsmh)
            c.pyapi.decref(uptz__milk)
            njdo__djvx = c.builder.basic_block
        with luk__iyip:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", mij__tpkd, orpa__esop)
            nfofd__vgy = c.builder.basic_block
    jzb__mmjn = c.builder.phi(nykwl__upsmh.type)
    veh__bge = c.builder.phi(rogm__lyqs.type)
    jzb__mmjn.add_incoming(nykwl__upsmh, njdo__djvx)
    jzb__mmjn.add_incoming(nykwl__upsmh.type(None), nfofd__vgy)
    veh__bge.add_incoming(rogm__lyqs, njdo__djvx)
    veh__bge.add_incoming(cgutils.true_bit, nfofd__vgy)
    c.pyapi.decref(orpa__esop)
    c.pyapi.decref(mij__tpkd)
    with c.builder.if_then(qhkq__yytw):
        c.pyapi.decref(val)
    return NativeValue(jzb__mmjn, is_error=veh__bge)


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
    umge__mefo = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=umge__mefo, name=updatevar)
    tla__wbupt = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=tla__wbupt, name=res)


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
        for iurfy__nltp, jpbp__qhjsb in other.items():
            d[iurfy__nltp] = jpbp__qhjsb
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
    xojy__rjn = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(xojy__rjn, res)


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
    lfybt__ixg = PassManager(name)
    if state.func_ir is None:
        lfybt__ixg.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            lfybt__ixg.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        lfybt__ixg.add_pass(FixupArgs, 'fix up args')
    lfybt__ixg.add_pass(IRProcessing, 'processing IR')
    lfybt__ixg.add_pass(WithLifting, 'Handle with contexts')
    lfybt__ixg.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        lfybt__ixg.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        lfybt__ixg.add_pass(DeadBranchPrune, 'dead branch pruning')
        lfybt__ixg.add_pass(GenericRewrites, 'nopython rewrites')
    lfybt__ixg.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    lfybt__ixg.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        lfybt__ixg.add_pass(DeadBranchPrune, 'dead branch pruning')
    lfybt__ixg.add_pass(FindLiterallyCalls, 'find literally calls')
    lfybt__ixg.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        lfybt__ixg.add_pass(ReconstructSSA, 'ssa')
    lfybt__ixg.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    lfybt__ixg.finalize()
    return lfybt__ixg


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
    a, keg__qlsck = args
    if isinstance(a, types.List) and isinstance(keg__qlsck, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(keg__qlsck, types.List):
        return signature(keg__qlsck, types.intp, keg__qlsck)


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
        hqcak__yeq, hrkc__ijk = 0, 1
    else:
        hqcak__yeq, hrkc__ijk = 1, 0
    edpv__hqt = ListInstance(context, builder, sig.args[hqcak__yeq], args[
        hqcak__yeq])
    pzjsy__dbua = edpv__hqt.size
    ujkcg__cxir = args[hrkc__ijk]
    lzw__plez = lir.Constant(ujkcg__cxir.type, 0)
    ujkcg__cxir = builder.select(cgutils.is_neg_int(builder, ujkcg__cxir),
        lzw__plez, ujkcg__cxir)
    vwc__vasp = builder.mul(ujkcg__cxir, pzjsy__dbua)
    eoet__czm = ListInstance.allocate(context, builder, sig.return_type,
        vwc__vasp)
    eoet__czm.size = vwc__vasp
    with cgutils.for_range_slice(builder, lzw__plez, vwc__vasp, pzjsy__dbua,
        inc=True) as (lvmar__gtabf, _):
        with cgutils.for_range(builder, pzjsy__dbua) as ftv__ddxdk:
            value = edpv__hqt.getitem(ftv__ddxdk.index)
            eoet__czm.setitem(builder.add(ftv__ddxdk.index, lvmar__gtabf),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, eoet__czm.value)


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
    zwb__qhbmo = first.unify(self, second)
    if zwb__qhbmo is not None:
        return zwb__qhbmo
    zwb__qhbmo = second.unify(self, first)
    if zwb__qhbmo is not None:
        return zwb__qhbmo
    batb__qqb = self.can_convert(fromty=first, toty=second)
    if batb__qqb is not None and batb__qqb <= Conversion.safe:
        return second
    batb__qqb = self.can_convert(fromty=second, toty=first)
    if batb__qqb is not None and batb__qqb <= Conversion.safe:
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
    vwc__vasp = payload.used
    listobj = c.pyapi.list_new(vwc__vasp)
    krn__eyb = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(krn__eyb, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(vwc__vasp.
            type, 0))
        with payload._iterate() as ftv__ddxdk:
            i = c.builder.load(index)
            item = ftv__ddxdk.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return krn__eyb, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    cep__swsgb = h.type
    ylhk__wjcdf = self.mask
    dtype = self._ty.dtype
    oztu__vaqu = context.typing_context
    fnty = oztu__vaqu.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(oztu__vaqu, (dtype, dtype), {})
    haaw__pup = context.get_function(fnty, sig)
    ljgzj__qirtv = ir.Constant(cep__swsgb, 1)
    tnbz__lyohi = ir.Constant(cep__swsgb, 5)
    jsi__erl = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, ylhk__wjcdf))
    if for_insert:
        yaxp__ijmu = ylhk__wjcdf.type(-1)
        eve__fwz = cgutils.alloca_once_value(builder, yaxp__ijmu)
    hhiz__kgol = builder.append_basic_block('lookup.body')
    wcn__zrkig = builder.append_basic_block('lookup.found')
    fpqod__uxz = builder.append_basic_block('lookup.not_found')
    zaa__rdg = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        uxktf__njvvv = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, uxktf__njvvv)):
            qnnr__ktydq = haaw__pup(builder, (item, entry.key))
            with builder.if_then(qnnr__ktydq):
                builder.branch(wcn__zrkig)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, uxktf__njvvv)):
            builder.branch(fpqod__uxz)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, uxktf__njvvv)):
                lbjr__rplj = builder.load(eve__fwz)
                lbjr__rplj = builder.select(builder.icmp_unsigned('==',
                    lbjr__rplj, yaxp__ijmu), i, lbjr__rplj)
                builder.store(lbjr__rplj, eve__fwz)
    with cgutils.for_range(builder, ir.Constant(cep__swsgb, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, ljgzj__qirtv)
        i = builder.and_(i, ylhk__wjcdf)
        builder.store(i, index)
    builder.branch(hhiz__kgol)
    with builder.goto_block(hhiz__kgol):
        i = builder.load(index)
        check_entry(i)
        uhq__veov = builder.load(jsi__erl)
        uhq__veov = builder.lshr(uhq__veov, tnbz__lyohi)
        i = builder.add(ljgzj__qirtv, builder.mul(i, tnbz__lyohi))
        i = builder.and_(ylhk__wjcdf, builder.add(i, uhq__veov))
        builder.store(i, index)
        builder.store(uhq__veov, jsi__erl)
        builder.branch(hhiz__kgol)
    with builder.goto_block(fpqod__uxz):
        if for_insert:
            i = builder.load(index)
            lbjr__rplj = builder.load(eve__fwz)
            i = builder.select(builder.icmp_unsigned('==', lbjr__rplj,
                yaxp__ijmu), i, lbjr__rplj)
            builder.store(i, index)
        builder.branch(zaa__rdg)
    with builder.goto_block(wcn__zrkig):
        builder.branch(zaa__rdg)
    builder.position_at_end(zaa__rdg)
    jlxu__nau = builder.phi(ir.IntType(1), 'found')
    jlxu__nau.add_incoming(cgutils.true_bit, wcn__zrkig)
    jlxu__nau.add_incoming(cgutils.false_bit, fpqod__uxz)
    return jlxu__nau, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    cjudv__uql = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    tcbm__jancn = payload.used
    ljgzj__qirtv = ir.Constant(tcbm__jancn.type, 1)
    tcbm__jancn = payload.used = builder.add(tcbm__jancn, ljgzj__qirtv)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, cjudv__uql), likely=True):
        payload.fill = builder.add(payload.fill, ljgzj__qirtv)
    if do_resize:
        self.upsize(tcbm__jancn)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    jlxu__nau, i = payload._lookup(item, h, for_insert=True)
    dex__pyevg = builder.not_(jlxu__nau)
    with builder.if_then(dex__pyevg):
        entry = payload.get_entry(i)
        cjudv__uql = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        tcbm__jancn = payload.used
        ljgzj__qirtv = ir.Constant(tcbm__jancn.type, 1)
        tcbm__jancn = payload.used = builder.add(tcbm__jancn, ljgzj__qirtv)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, cjudv__uql), likely=True):
            payload.fill = builder.add(payload.fill, ljgzj__qirtv)
        if do_resize:
            self.upsize(tcbm__jancn)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    tcbm__jancn = payload.used
    ljgzj__qirtv = ir.Constant(tcbm__jancn.type, 1)
    tcbm__jancn = payload.used = self._builder.sub(tcbm__jancn, ljgzj__qirtv)
    if do_resize:
        self.downsize(tcbm__jancn)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    qta__nkmw = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, qta__nkmw)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    dud__edwq = payload
    krn__eyb = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(krn__eyb), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with dud__edwq._iterate() as ftv__ddxdk:
        entry = ftv__ddxdk.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(dud__edwq.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as ftv__ddxdk:
        entry = ftv__ddxdk.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    krn__eyb = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(krn__eyb), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    krn__eyb = cgutils.alloca_once_value(builder, cgutils.true_bit)
    cep__swsgb = context.get_value_type(types.intp)
    lzw__plez = ir.Constant(cep__swsgb, 0)
    ljgzj__qirtv = ir.Constant(cep__swsgb, 1)
    znowe__dzzp = context.get_data_type(types.SetPayload(self._ty))
    ormmr__povdm = context.get_abi_sizeof(znowe__dzzp)
    auuhp__olgbx = self._entrysize
    ormmr__povdm -= auuhp__olgbx
    gry__llem, zvdl__yrz = cgutils.muladd_with_overflow(builder, nentries,
        ir.Constant(cep__swsgb, auuhp__olgbx), ir.Constant(cep__swsgb,
        ormmr__povdm))
    with builder.if_then(zvdl__yrz, likely=False):
        builder.store(cgutils.false_bit, krn__eyb)
    with builder.if_then(builder.load(krn__eyb), likely=True):
        if realloc:
            ryuee__wat = self._set.meminfo
            fzsgc__jstz = context.nrt.meminfo_varsize_alloc(builder,
                ryuee__wat, size=gry__llem)
            yam__ltyyl = cgutils.is_null(builder, fzsgc__jstz)
        else:
            vqrh__gglod = _imp_dtor(context, builder.module, self._ty)
            ryuee__wat = context.nrt.meminfo_new_varsize_dtor(builder,
                gry__llem, builder.bitcast(vqrh__gglod, cgutils.voidptr_t))
            yam__ltyyl = cgutils.is_null(builder, ryuee__wat)
        with builder.if_else(yam__ltyyl, likely=False) as (chutz__hwiae,
            pndq__syry):
            with chutz__hwiae:
                builder.store(cgutils.false_bit, krn__eyb)
            with pndq__syry:
                if not realloc:
                    self._set.meminfo = ryuee__wat
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, gry__llem, 255)
                payload.used = lzw__plez
                payload.fill = lzw__plez
                payload.finger = lzw__plez
                emc__pirrd = builder.sub(nentries, ljgzj__qirtv)
                payload.mask = emc__pirrd
    return builder.load(krn__eyb)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    krn__eyb = cgutils.alloca_once_value(builder, cgutils.true_bit)
    cep__swsgb = context.get_value_type(types.intp)
    lzw__plez = ir.Constant(cep__swsgb, 0)
    ljgzj__qirtv = ir.Constant(cep__swsgb, 1)
    znowe__dzzp = context.get_data_type(types.SetPayload(self._ty))
    ormmr__povdm = context.get_abi_sizeof(znowe__dzzp)
    auuhp__olgbx = self._entrysize
    ormmr__povdm -= auuhp__olgbx
    ylhk__wjcdf = src_payload.mask
    nentries = builder.add(ljgzj__qirtv, ylhk__wjcdf)
    gry__llem = builder.add(ir.Constant(cep__swsgb, ormmr__povdm), builder.
        mul(ir.Constant(cep__swsgb, auuhp__olgbx), nentries))
    with builder.if_then(builder.load(krn__eyb), likely=True):
        vqrh__gglod = _imp_dtor(context, builder.module, self._ty)
        ryuee__wat = context.nrt.meminfo_new_varsize_dtor(builder,
            gry__llem, builder.bitcast(vqrh__gglod, cgutils.voidptr_t))
        yam__ltyyl = cgutils.is_null(builder, ryuee__wat)
        with builder.if_else(yam__ltyyl, likely=False) as (chutz__hwiae,
            pndq__syry):
            with chutz__hwiae:
                builder.store(cgutils.false_bit, krn__eyb)
            with pndq__syry:
                self._set.meminfo = ryuee__wat
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = lzw__plez
                payload.mask = ylhk__wjcdf
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, auuhp__olgbx)
                with src_payload._iterate() as ftv__ddxdk:
                    context.nrt.incref(builder, self._ty.dtype, ftv__ddxdk.
                        entry.key)
    return builder.load(krn__eyb)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    wegel__jlv = context.get_value_type(types.voidptr)
    ydixu__bth = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [wegel__jlv, ydixu__bth, wegel__jlv])
    boxzn__hhq = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=boxzn__hhq)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        buwkg__kfr = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer()
            )
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, buwkg__kfr)
        with payload._iterate() as ftv__ddxdk:
            entry = ftv__ddxdk.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    iot__mogk, = sig.args
    kvm__tuoae, = args
    fvu__pdttw = numba.core.imputils.call_len(context, builder, iot__mogk,
        kvm__tuoae)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, fvu__pdttw)
    with numba.core.imputils.for_iter(context, builder, iot__mogk, kvm__tuoae
        ) as ftv__ddxdk:
        inst.add(ftv__ddxdk.value)
        context.nrt.decref(builder, set_type.dtype, ftv__ddxdk.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    iot__mogk = sig.args[1]
    kvm__tuoae = args[1]
    fvu__pdttw = numba.core.imputils.call_len(context, builder, iot__mogk,
        kvm__tuoae)
    if fvu__pdttw is not None:
        fdlnb__yqc = builder.add(inst.payload.used, fvu__pdttw)
        inst.upsize(fdlnb__yqc)
    with numba.core.imputils.for_iter(context, builder, iot__mogk, kvm__tuoae
        ) as ftv__ddxdk:
        vempn__axy = context.cast(builder, ftv__ddxdk.value, iot__mogk.
            dtype, inst.dtype)
        inst.add(vempn__axy)
        context.nrt.decref(builder, iot__mogk.dtype, ftv__ddxdk.value)
    if fvu__pdttw is not None:
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
    tae__egno = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, tae__egno, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    mcsn__gckbz = target_context.get_executable(library, fndesc, env)
    fkv__oxfjh = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=mcsn__gckbz, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return fkv__oxfjh


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
        zxc__tgg = MPI.COMM_WORLD
        gts__vmn = None
        if zxc__tgg.Get_rank() == 0:
            try:
                cbcee__swar = self.get_cache_path()
                os.makedirs(cbcee__swar, exist_ok=True)
                tempfile.TemporaryFile(dir=cbcee__swar).close()
            except Exception as e:
                gts__vmn = e
        gts__vmn = zxc__tgg.bcast(gts__vmn)
        if isinstance(gts__vmn, Exception):
            raise gts__vmn
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
    xugb__tmb = cgutils.create_struct_proxy(charseq.bytes_type)
    nzucl__nla = xugb__tmb(context, builder)
    if isinstance(nbytes, int):
        nbytes = ir.Constant(nzucl__nla.nitems.type, nbytes)
    nzucl__nla.meminfo = context.nrt.meminfo_alloc(builder, nbytes)
    nzucl__nla.nitems = nbytes
    nzucl__nla.itemsize = ir.Constant(nzucl__nla.itemsize.type, 1)
    nzucl__nla.data = context.nrt.meminfo_data(builder, nzucl__nla.meminfo)
    nzucl__nla.parent = cgutils.get_null_value(nzucl__nla.parent.type)
    nzucl__nla.shape = cgutils.pack_array(builder, [nzucl__nla.nitems],
        context.get_value_type(types.intp))
    nzucl__nla.strides = cgutils.pack_array(builder, [ir.Constant(
        nzucl__nla.strides.type.element, 1)], context.get_value_type(types.
        intp))
    return nzucl__nla


if _check_numba_change:
    lines = inspect.getsource(charseq._make_constant_bytes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b3ed23ad58baff7b935912e3e22f4d8af67423d8fd0e5f1836ba0b3028a6eb18':
        warnings.warn('charseq._make_constant_bytes has changed')
charseq._make_constant_bytes = _make_constant_bytes
