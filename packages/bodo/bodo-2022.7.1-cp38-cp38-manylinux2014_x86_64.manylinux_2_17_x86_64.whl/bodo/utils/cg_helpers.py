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
    mxh__ayx = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    sfs__pjdq = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    clbvb__wwcgb = builder.gep(null_bitmap_ptr, [mxh__ayx], inbounds=True)
    agllh__blvbj = builder.load(clbvb__wwcgb)
    enoiu__upsd = lir.ArrayType(lir.IntType(8), 8)
    dgwp__bsxfs = cgutils.alloca_once_value(builder, lir.Constant(
        enoiu__upsd, (1, 2, 4, 8, 16, 32, 64, 128)))
    lhs__dtgg = builder.load(builder.gep(dgwp__bsxfs, [lir.Constant(lir.
        IntType(64), 0), sfs__pjdq], inbounds=True))
    if val:
        builder.store(builder.or_(agllh__blvbj, lhs__dtgg), clbvb__wwcgb)
    else:
        lhs__dtgg = builder.xor(lhs__dtgg, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(agllh__blvbj, lhs__dtgg), clbvb__wwcgb)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    mxh__ayx = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    sfs__pjdq = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    agllh__blvbj = builder.load(builder.gep(null_bitmap_ptr, [mxh__ayx],
        inbounds=True))
    enoiu__upsd = lir.ArrayType(lir.IntType(8), 8)
    dgwp__bsxfs = cgutils.alloca_once_value(builder, lir.Constant(
        enoiu__upsd, (1, 2, 4, 8, 16, 32, 64, 128)))
    lhs__dtgg = builder.load(builder.gep(dgwp__bsxfs, [lir.Constant(lir.
        IntType(64), 0), sfs__pjdq], inbounds=True))
    return builder.and_(agllh__blvbj, lhs__dtgg)


