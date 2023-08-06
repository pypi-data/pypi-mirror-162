"""
Implements string array kernels that are specific to BodoSQL
"""
import numba
from numba.core import types
from numba.extending import overload
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
def format(arr, places):
    args = [arr, places]
    for nxqge__klts in range(2):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.format',
                ['arr', 'places'], nxqge__klts)

    def impl(arr, places):
        return format_util(arr, places)
    return impl


@numba.generated_jit(nopython=True)
def instr(arr, target):
    args = [arr, target]
    for nxqge__klts in range(2):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.instr',
                ['arr', 'target'], nxqge__klts)

    def impl(arr, target):
        return instr_util(arr, target)
    return impl


def left(arr, n_chars):
    return


@overload(left)
def overload_left(arr, n_chars):
    args = [arr, n_chars]
    for nxqge__klts in range(2):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.left', [
                'arr', 'n_chars'], nxqge__klts)

    def impl(arr, n_chars):
        return left_util(arr, n_chars)
    return impl


def lpad(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for nxqge__klts in range(3):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], nxqge__klts)

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
    for nxqge__klts in range(2):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.repeat',
                ['arr', 'repeats'], nxqge__klts)

    def impl(arr, repeats):
        return repeat_util(arr, repeats)
    return impl


@numba.generated_jit(nopython=True)
def replace(arr, to_replace, replace_with):
    args = [arr, to_replace, replace_with]
    for nxqge__klts in range(3):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.replace',
                ['arr', 'to_replace', 'replace_with'], nxqge__klts)

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
    for nxqge__klts in range(2):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.right',
                ['arr', 'n_chars'], nxqge__klts)

    def impl(arr, n_chars):
        return right_util(arr, n_chars)
    return impl


def rpad(arr, length, padstr):
    return


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for nxqge__klts in range(3):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], nxqge__klts)

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
    for nxqge__klts in range(2):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strcmp',
                ['arr0', 'arr1'], nxqge__klts)

    def impl(arr0, arr1):
        return strcmp_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def substring(arr, start, length):
    args = [arr, start, length]
    for nxqge__klts in range(3):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.substring',
                ['arr', 'start', 'length'], nxqge__klts)

    def impl(arr, start, length):
        return substring_util(arr, start, length)
    return impl


@numba.generated_jit(nopython=True)
def substring_index(arr, delimiter, occurrences):
    args = [arr, delimiter, occurrences]
    for nxqge__klts in range(3):
        if isinstance(args[nxqge__klts], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.substring_index', ['arr',
                'delimiter', 'occurrences'], nxqge__klts)

    def impl(arr, delimiter, occurrences):
        return substring_index_util(arr, delimiter, occurrences)
    return impl


@numba.generated_jit(nopython=True)
def char_util(arr):
    verify_int_arg(arr, 'CHAR', 'arr')
    zobc__wekc = ['arr']
    gxrw__etg = [arr]
    pqrx__mkah = [True]
    hacy__lchh = 'if 0 <= arg0 <= 127:\n'
    hacy__lchh += '   res[i] = chr(arg0)\n'
    hacy__lchh += 'else:\n'
    hacy__lchh += '   bodo.libs.array_kernels.setna(res, i)\n'
    rrbg__bdc = bodo.string_array_type
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def instr_util(arr, target):
    verify_string_arg(arr, 'instr', 'arr')
    verify_string_arg(target, 'instr', 'target')
    zobc__wekc = ['arr', 'target']
    gxrw__etg = [arr, target]
    pqrx__mkah = [True] * 2
    hacy__lchh = 'res[i] = arg0.find(arg1) + 1'
    rrbg__bdc = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def format_util(arr, places):
    verify_int_float_arg(arr, 'FORMAT', 'arr')
    verify_int_arg(places, 'FORMAT', 'places')
    zobc__wekc = ['arr', 'places']
    gxrw__etg = [arr, places]
    pqrx__mkah = [True] * 2
    hacy__lchh = 'prec = max(arg1, 0)\n'
    hacy__lchh += "res[i] = format(arg0, f',.{prec}f')"
    rrbg__bdc = bodo.string_array_type
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


