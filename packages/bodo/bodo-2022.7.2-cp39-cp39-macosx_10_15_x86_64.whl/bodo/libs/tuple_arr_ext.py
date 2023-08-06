"""Array of tuple values, implemented by reusing array of structs implementation.
"""
import operator
import numba
import numpy as np
from numba.core import types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.struct_arr_ext import StructArrayType, box_struct_arr, unbox_struct_array


class TupleArrayType(types.ArrayCompatible):

    def __init__(self, data):
        self.data = data
        super(TupleArrayType, self).__init__(name='TupleArrayType({})'.
            format(data))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.BaseTuple.from_types(tuple(gxz__aplua.dtype for
            gxz__aplua in self.data))

    def copy(self):
        return TupleArrayType(self.data)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(TupleArrayType)
class TupleArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tbkdz__tnaiz = [('data', StructArrayType(fe_type.data))]
        models.StructModel.__init__(self, dmm, fe_type, tbkdz__tnaiz)


make_attribute_wrapper(TupleArrayType, 'data', '_data')


@intrinsic
def init_tuple_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, StructArrayType)
    zpq__brx = TupleArrayType(data_typ.data)

    def codegen(context, builder, sig, args):
        lfe__biacq, = args
        jdoil__vgn = context.make_helper(builder, zpq__brx)
        jdoil__vgn.data = lfe__biacq
        context.nrt.incref(builder, data_typ, lfe__biacq)
        return jdoil__vgn._getvalue()
    return zpq__brx(data_typ), codegen


@unbox(TupleArrayType)
def unbox_tuple_array(typ, val, c):
    data_typ = StructArrayType(typ.data)
    qdfj__hbvfs = unbox_struct_array(data_typ, val, c, is_tuple_array=True)
    lfe__biacq = qdfj__hbvfs.value
    jdoil__vgn = c.context.make_helper(c.builder, typ)
    jdoil__vgn.data = lfe__biacq
    jva__kfitm = qdfj__hbvfs.is_error
    return NativeValue(jdoil__vgn._getvalue(), is_error=jva__kfitm)


@box(TupleArrayType)
def box_tuple_arr(typ, val, c):
    data_typ = StructArrayType(typ.data)
    jdoil__vgn = c.context.make_helper(c.builder, typ, val)
    arr = box_struct_arr(data_typ, jdoil__vgn.data, c, is_tuple_array=True)
    return arr


@numba.njit
def pre_alloc_tuple_array(n, nested_counts, dtypes):
    return init_tuple_arr(bodo.libs.struct_arr_ext.pre_alloc_struct_array(n,
        nested_counts, dtypes, None))


def pre_alloc_tuple_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_tuple_arr_ext_pre_alloc_tuple_array
    ) = pre_alloc_tuple_array_equiv


@overload(operator.getitem, no_unliteral=True)
def tuple_arr_getitem(arr, ind):
    if not isinstance(arr, TupleArrayType):
        return
    if isinstance(ind, types.Integer):
        pln__hdadm = 'def impl(arr, ind):\n'
        fjcyo__xovd = ','.join(f'get_data(arr._data)[{onimo__csg}][ind]' for
            onimo__csg in range(len(arr.data)))
        pln__hdadm += f'  return ({fjcyo__xovd})\n'
        dzflw__wrl = {}
        exec(pln__hdadm, {'get_data': bodo.libs.struct_arr_ext.get_data},
            dzflw__wrl)
        ivc__thc = dzflw__wrl['impl']
        return ivc__thc

    def impl_arr(arr, ind):
        return init_tuple_arr(arr._data[ind])
    return impl_arr


@overload(operator.setitem, no_unliteral=True)
def tuple_arr_setitem(arr, ind, val):
    if not isinstance(arr, TupleArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        odg__klx = len(arr.data)
        pln__hdadm = 'def impl(arr, ind, val):\n'
        pln__hdadm += '  data = get_data(arr._data)\n'
        pln__hdadm += '  null_bitmap = get_null_bitmap(arr._data)\n'
        pln__hdadm += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for onimo__csg in range(odg__klx):
            pln__hdadm += f'  data[{onimo__csg}][ind] = val[{onimo__csg}]\n'
        dzflw__wrl = {}
        exec(pln__hdadm, {'get_data': bodo.libs.struct_arr_ext.get_data,
            'get_null_bitmap': bodo.libs.struct_arr_ext.get_null_bitmap,
            'set_bit_to_arr': bodo.libs.int_arr_ext.set_bit_to_arr}, dzflw__wrl
            )
        ivc__thc = dzflw__wrl['impl']
        return ivc__thc

    def impl_arr(arr, ind, val):
        val = bodo.utils.conversion.coerce_to_array(val, use_nullable_array
            =True)
        arr._data[ind] = val._data
    return impl_arr


@overload(len, no_unliteral=True)
def overload_tuple_arr_len(A):
    if isinstance(A, TupleArrayType):
        return lambda A: len(A._data)


@overload_attribute(TupleArrayType, 'shape')
def overload_tuple_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(TupleArrayType, 'dtype')
def overload_tuple_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(TupleArrayType, 'ndim')
def overload_tuple_arr_ndim(A):
    return lambda A: 1


@overload_attribute(TupleArrayType, 'nbytes')
def overload_tuple_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(TupleArrayType, 'copy', no_unliteral=True)
def overload_tuple_arr_copy(A):

    def copy_impl(A):
        return init_tuple_arr(A._data.copy())
    return copy_impl
