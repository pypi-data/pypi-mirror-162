"""
Support for Series.str methods
"""
import operator
import re
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import StringIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.split_impl import get_split_view_data_ptr, get_split_view_index, string_array_split_view_type
from bodo.libs.array import get_search_regex
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.str_arr_ext import get_utf8_size, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import str_findall_count
from bodo.utils.typing import BodoError, create_unsupported_overload, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_str_len, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error


class SeriesStrMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        kqnjj__bpll = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(kqnjj__bpll)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zwkn__dgvz = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, zwkn__dgvz)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        psijj__kog, = args
        fdp__bkgx = signature.return_type
        ugc__vrdi = cgutils.create_struct_proxy(fdp__bkgx)(context, builder)
        ugc__vrdi.obj = psijj__kog
        context.nrt.incref(builder, signature.args[0], psijj__kog)
        return ugc__vrdi._getvalue()
    return SeriesStrMethodType(obj)(obj), codegen


def str_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.UnicodeType) and not is_overload_constant_str(
        arg):
        raise_bodo_error(
            "Series.str.{}(): parameter '{}' expected a string object, not {}"
            .format(func_name, arg_name, arg))


def int_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.Integer) and not is_overload_constant_int(arg
        ):
        raise BodoError(
            "Series.str.{}(): parameter '{}' expected an int object, not {}"
            .format(func_name, arg_name, arg))


def not_supported_arg_check(func_name, arg_name, arg, defval):
    if arg_name == 'na':
        if not isinstance(arg, types.Omitted) and (not isinstance(arg,
            float) or not np.isnan(arg)):
            raise BodoError(
                "Series.str.{}(): parameter '{}' is not supported, default: np.nan"
                .format(func_name, arg_name))
    elif not isinstance(arg, types.Omitted) and arg != defval:
        raise BodoError(
            "Series.str.{}(): parameter '{}' is not supported, default: {}"
            .format(func_name, arg_name, defval))


def common_validate_padding(func_name, width, fillchar):
    if is_overload_constant_str(fillchar):
        if get_overload_const_str_len(fillchar) != 1:
            raise BodoError(
                'Series.str.{}(): fillchar must be a character, not str'.
                format(func_name))
    elif not isinstance(fillchar, types.UnicodeType):
        raise BodoError('Series.str.{}(): fillchar must be a character, not {}'
            .format(func_name, fillchar))
    int_arg_check(func_name, 'width', width)


@overload_attribute(SeriesType, 'str')
def overload_series_str(S):
    if not (is_str_arr_type(S.data) or S.data ==
        string_array_split_view_type or isinstance(S.data, ArrayItemArrayType)
        ):
        raise_bodo_error(
            'Series.str: input should be a series of string or arrays')
    return lambda S: bodo.hiframes.series_str_impl.init_series_str_method(S)


@overload_method(SeriesStrMethodType, 'len', inline='always', no_unliteral=True
    )
def overload_str_method_len(S_str):
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_len_dict_impl(S_str):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(vieu__qrbu)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(vieu__qrbu, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'split', inline='always',
    no_unliteral=True)
