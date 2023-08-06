"""
Wrapper class for Tuples that supports tracking null entries.
This is primarily used for maintaining null information for
Series values used in df.apply
"""
import operator
import numba
from numba.core import cgutils, types
from numba.extending import box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model


class NullableTupleType(types.IterableType):

    def __init__(self, tuple_typ, null_typ):
        self._tuple_typ = tuple_typ
        self._null_typ = null_typ
        super(NullableTupleType, self).__init__(name=
            f'NullableTupleType({tuple_typ}, {null_typ})')

    @property
    def tuple_typ(self):
        return self._tuple_typ

    @property
    def null_typ(self):
        return self._null_typ

    def __getitem__(self, i):
        return self._tuple_typ[i]

    @property
    def key(self):
        return self._tuple_typ

    @property
    def dtype(self):
        return self.tuple_typ.dtype

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def iterator_type(self):
        return self.tuple_typ.iterator_type

    def __len__(self):
        return len(self.tuple_typ)


@register_model(NullableTupleType)
class NullableTupleModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        llde__kko = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, llde__kko)


make_attribute_wrapper(NullableTupleType, 'data', '_data')
make_attribute_wrapper(NullableTupleType, 'null_values', '_null_values')


@intrinsic
def build_nullable_tuple(typingctx, data_tuple, null_values):
    assert isinstance(data_tuple, types.BaseTuple
        ), "build_nullable_tuple 'data_tuple' argument must be a tuple"
    assert isinstance(null_values, types.BaseTuple
        ), "build_nullable_tuple 'null_values' argument must be a tuple"
    data_tuple = types.unliteral(data_tuple)
    null_values = types.unliteral(null_values)

    def codegen(context, builder, signature, args):
        data_tuple, null_values = args
        ccdr__cbrk = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ccdr__cbrk.data = data_tuple
        ccdr__cbrk.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return ccdr__cbrk._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    irmpt__mxo = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, irmpt__mxo.data)
    c.context.nrt.incref(c.builder, typ.null_typ, irmpt__mxo.null_values)
    ies__acx = c.pyapi.from_native_value(typ.tuple_typ, irmpt__mxo.data, c.
        env_manager)
    wikfv__sbywd = c.pyapi.from_native_value(typ.null_typ, irmpt__mxo.
        null_values, c.env_manager)
    gbec__buce = c.context.get_constant(types.int64, len(typ.tuple_typ))
    coo__itd = c.pyapi.list_new(gbec__buce)
    with cgutils.for_range(c.builder, gbec__buce) as fvj__ddq:
        i = fvj__ddq.index
        pzdh__qzb = c.pyapi.long_from_longlong(i)
        hkn__dxsa = c.pyapi.object_getitem(wikfv__sbywd, pzdh__qzb)
        gyrp__xgfei = c.pyapi.to_native_value(types.bool_, hkn__dxsa).value
        with c.builder.if_else(gyrp__xgfei) as (zshhy__puix, ehj__uehj):
            with zshhy__puix:
                c.pyapi.list_setitem(coo__itd, i, c.pyapi.make_none())
            with ehj__uehj:
                xlokz__zaspj = c.pyapi.object_getitem(ies__acx, pzdh__qzb)
                c.pyapi.list_setitem(coo__itd, i, xlokz__zaspj)
        c.pyapi.decref(pzdh__qzb)
        c.pyapi.decref(hkn__dxsa)
    wvj__asi = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    zui__ekes = c.pyapi.call_function_objargs(wvj__asi, (coo__itd,))
    c.pyapi.decref(ies__acx)
    c.pyapi.decref(wikfv__sbywd)
    c.pyapi.decref(wvj__asi)
    c.pyapi.decref(coo__itd)
    c.context.nrt.decref(c.builder, typ, val)
    return zui__ekes


@overload(operator.getitem)
def overload_getitem(A, idx):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A, idx: A._data[idx]


@overload(len)
def overload_len(A):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A: len(A._data)


@lower_builtin('getiter', NullableTupleType)
def nullable_tuple_getiter(context, builder, sig, args):
    ccdr__cbrk = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (ccdr__cbrk.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    dpk__quf = 'def impl(val1, val2):\n'
    dpk__quf += '    data_tup1 = val1._data\n'
    dpk__quf += '    null_tup1 = val1._null_values\n'
    dpk__quf += '    data_tup2 = val2._data\n'
    dpk__quf += '    null_tup2 = val2._null_values\n'
    tnjh__ucq = val1._tuple_typ
    for i in range(len(tnjh__ucq)):
        dpk__quf += f'    null1_{i} = null_tup1[{i}]\n'
        dpk__quf += f'    null2_{i} = null_tup2[{i}]\n'
        dpk__quf += f'    data1_{i} = data_tup1[{i}]\n'
        dpk__quf += f'    data2_{i} = data_tup2[{i}]\n'
        dpk__quf += f'    if null1_{i} != null2_{i}:\n'
        dpk__quf += '        return False\n'
        dpk__quf += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        dpk__quf += f'        return False\n'
    dpk__quf += f'    return True\n'
    hsas__pqp = {}
    exec(dpk__quf, {}, hsas__pqp)
    impl = hsas__pqp['impl']
    return impl


@overload_method(NullableTupleType, '__hash__')
def nullable_tuple_hash(val):

    def impl(val):
        return _nullable_tuple_hash(val)
    return impl


_PyHASH_XXPRIME_1 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_2 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_5 = numba.cpython.hashing._PyHASH_XXPRIME_1


@numba.generated_jit(nopython=True)
def _nullable_tuple_hash(nullable_tup):
    dpk__quf = 'def impl(nullable_tup):\n'
    dpk__quf += '    data_tup = nullable_tup._data\n'
    dpk__quf += '    null_tup = nullable_tup._null_values\n'
    dpk__quf += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    dpk__quf += '    acc = _PyHASH_XXPRIME_5\n'
    tnjh__ucq = nullable_tup._tuple_typ
    for i in range(len(tnjh__ucq)):
        dpk__quf += f'    null_val_{i} = null_tup[{i}]\n'
        dpk__quf += f'    null_lane_{i} = hash(null_val_{i})\n'
        dpk__quf += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        dpk__quf += '        return -1\n'
        dpk__quf += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        dpk__quf += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        dpk__quf += '    acc *= _PyHASH_XXPRIME_1\n'
        dpk__quf += f'    if not null_val_{i}:\n'
        dpk__quf += f'        lane_{i} = hash(data_tup[{i}])\n'
        dpk__quf += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        dpk__quf += f'            return -1\n'
        dpk__quf += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        dpk__quf += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        dpk__quf += '        acc *= _PyHASH_XXPRIME_1\n'
    dpk__quf += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    dpk__quf += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    dpk__quf += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    dpk__quf += '    return numba.cpython.hashing.process_return(acc)\n'
    hsas__pqp = {}
    exec(dpk__quf, {'numba': numba, '_PyHASH_XXPRIME_1': _PyHASH_XXPRIME_1,
        '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2, '_PyHASH_XXPRIME_5':
        _PyHASH_XXPRIME_5}, hsas__pqp)
    impl = hsas__pqp['impl']
    return impl
