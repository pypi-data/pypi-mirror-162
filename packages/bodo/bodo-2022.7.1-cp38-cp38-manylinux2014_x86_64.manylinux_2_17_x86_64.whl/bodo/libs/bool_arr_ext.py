"""Nullable boolean array that stores data in Numpy format (1 byte per value)
but nulls are stored in bit arrays (1 bit per value) similar to Arrow's nulls.
Pandas converts boolean array to object when NAs are introduced.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import is_list_like_index_type
ll.add_symbol('is_bool_array', hstr_ext.is_bool_array)
ll.add_symbol('is_pd_boolean_array', hstr_ext.is_pd_boolean_array)
ll.add_symbol('unbox_bool_array_obj', hstr_ext.unbox_bool_array_obj)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_overload_false, is_overload_true, parse_dtype, raise_bodo_error


class BooleanArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BooleanArrayType, self).__init__(name='BooleanArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.bool_

    def copy(self):
        return BooleanArrayType()


boolean_array = BooleanArrayType()


@typeof_impl.register(pd.arrays.BooleanArray)
def typeof_boolean_array(val, c):
    return boolean_array


data_type = types.Array(types.bool_, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(BooleanArrayType)
class BooleanArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kezt__aempb = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, kezt__aempb)


make_attribute_wrapper(BooleanArrayType, 'data', '_data')
make_attribute_wrapper(BooleanArrayType, 'null_bitmap', '_null_bitmap')


class BooleanDtype(types.Number):

    def __init__(self):
        self.dtype = types.bool_
        super(BooleanDtype, self).__init__('BooleanDtype')


boolean_dtype = BooleanDtype()
register_model(BooleanDtype)(models.OpaqueModel)


@box(BooleanDtype)
def box_boolean_dtype(typ, val, c):
    rqsd__boyfy = c.context.insert_const_string(c.builder.module, 'pandas')
    lrpmt__opt = c.pyapi.import_module_noblock(rqsd__boyfy)
    xvpwi__ini = c.pyapi.call_method(lrpmt__opt, 'BooleanDtype', ())
    c.pyapi.decref(lrpmt__opt)
    return xvpwi__ini


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    sizv__deaq = n + 7 >> 3
    return np.full(sizv__deaq, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    wtydo__qmhkj = c.context.typing_context.resolve_value_type(func)
    eakx__vsazu = wtydo__qmhkj.get_call_type(c.context.typing_context,
        arg_typs, {})
    utt__tni = c.context.get_function(wtydo__qmhkj, eakx__vsazu)
    rmix__rwtvb = c.context.call_conv.get_function_type(eakx__vsazu.
        return_type, eakx__vsazu.args)
    rnz__gbz = c.builder.module
    uwiy__wycvq = lir.Function(rnz__gbz, rmix__rwtvb, name=rnz__gbz.
        get_unique_name('.func_conv'))
    uwiy__wycvq.linkage = 'internal'
    tph__jcpw = lir.IRBuilder(uwiy__wycvq.append_basic_block())
    unmr__uyaap = c.context.call_conv.decode_arguments(tph__jcpw,
        eakx__vsazu.args, uwiy__wycvq)
    ooxrr__hveh = utt__tni(tph__jcpw, unmr__uyaap)
    c.context.call_conv.return_value(tph__jcpw, ooxrr__hveh)
    ivvx__llc, gxvn__hlm = c.context.call_conv.call_function(c.builder,
        uwiy__wycvq, eakx__vsazu.return_type, eakx__vsazu.args, args)
    return gxvn__hlm


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    zohg__auwx = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(zohg__auwx)
    c.pyapi.decref(zohg__auwx)
    rmix__rwtvb = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    bdmg__yrp = cgutils.get_or_insert_function(c.builder.module,
        rmix__rwtvb, name='is_bool_array')
    rmix__rwtvb = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    uwiy__wycvq = cgutils.get_or_insert_function(c.builder.module,
        rmix__rwtvb, name='is_pd_boolean_array')
    wupwi__nrs = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tnqbb__jco = c.builder.call(uwiy__wycvq, [obj])
    isjaz__xheof = c.builder.icmp_unsigned('!=', tnqbb__jco, tnqbb__jco.type(0)
        )
    with c.builder.if_else(isjaz__xheof) as (yjsc__szdph, jqqgk__jizrr):
        with yjsc__szdph:
            uvu__nojo = c.pyapi.object_getattr_string(obj, '_data')
            wupwi__nrs.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), uvu__nojo).value
            drfi__ymgx = c.pyapi.object_getattr_string(obj, '_mask')
            irk__xoxtg = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), drfi__ymgx).value
            sizv__deaq = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            jfw__tado = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, irk__xoxtg)
            spbyk__rgjcq = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [sizv__deaq])
            rmix__rwtvb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            uwiy__wycvq = cgutils.get_or_insert_function(c.builder.module,
                rmix__rwtvb, name='mask_arr_to_bitmap')
            c.builder.call(uwiy__wycvq, [spbyk__rgjcq.data, jfw__tado.data, n])
            wupwi__nrs.null_bitmap = spbyk__rgjcq._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), irk__xoxtg)
            c.pyapi.decref(uvu__nojo)
            c.pyapi.decref(drfi__ymgx)
        with jqqgk__jizrr:
            ycpay__czsv = c.builder.call(bdmg__yrp, [obj])
            hff__vnot = c.builder.icmp_unsigned('!=', ycpay__czsv,
                ycpay__czsv.type(0))
            with c.builder.if_else(hff__vnot) as (oppwt__ecus, ycr__sffa):
                with oppwt__ecus:
                    wupwi__nrs.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    wupwi__nrs.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with ycr__sffa:
                    wupwi__nrs.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    sizv__deaq = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    wupwi__nrs.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [sizv__deaq])._getvalue()
                    puy__ltrfa = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, wupwi__nrs.data
                        ).data
                    wusmk__scjay = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, wupwi__nrs.
                        null_bitmap).data
                    rmix__rwtvb = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    uwiy__wycvq = cgutils.get_or_insert_function(c.builder.
                        module, rmix__rwtvb, name='unbox_bool_array_obj')
                    c.builder.call(uwiy__wycvq, [obj, puy__ltrfa,
                        wusmk__scjay, n])
    return NativeValue(wupwi__nrs._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    wupwi__nrs = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        wupwi__nrs.data, c.env_manager)
    zqt__kpje = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, wupwi__nrs.null_bitmap).data
    zohg__auwx = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(zohg__auwx)
    rqsd__boyfy = c.context.insert_const_string(c.builder.module, 'numpy')
    mxsx__knc = c.pyapi.import_module_noblock(rqsd__boyfy)
    jtuos__vbdff = c.pyapi.object_getattr_string(mxsx__knc, 'bool_')
    irk__xoxtg = c.pyapi.call_method(mxsx__knc, 'empty', (zohg__auwx,
        jtuos__vbdff))
    kcfbb__ubbkg = c.pyapi.object_getattr_string(irk__xoxtg, 'ctypes')
    hxf__pnvg = c.pyapi.object_getattr_string(kcfbb__ubbkg, 'data')
    dxvy__nlf = c.builder.inttoptr(c.pyapi.long_as_longlong(hxf__pnvg), lir
        .IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as pxld__wfdho:
        ewp__apuw = pxld__wfdho.index
        phwle__yyrme = c.builder.lshr(ewp__apuw, lir.Constant(lir.IntType(
            64), 3))
        tdbn__zlro = c.builder.load(cgutils.gep(c.builder, zqt__kpje,
            phwle__yyrme))
        wrbe__tlso = c.builder.trunc(c.builder.and_(ewp__apuw, lir.Constant
            (lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(tdbn__zlro, wrbe__tlso), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        jrv__khl = cgutils.gep(c.builder, dxvy__nlf, ewp__apuw)
        c.builder.store(val, jrv__khl)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        wupwi__nrs.null_bitmap)
    rqsd__boyfy = c.context.insert_const_string(c.builder.module, 'pandas')
    lrpmt__opt = c.pyapi.import_module_noblock(rqsd__boyfy)
    bzcc__hfer = c.pyapi.object_getattr_string(lrpmt__opt, 'arrays')
    xvpwi__ini = c.pyapi.call_method(bzcc__hfer, 'BooleanArray', (data,
        irk__xoxtg))
    c.pyapi.decref(lrpmt__opt)
    c.pyapi.decref(zohg__auwx)
    c.pyapi.decref(mxsx__knc)
    c.pyapi.decref(jtuos__vbdff)
    c.pyapi.decref(kcfbb__ubbkg)
    c.pyapi.decref(hxf__pnvg)
    c.pyapi.decref(bzcc__hfer)
    c.pyapi.decref(data)
    c.pyapi.decref(irk__xoxtg)
    return xvpwi__ini


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    nfyk__rtlw = np.empty(n, np.bool_)
    aomul__rutto = np.empty(n + 7 >> 3, np.uint8)
    for ewp__apuw, s in enumerate(pyval):
        bgpf__ctn = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(aomul__rutto, ewp__apuw, int(
            not bgpf__ctn))
        if not bgpf__ctn:
            nfyk__rtlw[ewp__apuw] = s
    lir__oqp = context.get_constant_generic(builder, data_type, nfyk__rtlw)
    bwjmd__brqp = context.get_constant_generic(builder, nulls_type,
        aomul__rutto)
    return lir.Constant.literal_struct([lir__oqp, bwjmd__brqp])


def lower_init_bool_array(context, builder, signature, args):
    buw__mlwcq, wzlgt__vacq = args
    wupwi__nrs = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    wupwi__nrs.data = buw__mlwcq
    wupwi__nrs.null_bitmap = wzlgt__vacq
    context.nrt.incref(builder, signature.args[0], buw__mlwcq)
    context.nrt.incref(builder, signature.args[1], wzlgt__vacq)
    return wupwi__nrs._getvalue()


@intrinsic
def init_bool_array(typingctx, data, null_bitmap=None):
    assert data == types.Array(types.bool_, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    sig = boolean_array(data, null_bitmap)
    return sig, lower_init_bool_array


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_bool_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    avuhx__tsw = args[0]
    if equiv_set.has_shape(avuhx__tsw):
        return ArrayAnalysis.AnalyzeResult(shape=avuhx__tsw, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    avuhx__tsw = args[0]
    if equiv_set.has_shape(avuhx__tsw):
        return ArrayAnalysis.AnalyzeResult(shape=avuhx__tsw, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_init_bool_array = (
    init_bool_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_bool_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_bool_array',
    'bodo.libs.bool_arr_ext'] = alias_ext_init_bool_array
numba.core.ir_utils.alias_func_extensions['get_bool_arr_data',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_bool_arr_bitmap',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_bool_array(n):
    nfyk__rtlw = np.empty(n, dtype=np.bool_)
    sclvo__lzm = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(nfyk__rtlw, sclvo__lzm)


def alloc_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_alloc_bool_array = (
    alloc_bool_array_equiv)


@overload(operator.getitem, no_unliteral=True)
def bool_arr_getitem(A, ind):
    if A != boolean_array:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            bdaqu__zod, jrz__sjnda = array_getitem_bool_index(A, ind)
            return init_bool_array(bdaqu__zod, jrz__sjnda)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            bdaqu__zod, jrz__sjnda = array_getitem_int_index(A, ind)
            return init_bool_array(bdaqu__zod, jrz__sjnda)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            bdaqu__zod, jrz__sjnda = array_getitem_slice_index(A, ind)
            return init_bool_array(bdaqu__zod, jrz__sjnda)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    yrf__ptz = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(yrf__ptz)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(yrf__ptz)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for BooleanArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_bool_arr_len(A):
    if A == boolean_array:
        return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'size')
def overload_bool_arr_size(A):
    return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'shape')
def overload_bool_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(BooleanArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: pd.BooleanDtype()


@overload_attribute(BooleanArrayType, 'ndim')
def overload_bool_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BooleanArrayType, 'nbytes')
def bool_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(BooleanArrayType, 'copy', no_unliteral=True)
def overload_bool_arr_copy(A):
    return lambda A: bodo.libs.bool_arr_ext.init_bool_array(bodo.libs.
        bool_arr_ext.get_bool_arr_data(A).copy(), bodo.libs.bool_arr_ext.
        get_bool_arr_bitmap(A).copy())


@overload_method(BooleanArrayType, 'sum', no_unliteral=True, inline='always')
def overload_bool_sum(A):

    def impl(A):
        numba.parfors.parfor.init_prange()
        s = 0
        for ewp__apuw in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, ewp__apuw):
                val = A[ewp__apuw]
            s += val
        return s
    return impl


@overload_method(BooleanArrayType, 'astype', no_unliteral=True)
def overload_bool_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "BooleanArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if dtype == types.bool_:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    nb_dtype = parse_dtype(dtype, 'BooleanArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
            n = len(data)
            hanpb__xqs = np.empty(n, nb_dtype)
            for ewp__apuw in numba.parfors.parfor.internal_prange(n):
                hanpb__xqs[ewp__apuw] = data[ewp__apuw]
                if bodo.libs.array_kernels.isna(A, ewp__apuw):
                    hanpb__xqs[ewp__apuw] = np.nan
            return hanpb__xqs
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        hanpb__xqs = np.empty(n, dtype=np.bool_)
        for ewp__apuw in numba.parfors.parfor.internal_prange(n):
            hanpb__xqs[ewp__apuw] = data[ewp__apuw]
            if bodo.libs.array_kernels.isna(A, ewp__apuw):
                hanpb__xqs[ewp__apuw] = value
        return hanpb__xqs
    return impl


@overload(str, no_unliteral=True)
def overload_str_bool(val):
    if val == types.bool_:

        def impl(val):
            if val:
                return 'True'
            return 'False'
        return impl


ufunc_aliases = {'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    segbo__qdnt = op.__name__
    segbo__qdnt = ufunc_aliases.get(segbo__qdnt, segbo__qdnt)
    if n_inputs == 1:

        def overload_bool_arr_op_nin_1(A):
            if isinstance(A, BooleanArrayType):
                return bodo.libs.int_arr_ext.get_nullable_array_unary_impl(op,
                    A)
        return overload_bool_arr_op_nin_1
    elif n_inputs == 2:

        def overload_bool_arr_op_nin_2(lhs, rhs):
            if lhs == boolean_array or rhs == boolean_array:
                return bodo.libs.int_arr_ext.get_nullable_array_binary_impl(op,
                    lhs, rhs)
        return overload_bool_arr_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for vfs__elaq in numba.np.ufunc_db.get_ufuncs():
        vxxw__hur = create_op_overload(vfs__elaq, vfs__elaq.nin)
        overload(vfs__elaq, no_unliteral=True)(vxxw__hur)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        vxxw__hur = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vxxw__hur)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        vxxw__hur = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vxxw__hur)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        vxxw__hur = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(vxxw__hur)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        wrbe__tlso = []
        iod__zpn = False
        jowy__mhzd = False
        roql__mipbr = False
        for ewp__apuw in range(len(A)):
            if bodo.libs.array_kernels.isna(A, ewp__apuw):
                if not iod__zpn:
                    data.append(False)
                    wrbe__tlso.append(False)
                    iod__zpn = True
                continue
            val = A[ewp__apuw]
            if val and not jowy__mhzd:
                data.append(True)
                wrbe__tlso.append(True)
                jowy__mhzd = True
            if not val and not roql__mipbr:
                data.append(False)
                wrbe__tlso.append(True)
                roql__mipbr = True
            if iod__zpn and jowy__mhzd and roql__mipbr:
                break
        bdaqu__zod = np.array(data)
        n = len(bdaqu__zod)
        sizv__deaq = 1
        jrz__sjnda = np.empty(sizv__deaq, np.uint8)
        for ibd__wenwf in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(jrz__sjnda, ibd__wenwf,
                wrbe__tlso[ibd__wenwf])
        return init_bool_array(bdaqu__zod, jrz__sjnda)
    return impl_bool_arr


@overload(operator.getitem, no_unliteral=True)
def bool_arr_ind_getitem(A, ind):
    if ind == boolean_array and (isinstance(A, (types.Array, bodo.libs.
        int_arr_ext.IntegerArrayType)) or isinstance(A, bodo.libs.
        struct_arr_ext.StructArrayType) or isinstance(A, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType) or isinstance(A, bodo.libs.
        map_arr_ext.MapArrayType) or A in (string_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type, boolean_array)):
        return lambda A, ind: A[ind._data]


@lower_cast(types.Array(types.bool_, 1, 'C'), boolean_array)
def cast_np_bool_arr_to_bool_arr(context, builder, fromty, toty, val):
    func = lambda A: bodo.libs.bool_arr_ext.init_bool_array(A, np.full(len(
        A) + 7 >> 3, 255, np.uint8))
    xvpwi__ini = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, xvpwi__ini)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    pgos__poqju = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        cgv__gfo = bodo.utils.utils.is_array_typ(val1, False)
        aeqpj__ubb = bodo.utils.utils.is_array_typ(val2, False)
        omckh__xnmqq = 'val1' if cgv__gfo else 'val2'
        shvtg__mlzxy = 'def impl(val1, val2):\n'
        shvtg__mlzxy += f'  n = len({omckh__xnmqq})\n'
        shvtg__mlzxy += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        shvtg__mlzxy += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if cgv__gfo:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            ddme__axc = 'val1[i]'
        else:
            null1 = 'False\n'
            ddme__axc = 'val1'
        if aeqpj__ubb:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            tyus__dbqsh = 'val2[i]'
        else:
            null2 = 'False\n'
            tyus__dbqsh = 'val2'
        if pgos__poqju:
            shvtg__mlzxy += f"""    result, isna_val = compute_or_body({null1}, {null2}, {ddme__axc}, {tyus__dbqsh})
