"""Dictionary encoded array data type, similar to DictionaryArray of Arrow.
The purpose is to improve memory consumption and performance over string_array_type for
string arrays that have a lot of repetitive values (typical in practice).
Can be extended to be used with types other than strings as well.
See:
https://bodo.atlassian.net/browse/BE-2295
https://bodo.atlassian.net/wiki/spaces/B/pages/993722369/Dictionary-encoded+String+Array+Support+in+Parquet+read+compute+...
https://arrow.apache.org/docs/cpp/api/array.html#dictionary-encoded
"""
import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_builtin, lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
import bodo
from bodo.libs import hstr_ext
from bodo.libs.bool_arr_ext import init_bool_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, get_str_arr_item_length, overload_str_arr_astype, pre_alloc_string_array, string_array_type
from bodo.utils.typing import BodoArrayIterator, is_overload_none, raise_bodo_error
ll.add_symbol('box_dict_str_array', hstr_ext.box_dict_str_array)
dict_indices_arr_type = IntegerArrayType(types.int32)


class DictionaryArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self, arr_data_type):
        self.data = arr_data_type
        super(DictionaryArrayType, self).__init__(name=
            f'DictionaryArrayType({arr_data_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    @property
    def dtype(self):
        return self.data.dtype

    def copy(self):
        return DictionaryArrayType(self.data)

    @property
    def indices_type(self):
        return dict_indices_arr_type

    @property
    def indices_dtype(self):
        return dict_indices_arr_type.dtype

    def unify(self, typingctx, other):
        if other == string_array_type:
            return string_array_type


dict_str_arr_type = DictionaryArrayType(string_array_type)


@register_model(DictionaryArrayType)
class DictionaryArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vhqo__kcqxn = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, vhqo__kcqxn)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        qku__boewx, zffh__jsqm, sto__kzmz = args
        wwq__hwk = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        wwq__hwk.data = qku__boewx
        wwq__hwk.indices = zffh__jsqm
        wwq__hwk.has_global_dictionary = sto__kzmz
        context.nrt.incref(builder, signature.args[0], qku__boewx)
        context.nrt.incref(builder, signature.args[1], zffh__jsqm)
        return wwq__hwk._getvalue()
    gctn__tyxq = DictionaryArrayType(data_t)
    kxpg__rfma = gctn__tyxq(data_t, indices_t, types.bool_)
    return kxpg__rfma, codegen


@typeof_impl.register(pa.DictionaryArray)
def typeof_dict_value(val, c):
    if val.type.value_type == pa.string():
        return dict_str_arr_type


def to_pa_dict_arr(A):
    if isinstance(A, pa.DictionaryArray):
        return A
    for i in range(len(A)):
        if pd.isna(A[i]):
            A[i] = None
    return pa.array(A).dictionary_encode()


