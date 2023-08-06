import enum
import operator
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.utils.typing import NOT_CONSTANT, BodoError, MetaType, check_unsupported_args, dtype_to_array_type, get_literal_value, get_overload_const, get_overload_const_bool, is_common_scalar_dtype, is_iterable_type, is_list_like_index_type, is_literal_type, is_overload_constant_bool, is_overload_none, is_overload_true, is_scalar_type, raise_bodo_error


class PDCategoricalDtype(types.Opaque):

    def __init__(self, categories, elem_type, ordered, data=None, int_type=None
        ):
        self.categories = categories
        self.elem_type = elem_type
        self.ordered = ordered
        self.data = _get_cat_index_type(elem_type) if data is None else data
        self.int_type = int_type
        hfoa__toxz = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=hfoa__toxz)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    kqx__xdh = tuple(val.categories.values)
    elem_type = None if len(kqx__xdh) == 0 else bodo.typeof(val.categories.
        values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(kqx__xdh, elem_type, val.ordered, bodo.typeof
        (val.categories), int_type)


def _get_cat_index_type(elem_type):
    elem_type = bodo.string_type if elem_type is None else elem_type
    return bodo.utils.typing.get_index_type_from_dtype(elem_type)


@lower_constant(PDCategoricalDtype)
def lower_constant_categorical_type(context, builder, typ, pyval):
    categories = context.get_constant_generic(builder, bodo.typeof(pyval.
        categories), pyval.categories)
    ordered = context.get_constant(types.bool_, pyval.ordered)
    return lir.Constant.literal_struct([categories, ordered])


@register_model(PDCategoricalDtype)
class PDCategoricalDtypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fixl__neiv = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, fixl__neiv)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    ccrx__ojt = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    tye__woj = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, xsz__ealwc, xsz__ealwc = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    rqjj__iqjk = PDCategoricalDtype(tye__woj, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, ccrx__ojt)
    return rqjj__iqjk(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    eurya__tval = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, eurya__tval).value
    c.pyapi.decref(eurya__tval)
    plfvc__etop = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, plfvc__etop).value
    c.pyapi.decref(plfvc__etop)
    oow__xzpto = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=oow__xzpto)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    eurya__tval = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    six__vkb = c.pyapi.from_native_value(typ.data, cat_dtype.categories, c.
        env_manager)
    byp__zsfn = c.context.insert_const_string(c.builder.module, 'pandas')
    pgvt__tqld = c.pyapi.import_module_noblock(byp__zsfn)
    pxgpk__bzzaj = c.pyapi.call_method(pgvt__tqld, 'CategoricalDtype', (
        six__vkb, eurya__tval))
    c.pyapi.decref(eurya__tval)
    c.pyapi.decref(six__vkb)
    c.pyapi.decref(pgvt__tqld)
    c.context.nrt.decref(c.builder, typ, val)
    return pxgpk__bzzaj


@overload_attribute(PDCategoricalDtype, 'nbytes')
def pd_categorical_nbytes_overload(A):
    return lambda A: A.categories.nbytes + bodo.io.np_io.get_dtype_size(types
        .bool_)


class CategoricalArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(CategoricalArrayType, self).__init__(name=
            f'CategoricalArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return CategoricalArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.Categorical)
def _typeof_pd_cat(val, c):
    return CategoricalArrayType(bodo.typeof(val.dtype))


@register_model(CategoricalArrayType)
class CategoricalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mkm__laog = get_categories_int_type(fe_type.dtype)
        fixl__neiv = [('dtype', fe_type.dtype), ('codes', types.Array(
            mkm__laog, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, fixl__neiv)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    ual__xiqt = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), ual__xiqt
        ).value
    c.pyapi.decref(ual__xiqt)
    pxgpk__bzzaj = c.pyapi.object_getattr_string(val, 'dtype')
    awo__jaxg = c.pyapi.to_native_value(typ.dtype, pxgpk__bzzaj).value
    c.pyapi.decref(pxgpk__bzzaj)
    agf__nzzv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    agf__nzzv.codes = codes
    agf__nzzv.dtype = awo__jaxg
    return NativeValue(agf__nzzv._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    vpo__qxrty = get_categories_int_type(typ.dtype)
    jpgxs__mnpcn = context.get_constant_generic(builder, types.Array(
        vpo__qxrty, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, jpgxs__mnpcn])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    bebqo__zdam = len(cat_dtype.categories)
    if bebqo__zdam < np.iinfo(np.int8).max:
        dtype = types.int8
    elif bebqo__zdam < np.iinfo(np.int16).max:
        dtype = types.int16
    elif bebqo__zdam < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    byp__zsfn = c.context.insert_const_string(c.builder.module, 'pandas')
    pgvt__tqld = c.pyapi.import_module_noblock(byp__zsfn)
    mkm__laog = get_categories_int_type(dtype)
    uxh__ajrb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    zgn__xird = types.Array(mkm__laog, 1, 'C')
    c.context.nrt.incref(c.builder, zgn__xird, uxh__ajrb.codes)
    ual__xiqt = c.pyapi.from_native_value(zgn__xird, uxh__ajrb.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, uxh__ajrb.dtype)
    pxgpk__bzzaj = c.pyapi.from_native_value(dtype, uxh__ajrb.dtype, c.
        env_manager)
    eoe__cqd = c.pyapi.borrow_none()
    dmap__cupaz = c.pyapi.object_getattr_string(pgvt__tqld, 'Categorical')
    mdo__qgibu = c.pyapi.call_method(dmap__cupaz, 'from_codes', (ual__xiqt,
        eoe__cqd, eoe__cqd, pxgpk__bzzaj))
    c.pyapi.decref(dmap__cupaz)
    c.pyapi.decref(ual__xiqt)
    c.pyapi.decref(pxgpk__bzzaj)
    c.pyapi.decref(pgvt__tqld)
    c.context.nrt.decref(c.builder, typ, val)
    return mdo__qgibu


def _to_readonly(t):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, TimedeltaIndexType
    if isinstance(t, CategoricalArrayType):
        return CategoricalArrayType(_to_readonly(t.dtype))
    if isinstance(t, PDCategoricalDtype):
        return PDCategoricalDtype(t.categories, t.elem_type, t.ordered,
            _to_readonly(t.data), t.int_type)
    if isinstance(t, types.Array):
        return types.Array(t.dtype, t.ndim, 'C', True)
    if isinstance(t, NumericIndexType):
        return NumericIndexType(t.dtype, t.name_typ, _to_readonly(t.data))
    if isinstance(t, (DatetimeIndexType, TimedeltaIndexType)):
        return t.__class__(t.name_typ, _to_readonly(t.data))
    return t


@lower_cast(CategoricalArrayType, CategoricalArrayType)
def cast_cat_arr(context, builder, fromty, toty, val):
    if _to_readonly(toty) == fromty:
        return val
    raise BodoError(f'Cannot cast from {fromty} to {toty}')


def create_cmp_op_overload(op):

    def overload_cat_arr_cmp(A, other):
        if not isinstance(A, CategoricalArrayType):
            return
        if A.dtype.categories and is_literal_type(other) and types.unliteral(
            other) == A.dtype.elem_type:
            val = get_literal_value(other)
            tffm__deb = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                ccwng__lqff = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), tffm__deb)
                return ccwng__lqff
            return impl_lit

        def impl(A, other):
            tffm__deb = get_code_for_value(A.dtype, other)
            ccwng__lqff = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), tffm__deb)
            return ccwng__lqff
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        qqv__atybt = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(qqv__atybt)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    uxh__ajrb = cat_dtype.categories
    n = len(uxh__ajrb)
    for ibsm__ojf in range(n):
        if uxh__ajrb[ibsm__ojf] == val:
            return ibsm__ojf
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    sqc__dgbe = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype')
    if sqc__dgbe != A.dtype.elem_type and sqc__dgbe != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if sqc__dgbe == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            ccwng__lqff = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for ibsm__ojf in numba.parfors.parfor.internal_prange(n):
                btag__xtjt = codes[ibsm__ojf]
                if btag__xtjt == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            ccwng__lqff, ibsm__ojf)
                    else:
                        bodo.libs.array_kernels.setna(ccwng__lqff, ibsm__ojf)
                    continue
                ccwng__lqff[ibsm__ojf] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[btag__xtjt]))
            return ccwng__lqff
        return impl
    zgn__xird = dtype_to_array_type(sqc__dgbe)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        ccwng__lqff = bodo.utils.utils.alloc_type(n, zgn__xird, (-1,))
        for ibsm__ojf in numba.parfors.parfor.internal_prange(n):
            btag__xtjt = codes[ibsm__ojf]
            if btag__xtjt == -1:
                bodo.libs.array_kernels.setna(ccwng__lqff, ibsm__ojf)
                continue
            ccwng__lqff[ibsm__ojf] = bodo.utils.conversion.unbox_if_timestamp(
                categories[btag__xtjt])
        return ccwng__lqff
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        jpt__igyf, awo__jaxg = args
        uxh__ajrb = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        uxh__ajrb.codes = jpt__igyf
        uxh__ajrb.dtype = awo__jaxg
        context.nrt.incref(builder, signature.args[0], jpt__igyf)
        context.nrt.incref(builder, signature.args[1], awo__jaxg)
        return uxh__ajrb._getvalue()
    xpp__nxcdt = CategoricalArrayType(cat_dtype)
    sig = xpp__nxcdt(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ggcq__zbh = args[0]
    if equiv_set.has_shape(ggcq__zbh):
        return ArrayAnalysis.AnalyzeResult(shape=ggcq__zbh, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    mkm__laog = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, mkm__laog)
        return init_categorical_array(codes, cat_dtype)
    return impl


def alloc_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_alloc_categorical_array
    ) = alloc_categorical_array_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_categorical_arr_codes(A):
    return lambda A: A.codes


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_categorical_array',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_categorical_arr_codes',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func


