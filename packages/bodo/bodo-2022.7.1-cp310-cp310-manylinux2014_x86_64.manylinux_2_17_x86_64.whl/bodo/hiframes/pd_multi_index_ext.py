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
        tzuy__noglv = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, tzuy__noglv)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[nqq__ktcrv].values) for
        nqq__ktcrv in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (zntr__xunp) for zntr__xunp in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    vtoe__eborv = c.context.insert_const_string(c.builder.module, 'pandas')
    mzyi__lkds = c.pyapi.import_module_noblock(vtoe__eborv)
    tmnd__fla = c.pyapi.object_getattr_string(mzyi__lkds, 'MultiIndex')
    enmxd__icwq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        enmxd__icwq.data)
    coxhp__epi = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        enmxd__icwq.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), enmxd__icwq
        .names)
    ddxri__hoys = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        enmxd__icwq.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, enmxd__icwq.name)
    okznn__qqul = c.pyapi.from_native_value(typ.name_typ, enmxd__icwq.name,
        c.env_manager)
    vkqev__zdadi = c.pyapi.borrow_none()
    ogcw__vlbhl = c.pyapi.call_method(tmnd__fla, 'from_arrays', (coxhp__epi,
        vkqev__zdadi, ddxri__hoys))
    c.pyapi.object_setattr_string(ogcw__vlbhl, 'name', okznn__qqul)
    c.pyapi.decref(coxhp__epi)
    c.pyapi.decref(ddxri__hoys)
    c.pyapi.decref(okznn__qqul)
    c.pyapi.decref(mzyi__lkds)
    c.pyapi.decref(tmnd__fla)
    c.context.nrt.decref(c.builder, typ, val)
    return ogcw__vlbhl


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    shu__zndy = []
    kexkl__ztia = []
    for nqq__ktcrv in range(typ.nlevels):
        fhljg__bufe = c.pyapi.unserialize(c.pyapi.serialize_object(nqq__ktcrv))
        fsp__iwus = c.pyapi.call_method(val, 'get_level_values', (fhljg__bufe,)
            )
        wcjq__qzfpg = c.pyapi.object_getattr_string(fsp__iwus, 'values')
        c.pyapi.decref(fsp__iwus)
        c.pyapi.decref(fhljg__bufe)
        roqx__zbr = c.pyapi.to_native_value(typ.array_types[nqq__ktcrv],
            wcjq__qzfpg).value
        shu__zndy.append(roqx__zbr)
        kexkl__ztia.append(wcjq__qzfpg)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, shu__zndy)
    else:
        data = cgutils.pack_struct(c.builder, shu__zndy)
    ddxri__hoys = c.pyapi.object_getattr_string(val, 'names')
    qcg__ljsl = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    qnql__ecc = c.pyapi.call_function_objargs(qcg__ljsl, (ddxri__hoys,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), qnql__ecc
        ).value
    okznn__qqul = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, okznn__qqul).value
    enmxd__icwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    enmxd__icwq.data = data
    enmxd__icwq.names = names
    enmxd__icwq.name = name
    for wcjq__qzfpg in kexkl__ztia:
        c.pyapi.decref(wcjq__qzfpg)
    c.pyapi.decref(ddxri__hoys)
    c.pyapi.decref(qcg__ljsl)
    c.pyapi.decref(qnql__ecc)
    c.pyapi.decref(okznn__qqul)
    return NativeValue(enmxd__icwq._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    qzfmk__sgame = 'pandas.MultiIndex.from_product'
    ada__tuqtj = dict(sortorder=sortorder)
    ltsj__exo = dict(sortorder=None)
    check_unsupported_args(qzfmk__sgame, ada__tuqtj, ltsj__exo,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{qzfmk__sgame}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{qzfmk__sgame}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{qzfmk__sgame}: iterables and names must be of the same length.')


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
    khb__hchh = MultiIndexType(array_types, names_typ)
    pfg__fwhd = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, pfg__fwhd, khb__hchh)
    ewff__hvv = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{pfg__fwhd}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    aork__ahz = {}
    exec(ewff__hvv, globals(), aork__ahz)
    xeq__mbfw = aork__ahz['impl']
    return xeq__mbfw


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        uocup__xanxp, phh__xtt, qphz__izw = args
        wolon__tdo = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        wolon__tdo.data = uocup__xanxp
        wolon__tdo.names = phh__xtt
        wolon__tdo.name = qphz__izw
        context.nrt.incref(builder, signature.args[0], uocup__xanxp)
        context.nrt.incref(builder, signature.args[1], phh__xtt)
        context.nrt.incref(builder, signature.args[2], qphz__izw)
        return wolon__tdo._getvalue()
    wiv__dxw = MultiIndexType(data.types, names.types, name)
    return wiv__dxw(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        ydc__vch = len(I.array_types)
        ewff__hvv = 'def impl(I, ind):\n'
        ewff__hvv += '  data = I._data\n'
        ewff__hvv += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{nqq__ktcrv}][ind])' for nqq__ktcrv in
            range(ydc__vch))))
        aork__ahz = {}
        exec(ewff__hvv, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, aork__ahz)
        xeq__mbfw = aork__ahz['impl']
        return xeq__mbfw


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    gmm__pvk, qucbg__imq = sig.args
    if gmm__pvk != qucbg__imq:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
