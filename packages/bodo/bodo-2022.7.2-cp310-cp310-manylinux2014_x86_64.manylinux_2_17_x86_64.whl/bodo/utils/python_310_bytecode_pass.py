"""
transforms the IR to handle bytecode issues in Python 3.10. This
should be removed once https://github.com/numba/numba/pull/7866
is included in Numba 0.56
"""
import operator
import numba
from numba.core import ir
from numba.core.compiler_machinery import FunctionPass, register_pass
from numba.core.errors import UnsupportedError
from numba.core.ir_utils import dprint_func_ir, get_definition, guard


@register_pass(mutates_CFG=False, analysis_only=False)
class Bodo310ByteCodePass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        dprint_func_ir(state.func_ir,
            'starting Bodo 3.10 Bytecode optimizations pass')
        peep_hole_call_function_ex_to_call_function_kw(state.func_ir)
        peep_hole_fuse_dict_add_updates(state.func_ir)
        peep_hole_fuse_tuple_adds(state.func_ir)
        return True


def peep_hole_fuse_tuple_adds(func_ir):
    for flkp__diq in func_ir.blocks.values():
        new_body = []
        anqf__bpkzi = {}
        for sfpg__dzdey, lbkx__fpl in enumerate(flkp__diq.body):
            qjy__sorn = None
            if isinstance(lbkx__fpl, ir.Assign) and isinstance(lbkx__fpl.
                value, ir.Expr):
                npnbc__bapm = lbkx__fpl.target.name
                if lbkx__fpl.value.op == 'build_tuple':
                    qjy__sorn = npnbc__bapm
                    anqf__bpkzi[npnbc__bapm] = lbkx__fpl.value.items
                elif lbkx__fpl.value.op == 'binop' and lbkx__fpl.value.fn == operator.add and lbkx__fpl.value.lhs.name in anqf__bpkzi and lbkx__fpl.value.rhs.name in anqf__bpkzi:
                    qjy__sorn = npnbc__bapm
                    new_items = anqf__bpkzi[lbkx__fpl.value.lhs.name
                        ] + anqf__bpkzi[lbkx__fpl.value.rhs.name]
                    szt__eaw = ir.Expr.build_tuple(new_items, lbkx__fpl.
                        value.loc)
                    anqf__bpkzi[npnbc__bapm] = new_items
                    del anqf__bpkzi[lbkx__fpl.value.lhs.name]
                    del anqf__bpkzi[lbkx__fpl.value.rhs.name]
                    if lbkx__fpl.value in func_ir._definitions[npnbc__bapm]:
                        func_ir._definitions[npnbc__bapm].remove(lbkx__fpl.
                            value)
                    func_ir._definitions[npnbc__bapm].append(szt__eaw)
                    lbkx__fpl = ir.Assign(szt__eaw, lbkx__fpl.target,
                        lbkx__fpl.loc)
            for hay__eumbs in lbkx__fpl.list_vars():
                if (hay__eumbs.name in anqf__bpkzi and hay__eumbs.name !=
                    qjy__sorn):
                    del anqf__bpkzi[hay__eumbs.name]
            new_body.append(lbkx__fpl)
        flkp__diq.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    vpxvq__imjyu = keyword_expr.items.copy()
    qomsc__ahga = keyword_expr.value_indexes
    for yfy__mozbk, vsbr__ajzbs in qomsc__ahga.items():
        vpxvq__imjyu[vsbr__ajzbs] = yfy__mozbk, vpxvq__imjyu[vsbr__ajzbs][1]
    new_body[buildmap_idx] = None
    return vpxvq__imjyu


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    zlm__qtv = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    vpxvq__imjyu = []
    qji__qowui = buildmap_idx + 1
    while qji__qowui <= search_end:
        jcpf__tgjup = body[qji__qowui]
        if not (isinstance(jcpf__tgjup, ir.Assign) and isinstance(
            jcpf__tgjup.value, ir.Const)):
            raise UnsupportedError(zlm__qtv)
        cwput__cxchj = jcpf__tgjup.target.name
        dvs__hvys = jcpf__tgjup.value.value
        qji__qowui += 1
        lzh__jkgoo = True
        while qji__qowui <= search_end and lzh__jkgoo:
            bvjy__qulh = body[qji__qowui]
            if (isinstance(bvjy__qulh, ir.Assign) and isinstance(bvjy__qulh
                .value, ir.Expr) and bvjy__qulh.value.op == 'getattr' and 
                bvjy__qulh.value.value.name == buildmap_name and bvjy__qulh
                .value.attr == '__setitem__'):
                lzh__jkgoo = False
            else:
                qji__qowui += 1
        if lzh__jkgoo or qji__qowui == search_end:
            raise UnsupportedError(zlm__qtv)
        tzplt__rbma = body[qji__qowui + 1]
        if not (isinstance(tzplt__rbma, ir.Assign) and isinstance(
            tzplt__rbma.value, ir.Expr) and tzplt__rbma.value.op == 'call' and
            tzplt__rbma.value.func.name == bvjy__qulh.target.name and len(
            tzplt__rbma.value.args) == 2 and tzplt__rbma.value.args[0].name ==
            cwput__cxchj):
            raise UnsupportedError(zlm__qtv)
        beoo__igxti = tzplt__rbma.value.args[1]
        vpxvq__imjyu.append((dvs__hvys, beoo__igxti))
        new_body[qji__qowui] = None
        new_body[qji__qowui + 1] = None
        qji__qowui += 2
    return vpxvq__imjyu


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    zlm__qtv = 'CALL_FUNCTION_EX with **kwargs not supported'
    qji__qowui = 0
    qxj__rbcdz = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        gyhso__kvrx = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        gyhso__kvrx = vararg_stmt.target.name
    sqs__uvgx = True
    while search_end >= qji__qowui and sqs__uvgx:
        acdoe__trphu = body[search_end]
        if (isinstance(acdoe__trphu, ir.Assign) and acdoe__trphu.target.
            name == gyhso__kvrx and isinstance(acdoe__trphu.value, ir.Expr) and
            acdoe__trphu.value.op == 'build_tuple' and not acdoe__trphu.
            value.items):
            sqs__uvgx = False
            new_body[search_end] = None
        else:
            if search_end == qji__qowui or not (isinstance(acdoe__trphu, ir
                .Assign) and acdoe__trphu.target.name == gyhso__kvrx and
                isinstance(acdoe__trphu.value, ir.Expr) and acdoe__trphu.
                value.op == 'binop' and acdoe__trphu.value.fn == operator.add):
                raise UnsupportedError(zlm__qtv)
            ismmz__bkxx = acdoe__trphu.value.lhs.name
            yabgc__yxcni = acdoe__trphu.value.rhs.name
            erxl__ovo = body[search_end - 1]
            if not (isinstance(erxl__ovo, ir.Assign) and isinstance(
                erxl__ovo.value, ir.Expr) and erxl__ovo.value.op ==
                'build_tuple' and len(erxl__ovo.value.items) == 1):
                raise UnsupportedError(zlm__qtv)
            if erxl__ovo.target.name == ismmz__bkxx:
                gyhso__kvrx = yabgc__yxcni
            elif erxl__ovo.target.name == yabgc__yxcni:
                gyhso__kvrx = ismmz__bkxx
            else:
                raise UnsupportedError(zlm__qtv)
            qxj__rbcdz.append(erxl__ovo.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            lwfu__tdt = True
            while search_end >= qji__qowui and lwfu__tdt:
                aei__njgbu = body[search_end]
                if isinstance(aei__njgbu, ir.Assign
                    ) and aei__njgbu.target.name == gyhso__kvrx:
                    lwfu__tdt = False
                else:
                    search_end -= 1
    if sqs__uvgx:
        raise UnsupportedError(zlm__qtv)
    return qxj__rbcdz[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    zlm__qtv = 'CALL_FUNCTION_EX with **kwargs not supported'
    for flkp__diq in func_ir.blocks.values():
        fzx__zwwul = False
        new_body = []
        for sfpg__dzdey, lbkx__fpl in enumerate(flkp__diq.body):
            if (isinstance(lbkx__fpl, ir.Assign) and isinstance(lbkx__fpl.
                value, ir.Expr) and lbkx__fpl.value.op == 'call' and 
                lbkx__fpl.value.varkwarg is not None):
                fzx__zwwul = True
                vkvwj__khvzl = lbkx__fpl.value
                args = vkvwj__khvzl.args
                vpxvq__imjyu = vkvwj__khvzl.kws
                zhes__glqv = vkvwj__khvzl.vararg
                zsr__ecyzt = vkvwj__khvzl.varkwarg
                wtdej__itis = sfpg__dzdey - 1
                chvmg__gcv = wtdej__itis
                ufasd__qrz = None
                zrgzl__djcd = True
                while chvmg__gcv >= 0 and zrgzl__djcd:
                    ufasd__qrz = flkp__diq.body[chvmg__gcv]
                    if isinstance(ufasd__qrz, ir.Assign
                        ) and ufasd__qrz.target.name == zsr__ecyzt.name:
                        zrgzl__djcd = False
                    else:
                        chvmg__gcv -= 1
                if vpxvq__imjyu or zrgzl__djcd or not (isinstance(
                    ufasd__qrz.value, ir.Expr) and ufasd__qrz.value.op ==
                    'build_map'):
                    raise UnsupportedError(zlm__qtv)
                if ufasd__qrz.value.items:
                    vpxvq__imjyu = _call_function_ex_replace_kws_small(
                        ufasd__qrz.value, new_body, chvmg__gcv)
                else:
                    vpxvq__imjyu = _call_function_ex_replace_kws_large(
                        flkp__diq.body, zsr__ecyzt.name, chvmg__gcv, 
                        sfpg__dzdey - 1, new_body)
                wtdej__itis = chvmg__gcv
                if zhes__glqv is not None:
                    if args:
                        raise UnsupportedError(zlm__qtv)
                    kpmb__sykmm = wtdej__itis
                    env__vwujf = None
                    zrgzl__djcd = True
                    while kpmb__sykmm >= 0 and zrgzl__djcd:
                        env__vwujf = flkp__diq.body[kpmb__sykmm]
                        if isinstance(env__vwujf, ir.Assign
                            ) and env__vwujf.target.name == zhes__glqv.name:
                            zrgzl__djcd = False
                        else:
                            kpmb__sykmm -= 1
                    if zrgzl__djcd:
                        raise UnsupportedError(zlm__qtv)
                    if isinstance(env__vwujf.value, ir.Expr
                        ) and env__vwujf.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(env__vwujf
                            .value, new_body, kpmb__sykmm)
                    else:
                        args = _call_function_ex_replace_args_large(env__vwujf,
                            flkp__diq.body, new_body, kpmb__sykmm)
                hgg__rqp = ir.Expr.call(vkvwj__khvzl.func, args,
                    vpxvq__imjyu, vkvwj__khvzl.loc, target=vkvwj__khvzl.target)
                if lbkx__fpl.target.name in func_ir._definitions and len(
                    func_ir._definitions[lbkx__fpl.target.name]) == 1:
                    func_ir._definitions[lbkx__fpl.target.name].clear()
                func_ir._definitions[lbkx__fpl.target.name].append(hgg__rqp)
                lbkx__fpl = ir.Assign(hgg__rqp, lbkx__fpl.target, lbkx__fpl.loc
                    )
            new_body.append(lbkx__fpl)
        if fzx__zwwul:
            flkp__diq.body = [xit__jri for xit__jri in new_body if xit__jri
                 is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for flkp__diq in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        fzx__zwwul = False
        for sfpg__dzdey, lbkx__fpl in enumerate(flkp__diq.body):
            yasgj__mlk = True
            kzut__lxp = None
            if isinstance(lbkx__fpl, ir.Assign) and isinstance(lbkx__fpl.
                value, ir.Expr):
                if lbkx__fpl.value.op == 'build_map':
                    kzut__lxp = lbkx__fpl.target.name
                    lit_old_idx[lbkx__fpl.target.name] = sfpg__dzdey
                    lit_new_idx[lbkx__fpl.target.name] = sfpg__dzdey
                    map_updates[lbkx__fpl.target.name
                        ] = lbkx__fpl.value.items.copy()
                    yasgj__mlk = False
                elif lbkx__fpl.value.op == 'call' and sfpg__dzdey > 0:
                    krvsm__hpw = lbkx__fpl.value.func.name
                    bvjy__qulh = flkp__diq.body[sfpg__dzdey - 1]
                    args = lbkx__fpl.value.args
                    if (isinstance(bvjy__qulh, ir.Assign) and bvjy__qulh.
                        target.name == krvsm__hpw and isinstance(bvjy__qulh
                        .value, ir.Expr) and bvjy__qulh.value.op ==
                        'getattr' and bvjy__qulh.value.value.name in
                        lit_old_idx):
                        zqvr__iafpi = bvjy__qulh.value.value.name
                        dnzdk__kcoo = bvjy__qulh.value.attr
                        if dnzdk__kcoo == '__setitem__':
                            yasgj__mlk = False
                            map_updates[zqvr__iafpi].append(args)
                            new_body[-1] = None
                        elif dnzdk__kcoo == 'update' and args[0
                            ].name in lit_old_idx:
                            yasgj__mlk = False
                            map_updates[zqvr__iafpi].extend(map_updates[
                                args[0].name])
                            new_body[-1] = None
                        if not yasgj__mlk:
                            lit_new_idx[zqvr__iafpi] = sfpg__dzdey
                            func_ir._definitions[bvjy__qulh.target.name
                                ].remove(bvjy__qulh.value)
            if not (isinstance(lbkx__fpl, ir.Assign) and isinstance(
                lbkx__fpl.value, ir.Expr) and lbkx__fpl.value.op ==
                'getattr' and lbkx__fpl.value.value.name in lit_old_idx and
                lbkx__fpl.value.attr in ('__setitem__', 'update')):
                for hay__eumbs in lbkx__fpl.list_vars():
                    if (hay__eumbs.name in lit_old_idx and hay__eumbs.name !=
                        kzut__lxp):
                        _insert_build_map(func_ir, hay__eumbs.name,
                            flkp__diq.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if yasgj__mlk:
                new_body.append(lbkx__fpl)
            else:
                func_ir._definitions[lbkx__fpl.target.name].remove(lbkx__fpl
                    .value)
                fzx__zwwul = True
                new_body.append(None)
        xrqx__bdjr = list(lit_old_idx.keys())
        for vkjf__qltr in xrqx__bdjr:
            _insert_build_map(func_ir, vkjf__qltr, flkp__diq.body, new_body,
                lit_old_idx, lit_new_idx, map_updates)
        if fzx__zwwul:
            flkp__diq.body = [xit__jri for xit__jri in new_body if xit__jri
                 is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    lkac__kko = lit_old_idx[name]
    kuxw__ohj = lit_new_idx[name]
    vuit__edkp = map_updates[name]
    new_body[kuxw__ohj] = _build_new_build_map(func_ir, name, old_body,
        lkac__kko, vuit__edkp)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    mzi__gqqeg = old_body[old_lineno]
    ddtzd__qgjq = mzi__gqqeg.target
    pepc__qorn = mzi__gqqeg.value
    aeec__qdw = []
    llnd__qmnsj = []
    for ucaz__jrgrm in new_items:
        ssnsf__fcgi, ftae__rru = ucaz__jrgrm
        mfomb__rkrr = guard(get_definition, func_ir, ssnsf__fcgi)
        if isinstance(mfomb__rkrr, (ir.Const, ir.Global, ir.FreeVar)):
            aeec__qdw.append(mfomb__rkrr.value)
        izzey__qjspd = guard(get_definition, func_ir, ftae__rru)
        if isinstance(izzey__qjspd, (ir.Const, ir.Global, ir.FreeVar)):
            llnd__qmnsj.append(izzey__qjspd.value)
        else:
            llnd__qmnsj.append(numba.core.interpreter._UNKNOWN_VALUE(
                ftae__rru.name))
    qomsc__ahga = {}
    if len(aeec__qdw) == len(new_items):
        vsnmt__ngkaw = {xit__jri: cifv__ztw for xit__jri, cifv__ztw in zip(
            aeec__qdw, llnd__qmnsj)}
        for sfpg__dzdey, ssnsf__fcgi in enumerate(aeec__qdw):
            qomsc__ahga[ssnsf__fcgi] = sfpg__dzdey
    else:
        vsnmt__ngkaw = None
    fgupj__ouyq = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=vsnmt__ngkaw, value_indexes=qomsc__ahga, loc=
        pepc__qorn.loc)
    func_ir._definitions[name].append(fgupj__ouyq)
    return ir.Assign(fgupj__ouyq, ir.Var(ddtzd__qgjq.scope, name,
        ddtzd__qgjq.loc), fgupj__ouyq.loc)
