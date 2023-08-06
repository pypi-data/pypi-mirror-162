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
        evye__rzdt = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, evye__rzdt)


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
        sqyd__jqutc = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        sqyd__jqutc.data = data_tuple
        sqyd__jqutc.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return sqyd__jqutc._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    yvcst__noxvr = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, yvcst__noxvr.data)
    c.context.nrt.incref(c.builder, typ.null_typ, yvcst__noxvr.null_values)
    joklw__svml = c.pyapi.from_native_value(typ.tuple_typ, yvcst__noxvr.
        data, c.env_manager)
    xzme__jyqcp = c.pyapi.from_native_value(typ.null_typ, yvcst__noxvr.
        null_values, c.env_manager)
    ocv__pnlwl = c.context.get_constant(types.int64, len(typ.tuple_typ))
    tbtv__prsib = c.pyapi.list_new(ocv__pnlwl)
    with cgutils.for_range(c.builder, ocv__pnlwl) as jgq__snj:
        i = jgq__snj.index
        zmhei__owm = c.pyapi.long_from_longlong(i)
        blv__qax = c.pyapi.object_getitem(xzme__jyqcp, zmhei__owm)
        qafe__wlqx = c.pyapi.to_native_value(types.bool_, blv__qax).value
        with c.builder.if_else(qafe__wlqx) as (fzis__lhvc, qpd__pbw):
            with fzis__lhvc:
                c.pyapi.list_setitem(tbtv__prsib, i, c.pyapi.make_none())
            with qpd__pbw:
                wxle__qco = c.pyapi.object_getitem(joklw__svml, zmhei__owm)
                c.pyapi.list_setitem(tbtv__prsib, i, wxle__qco)
        c.pyapi.decref(zmhei__owm)
        c.pyapi.decref(blv__qax)
    lvv__caji = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    fan__xzey = c.pyapi.call_function_objargs(lvv__caji, (tbtv__prsib,))
    c.pyapi.decref(joklw__svml)
    c.pyapi.decref(xzme__jyqcp)
    c.pyapi.decref(lvv__caji)
    c.pyapi.decref(tbtv__prsib)
    c.context.nrt.decref(c.builder, typ, val)
    return fan__xzey


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
    sqyd__jqutc = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (sqyd__jqutc.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    rco__quhm = 'def impl(val1, val2):\n'
    rco__quhm += '    data_tup1 = val1._data\n'
    rco__quhm += '    null_tup1 = val1._null_values\n'
    rco__quhm += '    data_tup2 = val2._data\n'
    rco__quhm += '    null_tup2 = val2._null_values\n'
    tquuo__gqnll = val1._tuple_typ
    for i in range(len(tquuo__gqnll)):
        rco__quhm += f'    null1_{i} = null_tup1[{i}]\n'
        rco__quhm += f'    null2_{i} = null_tup2[{i}]\n'
        rco__quhm += f'    data1_{i} = data_tup1[{i}]\n'
        rco__quhm += f'    data2_{i} = data_tup2[{i}]\n'
        rco__quhm += f'    if null1_{i} != null2_{i}:\n'
        rco__quhm += '        return False\n'
        rco__quhm += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        rco__quhm += f'        return False\n'
    rco__quhm += f'    return True\n'
    gpth__jutu = {}
    exec(rco__quhm, {}, gpth__jutu)
    impl = gpth__jutu['impl']
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
    rco__quhm = 'def impl(nullable_tup):\n'
    rco__quhm += '    data_tup = nullable_tup._data\n'
    rco__quhm += '    null_tup = nullable_tup._null_values\n'
    rco__quhm += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    rco__quhm += '    acc = _PyHASH_XXPRIME_5\n'
    tquuo__gqnll = nullable_tup._tuple_typ
    for i in range(len(tquuo__gqnll)):
        rco__quhm += f'    null_val_{i} = null_tup[{i}]\n'
        rco__quhm += f'    null_lane_{i} = hash(null_val_{i})\n'
        rco__quhm += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        rco__quhm += '        return -1\n'
        rco__quhm += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        rco__quhm += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        rco__quhm += '    acc *= _PyHASH_XXPRIME_1\n'
        rco__quhm += f'    if not null_val_{i}:\n'
        rco__quhm += f'        lane_{i} = hash(data_tup[{i}])\n'
        rco__quhm += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        rco__quhm += f'            return -1\n'
        rco__quhm += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        rco__quhm += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        rco__quhm += '        acc *= _PyHASH_XXPRIME_1\n'
    rco__quhm += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    rco__quhm += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    rco__quhm += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    rco__quhm += '    return numba.cpython.hashing.process_return(acc)\n'
    gpth__jutu = {}
    exec(rco__quhm, {'numba': numba, '_PyHASH_XXPRIME_1': _PyHASH_XXPRIME_1,
        '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2, '_PyHASH_XXPRIME_5':
        _PyHASH_XXPRIME_5}, gpth__jutu)
    impl = gpth__jutu['impl']
    return impl
