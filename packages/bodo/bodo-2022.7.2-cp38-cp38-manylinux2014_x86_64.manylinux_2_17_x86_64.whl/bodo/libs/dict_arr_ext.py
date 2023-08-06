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
        vcqo__joook = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, vcqo__joook)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        ljlfp__qux, eko__jndo, yvjzq__mqu = args
        uggi__ifrf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        uggi__ifrf.data = ljlfp__qux
        uggi__ifrf.indices = eko__jndo
        uggi__ifrf.has_global_dictionary = yvjzq__mqu
        context.nrt.incref(builder, signature.args[0], ljlfp__qux)
        context.nrt.incref(builder, signature.args[1], eko__jndo)
        return uggi__ifrf._getvalue()
    wur__zcg = DictionaryArrayType(data_t)
    sulm__ocyx = wur__zcg(data_t, indices_t, types.bool_)
    return sulm__ocyx, codegen


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
        ztnwd__ecb = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(ztnwd__ecb, [val])
        c.pyapi.decref(ztnwd__ecb)
    uggi__ifrf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mbksf__bygug = c.pyapi.object_getattr_string(val, 'dictionary')
    fjaxg__fdvr = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    hqmc__eqs = c.pyapi.call_method(mbksf__bygug, 'to_numpy', (fjaxg__fdvr,))
    uggi__ifrf.data = c.unbox(typ.data, hqmc__eqs).value
    zgqd__oma = c.pyapi.object_getattr_string(val, 'indices')
    jqfxj__pdnir = c.context.insert_const_string(c.builder.module, 'pandas')
    gdzx__utsf = c.pyapi.import_module_noblock(jqfxj__pdnir)
    mml__xmey = c.pyapi.string_from_constant_string('Int32')
    tdsm__acehv = c.pyapi.call_method(gdzx__utsf, 'array', (zgqd__oma,
        mml__xmey))
    uggi__ifrf.indices = c.unbox(dict_indices_arr_type, tdsm__acehv).value
    uggi__ifrf.has_global_dictionary = c.context.get_constant(types.bool_, 
        False)
    c.pyapi.decref(mbksf__bygug)
    c.pyapi.decref(fjaxg__fdvr)
    c.pyapi.decref(hqmc__eqs)
    c.pyapi.decref(zgqd__oma)
    c.pyapi.decref(gdzx__utsf)
    c.pyapi.decref(mml__xmey)
    c.pyapi.decref(tdsm__acehv)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    fccr__ygwy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uggi__ifrf._getvalue(), is_error=fccr__ygwy)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    uggi__ifrf = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, uggi__ifrf.data)
        bzw__fhh = c.box(typ.data, uggi__ifrf.data)
        rijh__phykd = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, uggi__ifrf.indices)
        tqmz__ilvn = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        xpmd__xinld = cgutils.get_or_insert_function(c.builder.module,
            tqmz__ilvn, name='box_dict_str_array')
        agxmo__ibrcn = cgutils.create_struct_proxy(types.Array(types.int32,
            1, 'C'))(c.context, c.builder, rijh__phykd.data)
        zxjcy__juvy = c.builder.extract_value(agxmo__ibrcn.shape, 0)
        zcd__thhii = agxmo__ibrcn.data
        enn__eolzc = cgutils.create_struct_proxy(types.Array(types.int8, 1,
            'C'))(c.context, c.builder, rijh__phykd.null_bitmap).data
        hqmc__eqs = c.builder.call(xpmd__xinld, [zxjcy__juvy, bzw__fhh,
            zcd__thhii, enn__eolzc])
        c.pyapi.decref(bzw__fhh)
    else:
        jqfxj__pdnir = c.context.insert_const_string(c.builder.module,
            'pyarrow')
        ijtij__ugwbn = c.pyapi.import_module_noblock(jqfxj__pdnir)
        gmdbg__dlxo = c.pyapi.object_getattr_string(ijtij__ugwbn,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, uggi__ifrf.data)
        bzw__fhh = c.box(typ.data, uggi__ifrf.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, uggi__ifrf.
            indices)
        zgqd__oma = c.box(dict_indices_arr_type, uggi__ifrf.indices)
        ttrl__mwh = c.pyapi.call_method(gmdbg__dlxo, 'from_arrays', (
            zgqd__oma, bzw__fhh))
        fjaxg__fdvr = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        hqmc__eqs = c.pyapi.call_method(ttrl__mwh, 'to_numpy', (fjaxg__fdvr,))
        c.pyapi.decref(ijtij__ugwbn)
        c.pyapi.decref(bzw__fhh)
        c.pyapi.decref(zgqd__oma)
        c.pyapi.decref(gmdbg__dlxo)
        c.pyapi.decref(ttrl__mwh)
        c.pyapi.decref(fjaxg__fdvr)
    c.context.nrt.decref(c.builder, typ, val)
    return hqmc__eqs


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
    iuya__tdzs = pyval.dictionary.to_numpy(False)
    eimyt__iox = pd.array(pyval.indices, 'Int32')
    iuya__tdzs = context.get_constant_generic(builder, typ.data, iuya__tdzs)
    eimyt__iox = context.get_constant_generic(builder,
        dict_indices_arr_type, eimyt__iox)
    cidp__elsf = context.get_constant(types.bool_, False)
    uwje__qui = lir.Constant.literal_struct([iuya__tdzs, eimyt__iox,
        cidp__elsf])
    return uwje__qui


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            plwil__jwo = A._indices[ind]
            return A._data[plwil__jwo]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        ljlfp__qux = A._data
        eko__jndo = A._indices
        zxjcy__juvy = len(eko__jndo)
        nxbe__eibq = [get_str_arr_item_length(ljlfp__qux, i) for i in range
            (len(ljlfp__qux))]
        vtkbl__vwhat = 0
        for i in range(zxjcy__juvy):
            if not bodo.libs.array_kernels.isna(eko__jndo, i):
                vtkbl__vwhat += nxbe__eibq[eko__jndo[i]]
        jpol__klgu = pre_alloc_string_array(zxjcy__juvy, vtkbl__vwhat)
        for i in range(zxjcy__juvy):
            if bodo.libs.array_kernels.isna(eko__jndo, i):
                bodo.libs.array_kernels.setna(jpol__klgu, i)
                continue
            ind = eko__jndo[i]
            if bodo.libs.array_kernels.isna(ljlfp__qux, ind):
                bodo.libs.array_kernels.setna(jpol__klgu, i)
                continue
            jpol__klgu[i] = ljlfp__qux[ind]
        return jpol__klgu
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    plwil__jwo = -1
    ljlfp__qux = arr._data
    for i in range(len(ljlfp__qux)):
        if bodo.libs.array_kernels.isna(ljlfp__qux, i):
            continue
        if ljlfp__qux[i] == val:
            plwil__jwo = i
            break
    return plwil__jwo


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    zxjcy__juvy = len(arr)
    plwil__jwo = find_dict_ind(arr, val)
    if plwil__jwo == -1:
        return init_bool_array(np.full(zxjcy__juvy, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == plwil__jwo


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    zxjcy__juvy = len(arr)
    plwil__jwo = find_dict_ind(arr, val)
    if plwil__jwo == -1:
        return init_bool_array(np.full(zxjcy__juvy, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != plwil__jwo


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
        tnlhm__thrl = arr._data
        hcga__ikxtv = bodo.libs.int_arr_ext.alloc_int_array(len(tnlhm__thrl
            ), dtype)
        for moesq__uhqca in range(len(tnlhm__thrl)):
            if bodo.libs.array_kernels.isna(tnlhm__thrl, moesq__uhqca):
                bodo.libs.array_kernels.setna(hcga__ikxtv, moesq__uhqca)
                continue
            hcga__ikxtv[moesq__uhqca] = np.int64(tnlhm__thrl[moesq__uhqca])
        zxjcy__juvy = len(arr)
        eko__jndo = arr._indices
        jpol__klgu = bodo.libs.int_arr_ext.alloc_int_array(zxjcy__juvy, dtype)
        for i in range(zxjcy__juvy):
            if bodo.libs.array_kernels.isna(eko__jndo, i):
                bodo.libs.array_kernels.setna(jpol__klgu, i)
                continue
            jpol__klgu[i] = hcga__ikxtv[eko__jndo[i]]
        return jpol__klgu
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    lqk__uyyi = len(arrs)
    hppf__wxyjo = 'def impl(arrs, sep):\n'
    hppf__wxyjo += '  ind_map = {}\n'
    hppf__wxyjo += '  out_strs = []\n'
    hppf__wxyjo += '  n = len(arrs[0])\n'
    for i in range(lqk__uyyi):
        hppf__wxyjo += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(lqk__uyyi):
        hppf__wxyjo += f'  data{i} = arrs[{i}]._data\n'
    hppf__wxyjo += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    hppf__wxyjo += '  for i in range(n):\n'
    norz__yvufz = ' or '.join([
        f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for i in range(
        lqk__uyyi)])
    hppf__wxyjo += f'    if {norz__yvufz}:\n'
    hppf__wxyjo += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    hppf__wxyjo += '      continue\n'
    for i in range(lqk__uyyi):
        hppf__wxyjo += f'    ind{i} = indices{i}[i]\n'
    mqli__lfcs = '(' + ', '.join(f'ind{i}' for i in range(lqk__uyyi)) + ')'
    hppf__wxyjo += f'    if {mqli__lfcs} not in ind_map:\n'
    hppf__wxyjo += '      out_ind = len(out_strs)\n'
    hppf__wxyjo += f'      ind_map[{mqli__lfcs}] = out_ind\n'
    aqzk__gjppt = "''" if is_overload_none(sep) else 'sep'
    pmtul__htl = ', '.join([f'data{i}[ind{i}]' for i in range(lqk__uyyi)])
    hppf__wxyjo += f'      v = {aqzk__gjppt}.join([{pmtul__htl}])\n'
    hppf__wxyjo += '      out_strs.append(v)\n'
    hppf__wxyjo += '    else:\n'
    hppf__wxyjo += f'      out_ind = ind_map[{mqli__lfcs}]\n'
    hppf__wxyjo += '    out_indices[i] = out_ind\n'
    hppf__wxyjo += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    hppf__wxyjo += """  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)
"""
    jsb__iksxz = {}
    exec(hppf__wxyjo, {'bodo': bodo, 'numba': numba, 'np': np}, jsb__iksxz)
    impl = jsb__iksxz['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    pukd__cryx = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    sulm__ocyx = toty(fromty)
    emsu__iqqh = context.compile_internal(builder, pukd__cryx, sulm__ocyx,
        (val,))
    return impl_ret_new_ref(context, builder, toty, emsu__iqqh)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    iuya__tdzs = arr._data
    gdx__bat = len(iuya__tdzs)
    pmd__vvuqk = pre_alloc_string_array(gdx__bat, -1)
    if regex:
        cnk__tnsz = re.compile(pat, flags)
        for i in range(gdx__bat):
            if bodo.libs.array_kernels.isna(iuya__tdzs, i):
                bodo.libs.array_kernels.setna(pmd__vvuqk, i)
                continue
            pmd__vvuqk[i] = cnk__tnsz.sub(repl=repl, string=iuya__tdzs[i])
    else:
        for i in range(gdx__bat):
            if bodo.libs.array_kernels.isna(iuya__tdzs, i):
                bodo.libs.array_kernels.setna(pmd__vvuqk, i)
                continue
            pmd__vvuqk[i] = iuya__tdzs[i].replace(pat, repl)
    return init_dict_arr(pmd__vvuqk, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    uggi__ifrf = arr._data
    wmizj__flff = len(uggi__ifrf)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(wmizj__flff)
    for i in range(wmizj__flff):
        dict_arr_out[i] = uggi__ifrf[i].startswith(pat)
    eimyt__iox = arr._indices
    isi__luaou = len(eimyt__iox)
    jpol__klgu = bodo.libs.bool_arr_ext.alloc_bool_array(isi__luaou)
    for i in range(isi__luaou):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpol__klgu, i)
        else:
            jpol__klgu[i] = dict_arr_out[eimyt__iox[i]]
    return jpol__klgu


@register_jitable
def str_endswith(arr, pat, na):
    uggi__ifrf = arr._data
    wmizj__flff = len(uggi__ifrf)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(wmizj__flff)
    for i in range(wmizj__flff):
        dict_arr_out[i] = uggi__ifrf[i].endswith(pat)
    eimyt__iox = arr._indices
    isi__luaou = len(eimyt__iox)
    jpol__klgu = bodo.libs.bool_arr_ext.alloc_bool_array(isi__luaou)
    for i in range(isi__luaou):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpol__klgu, i)
        else:
            jpol__klgu[i] = dict_arr_out[eimyt__iox[i]]
    return jpol__klgu


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    uggi__ifrf = arr._data
    say__pwqvi = pd.Series(uggi__ifrf)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = say__pwqvi.array._str_contains(pat, case, flags, na,
            regex)
    eimyt__iox = arr._indices
    isi__luaou = len(eimyt__iox)
    jpol__klgu = bodo.libs.bool_arr_ext.alloc_bool_array(isi__luaou)
    for i in range(isi__luaou):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpol__klgu, i)
        else:
            jpol__klgu[i] = dict_arr_out[eimyt__iox[i]]
    return jpol__klgu


@register_jitable
def str_contains_non_regex(arr, pat, case):
    uggi__ifrf = arr._data
    wmizj__flff = len(uggi__ifrf)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(wmizj__flff)
    if not case:
        xkg__eyol = pat.upper()
    for i in range(wmizj__flff):
        if case:
            dict_arr_out[i] = pat in uggi__ifrf[i]
        else:
            dict_arr_out[i] = xkg__eyol in uggi__ifrf[i].upper()
    eimyt__iox = arr._indices
    isi__luaou = len(eimyt__iox)
    jpol__klgu = bodo.libs.bool_arr_ext.alloc_bool_array(isi__luaou)
    for i in range(isi__luaou):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpol__klgu, i)
        else:
            jpol__klgu[i] = dict_arr_out[eimyt__iox[i]]
    return jpol__klgu


@numba.njit
def str_match(arr, pat, case, flags, na):
    uggi__ifrf = arr._data
    eimyt__iox = arr._indices
    isi__luaou = len(eimyt__iox)
    jpol__klgu = bodo.libs.bool_arr_ext.alloc_bool_array(isi__luaou)
    say__pwqvi = pd.Series(uggi__ifrf)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = say__pwqvi.array._str_match(pat, case, flags, na)
    for i in range(isi__luaou):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpol__klgu, i)
        else:
            jpol__klgu[i] = dict_arr_out[eimyt__iox[i]]
    return jpol__klgu


def create_simple_str2str_methods(func_name, func_args):
    hppf__wxyjo = f"""def str_{func_name}({', '.join(func_args)}):
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
    jsb__iksxz = {}
    exec(hppf__wxyjo, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, jsb__iksxz)
    return jsb__iksxz[f'str_{func_name}']


def _register_simple_str2str_methods():
    oips__qfjvr = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in oips__qfjvr.keys():
        qetq__scnv = create_simple_str2str_methods(func_name, oips__qfjvr[
            func_name])
        qetq__scnv = register_jitable(qetq__scnv)
        globals()[f'str_{func_name}'] = qetq__scnv


_register_simple_str2str_methods()


def create_find_methods(func_name):
    hppf__wxyjo = f"""def str_{func_name}(arr, sub, start, end):
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
    jsb__iksxz = {}
    exec(hppf__wxyjo, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, jsb__iksxz)
    return jsb__iksxz[f'str_{func_name}']


def _register_find_methods():
    hto__tzum = ['find', 'rfind']
    for func_name in hto__tzum:
        qetq__scnv = create_find_methods(func_name)
        qetq__scnv = register_jitable(qetq__scnv)
        globals()[f'str_{func_name}'] = qetq__scnv


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    iuya__tdzs = arr._data
    eimyt__iox = arr._indices
    gdx__bat = len(iuya__tdzs)
    isi__luaou = len(eimyt__iox)
    rvicq__ivdk = bodo.libs.int_arr_ext.alloc_int_array(gdx__bat, np.int64)
    ankad__fqwwc = bodo.libs.int_arr_ext.alloc_int_array(isi__luaou, np.int64)
    regex = re.compile(pat, flags)
    for i in range(gdx__bat):
        if bodo.libs.array_kernels.isna(iuya__tdzs, i):
            bodo.libs.array_kernels.setna(rvicq__ivdk, i)
            continue
        rvicq__ivdk[i] = bodo.libs.str_ext.str_findall_count(regex,
            iuya__tdzs[i])
    for i in range(isi__luaou):
        if bodo.libs.array_kernels.isna(eimyt__iox, i
            ) or bodo.libs.array_kernels.isna(rvicq__ivdk, eimyt__iox[i]):
            bodo.libs.array_kernels.setna(ankad__fqwwc, i)
        else:
            ankad__fqwwc[i] = rvicq__ivdk[eimyt__iox[i]]
    return ankad__fqwwc


@register_jitable
def str_len(arr):
    iuya__tdzs = arr._data
    eimyt__iox = arr._indices
    isi__luaou = len(eimyt__iox)
    rvicq__ivdk = bodo.libs.array_kernels.get_arr_lens(iuya__tdzs, False)
    ankad__fqwwc = bodo.libs.int_arr_ext.alloc_int_array(isi__luaou, np.int64)
    for i in range(isi__luaou):
        if bodo.libs.array_kernels.isna(eimyt__iox, i
            ) or bodo.libs.array_kernels.isna(rvicq__ivdk, eimyt__iox[i]):
            bodo.libs.array_kernels.setna(ankad__fqwwc, i)
        else:
            ankad__fqwwc[i] = rvicq__ivdk[eimyt__iox[i]]
    return ankad__fqwwc


@register_jitable
def str_slice(arr, start, stop, step):
    iuya__tdzs = arr._data
    gdx__bat = len(iuya__tdzs)
    pmd__vvuqk = bodo.libs.str_arr_ext.pre_alloc_string_array(gdx__bat, -1)
    for i in range(gdx__bat):
        if bodo.libs.array_kernels.isna(iuya__tdzs, i):
            bodo.libs.array_kernels.setna(pmd__vvuqk, i)
            continue
        pmd__vvuqk[i] = iuya__tdzs[i][start:stop:step]
    return init_dict_arr(pmd__vvuqk, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    iuya__tdzs = arr._data
    eimyt__iox = arr._indices
    gdx__bat = len(iuya__tdzs)
    isi__luaou = len(eimyt__iox)
    pmd__vvuqk = pre_alloc_string_array(gdx__bat, -1)
    jpol__klgu = pre_alloc_string_array(isi__luaou, -1)
    for moesq__uhqca in range(gdx__bat):
        if bodo.libs.array_kernels.isna(iuya__tdzs, moesq__uhqca) or not -len(
            iuya__tdzs[moesq__uhqca]) <= i < len(iuya__tdzs[moesq__uhqca]):
            bodo.libs.array_kernels.setna(pmd__vvuqk, moesq__uhqca)
            continue
        pmd__vvuqk[moesq__uhqca] = iuya__tdzs[moesq__uhqca][i]
    for moesq__uhqca in range(isi__luaou):
        if bodo.libs.array_kernels.isna(eimyt__iox, moesq__uhqca
            ) or bodo.libs.array_kernels.isna(pmd__vvuqk, eimyt__iox[
            moesq__uhqca]):
            bodo.libs.array_kernels.setna(jpol__klgu, moesq__uhqca)
            continue
        jpol__klgu[moesq__uhqca] = pmd__vvuqk[eimyt__iox[moesq__uhqca]]
    return jpol__klgu


@register_jitable
def str_repeat_int(arr, repeats):
    iuya__tdzs = arr._data
    gdx__bat = len(iuya__tdzs)
    pmd__vvuqk = pre_alloc_string_array(gdx__bat, -1)
    for i in range(gdx__bat):
        if bodo.libs.array_kernels.isna(iuya__tdzs, i):
            bodo.libs.array_kernels.setna(pmd__vvuqk, i)
            continue
        pmd__vvuqk[i] = iuya__tdzs[i] * repeats
    return init_dict_arr(pmd__vvuqk, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    hppf__wxyjo = f"""def str_{func_name}(arr):
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
    jsb__iksxz = {}
    exec(hppf__wxyjo, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, jsb__iksxz)
    return jsb__iksxz[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        qetq__scnv = create_str2bool_methods(func_name)
        qetq__scnv = register_jitable(qetq__scnv)
        globals()[f'str_{func_name}'] = qetq__scnv


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    iuya__tdzs = arr._data
    eimyt__iox = arr._indices
    gdx__bat = len(iuya__tdzs)
    isi__luaou = len(eimyt__iox)
    regex = re.compile(pat, flags=flags)
    feu__wgg = []
    for fmn__tkowf in range(n_cols):
        feu__wgg.append(pre_alloc_string_array(gdx__bat, -1))
    truns__kha = bodo.libs.bool_arr_ext.alloc_bool_array(gdx__bat)
    ikfsz__lwulv = eimyt__iox.copy()
    for i in range(gdx__bat):
        if bodo.libs.array_kernels.isna(iuya__tdzs, i):
            truns__kha[i] = True
            for moesq__uhqca in range(n_cols):
                bodo.libs.array_kernels.setna(feu__wgg[moesq__uhqca], i)
            continue
        hlkrt__fykqz = regex.search(iuya__tdzs[i])
        if hlkrt__fykqz:
            truns__kha[i] = False
            gbk__fvay = hlkrt__fykqz.groups()
            for moesq__uhqca in range(n_cols):
                feu__wgg[moesq__uhqca][i] = gbk__fvay[moesq__uhqca]
        else:
            truns__kha[i] = True
            for moesq__uhqca in range(n_cols):
                bodo.libs.array_kernels.setna(feu__wgg[moesq__uhqca], i)
    for i in range(isi__luaou):
        if truns__kha[ikfsz__lwulv[i]]:
            bodo.libs.array_kernels.setna(ikfsz__lwulv, i)
    iflmt__mno = [init_dict_arr(feu__wgg[i], ikfsz__lwulv.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return iflmt__mno


def create_extractall_methods(is_multi_group):
    ymkj__wvn = '_multi' if is_multi_group else ''
    hppf__wxyjo = f"""def str_extractall{ymkj__wvn}(arr, regex, n_cols, index_arr):
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
    jsb__iksxz = {}
    exec(hppf__wxyjo, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, jsb__iksxz)
    return jsb__iksxz[f'str_extractall{ymkj__wvn}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        ymkj__wvn = '_multi' if is_multi_group else ''
        qetq__scnv = create_extractall_methods(is_multi_group)
        qetq__scnv = register_jitable(qetq__scnv)
        globals()[f'str_extractall{ymkj__wvn}'] = qetq__scnv


_register_extractall_methods()