def pyarray_check(builder, context, obj):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    ttkc__wlgp = lir.FunctionType(lir.IntType(32), [zzfda__jpxdn])
    bsrm__hnr = cgutils.get_or_insert_function(builder.module, ttkc__wlgp,
        name='is_np_array')
    return builder.call(bsrm__hnr, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    rcbx__acs = context.get_value_type(types.intp)
    wbyt__tng = lir.FunctionType(lir.IntType(8).as_pointer(), [zzfda__jpxdn,
        rcbx__acs])
    qiqr__fivn = cgutils.get_or_insert_function(builder.module, wbyt__tng,
        name='array_getptr1')
    ycbjr__sbwq = lir.FunctionType(zzfda__jpxdn, [zzfda__jpxdn, lir.IntType
        (8).as_pointer()])
    fvlyl__lmt = cgutils.get_or_insert_function(builder.module, ycbjr__sbwq,
        name='array_getitem')
    ikwl__gqqac = builder.call(qiqr__fivn, [arr_obj, ind])
    return builder.call(fvlyl__lmt, [arr_obj, ikwl__gqqac])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    rcbx__acs = context.get_value_type(types.intp)
    wbyt__tng = lir.FunctionType(lir.IntType(8).as_pointer(), [zzfda__jpxdn,
        rcbx__acs])
    qiqr__fivn = cgutils.get_or_insert_function(builder.module, wbyt__tng,
        name='array_getptr1')
    dxwm__ilowu = lir.FunctionType(lir.VoidType(), [zzfda__jpxdn, lir.
        IntType(8).as_pointer(), zzfda__jpxdn])
    ubsk__jftn = cgutils.get_or_insert_function(builder.module, dxwm__ilowu,
        name='array_setitem')
    ikwl__gqqac = builder.call(qiqr__fivn, [arr_obj, ind])
    builder.call(ubsk__jftn, [arr_obj, ikwl__gqqac, val_obj])


def seq_getitem(builder, context, obj, ind):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    rcbx__acs = context.get_value_type(types.intp)
    qhz__voxj = lir.FunctionType(zzfda__jpxdn, [zzfda__jpxdn, rcbx__acs])
    vgjmi__rta = cgutils.get_or_insert_function(builder.module, qhz__voxj,
        name='seq_getitem')
    return builder.call(vgjmi__rta, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    xgx__zcmxh = lir.FunctionType(lir.IntType(32), [zzfda__jpxdn, zzfda__jpxdn]
        )
    yve__bwdu = cgutils.get_or_insert_function(builder.module, xgx__zcmxh,
        name='is_na_value')
    return builder.call(yve__bwdu, [val, C_NA])


def list_check(builder, context, obj):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    nsuf__fng = context.get_value_type(types.int32)
    ofut__asfex = lir.FunctionType(nsuf__fng, [zzfda__jpxdn])
    sqgx__yszp = cgutils.get_or_insert_function(builder.module, ofut__asfex,
        name='list_check')
    return builder.call(sqgx__yszp, [obj])


def dict_keys(builder, context, obj):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    ofut__asfex = lir.FunctionType(zzfda__jpxdn, [zzfda__jpxdn])
    sqgx__yszp = cgutils.get_or_insert_function(builder.module, ofut__asfex,
        name='dict_keys')
    return builder.call(sqgx__yszp, [obj])


def dict_values(builder, context, obj):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    ofut__asfex = lir.FunctionType(zzfda__jpxdn, [zzfda__jpxdn])
    sqgx__yszp = cgutils.get_or_insert_function(builder.module, ofut__asfex,
        name='dict_values')
    return builder.call(sqgx__yszp, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    zzfda__jpxdn = context.get_argument_type(types.pyobject)
    ofut__asfex = lir.FunctionType(lir.VoidType(), [zzfda__jpxdn, zzfda__jpxdn]
        )
    sqgx__yszp = cgutils.get_or_insert_function(builder.module, ofut__asfex,
        name='dict_merge_from_seq2')
    builder.call(sqgx__yszp, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    cws__chgcq = cgutils.alloca_once_value(builder, val)
    rmht__scnsy = list_check(builder, context, val)
    groe__fwyko = builder.icmp_unsigned('!=', rmht__scnsy, lir.Constant(
        rmht__scnsy.type, 0))
    with builder.if_then(groe__fwyko):
        moyk__lelf = context.insert_const_string(builder.module, 'numpy')
        blmoy__ecdc = c.pyapi.import_module_noblock(moyk__lelf)
        cmn__imp = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            cmn__imp = str(typ.dtype)
        gyeoc__pmmq = c.pyapi.object_getattr_string(blmoy__ecdc, cmn__imp)
        audgs__coz = builder.load(cws__chgcq)
        nau__ragiy = c.pyapi.call_method(blmoy__ecdc, 'asarray', (
            audgs__coz, gyeoc__pmmq))
        builder.store(nau__ragiy, cws__chgcq)
        c.pyapi.decref(blmoy__ecdc)
        c.pyapi.decref(gyeoc__pmmq)
    val = builder.load(cws__chgcq)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        fkvql__bcdpo = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        cdum__xngn, mpp__qjc = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [fkvql__bcdpo])
        context.nrt.decref(builder, typ, fkvql__bcdpo)
        return cgutils.pack_array(builder, [mpp__qjc])
    if isinstance(typ, (StructType, types.BaseTuple)):
        moyk__lelf = context.insert_const_string(builder.module, 'pandas')
        djjwm__pzvr = c.pyapi.import_module_noblock(moyk__lelf)
        C_NA = c.pyapi.object_getattr_string(djjwm__pzvr, 'NA')
        ivngo__kqkgc = bodo.utils.transform.get_type_alloc_counts(typ)
        ldsd__fagw = context.make_tuple(builder, types.Tuple(ivngo__kqkgc *
            [types.int64]), ivngo__kqkgc * [context.get_constant(types.
            int64, 0)])
        cphm__nkg = cgutils.alloca_once_value(builder, ldsd__fagw)
        twv__qexof = 0
        itd__jlosw = typ.data if isinstance(typ, StructType) else typ.types
        for dwrc__opn, t in enumerate(itd__jlosw):
            jqq__ktew = bodo.utils.transform.get_type_alloc_counts(t)
            if jqq__ktew == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    dwrc__opn])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, dwrc__opn)
            kqspx__jnx = is_na_value(builder, context, val_obj, C_NA)
            lygq__eknf = builder.icmp_unsigned('!=', kqspx__jnx, lir.
                Constant(kqspx__jnx.type, 1))
            with builder.if_then(lygq__eknf):
                ldsd__fagw = builder.load(cphm__nkg)
                vtnz__jyl = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for dwrc__opn in range(jqq__ktew):
                    lqs__baio = builder.extract_value(ldsd__fagw, 
                        twv__qexof + dwrc__opn)
                    hoyd__ifnbm = builder.extract_value(vtnz__jyl, dwrc__opn)
                    ldsd__fagw = builder.insert_value(ldsd__fagw, builder.
                        add(lqs__baio, hoyd__ifnbm), twv__qexof + dwrc__opn)
                builder.store(ldsd__fagw, cphm__nkg)
            twv__qexof += jqq__ktew
        c.pyapi.decref(djjwm__pzvr)
        c.pyapi.decref(C_NA)
        return builder.load(cphm__nkg)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    moyk__lelf = context.insert_const_string(builder.module, 'pandas')
    djjwm__pzvr = c.pyapi.import_module_noblock(moyk__lelf)
    C_NA = c.pyapi.object_getattr_string(djjwm__pzvr, 'NA')
    ivngo__kqkgc = bodo.utils.transform.get_type_alloc_counts(typ)
    ldsd__fagw = context.make_tuple(builder, types.Tuple(ivngo__kqkgc * [
        types.int64]), [n] + (ivngo__kqkgc - 1) * [context.get_constant(
        types.int64, 0)])
    cphm__nkg = cgutils.alloca_once_value(builder, ldsd__fagw)
    with cgutils.for_range(builder, n) as lcx__msu:
        htwbi__hezb = lcx__msu.index
        fbgrf__gmtn = seq_getitem(builder, context, arr_obj, htwbi__hezb)
        kqspx__jnx = is_na_value(builder, context, fbgrf__gmtn, C_NA)
        lygq__eknf = builder.icmp_unsigned('!=', kqspx__jnx, lir.Constant(
            kqspx__jnx.type, 1))
        with builder.if_then(lygq__eknf):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                ldsd__fagw = builder.load(cphm__nkg)
                vtnz__jyl = get_array_elem_counts(c, builder, context,
                    fbgrf__gmtn, typ.dtype)
                for dwrc__opn in range(ivngo__kqkgc - 1):
                    lqs__baio = builder.extract_value(ldsd__fagw, dwrc__opn + 1
                        )
                    hoyd__ifnbm = builder.extract_value(vtnz__jyl, dwrc__opn)
                    ldsd__fagw = builder.insert_value(ldsd__fagw, builder.
                        add(lqs__baio, hoyd__ifnbm), dwrc__opn + 1)
                builder.store(ldsd__fagw, cphm__nkg)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                twv__qexof = 1
                for dwrc__opn, t in enumerate(typ.data):
                    jqq__ktew = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if jqq__ktew == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(fbgrf__gmtn, dwrc__opn)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(fbgrf__gmtn,
                            typ.names[dwrc__opn])
                    kqspx__jnx = is_na_value(builder, context, val_obj, C_NA)
                    lygq__eknf = builder.icmp_unsigned('!=', kqspx__jnx,
                        lir.Constant(kqspx__jnx.type, 1))
                    with builder.if_then(lygq__eknf):
                        ldsd__fagw = builder.load(cphm__nkg)
                        vtnz__jyl = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for dwrc__opn in range(jqq__ktew):
                            lqs__baio = builder.extract_value(ldsd__fagw, 
                                twv__qexof + dwrc__opn)
                            hoyd__ifnbm = builder.extract_value(vtnz__jyl,
                                dwrc__opn)
                            ldsd__fagw = builder.insert_value(ldsd__fagw,
                                builder.add(lqs__baio, hoyd__ifnbm), 
                                twv__qexof + dwrc__opn)
                        builder.store(ldsd__fagw, cphm__nkg)
                    twv__qexof += jqq__ktew
            else:
                assert isinstance(typ, MapArrayType), typ
                ldsd__fagw = builder.load(cphm__nkg)
                wcc__mnj = dict_keys(builder, context, fbgrf__gmtn)
                kku__qfyy = dict_values(builder, context, fbgrf__gmtn)
                cia__lyhp = get_array_elem_counts(c, builder, context,
                    wcc__mnj, typ.key_arr_type)
                bpig__dgvlq = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for dwrc__opn in range(1, bpig__dgvlq + 1):
                    lqs__baio = builder.extract_value(ldsd__fagw, dwrc__opn)
                    hoyd__ifnbm = builder.extract_value(cia__lyhp, 
                        dwrc__opn - 1)
                    ldsd__fagw = builder.insert_value(ldsd__fagw, builder.
                        add(lqs__baio, hoyd__ifnbm), dwrc__opn)
                zqbft__etiqt = get_array_elem_counts(c, builder, context,
                    kku__qfyy, typ.value_arr_type)
                for dwrc__opn in range(bpig__dgvlq + 1, ivngo__kqkgc):
                    lqs__baio = builder.extract_value(ldsd__fagw, dwrc__opn)
                    hoyd__ifnbm = builder.extract_value(zqbft__etiqt, 
                        dwrc__opn - bpig__dgvlq)
                    ldsd__fagw = builder.insert_value(ldsd__fagw, builder.
                        add(lqs__baio, hoyd__ifnbm), dwrc__opn)
                builder.store(ldsd__fagw, cphm__nkg)
                c.pyapi.decref(wcc__mnj)
                c.pyapi.decref(kku__qfyy)
        c.pyapi.decref(fbgrf__gmtn)
    c.pyapi.decref(djjwm__pzvr)
    c.pyapi.decref(C_NA)
    return builder.load(cphm__nkg)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    bym__mfyx = n_elems.type.count
    assert bym__mfyx >= 1
    rjdd__zel = builder.extract_value(n_elems, 0)
    if bym__mfyx != 1:
        ydh__rmfd = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, dwrc__opn) for dwrc__opn in range(1, bym__mfyx)])
        xmhs__ikr = types.Tuple([types.int64] * (bym__mfyx - 1))
    else:
        ydh__rmfd = context.get_dummy_value()
        xmhs__ikr = types.none
    txy__axu = types.TypeRef(arr_type)
    aly__ggn = arr_type(types.int64, txy__axu, xmhs__ikr)
    args = [rjdd__zel, context.get_dummy_value(), ydh__rmfd]
    ibpqc__pov = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        cdum__xngn, ewblp__mhdcm = c.pyapi.call_jit_code(ibpqc__pov,
            aly__ggn, args)
    else:
        ewblp__mhdcm = context.compile_internal(builder, ibpqc__pov,
            aly__ggn, args)
    return ewblp__mhdcm


