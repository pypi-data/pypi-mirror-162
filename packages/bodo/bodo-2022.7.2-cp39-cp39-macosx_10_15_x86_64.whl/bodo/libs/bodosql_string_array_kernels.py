"""
Implements string array kernels that are specific to BodoSQL
"""
import numba
import numpy as np
from numba.core import types
from numba.extending import overload, register_jitable
import bodo
from bodo.libs.bodosql_array_kernel_utils import *


@numba.generated_jit(nopython=True)
def char(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.char_util',
            ['arr'], 0)

    def impl(arr):
        return char_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def editdistance_no_max(s, t):
    args = [s, t]
    for igbhu__vdyq in range(2):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_no_max', ['s',
                't'], igbhu__vdyq)

    def impl(s, t):
        return editdistance_no_max_util(s, t)
    return impl


@numba.generated_jit(nopython=True)
def editdistance_with_max(s, t, maxDistance):
    args = [s, t, maxDistance]
    for igbhu__vdyq in range(3):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_with_max', [
                's', 't', 'maxDistance'], igbhu__vdyq)

    def impl(s, t, maxDistance):
        return editdistance_with_max_util(s, t, maxDistance)
    return impl


@numba.generated_jit(nopython=True)
def format(arr, places):
    args = [arr, places]
    for igbhu__vdyq in range(2):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.format',
                ['arr', 'places'], igbhu__vdyq)

    def impl(arr, places):
        return format_util(arr, places)
    return impl


@numba.generated_jit(nopython=True)
def instr(arr, target):
    args = [arr, target]
    for igbhu__vdyq in range(2):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.instr',
                ['arr', 'target'], igbhu__vdyq)

    def impl(arr, target):
        return instr_util(arr, target)
    return impl


def left(arr, n_chars):
    return


@overload(left)
def overload_left(arr, n_chars):
    args = [arr, n_chars]
    for igbhu__vdyq in range(2):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.left', [
                'arr', 'n_chars'], igbhu__vdyq)

    def impl(arr, n_chars):
        return left_util(arr, n_chars)
    return impl


def lpad(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for igbhu__vdyq in range(3):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], igbhu__vdyq)

    def impl(arr, length, padstr):
        return lpad_util(arr, length, padstr)
    return impl


@numba.generated_jit(nopython=True)
def ord_ascii(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.ord_ascii_util',
            ['arr'], 0)

    def impl(arr):
        return ord_ascii_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def repeat(arr, repeats):
    args = [arr, repeats]
    for igbhu__vdyq in range(2):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.repeat',
                ['arr', 'repeats'], igbhu__vdyq)

    def impl(arr, repeats):
        return repeat_util(arr, repeats)
    return impl


@numba.generated_jit(nopython=True)
def replace(arr, to_replace, replace_with):
    args = [arr, to_replace, replace_with]
    for igbhu__vdyq in range(3):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.replace',
                ['arr', 'to_replace', 'replace_with'], igbhu__vdyq)

    def impl(arr, to_replace, replace_with):
        return replace_util(arr, to_replace, replace_with)
    return impl


@numba.generated_jit(nopython=True)
def reverse(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.reverse_util',
            ['arr'], 0)

    def impl(arr):
        return reverse_util(arr)
    return impl


def right(arr, n_chars):
    return


@overload(right)
def overload_right(arr, n_chars):
    args = [arr, n_chars]
    for igbhu__vdyq in range(2):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.right',
                ['arr', 'n_chars'], igbhu__vdyq)

    def impl(arr, n_chars):
        return right_util(arr, n_chars)
    return impl


def rpad(arr, length, padstr):
    return


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for igbhu__vdyq in range(3):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], igbhu__vdyq)

    def impl(arr, length, padstr):
        return rpad_util(arr, length, padstr)
    return impl


@numba.generated_jit(nopython=True)
def space(n_chars):
    if isinstance(n_chars, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.space_util',
            ['n_chars'], 0)

    def impl(n_chars):
        return space_util(n_chars)
    return impl


@numba.generated_jit(nopython=True)
def strcmp(arr0, arr1):
    args = [arr0, arr1]
    for igbhu__vdyq in range(2):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strcmp',
                ['arr0', 'arr1'], igbhu__vdyq)

    def impl(arr0, arr1):
        return strcmp_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def substring(arr, start, length):
    args = [arr, start, length]
    for igbhu__vdyq in range(3):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.substring',
                ['arr', 'start', 'length'], igbhu__vdyq)

    def impl(arr, start, length):
        return substring_util(arr, start, length)
    return impl


