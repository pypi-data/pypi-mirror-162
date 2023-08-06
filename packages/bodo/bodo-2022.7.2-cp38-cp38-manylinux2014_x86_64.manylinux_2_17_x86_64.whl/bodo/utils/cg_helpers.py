"""helper functions for code generation with llvmlite
"""
import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
import bodo
from bodo.libs import array_ext, hdist
ll.add_symbol('array_getitem', array_ext.array_getitem)
ll.add_symbol('seq_getitem', array_ext.seq_getitem)
ll.add_symbol('list_check', array_ext.list_check)
ll.add_symbol('dict_keys', array_ext.dict_keys)
ll.add_symbol('dict_values', array_ext.dict_values)
ll.add_symbol('dict_merge_from_seq2', array_ext.dict_merge_from_seq2)
ll.add_symbol('is_na_value', array_ext.is_na_value)


def set_bitmap_bit(builder, null_bitmap_ptr, ind, val):
    ean__ygi = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    jzoqq__szd = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    rjp__bgb = builder.gep(null_bitmap_ptr, [ean__ygi], inbounds=True)
    rsapl__kqgw = builder.load(rjp__bgb)
    uksyf__nle = lir.ArrayType(lir.IntType(8), 8)
    uum__janes = cgutils.alloca_once_value(builder, lir.Constant(uksyf__nle,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    fhrx__xyn = builder.load(builder.gep(uum__janes, [lir.Constant(lir.
        IntType(64), 0), jzoqq__szd], inbounds=True))
    if val:
        builder.store(builder.or_(rsapl__kqgw, fhrx__xyn), rjp__bgb)
    else:
        fhrx__xyn = builder.xor(fhrx__xyn, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(rsapl__kqgw, fhrx__xyn), rjp__bgb)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    ean__ygi = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    jzoqq__szd = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    rsapl__kqgw = builder.load(builder.gep(null_bitmap_ptr, [ean__ygi],
        inbounds=True))
    uksyf__nle = lir.ArrayType(lir.IntType(8), 8)
    uum__janes = cgutils.alloca_once_value(builder, lir.Constant(uksyf__nle,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    fhrx__xyn = builder.load(builder.gep(uum__janes, [lir.Constant(lir.
        IntType(64), 0), jzoqq__szd], inbounds=True))
    return builder.and_(rsapl__kqgw, fhrx__xyn)


def pyarray_check(builder, context, obj):
    latu__vjwl = context.get_argument_type(types.pyobject)
    nbgyd__gkijf = lir.FunctionType(lir.IntType(32), [latu__vjwl])
    ikulw__osse = cgutils.get_or_insert_function(builder.module,
        nbgyd__gkijf, name='is_np_array')
    return builder.call(ikulw__osse, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    latu__vjwl = context.get_argument_type(types.pyobject)
    wizk__qzi = context.get_value_type(types.intp)
    sqj__faa = lir.FunctionType(lir.IntType(8).as_pointer(), [latu__vjwl,
        wizk__qzi])
    ycu__dgwsd = cgutils.get_or_insert_function(builder.module, sqj__faa,
        name='array_getptr1')
    bvjw__ayos = lir.FunctionType(latu__vjwl, [latu__vjwl, lir.IntType(8).
        as_pointer()])
    vef__qxxap = cgutils.get_or_insert_function(builder.module, bvjw__ayos,
        name='array_getitem')
    bew__etj = builder.call(ycu__dgwsd, [arr_obj, ind])
    return builder.call(vef__qxxap, [arr_obj, bew__etj])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    latu__vjwl = context.get_argument_type(types.pyobject)
    wizk__qzi = context.get_value_type(types.intp)
    sqj__faa = lir.FunctionType(lir.IntType(8).as_pointer(), [latu__vjwl,
        wizk__qzi])
    ycu__dgwsd = cgutils.get_or_insert_function(builder.module, sqj__faa,
        name='array_getptr1')
    erfr__vli = lir.FunctionType(lir.VoidType(), [latu__vjwl, lir.IntType(8
        ).as_pointer(), latu__vjwl])
    ksk__sfcx = cgutils.get_or_insert_function(builder.module, erfr__vli,
        name='array_setitem')
    bew__etj = builder.call(ycu__dgwsd, [arr_obj, ind])
    builder.call(ksk__sfcx, [arr_obj, bew__etj, val_obj])


def seq_getitem(builder, context, obj, ind):
    latu__vjwl = context.get_argument_type(types.pyobject)
    wizk__qzi = context.get_value_type(types.intp)
    psg__eecu = lir.FunctionType(latu__vjwl, [latu__vjwl, wizk__qzi])
    mor__jvp = cgutils.get_or_insert_function(builder.module, psg__eecu,
        name='seq_getitem')
    return builder.call(mor__jvp, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    latu__vjwl = context.get_argument_type(types.pyobject)
    adj__ciiq = lir.FunctionType(lir.IntType(32), [latu__vjwl, latu__vjwl])
    xczv__kxuj = cgutils.get_or_insert_function(builder.module, adj__ciiq,
        name='is_na_value')
    return builder.call(xczv__kxuj, [val, C_NA])


def list_check(builder, context, obj):
    latu__vjwl = context.get_argument_type(types.pyobject)
    xawc__xikf = context.get_value_type(types.int32)
    etey__ttt = lir.FunctionType(xawc__xikf, [latu__vjwl])
    ija__rtui = cgutils.get_or_insert_function(builder.module, etey__ttt,
        name='list_check')
    return builder.call(ija__rtui, [obj])


def dict_keys(builder, context, obj):
    latu__vjwl = context.get_argument_type(types.pyobject)
    etey__ttt = lir.FunctionType(latu__vjwl, [latu__vjwl])
    ija__rtui = cgutils.get_or_insert_function(builder.module, etey__ttt,
        name='dict_keys')
    return builder.call(ija__rtui, [obj])


def dict_values(builder, context, obj):
    latu__vjwl = context.get_argument_type(types.pyobject)
    etey__ttt = lir.FunctionType(latu__vjwl, [latu__vjwl])
    ija__rtui = cgutils.get_or_insert_function(builder.module, etey__ttt,
        name='dict_values')
    return builder.call(ija__rtui, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    latu__vjwl = context.get_argument_type(types.pyobject)
    etey__ttt = lir.FunctionType(lir.VoidType(), [latu__vjwl, latu__vjwl])
    ija__rtui = cgutils.get_or_insert_function(builder.module, etey__ttt,
        name='dict_merge_from_seq2')
    builder.call(ija__rtui, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    xahq__cxo = cgutils.alloca_once_value(builder, val)
    ztx__kpejf = list_check(builder, context, val)
    vnibt__czrq = builder.icmp_unsigned('!=', ztx__kpejf, lir.Constant(
        ztx__kpejf.type, 0))
    with builder.if_then(vnibt__czrq):
        uvvxc__idu = context.insert_const_string(builder.module, 'numpy')
        lwltv__cfz = c.pyapi.import_module_noblock(uvvxc__idu)
        esjib__ifew = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            esjib__ifew = str(typ.dtype)
        hqkl__sbz = c.pyapi.object_getattr_string(lwltv__cfz, esjib__ifew)
        fzxv__frmjr = builder.load(xahq__cxo)
        zdv__imfam = c.pyapi.call_method(lwltv__cfz, 'asarray', (
            fzxv__frmjr, hqkl__sbz))
        builder.store(zdv__imfam, xahq__cxo)
        c.pyapi.decref(lwltv__cfz)
        c.pyapi.decref(hqkl__sbz)
    val = builder.load(xahq__cxo)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        hhzwt__cyl = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        vgg__gqy, xhj__frg = c.pyapi.call_jit_code(lambda a: get_utf8_size(
            a), types.int64(bodo.string_type), [hhzwt__cyl])
        context.nrt.decref(builder, typ, hhzwt__cyl)
        return cgutils.pack_array(builder, [xhj__frg])
    if isinstance(typ, (StructType, types.BaseTuple)):
        uvvxc__idu = context.insert_const_string(builder.module, 'pandas')
        omhs__kmcc = c.pyapi.import_module_noblock(uvvxc__idu)
        C_NA = c.pyapi.object_getattr_string(omhs__kmcc, 'NA')
        wdorf__jwd = bodo.utils.transform.get_type_alloc_counts(typ)
        hgutd__hgaw = context.make_tuple(builder, types.Tuple(wdorf__jwd *
            [types.int64]), wdorf__jwd * [context.get_constant(types.int64, 0)]
            )
        fwvp__jgp = cgutils.alloca_once_value(builder, hgutd__hgaw)
        lyx__gxr = 0
        vfpq__ytht = typ.data if isinstance(typ, StructType) else typ.types
        for sjw__rnjqr, t in enumerate(vfpq__ytht):
            apymi__atysb = bodo.utils.transform.get_type_alloc_counts(t)
            if apymi__atysb == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    sjw__rnjqr])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, sjw__rnjqr)
            stnza__shav = is_na_value(builder, context, val_obj, C_NA)
            voszk__ewtzf = builder.icmp_unsigned('!=', stnza__shav, lir.
                Constant(stnza__shav.type, 1))
            with builder.if_then(voszk__ewtzf):
                hgutd__hgaw = builder.load(fwvp__jgp)
                oyp__whi = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for sjw__rnjqr in range(apymi__atysb):
                    iirc__rbjo = builder.extract_value(hgutd__hgaw, 
                        lyx__gxr + sjw__rnjqr)
                    szkxa__dfle = builder.extract_value(oyp__whi, sjw__rnjqr)
                    hgutd__hgaw = builder.insert_value(hgutd__hgaw, builder
                        .add(iirc__rbjo, szkxa__dfle), lyx__gxr + sjw__rnjqr)
                builder.store(hgutd__hgaw, fwvp__jgp)
            lyx__gxr += apymi__atysb
        c.pyapi.decref(omhs__kmcc)
        c.pyapi.decref(C_NA)
        return builder.load(fwvp__jgp)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    uvvxc__idu = context.insert_const_string(builder.module, 'pandas')
    omhs__kmcc = c.pyapi.import_module_noblock(uvvxc__idu)
    C_NA = c.pyapi.object_getattr_string(omhs__kmcc, 'NA')
    wdorf__jwd = bodo.utils.transform.get_type_alloc_counts(typ)
    hgutd__hgaw = context.make_tuple(builder, types.Tuple(wdorf__jwd * [
        types.int64]), [n] + (wdorf__jwd - 1) * [context.get_constant(types
        .int64, 0)])
    fwvp__jgp = cgutils.alloca_once_value(builder, hgutd__hgaw)
    with cgutils.for_range(builder, n) as qro__ncz:
        pwaa__tkvoa = qro__ncz.index
        udf__ktry = seq_getitem(builder, context, arr_obj, pwaa__tkvoa)
        stnza__shav = is_na_value(builder, context, udf__ktry, C_NA)
        voszk__ewtzf = builder.icmp_unsigned('!=', stnza__shav, lir.
            Constant(stnza__shav.type, 1))
        with builder.if_then(voszk__ewtzf):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                hgutd__hgaw = builder.load(fwvp__jgp)
                oyp__whi = get_array_elem_counts(c, builder, context,
                    udf__ktry, typ.dtype)
                for sjw__rnjqr in range(wdorf__jwd - 1):
                    iirc__rbjo = builder.extract_value(hgutd__hgaw, 
                        sjw__rnjqr + 1)
                    szkxa__dfle = builder.extract_value(oyp__whi, sjw__rnjqr)
                    hgutd__hgaw = builder.insert_value(hgutd__hgaw, builder
                        .add(iirc__rbjo, szkxa__dfle), sjw__rnjqr + 1)
                builder.store(hgutd__hgaw, fwvp__jgp)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                lyx__gxr = 1
                for sjw__rnjqr, t in enumerate(typ.data):
                    apymi__atysb = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if apymi__atysb == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(udf__ktry, sjw__rnjqr)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(udf__ktry,
                            typ.names[sjw__rnjqr])
                    stnza__shav = is_na_value(builder, context, val_obj, C_NA)
                    voszk__ewtzf = builder.icmp_unsigned('!=', stnza__shav,
                        lir.Constant(stnza__shav.type, 1))
                    with builder.if_then(voszk__ewtzf):
                        hgutd__hgaw = builder.load(fwvp__jgp)
                        oyp__whi = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for sjw__rnjqr in range(apymi__atysb):
                            iirc__rbjo = builder.extract_value(hgutd__hgaw,
                                lyx__gxr + sjw__rnjqr)
                            szkxa__dfle = builder.extract_value(oyp__whi,
                                sjw__rnjqr)
                            hgutd__hgaw = builder.insert_value(hgutd__hgaw,
                                builder.add(iirc__rbjo, szkxa__dfle), 
                                lyx__gxr + sjw__rnjqr)
                        builder.store(hgutd__hgaw, fwvp__jgp)
                    lyx__gxr += apymi__atysb
            else:
                assert isinstance(typ, MapArrayType), typ
                hgutd__hgaw = builder.load(fwvp__jgp)
                ztgaq__lijlw = dict_keys(builder, context, udf__ktry)
                xeiqv__jrirn = dict_values(builder, context, udf__ktry)
                ecl__pcbe = get_array_elem_counts(c, builder, context,
                    ztgaq__lijlw, typ.key_arr_type)
                qubu__oqd = bodo.utils.transform.get_type_alloc_counts(typ.
                    key_arr_type)
                for sjw__rnjqr in range(1, qubu__oqd + 1):
                    iirc__rbjo = builder.extract_value(hgutd__hgaw, sjw__rnjqr)
                    szkxa__dfle = builder.extract_value(ecl__pcbe, 
                        sjw__rnjqr - 1)
                    hgutd__hgaw = builder.insert_value(hgutd__hgaw, builder
                        .add(iirc__rbjo, szkxa__dfle), sjw__rnjqr)
                hvrfb__kox = get_array_elem_counts(c, builder, context,
                    xeiqv__jrirn, typ.value_arr_type)
                for sjw__rnjqr in range(qubu__oqd + 1, wdorf__jwd):
                    iirc__rbjo = builder.extract_value(hgutd__hgaw, sjw__rnjqr)
                    szkxa__dfle = builder.extract_value(hvrfb__kox, 
                        sjw__rnjqr - qubu__oqd)
                    hgutd__hgaw = builder.insert_value(hgutd__hgaw, builder
                        .add(iirc__rbjo, szkxa__dfle), sjw__rnjqr)
                builder.store(hgutd__hgaw, fwvp__jgp)
                c.pyapi.decref(ztgaq__lijlw)
                c.pyapi.decref(xeiqv__jrirn)
        c.pyapi.decref(udf__ktry)
    c.pyapi.decref(omhs__kmcc)
    c.pyapi.decref(C_NA)
    return builder.load(fwvp__jgp)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    hmrql__rzc = n_elems.type.count
    assert hmrql__rzc >= 1
    xzpf__xswp = builder.extract_value(n_elems, 0)
    if hmrql__rzc != 1:
        qlny__abpli = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, sjw__rnjqr) for sjw__rnjqr in range(1, hmrql__rzc)])
        msuf__ifpg = types.Tuple([types.int64] * (hmrql__rzc - 1))
    else:
        qlny__abpli = context.get_dummy_value()
        msuf__ifpg = types.none
    wznbn__zoog = types.TypeRef(arr_type)
    ahg__qesmc = arr_type(types.int64, wznbn__zoog, msuf__ifpg)
    args = [xzpf__xswp, context.get_dummy_value(), qlny__abpli]
    tcfi__swhxa = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        vgg__gqy, edvtd__vpie = c.pyapi.call_jit_code(tcfi__swhxa,
            ahg__qesmc, args)
    else:
        edvtd__vpie = context.compile_internal(builder, tcfi__swhxa,
            ahg__qesmc, args)
    return edvtd__vpie


def is_ll_eq(builder, val1, val2):
    lsrdq__zmdlw = val1.type.pointee
    bod__hxf = val2.type.pointee
    assert lsrdq__zmdlw == bod__hxf, 'invalid llvm value comparison'
    if isinstance(lsrdq__zmdlw, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(lsrdq__zmdlw.elements) if isinstance(lsrdq__zmdlw,
            lir.BaseStructType) else lsrdq__zmdlw.count
        umcft__buts = lir.Constant(lir.IntType(1), 1)
        for sjw__rnjqr in range(n_elems):
            oiz__hrgf = lir.IntType(32)(0)
            drwai__sdadu = lir.IntType(32)(sjw__rnjqr)
            qpm__zsq = builder.gep(val1, [oiz__hrgf, drwai__sdadu],
                inbounds=True)
            kpoo__ksl = builder.gep(val2, [oiz__hrgf, drwai__sdadu],
                inbounds=True)
            umcft__buts = builder.and_(umcft__buts, is_ll_eq(builder,
                qpm__zsq, kpoo__ksl))
        return umcft__buts
    icje__znwe = builder.load(val1)
    riud__evmng = builder.load(val2)
    if icje__znwe.type in (lir.FloatType(), lir.DoubleType()):
        epfjf__rnqwe = 32 if icje__znwe.type == lir.FloatType() else 64
        icje__znwe = builder.bitcast(icje__znwe, lir.IntType(epfjf__rnqwe))
        riud__evmng = builder.bitcast(riud__evmng, lir.IntType(epfjf__rnqwe))
    return builder.icmp_unsigned('==', icje__znwe, riud__evmng)
