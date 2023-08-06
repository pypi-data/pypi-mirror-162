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
        eitgi__wdd = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, eitgi__wdd)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[mqiea__wyx].values) for
        mqiea__wyx in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (rim__xrntp) for rim__xrntp in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    spnh__gofny = c.context.insert_const_string(c.builder.module, 'pandas')
    wworr__wxi = c.pyapi.import_module_noblock(spnh__gofny)
    ivqe__vuw = c.pyapi.object_getattr_string(wworr__wxi, 'MultiIndex')
    cliz__lzkal = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        cliz__lzkal.data)
    hgfl__lmv = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        cliz__lzkal.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), cliz__lzkal
        .names)
    qdr__bri = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        cliz__lzkal.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, cliz__lzkal.name)
    tebj__mmz = c.pyapi.from_native_value(typ.name_typ, cliz__lzkal.name, c
        .env_manager)
    trtq__nqm = c.pyapi.borrow_none()
    fmufi__tjtw = c.pyapi.call_method(ivqe__vuw, 'from_arrays', (hgfl__lmv,
        trtq__nqm, qdr__bri))
    c.pyapi.object_setattr_string(fmufi__tjtw, 'name', tebj__mmz)
    c.pyapi.decref(hgfl__lmv)
    c.pyapi.decref(qdr__bri)
    c.pyapi.decref(tebj__mmz)
    c.pyapi.decref(wworr__wxi)
    c.pyapi.decref(ivqe__vuw)
    c.context.nrt.decref(c.builder, typ, val)
    return fmufi__tjtw


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    lrym__mgc = []
    dlrnm__sdpaj = []
    for mqiea__wyx in range(typ.nlevels):
        hbyi__zxuhb = c.pyapi.unserialize(c.pyapi.serialize_object(mqiea__wyx))
        ukjg__xecci = c.pyapi.call_method(val, 'get_level_values', (
            hbyi__zxuhb,))
        xidg__zopli = c.pyapi.object_getattr_string(ukjg__xecci, 'values')
        c.pyapi.decref(ukjg__xecci)
        c.pyapi.decref(hbyi__zxuhb)
        hvkj__zdguq = c.pyapi.to_native_value(typ.array_types[mqiea__wyx],
            xidg__zopli).value
        lrym__mgc.append(hvkj__zdguq)
        dlrnm__sdpaj.append(xidg__zopli)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, lrym__mgc)
    else:
        data = cgutils.pack_struct(c.builder, lrym__mgc)
    qdr__bri = c.pyapi.object_getattr_string(val, 'names')
    scn__jmriw = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    diuhb__wmtqy = c.pyapi.call_function_objargs(scn__jmriw, (qdr__bri,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), diuhb__wmtqy
        ).value
    tebj__mmz = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, tebj__mmz).value
    cliz__lzkal = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cliz__lzkal.data = data
    cliz__lzkal.names = names
    cliz__lzkal.name = name
    for xidg__zopli in dlrnm__sdpaj:
        c.pyapi.decref(xidg__zopli)
    c.pyapi.decref(qdr__bri)
    c.pyapi.decref(scn__jmriw)
    c.pyapi.decref(diuhb__wmtqy)
    c.pyapi.decref(tebj__mmz)
    return NativeValue(cliz__lzkal._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    fvxb__vpl = 'pandas.MultiIndex.from_product'
    vqp__net = dict(sortorder=sortorder)
    rcbd__xjxwe = dict(sortorder=None)
    check_unsupported_args(fvxb__vpl, vqp__net, rcbd__xjxwe, package_name=
        'pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{fvxb__vpl}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{fvxb__vpl}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{fvxb__vpl}: iterables and names must be of the same length.')


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
    aiel__aar = MultiIndexType(array_types, names_typ)
    cja__pkgj = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, cja__pkgj, aiel__aar)
    kdmw__zenns = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{cja__pkgj}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    abqj__xsak = {}
    exec(kdmw__zenns, globals(), abqj__xsak)
    asdhf__qtiy = abqj__xsak['impl']
    return asdhf__qtiy


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        pxsjo__xtqv, sujp__sjmer, kpsj__nabn = args
        oiqac__dho = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        oiqac__dho.data = pxsjo__xtqv
        oiqac__dho.names = sujp__sjmer
        oiqac__dho.name = kpsj__nabn
        context.nrt.incref(builder, signature.args[0], pxsjo__xtqv)
        context.nrt.incref(builder, signature.args[1], sujp__sjmer)
        context.nrt.incref(builder, signature.args[2], kpsj__nabn)
        return oiqac__dho._getvalue()
    ddvfl__lwk = MultiIndexType(data.types, names.types, name)
    return ddvfl__lwk(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        kboo__eew = len(I.array_types)
        kdmw__zenns = 'def impl(I, ind):\n'
        kdmw__zenns += '  data = I._data\n'
        kdmw__zenns += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{mqiea__wyx}][ind])' for mqiea__wyx in
            range(kboo__eew))))
        abqj__xsak = {}
        exec(kdmw__zenns, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, abqj__xsak)
        asdhf__qtiy = abqj__xsak['impl']
        return asdhf__qtiy


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    tpcq__tcclf, dkhbf__uls = sig.args
    if tpcq__tcclf != dkhbf__uls:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