@overload_method(CategoricalArrayType, 'copy', no_unliteral=True)
def cat_arr_copy_overload(arr):
    return lambda arr: init_categorical_array(arr.codes.copy(), arr.dtype)


def build_replace_dicts(to_replace, value, categories):
    return dict(), np.empty(len(categories) + 1), 0


@overload(build_replace_dicts, no_unliteral=True)
def _build_replace_dicts(to_replace, value, categories):
    if isinstance(to_replace, types.Number) or to_replace == bodo.string_type:

        def impl(to_replace, value, categories):
            return build_replace_dicts([to_replace], value, categories)
        return impl
    else:

        def impl(to_replace, value, categories):
            n = len(categories)
            slh__yeyua = {}
            jpgxs__mnpcn = np.empty(n + 1, np.int64)
            tqgr__bqkud = {}
            jqqq__gpv = []
            zytd__nhlw = {}
            for ibsm__ojf in range(n):
                zytd__nhlw[categories[ibsm__ojf]] = ibsm__ojf
            for ojsrh__bfz in to_replace:
                if ojsrh__bfz != value:
                    if ojsrh__bfz in zytd__nhlw:
                        if value in zytd__nhlw:
                            slh__yeyua[ojsrh__bfz] = ojsrh__bfz
                            bmbul__ykcev = zytd__nhlw[ojsrh__bfz]
                            tqgr__bqkud[bmbul__ykcev] = zytd__nhlw[value]
                            jqqq__gpv.append(bmbul__ykcev)
                        else:
                            slh__yeyua[ojsrh__bfz] = value
                            zytd__nhlw[value] = zytd__nhlw[ojsrh__bfz]
            yupc__iqi = np.sort(np.array(jqqq__gpv))
            dcc__lheiz = 0
            mnai__kju = []
            for jmewt__vkak in range(-1, n):
                while dcc__lheiz < len(yupc__iqi) and jmewt__vkak > yupc__iqi[
                    dcc__lheiz]:
                    dcc__lheiz += 1
                mnai__kju.append(dcc__lheiz)
            for btza__pldu in range(-1, n):
                aja__jeeg = btza__pldu
                if btza__pldu in tqgr__bqkud:
                    aja__jeeg = tqgr__bqkud[btza__pldu]
                jpgxs__mnpcn[btza__pldu + 1] = aja__jeeg - mnai__kju[
                    aja__jeeg + 1]
            return slh__yeyua, jpgxs__mnpcn, len(yupc__iqi)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for ibsm__ojf in range(len(new_codes_arr)):
        new_codes_arr[ibsm__ojf] = codes_map_arr[old_codes_arr[ibsm__ojf] + 1]


@overload_method(CategoricalArrayType, 'replace', inline='always',
    no_unliteral=True)
def overload_replace(arr, to_replace, value):

    def impl(arr, to_replace, value):
        return bodo.hiframes.pd_categorical_ext.cat_replace(arr, to_replace,
            value)
    return impl


