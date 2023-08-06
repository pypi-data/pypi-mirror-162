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
        lrz__sthj = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(lrz__sthj)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nib__gbprp = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, nib__gbprp)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        lrdg__rat, = args
        jkgca__obi = signature.return_type
        eydgz__nycx = cgutils.create_struct_proxy(jkgca__obi)(context, builder)
        eydgz__nycx.obj = lrdg__rat
        context.nrt.incref(builder, signature.args[0], lrdg__rat)
        return eydgz__nycx._getvalue()
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
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(zgydj__rwsk)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(zgydj__rwsk, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
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
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(zgydj__rwsk,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(zgydj__rwsk, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    fur__kjxt = S_str.stype.data
    if (fur__kjxt != string_array_split_view_type and not is_str_arr_type(
        fur__kjxt)) and not isinstance(fur__kjxt, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(fur__kjxt, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(zgydj__rwsk, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_get_array_impl
    if fur__kjxt == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(zgydj__rwsk)
            jbrv__zjwj = 0
            for etve__jyhpy in numba.parfors.parfor.internal_prange(n):
                ahia__rbuly, ahia__rbuly, vdi__wdwrl = get_split_view_index(
                    zgydj__rwsk, etve__jyhpy, i)
                jbrv__zjwj += vdi__wdwrl
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, jbrv__zjwj)
            for wtxwm__vqxj in numba.parfors.parfor.internal_prange(n):
                dbpf__tbjqm, btqxm__uchnh, vdi__wdwrl = get_split_view_index(
                    zgydj__rwsk, wtxwm__vqxj, i)
                if dbpf__tbjqm == 0:
                    bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
                    rowvf__ofes = get_split_view_data_ptr(zgydj__rwsk, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        wtxwm__vqxj)
                    rowvf__ofes = get_split_view_data_ptr(zgydj__rwsk,
                        btqxm__uchnh)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    wtxwm__vqxj, rowvf__ofes, vdi__wdwrl)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(zgydj__rwsk, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(zgydj__rwsk)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for wtxwm__vqxj in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(zgydj__rwsk, wtxwm__vqxj
                ) or not len(zgydj__rwsk[wtxwm__vqxj]) > i >= -len(zgydj__rwsk
                [wtxwm__vqxj]):
                out_arr[wtxwm__vqxj] = ''
                bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
            else:
                out_arr[wtxwm__vqxj] = zgydj__rwsk[wtxwm__vqxj][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    fur__kjxt = S_str.stype.data
    if (fur__kjxt != string_array_split_view_type and fur__kjxt !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        fur__kjxt)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(xppms__tsjv)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for wtxwm__vqxj in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(xppms__tsjv, wtxwm__vqxj):
                out_arr[wtxwm__vqxj] = ''
                bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
            else:
                skjc__mlz = xppms__tsjv[wtxwm__vqxj]
                out_arr[wtxwm__vqxj] = sep.join(skjc__mlz)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
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
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(zgydj__rwsk, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            hukf__vgvlh = re.compile(pat, flags)
            rkwc__lort = len(zgydj__rwsk)
            out_arr = pre_alloc_string_array(rkwc__lort, -1)
            for wtxwm__vqxj in numba.parfors.parfor.internal_prange(rkwc__lort
                ):
                if bodo.libs.array_kernels.isna(zgydj__rwsk, wtxwm__vqxj):
                    out_arr[wtxwm__vqxj] = ''
                    bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
                    continue
                out_arr[wtxwm__vqxj] = hukf__vgvlh.sub(repl, zgydj__rwsk[
                    wtxwm__vqxj])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(zgydj__rwsk)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(rkwc__lort, -1)
        for wtxwm__vqxj in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(zgydj__rwsk, wtxwm__vqxj):
                out_arr[wtxwm__vqxj] = ''
                bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
                continue
            out_arr[wtxwm__vqxj] = zgydj__rwsk[wtxwm__vqxj].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
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
    xmm__wer = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(sdb__zbr in pat) for sdb__zbr in xmm__wer])
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
    ncwa__wbtcm = re.IGNORECASE.value
    dnv__exym = 'def impl(\n'
    dnv__exym += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    dnv__exym += '):\n'
    dnv__exym += '  S = S_str._obj\n'
    dnv__exym += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    dnv__exym += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    dnv__exym += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    dnv__exym += '  l = len(arr)\n'
    dnv__exym += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                dnv__exym += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                dnv__exym += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            dnv__exym += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        dnv__exym += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        dnv__exym += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            dnv__exym += '  upper_pat = pat.upper()\n'
        dnv__exym += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        dnv__exym += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        dnv__exym += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        dnv__exym += '      else: \n'
        if is_overload_true(case):
            dnv__exym += '          out_arr[i] = pat in arr[i]\n'
        else:
            dnv__exym += '          out_arr[i] = upper_pat in arr[i].upper()\n'
    dnv__exym += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    vpdbn__hfj = {}
    exec(dnv__exym, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': ncwa__wbtcm, 'get_search_regex':
        get_search_regex}, vpdbn__hfj)
    impl = vpdbn__hfj['impl']
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
    ncwa__wbtcm = re.IGNORECASE.value
    dnv__exym = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    dnv__exym += '        S = S_str._obj\n'
    dnv__exym += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    dnv__exym += '        l = len(arr)\n'
    dnv__exym += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    dnv__exym += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        dnv__exym += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        dnv__exym += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        dnv__exym += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        dnv__exym += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    dnv__exym += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    vpdbn__hfj = {}
    exec(dnv__exym, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': ncwa__wbtcm, 'get_search_regex':
        get_search_regex}, vpdbn__hfj)
    impl = vpdbn__hfj['impl']
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
    dnv__exym = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    dnv__exym += '  S = S_str._obj\n'
    dnv__exym += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    dnv__exym += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    dnv__exym += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    dnv__exym += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        dnv__exym += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})\n'
            )
    if S_str.stype.data == bodo.dict_str_arr_type and all(vtbnh__gkaih ==
        bodo.dict_str_arr_type for vtbnh__gkaih in others.data):
        jzf__wyth = ', '.join(f'data{i}' for i in range(len(others.columns)))
        dnv__exym += (
            f'  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {jzf__wyth}), sep)\n'
            )
    else:
        qou__lqlme = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        dnv__exym += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        dnv__exym += '  numba.parfors.parfor.init_prange()\n'
        dnv__exym += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        dnv__exym += f'      if {qou__lqlme}:\n'
        dnv__exym += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        dnv__exym += '          continue\n'
        uqng__ebtv = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range(
            len(others.columns))])
        ltdy__cpia = "''" if is_overload_none(sep) else 'sep'
        dnv__exym += f'      out_arr[i] = {ltdy__cpia}.join([{uqng__ebtv}])\n'
    dnv__exym += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    vpdbn__hfj = {}
    exec(dnv__exym, {'bodo': bodo, 'numba': numba}, vpdbn__hfj)
    impl = vpdbn__hfj['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(zgydj__rwsk, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        hukf__vgvlh = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(rkwc__lort, np.int64)
        for i in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(hukf__vgvlh, xppms__tsjv[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
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
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(zgydj__rwsk, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(rkwc__lort, np.int64)
        for i in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = xppms__tsjv[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
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
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(zgydj__rwsk, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(rkwc__lort, np.int64)
        for i in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = xppms__tsjv[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
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
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(rkwc__lort, -1)
        for wtxwm__vqxj in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, wtxwm__vqxj):
                bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
            else:
                if stop is not None:
                    uzw__taz = xppms__tsjv[wtxwm__vqxj][stop:]
                else:
                    uzw__taz = ''
                out_arr[wtxwm__vqxj] = xppms__tsjv[wtxwm__vqxj][:start
                    ] + repl + uzw__taz
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
                vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
                lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(zgydj__rwsk,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    vgltw__rebyd, lrz__sthj)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            rkwc__lort = len(xppms__tsjv)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(rkwc__lort,
                -1)
            for wtxwm__vqxj in numba.parfors.parfor.internal_prange(rkwc__lort
                ):
                if bodo.libs.array_kernels.isna(xppms__tsjv, wtxwm__vqxj):
                    bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
                else:
                    out_arr[wtxwm__vqxj] = xppms__tsjv[wtxwm__vqxj] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return impl
    elif is_overload_constant_list(repeats):
        msa__hjoek = get_overload_const_list(repeats)
        hrjq__sesk = all([isinstance(wnqt__patn, int) for wnqt__patn in
            msa__hjoek])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        hrjq__sesk = True
    else:
        hrjq__sesk = False
    if hrjq__sesk:

        def impl(S_str, repeats):
            S = S_str._obj
            xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            stp__eiuvh = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            rkwc__lort = len(xppms__tsjv)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(rkwc__lort,
                -1)
            for wtxwm__vqxj in numba.parfors.parfor.internal_prange(rkwc__lort
                ):
                if bodo.libs.array_kernels.isna(xppms__tsjv, wtxwm__vqxj):
                    bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
                else:
                    out_arr[wtxwm__vqxj] = xppms__tsjv[wtxwm__vqxj
                        ] * stp__eiuvh[wtxwm__vqxj]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    dnv__exym = f"""def dict_impl(S_str, width, fillchar=' '):
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
    vpdbn__hfj = {}
    wav__cdaz = {'bodo': bodo, 'numba': numba}
    exec(dnv__exym, wav__cdaz, vpdbn__hfj)
    impl = vpdbn__hfj['impl']
    elyb__zoo = vpdbn__hfj['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return elyb__zoo
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for qdnc__mgqw in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(qdnc__mgqw)
        overload_method(SeriesStrMethodType, qdnc__mgqw, inline='always',
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
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(zgydj__rwsk,
                    width, fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(zgydj__rwsk,
                    width, fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(zgydj__rwsk,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(rkwc__lort, -1)
        for wtxwm__vqxj in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, wtxwm__vqxj):
                out_arr[wtxwm__vqxj] = ''
                bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
            elif side == 'left':
                out_arr[wtxwm__vqxj] = xppms__tsjv[wtxwm__vqxj].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[wtxwm__vqxj] = xppms__tsjv[wtxwm__vqxj].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[wtxwm__vqxj] = xppms__tsjv[wtxwm__vqxj].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(zgydj__rwsk, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(rkwc__lort, -1)
        for wtxwm__vqxj in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, wtxwm__vqxj):
                out_arr[wtxwm__vqxj] = ''
                bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
            else:
                out_arr[wtxwm__vqxj] = xppms__tsjv[wtxwm__vqxj].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
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
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(zgydj__rwsk, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(rkwc__lort, -1)
        for wtxwm__vqxj in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, wtxwm__vqxj):
                out_arr[wtxwm__vqxj] = ''
                bodo.libs.array_kernels.setna(out_arr, wtxwm__vqxj)
            else:
                out_arr[wtxwm__vqxj] = xppms__tsjv[wtxwm__vqxj][start:stop:step
                    ]
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(zgydj__rwsk,
                pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(rkwc__lort)
        for i in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = xppms__tsjv[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
            vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(zgydj__rwsk, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                vgltw__rebyd, lrz__sthj)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        xppms__tsjv = bodo.hiframes.pd_series_ext.get_series_data(S)
        lrz__sthj = bodo.hiframes.pd_series_ext.get_series_name(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        rkwc__lort = len(xppms__tsjv)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(rkwc__lort)
        for i in numba.parfors.parfor.internal_prange(rkwc__lort):
            if bodo.libs.array_kernels.isna(xppms__tsjv, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = xppms__tsjv[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            vgltw__rebyd, lrz__sthj)
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
    zvgy__oezk, regex = _get_column_names_from_regex(pat, flags, 'extract')
    pnk__rzo = len(zvgy__oezk)
    if S_str.stype.data == bodo.dict_str_arr_type:
        dnv__exym = 'def impl(S_str, pat, flags=0, expand=True):\n'
        dnv__exym += '  S = S_str._obj\n'
        dnv__exym += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        dnv__exym += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        dnv__exym += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        dnv__exym += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {pnk__rzo})
"""
        for i in range(pnk__rzo):
            dnv__exym += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        dnv__exym = 'def impl(S_str, pat, flags=0, expand=True):\n'
        dnv__exym += '  regex = re.compile(pat, flags=flags)\n'
        dnv__exym += '  S = S_str._obj\n'
        dnv__exym += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        dnv__exym += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        dnv__exym += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        dnv__exym += '  numba.parfors.parfor.init_prange()\n'
        dnv__exym += '  n = len(str_arr)\n'
        for i in range(pnk__rzo):
            dnv__exym += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        dnv__exym += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        dnv__exym += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(pnk__rzo):
            dnv__exym += "          out_arr_{}[j] = ''\n".format(i)
            dnv__exym += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        dnv__exym += '      else:\n'
        dnv__exym += '          m = regex.search(str_arr[j])\n'
        dnv__exym += '          if m:\n'
        dnv__exym += '            g = m.groups()\n'
        for i in range(pnk__rzo):
            dnv__exym += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        dnv__exym += '          else:\n'
        for i in range(pnk__rzo):
            dnv__exym += "            out_arr_{}[j] = ''\n".format(i)
            dnv__exym += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        lrz__sthj = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        dnv__exym += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(lrz__sthj))
        vpdbn__hfj = {}
        exec(dnv__exym, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, vpdbn__hfj)
        impl = vpdbn__hfj['impl']
        return impl
    bxlva__pro = ', '.join('out_arr_{}'.format(i) for i in range(pnk__rzo))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(dnv__exym, zvgy__oezk,
        bxlva__pro, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    zvgy__oezk, ahia__rbuly = _get_column_names_from_regex(pat, flags,
        'extractall')
    pnk__rzo = len(zvgy__oezk)
    vlf__kaa = isinstance(S_str.stype.index, StringIndexType)
    nlot__cmkal = pnk__rzo > 1
    lkqxt__inkm = '_multi' if nlot__cmkal else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        dnv__exym = 'def impl(S_str, pat, flags=0):\n'
        dnv__exym += '  S = S_str._obj\n'
        dnv__exym += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        dnv__exym += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        dnv__exym += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        dnv__exym += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        dnv__exym += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        dnv__exym += '  regex = re.compile(pat, flags=flags)\n'
        dnv__exym += '  out_ind_arr, out_match_arr, out_arr_list = '
        dnv__exym += f'bodo.libs.dict_arr_ext.str_extractall{lkqxt__inkm}(\n'
        dnv__exym += f'arr, regex, {pnk__rzo}, index_arr)\n'
        for i in range(pnk__rzo):
            dnv__exym += f'  out_arr_{i} = out_arr_list[{i}]\n'
        dnv__exym += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        dnv__exym += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        dnv__exym = 'def impl(S_str, pat, flags=0):\n'
        dnv__exym += '  regex = re.compile(pat, flags=flags)\n'
        dnv__exym += '  S = S_str._obj\n'
        dnv__exym += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        dnv__exym += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        dnv__exym += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        dnv__exym += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        dnv__exym += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        dnv__exym += '  numba.parfors.parfor.init_prange()\n'
        dnv__exym += '  n = len(str_arr)\n'
        dnv__exym += '  out_n_l = [0]\n'
        for i in range(pnk__rzo):
            dnv__exym += '  num_chars_{} = 0\n'.format(i)
        if vlf__kaa:
            dnv__exym += '  index_num_chars = 0\n'
        dnv__exym += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if vlf__kaa:
            dnv__exym += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        dnv__exym += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        dnv__exym += '          continue\n'
        dnv__exym += '      m = regex.findall(str_arr[i])\n'
        dnv__exym += '      out_n_l[0] += len(m)\n'
        for i in range(pnk__rzo):
            dnv__exym += '      l_{} = 0\n'.format(i)
        dnv__exym += '      for s in m:\n'
        for i in range(pnk__rzo):
            dnv__exym += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if pnk__rzo > 1 else '')
        for i in range(pnk__rzo):
            dnv__exym += '      num_chars_{0} += l_{0}\n'.format(i)
        dnv__exym += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(pnk__rzo):
            dnv__exym += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if vlf__kaa:
            dnv__exym += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            dnv__exym += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        dnv__exym += '  out_match_arr = np.empty(out_n, np.int64)\n'
        dnv__exym += '  out_ind = 0\n'
        dnv__exym += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        dnv__exym += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        dnv__exym += '          continue\n'
        dnv__exym += '      m = regex.findall(str_arr[j])\n'
        dnv__exym += '      for k, s in enumerate(m):\n'
        for i in range(pnk__rzo):
            dnv__exym += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if pnk__rzo > 1 else ''))
        dnv__exym += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        dnv__exym += (
            '        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)\n'
            )
        dnv__exym += '        out_ind += 1\n'
        dnv__exym += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        dnv__exym += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    bxlva__pro = ', '.join('out_arr_{}'.format(i) for i in range(pnk__rzo))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(dnv__exym, zvgy__oezk,
        bxlva__pro, 'out_index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
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
    wjl__vzwms = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    zvgy__oezk = [wjl__vzwms.get(1 + i, i) for i in range(regex.groups)]
    return zvgy__oezk, regex


def create_str2str_methods_overload(func_name):
    oyjrk__kwjbk = func_name in ['lstrip', 'rstrip', 'strip']
    dnv__exym = f"""def f({'S_str, to_strip=None' if oyjrk__kwjbk else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if oyjrk__kwjbk else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if oyjrk__kwjbk else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    dnv__exym += f"""def _dict_impl({'S_str, to_strip=None' if oyjrk__kwjbk else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if oyjrk__kwjbk else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    vpdbn__hfj = {}
    exec(dnv__exym, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo.
        libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, vpdbn__hfj)
    jmjbj__opj = vpdbn__hfj['f']
    lhwnt__rbnt = vpdbn__hfj['_dict_impl']
    if oyjrk__kwjbk:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return lhwnt__rbnt
            return jmjbj__opj
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return lhwnt__rbnt
            return jmjbj__opj
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    dnv__exym = 'def dict_impl(S_str):\n'
    dnv__exym += '    S = S_str._obj\n'
    dnv__exym += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    dnv__exym += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    dnv__exym += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    dnv__exym += f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n'
    dnv__exym += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    dnv__exym += 'def impl(S_str):\n'
    dnv__exym += '    S = S_str._obj\n'
    dnv__exym += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    dnv__exym += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    dnv__exym += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    dnv__exym += '    numba.parfors.parfor.init_prange()\n'
    dnv__exym += '    l = len(str_arr)\n'
    dnv__exym += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    dnv__exym += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    dnv__exym += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    dnv__exym += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    dnv__exym += '        else:\n'
    dnv__exym += '            out_arr[i] = np.bool_(str_arr[i].{}())\n'.format(
        func_name)
    dnv__exym += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    dnv__exym += '      out_arr,index, name)\n'
    vpdbn__hfj = {}
    exec(dnv__exym, {'bodo': bodo, 'numba': numba, 'np': np}, vpdbn__hfj)
    impl = vpdbn__hfj['impl']
    elyb__zoo = vpdbn__hfj['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return elyb__zoo
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for jvqk__eim in bodo.hiframes.pd_series_ext.str2str_methods:
        drhbl__ywgr = create_str2str_methods_overload(jvqk__eim)
        overload_method(SeriesStrMethodType, jvqk__eim, inline='always',
            no_unliteral=True)(drhbl__ywgr)


def _install_str2bool_methods():
    for jvqk__eim in bodo.hiframes.pd_series_ext.str2bool_methods:
        drhbl__ywgr = create_str2bool_methods_overload(jvqk__eim)
        overload_method(SeriesStrMethodType, jvqk__eim, inline='always',
            no_unliteral=True)(drhbl__ywgr)


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
        lrz__sthj = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(lrz__sthj)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nib__gbprp = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, nib__gbprp)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        lrdg__rat, = args
        ykal__nhtq = signature.return_type
        ayqmp__nygvd = cgutils.create_struct_proxy(ykal__nhtq)(context, builder
            )
        ayqmp__nygvd.obj = lrdg__rat
        context.nrt.incref(builder, signature.args[0], lrdg__rat)
        return ayqmp__nygvd._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        zgydj__rwsk = bodo.hiframes.pd_series_ext.get_series_data(S)
        vgltw__rebyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        lrz__sthj = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(zgydj__rwsk),
            vgltw__rebyd, lrz__sthj)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for phc__udkf in unsupported_cat_attrs:
        jmas__qrn = 'Series.cat.' + phc__udkf
        overload_attribute(SeriesCatMethodType, phc__udkf)(
            create_unsupported_overload(jmas__qrn))
    for lazk__hjp in unsupported_cat_methods:
        jmas__qrn = 'Series.cat.' + lazk__hjp
        overload_method(SeriesCatMethodType, lazk__hjp)(
            create_unsupported_overload(jmas__qrn))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for lazk__hjp in unsupported_str_methods:
        jmas__qrn = 'Series.str.' + lazk__hjp
        overload_method(SeriesStrMethodType, lazk__hjp)(
            create_unsupported_overload(jmas__qrn))


_install_strseries_unsupported()
