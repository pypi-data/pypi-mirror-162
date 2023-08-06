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
    for vrbfn__uahp in func_ir.blocks.values():
        new_body = []
        brt__yrsei = {}
        for ljhi__kwwk, tqn__hoxcb in enumerate(vrbfn__uahp.body):
            sthoi__orpgn = None
            if isinstance(tqn__hoxcb, ir.Assign) and isinstance(tqn__hoxcb.
                value, ir.Expr):
                jby__uqupm = tqn__hoxcb.target.name
                if tqn__hoxcb.value.op == 'build_tuple':
                    sthoi__orpgn = jby__uqupm
                    brt__yrsei[jby__uqupm] = tqn__hoxcb.value.items
                elif tqn__hoxcb.value.op == 'binop' and tqn__hoxcb.value.fn == operator.add and tqn__hoxcb.value.lhs.name in brt__yrsei and tqn__hoxcb.value.rhs.name in brt__yrsei:
                    sthoi__orpgn = jby__uqupm
                    new_items = brt__yrsei[tqn__hoxcb.value.lhs.name
                        ] + brt__yrsei[tqn__hoxcb.value.rhs.name]
                    kqom__ego = ir.Expr.build_tuple(new_items, tqn__hoxcb.
                        value.loc)
                    brt__yrsei[jby__uqupm] = new_items
                    del brt__yrsei[tqn__hoxcb.value.lhs.name]
                    del brt__yrsei[tqn__hoxcb.value.rhs.name]
                    if tqn__hoxcb.value in func_ir._definitions[jby__uqupm]:
                        func_ir._definitions[jby__uqupm].remove(tqn__hoxcb.
                            value)
                    func_ir._definitions[jby__uqupm].append(kqom__ego)
                    tqn__hoxcb = ir.Assign(kqom__ego, tqn__hoxcb.target,
                        tqn__hoxcb.loc)
            for uon__xur in tqn__hoxcb.list_vars():
                if (uon__xur.name in brt__yrsei and uon__xur.name !=
                    sthoi__orpgn):
                    del brt__yrsei[uon__xur.name]
            new_body.append(tqn__hoxcb)
        vrbfn__uahp.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    gai__fwpkq = keyword_expr.items.copy()
    mlaqo__jbrwv = keyword_expr.value_indexes
    for dbok__uop, hta__nuu in mlaqo__jbrwv.items():
        gai__fwpkq[hta__nuu] = dbok__uop, gai__fwpkq[hta__nuu][1]
    new_body[buildmap_idx] = None
    return gai__fwpkq


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    jfp__fkk = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    gai__fwpkq = []
    tcy__vblrw = buildmap_idx + 1
    while tcy__vblrw <= search_end:
        cpmh__kjlv = body[tcy__vblrw]
        if not (isinstance(cpmh__kjlv, ir.Assign) and isinstance(cpmh__kjlv
            .value, ir.Const)):
            raise UnsupportedError(jfp__fkk)
        lhko__gbdxj = cpmh__kjlv.target.name
        ful__qqsvm = cpmh__kjlv.value.value
        tcy__vblrw += 1
        soq__axr = True
        while tcy__vblrw <= search_end and soq__axr:
            sjzv__yov = body[tcy__vblrw]
            if (isinstance(sjzv__yov, ir.Assign) and isinstance(sjzv__yov.
                value, ir.Expr) and sjzv__yov.value.op == 'getattr' and 
                sjzv__yov.value.value.name == buildmap_name and sjzv__yov.
                value.attr == '__setitem__'):
                soq__axr = False
            else:
                tcy__vblrw += 1
        if soq__axr or tcy__vblrw == search_end:
            raise UnsupportedError(jfp__fkk)
        hnt__jtg = body[tcy__vblrw + 1]
        if not (isinstance(hnt__jtg, ir.Assign) and isinstance(hnt__jtg.
            value, ir.Expr) and hnt__jtg.value.op == 'call' and hnt__jtg.
            value.func.name == sjzv__yov.target.name and len(hnt__jtg.value
            .args) == 2 and hnt__jtg.value.args[0].name == lhko__gbdxj):
            raise UnsupportedError(jfp__fkk)
        vay__fck = hnt__jtg.value.args[1]
        gai__fwpkq.append((ful__qqsvm, vay__fck))
        new_body[tcy__vblrw] = None
        new_body[tcy__vblrw + 1] = None
        tcy__vblrw += 2
    return gai__fwpkq


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    jfp__fkk = 'CALL_FUNCTION_EX with **kwargs not supported'
    tcy__vblrw = 0
    oab__rlsw = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        qntol__jmtv = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        qntol__jmtv = vararg_stmt.target.name
    zgo__xmt = True
    while search_end >= tcy__vblrw and zgo__xmt:
        xmj__esyr = body[search_end]
        if (isinstance(xmj__esyr, ir.Assign) and xmj__esyr.target.name ==
            qntol__jmtv and isinstance(xmj__esyr.value, ir.Expr) and 
            xmj__esyr.value.op == 'build_tuple' and not xmj__esyr.value.items):
            zgo__xmt = False
            new_body[search_end] = None
        else:
            if search_end == tcy__vblrw or not (isinstance(xmj__esyr, ir.
                Assign) and xmj__esyr.target.name == qntol__jmtv and
                isinstance(xmj__esyr.value, ir.Expr) and xmj__esyr.value.op ==
                'binop' and xmj__esyr.value.fn == operator.add):
                raise UnsupportedError(jfp__fkk)
            kqo__kgsqe = xmj__esyr.value.lhs.name
            hqj__toz = xmj__esyr.value.rhs.name
            bfzn__hzg = body[search_end - 1]
            if not (isinstance(bfzn__hzg, ir.Assign) and isinstance(
                bfzn__hzg.value, ir.Expr) and bfzn__hzg.value.op ==
                'build_tuple' and len(bfzn__hzg.value.items) == 1):
                raise UnsupportedError(jfp__fkk)
            if bfzn__hzg.target.name == kqo__kgsqe:
                qntol__jmtv = hqj__toz
            elif bfzn__hzg.target.name == hqj__toz:
                qntol__jmtv = kqo__kgsqe
            else:
                raise UnsupportedError(jfp__fkk)
            oab__rlsw.append(bfzn__hzg.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            vps__wwyy = True
            while search_end >= tcy__vblrw and vps__wwyy:
                ckq__gdpv = body[search_end]
                if isinstance(ckq__gdpv, ir.Assign
                    ) and ckq__gdpv.target.name == qntol__jmtv:
                    vps__wwyy = False
                else:
                    search_end -= 1
    if zgo__xmt:
        raise UnsupportedError(jfp__fkk)
    return oab__rlsw[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    jfp__fkk = 'CALL_FUNCTION_EX with **kwargs not supported'
    for vrbfn__uahp in func_ir.blocks.values():
        jfkyq__erbf = False
        new_body = []
        for ljhi__kwwk, tqn__hoxcb in enumerate(vrbfn__uahp.body):
            if (isinstance(tqn__hoxcb, ir.Assign) and isinstance(tqn__hoxcb
                .value, ir.Expr) and tqn__hoxcb.value.op == 'call' and 
                tqn__hoxcb.value.varkwarg is not None):
                jfkyq__erbf = True
                avrj__rjegt = tqn__hoxcb.value
                args = avrj__rjegt.args
                gai__fwpkq = avrj__rjegt.kws
                smcvl__fcmwi = avrj__rjegt.vararg
                bpqb__qzrfn = avrj__rjegt.varkwarg
                vgx__evyt = ljhi__kwwk - 1
                hynxi__fdjnw = vgx__evyt
                ryvy__aetin = None
                btmop__ximw = True
                while hynxi__fdjnw >= 0 and btmop__ximw:
                    ryvy__aetin = vrbfn__uahp.body[hynxi__fdjnw]
                    if isinstance(ryvy__aetin, ir.Assign
                        ) and ryvy__aetin.target.name == bpqb__qzrfn.name:
                        btmop__ximw = False
                    else:
                        hynxi__fdjnw -= 1
                if gai__fwpkq or btmop__ximw or not (isinstance(ryvy__aetin
                    .value, ir.Expr) and ryvy__aetin.value.op == 'build_map'):
                    raise UnsupportedError(jfp__fkk)
                if ryvy__aetin.value.items:
                    gai__fwpkq = _call_function_ex_replace_kws_small(
                        ryvy__aetin.value, new_body, hynxi__fdjnw)
                else:
                    gai__fwpkq = _call_function_ex_replace_kws_large(
                        vrbfn__uahp.body, bpqb__qzrfn.name, hynxi__fdjnw, 
                        ljhi__kwwk - 1, new_body)
                vgx__evyt = hynxi__fdjnw
                if smcvl__fcmwi is not None:
                    if args:
                        raise UnsupportedError(jfp__fkk)
                    ufx__way = vgx__evyt
                    ybkm__ezyv = None
                    btmop__ximw = True
                    while ufx__way >= 0 and btmop__ximw:
                        ybkm__ezyv = vrbfn__uahp.body[ufx__way]
                        if isinstance(ybkm__ezyv, ir.Assign
                            ) and ybkm__ezyv.target.name == smcvl__fcmwi.name:
                            btmop__ximw = False
                        else:
                            ufx__way -= 1
                    if btmop__ximw:
                        raise UnsupportedError(jfp__fkk)
                    if isinstance(ybkm__ezyv.value, ir.Expr
                        ) and ybkm__ezyv.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(ybkm__ezyv
                            .value, new_body, ufx__way)
                    else:
                        args = _call_function_ex_replace_args_large(ybkm__ezyv,
                            vrbfn__uahp.body, new_body, ufx__way)
                wwx__nsxis = ir.Expr.call(avrj__rjegt.func, args,
                    gai__fwpkq, avrj__rjegt.loc, target=avrj__rjegt.target)
                if tqn__hoxcb.target.name in func_ir._definitions and len(
                    func_ir._definitions[tqn__hoxcb.target.name]) == 1:
                    func_ir._definitions[tqn__hoxcb.target.name].clear()
                func_ir._definitions[tqn__hoxcb.target.name].append(wwx__nsxis)
                tqn__hoxcb = ir.Assign(wwx__nsxis, tqn__hoxcb.target,
                    tqn__hoxcb.loc)
            new_body.append(tqn__hoxcb)
        if jfkyq__erbf:
            vrbfn__uahp.body = [kfzpe__grhus for kfzpe__grhus in new_body if
                kfzpe__grhus is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for vrbfn__uahp in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        jfkyq__erbf = False
        for ljhi__kwwk, tqn__hoxcb in enumerate(vrbfn__uahp.body):
            cfj__skowx = True
            zjrrv__fmzx = None
            if isinstance(tqn__hoxcb, ir.Assign) and isinstance(tqn__hoxcb.
                value, ir.Expr):
                if tqn__hoxcb.value.op == 'build_map':
                    zjrrv__fmzx = tqn__hoxcb.target.name
                    lit_old_idx[tqn__hoxcb.target.name] = ljhi__kwwk
                    lit_new_idx[tqn__hoxcb.target.name] = ljhi__kwwk
                    map_updates[tqn__hoxcb.target.name
                        ] = tqn__hoxcb.value.items.copy()
                    cfj__skowx = False
                elif tqn__hoxcb.value.op == 'call' and ljhi__kwwk > 0:
                    nstwm__pnsg = tqn__hoxcb.value.func.name
                    sjzv__yov = vrbfn__uahp.body[ljhi__kwwk - 1]
                    args = tqn__hoxcb.value.args
                    if (isinstance(sjzv__yov, ir.Assign) and sjzv__yov.
                        target.name == nstwm__pnsg and isinstance(sjzv__yov
                        .value, ir.Expr) and sjzv__yov.value.op ==
                        'getattr' and sjzv__yov.value.value.name in lit_old_idx
                        ):
                        vowt__zrhf = sjzv__yov.value.value.name
                        vcnhc__ycvs = sjzv__yov.value.attr
                        if vcnhc__ycvs == '__setitem__':
                            cfj__skowx = False
                            map_updates[vowt__zrhf].append(args)
                            new_body[-1] = None
                        elif vcnhc__ycvs == 'update' and args[0
                            ].name in lit_old_idx:
                            cfj__skowx = False
                            map_updates[vowt__zrhf].extend(map_updates[args
                                [0].name])
                            new_body[-1] = None
                        if not cfj__skowx:
                            lit_new_idx[vowt__zrhf] = ljhi__kwwk
                            func_ir._definitions[sjzv__yov.target.name].remove(
                                sjzv__yov.value)
            if not (isinstance(tqn__hoxcb, ir.Assign) and isinstance(
                tqn__hoxcb.value, ir.Expr) and tqn__hoxcb.value.op ==
                'getattr' and tqn__hoxcb.value.value.name in lit_old_idx and
                tqn__hoxcb.value.attr in ('__setitem__', 'update')):
                for uon__xur in tqn__hoxcb.list_vars():
                    if (uon__xur.name in lit_old_idx and uon__xur.name !=
                        zjrrv__fmzx):
                        _insert_build_map(func_ir, uon__xur.name,
                            vrbfn__uahp.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if cfj__skowx:
                new_body.append(tqn__hoxcb)
            else:
                func_ir._definitions[tqn__hoxcb.target.name].remove(tqn__hoxcb
                    .value)
                jfkyq__erbf = True
                new_body.append(None)
        lxdj__bgook = list(lit_old_idx.keys())
        for zlar__sstrx in lxdj__bgook:
            _insert_build_map(func_ir, zlar__sstrx, vrbfn__uahp.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if jfkyq__erbf:
            vrbfn__uahp.body = [kfzpe__grhus for kfzpe__grhus in new_body if
                kfzpe__grhus is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    ugj__rui = lit_old_idx[name]
    aono__gpu = lit_new_idx[name]
    lrnvz__kuu = map_updates[name]
    new_body[aono__gpu] = _build_new_build_map(func_ir, name, old_body,
        ugj__rui, lrnvz__kuu)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    xgwh__zyqaq = old_body[old_lineno]
    raf__sphyq = xgwh__zyqaq.target
    zhrfr__maqvf = xgwh__zyqaq.value
    wrdd__yqgyr = []
    rhq__awr = []
    for hey__bfi in new_items:
        cotr__vbe, uul__umyde = hey__bfi
        wnbgt__otrn = guard(get_definition, func_ir, cotr__vbe)
        if isinstance(wnbgt__otrn, (ir.Const, ir.Global, ir.FreeVar)):
            wrdd__yqgyr.append(wnbgt__otrn.value)
        lapp__ehvav = guard(get_definition, func_ir, uul__umyde)
        if isinstance(lapp__ehvav, (ir.Const, ir.Global, ir.FreeVar)):
            rhq__awr.append(lapp__ehvav.value)
        else:
            rhq__awr.append(numba.core.interpreter._UNKNOWN_VALUE(
                uul__umyde.name))
    mlaqo__jbrwv = {}
    if len(wrdd__yqgyr) == len(new_items):
        mzvux__bdtod = {kfzpe__grhus: ajah__jsyjy for kfzpe__grhus,
            ajah__jsyjy in zip(wrdd__yqgyr, rhq__awr)}
        for ljhi__kwwk, cotr__vbe in enumerate(wrdd__yqgyr):
            mlaqo__jbrwv[cotr__vbe] = ljhi__kwwk
    else:
        mzvux__bdtod = None
    afnhw__hzq = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=mzvux__bdtod, value_indexes=mlaqo__jbrwv, loc=
        zhrfr__maqvf.loc)
    func_ir._definitions[name].append(afnhw__hzq)
    return ir.Assign(afnhw__hzq, ir.Var(raf__sphyq.scope, name, raf__sphyq.
        loc), afnhw__hzq.loc)