def cat_replace(arr, to_replace, value):
    return


@overload(cat_replace, no_unliteral=True)
def cat_replace_overload(arr, to_replace, value):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_replace,
        'CategoricalArray.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'CategoricalArray.replace()')
    qmdki__yai = arr.dtype.ordered
    xznv__kxqfg = arr.dtype.elem_type
    gdx__nbma = get_overload_const(to_replace)
    psuhr__knm = get_overload_const(value)
    if (arr.dtype.categories is not None and gdx__nbma is not NOT_CONSTANT and
        psuhr__knm is not NOT_CONSTANT):
        nggqf__wvmlx, codes_map_arr, xsz__ealwc = python_build_replace_dicts(
            gdx__nbma, psuhr__knm, arr.dtype.categories)
        if len(nggqf__wvmlx) == 0:
            return lambda arr, to_replace, value: arr.copy()
        owusx__gwof = []
        for hui__oezc in arr.dtype.categories:
            if hui__oezc in nggqf__wvmlx:
                bqt__sbjxd = nggqf__wvmlx[hui__oezc]
                if bqt__sbjxd != hui__oezc:
                    owusx__gwof.append(bqt__sbjxd)
            else:
                owusx__gwof.append(hui__oezc)
        jydlp__tlfj = bodo.utils.utils.create_categorical_type(owusx__gwof,
            arr.dtype.data.data, qmdki__yai)
        vypxf__tqmh = MetaType(tuple(jydlp__tlfj))

        def impl_dtype(arr, to_replace, value):
            ohnsm__efilh = init_cat_dtype(bodo.utils.conversion.
                index_from_array(jydlp__tlfj), qmdki__yai, None, vypxf__tqmh)
            uxh__ajrb = alloc_categorical_array(len(arr.codes), ohnsm__efilh)
            reassign_codes(uxh__ajrb.codes, arr.codes, codes_map_arr)
            return uxh__ajrb
        return impl_dtype
    xznv__kxqfg = arr.dtype.elem_type
    if xznv__kxqfg == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            slh__yeyua, codes_map_arr, twjsy__ytltl = build_replace_dicts(
                to_replace, value, categories.values)
            if len(slh__yeyua) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), qmdki__yai,
                    None, None))
            n = len(categories)
            jydlp__tlfj = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                twjsy__ytltl, -1)
            bsopo__vqy = 0
            for jmewt__vkak in range(n):
                htwu__odtk = categories[jmewt__vkak]
                if htwu__odtk in slh__yeyua:
                    pmqz__bgyt = slh__yeyua[htwu__odtk]
                    if pmqz__bgyt != htwu__odtk:
                        jydlp__tlfj[bsopo__vqy] = pmqz__bgyt
                        bsopo__vqy += 1
                else:
                    jydlp__tlfj[bsopo__vqy] = htwu__odtk
                    bsopo__vqy += 1
            uxh__ajrb = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                jydlp__tlfj), qmdki__yai, None, None))
            reassign_codes(uxh__ajrb.codes, arr.codes, codes_map_arr)
            return uxh__ajrb
        return impl_str
    gisy__hjm = dtype_to_array_type(xznv__kxqfg)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        slh__yeyua, codes_map_arr, twjsy__ytltl = build_replace_dicts(
            to_replace, value, categories.values)
        if len(slh__yeyua) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), qmdki__yai, None, None))
        n = len(categories)
        jydlp__tlfj = bodo.utils.utils.alloc_type(n - twjsy__ytltl,
            gisy__hjm, None)
        bsopo__vqy = 0
        for ibsm__ojf in range(n):
            htwu__odtk = categories[ibsm__ojf]
            if htwu__odtk in slh__yeyua:
                pmqz__bgyt = slh__yeyua[htwu__odtk]
                if pmqz__bgyt != htwu__odtk:
                    jydlp__tlfj[bsopo__vqy] = pmqz__bgyt
                    bsopo__vqy += 1
            else:
                jydlp__tlfj[bsopo__vqy] = htwu__odtk
                bsopo__vqy += 1
        uxh__ajrb = alloc_categorical_array(len(arr.codes), init_cat_dtype(
            bodo.utils.conversion.index_from_array(jydlp__tlfj), qmdki__yai,
            None, None))
        reassign_codes(uxh__ajrb.codes, arr.codes, codes_map_arr)
        return uxh__ajrb
    return impl


