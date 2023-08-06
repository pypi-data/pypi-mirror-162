"""CSR Matrix data type implementation for scipy.sparse.csr_matrix
"""
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.utils.typing import BodoError


class CSRMatrixType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, dtype, idx_dtype):
        self.dtype = dtype
        self.idx_dtype = idx_dtype
        super(CSRMatrixType, self).__init__(name=
            f'CSRMatrixType({dtype}, {idx_dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    def copy(self):
        return CSRMatrixType(self.dtype, self.idx_dtype)


@register_model(CSRMatrixType)
class CSRMatrixModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnzgz__luyi = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, fnzgz__luyi)


make_attribute_wrapper(CSRMatrixType, 'data', 'data')
make_attribute_wrapper(CSRMatrixType, 'indices', 'indices')
make_attribute_wrapper(CSRMatrixType, 'indptr', 'indptr')
make_attribute_wrapper(CSRMatrixType, 'shape', 'shape')


@intrinsic
def init_csr_matrix(typingctx, data_t, indices_t, indptr_t, shape_t=None):
    assert isinstance(data_t, types.Array)
    assert isinstance(indices_t, types.Array) and isinstance(indices_t.
        dtype, types.Integer)
    assert indices_t == indptr_t

    def codegen(context, builder, signature, args):
        xmazb__cgznt, ticig__elrc, nisfa__xwf, lir__nel = args
        upl__nbn = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        upl__nbn.data = xmazb__cgznt
        upl__nbn.indices = ticig__elrc
        upl__nbn.indptr = nisfa__xwf
        upl__nbn.shape = lir__nel
        context.nrt.incref(builder, signature.args[0], xmazb__cgznt)
        context.nrt.incref(builder, signature.args[1], ticig__elrc)
        context.nrt.incref(builder, signature.args[2], nisfa__xwf)
        return upl__nbn._getvalue()
    xvmgr__otp = CSRMatrixType(data_t.dtype, indices_t.dtype)
    eaadd__xqld = xvmgr__otp(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return eaadd__xqld, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    upl__nbn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    atar__nol = c.pyapi.object_getattr_string(val, 'data')
    mlp__fuktj = c.pyapi.object_getattr_string(val, 'indices')
    hlc__vacu = c.pyapi.object_getattr_string(val, 'indptr')
    qsvx__udtr = c.pyapi.object_getattr_string(val, 'shape')
    upl__nbn.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        atar__nol).value
    upl__nbn.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), mlp__fuktj).value
    upl__nbn.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), hlc__vacu).value
    upl__nbn.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2),
        qsvx__udtr).value
    c.pyapi.decref(atar__nol)
    c.pyapi.decref(mlp__fuktj)
    c.pyapi.decref(hlc__vacu)
    c.pyapi.decref(qsvx__udtr)
    mzj__pyrj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(upl__nbn._getvalue(), is_error=mzj__pyrj)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    nfs__orr = c.context.insert_const_string(c.builder.module, 'scipy.sparse')
    enuon__hzmjf = c.pyapi.import_module_noblock(nfs__orr)
    upl__nbn = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        upl__nbn.data)
    atar__nol = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        upl__nbn.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        upl__nbn.indices)
    mlp__fuktj = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), upl__nbn.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        upl__nbn.indptr)
    hlc__vacu = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), upl__nbn.indptr, c.env_manager)
    qsvx__udtr = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        upl__nbn.shape, c.env_manager)
    ivzn__kkkcg = c.pyapi.tuple_pack([atar__nol, mlp__fuktj, hlc__vacu])
    nqqze__vihv = c.pyapi.call_method(enuon__hzmjf, 'csr_matrix', (
        ivzn__kkkcg, qsvx__udtr))
    c.pyapi.decref(ivzn__kkkcg)
    c.pyapi.decref(atar__nol)
    c.pyapi.decref(mlp__fuktj)
    c.pyapi.decref(hlc__vacu)
    c.pyapi.decref(qsvx__udtr)
    c.pyapi.decref(enuon__hzmjf)
    c.context.nrt.decref(c.builder, typ, val)
    return nqqze__vihv


@overload(len, no_unliteral=True)
def overload_csr_matrix_len(A):
    if isinstance(A, CSRMatrixType):
        return lambda A: A.shape[0]


@overload_attribute(CSRMatrixType, 'ndim')
def overload_csr_matrix_ndim(A):
    return lambda A: 2


@overload_method(CSRMatrixType, 'copy', no_unliteral=True)
def overload_csr_matrix_copy(A):

    def copy_impl(A):
        return init_csr_matrix(A.data.copy(), A.indices.copy(), A.indptr.
            copy(), A.shape)
    return copy_impl


