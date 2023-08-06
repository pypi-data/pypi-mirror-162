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
        rqap__kcue = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, rqap__kcue)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[mozcn__hhf].values) for
        mozcn__hhf in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (zvuxy__xpw) for zvuxy__xpw in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    rlbu__motwu = c.context.insert_const_string(c.builder.module, 'pandas')
    lrfev__qlnv = c.pyapi.import_module_noblock(rlbu__motwu)
    ikwpk__fpx = c.pyapi.object_getattr_string(lrfev__qlnv, 'MultiIndex')
    rqzm__vsdo = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        rqzm__vsdo.data)
    shg__ghiwt = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        rqzm__vsdo.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), rqzm__vsdo.
        names)
    bhbvk__ocdoq = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        rqzm__vsdo.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, rqzm__vsdo.name)
    rhh__bqj = c.pyapi.from_native_value(typ.name_typ, rqzm__vsdo.name, c.
        env_manager)
    jubsq__enjzj = c.pyapi.borrow_none()
    bqtih__qmhrc = c.pyapi.call_method(ikwpk__fpx, 'from_arrays', (
        shg__ghiwt, jubsq__enjzj, bhbvk__ocdoq))
    c.pyapi.object_setattr_string(bqtih__qmhrc, 'name', rhh__bqj)
    c.pyapi.decref(shg__ghiwt)
    c.pyapi.decref(bhbvk__ocdoq)
    c.pyapi.decref(rhh__bqj)
    c.pyapi.decref(lrfev__qlnv)
    c.pyapi.decref(ikwpk__fpx)
    c.context.nrt.decref(c.builder, typ, val)
    return bqtih__qmhrc


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    twkrw__jbcep = []
    pkjj__zei = []
    for mozcn__hhf in range(typ.nlevels):
        fqcom__goyq = c.pyapi.unserialize(c.pyapi.serialize_object(mozcn__hhf))
        lnm__elbv = c.pyapi.call_method(val, 'get_level_values', (fqcom__goyq,)
            )
        mqwdx__lvzo = c.pyapi.object_getattr_string(lnm__elbv, 'values')
        c.pyapi.decref(lnm__elbv)
        c.pyapi.decref(fqcom__goyq)
        eap__dma = c.pyapi.to_native_value(typ.array_types[mozcn__hhf],
            mqwdx__lvzo).value
        twkrw__jbcep.append(eap__dma)
        pkjj__zei.append(mqwdx__lvzo)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, twkrw__jbcep)
    else:
        data = cgutils.pack_struct(c.builder, twkrw__jbcep)
    bhbvk__ocdoq = c.pyapi.object_getattr_string(val, 'names')
    eaxo__oin = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    fwku__hjf = c.pyapi.call_function_objargs(eaxo__oin, (bhbvk__ocdoq,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), fwku__hjf
        ).value
    rhh__bqj = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, rhh__bqj).value
    rqzm__vsdo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rqzm__vsdo.data = data
    rqzm__vsdo.names = names
    rqzm__vsdo.name = name
    for mqwdx__lvzo in pkjj__zei:
        c.pyapi.decref(mqwdx__lvzo)
    c.pyapi.decref(bhbvk__ocdoq)
    c.pyapi.decref(eaxo__oin)
    c.pyapi.decref(fwku__hjf)
    c.pyapi.decref(rhh__bqj)
    return NativeValue(rqzm__vsdo._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    rfny__pds = 'pandas.MultiIndex.from_product'
    hgzd__zdncy = dict(sortorder=sortorder)
    jwdnv__gva = dict(sortorder=None)
    check_unsupported_args(rfny__pds, hgzd__zdncy, jwdnv__gva, package_name
        ='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{rfny__pds}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{rfny__pds}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{rfny__pds}: iterables and names must be of the same length.')


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
    qnp__fsrjz = MultiIndexType(array_types, names_typ)
    hozi__elpc = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, hozi__elpc, qnp__fsrjz)
    opzf__pwnxs = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{hozi__elpc}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    egjvy__pjk = {}
    exec(opzf__pwnxs, globals(), egjvy__pjk)
    dzoe__wjb = egjvy__pjk['impl']
    return dzoe__wjb


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        iby__qhs, teoat__bsl, awzrq__cdtpb = args
        djm__cfenm = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        djm__cfenm.data = iby__qhs
        djm__cfenm.names = teoat__bsl
        djm__cfenm.name = awzrq__cdtpb
        context.nrt.incref(builder, signature.args[0], iby__qhs)
        context.nrt.incref(builder, signature.args[1], teoat__bsl)
        context.nrt.incref(builder, signature.args[2], awzrq__cdtpb)
        return djm__cfenm._getvalue()
    aznb__dsita = MultiIndexType(data.types, names.types, name)
    return aznb__dsita(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        mxij__ivwa = len(I.array_types)
        opzf__pwnxs = 'def impl(I, ind):\n'
        opzf__pwnxs += '  data = I._data\n'
        opzf__pwnxs += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{mozcn__hhf}][ind])' for mozcn__hhf in
            range(mxij__ivwa))))
        egjvy__pjk = {}
        exec(opzf__pwnxs, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, egjvy__pjk)
        dzoe__wjb = egjvy__pjk['impl']
        return dzoe__wjb


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    xcznw__fujj, sxl__vutk = sig.args
    if xcznw__fujj != sxl__vutk:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