@overload(len, no_unliteral=True)
def overload_cat_arr_len(A):
    if isinstance(A, CategoricalArrayType):
        return lambda A: len(A.codes)


@overload_attribute(CategoricalArrayType, 'shape')
def overload_cat_arr_shape(A):
    return lambda A: (len(A.codes),)


@overload_attribute(CategoricalArrayType, 'ndim')
def overload_cat_arr_ndim(A):
    return lambda A: 1


@overload_attribute(CategoricalArrayType, 'nbytes')
def cat_arr_nbytes_overload(A):
    return lambda A: A.codes.nbytes + A.dtype.nbytes


@register_jitable
def get_label_dict_from_categories(vals):
    yxqp__war = dict()
    kbcaf__ivrhe = 0
    for ibsm__ojf in range(len(vals)):
        val = vals[ibsm__ojf]
        if val in yxqp__war:
            continue
        yxqp__war[val] = kbcaf__ivrhe
        kbcaf__ivrhe += 1
    return yxqp__war


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    yxqp__war = dict()
    for ibsm__ojf in range(len(vals)):
        val = vals[ibsm__ojf]
        yxqp__war[val] = ibsm__ojf
    return yxqp__war


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    wxnqr__lhg = dict(fastpath=fastpath)
    mdfox__yok = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', wxnqr__lhg, mdfox__yok)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        uenkn__zjjz = get_overload_const(categories)
        if uenkn__zjjz is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                xpxql__tqti = False
            else:
                xpxql__tqti = get_overload_const_bool(ordered)
            ebcs__fwk = pd.CategoricalDtype(pd.array(uenkn__zjjz), xpxql__tqti
                ).categories.array
            ajb__oxp = MetaType(tuple(ebcs__fwk))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                ohnsm__efilh = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(ebcs__fwk), xpxql__tqti, None, ajb__oxp)
                return bodo.utils.conversion.fix_arr_dtype(data, ohnsm__efilh)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            kqx__xdh = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                kqx__xdh, ordered, None, None)
            return bodo.utils.conversion.fix_arr_dtype(data, cat_dtype)
        return impl_cats
    elif is_overload_none(ordered):

        def impl_auto(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, 'category')
        return impl_auto
    raise BodoError(
        f'pd.Categorical(): argument combination not supported yet: {values}, {categories}, {ordered}, {dtype}'
        )


@overload(operator.getitem, no_unliteral=True)
def categorical_array_getitem(arr, ind):
    if not isinstance(arr, CategoricalArrayType):
        return
    if isinstance(ind, types.Integer):

        def categorical_getitem_impl(arr, ind):
            gufvs__vhz = arr.codes[ind]
            return arr.dtype.categories[max(gufvs__vhz, 0)]
        return categorical_getitem_impl
    if is_list_like_index_type(ind) or isinstance(ind, types.SliceType):

        def impl_bool(arr, ind):
            return init_categorical_array(arr.codes[ind], arr.dtype)
        return impl_bool
    raise BodoError(
        f'getitem for CategoricalArrayType with indexing type {ind} not supported.'
        )


class CategoricalMatchingValues(enum.Enum):
    DIFFERENT_TYPES = -1
    DONT_MATCH = 0
    MAY_MATCH = 1
    DO_MATCH = 2


def categorical_arrs_match(arr1, arr2):
    if not (isinstance(arr1, CategoricalArrayType) and isinstance(arr2,
        CategoricalArrayType)):
        return CategoricalMatchingValues.DIFFERENT_TYPES
    if arr1.dtype.categories is None or arr2.dtype.categories is None:
        return CategoricalMatchingValues.MAY_MATCH
    return (CategoricalMatchingValues.DO_MATCH if arr1.dtype.categories ==
        arr2.dtype.categories and arr1.dtype.ordered == arr2.dtype.ordered else
        CategoricalMatchingValues.DONT_MATCH)


