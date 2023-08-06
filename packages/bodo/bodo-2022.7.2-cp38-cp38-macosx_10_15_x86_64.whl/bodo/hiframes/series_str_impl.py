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
        tvem__lbz = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(tvem__lbz)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xjig__cxo = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, xjig__cxo)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        xcri__lopzj, = args
        emg__ppm = signature.return_type
        lrmnu__ginvy = cgutils.create_struct_proxy(emg__ppm)(context, builder)
        lrmnu__ginvy.obj = xcri__lopzj
        context.nrt.incref(builder, signature.args[0], xcri__lopzj)
        return lrmnu__ginvy._getvalue()
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
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(bkh__doeht)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(bkh__doeht, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
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
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(bkh__doeht,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(bkh__doeht, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    ydqx__jgj = S_str.stype.data
    if (ydqx__jgj != string_array_split_view_type and not is_str_arr_type(
        ydqx__jgj)) and not isinstance(ydqx__jgj, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(ydqx__jgj, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(bkh__doeht, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_get_array_impl
    if ydqx__jgj == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(bkh__doeht)
            mkc__euvy = 0
            for zfohs__woe in numba.parfors.parfor.internal_prange(n):
                bhp__vskv, bhp__vskv, ypooe__vip = get_split_view_index(
                    bkh__doeht, zfohs__woe, i)
                mkc__euvy += ypooe__vip
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, mkc__euvy)
            for wxqe__ldiw in numba.parfors.parfor.internal_prange(n):
                cgfm__set, uujcf__hira, ypooe__vip = get_split_view_index(
                    bkh__doeht, wxqe__ldiw, i)
                if cgfm__set == 0:
                    bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
                    spht__tjngl = get_split_view_data_ptr(bkh__doeht, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        wxqe__ldiw)
                    spht__tjngl = get_split_view_data_ptr(bkh__doeht,
                        uujcf__hira)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    wxqe__ldiw, spht__tjngl, ypooe__vip)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(bkh__doeht, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(bkh__doeht)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for wxqe__ldiw in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(bkh__doeht, wxqe__ldiw) or not len(
                bkh__doeht[wxqe__ldiw]) > i >= -len(bkh__doeht[wxqe__ldiw]):
                out_arr[wxqe__ldiw] = ''
                bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
            else:
                out_arr[wxqe__ldiw] = bkh__doeht[wxqe__ldiw][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    ydqx__jgj = S_str.stype.data
    if (ydqx__jgj != string_array_split_view_type and ydqx__jgj !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        ydqx__jgj)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(ywfmd__kbnou)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for wxqe__ldiw in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, wxqe__ldiw):
                out_arr[wxqe__ldiw] = ''
                bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
            else:
                unin__byp = ywfmd__kbnou[wxqe__ldiw]
                out_arr[wxqe__ldiw] = sep.join(unin__byp)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
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
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(bkh__doeht, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            utif__wzp = re.compile(pat, flags)
            hcth__xbbfk = len(bkh__doeht)
            out_arr = pre_alloc_string_array(hcth__xbbfk, -1)
            for wxqe__ldiw in numba.parfors.parfor.internal_prange(hcth__xbbfk
                ):
                if bodo.libs.array_kernels.isna(bkh__doeht, wxqe__ldiw):
                    out_arr[wxqe__ldiw] = ''
                    bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
                    continue
                out_arr[wxqe__ldiw] = utif__wzp.sub(repl, bkh__doeht[
                    wxqe__ldiw])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(bkh__doeht)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(hcth__xbbfk, -1)
        for wxqe__ldiw in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(bkh__doeht, wxqe__ldiw):
                out_arr[wxqe__ldiw] = ''
                bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
                continue
            out_arr[wxqe__ldiw] = bkh__doeht[wxqe__ldiw].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
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
    wzg__esfk = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(inab__bhido in pat) for inab__bhido in wzg__esfk])
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
    dngd__dyflu = re.IGNORECASE.value
    wuyv__zrnz = 'def impl(\n'
    wuyv__zrnz += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    wuyv__zrnz += '):\n'
    wuyv__zrnz += '  S = S_str._obj\n'
    wuyv__zrnz += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    wuyv__zrnz += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    wuyv__zrnz += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    wuyv__zrnz += '  l = len(arr)\n'
    wuyv__zrnz += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                wuyv__zrnz += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                wuyv__zrnz += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            wuyv__zrnz += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        wuyv__zrnz += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        wuyv__zrnz += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            wuyv__zrnz += '  upper_pat = pat.upper()\n'
        wuyv__zrnz += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        wuyv__zrnz += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        wuyv__zrnz += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        wuyv__zrnz += '      else: \n'
        if is_overload_true(case):
            wuyv__zrnz += '          out_arr[i] = pat in arr[i]\n'
        else:
            wuyv__zrnz += (
                '          out_arr[i] = upper_pat in arr[i].upper()\n')
    wuyv__zrnz += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    mbap__kug = {}
    exec(wuyv__zrnz, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': dngd__dyflu, 'get_search_regex':
        get_search_regex}, mbap__kug)
    impl = mbap__kug['impl']
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
    dngd__dyflu = re.IGNORECASE.value
    wuyv__zrnz = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    wuyv__zrnz += '        S = S_str._obj\n'
    wuyv__zrnz += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    wuyv__zrnz += '        l = len(arr)\n'
    wuyv__zrnz += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    wuyv__zrnz += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        wuyv__zrnz += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        wuyv__zrnz += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        wuyv__zrnz += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        wuyv__zrnz += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    wuyv__zrnz += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    mbap__kug = {}
    exec(wuyv__zrnz, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': dngd__dyflu, 'get_search_regex':
        get_search_regex}, mbap__kug)
    impl = mbap__kug['impl']
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
    wuyv__zrnz = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    wuyv__zrnz += '  S = S_str._obj\n'
    wuyv__zrnz += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    wuyv__zrnz += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    wuyv__zrnz += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    wuyv__zrnz += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        wuyv__zrnz += f"""  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})
"""
    if S_str.stype.data == bodo.dict_str_arr_type and all(ehzqf__evp ==
        bodo.dict_str_arr_type for ehzqf__evp in others.data):
        maka__hyvx = ', '.join(f'data{i}' for i in range(len(others.columns)))
        wuyv__zrnz += (
            f'  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {maka__hyvx}), sep)\n'
            )
    else:
        hgdj__owqvl = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        wuyv__zrnz += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        wuyv__zrnz += '  numba.parfors.parfor.init_prange()\n'
        wuyv__zrnz += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        wuyv__zrnz += f'      if {hgdj__owqvl}:\n'
        wuyv__zrnz += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        wuyv__zrnz += '          continue\n'
        hsvtr__uidk = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range(
            len(others.columns))])
        ibnl__iln = "''" if is_overload_none(sep) else 'sep'
        wuyv__zrnz += f'      out_arr[i] = {ibnl__iln}.join([{hsvtr__uidk}])\n'
    wuyv__zrnz += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    mbap__kug = {}
    exec(wuyv__zrnz, {'bodo': bodo, 'numba': numba}, mbap__kug)
    impl = mbap__kug['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(bkh__doeht, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        utif__wzp = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(hcth__xbbfk, np.int64)
        for i in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(utif__wzp, ywfmd__kbnou[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
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
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(bkh__doeht, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(hcth__xbbfk, np.int64)
        for i in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ywfmd__kbnou[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
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
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(bkh__doeht, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(hcth__xbbfk, np.int64)
        for i in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ywfmd__kbnou[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
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
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(hcth__xbbfk, -1)
        for wxqe__ldiw in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, wxqe__ldiw):
                bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
            else:
                if stop is not None:
                    lnqe__oflz = ywfmd__kbnou[wxqe__ldiw][stop:]
                else:
                    lnqe__oflz = ''
                out_arr[wxqe__ldiw] = ywfmd__kbnou[wxqe__ldiw][:start
                    ] + repl + lnqe__oflz
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
                oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
                tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(bkh__doeht,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    oua__htz, tvem__lbz)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            hcth__xbbfk = len(ywfmd__kbnou)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(hcth__xbbfk,
                -1)
            for wxqe__ldiw in numba.parfors.parfor.internal_prange(hcth__xbbfk
                ):
                if bodo.libs.array_kernels.isna(ywfmd__kbnou, wxqe__ldiw):
                    bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
                else:
                    out_arr[wxqe__ldiw] = ywfmd__kbnou[wxqe__ldiw] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return impl
    elif is_overload_constant_list(repeats):
        izl__ewhr = get_overload_const_list(repeats)
        htle__lrp = all([isinstance(eyeq__mmy, int) for eyeq__mmy in izl__ewhr]
            )
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        htle__lrp = True
    else:
        htle__lrp = False
    if htle__lrp:

        def impl(S_str, repeats):
            S = S_str._obj
            ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            cvkm__yhutc = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            hcth__xbbfk = len(ywfmd__kbnou)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(hcth__xbbfk,
                -1)
            for wxqe__ldiw in numba.parfors.parfor.internal_prange(hcth__xbbfk
                ):
                if bodo.libs.array_kernels.isna(ywfmd__kbnou, wxqe__ldiw):
                    bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
                else:
                    out_arr[wxqe__ldiw] = ywfmd__kbnou[wxqe__ldiw
                        ] * cvkm__yhutc[wxqe__ldiw]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    wuyv__zrnz = f"""def dict_impl(S_str, width, fillchar=' '):
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
    mbap__kug = {}
    kpw__fyxi = {'bodo': bodo, 'numba': numba}
    exec(wuyv__zrnz, kpw__fyxi, mbap__kug)
    impl = mbap__kug['impl']
    drvwr__fet = mbap__kug['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return drvwr__fet
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for nxh__vko in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(nxh__vko)
        overload_method(SeriesStrMethodType, nxh__vko, inline='always',
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
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(bkh__doeht,
                    width, fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(bkh__doeht,
                    width, fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(bkh__doeht,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(hcth__xbbfk, -1)
        for wxqe__ldiw in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, wxqe__ldiw):
                out_arr[wxqe__ldiw] = ''
                bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
            elif side == 'left':
                out_arr[wxqe__ldiw] = ywfmd__kbnou[wxqe__ldiw].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[wxqe__ldiw] = ywfmd__kbnou[wxqe__ldiw].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[wxqe__ldiw] = ywfmd__kbnou[wxqe__ldiw].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(bkh__doeht, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(hcth__xbbfk, -1)
        for wxqe__ldiw in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, wxqe__ldiw):
                out_arr[wxqe__ldiw] = ''
                bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
            else:
                out_arr[wxqe__ldiw] = ywfmd__kbnou[wxqe__ldiw].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
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
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(bkh__doeht, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(hcth__xbbfk, -1)
        for wxqe__ldiw in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, wxqe__ldiw):
                out_arr[wxqe__ldiw] = ''
                bodo.libs.array_kernels.setna(out_arr, wxqe__ldiw)
            else:
                out_arr[wxqe__ldiw] = ywfmd__kbnou[wxqe__ldiw][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(bkh__doeht, pat, na
                )
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(hcth__xbbfk)
        for i in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ywfmd__kbnou[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
            oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
            tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(bkh__doeht, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                oua__htz, tvem__lbz)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        ywfmd__kbnou = bodo.hiframes.pd_series_ext.get_series_data(S)
        tvem__lbz = bodo.hiframes.pd_series_ext.get_series_name(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        hcth__xbbfk = len(ywfmd__kbnou)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(hcth__xbbfk)
        for i in numba.parfors.parfor.internal_prange(hcth__xbbfk):
            if bodo.libs.array_kernels.isna(ywfmd__kbnou, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ywfmd__kbnou[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, oua__htz,
            tvem__lbz)
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
    zyeyq__gxaxr, regex = _get_column_names_from_regex(pat, flags, 'extract')
    bjtqu__xtbx = len(zyeyq__gxaxr)
    if S_str.stype.data == bodo.dict_str_arr_type:
        wuyv__zrnz = 'def impl(S_str, pat, flags=0, expand=True):\n'
        wuyv__zrnz += '  S = S_str._obj\n'
        wuyv__zrnz += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wuyv__zrnz += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wuyv__zrnz += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wuyv__zrnz += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {bjtqu__xtbx})
"""
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        wuyv__zrnz = 'def impl(S_str, pat, flags=0, expand=True):\n'
        wuyv__zrnz += '  regex = re.compile(pat, flags=flags)\n'
        wuyv__zrnz += '  S = S_str._obj\n'
        wuyv__zrnz += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wuyv__zrnz += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wuyv__zrnz += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wuyv__zrnz += '  numba.parfors.parfor.init_prange()\n'
        wuyv__zrnz += '  n = len(str_arr)\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        wuyv__zrnz += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        wuyv__zrnz += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += "          out_arr_{}[j] = ''\n".format(i)
            wuyv__zrnz += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        wuyv__zrnz += '      else:\n'
        wuyv__zrnz += '          m = regex.search(str_arr[j])\n'
        wuyv__zrnz += '          if m:\n'
        wuyv__zrnz += '            g = m.groups()\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        wuyv__zrnz += '          else:\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += "            out_arr_{}[j] = ''\n".format(i)
            wuyv__zrnz += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        tvem__lbz = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        wuyv__zrnz += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(tvem__lbz))
        mbap__kug = {}
        exec(wuyv__zrnz, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, mbap__kug)
        impl = mbap__kug['impl']
        return impl
    sggnv__qlv = ', '.join('out_arr_{}'.format(i) for i in range(bjtqu__xtbx))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(wuyv__zrnz,
        zyeyq__gxaxr, sggnv__qlv, 'index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    zyeyq__gxaxr, bhp__vskv = _get_column_names_from_regex(pat, flags,
        'extractall')
    bjtqu__xtbx = len(zyeyq__gxaxr)
    pwuv__xrra = isinstance(S_str.stype.index, StringIndexType)
    ponrh__hep = bjtqu__xtbx > 1
    scy__npd = '_multi' if ponrh__hep else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        wuyv__zrnz = 'def impl(S_str, pat, flags=0):\n'
        wuyv__zrnz += '  S = S_str._obj\n'
        wuyv__zrnz += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wuyv__zrnz += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wuyv__zrnz += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wuyv__zrnz += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        wuyv__zrnz += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        wuyv__zrnz += '  regex = re.compile(pat, flags=flags)\n'
        wuyv__zrnz += '  out_ind_arr, out_match_arr, out_arr_list = '
        wuyv__zrnz += f'bodo.libs.dict_arr_ext.str_extractall{scy__npd}(\n'
        wuyv__zrnz += f'arr, regex, {bjtqu__xtbx}, index_arr)\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += f'  out_arr_{i} = out_arr_list[{i}]\n'
        wuyv__zrnz += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        wuyv__zrnz += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        wuyv__zrnz = 'def impl(S_str, pat, flags=0):\n'
        wuyv__zrnz += '  regex = re.compile(pat, flags=flags)\n'
        wuyv__zrnz += '  S = S_str._obj\n'
        wuyv__zrnz += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wuyv__zrnz += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wuyv__zrnz += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wuyv__zrnz += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        wuyv__zrnz += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        wuyv__zrnz += '  numba.parfors.parfor.init_prange()\n'
        wuyv__zrnz += '  n = len(str_arr)\n'
        wuyv__zrnz += '  out_n_l = [0]\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += '  num_chars_{} = 0\n'.format(i)
        if pwuv__xrra:
            wuyv__zrnz += '  index_num_chars = 0\n'
        wuyv__zrnz += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if pwuv__xrra:
            wuyv__zrnz += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        wuyv__zrnz += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        wuyv__zrnz += '          continue\n'
        wuyv__zrnz += '      m = regex.findall(str_arr[i])\n'
        wuyv__zrnz += '      out_n_l[0] += len(m)\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += '      l_{} = 0\n'.format(i)
        wuyv__zrnz += '      for s in m:\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if bjtqu__xtbx > 1 else '')
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += '      num_chars_{0} += l_{0}\n'.format(i)
        wuyv__zrnz += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if pwuv__xrra:
            wuyv__zrnz += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            wuyv__zrnz += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        wuyv__zrnz += '  out_match_arr = np.empty(out_n, np.int64)\n'
        wuyv__zrnz += '  out_ind = 0\n'
        wuyv__zrnz += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        wuyv__zrnz += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        wuyv__zrnz += '          continue\n'
        wuyv__zrnz += '      m = regex.findall(str_arr[j])\n'
        wuyv__zrnz += '      for k, s in enumerate(m):\n'
        for i in range(bjtqu__xtbx):
            wuyv__zrnz += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if bjtqu__xtbx > 1 else ''))
        wuyv__zrnz += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        wuyv__zrnz += """        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)
"""
        wuyv__zrnz += '        out_ind += 1\n'
        wuyv__zrnz += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        wuyv__zrnz += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    sggnv__qlv = ', '.join('out_arr_{}'.format(i) for i in range(bjtqu__xtbx))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(wuyv__zrnz,
        zyeyq__gxaxr, sggnv__qlv, 'out_index', extra_globals={
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
    ncet__olrfp = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    zyeyq__gxaxr = [ncet__olrfp.get(1 + i, i) for i in range(regex.groups)]
    return zyeyq__gxaxr, regex


def create_str2str_methods_overload(func_name):
    jsyyt__dpz = func_name in ['lstrip', 'rstrip', 'strip']
    wuyv__zrnz = f"""def f({'S_str, to_strip=None' if jsyyt__dpz else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if jsyyt__dpz else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if jsyyt__dpz else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    wuyv__zrnz += f"""def _dict_impl({'S_str, to_strip=None' if jsyyt__dpz else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if jsyyt__dpz else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    mbap__kug = {}
    exec(wuyv__zrnz, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo
        .libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, mbap__kug)
    qvr__trxs = mbap__kug['f']
    eqzkb__rekjz = mbap__kug['_dict_impl']
    if jsyyt__dpz:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return eqzkb__rekjz
            return qvr__trxs
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return eqzkb__rekjz
            return qvr__trxs
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    wuyv__zrnz = 'def dict_impl(S_str):\n'
    wuyv__zrnz += '    S = S_str._obj\n'
    wuyv__zrnz += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    wuyv__zrnz += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    wuyv__zrnz += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    wuyv__zrnz += (
        f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n')
    wuyv__zrnz += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    wuyv__zrnz += 'def impl(S_str):\n'
    wuyv__zrnz += '    S = S_str._obj\n'
    wuyv__zrnz += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    wuyv__zrnz += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    wuyv__zrnz += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    wuyv__zrnz += '    numba.parfors.parfor.init_prange()\n'
    wuyv__zrnz += '    l = len(str_arr)\n'
    wuyv__zrnz += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    wuyv__zrnz += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    wuyv__zrnz += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    wuyv__zrnz += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    wuyv__zrnz += '        else:\n'
    wuyv__zrnz += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'.
        format(func_name))
    wuyv__zrnz += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    wuyv__zrnz += '      out_arr,index, name)\n'
    mbap__kug = {}
    exec(wuyv__zrnz, {'bodo': bodo, 'numba': numba, 'np': np}, mbap__kug)
    impl = mbap__kug['impl']
    drvwr__fet = mbap__kug['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return drvwr__fet
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for ysxec__rflyl in bodo.hiframes.pd_series_ext.str2str_methods:
        yxlp__oublf = create_str2str_methods_overload(ysxec__rflyl)
        overload_method(SeriesStrMethodType, ysxec__rflyl, inline='always',
            no_unliteral=True)(yxlp__oublf)


def _install_str2bool_methods():
    for ysxec__rflyl in bodo.hiframes.pd_series_ext.str2bool_methods:
        yxlp__oublf = create_str2bool_methods_overload(ysxec__rflyl)
        overload_method(SeriesStrMethodType, ysxec__rflyl, inline='always',
            no_unliteral=True)(yxlp__oublf)


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
        tvem__lbz = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(tvem__lbz)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xjig__cxo = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, xjig__cxo)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        xcri__lopzj, = args
        oyje__efc = signature.return_type
        dflpn__deo = cgutils.create_struct_proxy(oyje__efc)(context, builder)
        dflpn__deo.obj = xcri__lopzj
        context.nrt.incref(builder, signature.args[0], xcri__lopzj)
        return dflpn__deo._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        bkh__doeht = bodo.hiframes.pd_series_ext.get_series_data(S)
        oua__htz = bodo.hiframes.pd_series_ext.get_series_index(S)
        tvem__lbz = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(bkh__doeht),
            oua__htz, tvem__lbz)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for fxqx__fdvp in unsupported_cat_attrs:
        roc__gji = 'Series.cat.' + fxqx__fdvp
        overload_attribute(SeriesCatMethodType, fxqx__fdvp)(
            create_unsupported_overload(roc__gji))
    for luvlt__csqe in unsupported_cat_methods:
        roc__gji = 'Series.cat.' + luvlt__csqe
        overload_method(SeriesCatMethodType, luvlt__csqe)(
            create_unsupported_overload(roc__gji))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for luvlt__csqe in unsupported_str_methods:
        roc__gji = 'Series.str.' + luvlt__csqe
        overload_method(SeriesStrMethodType, luvlt__csqe)(
            create_unsupported_overload(roc__gji))


_install_strseries_unsupported()
