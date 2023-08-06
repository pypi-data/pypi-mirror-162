"""Support for MultiIndex type of Pandas
"""
import operator
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from bodo.utils.conversion import ensure_contig_if_np
from bodo.utils.typing import BodoError, check_unsupported_args, dtype_to_array_type, get_val_type_maybe_str_literal, is_overload_none


class MultiIndexType(types.ArrayCompatible):

    def __init__(self, array_types, names_typ=None, name_typ=None):
        names_typ = (types.none,) * len(array_types
            ) if names_typ is None else names_typ
        name_typ = types.none if name_typ is None else name_typ
        self.array_types = array_types
        self.names_typ = names_typ
        self.name_typ = name_typ
        super(MultiIndexType, self).__init__(name=
            'MultiIndexType({}, {}, {})'.format(array_types, names_typ,
            name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return MultiIndexType(self.array_types, self.names_typ, self.name_typ)

    @property
    def nlevels(self):
        return len(self.array_types)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(MultiIndexType)
class MultiIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xtm__hupcj = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, xtm__hupcj)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[xacti__jfj].values) for
        xacti__jfj in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (tcz__vhwl) for tcz__vhwl in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    kkj__qhgrc = c.context.insert_const_string(c.builder.module, 'pandas')
    lbpht__hhwe = c.pyapi.import_module_noblock(kkj__qhgrc)
    gsunv__ydw = c.pyapi.object_getattr_string(lbpht__hhwe, 'MultiIndex')
    aif__tdqhu = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        aif__tdqhu.data)
    hrvi__wjbgy = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        aif__tdqhu.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), aif__tdqhu.
        names)
    dfgja__hjel = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        aif__tdqhu.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, aif__tdqhu.name)
    your__ymepn = c.pyapi.from_native_value(typ.name_typ, aif__tdqhu.name,
        c.env_manager)
    ossdo__heugd = c.pyapi.borrow_none()
    pvuah__stnv = c.pyapi.call_method(gsunv__ydw, 'from_arrays', (
        hrvi__wjbgy, ossdo__heugd, dfgja__hjel))
    c.pyapi.object_setattr_string(pvuah__stnv, 'name', your__ymepn)
    c.pyapi.decref(hrvi__wjbgy)
    c.pyapi.decref(dfgja__hjel)
    c.pyapi.decref(your__ymepn)
    c.pyapi.decref(lbpht__hhwe)
    c.pyapi.decref(gsunv__ydw)
    c.context.nrt.decref(c.builder, typ, val)
    return pvuah__stnv


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    ftk__cww = []
    hhliw__vizi = []
    for xacti__jfj in range(typ.nlevels):
        aje__svom = c.pyapi.unserialize(c.pyapi.serialize_object(xacti__jfj))
        hxxz__xih = c.pyapi.call_method(val, 'get_level_values', (aje__svom,))
        itmkp__augva = c.pyapi.object_getattr_string(hxxz__xih, 'values')
        c.pyapi.decref(hxxz__xih)
        c.pyapi.decref(aje__svom)
        qteht__zceqe = c.pyapi.to_native_value(typ.array_types[xacti__jfj],
            itmkp__augva).value
        ftk__cww.append(qteht__zceqe)
        hhliw__vizi.append(itmkp__augva)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, ftk__cww)
    else:
        data = cgutils.pack_struct(c.builder, ftk__cww)
    dfgja__hjel = c.pyapi.object_getattr_string(val, 'names')
    lske__frdc = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    cmo__kbuhv = c.pyapi.call_function_objargs(lske__frdc, (dfgja__hjel,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), cmo__kbuhv
        ).value
    your__ymepn = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, your__ymepn).value
    aif__tdqhu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    aif__tdqhu.data = data
    aif__tdqhu.names = names
    aif__tdqhu.name = name
    for itmkp__augva in hhliw__vizi:
        c.pyapi.decref(itmkp__augva)
    c.pyapi.decref(dfgja__hjel)
    c.pyapi.decref(lske__frdc)
    c.pyapi.decref(cmo__kbuhv)
    c.pyapi.decref(your__ymepn)
    return NativeValue(aif__tdqhu._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    hiqq__uhfp = 'pandas.MultiIndex.from_product'
    mgjt__gtyp = dict(sortorder=sortorder)
    oqyk__ytj = dict(sortorder=None)
    check_unsupported_args(hiqq__uhfp, mgjt__gtyp, oqyk__ytj, package_name=
        'pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{hiqq__uhfp}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{hiqq__uhfp}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{hiqq__uhfp}: iterables and names must be of the same length.')


def from_product(iterable, sortorder=None, names=None):
    pass


@overload(from_product)
def from_product_overload(iterables, sortorder=None, names=None):
    from_product_error_checking(iterables, sortorder, names)
    array_types = tuple(dtype_to_array_type(iterable.dtype) for iterable in
        iterables)
    if is_overload_none(names):
        names_typ = tuple([types.none] * len(iterables))
    else:
        names_typ = names.types
    lms__dxyll = MultiIndexType(array_types, names_typ)
    yee__vrk = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, yee__vrk, lms__dxyll)
    syc__jcjt = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{yee__vrk}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    gbqe__zdo = {}
    exec(syc__jcjt, globals(), gbqe__zdo)
    ipzc__nfyyh = gbqe__zdo['impl']
    return ipzc__nfyyh


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        epjmi__luid, ovqqg__jll, mjg__xdh = args
        dlmnz__nganf = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        dlmnz__nganf.data = epjmi__luid
        dlmnz__nganf.names = ovqqg__jll
        dlmnz__nganf.name = mjg__xdh
        context.nrt.incref(builder, signature.args[0], epjmi__luid)
        context.nrt.incref(builder, signature.args[1], ovqqg__jll)
        context.nrt.incref(builder, signature.args[2], mjg__xdh)
        return dlmnz__nganf._getvalue()
    bsh__znzyc = MultiIndexType(data.types, names.types, name)
    return bsh__znzyc(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        dqty__yvo = len(I.array_types)
        syc__jcjt = 'def impl(I, ind):\n'
        syc__jcjt += '  data = I._data\n'
        syc__jcjt += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{xacti__jfj}][ind])' for xacti__jfj in
            range(dqty__yvo))))
        gbqe__zdo = {}
        exec(syc__jcjt, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, gbqe__zdo)
        ipzc__nfyyh = gbqe__zdo['impl']
        return ipzc__nfyyh


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    qpx__fwe, tqee__poait = sig.args
    if qpx__fwe != tqee__poait:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