def left_util(arr, n_chars):
    return


def right_util(arr, n_chars):
    return


def create_left_right_util_overload(func_name):

    def overload_left_right_util(arr, n_chars):
        verify_string_arg(arr, func_name, 'arr')
        verify_int_arg(n_chars, func_name, 'n_chars')
        zobc__wekc = ['arr', 'n_chars']
        gxrw__etg = [arr, n_chars]
        pqrx__mkah = [True] * 2
        hacy__lchh = 'if arg1 <= 0:\n'
        hacy__lchh += "   res[i] = ''\n"
        hacy__lchh += 'else:\n'
        if func_name == 'LEFT':
            hacy__lchh += '   res[i] = arg0[:arg1]'
        elif func_name == 'RIGHT':
            hacy__lchh += '   res[i] = arg0[-arg1:]'
        rrbg__bdc = bodo.string_array_type
        return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
            rrbg__bdc)
    return overload_left_right_util


def _install_left_right_overload():
    for offhw__bhe, func_name in zip((left_util, right_util), ('LEFT', 'RIGHT')
        ):
        iuadg__duw = create_left_right_util_overload(func_name)
        overload(offhw__bhe)(iuadg__duw)


_install_left_right_overload()


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        verify_string_arg(arr, func_name, 'arr')
        verify_int_arg(length, func_name, 'length')
        verify_string_arg(pad_string, func_name, f'{func_name.lower()}_string')
        if func_name == 'LPAD':
            papxz__rxgju = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            papxz__rxgju = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        zobc__wekc = ['arr', 'length', 'pad_string']
        gxrw__etg = [arr, length, pad_string]
        pqrx__mkah = [True] * 3
        hacy__lchh = f"""            if arg1 <= 0:
                res[i] =  ''
            elif len(arg2) == 0:
                res[i] = arg0
            elif len(arg0) >= arg1:
                res[i] = arg0[:arg1]
            else:
                quotient = (arg1 - len(arg0)) // len(arg2)
                remainder = (arg1 - len(arg0)) % len(arg2)
                res[i] = {papxz__rxgju}"""
        rrbg__bdc = bodo.string_array_type
        return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
            rrbg__bdc)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for offhw__bhe, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')):
        iuadg__duw = create_lpad_rpad_util_overload(func_name)
        overload(offhw__bhe)(iuadg__duw)


_install_lpad_rpad_overload()


