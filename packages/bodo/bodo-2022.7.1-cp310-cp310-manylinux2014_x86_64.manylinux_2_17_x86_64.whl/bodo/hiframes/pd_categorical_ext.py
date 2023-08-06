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
        mlu__ars = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=mlu__ars)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    yarrm__mmnwf = tuple(val.categories.values)
    elem_type = None if len(yarrm__mmnwf) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(yarrm__mmnwf, elem_type, val.ordered, bodo.
        typeof(val.categories), int_type)


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
        uum__pvsqc = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, uum__pvsqc)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    tles__rmms = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    ppqeg__pxov = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, aaz__jcn, aaz__jcn = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    ekxk__lap = PDCategoricalDtype(ppqeg__pxov, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, tles__rmms)
    return ekxk__lap(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    leuha__aew = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, leuha__aew).value
    c.pyapi.decref(leuha__aew)
    rge__tzzpm = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, rge__tzzpm).value
    c.pyapi.decref(rge__tzzpm)
    issn__ikkyl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=issn__ikkyl)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    leuha__aew = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    fwmt__ljo = c.pyapi.from_native_value(typ.data, cat_dtype.categories, c
        .env_manager)
    atqw__brgn = c.context.insert_const_string(c.builder.module, 'pandas')
    rznp__slfy = c.pyapi.import_module_noblock(atqw__brgn)
    njffj__kuowk = c.pyapi.call_method(rznp__slfy, 'CategoricalDtype', (
        fwmt__ljo, leuha__aew))
    c.pyapi.decref(leuha__aew)
    c.pyapi.decref(fwmt__ljo)
    c.pyapi.decref(rznp__slfy)
    c.context.nrt.decref(c.builder, typ, val)
    return njffj__kuowk


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
        evxfg__haw = get_categories_int_type(fe_type.dtype)
        uum__pvsqc = [('dtype', fe_type.dtype), ('codes', types.Array(
            evxfg__haw, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, uum__pvsqc)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    oeb__oasxu = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), oeb__oasxu
        ).value
    c.pyapi.decref(oeb__oasxu)
    njffj__kuowk = c.pyapi.object_getattr_string(val, 'dtype')
    pwe__fzr = c.pyapi.to_native_value(typ.dtype, njffj__kuowk).value
    c.pyapi.decref(njffj__kuowk)
    jviv__smeno = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jviv__smeno.codes = codes
    jviv__smeno.dtype = pwe__fzr
    return NativeValue(jviv__smeno._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    buwp__wdfg = get_categories_int_type(typ.dtype)
    wmhft__gaaj = context.get_constant_generic(builder, types.Array(
        buwp__wdfg, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, wmhft__gaaj])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    xsbol__xtobw = len(cat_dtype.categories)
    if xsbol__xtobw < np.iinfo(np.int8).max:
        dtype = types.int8
    elif xsbol__xtobw < np.iinfo(np.int16).max:
        dtype = types.int16
    elif xsbol__xtobw < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    atqw__brgn = c.context.insert_const_string(c.builder.module, 'pandas')
    rznp__slfy = c.pyapi.import_module_noblock(atqw__brgn)
    evxfg__haw = get_categories_int_type(dtype)
    vtsp__kqovk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    pxixj__kkd = types.Array(evxfg__haw, 1, 'C')
    c.context.nrt.incref(c.builder, pxixj__kkd, vtsp__kqovk.codes)
    oeb__oasxu = c.pyapi.from_native_value(pxixj__kkd, vtsp__kqovk.codes, c
        .env_manager)
    c.context.nrt.incref(c.builder, dtype, vtsp__kqovk.dtype)
    njffj__kuowk = c.pyapi.from_native_value(dtype, vtsp__kqovk.dtype, c.
        env_manager)
    bualo__btczp = c.pyapi.borrow_none()
    uys__qvgc = c.pyapi.object_getattr_string(rznp__slfy, 'Categorical')
    rtzj__ukw = c.pyapi.call_method(uys__qvgc, 'from_codes', (oeb__oasxu,
        bualo__btczp, bualo__btczp, njffj__kuowk))
    c.pyapi.decref(uys__qvgc)
    c.pyapi.decref(oeb__oasxu)
    c.pyapi.decref(njffj__kuowk)
    c.pyapi.decref(rznp__slfy)
    c.context.nrt.decref(c.builder, typ, val)
    return rtzj__ukw


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
            dqonu__onbux = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                wwvgi__vwp = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), dqonu__onbux)
                return wwvgi__vwp
            return impl_lit

        def impl(A, other):
            dqonu__onbux = get_code_for_value(A.dtype, other)
            wwvgi__vwp = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), dqonu__onbux)
            return wwvgi__vwp
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        posp__ykp = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(posp__ykp)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    vtsp__kqovk = cat_dtype.categories
    n = len(vtsp__kqovk)
    for trzv__vmuqi in range(n):
        if vtsp__kqovk[trzv__vmuqi] == val:
            return trzv__vmuqi
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    xvuj__mywb = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype'
        )
    if xvuj__mywb != A.dtype.elem_type and xvuj__mywb != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if xvuj__mywb == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            wwvgi__vwp = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for trzv__vmuqi in numba.parfors.parfor.internal_prange(n):
                zvqre__aqh = codes[trzv__vmuqi]
                if zvqre__aqh == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(wwvgi__vwp
                            , trzv__vmuqi)
                    else:
                        bodo.libs.array_kernels.setna(wwvgi__vwp, trzv__vmuqi)
                    continue
                wwvgi__vwp[trzv__vmuqi] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[zvqre__aqh]))
            return wwvgi__vwp
        return impl
    pxixj__kkd = dtype_to_array_type(xvuj__mywb)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        wwvgi__vwp = bodo.utils.utils.alloc_type(n, pxixj__kkd, (-1,))
        for trzv__vmuqi in numba.parfors.parfor.internal_prange(n):
            zvqre__aqh = codes[trzv__vmuqi]
            if zvqre__aqh == -1:
                bodo.libs.array_kernels.setna(wwvgi__vwp, trzv__vmuqi)
                continue
            wwvgi__vwp[trzv__vmuqi] = bodo.utils.conversion.unbox_if_timestamp(
                categories[zvqre__aqh])
        return wwvgi__vwp
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        atj__gjgj, pwe__fzr = args
        vtsp__kqovk = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        vtsp__kqovk.codes = atj__gjgj
        vtsp__kqovk.dtype = pwe__fzr
        context.nrt.incref(builder, signature.args[0], atj__gjgj)
        context.nrt.incref(builder, signature.args[1], pwe__fzr)
        return vtsp__kqovk._getvalue()
    qqyyj__lfip = CategoricalArrayType(cat_dtype)
    sig = qqyyj__lfip(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    cdqm__uyluq = args[0]
    if equiv_set.has_shape(cdqm__uyluq):
        return ArrayAnalysis.AnalyzeResult(shape=cdqm__uyluq, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    evxfg__haw = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, evxfg__haw)
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
            qwf__evr = {}
            wmhft__gaaj = np.empty(n + 1, np.int64)
            xqzs__yut = {}
            ddqhg__vyf = []
            pbz__ngj = {}
            for trzv__vmuqi in range(n):
                pbz__ngj[categories[trzv__vmuqi]] = trzv__vmuqi
            for hatzj__bphk in to_replace:
                if hatzj__bphk != value:
                    if hatzj__bphk in pbz__ngj:
                        if value in pbz__ngj:
                            qwf__evr[hatzj__bphk] = hatzj__bphk
                            hyrd__rbgwn = pbz__ngj[hatzj__bphk]
                            xqzs__yut[hyrd__rbgwn] = pbz__ngj[value]
                            ddqhg__vyf.append(hyrd__rbgwn)
                        else:
                            qwf__evr[hatzj__bphk] = value
                            pbz__ngj[value] = pbz__ngj[hatzj__bphk]
            dbws__mik = np.sort(np.array(ddqhg__vyf))
            qhil__vcp = 0
            vvtil__xzo = []
            for lpkdr__wspyt in range(-1, n):
                while qhil__vcp < len(dbws__mik) and lpkdr__wspyt > dbws__mik[
                    qhil__vcp]:
                    qhil__vcp += 1
                vvtil__xzo.append(qhil__vcp)
            for dvg__tyey in range(-1, n):
                ius__aamb = dvg__tyey
                if dvg__tyey in xqzs__yut:
                    ius__aamb = xqzs__yut[dvg__tyey]
                wmhft__gaaj[dvg__tyey + 1] = ius__aamb - vvtil__xzo[
                    ius__aamb + 1]
            return qwf__evr, wmhft__gaaj, len(dbws__mik)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for trzv__vmuqi in range(len(new_codes_arr)):
        new_codes_arr[trzv__vmuqi] = codes_map_arr[old_codes_arr[
            trzv__vmuqi] + 1]


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
    iuv__bapn = arr.dtype.ordered
    htg__fwoj = arr.dtype.elem_type
    ito__unqk = get_overload_const(to_replace)
    efag__bwrrp = get_overload_const(value)
    if (arr.dtype.categories is not None and ito__unqk is not NOT_CONSTANT and
        efag__bwrrp is not NOT_CONSTANT):
        ewwu__mbel, codes_map_arr, aaz__jcn = python_build_replace_dicts(
            ito__unqk, efag__bwrrp, arr.dtype.categories)
        if len(ewwu__mbel) == 0:
            return lambda arr, to_replace, value: arr.copy()
        rtl__sasu = []
        for lmpsw__exzq in arr.dtype.categories:
            if lmpsw__exzq in ewwu__mbel:
                ddit__xcxdp = ewwu__mbel[lmpsw__exzq]
                if ddit__xcxdp != lmpsw__exzq:
                    rtl__sasu.append(ddit__xcxdp)
            else:
                rtl__sasu.append(lmpsw__exzq)
        yojh__tth = bodo.utils.utils.create_categorical_type(rtl__sasu, arr
            .dtype.data.data, iuv__bapn)
        iday__aeioa = MetaType(tuple(yojh__tth))

        def impl_dtype(arr, to_replace, value):
            glg__uhvr = init_cat_dtype(bodo.utils.conversion.
                index_from_array(yojh__tth), iuv__bapn, None, iday__aeioa)
            vtsp__kqovk = alloc_categorical_array(len(arr.codes), glg__uhvr)
            reassign_codes(vtsp__kqovk.codes, arr.codes, codes_map_arr)
            return vtsp__kqovk
        return impl_dtype
    htg__fwoj = arr.dtype.elem_type
    if htg__fwoj == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            qwf__evr, codes_map_arr, csy__wbzg = build_replace_dicts(to_replace
                , value, categories.values)
            if len(qwf__evr) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), iuv__bapn,
                    None, None))
            n = len(categories)
            yojh__tth = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                csy__wbzg, -1)
            nib__jrae = 0
            for lpkdr__wspyt in range(n):
                dtlu__wmhqw = categories[lpkdr__wspyt]
                if dtlu__wmhqw in qwf__evr:
                    daa__oahdy = qwf__evr[dtlu__wmhqw]
                    if daa__oahdy != dtlu__wmhqw:
                        yojh__tth[nib__jrae] = daa__oahdy
                        nib__jrae += 1
                else:
                    yojh__tth[nib__jrae] = dtlu__wmhqw
                    nib__jrae += 1
            vtsp__kqovk = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                yojh__tth), iuv__bapn, None, None))
            reassign_codes(vtsp__kqovk.codes, arr.codes, codes_map_arr)
            return vtsp__kqovk
        return impl_str
    xxru__gjt = dtype_to_array_type(htg__fwoj)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        qwf__evr, codes_map_arr, csy__wbzg = build_replace_dicts(to_replace,
            value, categories.values)
        if len(qwf__evr) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), iuv__bapn, None, None))
        n = len(categories)
        yojh__tth = bodo.utils.utils.alloc_type(n - csy__wbzg, xxru__gjt, None)
        nib__jrae = 0
        for trzv__vmuqi in range(n):
            dtlu__wmhqw = categories[trzv__vmuqi]
            if dtlu__wmhqw in qwf__evr:
                daa__oahdy = qwf__evr[dtlu__wmhqw]
                if daa__oahdy != dtlu__wmhqw:
                    yojh__tth[nib__jrae] = daa__oahdy
                    nib__jrae += 1
            else:
                yojh__tth[nib__jrae] = dtlu__wmhqw
                nib__jrae += 1
        vtsp__kqovk = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(yojh__tth
            ), iuv__bapn, None, None))
        reassign_codes(vtsp__kqovk.codes, arr.codes, codes_map_arr)
        return vtsp__kqovk
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
    ranqd__clhm = dict()
    qrwnk__muv = 0
    for trzv__vmuqi in range(len(vals)):
        val = vals[trzv__vmuqi]
        if val in ranqd__clhm:
            continue
        ranqd__clhm[val] = qrwnk__muv
        qrwnk__muv += 1
    return ranqd__clhm


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    ranqd__clhm = dict()
    for trzv__vmuqi in range(len(vals)):
        val = vals[trzv__vmuqi]
        ranqd__clhm[val] = trzv__vmuqi
    return ranqd__clhm


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    srqnk__sap = dict(fastpath=fastpath)
    emlin__yhp = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', srqnk__sap, emlin__yhp)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        mdc__bqy = get_overload_const(categories)
        if mdc__bqy is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                ajj__vcvro = False
            else:
                ajj__vcvro = get_overload_const_bool(ordered)
            ribsq__ptib = pd.CategoricalDtype(pd.array(mdc__bqy), ajj__vcvro
                ).categories.array
            txqzd__uxfu = MetaType(tuple(ribsq__ptib))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                glg__uhvr = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(ribsq__ptib), ajj__vcvro, None,
                    txqzd__uxfu)
                return bodo.utils.conversion.fix_arr_dtype(data, glg__uhvr)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            yarrm__mmnwf = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                yarrm__mmnwf, ordered, None, None)
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
            peyqg__sgh = arr.codes[ind]
            return arr.dtype.categories[max(peyqg__sgh, 0)]
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
    for trzv__vmuqi in range(len(arr1)):
        if arr1[trzv__vmuqi] != arr2[trzv__vmuqi]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    gvnal__ysval = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    nfx__xcq = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    lkf__ovgfg = categorical_arrs_match(arr, val)
    xxqd__axl = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    zjb__bnzr = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not gvnal__ysval:
            raise BodoError(xxqd__axl)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            peyqg__sgh = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = peyqg__sgh
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (gvnal__ysval or nfx__xcq or lkf__ovgfg !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(xxqd__axl)
        if lkf__ovgfg == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(zjb__bnzr)
        if gvnal__ysval:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                rfq__qqomq = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for lpkdr__wspyt in range(n):
                    arr.codes[ind[lpkdr__wspyt]] = rfq__qqomq
            return impl_scalar
        if lkf__ovgfg == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for trzv__vmuqi in range(n):
                    arr.codes[ind[trzv__vmuqi]] = val.codes[trzv__vmuqi]
            return impl_arr_ind_mask
        if lkf__ovgfg == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(zjb__bnzr)
                n = len(val.codes)
                for trzv__vmuqi in range(n):
                    arr.codes[ind[trzv__vmuqi]] = val.codes[trzv__vmuqi]
            return impl_arr_ind_mask
        if nfx__xcq:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for lpkdr__wspyt in range(n):
                    gndq__gpqx = bodo.utils.conversion.unbox_if_timestamp(val
                        [lpkdr__wspyt])
                    if gndq__gpqx not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    peyqg__sgh = categories.get_loc(gndq__gpqx)
                    arr.codes[ind[lpkdr__wspyt]] = peyqg__sgh
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (gvnal__ysval or nfx__xcq or lkf__ovgfg !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(xxqd__axl)
        if lkf__ovgfg == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(zjb__bnzr)
        if gvnal__ysval:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                rfq__qqomq = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for lpkdr__wspyt in range(n):
                    if ind[lpkdr__wspyt]:
                        arr.codes[lpkdr__wspyt] = rfq__qqomq
            return impl_scalar
        if lkf__ovgfg == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                lgf__ugid = 0
                for trzv__vmuqi in range(n):
                    if ind[trzv__vmuqi]:
                        arr.codes[trzv__vmuqi] = val.codes[lgf__ugid]
                        lgf__ugid += 1
            return impl_bool_ind_mask
        if lkf__ovgfg == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(zjb__bnzr)
                n = len(ind)
                lgf__ugid = 0
                for trzv__vmuqi in range(n):
                    if ind[trzv__vmuqi]:
                        arr.codes[trzv__vmuqi] = val.codes[lgf__ugid]
                        lgf__ugid += 1
            return impl_bool_ind_mask
        if nfx__xcq:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                lgf__ugid = 0
                categories = arr.dtype.categories
                for lpkdr__wspyt in range(n):
                    if ind[lpkdr__wspyt]:
                        gndq__gpqx = bodo.utils.conversion.unbox_if_timestamp(
                            val[lgf__ugid])
                        if gndq__gpqx not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        peyqg__sgh = categories.get_loc(gndq__gpqx)
                        arr.codes[lpkdr__wspyt] = peyqg__sgh
                        lgf__ugid += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (gvnal__ysval or nfx__xcq or lkf__ovgfg !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(xxqd__axl)
        if lkf__ovgfg == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(zjb__bnzr)
        if gvnal__ysval:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                rfq__qqomq = arr.dtype.categories.get_loc(val)
                lrd__woc = numba.cpython.unicode._normalize_slice(ind, len(arr)
                    )
                for lpkdr__wspyt in range(lrd__woc.start, lrd__woc.stop,
                    lrd__woc.step):
                    arr.codes[lpkdr__wspyt] = rfq__qqomq
            return impl_scalar
        if lkf__ovgfg == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if lkf__ovgfg == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(zjb__bnzr)
                arr.codes[ind] = val.codes
            return impl_arr
        if nfx__xcq:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                lrd__woc = numba.cpython.unicode._normalize_slice(ind, len(arr)
                    )
                lgf__ugid = 0
                for lpkdr__wspyt in range(lrd__woc.start, lrd__woc.stop,
                    lrd__woc.step):
                    gndq__gpqx = bodo.utils.conversion.unbox_if_timestamp(val
                        [lgf__ugid])
                    if gndq__gpqx not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    peyqg__sgh = categories.get_loc(gndq__gpqx)
                    arr.codes[lpkdr__wspyt] = peyqg__sgh
                    lgf__ugid += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