@unbox(DictionaryArrayType)
def unbox_dict_arr(typ, val, c):
    if bodo.hiframes.boxing._use_dict_str_type:
        alyk__wrmt = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(alyk__wrmt, [val])
        c.pyapi.decref(alyk__wrmt)
    wwq__hwk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mci__chf = c.pyapi.object_getattr_string(val, 'dictionary')
    fzx__sxpw = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_, 
        False))
    ngfq__tnj = c.pyapi.call_method(mci__chf, 'to_numpy', (fzx__sxpw,))
    wwq__hwk.data = c.unbox(typ.data, ngfq__tnj).value
    nlqnu__sdsqg = c.pyapi.object_getattr_string(val, 'indices')
    wby__iwx = c.context.insert_const_string(c.builder.module, 'pandas')
    ngdjw__qre = c.pyapi.import_module_noblock(wby__iwx)
    hkgdt__iup = c.pyapi.string_from_constant_string('Int32')
    lejn__cveuz = c.pyapi.call_method(ngdjw__qre, 'array', (nlqnu__sdsqg,
        hkgdt__iup))
    wwq__hwk.indices = c.unbox(dict_indices_arr_type, lejn__cveuz).value
    wwq__hwk.has_global_dictionary = c.context.get_constant(types.bool_, False)
    c.pyapi.decref(mci__chf)
    c.pyapi.decref(fzx__sxpw)
    c.pyapi.decref(ngfq__tnj)
    c.pyapi.decref(nlqnu__sdsqg)
    c.pyapi.decref(ngdjw__qre)
    c.pyapi.decref(hkgdt__iup)
    c.pyapi.decref(lejn__cveuz)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    awtm__jvtjt = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wwq__hwk._getvalue(), is_error=awtm__jvtjt)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    wwq__hwk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, wwq__hwk.data)
        fuzb__iuqwu = c.box(typ.data, wwq__hwk.data)
        egft__dwnzu = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, wwq__hwk.indices)
        ucim__gxe = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        wdbwb__ohpb = cgutils.get_or_insert_function(c.builder.module,
            ucim__gxe, name='box_dict_str_array')
        hkvxi__rijzy = cgutils.create_struct_proxy(types.Array(types.int32,
            1, 'C'))(c.context, c.builder, egft__dwnzu.data)
        fhfqm__ifqdy = c.builder.extract_value(hkvxi__rijzy.shape, 0)
        koc__ludrh = hkvxi__rijzy.data
        rdy__pnon = cgutils.create_struct_proxy(types.Array(types.int8, 1, 'C')
            )(c.context, c.builder, egft__dwnzu.null_bitmap).data
        ngfq__tnj = c.builder.call(wdbwb__ohpb, [fhfqm__ifqdy, fuzb__iuqwu,
            koc__ludrh, rdy__pnon])
        c.pyapi.decref(fuzb__iuqwu)
    else:
        wby__iwx = c.context.insert_const_string(c.builder.module, 'pyarrow')
        intpa__iazop = c.pyapi.import_module_noblock(wby__iwx)
        wddx__uhiqi = c.pyapi.object_getattr_string(intpa__iazop,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, wwq__hwk.data)
        fuzb__iuqwu = c.box(typ.data, wwq__hwk.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, wwq__hwk.indices
            )
        nlqnu__sdsqg = c.box(dict_indices_arr_type, wwq__hwk.indices)
        kyfb__vlzq = c.pyapi.call_method(wddx__uhiqi, 'from_arrays', (
            nlqnu__sdsqg, fuzb__iuqwu))
        fzx__sxpw = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        ngfq__tnj = c.pyapi.call_method(kyfb__vlzq, 'to_numpy', (fzx__sxpw,))
        c.pyapi.decref(intpa__iazop)
        c.pyapi.decref(fuzb__iuqwu)
        c.pyapi.decref(nlqnu__sdsqg)
        c.pyapi.decref(wddx__uhiqi)
        c.pyapi.decref(kyfb__vlzq)
        c.pyapi.decref(fzx__sxpw)
    c.context.nrt.decref(c.builder, typ, val)
    return ngfq__tnj


@overload(len, no_unliteral=True)
def overload_dict_arr_len(A):
    if isinstance(A, DictionaryArrayType):
        return lambda A: len(A._indices)


@overload_attribute(DictionaryArrayType, 'shape')
def overload_dict_arr_shape(A):
    return lambda A: (len(A._indices),)


@overload_attribute(DictionaryArrayType, 'ndim')
def overload_dict_arr_ndim(A):
    return lambda A: 1


@overload_attribute(DictionaryArrayType, 'size')
def overload_dict_arr_size(A):
    return lambda A: len(A._indices)


@overload_method(DictionaryArrayType, 'tolist', no_unliteral=True)
def overload_dict_arr_tolist(A):
    return lambda A: list(A)


overload_method(DictionaryArrayType, 'astype', no_unliteral=True)(
    overload_str_arr_astype)


@overload_method(DictionaryArrayType, 'copy', no_unliteral=True)
def overload_dict_arr_copy(A):

    def copy_impl(A):
        return init_dict_arr(A._data.copy(), A._indices.copy(), A.
            _has_global_dictionary)
    return copy_impl


@overload_attribute(DictionaryArrayType, 'dtype')
def overload_dict_arr_dtype(A):
    return lambda A: A._data.dtype


@overload_attribute(DictionaryArrayType, 'nbytes')
def dict_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._indices.nbytes