def is_ll_eq(builder, val1, val2):
    gfqbz__kybn = val1.type.pointee
    sgra__uzx = val2.type.pointee
    assert gfqbz__kybn == sgra__uzx, 'invalid llvm value comparison'
    if isinstance(gfqbz__kybn, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(gfqbz__kybn.elements) if isinstance(gfqbz__kybn, lir.
            BaseStructType) else gfqbz__kybn.count
        iumk__qdd = lir.Constant(lir.IntType(1), 1)
        for dwrc__opn in range(n_elems):
            acmsv__hjq = lir.IntType(32)(0)
            ezbg__noym = lir.IntType(32)(dwrc__opn)
            dhw__miju = builder.gep(val1, [acmsv__hjq, ezbg__noym],
                inbounds=True)
            yrewo__qxkt = builder.gep(val2, [acmsv__hjq, ezbg__noym],
                inbounds=True)
            iumk__qdd = builder.and_(iumk__qdd, is_ll_eq(builder, dhw__miju,
                yrewo__qxkt))
        return iumk__qdd
    kpas__wqjad = builder.load(val1)
    fcvy__xuxu = builder.load(val2)
    if kpas__wqjad.type in (lir.FloatType(), lir.DoubleType()):
        styq__doy = 32 if kpas__wqjad.type == lir.FloatType() else 64
        kpas__wqjad = builder.bitcast(kpas__wqjad, lir.IntType(styq__doy))
        fcvy__xuxu = builder.bitcast(fcvy__xuxu, lir.IntType(styq__doy))
    return builder.icmp_unsigned('==', kpas__wqjad, fcvy__xuxu)
