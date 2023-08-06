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
    for xawk__sskkn in range(2):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.format',
                ['arr', 'places'], xawk__sskkn)

    def impl(arr, places):
        return format_util(arr, places)
    return impl


@numba.generated_jit(nopython=True)
def instr(arr, target):
    args = [arr, target]
    for xawk__sskkn in range(2):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.instr',
                ['arr', 'target'], xawk__sskkn)

    def impl(arr, target):
        return instr_util(arr, target)
    return impl


def left(arr, n_chars):
    return


@overload(left)
def overload_left(arr, n_chars):
    args = [arr, n_chars]
    for xawk__sskkn in range(2):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.left', [
                'arr', 'n_chars'], xawk__sskkn)

    def impl(arr, n_chars):
        return left_util(arr, n_chars)
    return impl


def lpad(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for xawk__sskkn in range(3):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], xawk__sskkn)

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
    for xawk__sskkn in range(2):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.repeat',
                ['arr', 'repeats'], xawk__sskkn)

    def impl(arr, repeats):
        return repeat_util(arr, repeats)
    return impl


@numba.generated_jit(nopython=True)
def replace(arr, to_replace, replace_with):
    args = [arr, to_replace, replace_with]
    for xawk__sskkn in range(3):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.replace',
                ['arr', 'to_replace', 'replace_with'], xawk__sskkn)

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
    for xawk__sskkn in range(2):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.right',
                ['arr', 'n_chars'], xawk__sskkn)

    def impl(arr, n_chars):
        return right_util(arr, n_chars)
    return impl


def rpad(arr, length, padstr):
    return


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for xawk__sskkn in range(3):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], xawk__sskkn)

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
    for xawk__sskkn in range(2):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strcmp',
                ['arr0', 'arr1'], xawk__sskkn)

    def impl(arr0, arr1):
        return strcmp_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def substring(arr, start, length):
    args = [arr, start, length]
    for xawk__sskkn in range(3):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.substring',
                ['arr', 'start', 'length'], xawk__sskkn)

    def impl(arr, start, length):
        return substring_util(arr, start, length)
    return impl


@numba.generated_jit(nopython=True)
def substring_index(arr, delimiter, occurrences):
    args = [arr, delimiter, occurrences]
    for xawk__sskkn in range(3):
        if isinstance(args[xawk__sskkn], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.substring_index', ['arr',
                'delimiter', 'occurrences'], xawk__sskkn)

    def impl(arr, delimiter, occurrences):
        return substring_index_util(arr, delimiter, occurrences)
    return impl


@numba.generated_jit(nopython=True)
def char_util(arr):
    verify_int_arg(arr, 'CHAR', 'arr')
    did__dqiqj = ['arr']
    lgsn__ywx = [arr]
    jib__tzqbk = [True]
    moefy__ysw = 'if 0 <= arg0 <= 127:\n'
    moefy__ysw += '   res[i] = chr(arg0)\n'
    moefy__ysw += 'else:\n'
    moefy__ysw += '   bodo.libs.array_kernels.setna(res, i)\n'
    vngx__tcxu = bodo.string_array_type
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def instr_util(arr, target):
    verify_string_arg(arr, 'instr', 'arr')
    verify_string_arg(target, 'instr', 'target')
    did__dqiqj = ['arr', 'target']
    lgsn__ywx = [arr, target]
    jib__tzqbk = [True] * 2
    moefy__ysw = 'res[i] = arg0.find(arg1) + 1'
    vngx__tcxu = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def format_util(arr, places):
    verify_int_float_arg(arr, 'FORMAT', 'arr')
    verify_int_arg(places, 'FORMAT', 'places')
    did__dqiqj = ['arr', 'places']
    lgsn__ywx = [arr, places]
    jib__tzqbk = [True] * 2
    moefy__ysw = 'prec = max(arg1, 0)\n'
    moefy__ysw += "res[i] = format(arg0, f',.{prec}f')"
    vngx__tcxu = bodo.string_array_type
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


