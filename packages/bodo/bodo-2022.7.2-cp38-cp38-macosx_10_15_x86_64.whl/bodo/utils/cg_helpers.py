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
    tvtc__lgqk = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    oarv__whmy = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    mdjwy__kww = builder.gep(null_bitmap_ptr, [tvtc__lgqk], inbounds=True)
    nbynm__tits = builder.load(mdjwy__kww)
    vxfp__ytjlt = lir.ArrayType(lir.IntType(8), 8)
    yuxbb__kodre = cgutils.alloca_once_value(builder, lir.Constant(
        vxfp__ytjlt, (1, 2, 4, 8, 16, 32, 64, 128)))
    krnh__kfwsm = builder.load(builder.gep(yuxbb__kodre, [lir.Constant(lir.
        IntType(64), 0), oarv__whmy], inbounds=True))
    if val:
        builder.store(builder.or_(nbynm__tits, krnh__kfwsm), mdjwy__kww)
    else:
        krnh__kfwsm = builder.xor(krnh__kfwsm, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(nbynm__tits, krnh__kfwsm), mdjwy__kww)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    tvtc__lgqk = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    oarv__whmy = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    nbynm__tits = builder.load(builder.gep(null_bitmap_ptr, [tvtc__lgqk],
        inbounds=True))
    vxfp__ytjlt = lir.ArrayType(lir.IntType(8), 8)
    yuxbb__kodre = cgutils.alloca_once_value(builder, lir.Constant(
        vxfp__ytjlt, (1, 2, 4, 8, 16, 32, 64, 128)))
    krnh__kfwsm = builder.load(builder.gep(yuxbb__kodre, [lir.Constant(lir.
        IntType(64), 0), oarv__whmy], inbounds=True))
    return builder.and_(nbynm__tits, krnh__kfwsm)