def overload_str_method_split(S_str, pat=None, n=-1, expand=False):
    if not is_overload_none(pat):
        str_arg_check('split', 'pat', pat)
    int_arg_check('split', 'n', n)
    not_supported_arg_check('split', 'expand', expand, False)
    if is_overload_constant_str(pat) and len(get_overload_const_str(pat)
        ) == 1 and get_overload_const_str(pat).isascii(
        ) and is_overload_constant_int(n) and get_overload_const_int(n
        ) == -1 and S_str.stype.data == string_array_type:

        def _str_split_view_impl(S_str, pat=None, n=-1, expand=False):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(vieu__qrbu,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(vieu__qrbu, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    lji__byrbm = S_str.stype.data
    if (lji__byrbm != string_array_split_view_type and not is_str_arr_type(
        lji__byrbm)) and not isinstance(lji__byrbm, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(lji__byrbm, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(vieu__qrbu, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_get_array_impl
    if lji__byrbm == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(vieu__qrbu)
            vhg__tmge = 0
            for tibq__bghu in numba.parfors.parfor.internal_prange(n):
                scac__thpyg, scac__thpyg, vjvk__ivlsb = get_split_view_index(
                    vieu__qrbu, tibq__bghu, i)
                vhg__tmge += vjvk__ivlsb
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, vhg__tmge)
            for ubld__zzmyw in numba.parfors.parfor.internal_prange(n):
                gjgw__gqrqi, mnpnk__mux, vjvk__ivlsb = get_split_view_index(
                    vieu__qrbu, ubld__zzmyw, i)
                if gjgw__gqrqi == 0:
                    bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
                    djszy__tja = get_split_view_data_ptr(vieu__qrbu, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        ubld__zzmyw)
                    djszy__tja = get_split_view_data_ptr(vieu__qrbu, mnpnk__mux
                        )
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    ubld__zzmyw, djszy__tja, vjvk__ivlsb)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(vieu__qrbu, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(vieu__qrbu)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for ubld__zzmyw in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(vieu__qrbu, ubld__zzmyw
                ) or not len(vieu__qrbu[ubld__zzmyw]) > i >= -len(vieu__qrbu
                [ubld__zzmyw]):
                out_arr[ubld__zzmyw] = ''
                bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
            else:
                out_arr[ubld__zzmyw] = vieu__qrbu[ubld__zzmyw][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    lji__byrbm = S_str.stype.data
    if (lji__byrbm != string_array_split_view_type and lji__byrbm !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        lji__byrbm)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(rpvij__wbhpg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for ubld__zzmyw in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, ubld__zzmyw):
                out_arr[ubld__zzmyw] = ''
                bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
            else:
                dhbz__ezah = rpvij__wbhpg[ubld__zzmyw]
                out_arr[ubld__zzmyw] = sep.join(dhbz__ezah)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'replace', inline='always',
    no_unliteral=True)
def overload_str_method_replace(S_str, pat, repl, n=-1, case=None, flags=0,
    regex=True):
    not_supported_arg_check('replace', 'n', n, -1)
    not_supported_arg_check('replace', 'case', case, None)
    str_arg_check('replace', 'pat', pat)
    str_arg_check('replace', 'repl', repl)
    int_arg_check('replace', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_replace_dict_impl(S_str, pat, repl, n=-1, case=None, flags
            =0, regex=True):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(vieu__qrbu, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            qpdb__gxip = re.compile(pat, flags)
            tzaq__iowq = len(vieu__qrbu)
            out_arr = pre_alloc_string_array(tzaq__iowq, -1)
            for ubld__zzmyw in numba.parfors.parfor.internal_prange(tzaq__iowq
                ):
                if bodo.libs.array_kernels.isna(vieu__qrbu, ubld__zzmyw):
                    out_arr[ubld__zzmyw] = ''
                    bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
                    continue
                out_arr[ubld__zzmyw] = qpdb__gxip.sub(repl, vieu__qrbu[
                    ubld__zzmyw])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(vieu__qrbu)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(tzaq__iowq, -1)
        for ubld__zzmyw in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(vieu__qrbu, ubld__zzmyw):
                out_arr[ubld__zzmyw] = ''
                bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
                continue
            out_arr[ubld__zzmyw] = vieu__qrbu[ubld__zzmyw].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return _str_replace_noregex_impl


@numba.njit
def series_contains_regex(S, pat, case, flags, na, regex):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_contains(pat, case, flags, na, regex)
    return out_arr


@numba.njit
def series_match_regex(S, pat, case, flags, na):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_match(pat, case, flags, na)
    return out_arr


def is_regex_unsupported(pat):
    ybf__cvail = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(dqtsc__mlk in pat) for dqtsc__mlk in ybf__cvail])
    else:
        return True


@overload_method(SeriesStrMethodType, 'contains', no_unliteral=True)
def overload_str_method_contains(S_str, pat, case=True, flags=0, na=np.nan,
    regex=True):
    not_supported_arg_check('contains', 'na', na, np.nan)
    str_arg_check('contains', 'pat', pat)
    int_arg_check('contains', 'flags', flags)
    if not is_overload_constant_bool(regex):
        raise BodoError(
            "Series.str.contains(): 'regex' argument should be a constant boolean"
            )
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.contains(): 'case' argument should be a constant boolean"
            )
    pbip__qlo = re.IGNORECASE.value
    tooyv__dfdtj = 'def impl(\n'
    tooyv__dfdtj += (
        '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n')
    tooyv__dfdtj += '):\n'
    tooyv__dfdtj += '  S = S_str._obj\n'
    tooyv__dfdtj += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    tooyv__dfdtj += (
        '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tooyv__dfdtj += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    tooyv__dfdtj += '  l = len(arr)\n'
    tooyv__dfdtj += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                tooyv__dfdtj += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                tooyv__dfdtj += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            tooyv__dfdtj += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        tooyv__dfdtj += """  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)
"""
    else:
        tooyv__dfdtj += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            tooyv__dfdtj += '  upper_pat = pat.upper()\n'
        tooyv__dfdtj += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        tooyv__dfdtj += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        tooyv__dfdtj += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        tooyv__dfdtj += '      else: \n'
        if is_overload_true(case):
            tooyv__dfdtj += '          out_arr[i] = pat in arr[i]\n'
        else:
            tooyv__dfdtj += (
                '          out_arr[i] = upper_pat in arr[i].upper()\n')
    tooyv__dfdtj += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    fyw__jnxtx = {}
    exec(tooyv__dfdtj, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': pbip__qlo, 'get_search_regex':
        get_search_regex}, fyw__jnxtx)
    impl = fyw__jnxtx['impl']
    return impl


@overload_method(SeriesStrMethodType, 'match', inline='always',
    no_unliteral=True)
def overload_str_method_match(S_str, pat, case=True, flags=0, na=np.nan):
    not_supported_arg_check('match', 'na', na, np.nan)
    str_arg_check('match', 'pat', pat)
    int_arg_check('match', 'flags', flags)
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.match(): 'case' argument should be a constant boolean")
    pbip__qlo = re.IGNORECASE.value
    tooyv__dfdtj = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    tooyv__dfdtj += '        S = S_str._obj\n'
    tooyv__dfdtj += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    tooyv__dfdtj += '        l = len(arr)\n'
    tooyv__dfdtj += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tooyv__dfdtj += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        tooyv__dfdtj += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        tooyv__dfdtj += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        tooyv__dfdtj += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        tooyv__dfdtj += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    tooyv__dfdtj += """        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    fyw__jnxtx = {}
    exec(tooyv__dfdtj, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': pbip__qlo, 'get_search_regex':
        get_search_regex}, fyw__jnxtx)
    impl = fyw__jnxtx['impl']
    return impl


@overload_method(SeriesStrMethodType, 'cat', no_unliteral=True)
def overload_str_method_cat(S_str, others=None, sep=None, na_rep=None, join
    ='left'):
    if not isinstance(others, DataFrameType):
        raise_bodo_error(
            "Series.str.cat(): 'others' must be a DataFrame currently")
    if not is_overload_none(sep):
        str_arg_check('cat', 'sep', sep)
    if not is_overload_constant_str(join) or get_overload_const_str(join
        ) != 'left':
        raise_bodo_error("Series.str.cat(): 'join' not supported yet")
    tooyv__dfdtj = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    tooyv__dfdtj += '  S = S_str._obj\n'
    tooyv__dfdtj += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    tooyv__dfdtj += (
        '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tooyv__dfdtj += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    tooyv__dfdtj += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        tooyv__dfdtj += f"""  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})
"""
    if S_str.stype.data == bodo.dict_str_arr_type and all(lnoj__ktn == bodo
        .dict_str_arr_type for lnoj__ktn in others.data):
        hyarw__jnep = ', '.join(f'data{i}' for i in range(len(others.columns)))
        tooyv__dfdtj += f"""  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {hyarw__jnep}), sep)