@numba.generated_jit(nopython=True)
def substring_index(arr, delimiter, occurrences):
    args = [arr, delimiter, occurrences]
    for igbhu__vdyq in range(3):
        if isinstance(args[igbhu__vdyq], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.substring_index', ['arr',
                'delimiter', 'occurrences'], igbhu__vdyq)

    def impl(arr, delimiter, occurrences):
        return substring_index_util(arr, delimiter, occurrences)
    return impl


@numba.generated_jit(nopython=True)
def char_util(arr):
    verify_int_arg(arr, 'CHAR', 'arr')
    xrutd__vfe = ['arr']
    uxbp__oka = [arr]
    ghnsj__nemnb = [True]
    azlpv__qqm = 'if 0 <= arg0 <= 127:\n'
    azlpv__qqm += '   res[i] = chr(arg0)\n'
    azlpv__qqm += 'else:\n'
    azlpv__qqm += '   bodo.libs.array_kernels.setna(res, i)\n'
    cyk__ayzih = bodo.string_array_type
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def instr_util(arr, target):
    verify_string_arg(arr, 'instr', 'arr')
    verify_string_arg(target, 'instr', 'target')
    xrutd__vfe = ['arr', 'target']
    uxbp__oka = [arr, target]
    ghnsj__nemnb = [True] * 2
    azlpv__qqm = 'res[i] = arg0.find(arg1) + 1'
    cyk__ayzih = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@register_jitable
def min_edit_distance(s, t):
    if len(s) > len(t):
        s, t = t, s
    cisx__qkuw, ajkhn__yifvr = len(s), len(t)
    qarqe__lwmce, ruemd__zazd = 1, 0
    arr = np.zeros((2, cisx__qkuw + 1), dtype=np.uint32)
    arr[0, :] = np.arange(cisx__qkuw + 1)
    for igbhu__vdyq in range(1, ajkhn__yifvr + 1):
        arr[qarqe__lwmce, 0] = igbhu__vdyq
        for vnye__lpr in range(1, cisx__qkuw + 1):
            if s[vnye__lpr - 1] == t[igbhu__vdyq - 1]:
                arr[qarqe__lwmce, vnye__lpr] = arr[ruemd__zazd, vnye__lpr - 1]
            else:
                arr[qarqe__lwmce, vnye__lpr] = 1 + min(arr[qarqe__lwmce, 
                    vnye__lpr - 1], arr[ruemd__zazd, vnye__lpr], arr[
                    ruemd__zazd, vnye__lpr - 1])
        qarqe__lwmce, ruemd__zazd = ruemd__zazd, qarqe__lwmce
    return arr[ajkhn__yifvr % 2, cisx__qkuw]


@register_jitable
def min_edit_distance_with_max(s, t, maxDistance):
    if maxDistance < 0:
        return 0
    if len(s) > len(t):
        s, t = t, s
    cisx__qkuw, ajkhn__yifvr = len(s), len(t)
    if cisx__qkuw <= maxDistance and ajkhn__yifvr <= maxDistance:
        return min_edit_distance(s, t)
    qarqe__lwmce, ruemd__zazd = 1, 0
    arr = np.zeros((2, cisx__qkuw + 1), dtype=np.uint32)
    arr[0, :] = np.arange(cisx__qkuw + 1)
    for igbhu__vdyq in range(1, ajkhn__yifvr + 1):
        arr[qarqe__lwmce, 0] = igbhu__vdyq
        for vnye__lpr in range(1, cisx__qkuw + 1):
            if s[vnye__lpr - 1] == t[igbhu__vdyq - 1]:
                arr[qarqe__lwmce, vnye__lpr] = arr[ruemd__zazd, vnye__lpr - 1]
            else:
                arr[qarqe__lwmce, vnye__lpr] = 1 + min(arr[qarqe__lwmce, 
                    vnye__lpr - 1], arr[ruemd__zazd, vnye__lpr], arr[
                    ruemd__zazd, vnye__lpr - 1])
        if (arr[qarqe__lwmce] >= maxDistance).all():
            return maxDistance
        qarqe__lwmce, ruemd__zazd = ruemd__zazd, qarqe__lwmce
    return min(arr[ajkhn__yifvr % 2, cisx__qkuw], maxDistance)


@numba.generated_jit(nopython=True)
def editdistance_no_max_util(s, t):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    xrutd__vfe = ['s', 't']
    uxbp__oka = [s, t]
    ghnsj__nemnb = [True] * 2
    azlpv__qqm = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance(arg0, arg1)'
        )
    cyk__ayzih = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def editdistance_with_max_util(s, t, maxDistance):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    verify_int_arg(maxDistance, 'editdistance_no_max', 't')
    xrutd__vfe = ['s', 't', 'maxDistance']
    uxbp__oka = [s, t, maxDistance]
    ghnsj__nemnb = [True] * 3
    azlpv__qqm = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance_with_max(arg0, arg1, arg2)'
        )
    cyk__ayzih = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def format_util(arr, places):
    verify_int_float_arg(arr, 'FORMAT', 'arr')
    verify_int_arg(places, 'FORMAT', 'places')
    xrutd__vfe = ['arr', 'places']
    uxbp__oka = [arr, places]
    ghnsj__nemnb = [True] * 2
    azlpv__qqm = 'prec = max(arg1, 0)\n'
    azlpv__qqm += "res[i] = format(arg0, f',.{prec}f')"
    cyk__ayzih = bodo.string_array_type
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


