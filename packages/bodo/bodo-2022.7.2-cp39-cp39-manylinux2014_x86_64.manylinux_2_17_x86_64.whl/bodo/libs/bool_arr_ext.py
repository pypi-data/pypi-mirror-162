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
        mylg__iby = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, mylg__iby)


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
    linej__ibru = c.context.insert_const_string(c.builder.module, 'pandas')
    pbtg__gtnx = c.pyapi.import_module_noblock(linej__ibru)
    pqpnv__vyv = c.pyapi.call_method(pbtg__gtnx, 'BooleanDtype', ())
    c.pyapi.decref(pbtg__gtnx)
    return pqpnv__vyv


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    whb__nrk = n + 7 >> 3
    return np.full(whb__nrk, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    hzu__eal = c.context.typing_context.resolve_value_type(func)
    vjqj__jbsn = hzu__eal.get_call_type(c.context.typing_context, arg_typs, {})
    dgf__ptf = c.context.get_function(hzu__eal, vjqj__jbsn)
    zamqe__kgpa = c.context.call_conv.get_function_type(vjqj__jbsn.
        return_type, vjqj__jbsn.args)
    ezo__tosr = c.builder.module
    rgwwq__wubq = lir.Function(ezo__tosr, zamqe__kgpa, name=ezo__tosr.
        get_unique_name('.func_conv'))
    rgwwq__wubq.linkage = 'internal'
    vgtrg__dbmx = lir.IRBuilder(rgwwq__wubq.append_basic_block())
    myv__aqg = c.context.call_conv.decode_arguments(vgtrg__dbmx, vjqj__jbsn
        .args, rgwwq__wubq)
    nft__ltdu = dgf__ptf(vgtrg__dbmx, myv__aqg)
    c.context.call_conv.return_value(vgtrg__dbmx, nft__ltdu)
    kjd__pbe, lyqu__zdi = c.context.call_conv.call_function(c.builder,
        rgwwq__wubq, vjqj__jbsn.return_type, vjqj__jbsn.args, args)
    return lyqu__zdi


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    hwryo__zcbh = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(hwryo__zcbh)
    c.pyapi.decref(hwryo__zcbh)
    zamqe__kgpa = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    zbdrr__sxzq = cgutils.get_or_insert_function(c.builder.module,
        zamqe__kgpa, name='is_bool_array')
    zamqe__kgpa = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    rgwwq__wubq = cgutils.get_or_insert_function(c.builder.module,
        zamqe__kgpa, name='is_pd_boolean_array')
    steb__jam = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    twxx__xnjq = c.builder.call(rgwwq__wubq, [obj])
    jcy__jqo = c.builder.icmp_unsigned('!=', twxx__xnjq, twxx__xnjq.type(0))
    with c.builder.if_else(jcy__jqo) as (wylb__nufa, irql__uwkb):
        with wylb__nufa:
            dekro__qhury = c.pyapi.object_getattr_string(obj, '_data')
            steb__jam.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), dekro__qhury).value
            afat__jjp = c.pyapi.object_getattr_string(obj, '_mask')
            utbq__iedfc = c.pyapi.to_native_value(types.Array(types.bool_, 
                1, 'C'), afat__jjp).value
            whb__nrk = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            nepn__wxp = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, utbq__iedfc)
            ryf__wedf = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [whb__nrk])
            zamqe__kgpa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            rgwwq__wubq = cgutils.get_or_insert_function(c.builder.module,
                zamqe__kgpa, name='mask_arr_to_bitmap')
            c.builder.call(rgwwq__wubq, [ryf__wedf.data, nepn__wxp.data, n])
            steb__jam.null_bitmap = ryf__wedf._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), utbq__iedfc)
            c.pyapi.decref(dekro__qhury)
            c.pyapi.decref(afat__jjp)
        with irql__uwkb:
            uoqr__uzlj = c.builder.call(zbdrr__sxzq, [obj])
            ugeny__odstr = c.builder.icmp_unsigned('!=', uoqr__uzlj,
                uoqr__uzlj.type(0))
            with c.builder.if_else(ugeny__odstr) as (kleo__fxgfl, bsp__ttkw):
                with kleo__fxgfl:
                    steb__jam.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    steb__jam.null_bitmap = call_func_in_unbox(gen_full_bitmap,
                        (n,), (types.int64,), c)
                with bsp__ttkw:
                    steb__jam.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    whb__nrk = c.builder.udiv(c.builder.add(n, lir.Constant
                        (lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8)
                        )
                    steb__jam.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [whb__nrk])._getvalue()
                    vmld__hkwu = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, steb__jam.data
                        ).data
                    qtx__mcgw = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, steb__jam.
                        null_bitmap).data
                    zamqe__kgpa = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    rgwwq__wubq = cgutils.get_or_insert_function(c.builder.
                        module, zamqe__kgpa, name='unbox_bool_array_obj')
                    c.builder.call(rgwwq__wubq, [obj, vmld__hkwu, qtx__mcgw, n]
                        )
    return NativeValue(steb__jam._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    steb__jam = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        steb__jam.data, c.env_manager)
    vgbsc__zxdpq = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, steb__jam.null_bitmap).data
    hwryo__zcbh = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(hwryo__zcbh)
    linej__ibru = c.context.insert_const_string(c.builder.module, 'numpy')
    ipcs__qaas = c.pyapi.import_module_noblock(linej__ibru)
    vgwv__tes = c.pyapi.object_getattr_string(ipcs__qaas, 'bool_')
    utbq__iedfc = c.pyapi.call_method(ipcs__qaas, 'empty', (hwryo__zcbh,
        vgwv__tes))
    cunst__anz = c.pyapi.object_getattr_string(utbq__iedfc, 'ctypes')
    znyjr__fzr = c.pyapi.object_getattr_string(cunst__anz, 'data')
    iwgf__iilw = c.builder.inttoptr(c.pyapi.long_as_longlong(znyjr__fzr),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as bjuk__jvnnh:
        knu__fiqch = bjuk__jvnnh.index
        lippb__pfbxf = c.builder.lshr(knu__fiqch, lir.Constant(lir.IntType(
            64), 3))
        gaiwh__ifbh = c.builder.load(cgutils.gep(c.builder, vgbsc__zxdpq,
            lippb__pfbxf))
        bdvmx__gto = c.builder.trunc(c.builder.and_(knu__fiqch, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(gaiwh__ifbh, bdvmx__gto), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        btzwz__dpvxj = cgutils.gep(c.builder, iwgf__iilw, knu__fiqch)
        c.builder.store(val, btzwz__dpvxj)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        steb__jam.null_bitmap)
    linej__ibru = c.context.insert_const_string(c.builder.module, 'pandas')
    pbtg__gtnx = c.pyapi.import_module_noblock(linej__ibru)
    xjp__ddy = c.pyapi.object_getattr_string(pbtg__gtnx, 'arrays')
    pqpnv__vyv = c.pyapi.call_method(xjp__ddy, 'BooleanArray', (data,
        utbq__iedfc))
    c.pyapi.decref(pbtg__gtnx)
    c.pyapi.decref(hwryo__zcbh)
    c.pyapi.decref(ipcs__qaas)
    c.pyapi.decref(vgwv__tes)
    c.pyapi.decref(cunst__anz)
    c.pyapi.decref(znyjr__fzr)
    c.pyapi.decref(xjp__ddy)
    c.pyapi.decref(data)
    c.pyapi.decref(utbq__iedfc)
    return pqpnv__vyv


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    vxksp__mqdj = np.empty(n, np.bool_)
    kybvn__nelzo = np.empty(n + 7 >> 3, np.uint8)
    for knu__fiqch, s in enumerate(pyval):
        khoj__umcn = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(kybvn__nelzo, knu__fiqch, int(
            not khoj__umcn))
        if not khoj__umcn:
            vxksp__mqdj[knu__fiqch] = s
    opdki__twsq = context.get_constant_generic(builder, data_type, vxksp__mqdj)
    njmp__nxbcq = context.get_constant_generic(builder, nulls_type,
        kybvn__nelzo)
    return lir.Constant.literal_struct([opdki__twsq, njmp__nxbcq])


def lower_init_bool_array(context, builder, signature, args):
    ydrl__mbu, lmj__rpmaj = args
    steb__jam = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    steb__jam.data = ydrl__mbu
    steb__jam.null_bitmap = lmj__rpmaj
    context.nrt.incref(builder, signature.args[0], ydrl__mbu)
    context.nrt.incref(builder, signature.args[1], lmj__rpmaj)
    return steb__jam._getvalue()


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
    ghmyw__ite = args[0]
    if equiv_set.has_shape(ghmyw__ite):
        return ArrayAnalysis.AnalyzeResult(shape=ghmyw__ite, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ghmyw__ite = args[0]
    if equiv_set.has_shape(ghmyw__ite):
        return ArrayAnalysis.AnalyzeResult(shape=ghmyw__ite, pre=[])
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
    vxksp__mqdj = np.empty(n, dtype=np.bool_)
    ahwn__exkp = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(vxksp__mqdj, ahwn__exkp)


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
            agrq__trh, ecf__luncu = array_getitem_bool_index(A, ind)
            return init_bool_array(agrq__trh, ecf__luncu)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            agrq__trh, ecf__luncu = array_getitem_int_index(A, ind)
            return init_bool_array(agrq__trh, ecf__luncu)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            agrq__trh, ecf__luncu = array_getitem_slice_index(A, ind)
            return init_bool_array(agrq__trh, ecf__luncu)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    dvy__ppdbk = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(dvy__ppdbk)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(dvy__ppdbk)
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
        for knu__fiqch in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, knu__fiqch):
                val = A[knu__fiqch]
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
            npsl__vca = np.empty(n, nb_dtype)
            for knu__fiqch in numba.parfors.parfor.internal_prange(n):
                npsl__vca[knu__fiqch] = data[knu__fiqch]
                if bodo.libs.array_kernels.isna(A, knu__fiqch):
                    npsl__vca[knu__fiqch] = np.nan
            return npsl__vca
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        npsl__vca = np.empty(n, dtype=np.bool_)
        for knu__fiqch in numba.parfors.parfor.internal_prange(n):
            npsl__vca[knu__fiqch] = data[knu__fiqch]
            if bodo.libs.array_kernels.isna(A, knu__fiqch):
                npsl__vca[knu__fiqch] = value
        return npsl__vca
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
    djy__jmwxm = op.__name__
    djy__jmwxm = ufunc_aliases.get(djy__jmwxm, djy__jmwxm)
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
    for bpr__qnq in numba.np.ufunc_db.get_ufuncs():
        frqow__wpg = create_op_overload(bpr__qnq, bpr__qnq.nin)
        overload(bpr__qnq, no_unliteral=True)(frqow__wpg)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        frqow__wpg = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(frqow__wpg)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        frqow__wpg = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(frqow__wpg)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        frqow__wpg = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(frqow__wpg)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        bdvmx__gto = []
        hqaq__gbn = False
        iwauf__rmjz = False
        aplvc__xni = False
        for knu__fiqch in range(len(A)):
            if bodo.libs.array_kernels.isna(A, knu__fiqch):
                if not hqaq__gbn:
                    data.append(False)
                    bdvmx__gto.append(False)
                    hqaq__gbn = True
                continue
            val = A[knu__fiqch]
            if val and not iwauf__rmjz:
                data.append(True)
                bdvmx__gto.append(True)
                iwauf__rmjz = True
            if not val and not aplvc__xni:
                data.append(False)
                bdvmx__gto.append(True)
                aplvc__xni = True
            if hqaq__gbn and iwauf__rmjz and aplvc__xni:
                break
        agrq__trh = np.array(data)
        n = len(agrq__trh)
        whb__nrk = 1
        ecf__luncu = np.empty(whb__nrk, np.uint8)
        for big__gnq in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(ecf__luncu, big__gnq,
                bdvmx__gto[big__gnq])
        return init_bool_array(agrq__trh, ecf__luncu)
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
    pqpnv__vyv = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, pqpnv__vyv)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    nkt__dacxe = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        cgk__pffz = bodo.utils.utils.is_array_typ(val1, False)
        ywx__qdpk = bodo.utils.utils.is_array_typ(val2, False)
        joaen__kzais = 'val1' if cgk__pffz else 'val2'
        nvj__xjek = 'def impl(val1, val2):\n'
        nvj__xjek += f'  n = len({joaen__kzais})\n'
        nvj__xjek += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        nvj__xjek += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if cgk__pffz:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            tzecb__smkzu = 'val1[i]'
        else:
            null1 = 'False\n'
            tzecb__smkzu = 'val1'
        if ywx__qdpk:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            wmayq__wrztu = 'val2[i]'
        else:
            null2 = 'False\n'
            wmayq__wrztu = 'val2'
        if nkt__dacxe:
            nvj__xjek += f"""    result, isna_val = compute_or_body({null1}, {null2}, {tzecb__smkzu}, {wmayq__wrztu})
"""
        else:
            nvj__xjek += f"""    result, isna_val = compute_and_body({null1}, {null2}, {tzecb__smkzu}, {wmayq__wrztu})
"""
        nvj__xjek += '    out_arr[i] = result\n'
        nvj__xjek += '    if isna_val:\n'
        nvj__xjek += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        nvj__xjek += '      continue\n'
        nvj__xjek += '  return out_arr\n'
        xqgyn__lszzm = {}
        exec(nvj__xjek, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, xqgyn__lszzm
            )
        impl = xqgyn__lszzm['impl']
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
        pzfv__wcp = boolean_array
        return pzfv__wcp(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    xyse__ehp = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return xyse__ehp


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        uafla__hfs = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(uafla__hfs)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(uafla__hfs)


_install_nullable_logical_lowering()
