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
        zgdq__uoowm = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, zgdq__uoowm)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        ntikp__xrhs, fwhaf__ext, lqczl__qdh = args
        lna__luh = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        lna__luh.data = ntikp__xrhs
        lna__luh.indices = fwhaf__ext
        lna__luh.has_global_dictionary = lqczl__qdh
        context.nrt.incref(builder, signature.args[0], ntikp__xrhs)
        context.nrt.incref(builder, signature.args[1], fwhaf__ext)
        return lna__luh._getvalue()
    ait__gzrjy = DictionaryArrayType(data_t)
    gmwii__ffx = ait__gzrjy(data_t, indices_t, types.bool_)
    return gmwii__ffx, codegen


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
        olvh__baec = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(olvh__baec, [val])
        c.pyapi.decref(olvh__baec)
    lna__luh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    efxxo__vcgvz = c.pyapi.object_getattr_string(val, 'dictionary')
    xdo__oqlgg = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    bmdv__ykf = c.pyapi.call_method(efxxo__vcgvz, 'to_numpy', (xdo__oqlgg,))
    lna__luh.data = c.unbox(typ.data, bmdv__ykf).value
    idifv__vprbj = c.pyapi.object_getattr_string(val, 'indices')
    qtd__snga = c.context.insert_const_string(c.builder.module, 'pandas')
    nur__auwz = c.pyapi.import_module_noblock(qtd__snga)
    dwsrs__nhmi = c.pyapi.string_from_constant_string('Int32')
    buv__rihh = c.pyapi.call_method(nur__auwz, 'array', (idifv__vprbj,
        dwsrs__nhmi))
    lna__luh.indices = c.unbox(dict_indices_arr_type, buv__rihh).value
    lna__luh.has_global_dictionary = c.context.get_constant(types.bool_, False)
    c.pyapi.decref(efxxo__vcgvz)
    c.pyapi.decref(xdo__oqlgg)
    c.pyapi.decref(bmdv__ykf)
    c.pyapi.decref(idifv__vprbj)
    c.pyapi.decref(nur__auwz)
    c.pyapi.decref(dwsrs__nhmi)
    c.pyapi.decref(buv__rihh)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    dxr__iat = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(lna__luh._getvalue(), is_error=dxr__iat)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    lna__luh = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, lna__luh.data)
        xssc__ggn = c.box(typ.data, lna__luh.data)
        owf__dyar = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, lna__luh.indices)
        acax__azk = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        vukul__nuu = cgutils.get_or_insert_function(c.builder.module,
            acax__azk, name='box_dict_str_array')
        vdakw__alvzt = cgutils.create_struct_proxy(types.Array(types.int32,
            1, 'C'))(c.context, c.builder, owf__dyar.data)
        hxh__nxvys = c.builder.extract_value(vdakw__alvzt.shape, 0)
        pux__wmv = vdakw__alvzt.data
        tbfe__alw = cgutils.create_struct_proxy(types.Array(types.int8, 1, 'C')
            )(c.context, c.builder, owf__dyar.null_bitmap).data
        bmdv__ykf = c.builder.call(vukul__nuu, [hxh__nxvys, xssc__ggn,
            pux__wmv, tbfe__alw])
        c.pyapi.decref(xssc__ggn)
    else:
        qtd__snga = c.context.insert_const_string(c.builder.module, 'pyarrow')
        qmzxc__oduo = c.pyapi.import_module_noblock(qtd__snga)
        heru__qrzgv = c.pyapi.object_getattr_string(qmzxc__oduo,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, lna__luh.data)
        xssc__ggn = c.box(typ.data, lna__luh.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, lna__luh.indices
            )
        idifv__vprbj = c.box(dict_indices_arr_type, lna__luh.indices)
        mwqwf__ulxxo = c.pyapi.call_method(heru__qrzgv, 'from_arrays', (
            idifv__vprbj, xssc__ggn))
        xdo__oqlgg = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        bmdv__ykf = c.pyapi.call_method(mwqwf__ulxxo, 'to_numpy', (xdo__oqlgg,)
            )
        c.pyapi.decref(qmzxc__oduo)
        c.pyapi.decref(xssc__ggn)
        c.pyapi.decref(idifv__vprbj)
        c.pyapi.decref(heru__qrzgv)
        c.pyapi.decref(mwqwf__ulxxo)
        c.pyapi.decref(xdo__oqlgg)
    c.context.nrt.decref(c.builder, typ, val)
    return bmdv__ykf


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
    hur__vbsp = pyval.dictionary.to_numpy(False)
    hlcwh__ysr = pd.array(pyval.indices, 'Int32')
    hur__vbsp = context.get_constant_generic(builder, typ.data, hur__vbsp)
    hlcwh__ysr = context.get_constant_generic(builder,
        dict_indices_arr_type, hlcwh__ysr)
    nphbz__oocyo = context.get_constant(types.bool_, False)
    bpg__llvr = lir.Constant.literal_struct([hur__vbsp, hlcwh__ysr,
        nphbz__oocyo])
    return bpg__llvr


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            wnzd__kqoed = A._indices[ind]
            return A._data[wnzd__kqoed]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        ntikp__xrhs = A._data
        fwhaf__ext = A._indices
        hxh__nxvys = len(fwhaf__ext)
        xwa__mzm = [get_str_arr_item_length(ntikp__xrhs, i) for i in range(
            len(ntikp__xrhs))]
        cxzdd__elcf = 0
        for i in range(hxh__nxvys):
            if not bodo.libs.array_kernels.isna(fwhaf__ext, i):
                cxzdd__elcf += xwa__mzm[fwhaf__ext[i]]
        zwjsx__grb = pre_alloc_string_array(hxh__nxvys, cxzdd__elcf)
        for i in range(hxh__nxvys):
            if bodo.libs.array_kernels.isna(fwhaf__ext, i):
                bodo.libs.array_kernels.setna(zwjsx__grb, i)
                continue
            ind = fwhaf__ext[i]
            if bodo.libs.array_kernels.isna(ntikp__xrhs, ind):
                bodo.libs.array_kernels.setna(zwjsx__grb, i)
                continue
            zwjsx__grb[i] = ntikp__xrhs[ind]
        return zwjsx__grb
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    wnzd__kqoed = -1
    ntikp__xrhs = arr._data
    for i in range(len(ntikp__xrhs)):
        if bodo.libs.array_kernels.isna(ntikp__xrhs, i):
            continue
        if ntikp__xrhs[i] == val:
            wnzd__kqoed = i
            break
    return wnzd__kqoed


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    hxh__nxvys = len(arr)
    wnzd__kqoed = find_dict_ind(arr, val)
    if wnzd__kqoed == -1:
        return init_bool_array(np.full(hxh__nxvys, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == wnzd__kqoed


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    hxh__nxvys = len(arr)
    wnzd__kqoed = find_dict_ind(arr, val)
    if wnzd__kqoed == -1:
        return init_bool_array(np.full(hxh__nxvys, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != wnzd__kqoed


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
        rdrr__cjq = arr._data
        rmm__bhvcw = bodo.libs.int_arr_ext.alloc_int_array(len(rdrr__cjq),
            dtype)
        for qbpte__ybvhc in range(len(rdrr__cjq)):
            if bodo.libs.array_kernels.isna(rdrr__cjq, qbpte__ybvhc):
                bodo.libs.array_kernels.setna(rmm__bhvcw, qbpte__ybvhc)
                continue
            rmm__bhvcw[qbpte__ybvhc] = np.int64(rdrr__cjq[qbpte__ybvhc])
        hxh__nxvys = len(arr)
        fwhaf__ext = arr._indices
        zwjsx__grb = bodo.libs.int_arr_ext.alloc_int_array(hxh__nxvys, dtype)
        for i in range(hxh__nxvys):
            if bodo.libs.array_kernels.isna(fwhaf__ext, i):
                bodo.libs.array_kernels.setna(zwjsx__grb, i)
                continue
            zwjsx__grb[i] = rmm__bhvcw[fwhaf__ext[i]]
        return zwjsx__grb
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    glw__kfp = len(arrs)
    troy__mdf = 'def impl(arrs, sep):\n'
    troy__mdf += '  ind_map = {}\n'
    troy__mdf += '  out_strs = []\n'
    troy__mdf += '  n = len(arrs[0])\n'
    for i in range(glw__kfp):
        troy__mdf += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(glw__kfp):
        troy__mdf += f'  data{i} = arrs[{i}]._data\n'
    troy__mdf += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    troy__mdf += '  for i in range(n):\n'
    hyriq__upsh = ' or '.join([
        f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for i in range(glw__kfp)]
        )
    troy__mdf += f'    if {hyriq__upsh}:\n'
    troy__mdf += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    troy__mdf += '      continue\n'
    for i in range(glw__kfp):
        troy__mdf += f'    ind{i} = indices{i}[i]\n'
    ehtz__bvyjp = '(' + ', '.join(f'ind{i}' for i in range(glw__kfp)) + ')'
    troy__mdf += f'    if {ehtz__bvyjp} not in ind_map:\n'
    troy__mdf += '      out_ind = len(out_strs)\n'
    troy__mdf += f'      ind_map[{ehtz__bvyjp}] = out_ind\n'
    yjk__maka = "''" if is_overload_none(sep) else 'sep'
    zoujj__tltq = ', '.join([f'data{i}[ind{i}]' for i in range(glw__kfp)])
    troy__mdf += f'      v = {yjk__maka}.join([{zoujj__tltq}])\n'
    troy__mdf += '      out_strs.append(v)\n'
    troy__mdf += '    else:\n'
    troy__mdf += f'      out_ind = ind_map[{ehtz__bvyjp}]\n'
    troy__mdf += '    out_indices[i] = out_ind\n'
    troy__mdf += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    troy__mdf += (
        '  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)\n'
        )
    iave__myyqz = {}
    exec(troy__mdf, {'bodo': bodo, 'numba': numba, 'np': np}, iave__myyqz)
    impl = iave__myyqz['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    gdhaj__xdi = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    gmwii__ffx = toty(fromty)
    gusop__dwnx = context.compile_internal(builder, gdhaj__xdi, gmwii__ffx,
        (val,))
    return impl_ret_new_ref(context, builder, toty, gusop__dwnx)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    hur__vbsp = arr._data
    uwpd__ikr = len(hur__vbsp)
    opv__gnkp = pre_alloc_string_array(uwpd__ikr, -1)
    if regex:
        sstkf__gtcxr = re.compile(pat, flags)
        for i in range(uwpd__ikr):
            if bodo.libs.array_kernels.isna(hur__vbsp, i):
                bodo.libs.array_kernels.setna(opv__gnkp, i)
                continue
            opv__gnkp[i] = sstkf__gtcxr.sub(repl=repl, string=hur__vbsp[i])
    else:
        for i in range(uwpd__ikr):
            if bodo.libs.array_kernels.isna(hur__vbsp, i):
                bodo.libs.array_kernels.setna(opv__gnkp, i)
                continue
            opv__gnkp[i] = hur__vbsp[i].replace(pat, repl)
    return init_dict_arr(opv__gnkp, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    lna__luh = arr._data
    vgh__zgmad = len(lna__luh)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(vgh__zgmad)
    for i in range(vgh__zgmad):
        dict_arr_out[i] = lna__luh[i].startswith(pat)
    hlcwh__ysr = arr._indices
    wwc__gjki = len(hlcwh__ysr)
    zwjsx__grb = bodo.libs.bool_arr_ext.alloc_bool_array(wwc__gjki)
    for i in range(wwc__gjki):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(zwjsx__grb, i)
        else:
            zwjsx__grb[i] = dict_arr_out[hlcwh__ysr[i]]
    return zwjsx__grb


@register_jitable
def str_endswith(arr, pat, na):
    lna__luh = arr._data
    vgh__zgmad = len(lna__luh)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(vgh__zgmad)
    for i in range(vgh__zgmad):
        dict_arr_out[i] = lna__luh[i].endswith(pat)
    hlcwh__ysr = arr._indices
    wwc__gjki = len(hlcwh__ysr)
    zwjsx__grb = bodo.libs.bool_arr_ext.alloc_bool_array(wwc__gjki)
    for i in range(wwc__gjki):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(zwjsx__grb, i)
        else:
            zwjsx__grb[i] = dict_arr_out[hlcwh__ysr[i]]
    return zwjsx__grb


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    lna__luh = arr._data
    lnzaw__rzbb = pd.Series(lna__luh)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = lnzaw__rzbb.array._str_contains(pat, case, flags, na,
            regex)
    hlcwh__ysr = arr._indices
    wwc__gjki = len(hlcwh__ysr)
    zwjsx__grb = bodo.libs.bool_arr_ext.alloc_bool_array(wwc__gjki)
    for i in range(wwc__gjki):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(zwjsx__grb, i)
        else:
            zwjsx__grb[i] = dict_arr_out[hlcwh__ysr[i]]
    return zwjsx__grb


@register_jitable
def str_contains_non_regex(arr, pat, case):
    lna__luh = arr._data
    vgh__zgmad = len(lna__luh)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(vgh__zgmad)
    if not case:
        rzac__tkk = pat.upper()
    for i in range(vgh__zgmad):
        if case:
            dict_arr_out[i] = pat in lna__luh[i]
        else:
            dict_arr_out[i] = rzac__tkk in lna__luh[i].upper()
    hlcwh__ysr = arr._indices
    wwc__gjki = len(hlcwh__ysr)
    zwjsx__grb = bodo.libs.bool_arr_ext.alloc_bool_array(wwc__gjki)
    for i in range(wwc__gjki):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(zwjsx__grb, i)
        else:
            zwjsx__grb[i] = dict_arr_out[hlcwh__ysr[i]]
    return zwjsx__grb


@numba.njit
def str_match(arr, pat, case, flags, na):
    lna__luh = arr._data
    hlcwh__ysr = arr._indices
    wwc__gjki = len(hlcwh__ysr)
    zwjsx__grb = bodo.libs.bool_arr_ext.alloc_bool_array(wwc__gjki)
    lnzaw__rzbb = pd.Series(lna__luh)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = lnzaw__rzbb.array._str_match(pat, case, flags, na)
    for i in range(wwc__gjki):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(zwjsx__grb, i)
        else:
            zwjsx__grb[i] = dict_arr_out[hlcwh__ysr[i]]
    return zwjsx__grb


def create_simple_str2str_methods(func_name, func_args):
    troy__mdf = f"""def str_{func_name}({', '.join(func_args)}):
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
    iave__myyqz = {}
    exec(troy__mdf, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, iave__myyqz)
    return iave__myyqz[f'str_{func_name}']


def _register_simple_str2str_methods():
    mxxcg__hurfp = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in mxxcg__hurfp.keys():
        xgeoh__sffjc = create_simple_str2str_methods(func_name,
            mxxcg__hurfp[func_name])
        xgeoh__sffjc = register_jitable(xgeoh__sffjc)
        globals()[f'str_{func_name}'] = xgeoh__sffjc


_register_simple_str2str_methods()


def create_find_methods(func_name):
    troy__mdf = f"""def str_{func_name}(arr, sub, start, end):
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
    iave__myyqz = {}
    exec(troy__mdf, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, iave__myyqz)
    return iave__myyqz[f'str_{func_name}']


def _register_find_methods():
    ffd__evm = ['find', 'rfind']
    for func_name in ffd__evm:
        xgeoh__sffjc = create_find_methods(func_name)
        xgeoh__sffjc = register_jitable(xgeoh__sffjc)
        globals()[f'str_{func_name}'] = xgeoh__sffjc


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    hur__vbsp = arr._data
    hlcwh__ysr = arr._indices
    uwpd__ikr = len(hur__vbsp)
    wwc__gjki = len(hlcwh__ysr)
    tbpk__wnfs = bodo.libs.int_arr_ext.alloc_int_array(uwpd__ikr, np.int64)
    vqmdr__ufnvs = bodo.libs.int_arr_ext.alloc_int_array(wwc__gjki, np.int64)
    regex = re.compile(pat, flags)
    for i in range(uwpd__ikr):
        if bodo.libs.array_kernels.isna(hur__vbsp, i):
            bodo.libs.array_kernels.setna(tbpk__wnfs, i)
            continue
        tbpk__wnfs[i] = bodo.libs.str_ext.str_findall_count(regex, hur__vbsp[i]
            )
    for i in range(wwc__gjki):
        if bodo.libs.array_kernels.isna(hlcwh__ysr, i
            ) or bodo.libs.array_kernels.isna(tbpk__wnfs, hlcwh__ysr[i]):
            bodo.libs.array_kernels.setna(vqmdr__ufnvs, i)
        else:
            vqmdr__ufnvs[i] = tbpk__wnfs[hlcwh__ysr[i]]
    return vqmdr__ufnvs


@register_jitable
def str_len(arr):
    hur__vbsp = arr._data
    hlcwh__ysr = arr._indices
    wwc__gjki = len(hlcwh__ysr)
    tbpk__wnfs = bodo.libs.array_kernels.get_arr_lens(hur__vbsp, False)
    vqmdr__ufnvs = bodo.libs.int_arr_ext.alloc_int_array(wwc__gjki, np.int64)
    for i in range(wwc__gjki):
        if bodo.libs.array_kernels.isna(hlcwh__ysr, i
            ) or bodo.libs.array_kernels.isna(tbpk__wnfs, hlcwh__ysr[i]):
            bodo.libs.array_kernels.setna(vqmdr__ufnvs, i)
        else:
            vqmdr__ufnvs[i] = tbpk__wnfs[hlcwh__ysr[i]]
    return vqmdr__ufnvs


@register_jitable
def str_slice(arr, start, stop, step):
    hur__vbsp = arr._data
    uwpd__ikr = len(hur__vbsp)
    opv__gnkp = bodo.libs.str_arr_ext.pre_alloc_string_array(uwpd__ikr, -1)
    for i in range(uwpd__ikr):
        if bodo.libs.array_kernels.isna(hur__vbsp, i):
            bodo.libs.array_kernels.setna(opv__gnkp, i)
            continue
        opv__gnkp[i] = hur__vbsp[i][start:stop:step]
    return init_dict_arr(opv__gnkp, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    hur__vbsp = arr._data
    hlcwh__ysr = arr._indices
    uwpd__ikr = len(hur__vbsp)
    wwc__gjki = len(hlcwh__ysr)
    opv__gnkp = pre_alloc_string_array(uwpd__ikr, -1)
    zwjsx__grb = pre_alloc_string_array(wwc__gjki, -1)
    for qbpte__ybvhc in range(uwpd__ikr):
        if bodo.libs.array_kernels.isna(hur__vbsp, qbpte__ybvhc) or not -len(
            hur__vbsp[qbpte__ybvhc]) <= i < len(hur__vbsp[qbpte__ybvhc]):
            bodo.libs.array_kernels.setna(opv__gnkp, qbpte__ybvhc)
            continue
        opv__gnkp[qbpte__ybvhc] = hur__vbsp[qbpte__ybvhc][i]
    for qbpte__ybvhc in range(wwc__gjki):
        if bodo.libs.array_kernels.isna(hlcwh__ysr, qbpte__ybvhc
            ) or bodo.libs.array_kernels.isna(opv__gnkp, hlcwh__ysr[
            qbpte__ybvhc]):
            bodo.libs.array_kernels.setna(zwjsx__grb, qbpte__ybvhc)
            continue
        zwjsx__grb[qbpte__ybvhc] = opv__gnkp[hlcwh__ysr[qbpte__ybvhc]]
    return zwjsx__grb


@register_jitable
def str_repeat_int(arr, repeats):
    hur__vbsp = arr._data
    uwpd__ikr = len(hur__vbsp)
    opv__gnkp = pre_alloc_string_array(uwpd__ikr, -1)
    for i in range(uwpd__ikr):
        if bodo.libs.array_kernels.isna(hur__vbsp, i):
            bodo.libs.array_kernels.setna(opv__gnkp, i)
            continue
        opv__gnkp[i] = hur__vbsp[i] * repeats
    return init_dict_arr(opv__gnkp, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    troy__mdf = f"""def str_{func_name}(arr):
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
    iave__myyqz = {}
    exec(troy__mdf, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, iave__myyqz)
    return iave__myyqz[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        xgeoh__sffjc = create_str2bool_methods(func_name)
        xgeoh__sffjc = register_jitable(xgeoh__sffjc)
        globals()[f'str_{func_name}'] = xgeoh__sffjc


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    hur__vbsp = arr._data
    hlcwh__ysr = arr._indices
    uwpd__ikr = len(hur__vbsp)
    wwc__gjki = len(hlcwh__ysr)
    regex = re.compile(pat, flags=flags)
    ikw__bix = []
    for gwbll__lre in range(n_cols):
        ikw__bix.append(pre_alloc_string_array(uwpd__ikr, -1))
    icb__gjwgs = bodo.libs.bool_arr_ext.alloc_bool_array(uwpd__ikr)
    tlcox__lqo = hlcwh__ysr.copy()
    for i in range(uwpd__ikr):
        if bodo.libs.array_kernels.isna(hur__vbsp, i):
            icb__gjwgs[i] = True
            for qbpte__ybvhc in range(n_cols):
                bodo.libs.array_kernels.setna(ikw__bix[qbpte__ybvhc], i)
            continue
        fse__dcjjl = regex.search(hur__vbsp[i])
        if fse__dcjjl:
            icb__gjwgs[i] = False
            eayg__nhu = fse__dcjjl.groups()
            for qbpte__ybvhc in range(n_cols):
                ikw__bix[qbpte__ybvhc][i] = eayg__nhu[qbpte__ybvhc]
        else:
            icb__gjwgs[i] = True
            for qbpte__ybvhc in range(n_cols):
                bodo.libs.array_kernels.setna(ikw__bix[qbpte__ybvhc], i)
    for i in range(wwc__gjki):
        if icb__gjwgs[tlcox__lqo[i]]:
            bodo.libs.array_kernels.setna(tlcox__lqo, i)
    jyx__ootq = [init_dict_arr(ikw__bix[i], tlcox__lqo.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return jyx__ootq


def create_extractall_methods(is_multi_group):
    zclql__muxz = '_multi' if is_multi_group else ''
    troy__mdf = f"""def str_extractall{zclql__muxz}(arr, regex, n_cols, index_arr):
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
    iave__myyqz = {}
    exec(troy__mdf, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, iave__myyqz)
    return iave__myyqz[f'str_extractall{zclql__muxz}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        zclql__muxz = '_multi' if is_multi_group else ''
        xgeoh__sffjc = create_extractall_methods(is_multi_group)
        xgeoh__sffjc = register_jitable(xgeoh__sffjc)
        globals()[f'str_extractall{zclql__muxz}'] = xgeoh__sffjc


_register_extractall_methods()