def left_util(arr, n_chars):
    return


def right_util(arr, n_chars):
    return


def create_left_right_util_overload(func_name):

    def overload_left_right_util(arr, n_chars):
        iftui__qarc = verify_string_binary_arg(arr, func_name, 'arr')
        verify_int_arg(n_chars, func_name, 'n_chars')
        xcs__zlsbs = "''" if iftui__qarc else "b''"
        xrutd__vfe = ['arr', 'n_chars']
        uxbp__oka = [arr, n_chars]
        ghnsj__nemnb = [True] * 2
        azlpv__qqm = 'if arg1 <= 0:\n'
        azlpv__qqm += f'   res[i] = {xcs__zlsbs}\n'
        azlpv__qqm += 'else:\n'
        if func_name == 'LEFT':
            azlpv__qqm += '   res[i] = arg0[:arg1]'
        elif func_name == 'RIGHT':
            azlpv__qqm += '   res[i] = arg0[-arg1:]'
        cyk__ayzih = (bodo.string_array_type if iftui__qarc else bodo.
            binary_array_type)
        return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb,
            azlpv__qqm, cyk__ayzih)
    return overload_left_right_util


def _install_left_right_overload():
    for mzrd__sgw, func_name in zip((left_util, right_util), ('LEFT', 'RIGHT')
        ):
        wbay__dyek = create_left_right_util_overload(func_name)
        overload(mzrd__sgw)(wbay__dyek)


_install_left_right_overload()


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        ubaa__jhj = verify_string_binary_arg(pad_string, func_name,
            'pad_string')
        iftui__qarc = verify_string_binary_arg(arr, func_name, 'arr')
        if iftui__qarc != ubaa__jhj:
            raise bodo.utils.typing.BodoError(
                'Pad string and arr must be the same type!')
        cyk__ayzih = (bodo.string_array_type if iftui__qarc else bodo.
            binary_array_type)
        verify_int_arg(length, func_name, 'length')
        verify_string_binary_arg(pad_string, func_name,
            f'{func_name.lower()}_string')
        if func_name == 'LPAD':
            uyf__uqv = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            uyf__uqv = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        xrutd__vfe = ['arr', 'length', 'pad_string']
        uxbp__oka = [arr, length, pad_string]
        ghnsj__nemnb = [True] * 3
        xcs__zlsbs = "''" if iftui__qarc else "b''"
        azlpv__qqm = f"""                if arg1 <= 0:
                    res[i] = {xcs__zlsbs}
                elif len(arg2) == 0:
                    res[i] = arg0
                elif len(arg0) >= arg1:
                    res[i] = arg0[:arg1]
                else:
                    quotient = (arg1 - len(arg0)) // len(arg2)
                    remainder = (arg1 - len(arg0)) % len(arg2)
                    res[i] = {uyf__uqv}"""
        return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb,
            azlpv__qqm, cyk__ayzih)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for mzrd__sgw, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')):
        wbay__dyek = create_lpad_rpad_util_overload(func_name)
        overload(mzrd__sgw)(wbay__dyek)


_install_lpad_rpad_overload()


