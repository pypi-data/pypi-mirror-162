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
        klym__ncbh = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, klym__ncbh)


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
        bbo__ilc = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        bbo__ilc.data = data_tuple
        bbo__ilc.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return bbo__ilc._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    genvq__ycj = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, genvq__ycj.data)
    c.context.nrt.incref(c.builder, typ.null_typ, genvq__ycj.null_values)
    hupxq__rzxl = c.pyapi.from_native_value(typ.tuple_typ, genvq__ycj.data,
        c.env_manager)
    hxq__lsd = c.pyapi.from_native_value(typ.null_typ, genvq__ycj.
        null_values, c.env_manager)
    ohmj__ruwy = c.context.get_constant(types.int64, len(typ.tuple_typ))
    ffu__nhqd = c.pyapi.list_new(ohmj__ruwy)
    with cgutils.for_range(c.builder, ohmj__ruwy) as dzd__swurb:
        i = dzd__swurb.index
        tcw__mvkzj = c.pyapi.long_from_longlong(i)
        fwwfj__pygqf = c.pyapi.object_getitem(hxq__lsd, tcw__mvkzj)
        kur__azj = c.pyapi.to_native_value(types.bool_, fwwfj__pygqf).value
        with c.builder.if_else(kur__azj) as (qzqcs__tbg, aokeh__kkxpp):
            with qzqcs__tbg:
                c.pyapi.list_setitem(ffu__nhqd, i, c.pyapi.make_none())
            with aokeh__kkxpp:
                oibqp__apoc = c.pyapi.object_getitem(hupxq__rzxl, tcw__mvkzj)
                c.pyapi.list_setitem(ffu__nhqd, i, oibqp__apoc)
        c.pyapi.decref(tcw__mvkzj)
        c.pyapi.decref(fwwfj__pygqf)
    nje__fazl = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    zssqr__xhtd = c.pyapi.call_function_objargs(nje__fazl, (ffu__nhqd,))
    c.pyapi.decref(hupxq__rzxl)
    c.pyapi.decref(hxq__lsd)
    c.pyapi.decref(nje__fazl)
    c.pyapi.decref(ffu__nhqd)
    c.context.nrt.decref(c.builder, typ, val)
    return zssqr__xhtd


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
    bbo__ilc = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (bbo__ilc.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    yvplk__igbrj = 'def impl(val1, val2):\n'
    yvplk__igbrj += '    data_tup1 = val1._data\n'
    yvplk__igbrj += '    null_tup1 = val1._null_values\n'
    yvplk__igbrj += '    data_tup2 = val2._data\n'
    yvplk__igbrj += '    null_tup2 = val2._null_values\n'
    pdzlh__lyann = val1._tuple_typ
    for i in range(len(pdzlh__lyann)):
        yvplk__igbrj += f'    null1_{i} = null_tup1[{i}]\n'
        yvplk__igbrj += f'    null2_{i} = null_tup2[{i}]\n'
        yvplk__igbrj += f'    data1_{i} = data_tup1[{i}]\n'
        yvplk__igbrj += f'    data2_{i} = data_tup2[{i}]\n'
        yvplk__igbrj += f'    if null1_{i} != null2_{i}:\n'
        yvplk__igbrj += '        return False\n'
        yvplk__igbrj += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        yvplk__igbrj += f'        return False\n'
    yvplk__igbrj += f'    return True\n'
    mtxxp__fsuk = {}
    exec(yvplk__igbrj, {}, mtxxp__fsuk)
    impl = mtxxp__fsuk['impl']
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
    yvplk__igbrj = 'def impl(nullable_tup):\n'
    yvplk__igbrj += '    data_tup = nullable_tup._data\n'
    yvplk__igbrj += '    null_tup = nullable_tup._null_values\n'
    yvplk__igbrj += (
        '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n')
    yvplk__igbrj += '    acc = _PyHASH_XXPRIME_5\n'
    pdzlh__lyann = nullable_tup._tuple_typ
    for i in range(len(pdzlh__lyann)):
        yvplk__igbrj += f'    null_val_{i} = null_tup[{i}]\n'
        yvplk__igbrj += f'    null_lane_{i} = hash(null_val_{i})\n'
        yvplk__igbrj += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        yvplk__igbrj += '        return -1\n'
        yvplk__igbrj += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        yvplk__igbrj += (
            '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        yvplk__igbrj += '    acc *= _PyHASH_XXPRIME_1\n'
        yvplk__igbrj += f'    if not null_val_{i}:\n'
        yvplk__igbrj += f'        lane_{i} = hash(data_tup[{i}])\n'
        yvplk__igbrj += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        yvplk__igbrj += f'            return -1\n'
        yvplk__igbrj += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        yvplk__igbrj += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        yvplk__igbrj += '        acc *= _PyHASH_XXPRIME_1\n'
    yvplk__igbrj += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    yvplk__igbrj += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    yvplk__igbrj += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    yvplk__igbrj += '    return numba.cpython.hashing.process_return(acc)\n'
    mtxxp__fsuk = {}
    exec(yvplk__igbrj, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, mtxxp__fsuk)
    impl = mtxxp__fsuk['impl']
    return impl