@overload(operator.getitem, no_unliteral=True)
def csr_matrix_getitem(A, idx):
    if not isinstance(A, CSRMatrixType):
        return
    bbu__gprlm = A.dtype
    mufi__kxjph = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            gdabk__sxhor, uok__czoz = A.shape
            bnpoc__gbd = numba.cpython.unicode._normalize_slice(idx[0],
                gdabk__sxhor)
            aszwn__eqnx = numba.cpython.unicode._normalize_slice(idx[1],
                uok__czoz)
            if bnpoc__gbd.step != 1 or aszwn__eqnx.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            yirwk__bdbb = bnpoc__gbd.start
            tqzv__jjsu = bnpoc__gbd.stop
            akez__bqbk = aszwn__eqnx.start
            zlh__neb = aszwn__eqnx.stop
            twef__tnbkw = A.indptr
            ihq__uhk = A.indices
            zxb__qyeko = A.data
            txosr__dyah = tqzv__jjsu - yirwk__bdbb
            zqvsh__ujldu = zlh__neb - akez__bqbk
            igp__nhaxo = 0
            xqlj__gkw = 0
            for fohdq__uoiim in range(txosr__dyah):
                jquv__kosv = twef__tnbkw[yirwk__bdbb + fohdq__uoiim]
                ellv__krrgi = twef__tnbkw[yirwk__bdbb + fohdq__uoiim + 1]
                for zikhp__mfzgs in range(jquv__kosv, ellv__krrgi):
                    if ihq__uhk[zikhp__mfzgs] >= akez__bqbk and ihq__uhk[
                        zikhp__mfzgs] < zlh__neb:
                        igp__nhaxo += 1
            tzqyz__jluo = np.empty(txosr__dyah + 1, mufi__kxjph)
            frhfb__frcis = np.empty(igp__nhaxo, mufi__kxjph)
            umrr__bvbf = np.empty(igp__nhaxo, bbu__gprlm)
            tzqyz__jluo[0] = 0
            for fohdq__uoiim in range(txosr__dyah):
                jquv__kosv = twef__tnbkw[yirwk__bdbb + fohdq__uoiim]
                ellv__krrgi = twef__tnbkw[yirwk__bdbb + fohdq__uoiim + 1]
                for zikhp__mfzgs in range(jquv__kosv, ellv__krrgi):
                    if ihq__uhk[zikhp__mfzgs] >= akez__bqbk and ihq__uhk[
                        zikhp__mfzgs] < zlh__neb:
                        frhfb__frcis[xqlj__gkw] = ihq__uhk[zikhp__mfzgs
                            ] - akez__bqbk
                        umrr__bvbf[xqlj__gkw] = zxb__qyeko[zikhp__mfzgs]
                        xqlj__gkw += 1
                tzqyz__jluo[fohdq__uoiim + 1] = xqlj__gkw
            return init_csr_matrix(umrr__bvbf, frhfb__frcis, tzqyz__jluo, (
                txosr__dyah, zqvsh__ujldu))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == mufi__kxjph:

        def impl(A, idx):
            gdabk__sxhor, uok__czoz = A.shape
            twef__tnbkw = A.indptr
            ihq__uhk = A.indices
            zxb__qyeko = A.data
            txosr__dyah = len(idx)
            igp__nhaxo = 0
            xqlj__gkw = 0
            for fohdq__uoiim in range(txosr__dyah):
                swys__rbd = idx[fohdq__uoiim]
                jquv__kosv = twef__tnbkw[swys__rbd]
                ellv__krrgi = twef__tnbkw[swys__rbd + 1]
                igp__nhaxo += ellv__krrgi - jquv__kosv
            tzqyz__jluo = np.empty(txosr__dyah + 1, mufi__kxjph)
            frhfb__frcis = np.empty(igp__nhaxo, mufi__kxjph)
            umrr__bvbf = np.empty(igp__nhaxo, bbu__gprlm)
            tzqyz__jluo[0] = 0
            for fohdq__uoiim in range(txosr__dyah):
                swys__rbd = idx[fohdq__uoiim]
                jquv__kosv = twef__tnbkw[swys__rbd]
                ellv__krrgi = twef__tnbkw[swys__rbd + 1]
                frhfb__frcis[xqlj__gkw:xqlj__gkw + ellv__krrgi - jquv__kosv
                    ] = ihq__uhk[jquv__kosv:ellv__krrgi]
                umrr__bvbf[xqlj__gkw:xqlj__gkw + ellv__krrgi - jquv__kosv
                    ] = zxb__qyeko[jquv__kosv:ellv__krrgi]
                xqlj__gkw += ellv__krrgi - jquv__kosv
                tzqyz__jluo[fohdq__uoiim + 1] = xqlj__gkw
            bwnz__xjw = init_csr_matrix(umrr__bvbf, frhfb__frcis,
                tzqyz__jluo, (txosr__dyah, uok__czoz))
            return bwnz__xjw
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