@numba.generated_jit(nopython=True)
def ord_ascii_util(arr):
    verify_string_arg(arr, 'ORD', 'arr')
    xrutd__vfe = ['arr']
    uxbp__oka = [arr]
    ghnsj__nemnb = [True]
    azlpv__qqm = 'if len(arg0) == 0:\n'
    azlpv__qqm += '   bodo.libs.array_kernels.setna(res, i)\n'
    azlpv__qqm += 'else:\n'
    azlpv__qqm += '   res[i] = ord(arg0[0])'
    cyk__ayzih = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def repeat_util(arr, repeats):
    verify_string_arg(arr, 'REPEAT', 'arr')
    verify_int_arg(repeats, 'REPEAT', 'repeats')
    xrutd__vfe = ['arr', 'repeats']
    uxbp__oka = [arr, repeats]
    ghnsj__nemnb = [True] * 2
    azlpv__qqm = 'if arg1 <= 0:\n'
    azlpv__qqm += "   res[i] = ''\n"
    azlpv__qqm += 'else:\n'
    azlpv__qqm += '   res[i] = arg0 * arg1'
    cyk__ayzih = bodo.string_array_type
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def replace_util(arr, to_replace, replace_with):
    verify_string_arg(arr, 'REPLACE', 'arr')
    verify_string_arg(to_replace, 'REPLACE', 'to_replace')
    verify_string_arg(replace_with, 'REPLACE', 'replace_with')
    xrutd__vfe = ['arr', 'to_replace', 'replace_with']
    uxbp__oka = [arr, to_replace, replace_with]
    ghnsj__nemnb = [True] * 3
    azlpv__qqm = "if arg1 == '':\n"
    azlpv__qqm += '   res[i] = arg0\n'
    azlpv__qqm += 'else:\n'
    azlpv__qqm += '   res[i] = arg0.replace(arg1, arg2)'
    cyk__ayzih = bodo.string_array_type
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def reverse_util(arr):
    iftui__qarc = verify_string_binary_arg(arr, 'REVERSE', 'arr')
    xrutd__vfe = ['arr']
    uxbp__oka = [arr]
    ghnsj__nemnb = [True]
    azlpv__qqm = 'res[i] = arg0[::-1]'
    cyk__ayzih = bodo.string_array_type
    cyk__ayzih = (bodo.string_array_type if iftui__qarc else bodo.
        binary_array_type)
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def space_util(n_chars):
    verify_int_arg(n_chars, 'SPACE', 'n_chars')
    xrutd__vfe = ['n_chars']
    uxbp__oka = [n_chars]
    ghnsj__nemnb = [True]
    azlpv__qqm = 'if arg0 <= 0:\n'
    azlpv__qqm += "   res[i] = ''\n"
    azlpv__qqm += 'else:\n'
    azlpv__qqm += "   res[i] = ' ' * arg0"
    cyk__ayzih = bodo.string_array_type
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def strcmp_util(arr0, arr1):
    verify_string_arg(arr0, 'strcmp', 'arr0')
    verify_string_arg(arr1, 'strcmp', 'arr1')
    xrutd__vfe = ['arr0', 'arr1']
    uxbp__oka = [arr0, arr1]
    ghnsj__nemnb = [True] * 2
    azlpv__qqm = 'if arg0 < arg1:\n'
    azlpv__qqm += '   res[i] = -1\n'
    azlpv__qqm += 'elif arg0 > arg1:\n'
    azlpv__qqm += '   res[i] = 1\n'
    azlpv__qqm += 'else:\n'
    azlpv__qqm += '   res[i] = 0\n'
    cyk__ayzih = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def substring_util(arr, start, length):
    iftui__qarc = verify_string_binary_arg(arr, 'SUBSTRING', 'arr')
    verify_int_arg(start, 'SUBSTRING', 'start')
    verify_int_arg(length, 'SUBSTRING', 'length')
    cyk__ayzih = (bodo.string_array_type if iftui__qarc else bodo.
        binary_array_type)
    xrutd__vfe = ['arr', 'start', 'length']
    uxbp__oka = [arr, start, length]
    ghnsj__nemnb = [True] * 3
    azlpv__qqm = 'if arg2 <= 0:\n'
    azlpv__qqm += "   res[i] = ''\n" if iftui__qarc else "   res[i] = b''\n"
    azlpv__qqm += 'elif arg1 < 0 and arg1 + arg2 >= 0:\n'
    azlpv__qqm += '   res[i] = arg0[arg1:]\n'
    azlpv__qqm += 'else:\n'
    azlpv__qqm += '   if arg1 > 0: arg1 -= 1\n'
    azlpv__qqm += '   res[i] = arg0[arg1:arg1+arg2]\n'
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)


@numba.generated_jit(nopython=True)
def substring_index_util(arr, delimiter, occurrences):
    verify_string_arg(arr, 'SUBSTRING_INDEX', 'arr')
    verify_string_arg(delimiter, 'SUBSTRING_INDEX', 'delimiter')
    verify_int_arg(occurrences, 'SUBSTRING_INDEX', 'occurrences')
    xrutd__vfe = ['arr', 'delimiter', 'occurrences']
    uxbp__oka = [arr, delimiter, occurrences]
    ghnsj__nemnb = [True] * 3
    azlpv__qqm = "if arg1 == '' or arg2 == 0:\n"
    azlpv__qqm += "   res[i] = ''\n"
    azlpv__qqm += 'elif arg2 >= 0:\n'
    azlpv__qqm += '   res[i] = arg1.join(arg0.split(arg1, arg2+1)[:arg2])\n'
    azlpv__qqm += 'else:\n'
    azlpv__qqm += '   res[i] = arg1.join(arg0.split(arg1)[arg2:])\n'
    cyk__ayzih = bodo.string_array_type
    return gen_vectorized(xrutd__vfe, uxbp__oka, ghnsj__nemnb, azlpv__qqm,
        cyk__ayzih)