def left_util(arr, n_chars):
    return


def right_util(arr, n_chars):
    return


def create_left_right_util_overload(func_name):

    def overload_left_right_util(arr, n_chars):
        verify_string_arg(arr, func_name, 'arr')
        verify_int_arg(n_chars, func_name, 'n_chars')
        did__dqiqj = ['arr', 'n_chars']
        lgsn__ywx = [arr, n_chars]
        jib__tzqbk = [True] * 2
        moefy__ysw = 'if arg1 <= 0:\n'
        moefy__ysw += "   res[i] = ''\n"
        moefy__ysw += 'else:\n'
        if func_name == 'LEFT':
            moefy__ysw += '   res[i] = arg0[:arg1]'
        elif func_name == 'RIGHT':
            moefy__ysw += '   res[i] = arg0[-arg1:]'
        vngx__tcxu = bodo.string_array_type
        return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
            vngx__tcxu)
    return overload_left_right_util


def _install_left_right_overload():
    for dsgo__rekdy, func_name in zip((left_util, right_util), ('LEFT',
        'RIGHT')):
        qax__eoff = create_left_right_util_overload(func_name)
        overload(dsgo__rekdy)(qax__eoff)


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
            qlmy__fpvdw = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            qlmy__fpvdw = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        did__dqiqj = ['arr', 'length', 'pad_string']
        lgsn__ywx = [arr, length, pad_string]
        jib__tzqbk = [True] * 3
        moefy__ysw = f"""            if arg1 <= 0:
                res[i] =  ''
            elif len(arg2) == 0:
                res[i] = arg0
            elif len(arg0) >= arg1:
                res[i] = arg0[:arg1]
            else:
                quotient = (arg1 - len(arg0)) // len(arg2)
                remainder = (arg1 - len(arg0)) % len(arg2)
                res[i] = {qlmy__fpvdw}"""
        vngx__tcxu = bodo.string_array_type
        return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
            vngx__tcxu)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for dsgo__rekdy, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')
        ):
        qax__eoff = create_lpad_rpad_util_overload(func_name)
        overload(dsgo__rekdy)(qax__eoff)


_install_lpad_rpad_overload()


