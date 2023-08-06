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
        vru__vdzfb = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=vru__vdzfb)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    kgrhg__fkrwh = tuple(val.categories.values)
    elem_type = None if len(kgrhg__fkrwh) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(kgrhg__fkrwh, elem_type, val.ordered, bodo.
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
        ipc__ayaxi = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, ipc__ayaxi)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    ilkm__jpfx = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    qdyev__lbe = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, heima__wnw, heima__wnw = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    hep__iwfb = PDCategoricalDtype(qdyev__lbe, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, ilkm__jpfx)
    return hep__iwfb(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wiraf__hmdf = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, wiraf__hmdf).value
    c.pyapi.decref(wiraf__hmdf)
    hby__estnp = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, hby__estnp).value
    c.pyapi.decref(hby__estnp)
    bonqb__apjwb = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=bonqb__apjwb)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    wiraf__hmdf = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    xwoa__xtl = c.pyapi.from_native_value(typ.data, cat_dtype.categories, c
        .env_manager)
    xvxs__nkyef = c.context.insert_const_string(c.builder.module, 'pandas')
    wrb__ytvn = c.pyapi.import_module_noblock(xvxs__nkyef)
    mtn__jcwtw = c.pyapi.call_method(wrb__ytvn, 'CategoricalDtype', (
        xwoa__xtl, wiraf__hmdf))
    c.pyapi.decref(wiraf__hmdf)
    c.pyapi.decref(xwoa__xtl)
    c.pyapi.decref(wrb__ytvn)
    c.context.nrt.decref(c.builder, typ, val)
    return mtn__jcwtw


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
        dsni__met = get_categories_int_type(fe_type.dtype)
        ipc__ayaxi = [('dtype', fe_type.dtype), ('codes', types.Array(
            dsni__met, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, ipc__ayaxi)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    sfrkk__dbki = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), sfrkk__dbki
        ).value
    c.pyapi.decref(sfrkk__dbki)
    mtn__jcwtw = c.pyapi.object_getattr_string(val, 'dtype')
    dqa__hai = c.pyapi.to_native_value(typ.dtype, mtn__jcwtw).value
    c.pyapi.decref(mtn__jcwtw)
    kch__fqj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kch__fqj.codes = codes
    kch__fqj.dtype = dqa__hai
    return NativeValue(kch__fqj._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    aym__lrd = get_categories_int_type(typ.dtype)
    iaus__bdh = context.get_constant_generic(builder, types.Array(aym__lrd,
        1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, iaus__bdh])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    zvhd__dzr = len(cat_dtype.categories)
    if zvhd__dzr < np.iinfo(np.int8).max:
        dtype = types.int8
    elif zvhd__dzr < np.iinfo(np.int16).max:
        dtype = types.int16
    elif zvhd__dzr < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    xvxs__nkyef = c.context.insert_const_string(c.builder.module, 'pandas')
    wrb__ytvn = c.pyapi.import_module_noblock(xvxs__nkyef)
    dsni__met = get_categories_int_type(dtype)
    heypg__anoro = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    gmugn__iokxr = types.Array(dsni__met, 1, 'C')
    c.context.nrt.incref(c.builder, gmugn__iokxr, heypg__anoro.codes)
    sfrkk__dbki = c.pyapi.from_native_value(gmugn__iokxr, heypg__anoro.
        codes, c.env_manager)
    c.context.nrt.incref(c.builder, dtype, heypg__anoro.dtype)
    mtn__jcwtw = c.pyapi.from_native_value(dtype, heypg__anoro.dtype, c.
        env_manager)
    xxwx__meg = c.pyapi.borrow_none()
    gcld__fti = c.pyapi.object_getattr_string(wrb__ytvn, 'Categorical')
    xunzk__aqwiq = c.pyapi.call_method(gcld__fti, 'from_codes', (
        sfrkk__dbki, xxwx__meg, xxwx__meg, mtn__jcwtw))
    c.pyapi.decref(gcld__fti)
    c.pyapi.decref(sfrkk__dbki)
    c.pyapi.decref(mtn__jcwtw)
    c.pyapi.decref(wrb__ytvn)
    c.context.nrt.decref(c.builder, typ, val)
    return xunzk__aqwiq


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
            tstnh__neeyk = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                qqdrw__odf = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), tstnh__neeyk)
                return qqdrw__odf
            return impl_lit

        def impl(A, other):
            tstnh__neeyk = get_code_for_value(A.dtype, other)
            qqdrw__odf = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), tstnh__neeyk)
            return qqdrw__odf
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        rtzbj__jsbh = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(rtzbj__jsbh)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    heypg__anoro = cat_dtype.categories
    n = len(heypg__anoro)
    for wgfzg__rxgf in range(n):
        if heypg__anoro[wgfzg__rxgf] == val:
            return wgfzg__rxgf
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    ncind__crcxv = bodo.utils.typing.parse_dtype(dtype,
        'CategoricalArray.astype')
    if (ncind__crcxv != A.dtype.elem_type and ncind__crcxv != types.
        unicode_type):
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if ncind__crcxv == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            qqdrw__odf = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for wgfzg__rxgf in numba.parfors.parfor.internal_prange(n):
                owub__vboa = codes[wgfzg__rxgf]
                if owub__vboa == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(qqdrw__odf
                            , wgfzg__rxgf)
                    else:
                        bodo.libs.array_kernels.setna(qqdrw__odf, wgfzg__rxgf)
                    continue
                qqdrw__odf[wgfzg__rxgf] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[owub__vboa]))
            return qqdrw__odf
        return impl
    gmugn__iokxr = dtype_to_array_type(ncind__crcxv)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        qqdrw__odf = bodo.utils.utils.alloc_type(n, gmugn__iokxr, (-1,))
        for wgfzg__rxgf in numba.parfors.parfor.internal_prange(n):
            owub__vboa = codes[wgfzg__rxgf]
            if owub__vboa == -1:
                bodo.libs.array_kernels.setna(qqdrw__odf, wgfzg__rxgf)
                continue
            qqdrw__odf[wgfzg__rxgf] = bodo.utils.conversion.unbox_if_timestamp(
                categories[owub__vboa])
        return qqdrw__odf
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        vgn__xvj, dqa__hai = args
        heypg__anoro = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        heypg__anoro.codes = vgn__xvj
        heypg__anoro.dtype = dqa__hai
        context.nrt.incref(builder, signature.args[0], vgn__xvj)
        context.nrt.incref(builder, signature.args[1], dqa__hai)
        return heypg__anoro._getvalue()
    xzo__cgpvt = CategoricalArrayType(cat_dtype)
    sig = xzo__cgpvt(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    svr__gfdz = args[0]
    if equiv_set.has_shape(svr__gfdz):
        return ArrayAnalysis.AnalyzeResult(shape=svr__gfdz, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    dsni__met = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, dsni__met)
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
            vqa__kbad = {}
            iaus__bdh = np.empty(n + 1, np.int64)
            onyn__qwox = {}
            ajaea__foo = []
            yqhrk__syv = {}
            for wgfzg__rxgf in range(n):
                yqhrk__syv[categories[wgfzg__rxgf]] = wgfzg__rxgf
            for dvvz__fzjg in to_replace:
                if dvvz__fzjg != value:
                    if dvvz__fzjg in yqhrk__syv:
                        if value in yqhrk__syv:
                            vqa__kbad[dvvz__fzjg] = dvvz__fzjg
                            iusvh__uxy = yqhrk__syv[dvvz__fzjg]
                            onyn__qwox[iusvh__uxy] = yqhrk__syv[value]
                            ajaea__foo.append(iusvh__uxy)
                        else:
                            vqa__kbad[dvvz__fzjg] = value
                            yqhrk__syv[value] = yqhrk__syv[dvvz__fzjg]
            acuu__ibeng = np.sort(np.array(ajaea__foo))
            vzxgc__sveco = 0
            lnh__lfhc = []
            for dsb__bnt in range(-1, n):
                while vzxgc__sveco < len(acuu__ibeng
                    ) and dsb__bnt > acuu__ibeng[vzxgc__sveco]:
                    vzxgc__sveco += 1
                lnh__lfhc.append(vzxgc__sveco)
            for eje__vzx in range(-1, n):
                hvci__vnj = eje__vzx
                if eje__vzx in onyn__qwox:
                    hvci__vnj = onyn__qwox[eje__vzx]
                iaus__bdh[eje__vzx + 1] = hvci__vnj - lnh__lfhc[hvci__vnj + 1]
            return vqa__kbad, iaus__bdh, len(acuu__ibeng)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for wgfzg__rxgf in range(len(new_codes_arr)):
        new_codes_arr[wgfzg__rxgf] = codes_map_arr[old_codes_arr[
            wgfzg__rxgf] + 1]


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
    nwi__fdyy = arr.dtype.ordered
    uria__loe = arr.dtype.elem_type
    zml__fhm = get_overload_const(to_replace)
    yellc__lfc = get_overload_const(value)
    if (arr.dtype.categories is not None and zml__fhm is not NOT_CONSTANT and
        yellc__lfc is not NOT_CONSTANT):
        ckfr__wcv, codes_map_arr, heima__wnw = python_build_replace_dicts(
            zml__fhm, yellc__lfc, arr.dtype.categories)
        if len(ckfr__wcv) == 0:
            return lambda arr, to_replace, value: arr.copy()
        thyl__qpl = []
        for etk__tng in arr.dtype.categories:
            if etk__tng in ckfr__wcv:
                mcl__pfg = ckfr__wcv[etk__tng]
                if mcl__pfg != etk__tng:
                    thyl__qpl.append(mcl__pfg)
            else:
                thyl__qpl.append(etk__tng)
        zxscr__ybasn = bodo.utils.utils.create_categorical_type(thyl__qpl,
            arr.dtype.data.data, nwi__fdyy)
        vbhaf__cub = MetaType(tuple(zxscr__ybasn))

        def impl_dtype(arr, to_replace, value):
            vfuh__wudso = init_cat_dtype(bodo.utils.conversion.
                index_from_array(zxscr__ybasn), nwi__fdyy, None, vbhaf__cub)
            heypg__anoro = alloc_categorical_array(len(arr.codes), vfuh__wudso)
            reassign_codes(heypg__anoro.codes, arr.codes, codes_map_arr)
            return heypg__anoro
        return impl_dtype
    uria__loe = arr.dtype.elem_type
    if uria__loe == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            vqa__kbad, codes_map_arr, lcpm__svez = build_replace_dicts(
                to_replace, value, categories.values)
            if len(vqa__kbad) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), nwi__fdyy,
                    None, None))
            n = len(categories)
            zxscr__ybasn = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                lcpm__svez, -1)
            irkqk__xafp = 0
            for dsb__bnt in range(n):
                smnv__icic = categories[dsb__bnt]
                if smnv__icic in vqa__kbad:
                    bbxy__uhlb = vqa__kbad[smnv__icic]
                    if bbxy__uhlb != smnv__icic:
                        zxscr__ybasn[irkqk__xafp] = bbxy__uhlb
                        irkqk__xafp += 1
                else:
                    zxscr__ybasn[irkqk__xafp] = smnv__icic
                    irkqk__xafp += 1
            heypg__anoro = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                zxscr__ybasn), nwi__fdyy, None, None))
            reassign_codes(heypg__anoro.codes, arr.codes, codes_map_arr)
            return heypg__anoro
        return impl_str
    tnlkv__ageu = dtype_to_array_type(uria__loe)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        vqa__kbad, codes_map_arr, lcpm__svez = build_replace_dicts(to_replace,
            value, categories.values)
        if len(vqa__kbad) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), nwi__fdyy, None, None))
        n = len(categories)
        zxscr__ybasn = bodo.utils.utils.alloc_type(n - lcpm__svez,
            tnlkv__ageu, None)
        irkqk__xafp = 0
        for wgfzg__rxgf in range(n):
            smnv__icic = categories[wgfzg__rxgf]
            if smnv__icic in vqa__kbad:
                bbxy__uhlb = vqa__kbad[smnv__icic]
                if bbxy__uhlb != smnv__icic:
                    zxscr__ybasn[irkqk__xafp] = bbxy__uhlb
                    irkqk__xafp += 1
            else:
                zxscr__ybasn[irkqk__xafp] = smnv__icic
                irkqk__xafp += 1
        heypg__anoro = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(
            zxscr__ybasn), nwi__fdyy, None, None))
        reassign_codes(heypg__anoro.codes, arr.codes, codes_map_arr)
        return heypg__anoro
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
    uwedu__pwgel = dict()
    cbow__pgo = 0
    for wgfzg__rxgf in range(len(vals)):
        val = vals[wgfzg__rxgf]
        if val in uwedu__pwgel:
            continue
        uwedu__pwgel[val] = cbow__pgo
        cbow__pgo += 1
    return uwedu__pwgel


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    uwedu__pwgel = dict()
    for wgfzg__rxgf in range(len(vals)):
        val = vals[wgfzg__rxgf]
        uwedu__pwgel[val] = wgfzg__rxgf
    return uwedu__pwgel


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    tvzs__ciks = dict(fastpath=fastpath)
    qxdgg__isvz = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', tvzs__ciks, qxdgg__isvz)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        ucs__ziegf = get_overload_const(categories)
        if ucs__ziegf is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                hvvqg__ckv = False
            else:
                hvvqg__ckv = get_overload_const_bool(ordered)
            bjnn__tgjne = pd.CategoricalDtype(pd.array(ucs__ziegf), hvvqg__ckv
                ).categories.array
            ezl__zhl = MetaType(tuple(bjnn__tgjne))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                vfuh__wudso = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(bjnn__tgjne), hvvqg__ckv, None, ezl__zhl)
                return bodo.utils.conversion.fix_arr_dtype(data, vfuh__wudso)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            kgrhg__fkrwh = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                kgrhg__fkrwh, ordered, None, None)
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
            yfd__ggmfw = arr.codes[ind]
            return arr.dtype.categories[max(yfd__ggmfw, 0)]
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
    for wgfzg__rxgf in range(len(arr1)):
        if arr1[wgfzg__rxgf] != arr2[wgfzg__rxgf]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    wzkn__gbjz = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    alz__pzo = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    cdn__ktndc = categorical_arrs_match(arr, val)
    gupil__sku = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    fieth__lzo = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not wzkn__gbjz:
            raise BodoError(gupil__sku)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            yfd__ggmfw = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = yfd__ggmfw
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (wzkn__gbjz or alz__pzo or cdn__ktndc !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gupil__sku)
        if cdn__ktndc == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(fieth__lzo)
        if wzkn__gbjz:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                tshyl__hfd = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for dsb__bnt in range(n):
                    arr.codes[ind[dsb__bnt]] = tshyl__hfd
            return impl_scalar
        if cdn__ktndc == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for wgfzg__rxgf in range(n):
                    arr.codes[ind[wgfzg__rxgf]] = val.codes[wgfzg__rxgf]
            return impl_arr_ind_mask
        if cdn__ktndc == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(fieth__lzo)
                n = len(val.codes)
                for wgfzg__rxgf in range(n):
                    arr.codes[ind[wgfzg__rxgf]] = val.codes[wgfzg__rxgf]
            return impl_arr_ind_mask
        if alz__pzo:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for dsb__bnt in range(n):
                    hecu__tyhkr = bodo.utils.conversion.unbox_if_timestamp(val
                        [dsb__bnt])
                    if hecu__tyhkr not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    yfd__ggmfw = categories.get_loc(hecu__tyhkr)
                    arr.codes[ind[dsb__bnt]] = yfd__ggmfw
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (wzkn__gbjz or alz__pzo or cdn__ktndc !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gupil__sku)
        if cdn__ktndc == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(fieth__lzo)
        if wzkn__gbjz:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                tshyl__hfd = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for dsb__bnt in range(n):
                    if ind[dsb__bnt]:
                        arr.codes[dsb__bnt] = tshyl__hfd
            return impl_scalar
        if cdn__ktndc == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                efil__mrqg = 0
                for wgfzg__rxgf in range(n):
                    if ind[wgfzg__rxgf]:
                        arr.codes[wgfzg__rxgf] = val.codes[efil__mrqg]
                        efil__mrqg += 1
            return impl_bool_ind_mask
        if cdn__ktndc == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(fieth__lzo)
                n = len(ind)
                efil__mrqg = 0
                for wgfzg__rxgf in range(n):
                    if ind[wgfzg__rxgf]:
                        arr.codes[wgfzg__rxgf] = val.codes[efil__mrqg]
                        efil__mrqg += 1
            return impl_bool_ind_mask
        if alz__pzo:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                efil__mrqg = 0
                categories = arr.dtype.categories
                for dsb__bnt in range(n):
                    if ind[dsb__bnt]:
                        hecu__tyhkr = bodo.utils.conversion.unbox_if_timestamp(
                            val[efil__mrqg])
                        if hecu__tyhkr not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        yfd__ggmfw = categories.get_loc(hecu__tyhkr)
                        arr.codes[dsb__bnt] = yfd__ggmfw
                        efil__mrqg += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (wzkn__gbjz or alz__pzo or cdn__ktndc !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(gupil__sku)
        if cdn__ktndc == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(fieth__lzo)
        if wzkn__gbjz:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                tshyl__hfd = arr.dtype.categories.get_loc(val)
                ekuov__mgvsk = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                for dsb__bnt in range(ekuov__mgvsk.start, ekuov__mgvsk.stop,
                    ekuov__mgvsk.step):
                    arr.codes[dsb__bnt] = tshyl__hfd
            return impl_scalar
        if cdn__ktndc == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if cdn__ktndc == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(fieth__lzo)
                arr.codes[ind] = val.codes
            return impl_arr
        if alz__pzo:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                ekuov__mgvsk = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                efil__mrqg = 0
                for dsb__bnt in range(ekuov__mgvsk.start, ekuov__mgvsk.stop,
                    ekuov__mgvsk.step):
                    hecu__tyhkr = bodo.utils.conversion.unbox_if_timestamp(val
                        [efil__mrqg])
                    if hecu__tyhkr not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    yfd__ggmfw = categories.get_loc(hecu__tyhkr)
                    arr.codes[dsb__bnt] = yfd__ggmfw
                    efil__mrqg += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
