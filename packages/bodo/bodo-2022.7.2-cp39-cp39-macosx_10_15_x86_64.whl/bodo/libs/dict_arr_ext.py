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
        wxk__rtva = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, wxk__rtva)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        boilx__cmmjt, xbz__fbmi, fnay__jdni = args
        thm__dxvg = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        thm__dxvg.data = boilx__cmmjt
        thm__dxvg.indices = xbz__fbmi
        thm__dxvg.has_global_dictionary = fnay__jdni
        context.nrt.incref(builder, signature.args[0], boilx__cmmjt)
        context.nrt.incref(builder, signature.args[1], xbz__fbmi)
        return thm__dxvg._getvalue()
    qcw__oxcz = DictionaryArrayType(data_t)
    ietnp__kyvrl = qcw__oxcz(data_t, indices_t, types.bool_)
    return ietnp__kyvrl, codegen


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
        iaj__cmns = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(iaj__cmns, [val])
        c.pyapi.decref(iaj__cmns)
    thm__dxvg = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    frb__qvamw = c.pyapi.object_getattr_string(val, 'dictionary')
    yebhu__xogz = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    rkiek__fsun = c.pyapi.call_method(frb__qvamw, 'to_numpy', (yebhu__xogz,))
    thm__dxvg.data = c.unbox(typ.data, rkiek__fsun).value
    nkcbs__dlbv = c.pyapi.object_getattr_string(val, 'indices')
    hovi__bpyx = c.context.insert_const_string(c.builder.module, 'pandas')
    zhrt__gtw = c.pyapi.import_module_noblock(hovi__bpyx)
    jdhzj__rxr = c.pyapi.string_from_constant_string('Int32')
    vte__qdfk = c.pyapi.call_method(zhrt__gtw, 'array', (nkcbs__dlbv,
        jdhzj__rxr))
    thm__dxvg.indices = c.unbox(dict_indices_arr_type, vte__qdfk).value
    thm__dxvg.has_global_dictionary = c.context.get_constant(types.bool_, False
        )
    c.pyapi.decref(frb__qvamw)
    c.pyapi.decref(yebhu__xogz)
    c.pyapi.decref(rkiek__fsun)
    c.pyapi.decref(nkcbs__dlbv)
    c.pyapi.decref(zhrt__gtw)
    c.pyapi.decref(jdhzj__rxr)
    c.pyapi.decref(vte__qdfk)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    jcqj__mzy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(thm__dxvg._getvalue(), is_error=jcqj__mzy)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    thm__dxvg = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, thm__dxvg.data)
        osqy__bwdax = c.box(typ.data, thm__dxvg.data)
        gnh__acd = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, thm__dxvg.indices)
        csm__jjq = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        dvn__kpd = cgutils.get_or_insert_function(c.builder.module,
            csm__jjq, name='box_dict_str_array')
        tsf__dmmi = cgutils.create_struct_proxy(types.Array(types.int32, 1,
            'C'))(c.context, c.builder, gnh__acd.data)
        vgy__zzq = c.builder.extract_value(tsf__dmmi.shape, 0)
        mgsg__nehl = tsf__dmmi.data
        mku__rggto = cgutils.create_struct_proxy(types.Array(types.int8, 1,
            'C'))(c.context, c.builder, gnh__acd.null_bitmap).data
        rkiek__fsun = c.builder.call(dvn__kpd, [vgy__zzq, osqy__bwdax,
            mgsg__nehl, mku__rggto])
        c.pyapi.decref(osqy__bwdax)
    else:
        hovi__bpyx = c.context.insert_const_string(c.builder.module, 'pyarrow')
        xpgv__yqyht = c.pyapi.import_module_noblock(hovi__bpyx)
        nyyg__yjqo = c.pyapi.object_getattr_string(xpgv__yqyht,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, thm__dxvg.data)
        osqy__bwdax = c.box(typ.data, thm__dxvg.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, thm__dxvg.
            indices)
        nkcbs__dlbv = c.box(dict_indices_arr_type, thm__dxvg.indices)
        kymv__vwa = c.pyapi.call_method(nyyg__yjqo, 'from_arrays', (
            nkcbs__dlbv, osqy__bwdax))
        yebhu__xogz = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        rkiek__fsun = c.pyapi.call_method(kymv__vwa, 'to_numpy', (yebhu__xogz,)
            )
        c.pyapi.decref(xpgv__yqyht)
        c.pyapi.decref(osqy__bwdax)
        c.pyapi.decref(nkcbs__dlbv)
        c.pyapi.decref(nyyg__yjqo)
        c.pyapi.decref(kymv__vwa)
        c.pyapi.decref(yebhu__xogz)
    c.context.nrt.decref(c.builder, typ, val)
    return rkiek__fsun


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
    rump__ohfl = pyval.dictionary.to_numpy(False)
    msbou__zbb = pd.array(pyval.indices, 'Int32')
    rump__ohfl = context.get_constant_generic(builder, typ.data, rump__ohfl)
    msbou__zbb = context.get_constant_generic(builder,
        dict_indices_arr_type, msbou__zbb)
    edrqg__izxrw = context.get_constant(types.bool_, False)
    kgcp__aybiu = lir.Constant.literal_struct([rump__ohfl, msbou__zbb,
        edrqg__izxrw])
    return kgcp__aybiu


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            fycn__ijiqv = A._indices[ind]
            return A._data[fycn__ijiqv]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        boilx__cmmjt = A._data
        xbz__fbmi = A._indices
        vgy__zzq = len(xbz__fbmi)
        atp__vpxi = [get_str_arr_item_length(boilx__cmmjt, i) for i in
            range(len(boilx__cmmjt))]
        rgh__jcwv = 0
        for i in range(vgy__zzq):
            if not bodo.libs.array_kernels.isna(xbz__fbmi, i):
                rgh__jcwv += atp__vpxi[xbz__fbmi[i]]
        jxwz__xry = pre_alloc_string_array(vgy__zzq, rgh__jcwv)
        for i in range(vgy__zzq):
            if bodo.libs.array_kernels.isna(xbz__fbmi, i):
                bodo.libs.array_kernels.setna(jxwz__xry, i)
                continue
            ind = xbz__fbmi[i]
            if bodo.libs.array_kernels.isna(boilx__cmmjt, ind):
                bodo.libs.array_kernels.setna(jxwz__xry, i)
                continue
            jxwz__xry[i] = boilx__cmmjt[ind]
        return jxwz__xry
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    fycn__ijiqv = -1
    boilx__cmmjt = arr._data
    for i in range(len(boilx__cmmjt)):
        if bodo.libs.array_kernels.isna(boilx__cmmjt, i):
            continue
        if boilx__cmmjt[i] == val:
            fycn__ijiqv = i
            break
    return fycn__ijiqv


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    vgy__zzq = len(arr)
    fycn__ijiqv = find_dict_ind(arr, val)
    if fycn__ijiqv == -1:
        return init_bool_array(np.full(vgy__zzq, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == fycn__ijiqv


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    vgy__zzq = len(arr)
    fycn__ijiqv = find_dict_ind(arr, val)
    if fycn__ijiqv == -1:
        return init_bool_array(np.full(vgy__zzq, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != fycn__ijiqv


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
        pbemo__nryuf = arr._data
        sbz__yajfq = bodo.libs.int_arr_ext.alloc_int_array(len(pbemo__nryuf
            ), dtype)
        for bewxz__kryq in range(len(pbemo__nryuf)):
            if bodo.libs.array_kernels.isna(pbemo__nryuf, bewxz__kryq):
                bodo.libs.array_kernels.setna(sbz__yajfq, bewxz__kryq)
                continue
            sbz__yajfq[bewxz__kryq] = np.int64(pbemo__nryuf[bewxz__kryq])
        vgy__zzq = len(arr)
        xbz__fbmi = arr._indices
        jxwz__xry = bodo.libs.int_arr_ext.alloc_int_array(vgy__zzq, dtype)
        for i in range(vgy__zzq):
            if bodo.libs.array_kernels.isna(xbz__fbmi, i):
                bodo.libs.array_kernels.setna(jxwz__xry, i)
                continue
            jxwz__xry[i] = sbz__yajfq[xbz__fbmi[i]]
        return jxwz__xry
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    mjgx__wqy = len(arrs)
    coa__hee = 'def impl(arrs, sep):\n'
    coa__hee += '  ind_map = {}\n'
    coa__hee += '  out_strs = []\n'
    coa__hee += '  n = len(arrs[0])\n'
    for i in range(mjgx__wqy):
        coa__hee += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(mjgx__wqy):
        coa__hee += f'  data{i} = arrs[{i}]._data\n'
    coa__hee += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    coa__hee += '  for i in range(n):\n'
    vuhuq__oves = ' or '.join([
        f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for i in range(
        mjgx__wqy)])
    coa__hee += f'    if {vuhuq__oves}:\n'
    coa__hee += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    coa__hee += '      continue\n'
    for i in range(mjgx__wqy):
        coa__hee += f'    ind{i} = indices{i}[i]\n'
    yoql__qrl = '(' + ', '.join(f'ind{i}' for i in range(mjgx__wqy)) + ')'
    coa__hee += f'    if {yoql__qrl} not in ind_map:\n'
    coa__hee += '      out_ind = len(out_strs)\n'
    coa__hee += f'      ind_map[{yoql__qrl}] = out_ind\n'
    jpvws__qoj = "''" if is_overload_none(sep) else 'sep'
    teqb__qpbk = ', '.join([f'data{i}[ind{i}]' for i in range(mjgx__wqy)])
    coa__hee += f'      v = {jpvws__qoj}.join([{teqb__qpbk}])\n'
    coa__hee += '      out_strs.append(v)\n'
    coa__hee += '    else:\n'
    coa__hee += f'      out_ind = ind_map[{yoql__qrl}]\n'
    coa__hee += '    out_indices[i] = out_ind\n'
    coa__hee += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    coa__hee += (
        '  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)\n'
        )
    enwa__zjc = {}
    exec(coa__hee, {'bodo': bodo, 'numba': numba, 'np': np}, enwa__zjc)
    impl = enwa__zjc['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    icqc__rdzu = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    ietnp__kyvrl = toty(fromty)
    tqiy__dtp = context.compile_internal(builder, icqc__rdzu, ietnp__kyvrl,
        (val,))
    return impl_ret_new_ref(context, builder, toty, tqiy__dtp)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    rump__ohfl = arr._data
    yvhr__axb = len(rump__ohfl)
    oiyf__oatx = pre_alloc_string_array(yvhr__axb, -1)
    if regex:
        onpa__schmm = re.compile(pat, flags)
        for i in range(yvhr__axb):
            if bodo.libs.array_kernels.isna(rump__ohfl, i):
                bodo.libs.array_kernels.setna(oiyf__oatx, i)
                continue
            oiyf__oatx[i] = onpa__schmm.sub(repl=repl, string=rump__ohfl[i])
    else:
        for i in range(yvhr__axb):
            if bodo.libs.array_kernels.isna(rump__ohfl, i):
                bodo.libs.array_kernels.setna(oiyf__oatx, i)
                continue
            oiyf__oatx[i] = rump__ohfl[i].replace(pat, repl)
    return init_dict_arr(oiyf__oatx, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    thm__dxvg = arr._data
    gqy__iojen = len(thm__dxvg)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gqy__iojen)
    for i in range(gqy__iojen):
        dict_arr_out[i] = thm__dxvg[i].startswith(pat)
    msbou__zbb = arr._indices
    ikazw__rpcjw = len(msbou__zbb)
    jxwz__xry = bodo.libs.bool_arr_ext.alloc_bool_array(ikazw__rpcjw)
    for i in range(ikazw__rpcjw):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jxwz__xry, i)
        else:
            jxwz__xry[i] = dict_arr_out[msbou__zbb[i]]
    return jxwz__xry


@register_jitable
def str_endswith(arr, pat, na):
    thm__dxvg = arr._data
    gqy__iojen = len(thm__dxvg)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gqy__iojen)
    for i in range(gqy__iojen):
        dict_arr_out[i] = thm__dxvg[i].endswith(pat)
    msbou__zbb = arr._indices
    ikazw__rpcjw = len(msbou__zbb)
    jxwz__xry = bodo.libs.bool_arr_ext.alloc_bool_array(ikazw__rpcjw)
    for i in range(ikazw__rpcjw):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jxwz__xry, i)
        else:
            jxwz__xry[i] = dict_arr_out[msbou__zbb[i]]
    return jxwz__xry


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    thm__dxvg = arr._data
    tsss__uls = pd.Series(thm__dxvg)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = tsss__uls.array._str_contains(pat, case, flags, na,
            regex)
    msbou__zbb = arr._indices
    ikazw__rpcjw = len(msbou__zbb)
    jxwz__xry = bodo.libs.bool_arr_ext.alloc_bool_array(ikazw__rpcjw)
    for i in range(ikazw__rpcjw):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jxwz__xry, i)
        else:
            jxwz__xry[i] = dict_arr_out[msbou__zbb[i]]
    return jxwz__xry


@register_jitable
def str_contains_non_regex(arr, pat, case):
    thm__dxvg = arr._data
    gqy__iojen = len(thm__dxvg)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(gqy__iojen)
    if not case:
        anhy__urmu = pat.upper()
    for i in range(gqy__iojen):
        if case:
            dict_arr_out[i] = pat in thm__dxvg[i]
        else:
            dict_arr_out[i] = anhy__urmu in thm__dxvg[i].upper()
    msbou__zbb = arr._indices
    ikazw__rpcjw = len(msbou__zbb)
    jxwz__xry = bodo.libs.bool_arr_ext.alloc_bool_array(ikazw__rpcjw)
    for i in range(ikazw__rpcjw):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jxwz__xry, i)
        else:
            jxwz__xry[i] = dict_arr_out[msbou__zbb[i]]
    return jxwz__xry