@numba.generated_jit(nopython=True)
def ord_ascii_util(arr):
    verify_string_arg(arr, 'ORD', 'arr')
    did__dqiqj = ['arr']
    lgsn__ywx = [arr]
    jib__tzqbk = [True]
    moefy__ysw = 'if len(arg0) == 0:\n'
    moefy__ysw += '   bodo.libs.array_kernels.setna(res, i)\n'
    moefy__ysw += 'else:\n'
    moefy__ysw += '   res[i] = ord(arg0[0])'
    vngx__tcxu = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def repeat_util(arr, repeats):
    verify_string_arg(arr, 'REPEAT', 'arr')
    verify_int_arg(repeats, 'REPEAT', 'repeats')
    did__dqiqj = ['arr', 'repeats']
    lgsn__ywx = [arr, repeats]
    jib__tzqbk = [True] * 2
    moefy__ysw = 'if arg1 <= 0:\n'
    moefy__ysw += "   res[i] = ''\n"
    moefy__ysw += 'else:\n'
    moefy__ysw += '   res[i] = arg0 * arg1'
    vngx__tcxu = bodo.string_array_type
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def replace_util(arr, to_replace, replace_with):
    verify_string_arg(arr, 'REPLACE', 'arr')
    verify_string_arg(to_replace, 'REPLACE', 'to_replace')
    verify_string_arg(replace_with, 'REPLACE', 'replace_with')
    did__dqiqj = ['arr', 'to_replace', 'replace_with']
    lgsn__ywx = [arr, to_replace, replace_with]
    jib__tzqbk = [True] * 3
    moefy__ysw = "if arg1 == '':\n"
    moefy__ysw += '   res[i] = arg0\n'
    moefy__ysw += 'else:\n'
    moefy__ysw += '   res[i] = arg0.replace(arg1, arg2)'
    vngx__tcxu = bodo.string_array_type
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def reverse_util(arr):
    verify_string_arg(arr, 'REVERSE', 'arr')
    did__dqiqj = ['arr']
    lgsn__ywx = [arr]
    jib__tzqbk = [True]
    moefy__ysw = 'res[i] = arg0[::-1]'
    vngx__tcxu = bodo.string_array_type
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def space_util(n_chars):
    verify_int_arg(n_chars, 'SPACE', 'n_chars')
    did__dqiqj = ['n_chars']
    lgsn__ywx = [n_chars]
    jib__tzqbk = [True]
    moefy__ysw = 'if arg0 <= 0:\n'
    moefy__ysw += "   res[i] = ''\n"
    moefy__ysw += 'else:\n'
    moefy__ysw += "   res[i] = ' ' * arg0"
    vngx__tcxu = bodo.string_array_type
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def strcmp_util(arr0, arr1):
    verify_string_arg(arr0, 'strcmp', 'arr0')
    verify_string_arg(arr1, 'strcmp', 'arr1')
    did__dqiqj = ['arr0', 'arr1']
    lgsn__ywx = [arr0, arr1]
    jib__tzqbk = [True] * 2
    moefy__ysw = 'if arg0 < arg1:\n'
    moefy__ysw += '   res[i] = -1\n'
    moefy__ysw += 'elif arg0 > arg1:\n'
    moefy__ysw += '   res[i] = 1\n'
    moefy__ysw += 'else:\n'
    moefy__ysw += '   res[i] = 0\n'
    vngx__tcxu = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def substring_util(arr, start, length):
    verify_string_arg(arr, 'SUBSTRING', 'arr')
    verify_int_arg(start, 'SUBSTRING', 'start')
    verify_int_arg(length, 'SUBSTRING', 'length')
    did__dqiqj = ['arr', 'start', 'length']
    lgsn__ywx = [arr, start, length]
    jib__tzqbk = [True] * 3
    moefy__ysw = 'if arg2 <= 0:\n'
    moefy__ysw += "   res[i] = ''\n"
    moefy__ysw += 'elif arg1 < 0 and arg1 + arg2 >= 0:\n'
    moefy__ysw += '   res[i] = arg0[arg1:]\n'
    moefy__ysw += 'else:\n'
    moefy__ysw += '   if arg1 > 0: arg1 -= 1\n'
    moefy__ysw += '   res[i] = arg0[arg1:arg1+arg2]\n'
    vngx__tcxu = bodo.string_array_type
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)


@numba.generated_jit(nopython=True)
def substring_index_util(arr, delimiter, occurrences):
    verify_string_arg(arr, 'SUBSTRING_INDEX', 'arr')
    verify_string_arg(delimiter, 'SUBSTRING_INDEX', 'delimiter')
    verify_int_arg(occurrences, 'SUBSTRING_INDEX', 'occurrences')
    did__dqiqj = ['arr', 'delimiter', 'occurrences']
    lgsn__ywx = [arr, delimiter, occurrences]
    jib__tzqbk = [True] * 3
    moefy__ysw = "if arg1 == '' or arg2 == 0:\n"
    moefy__ysw += "   res[i] = ''\n"
    moefy__ysw += 'elif arg2 >= 0:\n'
    moefy__ysw += '   res[i] = arg1.join(arg0.split(arg1, arg2+1)[:arg2])\n'
    moefy__ysw += 'else:\n'
    moefy__ysw += '   res[i] = arg1.join(arg0.split(arg1)[arg2:])\n'
    vngx__tcxu = bodo.string_array_type
    return gen_vectorized(did__dqiqj, lgsn__ywx, jib__tzqbk, moefy__ysw,
        vngx__tcxu)
