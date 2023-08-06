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
    wfks__cbkvr = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    uxv__mml = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    hwh__lwl = builder.gep(null_bitmap_ptr, [wfks__cbkvr], inbounds=True)
    zunx__escb = builder.load(hwh__lwl)
    fzv__cgpvn = lir.ArrayType(lir.IntType(8), 8)
    mpua__ponr = cgutils.alloca_once_value(builder, lir.Constant(fzv__cgpvn,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    cel__qnek = builder.load(builder.gep(mpua__ponr, [lir.Constant(lir.
        IntType(64), 0), uxv__mml], inbounds=True))
    if val:
        builder.store(builder.or_(zunx__escb, cel__qnek), hwh__lwl)
    else:
        cel__qnek = builder.xor(cel__qnek, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(zunx__escb, cel__qnek), hwh__lwl)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    wfks__cbkvr = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    uxv__mml = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    zunx__escb = builder.load(builder.gep(null_bitmap_ptr, [wfks__cbkvr],
        inbounds=True))
    fzv__cgpvn = lir.ArrayType(lir.IntType(8), 8)
    mpua__ponr = cgutils.alloca_once_value(builder, lir.Constant(fzv__cgpvn,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    cel__qnek = builder.load(builder.gep(mpua__ponr, [lir.Constant(lir.
        IntType(64), 0), uxv__mml], inbounds=True))
    return builder.and_(zunx__escb, cel__qnek)


def pyarray_check(builder, context, obj):
    aicu__awg = context.get_argument_type(types.pyobject)
    nbpc__jihlt = lir.FunctionType(lir.IntType(32), [aicu__awg])
    vac__iqnlu = cgutils.get_or_insert_function(builder.module, nbpc__jihlt,
        name='is_np_array')
    return builder.call(vac__iqnlu, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    aicu__awg = context.get_argument_type(types.pyobject)
    psm__fpm = context.get_value_type(types.intp)
    wsaq__xucxj = lir.FunctionType(lir.IntType(8).as_pointer(), [aicu__awg,
        psm__fpm])
    iwbjb__mlxn = cgutils.get_or_insert_function(builder.module,
        wsaq__xucxj, name='array_getptr1')
    clno__snk = lir.FunctionType(aicu__awg, [aicu__awg, lir.IntType(8).
        as_pointer()])
    wvjdg__euq = cgutils.get_or_insert_function(builder.module, clno__snk,
        name='array_getitem')
    kqoai__oto = builder.call(iwbjb__mlxn, [arr_obj, ind])
    return builder.call(wvjdg__euq, [arr_obj, kqoai__oto])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    aicu__awg = context.get_argument_type(types.pyobject)
    psm__fpm = context.get_value_type(types.intp)
    wsaq__xucxj = lir.FunctionType(lir.IntType(8).as_pointer(), [aicu__awg,
        psm__fpm])
    iwbjb__mlxn = cgutils.get_or_insert_function(builder.module,
        wsaq__xucxj, name='array_getptr1')
    lqlyc__uqn = lir.FunctionType(lir.VoidType(), [aicu__awg, lir.IntType(8
        ).as_pointer(), aicu__awg])
    ieow__gisjj = cgutils.get_or_insert_function(builder.module, lqlyc__uqn,
        name='array_setitem')
    kqoai__oto = builder.call(iwbjb__mlxn, [arr_obj, ind])
    builder.call(ieow__gisjj, [arr_obj, kqoai__oto, val_obj])


def seq_getitem(builder, context, obj, ind):
    aicu__awg = context.get_argument_type(types.pyobject)
    psm__fpm = context.get_value_type(types.intp)
    bngmz__wobkz = lir.FunctionType(aicu__awg, [aicu__awg, psm__fpm])
    ari__fekr = cgutils.get_or_insert_function(builder.module, bngmz__wobkz,
        name='seq_getitem')
    return builder.call(ari__fekr, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    aicu__awg = context.get_argument_type(types.pyobject)
    uyji__bfxqx = lir.FunctionType(lir.IntType(32), [aicu__awg, aicu__awg])
    mgzxj__iqb = cgutils.get_or_insert_function(builder.module, uyji__bfxqx,
        name='is_na_value')
    return builder.call(mgzxj__iqb, [val, C_NA])


def list_check(builder, context, obj):
    aicu__awg = context.get_argument_type(types.pyobject)
    gxhzk__kiqf = context.get_value_type(types.int32)
    vrnqb__ftn = lir.FunctionType(gxhzk__kiqf, [aicu__awg])
    yak__lqu = cgutils.get_or_insert_function(builder.module, vrnqb__ftn,
        name='list_check')
    return builder.call(yak__lqu, [obj])


def dict_keys(builder, context, obj):
    aicu__awg = context.get_argument_type(types.pyobject)
    vrnqb__ftn = lir.FunctionType(aicu__awg, [aicu__awg])
    yak__lqu = cgutils.get_or_insert_function(builder.module, vrnqb__ftn,
        name='dict_keys')
    return builder.call(yak__lqu, [obj])


def dict_values(builder, context, obj):
    aicu__awg = context.get_argument_type(types.pyobject)
    vrnqb__ftn = lir.FunctionType(aicu__awg, [aicu__awg])
    yak__lqu = cgutils.get_or_insert_function(builder.module, vrnqb__ftn,
        name='dict_values')
    return builder.call(yak__lqu, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    aicu__awg = context.get_argument_type(types.pyobject)
    vrnqb__ftn = lir.FunctionType(lir.VoidType(), [aicu__awg, aicu__awg])
    yak__lqu = cgutils.get_or_insert_function(builder.module, vrnqb__ftn,
        name='dict_merge_from_seq2')
    builder.call(yak__lqu, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    tpq__xglxo = cgutils.alloca_once_value(builder, val)
    bgov__aqxf = list_check(builder, context, val)
    asxgl__etno = builder.icmp_unsigned('!=', bgov__aqxf, lir.Constant(
        bgov__aqxf.type, 0))
    with builder.if_then(asxgl__etno):
        fettd__qbg = context.insert_const_string(builder.module, 'numpy')
        zaa__iuw = c.pyapi.import_module_noblock(fettd__qbg)
        kph__zqy = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            kph__zqy = str(typ.dtype)
        btrhu__diri = c.pyapi.object_getattr_string(zaa__iuw, kph__zqy)
        qmbr__aft = builder.load(tpq__xglxo)
        yas__bhjf = c.pyapi.call_method(zaa__iuw, 'asarray', (qmbr__aft,
            btrhu__diri))
        builder.store(yas__bhjf, tpq__xglxo)
        c.pyapi.decref(zaa__iuw)
        c.pyapi.decref(btrhu__diri)
    val = builder.load(tpq__xglxo)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        ypv__ger = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        idok__mlhni, qxfvg__exxgb = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [ypv__ger])
        context.nrt.decref(builder, typ, ypv__ger)
        return cgutils.pack_array(builder, [qxfvg__exxgb])
    if isinstance(typ, (StructType, types.BaseTuple)):
        fettd__qbg = context.insert_const_string(builder.module, 'pandas')
        zkbtp__dqp = c.pyapi.import_module_noblock(fettd__qbg)
        C_NA = c.pyapi.object_getattr_string(zkbtp__dqp, 'NA')
        gxvm__mtvey = bodo.utils.transform.get_type_alloc_counts(typ)
        vkrt__snv = context.make_tuple(builder, types.Tuple(gxvm__mtvey * [
            types.int64]), gxvm__mtvey * [context.get_constant(types.int64, 0)]
            )
        djs__slso = cgutils.alloca_once_value(builder, vkrt__snv)
        cpu__cdto = 0
        ddkxx__trro = typ.data if isinstance(typ, StructType) else typ.types
        for ouoxe__tqo, t in enumerate(ddkxx__trro):
            estz__dgf = bodo.utils.transform.get_type_alloc_counts(t)
            if estz__dgf == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    ouoxe__tqo])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, ouoxe__tqo)
            ubh__sgbri = is_na_value(builder, context, val_obj, C_NA)
            xykg__apizr = builder.icmp_unsigned('!=', ubh__sgbri, lir.
                Constant(ubh__sgbri.type, 1))
            with builder.if_then(xykg__apizr):
                vkrt__snv = builder.load(djs__slso)
                avden__yrr = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for ouoxe__tqo in range(estz__dgf):
                    aslw__swql = builder.extract_value(vkrt__snv, cpu__cdto +
                        ouoxe__tqo)
                    zdqab__zid = builder.extract_value(avden__yrr, ouoxe__tqo)
                    vkrt__snv = builder.insert_value(vkrt__snv, builder.add
                        (aslw__swql, zdqab__zid), cpu__cdto + ouoxe__tqo)
                builder.store(vkrt__snv, djs__slso)
            cpu__cdto += estz__dgf
        c.pyapi.decref(zkbtp__dqp)
        c.pyapi.decref(C_NA)
        return builder.load(djs__slso)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    fettd__qbg = context.insert_const_string(builder.module, 'pandas')
    zkbtp__dqp = c.pyapi.import_module_noblock(fettd__qbg)
    C_NA = c.pyapi.object_getattr_string(zkbtp__dqp, 'NA')
    gxvm__mtvey = bodo.utils.transform.get_type_alloc_counts(typ)
    vkrt__snv = context.make_tuple(builder, types.Tuple(gxvm__mtvey * [
        types.int64]), [n] + (gxvm__mtvey - 1) * [context.get_constant(
        types.int64, 0)])
    djs__slso = cgutils.alloca_once_value(builder, vkrt__snv)
    with cgutils.for_range(builder, n) as gfx__mfbt:
        omg__zsm = gfx__mfbt.index
        muamt__wvh = seq_getitem(builder, context, arr_obj, omg__zsm)
        ubh__sgbri = is_na_value(builder, context, muamt__wvh, C_NA)
        xykg__apizr = builder.icmp_unsigned('!=', ubh__sgbri, lir.Constant(
            ubh__sgbri.type, 1))
        with builder.if_then(xykg__apizr):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                vkrt__snv = builder.load(djs__slso)
                avden__yrr = get_array_elem_counts(c, builder, context,
                    muamt__wvh, typ.dtype)
                for ouoxe__tqo in range(gxvm__mtvey - 1):
                    aslw__swql = builder.extract_value(vkrt__snv, 
                        ouoxe__tqo + 1)
                    zdqab__zid = builder.extract_value(avden__yrr, ouoxe__tqo)
                    vkrt__snv = builder.insert_value(vkrt__snv, builder.add
                        (aslw__swql, zdqab__zid), ouoxe__tqo + 1)
                builder.store(vkrt__snv, djs__slso)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                cpu__cdto = 1
                for ouoxe__tqo, t in enumerate(typ.data):
                    estz__dgf = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if estz__dgf == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(muamt__wvh, ouoxe__tqo)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(muamt__wvh,
                            typ.names[ouoxe__tqo])
                    ubh__sgbri = is_na_value(builder, context, val_obj, C_NA)
                    xykg__apizr = builder.icmp_unsigned('!=', ubh__sgbri,
                        lir.Constant(ubh__sgbri.type, 1))
                    with builder.if_then(xykg__apizr):
                        vkrt__snv = builder.load(djs__slso)
                        avden__yrr = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for ouoxe__tqo in range(estz__dgf):
                            aslw__swql = builder.extract_value(vkrt__snv, 
                                cpu__cdto + ouoxe__tqo)
                            zdqab__zid = builder.extract_value(avden__yrr,
                                ouoxe__tqo)
                            vkrt__snv = builder.insert_value(vkrt__snv,
                                builder.add(aslw__swql, zdqab__zid), 
                                cpu__cdto + ouoxe__tqo)
                        builder.store(vkrt__snv, djs__slso)
                    cpu__cdto += estz__dgf
            else:
                assert isinstance(typ, MapArrayType), typ
                vkrt__snv = builder.load(djs__slso)
                mipa__wos = dict_keys(builder, context, muamt__wvh)
                wznb__cfgd = dict_values(builder, context, muamt__wvh)
                ujtvb__wyvkl = get_array_elem_counts(c, builder, context,
                    mipa__wos, typ.key_arr_type)
                leam__oprpf = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for ouoxe__tqo in range(1, leam__oprpf + 1):
                    aslw__swql = builder.extract_value(vkrt__snv, ouoxe__tqo)
                    zdqab__zid = builder.extract_value(ujtvb__wyvkl, 
                        ouoxe__tqo - 1)
                    vkrt__snv = builder.insert_value(vkrt__snv, builder.add
                        (aslw__swql, zdqab__zid), ouoxe__tqo)
                eekf__pgj = get_array_elem_counts(c, builder, context,
                    wznb__cfgd, typ.value_arr_type)
                for ouoxe__tqo in range(leam__oprpf + 1, gxvm__mtvey):
                    aslw__swql = builder.extract_value(vkrt__snv, ouoxe__tqo)
                    zdqab__zid = builder.extract_value(eekf__pgj, 
                        ouoxe__tqo - leam__oprpf)
                    vkrt__snv = builder.insert_value(vkrt__snv, builder.add
                        (aslw__swql, zdqab__zid), ouoxe__tqo)
                builder.store(vkrt__snv, djs__slso)
                c.pyapi.decref(mipa__wos)
                c.pyapi.decref(wznb__cfgd)
        c.pyapi.decref(muamt__wvh)
    c.pyapi.decref(zkbtp__dqp)
    c.pyapi.decref(C_NA)
    return builder.load(djs__slso)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    gtos__tfjb = n_elems.type.count
    assert gtos__tfjb >= 1
    eta__rdif = builder.extract_value(n_elems, 0)
    if gtos__tfjb != 1:
        jevb__ixurt = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, ouoxe__tqo) for ouoxe__tqo in range(1, gtos__tfjb)])
        cyqf__fyc = types.Tuple([types.int64] * (gtos__tfjb - 1))
    else:
        jevb__ixurt = context.get_dummy_value()
        cyqf__fyc = types.none
    egy__pery = types.TypeRef(arr_type)
    wvg__dbyt = arr_type(types.int64, egy__pery, cyqf__fyc)
    args = [eta__rdif, context.get_dummy_value(), jevb__ixurt]
    mrd__zkoeh = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        idok__mlhni, dzg__gcf = c.pyapi.call_jit_code(mrd__zkoeh, wvg__dbyt,
            args)
    else:
        dzg__gcf = context.compile_internal(builder, mrd__zkoeh, wvg__dbyt,
            args)
    return dzg__gcf


def is_ll_eq(builder, val1, val2):
    jsdko__nzay = val1.type.pointee
    wzfph__ryo = val2.type.pointee
    assert jsdko__nzay == wzfph__ryo, 'invalid llvm value comparison'
    if isinstance(jsdko__nzay, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(jsdko__nzay.elements) if isinstance(jsdko__nzay, lir.
            BaseStructType) else jsdko__nzay.count
        auslc__dxtq = lir.Constant(lir.IntType(1), 1)
        for ouoxe__tqo in range(n_elems):
            vjug__rsnlc = lir.IntType(32)(0)
            gbp__amido = lir.IntType(32)(ouoxe__tqo)
            nbnw__twdj = builder.gep(val1, [vjug__rsnlc, gbp__amido],
                inbounds=True)
            bpcve__zqf = builder.gep(val2, [vjug__rsnlc, gbp__amido],
                inbounds=True)
            auslc__dxtq = builder.and_(auslc__dxtq, is_ll_eq(builder,
                nbnw__twdj, bpcve__zqf))
        return auslc__dxtq
    hanj__xeoe = builder.load(val1)
    ary__tgz = builder.load(val2)
    if hanj__xeoe.type in (lir.FloatType(), lir.DoubleType()):
        beci__cjv = 32 if hanj__xeoe.type == lir.FloatType() else 64
        hanj__xeoe = builder.bitcast(hanj__xeoe, lir.IntType(beci__cjv))
        ary__tgz = builder.bitcast(ary__tgz, lir.IntType(beci__cjv))
    return builder.icmp_unsigned('==', hanj__xeoe, ary__tgz)
