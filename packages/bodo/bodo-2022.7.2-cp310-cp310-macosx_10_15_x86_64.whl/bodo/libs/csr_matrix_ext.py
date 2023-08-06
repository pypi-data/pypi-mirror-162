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
        vqofs__aygh = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, vqofs__aygh)


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
        ggy__koyaw, rvwi__dlp, efw__ujnif, zpcxd__dwj = args
        iou__udpx = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        iou__udpx.data = ggy__koyaw
        iou__udpx.indices = rvwi__dlp
        iou__udpx.indptr = efw__ujnif
        iou__udpx.shape = zpcxd__dwj
        context.nrt.incref(builder, signature.args[0], ggy__koyaw)
        context.nrt.incref(builder, signature.args[1], rvwi__dlp)
        context.nrt.incref(builder, signature.args[2], efw__ujnif)
        return iou__udpx._getvalue()
    dwbad__vuuj = CSRMatrixType(data_t.dtype, indices_t.dtype)
    wmxpu__cyqrv = dwbad__vuuj(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return wmxpu__cyqrv, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    iou__udpx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xwf__hxy = c.pyapi.object_getattr_string(val, 'data')
    sbh__ylpxp = c.pyapi.object_getattr_string(val, 'indices')
    tgx__xbou = c.pyapi.object_getattr_string(val, 'indptr')
    tqqtl__ltyup = c.pyapi.object_getattr_string(val, 'shape')
    iou__udpx.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        xwf__hxy).value
    iou__udpx.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), sbh__ylpxp).value
    iou__udpx.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), tgx__xbou).value
    iou__udpx.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2
        ), tqqtl__ltyup).value
    c.pyapi.decref(xwf__hxy)
    c.pyapi.decref(sbh__ylpxp)
    c.pyapi.decref(tgx__xbou)
    c.pyapi.decref(tqqtl__ltyup)
    cxjeq__fqpb = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(iou__udpx._getvalue(), is_error=cxjeq__fqpb)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    fgsax__smmp = c.context.insert_const_string(c.builder.module,
        'scipy.sparse')
    cmw__ugy = c.pyapi.import_module_noblock(fgsax__smmp)
    iou__udpx = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        iou__udpx.data)
    xwf__hxy = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        iou__udpx.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        iou__udpx.indices)
    sbh__ylpxp = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), iou__udpx.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        iou__udpx.indptr)
    tgx__xbou = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), iou__udpx.indptr, c.env_manager)
    tqqtl__ltyup = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        iou__udpx.shape, c.env_manager)
    gbtqz__xzhgb = c.pyapi.tuple_pack([xwf__hxy, sbh__ylpxp, tgx__xbou])
    jclt__xjd = c.pyapi.call_method(cmw__ugy, 'csr_matrix', (gbtqz__xzhgb,
        tqqtl__ltyup))
    c.pyapi.decref(gbtqz__xzhgb)
    c.pyapi.decref(xwf__hxy)
    c.pyapi.decref(sbh__ylpxp)
    c.pyapi.decref(tgx__xbou)
    c.pyapi.decref(tqqtl__ltyup)
    c.pyapi.decref(cmw__ugy)
    c.context.nrt.decref(c.builder, typ, val)
    return jclt__xjd


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
    dngu__ifw = A.dtype
    amkbs__ojj = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            vjx__riy, tclsl__tdy = A.shape
            hivqt__zde = numba.cpython.unicode._normalize_slice(idx[0],
                vjx__riy)
            ezvg__ibwxd = numba.cpython.unicode._normalize_slice(idx[1],
                tclsl__tdy)
            if hivqt__zde.step != 1 or ezvg__ibwxd.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            bzak__omjf = hivqt__zde.start
            jcjca__loz = hivqt__zde.stop
            rmwhg__raw = ezvg__ibwxd.start
            qahd__dsd = ezvg__ibwxd.stop
            heuxe__fzn = A.indptr
            dsh__cdgi = A.indices
            uot__phk = A.data
            awwhg__xwn = jcjca__loz - bzak__omjf
            dzbq__hhvei = qahd__dsd - rmwhg__raw
            gydbx__porx = 0
            bqh__bonor = 0
            for ujha__edkl in range(awwhg__xwn):
                uqo__hlro = heuxe__fzn[bzak__omjf + ujha__edkl]
                lwul__ctnm = heuxe__fzn[bzak__omjf + ujha__edkl + 1]
                for paa__apbnu in range(uqo__hlro, lwul__ctnm):
                    if dsh__cdgi[paa__apbnu] >= rmwhg__raw and dsh__cdgi[
                        paa__apbnu] < qahd__dsd:
                        gydbx__porx += 1
            fnag__ugtq = np.empty(awwhg__xwn + 1, amkbs__ojj)
            oeh__qrhgj = np.empty(gydbx__porx, amkbs__ojj)
            amxaz__zms = np.empty(gydbx__porx, dngu__ifw)
            fnag__ugtq[0] = 0
            for ujha__edkl in range(awwhg__xwn):
                uqo__hlro = heuxe__fzn[bzak__omjf + ujha__edkl]
                lwul__ctnm = heuxe__fzn[bzak__omjf + ujha__edkl + 1]
                for paa__apbnu in range(uqo__hlro, lwul__ctnm):
                    if dsh__cdgi[paa__apbnu] >= rmwhg__raw and dsh__cdgi[
                        paa__apbnu] < qahd__dsd:
                        oeh__qrhgj[bqh__bonor] = dsh__cdgi[paa__apbnu
                            ] - rmwhg__raw
                        amxaz__zms[bqh__bonor] = uot__phk[paa__apbnu]
                        bqh__bonor += 1
                fnag__ugtq[ujha__edkl + 1] = bqh__bonor
            return init_csr_matrix(amxaz__zms, oeh__qrhgj, fnag__ugtq, (
                awwhg__xwn, dzbq__hhvei))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == amkbs__ojj:

        def impl(A, idx):
            vjx__riy, tclsl__tdy = A.shape
            heuxe__fzn = A.indptr
            dsh__cdgi = A.indices
            uot__phk = A.data
            awwhg__xwn = len(idx)
            gydbx__porx = 0
            bqh__bonor = 0
            for ujha__edkl in range(awwhg__xwn):
                qpd__auj = idx[ujha__edkl]
                uqo__hlro = heuxe__fzn[qpd__auj]
                lwul__ctnm = heuxe__fzn[qpd__auj + 1]
                gydbx__porx += lwul__ctnm - uqo__hlro
            fnag__ugtq = np.empty(awwhg__xwn + 1, amkbs__ojj)
            oeh__qrhgj = np.empty(gydbx__porx, amkbs__ojj)
            amxaz__zms = np.empty(gydbx__porx, dngu__ifw)
            fnag__ugtq[0] = 0
            for ujha__edkl in range(awwhg__xwn):
                qpd__auj = idx[ujha__edkl]
                uqo__hlro = heuxe__fzn[qpd__auj]
                lwul__ctnm = heuxe__fzn[qpd__auj + 1]
                oeh__qrhgj[bqh__bonor:bqh__bonor + lwul__ctnm - uqo__hlro
                    ] = dsh__cdgi[uqo__hlro:lwul__ctnm]
                amxaz__zms[bqh__bonor:bqh__bonor + lwul__ctnm - uqo__hlro
                    ] = uot__phk[uqo__hlro:lwul__ctnm]
                bqh__bonor += lwul__ctnm - uqo__hlro
                fnag__ugtq[ujha__edkl + 1] = bqh__bonor
            cbub__lsvfg = init_csr_matrix(amxaz__zms, oeh__qrhgj,
                fnag__ugtq, (awwhg__xwn, tclsl__tdy))
            return cbub__lsvfg
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
