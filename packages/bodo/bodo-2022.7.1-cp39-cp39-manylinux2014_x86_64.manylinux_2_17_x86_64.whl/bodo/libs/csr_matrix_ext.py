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
        dya__vqe = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, dya__vqe)


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
        texn__lvy, ncu__zrqh, pkwi__dquv, skvg__ttm = args
        eqh__bjy = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        eqh__bjy.data = texn__lvy
        eqh__bjy.indices = ncu__zrqh
        eqh__bjy.indptr = pkwi__dquv
        eqh__bjy.shape = skvg__ttm
        context.nrt.incref(builder, signature.args[0], texn__lvy)
        context.nrt.incref(builder, signature.args[1], ncu__zrqh)
        context.nrt.incref(builder, signature.args[2], pkwi__dquv)
        return eqh__bjy._getvalue()
    poo__lhtjx = CSRMatrixType(data_t.dtype, indices_t.dtype)
    qkwo__tbste = poo__lhtjx(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return qkwo__tbste, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    eqh__bjy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    azgwk__tewxx = c.pyapi.object_getattr_string(val, 'data')
    owln__vzd = c.pyapi.object_getattr_string(val, 'indices')
    vhgt__qujl = c.pyapi.object_getattr_string(val, 'indptr')
    yurv__vfe = c.pyapi.object_getattr_string(val, 'shape')
    eqh__bjy.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        azgwk__tewxx).value
    eqh__bjy.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), owln__vzd).value
    eqh__bjy.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), vhgt__qujl).value
    eqh__bjy.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2),
        yurv__vfe).value
    c.pyapi.decref(azgwk__tewxx)
    c.pyapi.decref(owln__vzd)
    c.pyapi.decref(vhgt__qujl)
    c.pyapi.decref(yurv__vfe)
    tlwyr__vaehs = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(eqh__bjy._getvalue(), is_error=tlwyr__vaehs)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    cpsyu__jvj = c.context.insert_const_string(c.builder.module, 'scipy.sparse'
        )
    iqus__oyww = c.pyapi.import_module_noblock(cpsyu__jvj)
    eqh__bjy = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        eqh__bjy.data)
    azgwk__tewxx = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        eqh__bjy.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        eqh__bjy.indices)
    owln__vzd = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), eqh__bjy.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        eqh__bjy.indptr)
    vhgt__qujl = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), eqh__bjy.indptr, c.env_manager)
    yurv__vfe = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        eqh__bjy.shape, c.env_manager)
    abb__fnt = c.pyapi.tuple_pack([azgwk__tewxx, owln__vzd, vhgt__qujl])
    eoqmt__fyok = c.pyapi.call_method(iqus__oyww, 'csr_matrix', (abb__fnt,
        yurv__vfe))
    c.pyapi.decref(abb__fnt)
    c.pyapi.decref(azgwk__tewxx)
    c.pyapi.decref(owln__vzd)
    c.pyapi.decref(vhgt__qujl)
    c.pyapi.decref(yurv__vfe)
    c.pyapi.decref(iqus__oyww)
    c.context.nrt.decref(c.builder, typ, val)
    return eoqmt__fyok


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
    nzgn__zjqs = A.dtype
    iuq__ntwk = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            uit__qkwer, kjl__szsax = A.shape
            btpg__hzwbd = numba.cpython.unicode._normalize_slice(idx[0],
                uit__qkwer)
            zfw__gtcq = numba.cpython.unicode._normalize_slice(idx[1],
                kjl__szsax)
            if btpg__hzwbd.step != 1 or zfw__gtcq.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            sjdlo__jvddi = btpg__hzwbd.start
            bjq__zrq = btpg__hzwbd.stop
            onvci__hdxb = zfw__gtcq.start
            mhxgt__fwmx = zfw__gtcq.stop
            alzne__voy = A.indptr
            ujklj__ijr = A.indices
            ycmlv__eyf = A.data
            rnkyv__yoyol = bjq__zrq - sjdlo__jvddi
            aqxfa__hjp = mhxgt__fwmx - onvci__hdxb
            vrua__upnll = 0
            filvu__yjf = 0
            for rtni__wjady in range(rnkyv__yoyol):
                mfky__kllyc = alzne__voy[sjdlo__jvddi + rtni__wjady]
                fjf__oese = alzne__voy[sjdlo__jvddi + rtni__wjady + 1]
                for fakja__wzs in range(mfky__kllyc, fjf__oese):
                    if ujklj__ijr[fakja__wzs] >= onvci__hdxb and ujklj__ijr[
                        fakja__wzs] < mhxgt__fwmx:
                        vrua__upnll += 1
            njj__oqh = np.empty(rnkyv__yoyol + 1, iuq__ntwk)
            soaid__zlem = np.empty(vrua__upnll, iuq__ntwk)
            kpkeu__izko = np.empty(vrua__upnll, nzgn__zjqs)
            njj__oqh[0] = 0
            for rtni__wjady in range(rnkyv__yoyol):
                mfky__kllyc = alzne__voy[sjdlo__jvddi + rtni__wjady]
                fjf__oese = alzne__voy[sjdlo__jvddi + rtni__wjady + 1]
                for fakja__wzs in range(mfky__kllyc, fjf__oese):
                    if ujklj__ijr[fakja__wzs] >= onvci__hdxb and ujklj__ijr[
                        fakja__wzs] < mhxgt__fwmx:
                        soaid__zlem[filvu__yjf] = ujklj__ijr[fakja__wzs
                            ] - onvci__hdxb
                        kpkeu__izko[filvu__yjf] = ycmlv__eyf[fakja__wzs]
                        filvu__yjf += 1
                njj__oqh[rtni__wjady + 1] = filvu__yjf
            return init_csr_matrix(kpkeu__izko, soaid__zlem, njj__oqh, (
                rnkyv__yoyol, aqxfa__hjp))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == iuq__ntwk:

        def impl(A, idx):
            uit__qkwer, kjl__szsax = A.shape
            alzne__voy = A.indptr
            ujklj__ijr = A.indices
            ycmlv__eyf = A.data
            rnkyv__yoyol = len(idx)
            vrua__upnll = 0
            filvu__yjf = 0
            for rtni__wjady in range(rnkyv__yoyol):
                tbpg__ftecw = idx[rtni__wjady]
                mfky__kllyc = alzne__voy[tbpg__ftecw]
                fjf__oese = alzne__voy[tbpg__ftecw + 1]
                vrua__upnll += fjf__oese - mfky__kllyc
            njj__oqh = np.empty(rnkyv__yoyol + 1, iuq__ntwk)
            soaid__zlem = np.empty(vrua__upnll, iuq__ntwk)
            kpkeu__izko = np.empty(vrua__upnll, nzgn__zjqs)
            njj__oqh[0] = 0
            for rtni__wjady in range(rnkyv__yoyol):
                tbpg__ftecw = idx[rtni__wjady]
                mfky__kllyc = alzne__voy[tbpg__ftecw]
                fjf__oese = alzne__voy[tbpg__ftecw + 1]
                soaid__zlem[filvu__yjf:filvu__yjf + fjf__oese - mfky__kllyc
                    ] = ujklj__ijr[mfky__kllyc:fjf__oese]
                kpkeu__izko[filvu__yjf:filvu__yjf + fjf__oese - mfky__kllyc
                    ] = ycmlv__eyf[mfky__kllyc:fjf__oese]
                filvu__yjf += fjf__oese - mfky__kllyc
                njj__oqh[rtni__wjady + 1] = filvu__yjf
            nnvk__twq = init_csr_matrix(kpkeu__izko, soaid__zlem, njj__oqh,
                (rnkyv__yoyol, kjl__szsax))
            return nnvk__twq
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