@lower_constant(DictionaryArrayType)
def lower_constant_dict_arr(context, builder, typ, pyval):
    if bodo.hiframes.boxing._use_dict_str_type and isinstance(pyval, np.ndarray
        ):
        pyval = pa.array(pyval).dictionary_encode()
    fydh__joyk = pyval.dictionary.to_numpy(False)
    vfqm__peut = pd.array(pyval.indices, 'Int32')
    fydh__joyk = context.get_constant_generic(builder, typ.data, fydh__joyk)
    vfqm__peut = context.get_constant_generic(builder,
        dict_indices_arr_type, vfqm__peut)
    dzuq__mgpz = context.get_constant(types.bool_, False)
    anjd__iqq = lir.Constant.literal_struct([fydh__joyk, vfqm__peut,
        dzuq__mgpz])
    return anjd__iqq


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            gylq__njru = A._indices[ind]
            return A._data[gylq__njru]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        qku__boewx = A._data
        zffh__jsqm = A._indices
        fhfqm__ifqdy = len(zffh__jsqm)
        wvwab__xrlr = [get_str_arr_item_length(qku__boewx, i) for i in
            range(len(qku__boewx))]
        qdd__kfx = 0
        for i in range(fhfqm__ifqdy):
            if not bodo.libs.array_kernels.isna(zffh__jsqm, i):
                qdd__kfx += wvwab__xrlr[zffh__jsqm[i]]
        wvzrv__ani = pre_alloc_string_array(fhfqm__ifqdy, qdd__kfx)
        for i in range(fhfqm__ifqdy):
            if bodo.libs.array_kernels.isna(zffh__jsqm, i):
                bodo.libs.array_kernels.setna(wvzrv__ani, i)
                continue
            ind = zffh__jsqm[i]
            if bodo.libs.array_kernels.isna(qku__boewx, ind):
                bodo.libs.array_kernels.setna(wvzrv__ani, i)
                continue
            wvzrv__ani[i] = qku__boewx[ind]
        return wvzrv__ani
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    gylq__njru = -1
    qku__boewx = arr._data
    for i in range(len(qku__boewx)):
        if bodo.libs.array_kernels.isna(qku__boewx, i):
            continue
        if qku__boewx[i] == val:
            gylq__njru = i
            break
    return gylq__njru


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    fhfqm__ifqdy = len(arr)
    gylq__njru = find_dict_ind(arr, val)
    if gylq__njru == -1:
        return init_bool_array(np.full(fhfqm__ifqdy, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == gylq__njru


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    fhfqm__ifqdy = len(arr)
    gylq__njru = find_dict_ind(arr, val)
    if gylq__njru == -1:
        return init_bool_array(np.full(fhfqm__ifqdy, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != gylq__njru


def get_binary_op_overload(op, lhs, rhs):
    if op == operator.eq:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(rhs, lhs)
    if op == operator.ne:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(rhs, lhs)


def convert_dict_arr_to_int(arr, dtype):
    return arr


@overload(convert_dict_arr_to_int)
def convert_dict_arr_to_int_overload(arr, dtype):

    def impl(arr, dtype):
        pvrva__onbj = arr._data
        emnzy__fnyur = bodo.libs.int_arr_ext.alloc_int_array(len(
            pvrva__onbj), dtype)
        for dbnwz__zev in range(len(pvrva__onbj)):
            if bodo.libs.array_kernels.isna(pvrva__onbj, dbnwz__zev):
                bodo.libs.array_kernels.setna(emnzy__fnyur, dbnwz__zev)
                continue
            emnzy__fnyur[dbnwz__zev] = np.int64(pvrva__onbj[dbnwz__zev])
        fhfqm__ifqdy = len(arr)
        zffh__jsqm = arr._indices
        wvzrv__ani = bodo.libs.int_arr_ext.alloc_int_array(fhfqm__ifqdy, dtype)
        for i in range(fhfqm__ifqdy):
            if bodo.libs.array_kernels.isna(zffh__jsqm, i):
                bodo.libs.array_kernels.setna(wvzrv__ani, i)
                continue
            wvzrv__ani[i] = emnzy__fnyur[zffh__jsqm[i]]
        return wvzrv__ani
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    coo__sje = len(arrs)
    zqx__tbem = 'def impl(arrs, sep):\n'
    zqx__tbem += '  ind_map = {}\n'
    zqx__tbem += '  out_strs = []\n'
    zqx__tbem += '  n = len(arrs[0])\n'
    for i in range(coo__sje):
        zqx__tbem += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(coo__sje):
        zqx__tbem += f'  data{i} = arrs[{i}]._data\n'
    zqx__tbem += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    zqx__tbem += '  for i in range(n):\n'
    jrrx__rilim = ' or '.join([
        f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for i in range(coo__sje)]
        )
    zqx__tbem += f'    if {jrrx__rilim}:\n'
    zqx__tbem += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    zqx__tbem += '      continue\n'
    for i in range(coo__sje):
        zqx__tbem += f'    ind{i} = indices{i}[i]\n'
    ccywd__ntiq = '(' + ', '.join(f'ind{i}' for i in range(coo__sje)) + ')'
    zqx__tbem += f'    if {ccywd__ntiq} not in ind_map:\n'
    zqx__tbem += '      out_ind = len(out_strs)\n'
    zqx__tbem += f'      ind_map[{ccywd__ntiq}] = out_ind\n'
    sizsq__ihs = "''" if is_overload_none(sep) else 'sep'
    ukte__ctwwc = ', '.join([f'data{i}[ind{i}]' for i in range(coo__sje)])
    zqx__tbem += f'      v = {sizsq__ihs}.join([{ukte__ctwwc}])\n'
    zqx__tbem += '      out_strs.append(v)\n'
    zqx__tbem += '    else:\n'
    zqx__tbem += f'      out_ind = ind_map[{ccywd__ntiq}]\n'
    zqx__tbem += '    out_indices[i] = out_ind\n'
    zqx__tbem += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    zqx__tbem += (
        '  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)\n'
        )
    xow__dgt = {}
    exec(zqx__tbem, {'bodo': bodo, 'numba': numba, 'np': np}, xow__dgt)
    impl = xow__dgt['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    bxrca__skyn = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    kxpg__rfma = toty(fromty)
    rzsox__gbu = context.compile_internal(builder, bxrca__skyn, kxpg__rfma,
        (val,))
    return impl_ret_new_ref(context, builder, toty, rzsox__gbu)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    fydh__joyk = arr._data
    xax__opdlb = len(fydh__joyk)
    pjmc__pncc = pre_alloc_string_array(xax__opdlb, -1)
    if regex:
        caith__jqb = re.compile(pat, flags)
        for i in range(xax__opdlb):
            if bodo.libs.array_kernels.isna(fydh__joyk, i):
                bodo.libs.array_kernels.setna(pjmc__pncc, i)
                continue
            pjmc__pncc[i] = caith__jqb.sub(repl=repl, string=fydh__joyk[i])
    else:
        for i in range(xax__opdlb):
            if bodo.libs.array_kernels.isna(fydh__joyk, i):
                bodo.libs.array_kernels.setna(pjmc__pncc, i)
                continue
            pjmc__pncc[i] = fydh__joyk[i].replace(pat, repl)
    return init_dict_arr(pjmc__pncc, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    wwq__hwk = arr._data
    lsv__geu = len(wwq__hwk)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(lsv__geu)
    for i in range(lsv__geu):
        dict_arr_out[i] = wwq__hwk[i].startswith(pat)
    vfqm__peut = arr._indices
    osk__knh = len(vfqm__peut)
    wvzrv__ani = bodo.libs.bool_arr_ext.alloc_bool_array(osk__knh)
    for i in range(osk__knh):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wvzrv__ani, i)
        else:
            wvzrv__ani[i] = dict_arr_out[vfqm__peut[i]]
    return wvzrv__ani


@register_jitable
def str_endswith(arr, pat, na):
    wwq__hwk = arr._data
    lsv__geu = len(wwq__hwk)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(lsv__geu)
    for i in range(lsv__geu):
        dict_arr_out[i] = wwq__hwk[i].endswith(pat)
    vfqm__peut = arr._indices
    osk__knh = len(vfqm__peut)
    wvzrv__ani = bodo.libs.bool_arr_ext.alloc_bool_array(osk__knh)
    for i in range(osk__knh):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wvzrv__ani, i)
        else:
            wvzrv__ani[i] = dict_arr_out[vfqm__peut[i]]
    return wvzrv__ani


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    wwq__hwk = arr._data
    ullzv__vtmqz = pd.Series(wwq__hwk)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = ullzv__vtmqz.array._str_contains(pat, case, flags,
            na, regex)
    vfqm__peut = arr._indices
    osk__knh = len(vfqm__peut)
    wvzrv__ani = bodo.libs.bool_arr_ext.alloc_bool_array(osk__knh)
    for i in range(osk__knh):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wvzrv__ani, i)
        else:
            wvzrv__ani[i] = dict_arr_out[vfqm__peut[i]]
    return wvzrv__ani


@register_jitable
def str_contains_non_regex(arr, pat, case):
    wwq__hwk = arr._data
    lsv__geu = len(wwq__hwk)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(lsv__geu)
    if not case:
        jrtml__ist = pat.upper()
    for i in range(lsv__geu):
        if case:
            dict_arr_out[i] = pat in wwq__hwk[i]
        else:
            dict_arr_out[i] = jrtml__ist in wwq__hwk[i].upper()
    vfqm__peut = arr._indices
    osk__knh = len(vfqm__peut)
    wvzrv__ani = bodo.libs.bool_arr_ext.alloc_bool_array(osk__knh)
    for i in range(osk__knh):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wvzrv__ani, i)
        else:
            wvzrv__ani[i] = dict_arr_out[vfqm__peut[i]]
    return wvzrv__ani


@numba.njit
def str_match(arr, pat, case, flags, na):
    wwq__hwk = arr._data
    vfqm__peut = arr._indices
    osk__knh = len(vfqm__peut)
    wvzrv__ani = bodo.libs.bool_arr_ext.alloc_bool_array(osk__knh)
    ullzv__vtmqz = pd.Series(wwq__hwk)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = ullzv__vtmqz.array._str_match(pat, case, flags, na)
    for i in range(osk__knh):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wvzrv__ani, i)
        else:
            wvzrv__ani[i] = dict_arr_out[vfqm__peut[i]]
    return wvzrv__ani


def create_simple_str2str_methods(func_name, func_args):
    zqx__tbem = f"""def str_{func_name}({', '.join(func_args)}):
    data_arr = arr._data
    n_data = len(data_arr)
    out_str_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_data, -1)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_str_arr, i)
            continue
        out_str_arr[i] = data_arr[i].{func_name}({', '.join(func_args[1:])})
    return init_dict_arr(out_str_arr, arr._indices.copy(), arr._has_global_dictionary)
"""
    xow__dgt = {}
    exec(zqx__tbem, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, xow__dgt)
    return xow__dgt[f'str_{func_name}']


def _register_simple_str2str_methods():
    lhpvd__wik = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in lhpvd__wik.keys():
        imp__zikz = create_simple_str2str_methods(func_name, lhpvd__wik[
            func_name])
        imp__zikz = register_jitable(imp__zikz)
        globals()[f'str_{func_name}'] = imp__zikz


_register_simple_str2str_methods()


def create_find_methods(func_name):
    zqx__tbem = f"""def str_{func_name}(arr, sub, start, end):
  data_arr = arr._data
  indices_arr = arr._indices
  n_data = len(data_arr)
  n_indices = len(indices_arr)
  tmp_dict_arr = bodo.libs.int_arr_ext.alloc_int_array(n_data, np.int64)
  out_int_arr = bodo.libs.int_arr_ext.alloc_int_array(n_indices, np.int64)
  for i in range(n_data):
    if bodo.libs.array_kernels.isna(data_arr, i):
      bodo.libs.array_kernels.setna(tmp_dict_arr, i)
      continue
    tmp_dict_arr[i] = data_arr[i].{func_name}(sub, start, end)
  for i in range(n_indices):
    if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
      tmp_dict_arr, indices_arr[i]
    ):
      bodo.libs.array_kernels.setna(out_int_arr, i)
    else:
      out_int_arr[i] = tmp_dict_arr[indices_arr[i]]
  return out_int_arr"""
    xow__dgt = {}
    exec(zqx__tbem, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, xow__dgt)
    return xow__dgt[f'str_{func_name}']


def _register_find_methods():
    mhmf__emacm = ['find', 'rfind']
    for func_name in mhmf__emacm:
        imp__zikz = create_find_methods(func_name)
        imp__zikz = register_jitable(imp__zikz)
        globals()[f'str_{func_name}'] = imp__zikz


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    fydh__joyk = arr._data
    vfqm__peut = arr._indices
    xax__opdlb = len(fydh__joyk)
    osk__knh = len(vfqm__peut)
    rhou__ugklr = bodo.libs.int_arr_ext.alloc_int_array(xax__opdlb, np.int64)
    shdhu__tjqlj = bodo.libs.int_arr_ext.alloc_int_array(osk__knh, np.int64)
    regex = re.compile(pat, flags)
    for i in range(xax__opdlb):
        if bodo.libs.array_kernels.isna(fydh__joyk, i):
            bodo.libs.array_kernels.setna(rhou__ugklr, i)
            continue
        rhou__ugklr[i] = bodo.libs.str_ext.str_findall_count(regex,
            fydh__joyk[i])
    for i in range(osk__knh):
        if bodo.libs.array_kernels.isna(vfqm__peut, i
            ) or bodo.libs.array_kernels.isna(rhou__ugklr, vfqm__peut[i]):
            bodo.libs.array_kernels.setna(shdhu__tjqlj, i)
        else:
            shdhu__tjqlj[i] = rhou__ugklr[vfqm__peut[i]]
    return shdhu__tjqlj


@register_jitable
def str_len(arr):
    fydh__joyk = arr._data
    vfqm__peut = arr._indices
    osk__knh = len(vfqm__peut)
    rhou__ugklr = bodo.libs.array_kernels.get_arr_lens(fydh__joyk, False)
    shdhu__tjqlj = bodo.libs.int_arr_ext.alloc_int_array(osk__knh, np.int64)
    for i in range(osk__knh):
        if bodo.libs.array_kernels.isna(vfqm__peut, i
            ) or bodo.libs.array_kernels.isna(rhou__ugklr, vfqm__peut[i]):
            bodo.libs.array_kernels.setna(shdhu__tjqlj, i)
        else:
            shdhu__tjqlj[i] = rhou__ugklr[vfqm__peut[i]]
    return shdhu__tjqlj


@register_jitable
def str_slice(arr, start, stop, step):
    fydh__joyk = arr._data
    xax__opdlb = len(fydh__joyk)
    pjmc__pncc = bodo.libs.str_arr_ext.pre_alloc_string_array(xax__opdlb, -1)
    for i in range(xax__opdlb):
        if bodo.libs.array_kernels.isna(fydh__joyk, i):
            bodo.libs.array_kernels.setna(pjmc__pncc, i)
            continue
        pjmc__pncc[i] = fydh__joyk[i][start:stop:step]
    return init_dict_arr(pjmc__pncc, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    fydh__joyk = arr._data
    vfqm__peut = arr._indices
    xax__opdlb = len(fydh__joyk)
    osk__knh = len(vfqm__peut)
    pjmc__pncc = pre_alloc_string_array(xax__opdlb, -1)
    wvzrv__ani = pre_alloc_string_array(osk__knh, -1)
    for dbnwz__zev in range(xax__opdlb):
        if bodo.libs.array_kernels.isna(fydh__joyk, dbnwz__zev) or not -len(
            fydh__joyk[dbnwz__zev]) <= i < len(fydh__joyk[dbnwz__zev]):
            bodo.libs.array_kernels.setna(pjmc__pncc, dbnwz__zev)
            continue
        pjmc__pncc[dbnwz__zev] = fydh__joyk[dbnwz__zev][i]
    for dbnwz__zev in range(osk__knh):
        if bodo.libs.array_kernels.isna(vfqm__peut, dbnwz__zev
            ) or bodo.libs.array_kernels.isna(pjmc__pncc, vfqm__peut[
            dbnwz__zev]):
            bodo.libs.array_kernels.setna(wvzrv__ani, dbnwz__zev)
            continue
        wvzrv__ani[dbnwz__zev] = pjmc__pncc[vfqm__peut[dbnwz__zev]]
    return wvzrv__ani


@register_jitable
def str_repeat_int(arr, repeats):
    fydh__joyk = arr._data
    xax__opdlb = len(fydh__joyk)
    pjmc__pncc = pre_alloc_string_array(xax__opdlb, -1)
    for i in range(xax__opdlb):
        if bodo.libs.array_kernels.isna(fydh__joyk, i):
            bodo.libs.array_kernels.setna(pjmc__pncc, i)
            continue
        pjmc__pncc[i] = fydh__joyk[i] * repeats
    return init_dict_arr(pjmc__pncc, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    zqx__tbem = f"""def str_{func_name}(arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    out_dict_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_data)
    out_bool_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_indices)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_dict_arr, i)
            continue
        out_dict_arr[i] = np.bool_(data_arr[i].{func_name}())
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
            data_arr, indices_arr[i]        ):
            bodo.libs.array_kernels.setna(out_bool_arr, i)
        else:
            out_bool_arr[i] = out_dict_arr[indices_arr[i]]
    return out_bool_arr"""
    xow__dgt = {}
    exec(zqx__tbem, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, xow__dgt)
    return xow__dgt[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        imp__zikz = create_str2bool_methods(func_name)
        imp__zikz = register_jitable(imp__zikz)
        globals()[f'str_{func_name}'] = imp__zikz


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    fydh__joyk = arr._data
    vfqm__peut = arr._indices
    xax__opdlb = len(fydh__joyk)
    osk__knh = len(vfqm__peut)
    regex = re.compile(pat, flags=flags)
    qkg__xlgc = []
    for tfkka__drjr in range(n_cols):
        qkg__xlgc.append(pre_alloc_string_array(xax__opdlb, -1))
    evsn__mami = bodo.libs.bool_arr_ext.alloc_bool_array(xax__opdlb)
    snwn__fupy = vfqm__peut.copy()
    for i in range(xax__opdlb):
        if bodo.libs.array_kernels.isna(fydh__joyk, i):
            evsn__mami[i] = True
            for dbnwz__zev in range(n_cols):
                bodo.libs.array_kernels.setna(qkg__xlgc[dbnwz__zev], i)
            continue
        uzivs__fat = regex.search(fydh__joyk[i])
        if uzivs__fat:
            evsn__mami[i] = False
            wba__avk = uzivs__fat.groups()
            for dbnwz__zev in range(n_cols):
                qkg__xlgc[dbnwz__zev][i] = wba__avk[dbnwz__zev]
        else:
            evsn__mami[i] = True
            for dbnwz__zev in range(n_cols):
                bodo.libs.array_kernels.setna(qkg__xlgc[dbnwz__zev], i)
    for i in range(osk__knh):
        if evsn__mami[snwn__fupy[i]]:
            bodo.libs.array_kernels.setna(snwn__fupy, i)
    nwzk__odfsx = [init_dict_arr(qkg__xlgc[i], snwn__fupy.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return nwzk__odfsx


def create_extractall_methods(is_multi_group):
    fzvok__axj = '_multi' if is_multi_group else ''
    zqx__tbem = f"""def str_extractall{fzvok__axj}(arr, regex, n_cols, index_arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    indices_count = [0 for _ in range(n_data)]
    for i in range(n_indices):
        if not bodo.libs.array_kernels.isna(indices_arr, i):
            indices_count[indices_arr[i]] += 1
    dict_group_count = []
    out_dict_len = out_ind_len = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        dict_group_count.append((out_dict_len, len(m)))
        out_dict_len += len(m)
        out_ind_len += indices_count[i] * len(m)
    out_dict_arr_list = []
    for _ in range(n_cols):
        out_dict_arr_list.append(pre_alloc_string_array(out_dict_len, -1))
    out_indices_arr = bodo.libs.int_arr_ext.alloc_int_array(out_ind_len, np.int32)
    out_ind_arr = bodo.utils.utils.alloc_type(out_ind_len, index_arr, (-1,))
    out_match_arr = np.empty(out_ind_len, np.int64)
    curr_ind = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        for s in m:
            for j in range(n_cols):
                out_dict_arr_list[j][curr_ind] = s{'[j]' if is_multi_group else ''}
            curr_ind += 1
    curr_ind = 0
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i):
            continue
        n_rows = dict_group_count[indices_arr[i]][1]
        for k in range(n_rows):
            out_indices_arr[curr_ind] = dict_group_count[indices_arr[i]][0] + k
            out_ind_arr[curr_ind] = index_arr[i]
            out_match_arr[curr_ind] = k
            curr_ind += 1
    out_arr_list = [
        init_dict_arr(
            out_dict_arr_list[i], out_indices_arr.copy(), arr._has_global_dictionary
        )
        for i in range(n_cols)
    ]
    return (out_ind_arr, out_match_arr, out_arr_list) 
"""
    xow__dgt = {}
    exec(zqx__tbem, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, xow__dgt)
    return xow__dgt[f'str_extractall{fzvok__axj}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        fzvok__axj = '_multi' if is_multi_group else ''
        imp__zikz = create_extractall_methods(is_multi_group)
        imp__zikz = register_jitable(imp__zikz)
        globals()[f'str_extractall{fzvok__axj}'] = imp__zikz


_register_extractall_methods()
