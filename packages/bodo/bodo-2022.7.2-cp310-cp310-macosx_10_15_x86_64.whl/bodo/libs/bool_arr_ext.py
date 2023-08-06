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
        xkbg__oitu = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, xkbg__oitu)


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
    spy__yki = c.context.insert_const_string(c.builder.module, 'pandas')
    kdh__iywhp = c.pyapi.import_module_noblock(spy__yki)
    vkr__yqfn = c.pyapi.call_method(kdh__iywhp, 'BooleanDtype', ())
    c.pyapi.decref(kdh__iywhp)
    return vkr__yqfn


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    cyzle__xuzih = n + 7 >> 3
    return np.full(cyzle__xuzih, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    migrl__lpz = c.context.typing_context.resolve_value_type(func)
    dezr__nafcs = migrl__lpz.get_call_type(c.context.typing_context,
        arg_typs, {})
    avjhw__jenh = c.context.get_function(migrl__lpz, dezr__nafcs)
    tnj__avdw = c.context.call_conv.get_function_type(dezr__nafcs.
        return_type, dezr__nafcs.args)
    wdkj__tfnqk = c.builder.module
    keaj__nzd = lir.Function(wdkj__tfnqk, tnj__avdw, name=wdkj__tfnqk.
        get_unique_name('.func_conv'))
    keaj__nzd.linkage = 'internal'
    yzlk__pgnv = lir.IRBuilder(keaj__nzd.append_basic_block())
    lon__bghc = c.context.call_conv.decode_arguments(yzlk__pgnv,
        dezr__nafcs.args, keaj__nzd)
    tvk__xtwsp = avjhw__jenh(yzlk__pgnv, lon__bghc)
    c.context.call_conv.return_value(yzlk__pgnv, tvk__xtwsp)
    lkt__tdiwl, isqlq__qkvqi = c.context.call_conv.call_function(c.builder,
        keaj__nzd, dezr__nafcs.return_type, dezr__nafcs.args, args)
    return isqlq__qkvqi


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    svqls__bhr = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(svqls__bhr)
    c.pyapi.decref(svqls__bhr)
    tnj__avdw = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    tycn__wimhc = cgutils.get_or_insert_function(c.builder.module,
        tnj__avdw, name='is_bool_array')
    tnj__avdw = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    keaj__nzd = cgutils.get_or_insert_function(c.builder.module, tnj__avdw,
        name='is_pd_boolean_array')
    sfivr__oqu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xtmyt__tjcgu = c.builder.call(keaj__nzd, [obj])
    uqqzt__kqs = c.builder.icmp_unsigned('!=', xtmyt__tjcgu, xtmyt__tjcgu.
        type(0))
    with c.builder.if_else(uqqzt__kqs) as (fusb__nboub, szp__aalg):
        with fusb__nboub:
            lhf__fwjv = c.pyapi.object_getattr_string(obj, '_data')
            sfivr__oqu.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), lhf__fwjv).value
            kbroz__rrtuc = c.pyapi.object_getattr_string(obj, '_mask')
            fkbk__jprro = c.pyapi.to_native_value(types.Array(types.bool_, 
                1, 'C'), kbroz__rrtuc).value
            cyzle__xuzih = c.builder.udiv(c.builder.add(n, lir.Constant(lir
                .IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            ctd__cfg = c.context.make_array(types.Array(types.bool_, 1, 'C'))(c
                .context, c.builder, fkbk__jprro)
            fxj__wpsgx = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [cyzle__xuzih])
            tnj__avdw = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            keaj__nzd = cgutils.get_or_insert_function(c.builder.module,
                tnj__avdw, name='mask_arr_to_bitmap')
            c.builder.call(keaj__nzd, [fxj__wpsgx.data, ctd__cfg.data, n])
            sfivr__oqu.null_bitmap = fxj__wpsgx._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), fkbk__jprro)
            c.pyapi.decref(lhf__fwjv)
            c.pyapi.decref(kbroz__rrtuc)
        with szp__aalg:
            ffo__hgee = c.builder.call(tycn__wimhc, [obj])
            iobj__gxiq = c.builder.icmp_unsigned('!=', ffo__hgee, ffo__hgee
                .type(0))
            with c.builder.if_else(iobj__gxiq) as (fypyw__yqjz, ret__ysxnq):
                with fypyw__yqjz:
                    sfivr__oqu.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    sfivr__oqu.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with ret__ysxnq:
                    sfivr__oqu.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    cyzle__xuzih = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    sfivr__oqu.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [cyzle__xuzih])._getvalue()
                    qlqkh__qeip = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, sfivr__oqu.data
                        ).data
                    epnat__mqq = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, sfivr__oqu.
                        null_bitmap).data
                    tnj__avdw = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    keaj__nzd = cgutils.get_or_insert_function(c.builder.
                        module, tnj__avdw, name='unbox_bool_array_obj')
                    c.builder.call(keaj__nzd, [obj, qlqkh__qeip, epnat__mqq, n]
                        )
    return NativeValue(sfivr__oqu._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    sfivr__oqu = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        sfivr__oqu.data, c.env_manager)
    tjcyb__tqs = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, sfivr__oqu.null_bitmap).data
    svqls__bhr = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(svqls__bhr)
    spy__yki = c.context.insert_const_string(c.builder.module, 'numpy')
    mcl__pqow = c.pyapi.import_module_noblock(spy__yki)
    myjgn__kjyb = c.pyapi.object_getattr_string(mcl__pqow, 'bool_')
    fkbk__jprro = c.pyapi.call_method(mcl__pqow, 'empty', (svqls__bhr,
        myjgn__kjyb))
    wicj__lhmlz = c.pyapi.object_getattr_string(fkbk__jprro, 'ctypes')
    phhnt__eiev = c.pyapi.object_getattr_string(wicj__lhmlz, 'data')
    ocfz__xae = c.builder.inttoptr(c.pyapi.long_as_longlong(phhnt__eiev),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as ubz__imupx:
        lsgyu__shbl = ubz__imupx.index
        fyp__ofvl = c.builder.lshr(lsgyu__shbl, lir.Constant(lir.IntType(64
            ), 3))
        ptwg__evk = c.builder.load(cgutils.gep(c.builder, tjcyb__tqs,
            fyp__ofvl))
        memf__ourl = c.builder.trunc(c.builder.and_(lsgyu__shbl, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(ptwg__evk, memf__ourl), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        iyvas__mechn = cgutils.gep(c.builder, ocfz__xae, lsgyu__shbl)
        c.builder.store(val, iyvas__mechn)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        sfivr__oqu.null_bitmap)
    spy__yki = c.context.insert_const_string(c.builder.module, 'pandas')
    kdh__iywhp = c.pyapi.import_module_noblock(spy__yki)
    pti__bde = c.pyapi.object_getattr_string(kdh__iywhp, 'arrays')
    vkr__yqfn = c.pyapi.call_method(pti__bde, 'BooleanArray', (data,
        fkbk__jprro))
    c.pyapi.decref(kdh__iywhp)
    c.pyapi.decref(svqls__bhr)
    c.pyapi.decref(mcl__pqow)
    c.pyapi.decref(myjgn__kjyb)
    c.pyapi.decref(wicj__lhmlz)
    c.pyapi.decref(phhnt__eiev)
    c.pyapi.decref(pti__bde)
    c.pyapi.decref(data)
    c.pyapi.decref(fkbk__jprro)
    return vkr__yqfn


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    hbae__coxxe = np.empty(n, np.bool_)
    gopvx__xhd = np.empty(n + 7 >> 3, np.uint8)
    for lsgyu__shbl, s in enumerate(pyval):
        gldjh__aycgp = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(gopvx__xhd, lsgyu__shbl, int(
            not gldjh__aycgp))
        if not gldjh__aycgp:
            hbae__coxxe[lsgyu__shbl] = s
    lozr__awbx = context.get_constant_generic(builder, data_type, hbae__coxxe)
    jqujy__vwf = context.get_constant_generic(builder, nulls_type, gopvx__xhd)
    return lir.Constant.literal_struct([lozr__awbx, jqujy__vwf])


def lower_init_bool_array(context, builder, signature, args):
    lktw__itbk, bgnbm__qmeb = args
    sfivr__oqu = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    sfivr__oqu.data = lktw__itbk
    sfivr__oqu.null_bitmap = bgnbm__qmeb
    context.nrt.incref(builder, signature.args[0], lktw__itbk)
    context.nrt.incref(builder, signature.args[1], bgnbm__qmeb)
    return sfivr__oqu._getvalue()


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
    tuj__aer = args[0]
    if equiv_set.has_shape(tuj__aer):
        return ArrayAnalysis.AnalyzeResult(shape=tuj__aer, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    tuj__aer = args[0]
    if equiv_set.has_shape(tuj__aer):
        return ArrayAnalysis.AnalyzeResult(shape=tuj__aer, pre=[])
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
    hbae__coxxe = np.empty(n, dtype=np.bool_)
    lad__wwxm = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(hbae__coxxe, lad__wwxm)


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
            pxclg__nona, aqpk__aty = array_getitem_bool_index(A, ind)
            return init_bool_array(pxclg__nona, aqpk__aty)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            pxclg__nona, aqpk__aty = array_getitem_int_index(A, ind)
            return init_bool_array(pxclg__nona, aqpk__aty)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            pxclg__nona, aqpk__aty = array_getitem_slice_index(A, ind)
            return init_bool_array(pxclg__nona, aqpk__aty)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    isas__hnuna = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(isas__hnuna)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(isas__hnuna)
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
        for lsgyu__shbl in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, lsgyu__shbl):
                val = A[lsgyu__shbl]
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
            zcmqa__yjm = np.empty(n, nb_dtype)
            for lsgyu__shbl in numba.parfors.parfor.internal_prange(n):
                zcmqa__yjm[lsgyu__shbl] = data[lsgyu__shbl]
                if bodo.libs.array_kernels.isna(A, lsgyu__shbl):
                    zcmqa__yjm[lsgyu__shbl] = np.nan
            return zcmqa__yjm
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        zcmqa__yjm = np.empty(n, dtype=np.bool_)
        for lsgyu__shbl in numba.parfors.parfor.internal_prange(n):
            zcmqa__yjm[lsgyu__shbl] = data[lsgyu__shbl]
            if bodo.libs.array_kernels.isna(A, lsgyu__shbl):
                zcmqa__yjm[lsgyu__shbl] = value
        return zcmqa__yjm
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
    sqdf__ibh = op.__name__
    sqdf__ibh = ufunc_aliases.get(sqdf__ibh, sqdf__ibh)
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
    for ulm__pxwm in numba.np.ufunc_db.get_ufuncs():
        vrcj__ajwn = create_op_overload(ulm__pxwm, ulm__pxwm.nin)
        overload(ulm__pxwm, no_unliteral=True)(vrcj__ajwn)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        vrcj__ajwn = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vrcj__ajwn)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        vrcj__ajwn = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vrcj__ajwn)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        vrcj__ajwn = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(vrcj__ajwn)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        memf__ourl = []
        bkmc__wfv = False
        otuzx__zzjs = False
        yms__eprnn = False
        for lsgyu__shbl in range(len(A)):
            if bodo.libs.array_kernels.isna(A, lsgyu__shbl):
                if not bkmc__wfv:
                    data.append(False)
                    memf__ourl.append(False)
                    bkmc__wfv = True
                continue
            val = A[lsgyu__shbl]
            if val and not otuzx__zzjs:
                data.append(True)
                memf__ourl.append(True)
                otuzx__zzjs = True
            if not val and not yms__eprnn:
                data.append(False)
                memf__ourl.append(True)
                yms__eprnn = True
            if bkmc__wfv and otuzx__zzjs and yms__eprnn:
                break
        pxclg__nona = np.array(data)
        n = len(pxclg__nona)
        cyzle__xuzih = 1
        aqpk__aty = np.empty(cyzle__xuzih, np.uint8)
        for owg__czhzj in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(aqpk__aty, owg__czhzj,
                memf__ourl[owg__czhzj])
        return init_bool_array(pxclg__nona, aqpk__aty)
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
    vkr__yqfn = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, vkr__yqfn)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    pgw__aqh = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        ysx__pnvki = bodo.utils.utils.is_array_typ(val1, False)
        knij__lbeof = bodo.utils.utils.is_array_typ(val2, False)
        jxtyq__kqpo = 'val1' if ysx__pnvki else 'val2'
        vkcs__izdjn = 'def impl(val1, val2):\n'
        vkcs__izdjn += f'  n = len({jxtyq__kqpo})\n'
        vkcs__izdjn += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        vkcs__izdjn += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if ysx__pnvki:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            ojqgg__szf = 'val1[i]'
        else:
            null1 = 'False\n'
            ojqgg__szf = 'val1'
        if knij__lbeof:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            uqc__vtn = 'val2[i]'
        else:
            null2 = 'False\n'
            uqc__vtn = 'val2'
        if pgw__aqh:
            vkcs__izdjn += f"""    result, isna_val = compute_or_body({null1}, {null2}, {ojqgg__szf}, {uqc__vtn})
"""
        else:
            vkcs__izdjn += f"""    result, isna_val = compute_and_body({null1}, {null2}, {ojqgg__szf}, {uqc__vtn})
"""
        vkcs__izdjn += '    out_arr[i] = result\n'
        vkcs__izdjn += '    if isna_val:\n'
        vkcs__izdjn += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        vkcs__izdjn += '      continue\n'
        vkcs__izdjn += '  return out_arr\n'
        irytq__amj = {}
        exec(vkcs__izdjn, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, irytq__amj)
        impl = irytq__amj['impl']
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
        nvkme__dbsl = boolean_array
        return nvkme__dbsl(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    mvzk__hcmg = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return mvzk__hcmg


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        refmk__uivtr = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(refmk__uivtr)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(refmk__uivtr)


_install_nullable_logical_lowering()