@numba.njit
def str_match(arr, pat, case, flags, na):
    thm__dxvg = arr._data
    msbou__zbb = arr._indices
    ikazw__rpcjw = len(msbou__zbb)
    jxwz__xry = bodo.libs.bool_arr_ext.alloc_bool_array(ikazw__rpcjw)
    tsss__uls = pd.Series(thm__dxvg)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = tsss__uls.array._str_match(pat, case, flags, na)
    for i in range(ikazw__rpcjw):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jxwz__xry, i)
        else:
            jxwz__xry[i] = dict_arr_out[msbou__zbb[i]]
    return jxwz__xry


def create_simple_str2str_methods(func_name, func_args):
    coa__hee = f"""def str_{func_name}({', '.join(func_args)}):
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
    enwa__zjc = {}
    exec(coa__hee, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, enwa__zjc)
    return enwa__zjc[f'str_{func_name}']


def _register_simple_str2str_methods():
    ikn__cnjc = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in ikn__cnjc.keys():
        lpus__wav = create_simple_str2str_methods(func_name, ikn__cnjc[
            func_name])
        lpus__wav = register_jitable(lpus__wav)
        globals()[f'str_{func_name}'] = lpus__wav


_register_simple_str2str_methods()


def create_find_methods(func_name):
    coa__hee = f"""def str_{func_name}(arr, sub, start, end):
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
    enwa__zjc = {}
    exec(coa__hee, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, enwa__zjc)
    return enwa__zjc[f'str_{func_name}']


