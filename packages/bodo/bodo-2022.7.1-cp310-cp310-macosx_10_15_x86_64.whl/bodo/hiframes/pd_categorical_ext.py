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
        rffgj__khb = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=rffgj__khb)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    rpa__bdq = tuple(val.categories.values)
    elem_type = None if len(rpa__bdq) == 0 else bodo.typeof(val.categories.
        values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(rpa__bdq, elem_type, val.ordered, bodo.typeof
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
        iuw__gfjn = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, iuw__gfjn)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    olu__vfarh = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    qbi__sldla = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, dfxu__ipmh, dfxu__ipmh = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    dvwob__ehgd = PDCategoricalDtype(qbi__sldla, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, olu__vfarh)
    return dvwob__ehgd(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ejky__swd = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, ejky__swd).value
    c.pyapi.decref(ejky__swd)
    rfnro__cssu = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, rfnro__cssu).value
    c.pyapi.decref(rfnro__cssu)
    dghh__qizf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=dghh__qizf)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    ejky__swd = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    lopj__ilsr = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    llmzi__gflz = c.context.insert_const_string(c.builder.module, 'pandas')
    yuh__feomf = c.pyapi.import_module_noblock(llmzi__gflz)
    uxuao__conv = c.pyapi.call_method(yuh__feomf, 'CategoricalDtype', (
        lopj__ilsr, ejky__swd))
    c.pyapi.decref(ejky__swd)
    c.pyapi.decref(lopj__ilsr)
    c.pyapi.decref(yuh__feomf)
    c.context.nrt.decref(c.builder, typ, val)
    return uxuao__conv


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
        crch__pbmm = get_categories_int_type(fe_type.dtype)
        iuw__gfjn = [('dtype', fe_type.dtype), ('codes', types.Array(
            crch__pbmm, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, iuw__gfjn)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    zojur__snj = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), zojur__snj
        ).value
    c.pyapi.decref(zojur__snj)
    uxuao__conv = c.pyapi.object_getattr_string(val, 'dtype')
    cqpbg__otnnf = c.pyapi.to_native_value(typ.dtype, uxuao__conv).value
    c.pyapi.decref(uxuao__conv)
    mqgo__ssnk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mqgo__ssnk.codes = codes
    mqgo__ssnk.dtype = cqpbg__otnnf
    return NativeValue(mqgo__ssnk._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    smfr__febn = get_categories_int_type(typ.dtype)
    kkdz__eoea = context.get_constant_generic(builder, types.Array(
        smfr__febn, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, kkdz__eoea])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    gbpu__kpln = len(cat_dtype.categories)
    if gbpu__kpln < np.iinfo(np.int8).max:
        dtype = types.int8
    elif gbpu__kpln < np.iinfo(np.int16).max:
        dtype = types.int16
    elif gbpu__kpln < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    llmzi__gflz = c.context.insert_const_string(c.builder.module, 'pandas')
    yuh__feomf = c.pyapi.import_module_noblock(llmzi__gflz)
    crch__pbmm = get_categories_int_type(dtype)
    jqk__eol = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    sctd__mxqn = types.Array(crch__pbmm, 1, 'C')
    c.context.nrt.incref(c.builder, sctd__mxqn, jqk__eol.codes)
    zojur__snj = c.pyapi.from_native_value(sctd__mxqn, jqk__eol.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, jqk__eol.dtype)
    uxuao__conv = c.pyapi.from_native_value(dtype, jqk__eol.dtype, c.
        env_manager)
    dvye__bih = c.pyapi.borrow_none()
    wonl__yalg = c.pyapi.object_getattr_string(yuh__feomf, 'Categorical')
    ktnc__bxlgt = c.pyapi.call_method(wonl__yalg, 'from_codes', (zojur__snj,
        dvye__bih, dvye__bih, uxuao__conv))
    c.pyapi.decref(wonl__yalg)
    c.pyapi.decref(zojur__snj)
    c.pyapi.decref(uxuao__conv)
    c.pyapi.decref(yuh__feomf)
    c.context.nrt.decref(c.builder, typ, val)
    return ktnc__bxlgt


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
            rta__oygj = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                iplkm__vaac = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), rta__oygj)
                return iplkm__vaac
            return impl_lit

        def impl(A, other):
            rta__oygj = get_code_for_value(A.dtype, other)
            iplkm__vaac = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), rta__oygj)
            return iplkm__vaac
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        eihn__dhrr = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(eihn__dhrr)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    jqk__eol = cat_dtype.categories
    n = len(jqk__eol)
    for gqnk__owcj in range(n):
        if jqk__eol[gqnk__owcj] == val:
            return gqnk__owcj
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    nymp__uwjn = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype'
        )
    if nymp__uwjn != A.dtype.elem_type and nymp__uwjn != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if nymp__uwjn == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            iplkm__vaac = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for gqnk__owcj in numba.parfors.parfor.internal_prange(n):
                wrpu__kkrf = codes[gqnk__owcj]
                if wrpu__kkrf == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            iplkm__vaac, gqnk__owcj)
                    else:
                        bodo.libs.array_kernels.setna(iplkm__vaac, gqnk__owcj)
                    continue
                iplkm__vaac[gqnk__owcj] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[wrpu__kkrf]))
            return iplkm__vaac
        return impl
    sctd__mxqn = dtype_to_array_type(nymp__uwjn)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        iplkm__vaac = bodo.utils.utils.alloc_type(n, sctd__mxqn, (-1,))
        for gqnk__owcj in numba.parfors.parfor.internal_prange(n):
            wrpu__kkrf = codes[gqnk__owcj]
            if wrpu__kkrf == -1:
                bodo.libs.array_kernels.setna(iplkm__vaac, gqnk__owcj)
                continue
            iplkm__vaac[gqnk__owcj] = bodo.utils.conversion.unbox_if_timestamp(
                categories[wrpu__kkrf])
        return iplkm__vaac
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        aowr__kqypi, cqpbg__otnnf = args
        jqk__eol = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        jqk__eol.codes = aowr__kqypi
        jqk__eol.dtype = cqpbg__otnnf
        context.nrt.incref(builder, signature.args[0], aowr__kqypi)
        context.nrt.incref(builder, signature.args[1], cqpbg__otnnf)
        return jqk__eol._getvalue()
    lot__bzovr = CategoricalArrayType(cat_dtype)
    sig = lot__bzovr(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    zvcn__hyvf = args[0]
    if equiv_set.has_shape(zvcn__hyvf):
        return ArrayAnalysis.AnalyzeResult(shape=zvcn__hyvf, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    crch__pbmm = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, crch__pbmm)
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
            pryz__lllk = {}
            kkdz__eoea = np.empty(n + 1, np.int64)
            nhmfm__xys = {}
            djc__wlq = []
            jxts__vpo = {}
            for gqnk__owcj in range(n):
                jxts__vpo[categories[gqnk__owcj]] = gqnk__owcj
            for gjtn__hwv in to_replace:
                if gjtn__hwv != value:
                    if gjtn__hwv in jxts__vpo:
                        if value in jxts__vpo:
                            pryz__lllk[gjtn__hwv] = gjtn__hwv
                            sjag__uibsi = jxts__vpo[gjtn__hwv]
                            nhmfm__xys[sjag__uibsi] = jxts__vpo[value]
                            djc__wlq.append(sjag__uibsi)
                        else:
                            pryz__lllk[gjtn__hwv] = value
                            jxts__vpo[value] = jxts__vpo[gjtn__hwv]
            ddz__sxjq = np.sort(np.array(djc__wlq))
            sng__xjr = 0
            zxxcr__exom = []
            for howh__jis in range(-1, n):
                while sng__xjr < len(ddz__sxjq) and howh__jis > ddz__sxjq[
                    sng__xjr]:
                    sng__xjr += 1
                zxxcr__exom.append(sng__xjr)
            for pgmpz__jkly in range(-1, n):
                evmpi__xheoj = pgmpz__jkly
                if pgmpz__jkly in nhmfm__xys:
                    evmpi__xheoj = nhmfm__xys[pgmpz__jkly]
                kkdz__eoea[pgmpz__jkly + 1] = evmpi__xheoj - zxxcr__exom[
                    evmpi__xheoj + 1]
            return pryz__lllk, kkdz__eoea, len(ddz__sxjq)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for gqnk__owcj in range(len(new_codes_arr)):
        new_codes_arr[gqnk__owcj] = codes_map_arr[old_codes_arr[gqnk__owcj] + 1
            ]


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
    eut__pue = arr.dtype.ordered
    xju__zofvq = arr.dtype.elem_type
    hhfx__prir = get_overload_const(to_replace)
    vex__zswu = get_overload_const(value)
    if (arr.dtype.categories is not None and hhfx__prir is not NOT_CONSTANT and
        vex__zswu is not NOT_CONSTANT):
        iqtj__jsk, codes_map_arr, dfxu__ipmh = python_build_replace_dicts(
            hhfx__prir, vex__zswu, arr.dtype.categories)
        if len(iqtj__jsk) == 0:
            return lambda arr, to_replace, value: arr.copy()
        ftlg__bcaw = []
        for jblt__jzeq in arr.dtype.categories:
            if jblt__jzeq in iqtj__jsk:
                ifi__nyyve = iqtj__jsk[jblt__jzeq]
                if ifi__nyyve != jblt__jzeq:
                    ftlg__bcaw.append(ifi__nyyve)
            else:
                ftlg__bcaw.append(jblt__jzeq)
        qcnj__sewtb = bodo.utils.utils.create_categorical_type(ftlg__bcaw,
            arr.dtype.data.data, eut__pue)
        qtgf__ioq = MetaType(tuple(qcnj__sewtb))

        def impl_dtype(arr, to_replace, value):
            xts__zqz = init_cat_dtype(bodo.utils.conversion.
                index_from_array(qcnj__sewtb), eut__pue, None, qtgf__ioq)
            jqk__eol = alloc_categorical_array(len(arr.codes), xts__zqz)
            reassign_codes(jqk__eol.codes, arr.codes, codes_map_arr)
            return jqk__eol
        return impl_dtype
    xju__zofvq = arr.dtype.elem_type
    if xju__zofvq == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            pryz__lllk, codes_map_arr, scy__cjlvz = build_replace_dicts(
                to_replace, value, categories.values)
            if len(pryz__lllk) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), eut__pue,
                    None, None))
            n = len(categories)
            qcnj__sewtb = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                scy__cjlvz, -1)
            wcui__wkkzl = 0
            for howh__jis in range(n):
                zjlp__wmnqk = categories[howh__jis]
                if zjlp__wmnqk in pryz__lllk:
                    otxg__qnkv = pryz__lllk[zjlp__wmnqk]
                    if otxg__qnkv != zjlp__wmnqk:
                        qcnj__sewtb[wcui__wkkzl] = otxg__qnkv
                        wcui__wkkzl += 1
                else:
                    qcnj__sewtb[wcui__wkkzl] = zjlp__wmnqk
                    wcui__wkkzl += 1
            jqk__eol = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                qcnj__sewtb), eut__pue, None, None))
            reassign_codes(jqk__eol.codes, arr.codes, codes_map_arr)
            return jqk__eol
        return impl_str
    cmjpo__uylpj = dtype_to_array_type(xju__zofvq)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        pryz__lllk, codes_map_arr, scy__cjlvz = build_replace_dicts(to_replace,
            value, categories.values)
        if len(pryz__lllk) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), eut__pue, None, None))
        n = len(categories)
        qcnj__sewtb = bodo.utils.utils.alloc_type(n - scy__cjlvz,
            cmjpo__uylpj, None)
        wcui__wkkzl = 0
        for gqnk__owcj in range(n):
            zjlp__wmnqk = categories[gqnk__owcj]
            if zjlp__wmnqk in pryz__lllk:
                otxg__qnkv = pryz__lllk[zjlp__wmnqk]
                if otxg__qnkv != zjlp__wmnqk:
                    qcnj__sewtb[wcui__wkkzl] = otxg__qnkv
                    wcui__wkkzl += 1
            else:
                qcnj__sewtb[wcui__wkkzl] = zjlp__wmnqk
                wcui__wkkzl += 1
        jqk__eol = alloc_categorical_array(len(arr.codes), init_cat_dtype(
            bodo.utils.conversion.index_from_array(qcnj__sewtb), eut__pue,
            None, None))
        reassign_codes(jqk__eol.codes, arr.codes, codes_map_arr)
        return jqk__eol
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
    wunxp__tffe = dict()
    vbo__xht = 0
    for gqnk__owcj in range(len(vals)):
        val = vals[gqnk__owcj]
        if val in wunxp__tffe:
            continue
        wunxp__tffe[val] = vbo__xht
        vbo__xht += 1
    return wunxp__tffe


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    wunxp__tffe = dict()
    for gqnk__owcj in range(len(vals)):
        val = vals[gqnk__owcj]
        wunxp__tffe[val] = gqnk__owcj
    return wunxp__tffe


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    dxne__oade = dict(fastpath=fastpath)
    awp__lmglg = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', dxne__oade, awp__lmglg)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        bedd__vpv = get_overload_const(categories)
        if bedd__vpv is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                ajhm__guvk = False
            else:
                ajhm__guvk = get_overload_const_bool(ordered)
            ucwue__ddvnq = pd.CategoricalDtype(pd.array(bedd__vpv), ajhm__guvk
                ).categories.array
            scqtt__ehnx = MetaType(tuple(ucwue__ddvnq))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                xts__zqz = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(ucwue__ddvnq), ajhm__guvk, None,
                    scqtt__ehnx)
                return bodo.utils.conversion.fix_arr_dtype(data, xts__zqz)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            rpa__bdq = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                rpa__bdq, ordered, None, None)
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
            sto__tqbw = arr.codes[ind]
            return arr.dtype.categories[max(sto__tqbw, 0)]
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
    for gqnk__owcj in range(len(arr1)):
        if arr1[gqnk__owcj] != arr2[gqnk__owcj]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    xqaw__iyoqg = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    asqw__kiw = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    rmws__peiwr = categorical_arrs_match(arr, val)
    wxa__jlgrc = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    mieu__djraz = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not xqaw__iyoqg:
            raise BodoError(wxa__jlgrc)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            sto__tqbw = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = sto__tqbw
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (xqaw__iyoqg or asqw__kiw or rmws__peiwr !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(wxa__jlgrc)
        if rmws__peiwr == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mieu__djraz)
        if xqaw__iyoqg:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                rkzw__epytq = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for howh__jis in range(n):
                    arr.codes[ind[howh__jis]] = rkzw__epytq
            return impl_scalar
        if rmws__peiwr == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for gqnk__owcj in range(n):
                    arr.codes[ind[gqnk__owcj]] = val.codes[gqnk__owcj]
            return impl_arr_ind_mask
        if rmws__peiwr == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mieu__djraz)
                n = len(val.codes)
                for gqnk__owcj in range(n):
                    arr.codes[ind[gqnk__owcj]] = val.codes[gqnk__owcj]
            return impl_arr_ind_mask
        if asqw__kiw:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for howh__jis in range(n):
                    axhp__nfhcx = bodo.utils.conversion.unbox_if_timestamp(val
                        [howh__jis])
                    if axhp__nfhcx not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    sto__tqbw = categories.get_loc(axhp__nfhcx)
                    arr.codes[ind[howh__jis]] = sto__tqbw
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (xqaw__iyoqg or asqw__kiw or rmws__peiwr !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(wxa__jlgrc)
        if rmws__peiwr == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mieu__djraz)
        if xqaw__iyoqg:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                rkzw__epytq = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for howh__jis in range(n):
                    if ind[howh__jis]:
                        arr.codes[howh__jis] = rkzw__epytq
            return impl_scalar
        if rmws__peiwr == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                tkt__nrgjx = 0
                for gqnk__owcj in range(n):
                    if ind[gqnk__owcj]:
                        arr.codes[gqnk__owcj] = val.codes[tkt__nrgjx]
                        tkt__nrgjx += 1
            return impl_bool_ind_mask
        if rmws__peiwr == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mieu__djraz)
                n = len(ind)
                tkt__nrgjx = 0
                for gqnk__owcj in range(n):
                    if ind[gqnk__owcj]:
                        arr.codes[gqnk__owcj] = val.codes[tkt__nrgjx]
                        tkt__nrgjx += 1
            return impl_bool_ind_mask
        if asqw__kiw:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                tkt__nrgjx = 0
                categories = arr.dtype.categories
                for howh__jis in range(n):
                    if ind[howh__jis]:
                        axhp__nfhcx = bodo.utils.conversion.unbox_if_timestamp(
                            val[tkt__nrgjx])
                        if axhp__nfhcx not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        sto__tqbw = categories.get_loc(axhp__nfhcx)
                        arr.codes[howh__jis] = sto__tqbw
                        tkt__nrgjx += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (xqaw__iyoqg or asqw__kiw or rmws__peiwr !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(wxa__jlgrc)
        if rmws__peiwr == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mieu__djraz)
        if xqaw__iyoqg:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                rkzw__epytq = arr.dtype.categories.get_loc(val)
                kck__zplj = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                for howh__jis in range(kck__zplj.start, kck__zplj.stop,
                    kck__zplj.step):
                    arr.codes[howh__jis] = rkzw__epytq
            return impl_scalar
        if rmws__peiwr == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if rmws__peiwr == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mieu__djraz)
                arr.codes[ind] = val.codes
            return impl_arr
        if asqw__kiw:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                kck__zplj = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                tkt__nrgjx = 0
                for howh__jis in range(kck__zplj.start, kck__zplj.stop,
                    kck__zplj.step):
                    axhp__nfhcx = bodo.utils.conversion.unbox_if_timestamp(val
                        [tkt__nrgjx])
                    if axhp__nfhcx not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    sto__tqbw = categories.get_loc(axhp__nfhcx)
                    arr.codes[howh__jis] = sto__tqbw
                    tkt__nrgjx += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