"""
    else:
        wokp__zoitf = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        tooyv__dfdtj += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        tooyv__dfdtj += '  numba.parfors.parfor.init_prange()\n'
        tooyv__dfdtj += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        tooyv__dfdtj += f'      if {wokp__zoitf}:\n'
        tooyv__dfdtj += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        tooyv__dfdtj += '          continue\n'
        aisd__xxooc = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range(
            len(others.columns))])
        hvk__wzn = "''" if is_overload_none(sep) else 'sep'
        tooyv__dfdtj += (
            f'      out_arr[i] = {hvk__wzn}.join([{aisd__xxooc}])\n')
    tooyv__dfdtj += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    fyw__jnxtx = {}
    exec(tooyv__dfdtj, {'bodo': bodo, 'numba': numba}, fyw__jnxtx)
    impl = fyw__jnxtx['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(vieu__qrbu, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        qpdb__gxip = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(tzaq__iowq, np.int64)
        for i in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(qpdb__gxip, rpvij__wbhpg[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'find', inline='always', no_unliteral
    =True)
def overload_str_method_find(S_str, sub, start=0, end=None):
    str_arg_check('find', 'sub', sub)
    int_arg_check('find', 'start', start)
    if not is_overload_none(end):
        int_arg_check('find', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_find_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(vieu__qrbu, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(tzaq__iowq, np.int64)
        for i in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = rpvij__wbhpg[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'rfind', inline='always',
    no_unliteral=True)
def overload_str_method_rfind(S_str, sub, start=0, end=None):
    str_arg_check('rfind', 'sub', sub)
    if start != 0:
        int_arg_check('rfind', 'start', start)
    if not is_overload_none(end):
        int_arg_check('rfind', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_rfind_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(vieu__qrbu, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(tzaq__iowq, np.int64)
        for i in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = rpvij__wbhpg[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'slice_replace', inline='always',
    no_unliteral=True)
def overload_str_method_slice_replace(S_str, start=0, stop=None, repl=''):
    int_arg_check('slice_replace', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice_replace', 'stop', stop)
    str_arg_check('slice_replace', 'repl', repl)

    def impl(S_str, start=0, stop=None, repl=''):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(tzaq__iowq, -1)
        for ubld__zzmyw in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, ubld__zzmyw):
                bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
            else:
                if stop is not None:
                    ezzyd__dnjuy = rpvij__wbhpg[ubld__zzmyw][stop:]
                else:
                    ezzyd__dnjuy = ''
                out_arr[ubld__zzmyw] = rpvij__wbhpg[ubld__zzmyw][:start
                    ] + repl + ezzyd__dnjuy
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
                bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
                kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(vieu__qrbu,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    bfedg__juwd, kqnjj__bpll)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            tzaq__iowq = len(rpvij__wbhpg)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(tzaq__iowq,
                -1)
            for ubld__zzmyw in numba.parfors.parfor.internal_prange(tzaq__iowq
                ):
                if bodo.libs.array_kernels.isna(rpvij__wbhpg, ubld__zzmyw):
                    bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
                else:
                    out_arr[ubld__zzmyw] = rpvij__wbhpg[ubld__zzmyw] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return impl
    elif is_overload_constant_list(repeats):
        ggjz__lbgia = get_overload_const_list(repeats)
        onet__msdt = all([isinstance(rcp__dfnz, int) for rcp__dfnz in
            ggjz__lbgia])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        onet__msdt = True
    else:
        onet__msdt = False
    if onet__msdt:

        def impl(S_str, repeats):
            S = S_str._obj
            rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            sol__kva = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            tzaq__iowq = len(rpvij__wbhpg)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(tzaq__iowq,
                -1)
            for ubld__zzmyw in numba.parfors.parfor.internal_prange(tzaq__iowq
                ):
                if bodo.libs.array_kernels.isna(rpvij__wbhpg, ubld__zzmyw):
                    bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
                else:
                    out_arr[ubld__zzmyw] = rpvij__wbhpg[ubld__zzmyw
                        ] * sol__kva[ubld__zzmyw]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    tooyv__dfdtj = f"""def dict_impl(S_str, width, fillchar=' '):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr, width, fillchar)
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
def impl(S_str, width, fillchar=' '):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    numba.parfors.parfor.init_prange()
    l = len(str_arr)
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
    for j in numba.parfors.parfor.internal_prange(l):
        if bodo.libs.array_kernels.isna(str_arr, j):
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}(width, fillchar)
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    fyw__jnxtx = {}
    gan__nju = {'bodo': bodo, 'numba': numba}
    exec(tooyv__dfdtj, gan__nju, fyw__jnxtx)
    impl = fyw__jnxtx['impl']
    uxcpt__ezur = fyw__jnxtx['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return uxcpt__ezur
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for zpi__oddo in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(zpi__oddo)
        overload_method(SeriesStrMethodType, zpi__oddo, inline='always',
            no_unliteral=True)(impl)


_install_ljust_rjust_center()


@overload_method(SeriesStrMethodType, 'pad', no_unliteral=True)
def overload_str_method_pad(S_str, width, side='left', fillchar=' '):
    common_validate_padding('pad', width, fillchar)
    if is_overload_constant_str(side):
        if get_overload_const_str(side) not in ['left', 'right', 'both']:
            raise BodoError('Series.str.pad(): Invalid Side')
    else:
        raise BodoError('Series.str.pad(): Invalid Side')
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_pad_dict_impl(S_str, width, side='left', fillchar=' '):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(vieu__qrbu,
                    width, fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(vieu__qrbu,
                    width, fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(vieu__qrbu,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(tzaq__iowq, -1)
        for ubld__zzmyw in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, ubld__zzmyw):
                out_arr[ubld__zzmyw] = ''
                bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
            elif side == 'left':
                out_arr[ubld__zzmyw] = rpvij__wbhpg[ubld__zzmyw].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[ubld__zzmyw] = rpvij__wbhpg[ubld__zzmyw].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[ubld__zzmyw] = rpvij__wbhpg[ubld__zzmyw].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(vieu__qrbu, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(tzaq__iowq, -1)
        for ubld__zzmyw in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, ubld__zzmyw):
                out_arr[ubld__zzmyw] = ''
                bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
            else:
                out_arr[ubld__zzmyw] = rpvij__wbhpg[ubld__zzmyw].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'slice', no_unliteral=True)
def overload_str_method_slice(S_str, start=None, stop=None, step=None):
    if not is_overload_none(start):
        int_arg_check('slice', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice', 'stop', stop)
    if not is_overload_none(step):
        int_arg_check('slice', 'step', step)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_slice_dict_impl(S_str, start=None, stop=None, step=None):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(vieu__qrbu, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(tzaq__iowq, -1)
        for ubld__zzmyw in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, ubld__zzmyw):
                out_arr[ubld__zzmyw] = ''
                bodo.libs.array_kernels.setna(out_arr, ubld__zzmyw)
            else:
                out_arr[ubld__zzmyw] = rpvij__wbhpg[ubld__zzmyw][start:stop
                    :step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(vieu__qrbu, pat, na
                )
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(tzaq__iowq)
        for i in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = rpvij__wbhpg[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
            bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
            kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(vieu__qrbu, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bfedg__juwd, kqnjj__bpll)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        rpvij__wbhpg = bodo.hiframes.pd_series_ext.get_series_data(S)
        kqnjj__bpll = bodo.hiframes.pd_series_ext.get_series_name(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        tzaq__iowq = len(rpvij__wbhpg)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(tzaq__iowq)
        for i in numba.parfors.parfor.internal_prange(tzaq__iowq):
            if bodo.libs.array_kernels.isna(rpvij__wbhpg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = rpvij__wbhpg[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, bfedg__juwd,
            kqnjj__bpll)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_str_method_getitem(S_str, ind):
    if not isinstance(S_str, SeriesStrMethodType):
        return
    if not isinstance(types.unliteral(ind), (types.SliceType, types.Integer)):
        raise BodoError(
            'index input to Series.str[] should be a slice or an integer')
    if isinstance(ind, types.SliceType):
        return lambda S_str, ind: S_str.slice(ind.start, ind.stop, ind.step)
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda S_str, ind: S_str.get(ind)


@overload_method(SeriesStrMethodType, 'extract', inline='always',
    no_unliteral=True)
def overload_str_method_extract(S_str, pat, flags=0, expand=True):
    if not is_overload_constant_bool(expand):
        raise BodoError(
            "Series.str.extract(): 'expand' argument should be a constant bool"
            )
    udegx__girq, regex = _get_column_names_from_regex(pat, flags, 'extract')
    khuk__qbof = len(udegx__girq)
    if S_str.stype.data == bodo.dict_str_arr_type:
        tooyv__dfdtj = 'def impl(S_str, pat, flags=0, expand=True):\n'
        tooyv__dfdtj += '  S = S_str._obj\n'
        tooyv__dfdtj += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        tooyv__dfdtj += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tooyv__dfdtj += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tooyv__dfdtj += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {khuk__qbof})
"""
        for i in range(khuk__qbof):
            tooyv__dfdtj += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        tooyv__dfdtj = 'def impl(S_str, pat, flags=0, expand=True):\n'
        tooyv__dfdtj += '  regex = re.compile(pat, flags=flags)\n'
        tooyv__dfdtj += '  S = S_str._obj\n'
        tooyv__dfdtj += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        tooyv__dfdtj += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tooyv__dfdtj += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tooyv__dfdtj += '  numba.parfors.parfor.init_prange()\n'
        tooyv__dfdtj += '  n = len(str_arr)\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        tooyv__dfdtj += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        tooyv__dfdtj += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += "          out_arr_{}[j] = ''\n".format(i)
            tooyv__dfdtj += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        tooyv__dfdtj += '      else:\n'
        tooyv__dfdtj += '          m = regex.search(str_arr[j])\n'
        tooyv__dfdtj += '          if m:\n'
        tooyv__dfdtj += '            g = m.groups()\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        tooyv__dfdtj += '          else:\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += "            out_arr_{}[j] = ''\n".format(i)
            tooyv__dfdtj += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        kqnjj__bpll = "'{}'".format(list(regex.groupindex.keys()).pop()
            ) if len(regex.groupindex.keys()) > 0 else 'name'
        tooyv__dfdtj += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(kqnjj__bpll))
        fyw__jnxtx = {}
        exec(tooyv__dfdtj, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, fyw__jnxtx)
        impl = fyw__jnxtx['impl']
        return impl
    lnraq__ubc = ', '.join('out_arr_{}'.format(i) for i in range(khuk__qbof))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(tooyv__dfdtj,
        udegx__girq, lnraq__ubc, 'index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    udegx__girq, scac__thpyg = _get_column_names_from_regex(pat, flags,
        'extractall')
    khuk__qbof = len(udegx__girq)
    kfy__kqudf = isinstance(S_str.stype.index, StringIndexType)
    dwdpm__yceio = khuk__qbof > 1
    mdsf__wdc = '_multi' if dwdpm__yceio else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        tooyv__dfdtj = 'def impl(S_str, pat, flags=0):\n'
        tooyv__dfdtj += '  S = S_str._obj\n'
        tooyv__dfdtj += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        tooyv__dfdtj += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tooyv__dfdtj += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tooyv__dfdtj += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        tooyv__dfdtj += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        tooyv__dfdtj += '  regex = re.compile(pat, flags=flags)\n'
        tooyv__dfdtj += '  out_ind_arr, out_match_arr, out_arr_list = '
        tooyv__dfdtj += f'bodo.libs.dict_arr_ext.str_extractall{mdsf__wdc}(\n'
        tooyv__dfdtj += f'arr, regex, {khuk__qbof}, index_arr)\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += f'  out_arr_{i} = out_arr_list[{i}]\n'
        tooyv__dfdtj += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        tooyv__dfdtj += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        tooyv__dfdtj = 'def impl(S_str, pat, flags=0):\n'
        tooyv__dfdtj += '  regex = re.compile(pat, flags=flags)\n'
        tooyv__dfdtj += '  S = S_str._obj\n'
        tooyv__dfdtj += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        tooyv__dfdtj += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tooyv__dfdtj += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tooyv__dfdtj += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        tooyv__dfdtj += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        tooyv__dfdtj += '  numba.parfors.parfor.init_prange()\n'
        tooyv__dfdtj += '  n = len(str_arr)\n'
        tooyv__dfdtj += '  out_n_l = [0]\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += '  num_chars_{} = 0\n'.format(i)
        if kfy__kqudf:
            tooyv__dfdtj += '  index_num_chars = 0\n'
        tooyv__dfdtj += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if kfy__kqudf:
            tooyv__dfdtj += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        tooyv__dfdtj += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        tooyv__dfdtj += '          continue\n'
        tooyv__dfdtj += '      m = regex.findall(str_arr[i])\n'
        tooyv__dfdtj += '      out_n_l[0] += len(m)\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += '      l_{} = 0\n'.format(i)
        tooyv__dfdtj += '      for s in m:\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += '        l_{} += get_utf8_size(s{})\n'.format(i,
                '[{}]'.format(i) if khuk__qbof > 1 else '')
        for i in range(khuk__qbof):
            tooyv__dfdtj += '      num_chars_{0} += l_{0}\n'.format(i)
        tooyv__dfdtj += """  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)
"""
        for i in range(khuk__qbof):
            tooyv__dfdtj += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if kfy__kqudf:
            tooyv__dfdtj += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            tooyv__dfdtj += (
                '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n')
        tooyv__dfdtj += '  out_match_arr = np.empty(out_n, np.int64)\n'
        tooyv__dfdtj += '  out_ind = 0\n'
        tooyv__dfdtj += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        tooyv__dfdtj += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        tooyv__dfdtj += '          continue\n'
        tooyv__dfdtj += '      m = regex.findall(str_arr[j])\n'
        tooyv__dfdtj += '      for k, s in enumerate(m):\n'
        for i in range(khuk__qbof):
            tooyv__dfdtj += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if khuk__qbof > 1 else ''))
        tooyv__dfdtj += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        tooyv__dfdtj += """        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)
"""
        tooyv__dfdtj += '        out_ind += 1\n'
        tooyv__dfdtj += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        tooyv__dfdtj += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    lnraq__ubc = ', '.join('out_arr_{}'.format(i) for i in range(khuk__qbof))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(tooyv__dfdtj,
        udegx__girq, lnraq__ubc, 'out_index', extra_globals={
        'get_utf8_size': get_utf8_size, 're': re})
    return impl


def _get_column_names_from_regex(pat, flags, func_name):
    if not is_overload_constant_str(pat):
        raise BodoError(
            "Series.str.{}(): 'pat' argument should be a constant string".
            format(func_name))
    if not is_overload_constant_int(flags):
        raise BodoError(
            "Series.str.{}(): 'flags' argument should be a constant int".
            format(func_name))
    pat = get_overload_const_str(pat)
    flags = get_overload_const_int(flags)
    regex = re.compile(pat, flags=flags)
    if regex.groups == 0:
        raise BodoError(
            'Series.str.{}(): pattern {} contains no capture groups'.format
            (func_name, pat))
    ovl__lcmeg = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    udegx__girq = [ovl__lcmeg.get(1 + i, i) for i in range(regex.groups)]
    return udegx__girq, regex


def create_str2str_methods_overload(func_name):
    rcmm__gtv = func_name in ['lstrip', 'rstrip', 'strip']
    tooyv__dfdtj = f"""def f({'S_str, to_strip=None' if rcmm__gtv else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if rcmm__gtv else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if rcmm__gtv else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    tooyv__dfdtj += f"""def _dict_impl({'S_str, to_strip=None' if rcmm__gtv else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if rcmm__gtv else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    fyw__jnxtx = {}
    exec(tooyv__dfdtj, {'bodo': bodo, 'numba': numba, 'num_total_chars':
        bodo.libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, fyw__jnxtx)
    mbi__sek = fyw__jnxtx['f']
    kxh__sfy = fyw__jnxtx['_dict_impl']
    if rcmm__gtv:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return kxh__sfy
            return mbi__sek
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return kxh__sfy
            return mbi__sek
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    tooyv__dfdtj = 'def dict_impl(S_str):\n'
    tooyv__dfdtj += '    S = S_str._obj\n'
    tooyv__dfdtj += (
        '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    tooyv__dfdtj += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tooyv__dfdtj += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    tooyv__dfdtj += (
        f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n')
    tooyv__dfdtj += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    tooyv__dfdtj += 'def impl(S_str):\n'
    tooyv__dfdtj += '    S = S_str._obj\n'
    tooyv__dfdtj += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    tooyv__dfdtj += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tooyv__dfdtj += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    tooyv__dfdtj += '    numba.parfors.parfor.init_prange()\n'
    tooyv__dfdtj += '    l = len(str_arr)\n'
    tooyv__dfdtj += (
        '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
    tooyv__dfdtj += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    tooyv__dfdtj += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    tooyv__dfdtj += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    tooyv__dfdtj += '        else:\n'
    tooyv__dfdtj += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'
        .format(func_name))
    tooyv__dfdtj += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    tooyv__dfdtj += '      out_arr,index, name)\n'
    fyw__jnxtx = {}
    exec(tooyv__dfdtj, {'bodo': bodo, 'numba': numba, 'np': np}, fyw__jnxtx)
    impl = fyw__jnxtx['impl']
    uxcpt__ezur = fyw__jnxtx['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return uxcpt__ezur
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for fwav__ousj in bodo.hiframes.pd_series_ext.str2str_methods:
        njc__soj = create_str2str_methods_overload(fwav__ousj)
        overload_method(SeriesStrMethodType, fwav__ousj, inline='always',
            no_unliteral=True)(njc__soj)


def _install_str2bool_methods():
    for fwav__ousj in bodo.hiframes.pd_series_ext.str2bool_methods:
        njc__soj = create_str2bool_methods_overload(fwav__ousj)
        overload_method(SeriesStrMethodType, fwav__ousj, inline='always',
            no_unliteral=True)(njc__soj)


_install_str2str_methods()
_install_str2bool_methods()


@overload_attribute(SeriesType, 'cat')
def overload_series_cat(s):
    if not isinstance(s.dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):
        raise BodoError('Can only use .cat accessor with categorical values.')
    return lambda s: bodo.hiframes.series_str_impl.init_series_cat_method(s)


class SeriesCatMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        kqnjj__bpll = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(kqnjj__bpll)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zwkn__dgvz = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, zwkn__dgvz)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        psijj__kog, = args
        wboa__evs = signature.return_type
        jbch__yrjt = cgutils.create_struct_proxy(wboa__evs)(context, builder)
        jbch__yrjt.obj = psijj__kog
        context.nrt.incref(builder, signature.args[0], psijj__kog)
        return jbch__yrjt._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        vieu__qrbu = bodo.hiframes.pd_series_ext.get_series_data(S)
        bfedg__juwd = bodo.hiframes.pd_series_ext.get_series_index(S)
        kqnjj__bpll = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(vieu__qrbu),
            bfedg__juwd, kqnjj__bpll)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for zofln__ysomh in unsupported_cat_attrs:
        jmpk__duya = 'Series.cat.' + zofln__ysomh
        overload_attribute(SeriesCatMethodType, zofln__ysomh)(
            create_unsupported_overload(jmpk__duya))
    for ofbm__jrok in unsupported_cat_methods:
        jmpk__duya = 'Series.cat.' + ofbm__jrok
        overload_method(SeriesCatMethodType, ofbm__jrok)(
            create_unsupported_overload(jmpk__duya))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for ofbm__jrok in unsupported_str_methods:
        jmpk__duya = 'Series.str.' + ofbm__jrok
        overload_method(SeriesStrMethodType, ofbm__jrok)(
            create_unsupported_overload(jmpk__duya))


_install_strseries_unsupported()
