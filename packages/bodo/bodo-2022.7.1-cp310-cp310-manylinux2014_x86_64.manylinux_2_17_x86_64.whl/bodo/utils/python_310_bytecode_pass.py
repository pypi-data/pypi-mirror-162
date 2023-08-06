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
    for qzqp__yjk in func_ir.blocks.values():
        new_body = []
        bkd__kozhm = {}
        for pex__lusfn, bae__ewdye in enumerate(qzqp__yjk.body):
            lzntg__pzju = None
            if isinstance(bae__ewdye, ir.Assign) and isinstance(bae__ewdye.
                value, ir.Expr):
                wrszw__yka = bae__ewdye.target.name
                if bae__ewdye.value.op == 'build_tuple':
                    lzntg__pzju = wrszw__yka
                    bkd__kozhm[wrszw__yka] = bae__ewdye.value.items
                elif bae__ewdye.value.op == 'binop' and bae__ewdye.value.fn == operator.add and bae__ewdye.value.lhs.name in bkd__kozhm and bae__ewdye.value.rhs.name in bkd__kozhm:
                    lzntg__pzju = wrszw__yka
                    new_items = bkd__kozhm[bae__ewdye.value.lhs.name
                        ] + bkd__kozhm[bae__ewdye.value.rhs.name]
                    hhwjo__crghw = ir.Expr.build_tuple(new_items,
                        bae__ewdye.value.loc)
                    bkd__kozhm[wrszw__yka] = new_items
                    del bkd__kozhm[bae__ewdye.value.lhs.name]
                    del bkd__kozhm[bae__ewdye.value.rhs.name]
                    if bae__ewdye.value in func_ir._definitions[wrszw__yka]:
                        func_ir._definitions[wrszw__yka].remove(bae__ewdye.
                            value)
                    func_ir._definitions[wrszw__yka].append(hhwjo__crghw)
                    bae__ewdye = ir.Assign(hhwjo__crghw, bae__ewdye.target,
                        bae__ewdye.loc)
            for tqj__dfro in bae__ewdye.list_vars():
                if (tqj__dfro.name in bkd__kozhm and tqj__dfro.name !=
                    lzntg__pzju):
                    del bkd__kozhm[tqj__dfro.name]
            new_body.append(bae__ewdye)
        qzqp__yjk.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    tezlw__nhp = keyword_expr.items.copy()
    bfqi__xkolm = keyword_expr.value_indexes
    for utry__reva, bwk__wrwt in bfqi__xkolm.items():
        tezlw__nhp[bwk__wrwt] = utry__reva, tezlw__nhp[bwk__wrwt][1]
    new_body[buildmap_idx] = None
    return tezlw__nhp


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    orrm__lhj = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    tezlw__nhp = []
    vqwlq__hcyl = buildmap_idx + 1
    while vqwlq__hcyl <= search_end:
        jdhsz__vdgr = body[vqwlq__hcyl]
        if not (isinstance(jdhsz__vdgr, ir.Assign) and isinstance(
            jdhsz__vdgr.value, ir.Const)):
            raise UnsupportedError(orrm__lhj)
        hikze__ukhvm = jdhsz__vdgr.target.name
        rswyg__opuez = jdhsz__vdgr.value.value
        vqwlq__hcyl += 1
        waq__zpkn = True
        while vqwlq__hcyl <= search_end and waq__zpkn:
            xpur__egpqq = body[vqwlq__hcyl]
            if (isinstance(xpur__egpqq, ir.Assign) and isinstance(
                xpur__egpqq.value, ir.Expr) and xpur__egpqq.value.op ==
                'getattr' and xpur__egpqq.value.value.name == buildmap_name and
                xpur__egpqq.value.attr == '__setitem__'):
                waq__zpkn = False
            else:
                vqwlq__hcyl += 1
        if waq__zpkn or vqwlq__hcyl == search_end:
            raise UnsupportedError(orrm__lhj)
        tgv__qxzdf = body[vqwlq__hcyl + 1]
        if not (isinstance(tgv__qxzdf, ir.Assign) and isinstance(tgv__qxzdf
            .value, ir.Expr) and tgv__qxzdf.value.op == 'call' and 
            tgv__qxzdf.value.func.name == xpur__egpqq.target.name and len(
            tgv__qxzdf.value.args) == 2 and tgv__qxzdf.value.args[0].name ==
            hikze__ukhvm):
            raise UnsupportedError(orrm__lhj)
        izmve__rik = tgv__qxzdf.value.args[1]
        tezlw__nhp.append((rswyg__opuez, izmve__rik))
        new_body[vqwlq__hcyl] = None
        new_body[vqwlq__hcyl + 1] = None
        vqwlq__hcyl += 2
    return tezlw__nhp


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    orrm__lhj = 'CALL_FUNCTION_EX with **kwargs not supported'
    vqwlq__hcyl = 0
    qia__xmba = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        vbl__bkx = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        vbl__bkx = vararg_stmt.target.name
    dbe__asjwy = True
    while search_end >= vqwlq__hcyl and dbe__asjwy:
        siglu__nhk = body[search_end]
        if (isinstance(siglu__nhk, ir.Assign) and siglu__nhk.target.name ==
            vbl__bkx and isinstance(siglu__nhk.value, ir.Expr) and 
            siglu__nhk.value.op == 'build_tuple' and not siglu__nhk.value.items
            ):
            dbe__asjwy = False
            new_body[search_end] = None
        else:
            if search_end == vqwlq__hcyl or not (isinstance(siglu__nhk, ir.
                Assign) and siglu__nhk.target.name == vbl__bkx and
                isinstance(siglu__nhk.value, ir.Expr) and siglu__nhk.value.
                op == 'binop' and siglu__nhk.value.fn == operator.add):
                raise UnsupportedError(orrm__lhj)
            hvlxn__xxdz = siglu__nhk.value.lhs.name
            yiomp__gaa = siglu__nhk.value.rhs.name
            kcsrv__uupy = body[search_end - 1]
            if not (isinstance(kcsrv__uupy, ir.Assign) and isinstance(
                kcsrv__uupy.value, ir.Expr) and kcsrv__uupy.value.op ==
                'build_tuple' and len(kcsrv__uupy.value.items) == 1):
                raise UnsupportedError(orrm__lhj)
            if kcsrv__uupy.target.name == hvlxn__xxdz:
                vbl__bkx = yiomp__gaa
            elif kcsrv__uupy.target.name == yiomp__gaa:
                vbl__bkx = hvlxn__xxdz
            else:
                raise UnsupportedError(orrm__lhj)
            qia__xmba.append(kcsrv__uupy.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            rrk__vaw = True
            while search_end >= vqwlq__hcyl and rrk__vaw:
                polgc__hjx = body[search_end]
                if isinstance(polgc__hjx, ir.Assign
                    ) and polgc__hjx.target.name == vbl__bkx:
                    rrk__vaw = False
                else:
                    search_end -= 1
    if dbe__asjwy:
        raise UnsupportedError(orrm__lhj)
    return qia__xmba[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    orrm__lhj = 'CALL_FUNCTION_EX with **kwargs not supported'
    for qzqp__yjk in func_ir.blocks.values():
        dwcg__rqfe = False
        new_body = []
        for pex__lusfn, bae__ewdye in enumerate(qzqp__yjk.body):
            if (isinstance(bae__ewdye, ir.Assign) and isinstance(bae__ewdye
                .value, ir.Expr) and bae__ewdye.value.op == 'call' and 
                bae__ewdye.value.varkwarg is not None):
                dwcg__rqfe = True
                ebt__xpxz = bae__ewdye.value
                args = ebt__xpxz.args
                tezlw__nhp = ebt__xpxz.kws
                iqf__bjaa = ebt__xpxz.vararg
                pugn__mxkyl = ebt__xpxz.varkwarg
                rul__dhmw = pex__lusfn - 1
                oeawn__fjvct = rul__dhmw
                ztdq__qghv = None
                gnx__kehly = True
                while oeawn__fjvct >= 0 and gnx__kehly:
                    ztdq__qghv = qzqp__yjk.body[oeawn__fjvct]
                    if isinstance(ztdq__qghv, ir.Assign
                        ) and ztdq__qghv.target.name == pugn__mxkyl.name:
                        gnx__kehly = False
                    else:
                        oeawn__fjvct -= 1
                if tezlw__nhp or gnx__kehly or not (isinstance(ztdq__qghv.
                    value, ir.Expr) and ztdq__qghv.value.op == 'build_map'):
                    raise UnsupportedError(orrm__lhj)
                if ztdq__qghv.value.items:
                    tezlw__nhp = _call_function_ex_replace_kws_small(ztdq__qghv
                        .value, new_body, oeawn__fjvct)
                else:
                    tezlw__nhp = _call_function_ex_replace_kws_large(qzqp__yjk
                        .body, pugn__mxkyl.name, oeawn__fjvct, pex__lusfn -
                        1, new_body)
                rul__dhmw = oeawn__fjvct
                if iqf__bjaa is not None:
                    if args:
                        raise UnsupportedError(orrm__lhj)
                    edyj__kgk = rul__dhmw
                    irdlk__epygo = None
                    gnx__kehly = True
                    while edyj__kgk >= 0 and gnx__kehly:
                        irdlk__epygo = qzqp__yjk.body[edyj__kgk]
                        if isinstance(irdlk__epygo, ir.Assign
                            ) and irdlk__epygo.target.name == iqf__bjaa.name:
                            gnx__kehly = False
                        else:
                            edyj__kgk -= 1
                    if gnx__kehly:
                        raise UnsupportedError(orrm__lhj)
                    if isinstance(irdlk__epygo.value, ir.Expr
                        ) and irdlk__epygo.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(
                            irdlk__epygo.value, new_body, edyj__kgk)
                    else:
                        args = _call_function_ex_replace_args_large(
                            irdlk__epygo, qzqp__yjk.body, new_body, edyj__kgk)
                bbweh__ngykq = ir.Expr.call(ebt__xpxz.func, args,
                    tezlw__nhp, ebt__xpxz.loc, target=ebt__xpxz.target)
                if bae__ewdye.target.name in func_ir._definitions and len(
                    func_ir._definitions[bae__ewdye.target.name]) == 1:
                    func_ir._definitions[bae__ewdye.target.name].clear()
                func_ir._definitions[bae__ewdye.target.name].append(
                    bbweh__ngykq)
                bae__ewdye = ir.Assign(bbweh__ngykq, bae__ewdye.target,
                    bae__ewdye.loc)
            new_body.append(bae__ewdye)
        if dwcg__rqfe:
            qzqp__yjk.body = [vqqo__pmmfa for vqqo__pmmfa in new_body if 
                vqqo__pmmfa is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for qzqp__yjk in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        dwcg__rqfe = False
        for pex__lusfn, bae__ewdye in enumerate(qzqp__yjk.body):
            jtiwh__uiu = True
            oxa__siv = None
            if isinstance(bae__ewdye, ir.Assign) and isinstance(bae__ewdye.
                value, ir.Expr):
                if bae__ewdye.value.op == 'build_map':
                    oxa__siv = bae__ewdye.target.name
                    lit_old_idx[bae__ewdye.target.name] = pex__lusfn
                    lit_new_idx[bae__ewdye.target.name] = pex__lusfn
                    map_updates[bae__ewdye.target.name
                        ] = bae__ewdye.value.items.copy()
                    jtiwh__uiu = False
                elif bae__ewdye.value.op == 'call' and pex__lusfn > 0:
                    xsy__rgo = bae__ewdye.value.func.name
                    xpur__egpqq = qzqp__yjk.body[pex__lusfn - 1]
                    args = bae__ewdye.value.args
                    if (isinstance(xpur__egpqq, ir.Assign) and xpur__egpqq.
                        target.name == xsy__rgo and isinstance(xpur__egpqq.
                        value, ir.Expr) and xpur__egpqq.value.op ==
                        'getattr' and xpur__egpqq.value.value.name in
                        lit_old_idx):
                        flrsd__jofyl = xpur__egpqq.value.value.name
                        gxiad__pngyk = xpur__egpqq.value.attr
                        if gxiad__pngyk == '__setitem__':
                            jtiwh__uiu = False
                            map_updates[flrsd__jofyl].append(args)
                            new_body[-1] = None
                        elif gxiad__pngyk == 'update' and args[0
                            ].name in lit_old_idx:
                            jtiwh__uiu = False
                            map_updates[flrsd__jofyl].extend(map_updates[
                                args[0].name])
                            new_body[-1] = None
                        if not jtiwh__uiu:
                            lit_new_idx[flrsd__jofyl] = pex__lusfn
                            func_ir._definitions[xpur__egpqq.target.name
                                ].remove(xpur__egpqq.value)
            if not (isinstance(bae__ewdye, ir.Assign) and isinstance(
                bae__ewdye.value, ir.Expr) and bae__ewdye.value.op ==
                'getattr' and bae__ewdye.value.value.name in lit_old_idx and
                bae__ewdye.value.attr in ('__setitem__', 'update')):
                for tqj__dfro in bae__ewdye.list_vars():
                    if (tqj__dfro.name in lit_old_idx and tqj__dfro.name !=
                        oxa__siv):
                        _insert_build_map(func_ir, tqj__dfro.name,
                            qzqp__yjk.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if jtiwh__uiu:
                new_body.append(bae__ewdye)
            else:
                func_ir._definitions[bae__ewdye.target.name].remove(bae__ewdye
                    .value)
                dwcg__rqfe = True
                new_body.append(None)
        poohq__qww = list(lit_old_idx.keys())
        for yhv__qli in poohq__qww:
            _insert_build_map(func_ir, yhv__qli, qzqp__yjk.body, new_body,
                lit_old_idx, lit_new_idx, map_updates)
        if dwcg__rqfe:
            qzqp__yjk.body = [vqqo__pmmfa for vqqo__pmmfa in new_body if 
                vqqo__pmmfa is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    boj__lupby = lit_old_idx[name]
    tmy__ipw = lit_new_idx[name]
    idmvy__orweb = map_updates[name]
    new_body[tmy__ipw] = _build_new_build_map(func_ir, name, old_body,
        boj__lupby, idmvy__orweb)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    drdx__lxih = old_body[old_lineno]
    buau__rmln = drdx__lxih.target
    vhuq__bcduc = drdx__lxih.value
    gtfa__kvk = []
    jzjoa__jvvo = []
    for twicp__qwbbb in new_items:
        kywt__iqq, flqgn__ygsu = twicp__qwbbb
        idve__cwtq = guard(get_definition, func_ir, kywt__iqq)
        if isinstance(idve__cwtq, (ir.Const, ir.Global, ir.FreeVar)):
            gtfa__kvk.append(idve__cwtq.value)
        nyde__bji = guard(get_definition, func_ir, flqgn__ygsu)
        if isinstance(nyde__bji, (ir.Const, ir.Global, ir.FreeVar)):
            jzjoa__jvvo.append(nyde__bji.value)
        else:
            jzjoa__jvvo.append(numba.core.interpreter._UNKNOWN_VALUE(
                flqgn__ygsu.name))
    bfqi__xkolm = {}
    if len(gtfa__kvk) == len(new_items):
        vav__vday = {vqqo__pmmfa: lgq__gxz for vqqo__pmmfa, lgq__gxz in zip
            (gtfa__kvk, jzjoa__jvvo)}
        for pex__lusfn, kywt__iqq in enumerate(gtfa__kvk):
            bfqi__xkolm[kywt__iqq] = pex__lusfn
    else:
        vav__vday = None
    kcxx__bpbe = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=vav__vday, value_indexes=bfqi__xkolm, loc=vhuq__bcduc.loc
        )
    func_ir._definitions[name].append(kcxx__bpbe)
    return ir.Assign(kcxx__bpbe, ir.Var(buau__rmln.scope, name, buau__rmln.
        loc), kcxx__bpbe.loc)
