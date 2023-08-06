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
        zslbf__erx = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, zslbf__erx)


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
    lechj__pda = c.context.insert_const_string(c.builder.module, 'pandas')
    pbjom__amig = c.pyapi.import_module_noblock(lechj__pda)
    wnbr__ksxrx = c.pyapi.call_method(pbjom__amig, 'BooleanDtype', ())
    c.pyapi.decref(pbjom__amig)
    return wnbr__ksxrx


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    prnxp__sgyn = n + 7 >> 3
    return np.full(prnxp__sgyn, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    xqu__ssiyo = c.context.typing_context.resolve_value_type(func)
    suy__nojdh = xqu__ssiyo.get_call_type(c.context.typing_context,
        arg_typs, {})
    yeoso__qzgef = c.context.get_function(xqu__ssiyo, suy__nojdh)
    mkcn__ynob = c.context.call_conv.get_function_type(suy__nojdh.
        return_type, suy__nojdh.args)
    hqfzs__zlx = c.builder.module
    kkmoy__kwh = lir.Function(hqfzs__zlx, mkcn__ynob, name=hqfzs__zlx.
        get_unique_name('.func_conv'))
    kkmoy__kwh.linkage = 'internal'
    ynj__salcl = lir.IRBuilder(kkmoy__kwh.append_basic_block())
    qql__akof = c.context.call_conv.decode_arguments(ynj__salcl, suy__nojdh
        .args, kkmoy__kwh)
    ayc__cgeo = yeoso__qzgef(ynj__salcl, qql__akof)
    c.context.call_conv.return_value(ynj__salcl, ayc__cgeo)
    aotfm__pbagt, setn__hit = c.context.call_conv.call_function(c.builder,
        kkmoy__kwh, suy__nojdh.return_type, suy__nojdh.args, args)
    return setn__hit


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    fikac__vmzm = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(fikac__vmzm)
    c.pyapi.decref(fikac__vmzm)
    mkcn__ynob = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    gqyz__qgdyd = cgutils.get_or_insert_function(c.builder.module,
        mkcn__ynob, name='is_bool_array')
    mkcn__ynob = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    kkmoy__kwh = cgutils.get_or_insert_function(c.builder.module,
        mkcn__ynob, name='is_pd_boolean_array')
    vqjy__eme = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ikoen__asmsj = c.builder.call(kkmoy__kwh, [obj])
    cnys__yup = c.builder.icmp_unsigned('!=', ikoen__asmsj, ikoen__asmsj.
        type(0))
    with c.builder.if_else(cnys__yup) as (qpy__wmmlj, kyog__hng):
        with qpy__wmmlj:
            bnreh__rddrm = c.pyapi.object_getattr_string(obj, '_data')
            vqjy__eme.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), bnreh__rddrm).value
            edhef__icpap = c.pyapi.object_getattr_string(obj, '_mask')
            vpxqy__usn = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), edhef__icpap).value
            prnxp__sgyn = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            hyra__gpaj = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, vpxqy__usn)
            mry__iiy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
                types.Array(types.uint8, 1, 'C'), [prnxp__sgyn])
            mkcn__ynob = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            kkmoy__kwh = cgutils.get_or_insert_function(c.builder.module,
                mkcn__ynob, name='mask_arr_to_bitmap')
            c.builder.call(kkmoy__kwh, [mry__iiy.data, hyra__gpaj.data, n])
            vqjy__eme.null_bitmap = mry__iiy._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), vpxqy__usn)
            c.pyapi.decref(bnreh__rddrm)
            c.pyapi.decref(edhef__icpap)
        with kyog__hng:
            eilfo__pqu = c.builder.call(gqyz__qgdyd, [obj])
            dfvl__ozdhp = c.builder.icmp_unsigned('!=', eilfo__pqu,
                eilfo__pqu.type(0))
            with c.builder.if_else(dfvl__ozdhp) as (unbom__lzimg, prcz__clqs):
                with unbom__lzimg:
                    vqjy__eme.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    vqjy__eme.null_bitmap = call_func_in_unbox(gen_full_bitmap,
                        (n,), (types.int64,), c)
                with prcz__clqs:
                    vqjy__eme.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    prnxp__sgyn = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    vqjy__eme.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [prnxp__sgyn])._getvalue()
                    gxvjg__ryae = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, vqjy__eme.data
                        ).data
                    wvyf__gnoz = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, vqjy__eme.
                        null_bitmap).data
                    mkcn__ynob = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    kkmoy__kwh = cgutils.get_or_insert_function(c.builder.
                        module, mkcn__ynob, name='unbox_bool_array_obj')
                    c.builder.call(kkmoy__kwh, [obj, gxvjg__ryae,
                        wvyf__gnoz, n])
    return NativeValue(vqjy__eme._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    vqjy__eme = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        vqjy__eme.data, c.env_manager)
    auts__ygj = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, vqjy__eme.null_bitmap).data
    fikac__vmzm = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(fikac__vmzm)
    lechj__pda = c.context.insert_const_string(c.builder.module, 'numpy')
    pid__nkfpp = c.pyapi.import_module_noblock(lechj__pda)
    xwtq__peh = c.pyapi.object_getattr_string(pid__nkfpp, 'bool_')
    vpxqy__usn = c.pyapi.call_method(pid__nkfpp, 'empty', (fikac__vmzm,
        xwtq__peh))
    ess__hclwa = c.pyapi.object_getattr_string(vpxqy__usn, 'ctypes')
    xrb__tjo = c.pyapi.object_getattr_string(ess__hclwa, 'data')
    fiub__czxl = c.builder.inttoptr(c.pyapi.long_as_longlong(xrb__tjo), lir
        .IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as jkuuw__uti:
        zda__pnrc = jkuuw__uti.index
        qdwsv__pcwyl = c.builder.lshr(zda__pnrc, lir.Constant(lir.IntType(
            64), 3))
        jefqv__quhca = c.builder.load(cgutils.gep(c.builder, auts__ygj,
            qdwsv__pcwyl))
        rxjqd__zsj = c.builder.trunc(c.builder.and_(zda__pnrc, lir.Constant
            (lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(jefqv__quhca, rxjqd__zsj), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        vresg__gwqb = cgutils.gep(c.builder, fiub__czxl, zda__pnrc)
        c.builder.store(val, vresg__gwqb)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        vqjy__eme.null_bitmap)
    lechj__pda = c.context.insert_const_string(c.builder.module, 'pandas')
    pbjom__amig = c.pyapi.import_module_noblock(lechj__pda)
    hjuo__rtnz = c.pyapi.object_getattr_string(pbjom__amig, 'arrays')
    wnbr__ksxrx = c.pyapi.call_method(hjuo__rtnz, 'BooleanArray', (data,
        vpxqy__usn))
    c.pyapi.decref(pbjom__amig)
    c.pyapi.decref(fikac__vmzm)
    c.pyapi.decref(pid__nkfpp)
    c.pyapi.decref(xwtq__peh)
    c.pyapi.decref(ess__hclwa)
    c.pyapi.decref(xrb__tjo)
    c.pyapi.decref(hjuo__rtnz)
    c.pyapi.decref(data)
    c.pyapi.decref(vpxqy__usn)
    return wnbr__ksxrx


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    dmnld__xyl = np.empty(n, np.bool_)
    uorw__ktmwi = np.empty(n + 7 >> 3, np.uint8)
    for zda__pnrc, s in enumerate(pyval):
        yqpzh__xdjvk = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(uorw__ktmwi, zda__pnrc, int(
            not yqpzh__xdjvk))
        if not yqpzh__xdjvk:
            dmnld__xyl[zda__pnrc] = s
    rir__tzfd = context.get_constant_generic(builder, data_type, dmnld__xyl)
    khkvw__aqxma = context.get_constant_generic(builder, nulls_type,
        uorw__ktmwi)
    return lir.Constant.literal_struct([rir__tzfd, khkvw__aqxma])


def lower_init_bool_array(context, builder, signature, args):
    jji__whh, gon__mwal = args
    vqjy__eme = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    vqjy__eme.data = jji__whh
    vqjy__eme.null_bitmap = gon__mwal
    context.nrt.incref(builder, signature.args[0], jji__whh)
    context.nrt.incref(builder, signature.args[1], gon__mwal)
    return vqjy__eme._getvalue()


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
    gvgp__lnfe = args[0]
    if equiv_set.has_shape(gvgp__lnfe):
        return ArrayAnalysis.AnalyzeResult(shape=gvgp__lnfe, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    gvgp__lnfe = args[0]
    if equiv_set.has_shape(gvgp__lnfe):
        return ArrayAnalysis.AnalyzeResult(shape=gvgp__lnfe, pre=[])
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
    dmnld__xyl = np.empty(n, dtype=np.bool_)
    rqjk__fbzl = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(dmnld__xyl, rqjk__fbzl)


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
            rpk__mluai, arj__wym = array_getitem_bool_index(A, ind)
            return init_bool_array(rpk__mluai, arj__wym)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            rpk__mluai, arj__wym = array_getitem_int_index(A, ind)
            return init_bool_array(rpk__mluai, arj__wym)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            rpk__mluai, arj__wym = array_getitem_slice_index(A, ind)
            return init_bool_array(rpk__mluai, arj__wym)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    wjz__ded = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(wjz__ded)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(wjz__ded)
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
        for zda__pnrc in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, zda__pnrc):
                val = A[zda__pnrc]
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
            ivl__qnuf = np.empty(n, nb_dtype)
            for zda__pnrc in numba.parfors.parfor.internal_prange(n):
                ivl__qnuf[zda__pnrc] = data[zda__pnrc]
                if bodo.libs.array_kernels.isna(A, zda__pnrc):
                    ivl__qnuf[zda__pnrc] = np.nan
            return ivl__qnuf
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        ivl__qnuf = np.empty(n, dtype=np.bool_)
        for zda__pnrc in numba.parfors.parfor.internal_prange(n):
            ivl__qnuf[zda__pnrc] = data[zda__pnrc]
            if bodo.libs.array_kernels.isna(A, zda__pnrc):
                ivl__qnuf[zda__pnrc] = value
        return ivl__qnuf
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
    zsu__yrdj = op.__name__
    zsu__yrdj = ufunc_aliases.get(zsu__yrdj, zsu__yrdj)
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
    for nymm__aqeod in numba.np.ufunc_db.get_ufuncs():
        mctc__yrxou = create_op_overload(nymm__aqeod, nymm__aqeod.nin)
        overload(nymm__aqeod, no_unliteral=True)(mctc__yrxou)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        mctc__yrxou = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(mctc__yrxou)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        mctc__yrxou = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(mctc__yrxou)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        mctc__yrxou = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(mctc__yrxou)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        rxjqd__zsj = []
        gysm__brbk = False
        evc__hrrch = False
        uha__geq = False
        for zda__pnrc in range(len(A)):
            if bodo.libs.array_kernels.isna(A, zda__pnrc):
                if not gysm__brbk:
                    data.append(False)
                    rxjqd__zsj.append(False)
                    gysm__brbk = True
                continue
            val = A[zda__pnrc]
            if val and not evc__hrrch:
                data.append(True)
                rxjqd__zsj.append(True)
                evc__hrrch = True
            if not val and not uha__geq:
                data.append(False)
                rxjqd__zsj.append(True)
                uha__geq = True
            if gysm__brbk and evc__hrrch and uha__geq:
                break
        rpk__mluai = np.array(data)
        n = len(rpk__mluai)
        prnxp__sgyn = 1
        arj__wym = np.empty(prnxp__sgyn, np.uint8)
        for bsu__byaoa in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(arj__wym, bsu__byaoa,
                rxjqd__zsj[bsu__byaoa])
        return init_bool_array(rpk__mluai, arj__wym)
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
    wnbr__ksxrx = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, wnbr__ksxrx)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    updvq__fqja = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        xrcmw__kfevm = bodo.utils.utils.is_array_typ(val1, False)
        pljs__brak = bodo.utils.utils.is_array_typ(val2, False)
        kmh__imzhr = 'val1' if xrcmw__kfevm else 'val2'
        piboi__xjw = 'def impl(val1, val2):\n'
        piboi__xjw += f'  n = len({kmh__imzhr})\n'
        piboi__xjw += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        piboi__xjw += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if xrcmw__kfevm:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            ktwq__gkexz = 'val1[i]'
        else:
            null1 = 'False\n'
            ktwq__gkexz = 'val1'
        if pljs__brak:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            snaxt__qkkzv = 'val2[i]'
        else:
            null2 = 'False\n'
            snaxt__qkkzv = 'val2'
        if updvq__fqja:
            piboi__xjw += f"""    result, isna_val = compute_or_body({null1}, {null2}, {ktwq__gkexz}, {snaxt__qkkzv})
"""
        else:
            piboi__xjw += f"""    result, isna_val = compute_and_body({null1}, {null2}, {ktwq__gkexz}, {snaxt__qkkzv})
"""
        piboi__xjw += '    out_arr[i] = result\n'
        piboi__xjw += '    if isna_val:\n'
        piboi__xjw += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        piboi__xjw += '      continue\n'
        piboi__xjw += '  return out_arr\n'
        efy__iqid = {}
        exec(piboi__xjw, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, efy__iqid)
        impl = efy__iqid['impl']
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
        fbv__nghaz = boolean_array
        return fbv__nghaz(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    ubih__qsbnq = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return ubih__qsbnq


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        fmtno__zwfve = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(fmtno__zwfve)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(fmtno__zwfve)


_install_nullable_logical_lowering()