def _register_find_methods():
    shz__gjrw = ['find', 'rfind']
    for func_name in shz__gjrw:
        lpus__wav = create_find_methods(func_name)
        lpus__wav = register_jitable(lpus__wav)
        globals()[f'str_{func_name}'] = lpus__wav


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    rump__ohfl = arr._data
    msbou__zbb = arr._indices
    yvhr__axb = len(rump__ohfl)
    ikazw__rpcjw = len(msbou__zbb)
    xul__pbj = bodo.libs.int_arr_ext.alloc_int_array(yvhr__axb, np.int64)
    dqjg__vlpc = bodo.libs.int_arr_ext.alloc_int_array(ikazw__rpcjw, np.int64)
    regex = re.compile(pat, flags)
    for i in range(yvhr__axb):
        if bodo.libs.array_kernels.isna(rump__ohfl, i):
            bodo.libs.array_kernels.setna(xul__pbj, i)
            continue
        xul__pbj[i] = bodo.libs.str_ext.str_findall_count(regex, rump__ohfl[i])
    for i in range(ikazw__rpcjw):
        if bodo.libs.array_kernels.isna(msbou__zbb, i
            ) or bodo.libs.array_kernels.isna(xul__pbj, msbou__zbb[i]):
            bodo.libs.array_kernels.setna(dqjg__vlpc, i)
        else:
            dqjg__vlpc[i] = xul__pbj[msbou__zbb[i]]
    return dqjg__vlpc