@numba.generated_jit(nopython=True)
def ord_ascii_util(arr):
    verify_string_arg(arr, 'ORD', 'arr')
    zobc__wekc = ['arr']
    gxrw__etg = [arr]
    pqrx__mkah = [True]
    hacy__lchh = 'if len(arg0) == 0:\n'
    hacy__lchh += '   bodo.libs.array_kernels.setna(res, i)\n'
    hacy__lchh += 'else:\n'
    hacy__lchh += '   res[i] = ord(arg0[0])'
    rrbg__bdc = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def repeat_util(arr, repeats):
    verify_string_arg(arr, 'REPEAT', 'arr')
    verify_int_arg(repeats, 'REPEAT', 'repeats')
    zobc__wekc = ['arr', 'repeats']
    gxrw__etg = [arr, repeats]
    pqrx__mkah = [True] * 2
    hacy__lchh = 'if arg1 <= 0:\n'
    hacy__lchh += "   res[i] = ''\n"
    hacy__lchh += 'else:\n'
    hacy__lchh += '   res[i] = arg0 * arg1'
    rrbg__bdc = bodo.string_array_type
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def replace_util(arr, to_replace, replace_with):
    verify_string_arg(arr, 'REPLACE', 'arr')
    verify_string_arg(to_replace, 'REPLACE', 'to_replace')
    verify_string_arg(replace_with, 'REPLACE', 'replace_with')
    zobc__wekc = ['arr', 'to_replace', 'replace_with']
    gxrw__etg = [arr, to_replace, replace_with]
    pqrx__mkah = [True] * 3
    hacy__lchh = "if arg1 == '':\n"
    hacy__lchh += '   res[i] = arg0\n'
    hacy__lchh += 'else:\n'
    hacy__lchh += '   res[i] = arg0.replace(arg1, arg2)'
    rrbg__bdc = bodo.string_array_type
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def reverse_util(arr):
    verify_string_arg(arr, 'REVERSE', 'arr')
    zobc__wekc = ['arr']
    gxrw__etg = [arr]
    pqrx__mkah = [True]
    hacy__lchh = 'res[i] = arg0[::-1]'
    rrbg__bdc = bodo.string_array_type
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def space_util(n_chars):
    verify_int_arg(n_chars, 'SPACE', 'n_chars')
    zobc__wekc = ['n_chars']
    gxrw__etg = [n_chars]
    pqrx__mkah = [True]
    hacy__lchh = 'if arg0 <= 0:\n'
    hacy__lchh += "   res[i] = ''\n"
    hacy__lchh += 'else:\n'
    hacy__lchh += "   res[i] = ' ' * arg0"
    rrbg__bdc = bodo.string_array_type
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def strcmp_util(arr0, arr1):
    verify_string_arg(arr0, 'strcmp', 'arr0')
    verify_string_arg(arr1, 'strcmp', 'arr1')
    zobc__wekc = ['arr0', 'arr1']
    gxrw__etg = [arr0, arr1]
    pqrx__mkah = [True] * 2
    hacy__lchh = 'if arg0 < arg1:\n'
    hacy__lchh += '   res[i] = -1\n'
    hacy__lchh += 'elif arg0 > arg1:\n'
    hacy__lchh += '   res[i] = 1\n'
    hacy__lchh += 'else:\n'
    hacy__lchh += '   res[i] = 0\n'
    rrbg__bdc = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def substring_util(arr, start, length):
    verify_string_arg(arr, 'SUBSTRING', 'arr')
    verify_int_arg(start, 'SUBSTRING', 'start')
    verify_int_arg(length, 'SUBSTRING', 'length')
    zobc__wekc = ['arr', 'start', 'length']
    gxrw__etg = [arr, start, length]
    pqrx__mkah = [True] * 3
    hacy__lchh = 'if arg2 <= 0:\n'
    hacy__lchh += "   res[i] = ''\n"
    hacy__lchh += 'elif arg1 < 0 and arg1 + arg2 >= 0:\n'
    hacy__lchh += '   res[i] = arg0[arg1:]\n'
    hacy__lchh += 'else:\n'
    hacy__lchh += '   if arg1 > 0: arg1 -= 1\n'
    hacy__lchh += '   res[i] = arg0[arg1:arg1+arg2]\n'
    rrbg__bdc = bodo.string_array_type
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)


@numba.generated_jit(nopython=True)
def substring_index_util(arr, delimiter, occurrences):
    verify_string_arg(arr, 'SUBSTRING_INDEX', 'arr')
    verify_string_arg(delimiter, 'SUBSTRING_INDEX', 'delimiter')
    verify_int_arg(occurrences, 'SUBSTRING_INDEX', 'occurrences')
    zobc__wekc = ['arr', 'delimiter', 'occurrences']
    gxrw__etg = [arr, delimiter, occurrences]
    pqrx__mkah = [True] * 3
    hacy__lchh = "if arg1 == '' or arg2 == 0:\n"
    hacy__lchh += "   res[i] = ''\n"
    hacy__lchh += 'elif arg2 >= 0:\n'
    hacy__lchh += '   res[i] = arg1.join(arg0.split(arg1, arg2+1)[:arg2])\n'
    hacy__lchh += 'else:\n'
    hacy__lchh += '   res[i] = arg1.join(arg0.split(arg1)[arg2:])\n'
    rrbg__bdc = bodo.string_array_type
    return gen_vectorized(zobc__wekc, gxrw__etg, pqrx__mkah, hacy__lchh,
        rrbg__bdc)