def pyarray_check(builder, context, obj):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    ykza__hjlnm = lir.FunctionType(lir.IntType(32), [nyjsk__prte])
    bed__qjba = cgutils.get_or_insert_function(builder.module, ykza__hjlnm,
        name='is_np_array')
    return builder.call(bed__qjba, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    wlta__rce = context.get_value_type(types.intp)
    vruku__aqtyj = lir.FunctionType(lir.IntType(8).as_pointer(), [
        nyjsk__prte, wlta__rce])
    vqyg__vzmyq = cgutils.get_or_insert_function(builder.module,
        vruku__aqtyj, name='array_getptr1')
    fla__wlcd = lir.FunctionType(nyjsk__prte, [nyjsk__prte, lir.IntType(8).
        as_pointer()])
    jhdm__zcgc = cgutils.get_or_insert_function(builder.module, fla__wlcd,
        name='array_getitem')
    wea__bptxd = builder.call(vqyg__vzmyq, [arr_obj, ind])
    return builder.call(jhdm__zcgc, [arr_obj, wea__bptxd])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    wlta__rce = context.get_value_type(types.intp)
    vruku__aqtyj = lir.FunctionType(lir.IntType(8).as_pointer(), [
        nyjsk__prte, wlta__rce])
    vqyg__vzmyq = cgutils.get_or_insert_function(builder.module,
        vruku__aqtyj, name='array_getptr1')
    dukm__iwonw = lir.FunctionType(lir.VoidType(), [nyjsk__prte, lir.
        IntType(8).as_pointer(), nyjsk__prte])
    ftta__sgpsq = cgutils.get_or_insert_function(builder.module,
        dukm__iwonw, name='array_setitem')
    wea__bptxd = builder.call(vqyg__vzmyq, [arr_obj, ind])
    builder.call(ftta__sgpsq, [arr_obj, wea__bptxd, val_obj])


def seq_getitem(builder, context, obj, ind):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    wlta__rce = context.get_value_type(types.intp)
    eckiy__ubv = lir.FunctionType(nyjsk__prte, [nyjsk__prte, wlta__rce])
    xfbt__ktrr = cgutils.get_or_insert_function(builder.module, eckiy__ubv,
        name='seq_getitem')
    return builder.call(xfbt__ktrr, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    unko__dnot = lir.FunctionType(lir.IntType(32), [nyjsk__prte, nyjsk__prte])
    vyay__twjat = cgutils.get_or_insert_function(builder.module, unko__dnot,
        name='is_na_value')
    return builder.call(vyay__twjat, [val, C_NA])


def list_check(builder, context, obj):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    kdlb__omir = context.get_value_type(types.int32)
    nlu__jnhl = lir.FunctionType(kdlb__omir, [nyjsk__prte])
    imz__kxz = cgutils.get_or_insert_function(builder.module, nlu__jnhl,
        name='list_check')
    return builder.call(imz__kxz, [obj])


def dict_keys(builder, context, obj):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    nlu__jnhl = lir.FunctionType(nyjsk__prte, [nyjsk__prte])
    imz__kxz = cgutils.get_or_insert_function(builder.module, nlu__jnhl,
        name='dict_keys')
    return builder.call(imz__kxz, [obj])


def dict_values(builder, context, obj):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    nlu__jnhl = lir.FunctionType(nyjsk__prte, [nyjsk__prte])
    imz__kxz = cgutils.get_or_insert_function(builder.module, nlu__jnhl,
        name='dict_values')
    return builder.call(imz__kxz, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    nyjsk__prte = context.get_argument_type(types.pyobject)
    nlu__jnhl = lir.FunctionType(lir.VoidType(), [nyjsk__prte, nyjsk__prte])
    imz__kxz = cgutils.get_or_insert_function(builder.module, nlu__jnhl,
        name='dict_merge_from_seq2')
    builder.call(imz__kxz, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    phj__dgjv = cgutils.alloca_once_value(builder, val)
    lcrm__bklu = list_check(builder, context, val)
    gvvyu__lev = builder.icmp_unsigned('!=', lcrm__bklu, lir.Constant(
        lcrm__bklu.type, 0))
    with builder.if_then(gvvyu__lev):
        hekl__xagf = context.insert_const_string(builder.module, 'numpy')
        qmulc__qiz = c.pyapi.import_module_noblock(hekl__xagf)
        osmif__mfl = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            osmif__mfl = str(typ.dtype)
        fpj__dfq = c.pyapi.object_getattr_string(qmulc__qiz, osmif__mfl)
        pnbc__nuh = builder.load(phj__dgjv)
        fgzk__xjyep = c.pyapi.call_method(qmulc__qiz, 'asarray', (pnbc__nuh,
            fpj__dfq))
        builder.store(fgzk__xjyep, phj__dgjv)
        c.pyapi.decref(qmulc__qiz)
        c.pyapi.decref(fpj__dfq)
    val = builder.load(phj__dgjv)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        ziin__nfztc = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        zmg__cdrif, qqwxv__bqeh = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [ziin__nfztc])
        context.nrt.decref(builder, typ, ziin__nfztc)
        return cgutils.pack_array(builder, [qqwxv__bqeh])
    if isinstance(typ, (StructType, types.BaseTuple)):
        hekl__xagf = context.insert_const_string(builder.module, 'pandas')
        ncvdi__uos = c.pyapi.import_module_noblock(hekl__xagf)
        C_NA = c.pyapi.object_getattr_string(ncvdi__uos, 'NA')
        beg__oxkz = bodo.utils.transform.get_type_alloc_counts(typ)
        krc__lmr = context.make_tuple(builder, types.Tuple(beg__oxkz * [
            types.int64]), beg__oxkz * [context.get_constant(types.int64, 0)])
        elz__gqeg = cgutils.alloca_once_value(builder, krc__lmr)
        kayp__brypp = 0
        zrdug__ivqv = typ.data if isinstance(typ, StructType) else typ.types
        for gauvg__wmt, t in enumerate(zrdug__ivqv):
            ijvk__apv = bodo.utils.transform.get_type_alloc_counts(t)
            if ijvk__apv == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    gauvg__wmt])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, gauvg__wmt)
            fbpw__ylf = is_na_value(builder, context, val_obj, C_NA)
            svu__vyt = builder.icmp_unsigned('!=', fbpw__ylf, lir.Constant(
                fbpw__ylf.type, 1))
            with builder.if_then(svu__vyt):
                krc__lmr = builder.load(elz__gqeg)
                nlya__lmqku = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for gauvg__wmt in range(ijvk__apv):
                    oxei__kilku = builder.extract_value(krc__lmr, 
                        kayp__brypp + gauvg__wmt)
                    tjlz__zhhr = builder.extract_value(nlya__lmqku, gauvg__wmt)
                    krc__lmr = builder.insert_value(krc__lmr, builder.add(
                        oxei__kilku, tjlz__zhhr), kayp__brypp + gauvg__wmt)
                builder.store(krc__lmr, elz__gqeg)
            kayp__brypp += ijvk__apv
        c.pyapi.decref(ncvdi__uos)
        c.pyapi.decref(C_NA)
        return builder.load(elz__gqeg)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    hekl__xagf = context.insert_const_string(builder.module, 'pandas')
    ncvdi__uos = c.pyapi.import_module_noblock(hekl__xagf)
    C_NA = c.pyapi.object_getattr_string(ncvdi__uos, 'NA')
    beg__oxkz = bodo.utils.transform.get_type_alloc_counts(typ)
    krc__lmr = context.make_tuple(builder, types.Tuple(beg__oxkz * [types.
        int64]), [n] + (beg__oxkz - 1) * [context.get_constant(types.int64, 0)]
        )
    elz__gqeg = cgutils.alloca_once_value(builder, krc__lmr)
    with cgutils.for_range(builder, n) as jjk__ptivd:
        ubdm__dkox = jjk__ptivd.index
        auglf__sgocf = seq_getitem(builder, context, arr_obj, ubdm__dkox)
        fbpw__ylf = is_na_value(builder, context, auglf__sgocf, C_NA)
        svu__vyt = builder.icmp_unsigned('!=', fbpw__ylf, lir.Constant(
            fbpw__ylf.type, 1))
        with builder.if_then(svu__vyt):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                krc__lmr = builder.load(elz__gqeg)
                nlya__lmqku = get_array_elem_counts(c, builder, context,
                    auglf__sgocf, typ.dtype)
                for gauvg__wmt in range(beg__oxkz - 1):
                    oxei__kilku = builder.extract_value(krc__lmr, 
                        gauvg__wmt + 1)
                    tjlz__zhhr = builder.extract_value(nlya__lmqku, gauvg__wmt)
                    krc__lmr = builder.insert_value(krc__lmr, builder.add(
                        oxei__kilku, tjlz__zhhr), gauvg__wmt + 1)
                builder.store(krc__lmr, elz__gqeg)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                kayp__brypp = 1
                for gauvg__wmt, t in enumerate(typ.data):
                    ijvk__apv = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if ijvk__apv == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(auglf__sgocf,
                            gauvg__wmt)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(auglf__sgocf,
                            typ.names[gauvg__wmt])
                    fbpw__ylf = is_na_value(builder, context, val_obj, C_NA)
                    svu__vyt = builder.icmp_unsigned('!=', fbpw__ylf, lir.
                        Constant(fbpw__ylf.type, 1))
                    with builder.if_then(svu__vyt):
                        krc__lmr = builder.load(elz__gqeg)
                        nlya__lmqku = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for gauvg__wmt in range(ijvk__apv):
                            oxei__kilku = builder.extract_value(krc__lmr, 
                                kayp__brypp + gauvg__wmt)
                            tjlz__zhhr = builder.extract_value(nlya__lmqku,
                                gauvg__wmt)
                            krc__lmr = builder.insert_value(krc__lmr,
                                builder.add(oxei__kilku, tjlz__zhhr), 
                                kayp__brypp + gauvg__wmt)
                        builder.store(krc__lmr, elz__gqeg)
                    kayp__brypp += ijvk__apv
            else:
                assert isinstance(typ, MapArrayType), typ
                krc__lmr = builder.load(elz__gqeg)
                tuih__tldfb = dict_keys(builder, context, auglf__sgocf)
                ebbh__hbva = dict_values(builder, context, auglf__sgocf)
                fnpz__hlqyh = get_array_elem_counts(c, builder, context,
                    tuih__tldfb, typ.key_arr_type)
                sgu__fsr = bodo.utils.transform.get_type_alloc_counts(typ.
                    key_arr_type)
                for gauvg__wmt in range(1, sgu__fsr + 1):
                    oxei__kilku = builder.extract_value(krc__lmr, gauvg__wmt)
                    tjlz__zhhr = builder.extract_value(fnpz__hlqyh, 
                        gauvg__wmt - 1)
                    krc__lmr = builder.insert_value(krc__lmr, builder.add(
                        oxei__kilku, tjlz__zhhr), gauvg__wmt)
                wlr__dqih = get_array_elem_counts(c, builder, context,
                    ebbh__hbva, typ.value_arr_type)
                for gauvg__wmt in range(sgu__fsr + 1, beg__oxkz):
                    oxei__kilku = builder.extract_value(krc__lmr, gauvg__wmt)
                    tjlz__zhhr = builder.extract_value(wlr__dqih, 
                        gauvg__wmt - sgu__fsr)
                    krc__lmr = builder.insert_value(krc__lmr, builder.add(
                        oxei__kilku, tjlz__zhhr), gauvg__wmt)
                builder.store(krc__lmr, elz__gqeg)
                c.pyapi.decref(tuih__tldfb)
                c.pyapi.decref(ebbh__hbva)
        c.pyapi.decref(auglf__sgocf)
    c.pyapi.decref(ncvdi__uos)
    c.pyapi.decref(C_NA)
    return builder.load(elz__gqeg)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    yttaw__rxxn = n_elems.type.count
    assert yttaw__rxxn >= 1
    eig__zrbm = builder.extract_value(n_elems, 0)
    if yttaw__rxxn != 1:
        vagp__jxq = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, gauvg__wmt) for gauvg__wmt in range(1, yttaw__rxxn)])
        odfpp__oixo = types.Tuple([types.int64] * (yttaw__rxxn - 1))
    else:
        vagp__jxq = context.get_dummy_value()
        odfpp__oixo = types.none
    fmtb__gbl = types.TypeRef(arr_type)
    azir__qzbnj = arr_type(types.int64, fmtb__gbl, odfpp__oixo)
    args = [eig__zrbm, context.get_dummy_value(), vagp__jxq]
    kgya__sdumi = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        zmg__cdrif, fwzw__lflmj = c.pyapi.call_jit_code(kgya__sdumi,
            azir__qzbnj, args)
    else:
        fwzw__lflmj = context.compile_internal(builder, kgya__sdumi,
            azir__qzbnj, args)
    return fwzw__lflmj


