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
        pixr__icsha = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, pixr__icsha)


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
        glhla__yuak, qjg__lhhzu, uiqp__uigsb, kmf__godk = args
        upii__tch = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        upii__tch.data = glhla__yuak
        upii__tch.indices = qjg__lhhzu
        upii__tch.indptr = uiqp__uigsb
        upii__tch.shape = kmf__godk
        context.nrt.incref(builder, signature.args[0], glhla__yuak)
        context.nrt.incref(builder, signature.args[1], qjg__lhhzu)
        context.nrt.incref(builder, signature.args[2], uiqp__uigsb)
        return upii__tch._getvalue()
    rsdlx__adygl = CSRMatrixType(data_t.dtype, indices_t.dtype)
    idba__qkd = rsdlx__adygl(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return idba__qkd, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    upii__tch = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    awrg__cpb = c.pyapi.object_getattr_string(val, 'data')
    gff__nkzdk = c.pyapi.object_getattr_string(val, 'indices')
    gaab__eitmg = c.pyapi.object_getattr_string(val, 'indptr')
    wbu__kua = c.pyapi.object_getattr_string(val, 'shape')
    upii__tch.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        awrg__cpb).value
    upii__tch.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), gff__nkzdk).value
    upii__tch.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), gaab__eitmg).value
    upii__tch.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2
        ), wbu__kua).value
    c.pyapi.decref(awrg__cpb)
    c.pyapi.decref(gff__nkzdk)
    c.pyapi.decref(gaab__eitmg)
    c.pyapi.decref(wbu__kua)
    gype__loo = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(upii__tch._getvalue(), is_error=gype__loo)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    dgewz__vtlg = c.context.insert_const_string(c.builder.module,
        'scipy.sparse')
    wmj__wpmz = c.pyapi.import_module_noblock(dgewz__vtlg)
    upii__tch = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        upii__tch.data)
    awrg__cpb = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        upii__tch.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        upii__tch.indices)
    gff__nkzdk = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), upii__tch.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        upii__tch.indptr)
    gaab__eitmg = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), upii__tch.indptr, c.env_manager)
    wbu__kua = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        upii__tch.shape, c.env_manager)
    dkmt__fvyfr = c.pyapi.tuple_pack([awrg__cpb, gff__nkzdk, gaab__eitmg])
    soy__tqq = c.pyapi.call_method(wmj__wpmz, 'csr_matrix', (dkmt__fvyfr,
        wbu__kua))
    c.pyapi.decref(dkmt__fvyfr)
    c.pyapi.decref(awrg__cpb)
    c.pyapi.decref(gff__nkzdk)
    c.pyapi.decref(gaab__eitmg)
    c.pyapi.decref(wbu__kua)
    c.pyapi.decref(wmj__wpmz)
    c.context.nrt.decref(c.builder, typ, val)
    return soy__tqq


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
    vkh__rejv = A.dtype
    lei__qut = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            yhr__xcwm, ymosu__lkngo = A.shape
            bok__veko = numba.cpython.unicode._normalize_slice(idx[0],
                yhr__xcwm)
            flkmx__zpc = numba.cpython.unicode._normalize_slice(idx[1],
                ymosu__lkngo)
            if bok__veko.step != 1 or flkmx__zpc.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            oykm__vjq = bok__veko.start
            ywoo__pwtve = bok__veko.stop
            twzcs__imol = flkmx__zpc.start
            eqk__gaj = flkmx__zpc.stop
            lkvyr__jpwh = A.indptr
            gyzek__hdi = A.indices
            spq__drlya = A.data
            rnty__cisd = ywoo__pwtve - oykm__vjq
            czhqu__otsf = eqk__gaj - twzcs__imol
            eexx__jyg = 0
            kue__mme = 0
            for mxvum__kjckb in range(rnty__cisd):
                fjiia__wybaj = lkvyr__jpwh[oykm__vjq + mxvum__kjckb]
                krru__ljcp = lkvyr__jpwh[oykm__vjq + mxvum__kjckb + 1]
                for ots__juy in range(fjiia__wybaj, krru__ljcp):
                    if gyzek__hdi[ots__juy] >= twzcs__imol and gyzek__hdi[
                        ots__juy] < eqk__gaj:
                        eexx__jyg += 1
            doq__tqapq = np.empty(rnty__cisd + 1, lei__qut)
            gceq__vkecx = np.empty(eexx__jyg, lei__qut)
            gaswc__sdvqn = np.empty(eexx__jyg, vkh__rejv)
            doq__tqapq[0] = 0
            for mxvum__kjckb in range(rnty__cisd):
                fjiia__wybaj = lkvyr__jpwh[oykm__vjq + mxvum__kjckb]
                krru__ljcp = lkvyr__jpwh[oykm__vjq + mxvum__kjckb + 1]
                for ots__juy in range(fjiia__wybaj, krru__ljcp):
                    if gyzek__hdi[ots__juy] >= twzcs__imol and gyzek__hdi[
                        ots__juy] < eqk__gaj:
                        gceq__vkecx[kue__mme] = gyzek__hdi[ots__juy
                            ] - twzcs__imol
                        gaswc__sdvqn[kue__mme] = spq__drlya[ots__juy]
                        kue__mme += 1
                doq__tqapq[mxvum__kjckb + 1] = kue__mme
            return init_csr_matrix(gaswc__sdvqn, gceq__vkecx, doq__tqapq, (
                rnty__cisd, czhqu__otsf))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == lei__qut:

        def impl(A, idx):
            yhr__xcwm, ymosu__lkngo = A.shape
            lkvyr__jpwh = A.indptr
            gyzek__hdi = A.indices
            spq__drlya = A.data
            rnty__cisd = len(idx)
            eexx__jyg = 0
            kue__mme = 0
            for mxvum__kjckb in range(rnty__cisd):
                nuu__cevqw = idx[mxvum__kjckb]
                fjiia__wybaj = lkvyr__jpwh[nuu__cevqw]
                krru__ljcp = lkvyr__jpwh[nuu__cevqw + 1]
                eexx__jyg += krru__ljcp - fjiia__wybaj
            doq__tqapq = np.empty(rnty__cisd + 1, lei__qut)
            gceq__vkecx = np.empty(eexx__jyg, lei__qut)
            gaswc__sdvqn = np.empty(eexx__jyg, vkh__rejv)
            doq__tqapq[0] = 0
            for mxvum__kjckb in range(rnty__cisd):
                nuu__cevqw = idx[mxvum__kjckb]
                fjiia__wybaj = lkvyr__jpwh[nuu__cevqw]
                krru__ljcp = lkvyr__jpwh[nuu__cevqw + 1]
                gceq__vkecx[kue__mme:kue__mme + krru__ljcp - fjiia__wybaj
                    ] = gyzek__hdi[fjiia__wybaj:krru__ljcp]
                gaswc__sdvqn[kue__mme:kue__mme + krru__ljcp - fjiia__wybaj
                    ] = spq__drlya[fjiia__wybaj:krru__ljcp]
                kue__mme += krru__ljcp - fjiia__wybaj
                doq__tqapq[mxvum__kjckb + 1] = kue__mme
            koxea__xvta = init_csr_matrix(gaswc__sdvqn, gceq__vkecx,
                doq__tqapq, (rnty__cisd, ymosu__lkngo))
            return koxea__xvta
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