"""
        else:
            shvtg__mlzxy += f"""    result, isna_val = compute_and_body({null1}, {null2}, {ddme__axc}, {tyus__dbqsh})
"""
        shvtg__mlzxy += '    out_arr[i] = result\n'
        shvtg__mlzxy += '    if isna_val:\n'
        shvtg__mlzxy += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        shvtg__mlzxy += '      continue\n'
        shvtg__mlzxy += '  return out_arr\n'
        lae__ehz = {}
        exec(shvtg__mlzxy, {'bodo': bodo, 'numba': numba,
            'compute_and_body': compute_and_body, 'compute_or_body':
            compute_or_body}, lae__ehz)
        impl = lae__ehz['impl']
        return impl
    return bool_array_impl


def compute_or_body(null1, null2, val1, val2):
    pass


@overload(compute_or_body)
def overload_compute_or_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == False
        elif null2:
            return val1, val1 == False
        else:
            return val1 | val2, False
    return impl


def compute_and_body(null1, null2, val1, val2):
    pass


@overload(compute_and_body)
def overload_compute_and_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == True
        elif null2:
            return val1, val1 == True
        else:
            return val1 & val2, False
    return impl


def create_boolean_array_logical_lower_impl(op):

    def logical_lower_impl(context, builder, sig, args):
        impl = create_nullable_logical_op_overload(op)(*sig.args)
        return context.compile_internal(builder, impl, sig, args)
    return logical_lower_impl


class BooleanArrayLogicalOperatorTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        if not is_valid_boolean_array_logical_op(args[0], args[1]):
            return
        cwa__xtdka = boolean_array
        return cwa__xtdka(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    edj__jlct = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return edj__jlct


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        zfeja__jypu = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(zfeja__jypu)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(zfeja__jypu)


_install_nullable_logical_lowering()