@register_jitable
def cat_dtype_equal(dtype1, dtype2):
    if dtype1.ordered != dtype2.ordered or len(dtype1.categories) != len(dtype2
        .categories):
        return False
    arr1 = dtype1.categories.values
    arr2 = dtype2.categories.values
    for ibsm__ojf in range(len(arr1)):
        if arr1[ibsm__ojf] != arr2[ibsm__ojf]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    crn__lss = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    fqxpi__kdgjb = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    umpu__rlj = categorical_arrs_match(arr, val)
    mog__ldux = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    xpkv__glex = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not crn__lss:
            raise BodoError(mog__ldux)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            gufvs__vhz = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = gufvs__vhz
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (crn__lss or fqxpi__kdgjb or umpu__rlj !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(mog__ldux)
        if umpu__rlj == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(xpkv__glex)
        if crn__lss:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ykobk__nfmk = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for jmewt__vkak in range(n):
                    arr.codes[ind[jmewt__vkak]] = ykobk__nfmk
            return impl_scalar
        if umpu__rlj == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for ibsm__ojf in range(n):
                    arr.codes[ind[ibsm__ojf]] = val.codes[ibsm__ojf]
            return impl_arr_ind_mask
        if umpu__rlj == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(xpkv__glex)
                n = len(val.codes)
                for ibsm__ojf in range(n):
                    arr.codes[ind[ibsm__ojf]] = val.codes[ibsm__ojf]
            return impl_arr_ind_mask
        if fqxpi__kdgjb:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for jmewt__vkak in range(n):
                    uxa__kaei = bodo.utils.conversion.unbox_if_timestamp(val
                        [jmewt__vkak])
                    if uxa__kaei not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    gufvs__vhz = categories.get_loc(uxa__kaei)
                    arr.codes[ind[jmewt__vkak]] = gufvs__vhz
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (crn__lss or fqxpi__kdgjb or umpu__rlj !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(mog__ldux)
        if umpu__rlj == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(xpkv__glex)
        if crn__lss:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ykobk__nfmk = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for jmewt__vkak in range(n):
                    if ind[jmewt__vkak]:
                        arr.codes[jmewt__vkak] = ykobk__nfmk
            return impl_scalar
        if umpu__rlj == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                lbbgg__dgy = 0
                for ibsm__ojf in range(n):
                    if ind[ibsm__ojf]:
                        arr.codes[ibsm__ojf] = val.codes[lbbgg__dgy]
                        lbbgg__dgy += 1
            return impl_bool_ind_mask
        if umpu__rlj == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(xpkv__glex)
                n = len(ind)
                lbbgg__dgy = 0
                for ibsm__ojf in range(n):
                    if ind[ibsm__ojf]:
                        arr.codes[ibsm__ojf] = val.codes[lbbgg__dgy]
                        lbbgg__dgy += 1
            return impl_bool_ind_mask
        if fqxpi__kdgjb:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                lbbgg__dgy = 0
                categories = arr.dtype.categories
                for jmewt__vkak in range(n):
                    if ind[jmewt__vkak]:
                        uxa__kaei = bodo.utils.conversion.unbox_if_timestamp(
                            val[lbbgg__dgy])
                        if uxa__kaei not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        gufvs__vhz = categories.get_loc(uxa__kaei)
                        arr.codes[jmewt__vkak] = gufvs__vhz
                        lbbgg__dgy += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (crn__lss or fqxpi__kdgjb or umpu__rlj !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(mog__ldux)
        if umpu__rlj == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(xpkv__glex)
        if crn__lss:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ykobk__nfmk = arr.dtype.categories.get_loc(val)
                rfvu__fyr = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                for jmewt__vkak in range(rfvu__fyr.start, rfvu__fyr.stop,
                    rfvu__fyr.step):
                    arr.codes[jmewt__vkak] = ykobk__nfmk
            return impl_scalar
        if umpu__rlj == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if umpu__rlj == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(xpkv__glex)
                arr.codes[ind] = val.codes
            return impl_arr
        if fqxpi__kdgjb:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                rfvu__fyr = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                lbbgg__dgy = 0
                for jmewt__vkak in range(rfvu__fyr.start, rfvu__fyr.stop,
                    rfvu__fyr.step):
                    uxa__kaei = bodo.utils.conversion.unbox_if_timestamp(val
                        [lbbgg__dgy])
                    if uxa__kaei not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    gufvs__vhz = categories.get_loc(uxa__kaei)
                    arr.codes[jmewt__vkak] = gufvs__vhz
                    lbbgg__dgy += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