@register_jitable
def str_len(arr):
    rump__ohfl = arr._data
    msbou__zbb = arr._indices
    ikazw__rpcjw = len(msbou__zbb)
    xul__pbj = bodo.libs.array_kernels.get_arr_lens(rump__ohfl, False)
    dqjg__vlpc = bodo.libs.int_arr_ext.alloc_int_array(ikazw__rpcjw, np.int64)
    for i in range(ikazw__rpcjw):
        if bodo.libs.array_kernels.isna(msbou__zbb, i
            ) or bodo.libs.array_kernels.isna(xul__pbj, msbou__zbb[i]):
            bodo.libs.array_kernels.setna(dqjg__vlpc, i)
        else:
            dqjg__vlpc[i] = xul__pbj[msbou__zbb[i]]
    return dqjg__vlpc


@register_jitable
def str_slice(arr, start, stop, step):
    rump__ohfl = arr._data
    yvhr__axb = len(rump__ohfl)
    oiyf__oatx = bodo.libs.str_arr_ext.pre_alloc_string_array(yvhr__axb, -1)
    for i in range(yvhr__axb):
        if bodo.libs.array_kernels.isna(rump__ohfl, i):
            bodo.libs.array_kernels.setna(oiyf__oatx, i)
            continue
        oiyf__oatx[i] = rump__ohfl[i][start:stop:step]
    return init_dict_arr(oiyf__oatx, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    rump__ohfl = arr._data
    msbou__zbb = arr._indices
    yvhr__axb = len(rump__ohfl)
    ikazw__rpcjw = len(msbou__zbb)
    oiyf__oatx = pre_alloc_string_array(yvhr__axb, -1)
    jxwz__xry = pre_alloc_string_array(ikazw__rpcjw, -1)
    for bewxz__kryq in range(yvhr__axb):
        if bodo.libs.array_kernels.isna(rump__ohfl, bewxz__kryq) or not -len(
            rump__ohfl[bewxz__kryq]) <= i < len(rump__ohfl[bewxz__kryq]):
            bodo.libs.array_kernels.setna(oiyf__oatx, bewxz__kryq)
            continue
        oiyf__oatx[bewxz__kryq] = rump__ohfl[bewxz__kryq][i]
    for bewxz__kryq in range(ikazw__rpcjw):
        if bodo.libs.array_kernels.isna(msbou__zbb, bewxz__kryq
            ) or bodo.libs.array_kernels.isna(oiyf__oatx, msbou__zbb[
            bewxz__kryq]):
            bodo.libs.array_kernels.setna(jxwz__xry, bewxz__kryq)
            continue
        jxwz__xry[bewxz__kryq] = oiyf__oatx[msbou__zbb[bewxz__kryq]]
    return jxwz__xry


@register_jitable
def str_repeat_int(arr, repeats):
    rump__ohfl = arr._data
    yvhr__axb = len(rump__ohfl)
    oiyf__oatx = pre_alloc_string_array(yvhr__axb, -1)
    for i in range(yvhr__axb):
        if bodo.libs.array_kernels.isna(rump__ohfl, i):
            bodo.libs.array_kernels.setna(oiyf__oatx, i)
            continue
        oiyf__oatx[i] = rump__ohfl[i] * repeats
    return init_dict_arr(oiyf__oatx, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    coa__hee = f"""def str_{func_name}(arr):
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
    enwa__zjc = {}
    exec(coa__hee, {'bodo': bodo, 'numba': numba, 'np': np, 'init_dict_arr':
        init_dict_arr}, enwa__zjc)
    return enwa__zjc[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        lpus__wav = create_str2bool_methods(func_name)
        lpus__wav = register_jitable(lpus__wav)
        globals()[f'str_{func_name}'] = lpus__wav


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    rump__ohfl = arr._data
    msbou__zbb = arr._indices
    yvhr__axb = len(rump__ohfl)
    ikazw__rpcjw = len(msbou__zbb)
    regex = re.compile(pat, flags=flags)
    tpcn__cjbb = []
    for rgty__bsw in range(n_cols):
        tpcn__cjbb.append(pre_alloc_string_array(yvhr__axb, -1))
    uukfb__che = bodo.libs.bool_arr_ext.alloc_bool_array(yvhr__axb)
    poq__qcs = msbou__zbb.copy()
    for i in range(yvhr__axb):
        if bodo.libs.array_kernels.isna(rump__ohfl, i):
            uukfb__che[i] = True
            for bewxz__kryq in range(n_cols):
                bodo.libs.array_kernels.setna(tpcn__cjbb[bewxz__kryq], i)
            continue
        lsekt__zekdv = regex.search(rump__ohfl[i])
        if lsekt__zekdv:
            uukfb__che[i] = False
            frsw__krz = lsekt__zekdv.groups()
            for bewxz__kryq in range(n_cols):
                tpcn__cjbb[bewxz__kryq][i] = frsw__krz[bewxz__kryq]
        else:
            uukfb__che[i] = True
            for bewxz__kryq in range(n_cols):
                bodo.libs.array_kernels.setna(tpcn__cjbb[bewxz__kryq], i)
    for i in range(ikazw__rpcjw):
        if uukfb__che[poq__qcs[i]]:
            bodo.libs.array_kernels.setna(poq__qcs, i)
    hmx__zzfoo = [init_dict_arr(tpcn__cjbb[i], poq__qcs.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return hmx__zzfoo


def create_extractall_methods(is_multi_group):
    davxr__jzlyy = '_multi' if is_multi_group else ''
    coa__hee = f"""def str_extractall{davxr__jzlyy}(arr, regex, n_cols, index_arr):
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
    enwa__zjc = {}
    exec(coa__hee, {'bodo': bodo, 'numba': numba, 'np': np, 'init_dict_arr':
        init_dict_arr, 'pre_alloc_string_array': pre_alloc_string_array},
        enwa__zjc)
    return enwa__zjc[f'str_extractall{davxr__jzlyy}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        davxr__jzlyy = '_multi' if is_multi_group else ''
        lpus__wav = create_extractall_methods(is_multi_group)
        lpus__wav = register_jitable(lpus__wav)
        globals()[f'str_extractall{davxr__jzlyy}'] = lpus__wav


_register_extractall_methods()
