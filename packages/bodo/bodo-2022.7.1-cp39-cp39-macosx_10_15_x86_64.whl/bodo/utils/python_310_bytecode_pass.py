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
    for xmd__odq in func_ir.blocks.values():
        new_body = []
        cehn__ymwjj = {}
        for fxro__qwfx, cstyp__iwja in enumerate(xmd__odq.body):
            gpdri__rzyur = None
            if isinstance(cstyp__iwja, ir.Assign) and isinstance(cstyp__iwja
                .value, ir.Expr):
                hwvmt__comdn = cstyp__iwja.target.name
                if cstyp__iwja.value.op == 'build_tuple':
                    gpdri__rzyur = hwvmt__comdn
                    cehn__ymwjj[hwvmt__comdn] = cstyp__iwja.value.items
                elif cstyp__iwja.value.op == 'binop' and cstyp__iwja.value.fn == operator.add and cstyp__iwja.value.lhs.name in cehn__ymwjj and cstyp__iwja.value.rhs.name in cehn__ymwjj:
                    gpdri__rzyur = hwvmt__comdn
                    new_items = cehn__ymwjj[cstyp__iwja.value.lhs.name
                        ] + cehn__ymwjj[cstyp__iwja.value.rhs.name]
                    vpcr__hkg = ir.Expr.build_tuple(new_items, cstyp__iwja.
                        value.loc)
                    cehn__ymwjj[hwvmt__comdn] = new_items
                    del cehn__ymwjj[cstyp__iwja.value.lhs.name]
                    del cehn__ymwjj[cstyp__iwja.value.rhs.name]
                    if cstyp__iwja.value in func_ir._definitions[hwvmt__comdn]:
                        func_ir._definitions[hwvmt__comdn].remove(cstyp__iwja
                            .value)
                    func_ir._definitions[hwvmt__comdn].append(vpcr__hkg)
                    cstyp__iwja = ir.Assign(vpcr__hkg, cstyp__iwja.target,
                        cstyp__iwja.loc)
            for gzf__imcl in cstyp__iwja.list_vars():
                if (gzf__imcl.name in cehn__ymwjj and gzf__imcl.name !=
                    gpdri__rzyur):
                    del cehn__ymwjj[gzf__imcl.name]
            new_body.append(cstyp__iwja)
        xmd__odq.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    qwey__aioy = keyword_expr.items.copy()
    okdv__zlt = keyword_expr.value_indexes
    for cjzp__fxs, bmkw__qfzyg in okdv__zlt.items():
        qwey__aioy[bmkw__qfzyg] = cjzp__fxs, qwey__aioy[bmkw__qfzyg][1]
    new_body[buildmap_idx] = None
    return qwey__aioy


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    lpa__mtmnc = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    qwey__aioy = []
    vlu__tbl = buildmap_idx + 1
    while vlu__tbl <= search_end:
        oosov__mzkag = body[vlu__tbl]
        if not (isinstance(oosov__mzkag, ir.Assign) and isinstance(
            oosov__mzkag.value, ir.Const)):
            raise UnsupportedError(lpa__mtmnc)
        xnyl__bdex = oosov__mzkag.target.name
        rug__zgeb = oosov__mzkag.value.value
        vlu__tbl += 1
        boiqk__kdbn = True
        while vlu__tbl <= search_end and boiqk__kdbn:
            tohf__sqd = body[vlu__tbl]
            if (isinstance(tohf__sqd, ir.Assign) and isinstance(tohf__sqd.
                value, ir.Expr) and tohf__sqd.value.op == 'getattr' and 
                tohf__sqd.value.value.name == buildmap_name and tohf__sqd.
                value.attr == '__setitem__'):
                boiqk__kdbn = False
            else:
                vlu__tbl += 1
        if boiqk__kdbn or vlu__tbl == search_end:
            raise UnsupportedError(lpa__mtmnc)
        zucc__tping = body[vlu__tbl + 1]
        if not (isinstance(zucc__tping, ir.Assign) and isinstance(
            zucc__tping.value, ir.Expr) and zucc__tping.value.op == 'call' and
            zucc__tping.value.func.name == tohf__sqd.target.name and len(
            zucc__tping.value.args) == 2 and zucc__tping.value.args[0].name ==
            xnyl__bdex):
            raise UnsupportedError(lpa__mtmnc)
        jgjle__ninkb = zucc__tping.value.args[1]
        qwey__aioy.append((rug__zgeb, jgjle__ninkb))
        new_body[vlu__tbl] = None
        new_body[vlu__tbl + 1] = None
        vlu__tbl += 2
    return qwey__aioy


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    lpa__mtmnc = 'CALL_FUNCTION_EX with **kwargs not supported'
    vlu__tbl = 0
    kcngi__vgdnr = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        lbpw__jpnj = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        lbpw__jpnj = vararg_stmt.target.name
    ssw__zscu = True
    while search_end >= vlu__tbl and ssw__zscu:
        bqv__qqciu = body[search_end]
        if (isinstance(bqv__qqciu, ir.Assign) and bqv__qqciu.target.name ==
            lbpw__jpnj and isinstance(bqv__qqciu.value, ir.Expr) and 
            bqv__qqciu.value.op == 'build_tuple' and not bqv__qqciu.value.items
            ):
            ssw__zscu = False
            new_body[search_end] = None
        else:
            if search_end == vlu__tbl or not (isinstance(bqv__qqciu, ir.
                Assign) and bqv__qqciu.target.name == lbpw__jpnj and
                isinstance(bqv__qqciu.value, ir.Expr) and bqv__qqciu.value.
                op == 'binop' and bqv__qqciu.value.fn == operator.add):
                raise UnsupportedError(lpa__mtmnc)
            vtw__nqwka = bqv__qqciu.value.lhs.name
            lbmm__stsso = bqv__qqciu.value.rhs.name
            glf__atq = body[search_end - 1]
            if not (isinstance(glf__atq, ir.Assign) and isinstance(glf__atq
                .value, ir.Expr) and glf__atq.value.op == 'build_tuple' and
                len(glf__atq.value.items) == 1):
                raise UnsupportedError(lpa__mtmnc)
            if glf__atq.target.name == vtw__nqwka:
                lbpw__jpnj = lbmm__stsso
            elif glf__atq.target.name == lbmm__stsso:
                lbpw__jpnj = vtw__nqwka
            else:
                raise UnsupportedError(lpa__mtmnc)
            kcngi__vgdnr.append(glf__atq.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            ipmp__rqxe = True
            while search_end >= vlu__tbl and ipmp__rqxe:
                bfrte__wfiai = body[search_end]
                if isinstance(bfrte__wfiai, ir.Assign
                    ) and bfrte__wfiai.target.name == lbpw__jpnj:
                    ipmp__rqxe = False
                else:
                    search_end -= 1
    if ssw__zscu:
        raise UnsupportedError(lpa__mtmnc)
    return kcngi__vgdnr[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    lpa__mtmnc = 'CALL_FUNCTION_EX with **kwargs not supported'
    for xmd__odq in func_ir.blocks.values():
        htrqn__upmqa = False
        new_body = []
        for fxro__qwfx, cstyp__iwja in enumerate(xmd__odq.body):
            if (isinstance(cstyp__iwja, ir.Assign) and isinstance(
                cstyp__iwja.value, ir.Expr) and cstyp__iwja.value.op ==
                'call' and cstyp__iwja.value.varkwarg is not None):
                htrqn__upmqa = True
                fsisn__elkuy = cstyp__iwja.value
                args = fsisn__elkuy.args
                qwey__aioy = fsisn__elkuy.kws
                aal__fdkh = fsisn__elkuy.vararg
                qbh__pzp = fsisn__elkuy.varkwarg
                jys__xibm = fxro__qwfx - 1
                sxmp__qfeik = jys__xibm
                deoe__whv = None
                khmrq__wzqvj = True
                while sxmp__qfeik >= 0 and khmrq__wzqvj:
                    deoe__whv = xmd__odq.body[sxmp__qfeik]
                    if isinstance(deoe__whv, ir.Assign
                        ) and deoe__whv.target.name == qbh__pzp.name:
                        khmrq__wzqvj = False
                    else:
                        sxmp__qfeik -= 1
                if qwey__aioy or khmrq__wzqvj or not (isinstance(deoe__whv.
                    value, ir.Expr) and deoe__whv.value.op == 'build_map'):
                    raise UnsupportedError(lpa__mtmnc)
                if deoe__whv.value.items:
                    qwey__aioy = _call_function_ex_replace_kws_small(deoe__whv
                        .value, new_body, sxmp__qfeik)
                else:
                    qwey__aioy = _call_function_ex_replace_kws_large(xmd__odq
                        .body, qbh__pzp.name, sxmp__qfeik, fxro__qwfx - 1,
                        new_body)
                jys__xibm = sxmp__qfeik
                if aal__fdkh is not None:
                    if args:
                        raise UnsupportedError(lpa__mtmnc)
                    iky__kyzi = jys__xibm
                    fjy__bvqnj = None
                    khmrq__wzqvj = True
                    while iky__kyzi >= 0 and khmrq__wzqvj:
                        fjy__bvqnj = xmd__odq.body[iky__kyzi]
                        if isinstance(fjy__bvqnj, ir.Assign
                            ) and fjy__bvqnj.target.name == aal__fdkh.name:
                            khmrq__wzqvj = False
                        else:
                            iky__kyzi -= 1
                    if khmrq__wzqvj:
                        raise UnsupportedError(lpa__mtmnc)
                    if isinstance(fjy__bvqnj.value, ir.Expr
                        ) and fjy__bvqnj.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(fjy__bvqnj
                            .value, new_body, iky__kyzi)
                    else:
                        args = _call_function_ex_replace_args_large(fjy__bvqnj,
                            xmd__odq.body, new_body, iky__kyzi)
                rhsxa__snop = ir.Expr.call(fsisn__elkuy.func, args,
                    qwey__aioy, fsisn__elkuy.loc, target=fsisn__elkuy.target)
                if cstyp__iwja.target.name in func_ir._definitions and len(
                    func_ir._definitions[cstyp__iwja.target.name]) == 1:
                    func_ir._definitions[cstyp__iwja.target.name].clear()
                func_ir._definitions[cstyp__iwja.target.name].append(
                    rhsxa__snop)
                cstyp__iwja = ir.Assign(rhsxa__snop, cstyp__iwja.target,
                    cstyp__iwja.loc)
            new_body.append(cstyp__iwja)
        if htrqn__upmqa:
            xmd__odq.body = [plrm__dat for plrm__dat in new_body if 
                plrm__dat is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for xmd__odq in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        htrqn__upmqa = False
        for fxro__qwfx, cstyp__iwja in enumerate(xmd__odq.body):
            sqgm__rikio = True
            mpt__faybi = None
            if isinstance(cstyp__iwja, ir.Assign) and isinstance(cstyp__iwja
                .value, ir.Expr):
                if cstyp__iwja.value.op == 'build_map':
                    mpt__faybi = cstyp__iwja.target.name
                    lit_old_idx[cstyp__iwja.target.name] = fxro__qwfx
                    lit_new_idx[cstyp__iwja.target.name] = fxro__qwfx
                    map_updates[cstyp__iwja.target.name
                        ] = cstyp__iwja.value.items.copy()
                    sqgm__rikio = False
                elif cstyp__iwja.value.op == 'call' and fxro__qwfx > 0:
                    eljka__ntu = cstyp__iwja.value.func.name
                    tohf__sqd = xmd__odq.body[fxro__qwfx - 1]
                    args = cstyp__iwja.value.args
                    if (isinstance(tohf__sqd, ir.Assign) and tohf__sqd.
                        target.name == eljka__ntu and isinstance(tohf__sqd.
                        value, ir.Expr) and tohf__sqd.value.op == 'getattr' and
                        tohf__sqd.value.value.name in lit_old_idx):
                        vvk__yvxzb = tohf__sqd.value.value.name
                        fot__qcv = tohf__sqd.value.attr
                        if fot__qcv == '__setitem__':
                            sqgm__rikio = False
                            map_updates[vvk__yvxzb].append(args)
                            new_body[-1] = None
                        elif fot__qcv == 'update' and args[0
                            ].name in lit_old_idx:
                            sqgm__rikio = False
                            map_updates[vvk__yvxzb].extend(map_updates[args
                                [0].name])
                            new_body[-1] = None
                        if not sqgm__rikio:
                            lit_new_idx[vvk__yvxzb] = fxro__qwfx
                            func_ir._definitions[tohf__sqd.target.name].remove(
                                tohf__sqd.value)
            if not (isinstance(cstyp__iwja, ir.Assign) and isinstance(
                cstyp__iwja.value, ir.Expr) and cstyp__iwja.value.op ==
                'getattr' and cstyp__iwja.value.value.name in lit_old_idx and
                cstyp__iwja.value.attr in ('__setitem__', 'update')):
                for gzf__imcl in cstyp__iwja.list_vars():
                    if (gzf__imcl.name in lit_old_idx and gzf__imcl.name !=
                        mpt__faybi):
                        _insert_build_map(func_ir, gzf__imcl.name, xmd__odq
                            .body, new_body, lit_old_idx, lit_new_idx,
                            map_updates)
            if sqgm__rikio:
                new_body.append(cstyp__iwja)
            else:
                func_ir._definitions[cstyp__iwja.target.name].remove(
                    cstyp__iwja.value)
                htrqn__upmqa = True
                new_body.append(None)
        eht__fjeax = list(lit_old_idx.keys())
        for gjbs__tkww in eht__fjeax:
            _insert_build_map(func_ir, gjbs__tkww, xmd__odq.body, new_body,
                lit_old_idx, lit_new_idx, map_updates)
        if htrqn__upmqa:
            xmd__odq.body = [plrm__dat for plrm__dat in new_body if 
                plrm__dat is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    oad__bdx = lit_old_idx[name]
    hxt__ozeww = lit_new_idx[name]
    xsihj__rhp = map_updates[name]
    new_body[hxt__ozeww] = _build_new_build_map(func_ir, name, old_body,
        oad__bdx, xsihj__rhp)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    skvio__wbqzf = old_body[old_lineno]
    neh__lvdq = skvio__wbqzf.target
    kds__ziajl = skvio__wbqzf.value
    cccrh__klkf = []
    ajr__rfc = []
    for dhwxb__jvt in new_items:
        fqbia__tigxy, bmfh__ayxa = dhwxb__jvt
        hzf__jenjk = guard(get_definition, func_ir, fqbia__tigxy)
        if isinstance(hzf__jenjk, (ir.Const, ir.Global, ir.FreeVar)):
            cccrh__klkf.append(hzf__jenjk.value)
        ustlh__xigj = guard(get_definition, func_ir, bmfh__ayxa)
        if isinstance(ustlh__xigj, (ir.Const, ir.Global, ir.FreeVar)):
            ajr__rfc.append(ustlh__xigj.value)
        else:
            ajr__rfc.append(numba.core.interpreter._UNKNOWN_VALUE(
                bmfh__ayxa.name))
    okdv__zlt = {}
    if len(cccrh__klkf) == len(new_items):
        zcoaf__cxzi = {plrm__dat: ciyc__xlal for plrm__dat, ciyc__xlal in
            zip(cccrh__klkf, ajr__rfc)}
        for fxro__qwfx, fqbia__tigxy in enumerate(cccrh__klkf):
            okdv__zlt[fqbia__tigxy] = fxro__qwfx
    else:
        zcoaf__cxzi = None
    ofxk__zet = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=zcoaf__cxzi, value_indexes=okdv__zlt, loc=kds__ziajl.loc)
    func_ir._definitions[name].append(ofxk__zet)
    return ir.Assign(ofxk__zet, ir.Var(neh__lvdq.scope, name, neh__lvdq.loc
        ), ofxk__zet.loc)