def is_ll_eq(builder, val1, val2):
    iplj__wix = val1.type.pointee
    xinn__bza = val2.type.pointee
    assert iplj__wix == xinn__bza, 'invalid llvm value comparison'
    if isinstance(iplj__wix, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(iplj__wix.elements) if isinstance(iplj__wix, lir.
            BaseStructType) else iplj__wix.count
        gnbpz__kale = lir.Constant(lir.IntType(1), 1)
        for gauvg__wmt in range(n_elems):
            wvmkr__wprbr = lir.IntType(32)(0)
            rema__vyqo = lir.IntType(32)(gauvg__wmt)
            hkpbs__ndtw = builder.gep(val1, [wvmkr__wprbr, rema__vyqo],
                inbounds=True)
            iessv__mqsos = builder.gep(val2, [wvmkr__wprbr, rema__vyqo],
                inbounds=True)
            gnbpz__kale = builder.and_(gnbpz__kale, is_ll_eq(builder,
                hkpbs__ndtw, iessv__mqsos))
        return gnbpz__kale
    yai__dgnoj = builder.load(val1)
    dvmm__dwh = builder.load(val2)
    if yai__dgnoj.type in (lir.FloatType(), lir.DoubleType()):
        jzkl__icc = 32 if yai__dgnoj.type == lir.FloatType() else 64
        yai__dgnoj = builder.bitcast(yai__dgnoj, lir.IntType(jzkl__icc))
        dvmm__dwh = builder.bitcast(dvmm__dwh, lir.IntType(jzkl__icc))
    return builder.icmp_unsigned('==', yai__dgnoj, dvmm__dwh)
