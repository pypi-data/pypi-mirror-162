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
        fyt__qvlf = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, fyt__qvlf)


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
        nesvt__ffeb = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        nesvt__ffeb.data = data_tuple
        nesvt__ffeb.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return nesvt__ffeb._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    zkmqb__xsi = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, zkmqb__xsi.data)
    c.context.nrt.incref(c.builder, typ.null_typ, zkmqb__xsi.null_values)
    gvs__tesn = c.pyapi.from_native_value(typ.tuple_typ, zkmqb__xsi.data, c
        .env_manager)
    vzhnf__fetdh = c.pyapi.from_native_value(typ.null_typ, zkmqb__xsi.
        null_values, c.env_manager)
    mggl__ydmn = c.context.get_constant(types.int64, len(typ.tuple_typ))
    tmd__lowvt = c.pyapi.list_new(mggl__ydmn)
    with cgutils.for_range(c.builder, mggl__ydmn) as comr__fexus:
        i = comr__fexus.index
        okv__hhul = c.pyapi.long_from_longlong(i)
        lxcn__fyze = c.pyapi.object_getitem(vzhnf__fetdh, okv__hhul)
        cpp__psz = c.pyapi.to_native_value(types.bool_, lxcn__fyze).value
        with c.builder.if_else(cpp__psz) as (mrcl__yqh, lrklq__tyod):
            with mrcl__yqh:
                c.pyapi.list_setitem(tmd__lowvt, i, c.pyapi.make_none())
            with lrklq__tyod:
                olutw__gxhgm = c.pyapi.object_getitem(gvs__tesn, okv__hhul)
                c.pyapi.list_setitem(tmd__lowvt, i, olutw__gxhgm)
        c.pyapi.decref(okv__hhul)
        c.pyapi.decref(lxcn__fyze)
    fdpjg__jisk = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    fvezt__zla = c.pyapi.call_function_objargs(fdpjg__jisk, (tmd__lowvt,))
    c.pyapi.decref(gvs__tesn)
    c.pyapi.decref(vzhnf__fetdh)
    c.pyapi.decref(fdpjg__jisk)
    c.pyapi.decref(tmd__lowvt)
    c.context.nrt.decref(c.builder, typ, val)
    return fvezt__zla


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
    nesvt__ffeb = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (nesvt__ffeb.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    yju__apnum = 'def impl(val1, val2):\n'
    yju__apnum += '    data_tup1 = val1._data\n'
    yju__apnum += '    null_tup1 = val1._null_values\n'
    yju__apnum += '    data_tup2 = val2._data\n'
    yju__apnum += '    null_tup2 = val2._null_values\n'
    oho__svx = val1._tuple_typ
    for i in range(len(oho__svx)):
        yju__apnum += f'    null1_{i} = null_tup1[{i}]\n'
        yju__apnum += f'    null2_{i} = null_tup2[{i}]\n'
        yju__apnum += f'    data1_{i} = data_tup1[{i}]\n'
        yju__apnum += f'    data2_{i} = data_tup2[{i}]\n'
        yju__apnum += f'    if null1_{i} != null2_{i}:\n'
        yju__apnum += '        return False\n'
        yju__apnum += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        yju__apnum += f'        return False\n'
    yju__apnum += f'    return True\n'
    pega__apy = {}
    exec(yju__apnum, {}, pega__apy)
    impl = pega__apy['impl']
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
    yju__apnum = 'def impl(nullable_tup):\n'
    yju__apnum += '    data_tup = nullable_tup._data\n'
    yju__apnum += '    null_tup = nullable_tup._null_values\n'
    yju__apnum += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    yju__apnum += '    acc = _PyHASH_XXPRIME_5\n'
    oho__svx = nullable_tup._tuple_typ
    for i in range(len(oho__svx)):
        yju__apnum += f'    null_val_{i} = null_tup[{i}]\n'
        yju__apnum += f'    null_lane_{i} = hash(null_val_{i})\n'
        yju__apnum += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        yju__apnum += '        return -1\n'
        yju__apnum += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        yju__apnum += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        yju__apnum += '    acc *= _PyHASH_XXPRIME_1\n'
        yju__apnum += f'    if not null_val_{i}:\n'
        yju__apnum += f'        lane_{i} = hash(data_tup[{i}])\n'
        yju__apnum += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        yju__apnum += f'            return -1\n'
        yju__apnum += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        yju__apnum += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        yju__apnum += '        acc *= _PyHASH_XXPRIME_1\n'
    yju__apnum += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    yju__apnum += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    yju__apnum += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    yju__apnum += '    return numba.cpython.hashing.process_return(acc)\n'
    pega__apy = {}
    exec(yju__apnum, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, pega__apy)
    impl = pega__apy['impl']
    return impl
