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
    for izhcv__wetur in range(2):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_no_max', ['s',
                't'], izhcv__wetur)

    def impl(s, t):
        return editdistance_no_max_util(s, t)
    return impl


@numba.generated_jit(nopython=True)
def editdistance_with_max(s, t, maxDistance):
    args = [s, t, maxDistance]
    for izhcv__wetur in range(3):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_with_max', [
                's', 't', 'maxDistance'], izhcv__wetur)

    def impl(s, t, maxDistance):
        return editdistance_with_max_util(s, t, maxDistance)
    return impl


@numba.generated_jit(nopython=True)
def format(arr, places):
    args = [arr, places]
    for izhcv__wetur in range(2):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.format',
                ['arr', 'places'], izhcv__wetur)

    def impl(arr, places):
        return format_util(arr, places)
    return impl


@numba.generated_jit(nopython=True)
def instr(arr, target):
    args = [arr, target]
    for izhcv__wetur in range(2):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.instr',
                ['arr', 'target'], izhcv__wetur)

    def impl(arr, target):
        return instr_util(arr, target)
    return impl


def left(arr, n_chars):
    return


@overload(left)
def overload_left(arr, n_chars):
    args = [arr, n_chars]
    for izhcv__wetur in range(2):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.left', [
                'arr', 'n_chars'], izhcv__wetur)

    def impl(arr, n_chars):
        return left_util(arr, n_chars)
    return impl


def lpad(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for izhcv__wetur in range(3):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], izhcv__wetur)

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
    for izhcv__wetur in range(2):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.repeat',
                ['arr', 'repeats'], izhcv__wetur)

    def impl(arr, repeats):
        return repeat_util(arr, repeats)
    return impl


@numba.generated_jit(nopython=True)
def replace(arr, to_replace, replace_with):
    args = [arr, to_replace, replace_with]
    for izhcv__wetur in range(3):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.replace',
                ['arr', 'to_replace', 'replace_with'], izhcv__wetur)

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
    for izhcv__wetur in range(2):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.right',
                ['arr', 'n_chars'], izhcv__wetur)

    def impl(arr, n_chars):
        return right_util(arr, n_chars)
    return impl


def rpad(arr, length, padstr):
    return


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for izhcv__wetur in range(3):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], izhcv__wetur)

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
    for izhcv__wetur in range(2):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strcmp',
                ['arr0', 'arr1'], izhcv__wetur)

    def impl(arr0, arr1):
        return strcmp_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def substring(arr, start, length):
    args = [arr, start, length]
    for izhcv__wetur in range(3):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.substring',
                ['arr', 'start', 'length'], izhcv__wetur)

    def impl(arr, start, length):
        return substring_util(arr, start, length)
    return impl


@numba.generated_jit(nopython=True)
def substring_index(arr, delimiter, occurrences):
    args = [arr, delimiter, occurrences]
    for izhcv__wetur in range(3):
        if isinstance(args[izhcv__wetur], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.substring_index', ['arr',
                'delimiter', 'occurrences'], izhcv__wetur)

    def impl(arr, delimiter, occurrences):
        return substring_index_util(arr, delimiter, occurrences)
    return impl


@numba.generated_jit(nopython=True)
def char_util(arr):
    verify_int_arg(arr, 'CHAR', 'arr')
    org__pkv = ['arr']
    fnym__fkold = [arr]
    bkh__cpfrp = [True]
    toaid__cwd = 'if 0 <= arg0 <= 127:\n'
    toaid__cwd += '   res[i] = chr(arg0)\n'
    toaid__cwd += 'else:\n'
    toaid__cwd += '   bodo.libs.array_kernels.setna(res, i)\n'
    llklu__zbz = bodo.string_array_type
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def instr_util(arr, target):
    verify_string_arg(arr, 'instr', 'arr')
    verify_string_arg(target, 'instr', 'target')
    org__pkv = ['arr', 'target']
    fnym__fkold = [arr, target]
    bkh__cpfrp = [True] * 2
    toaid__cwd = 'res[i] = arg0.find(arg1) + 1'
    llklu__zbz = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@register_jitable
def min_edit_distance(s, t):
    if len(s) > len(t):
        s, t = t, s
    mua__jkc, hfiot__cych = len(s), len(t)
    cld__ijkt, vsa__kgs = 1, 0
    arr = np.zeros((2, mua__jkc + 1), dtype=np.uint32)
    arr[0, :] = np.arange(mua__jkc + 1)
    for izhcv__wetur in range(1, hfiot__cych + 1):
        arr[cld__ijkt, 0] = izhcv__wetur
        for japy__wbd in range(1, mua__jkc + 1):
            if s[japy__wbd - 1] == t[izhcv__wetur - 1]:
                arr[cld__ijkt, japy__wbd] = arr[vsa__kgs, japy__wbd - 1]
            else:
                arr[cld__ijkt, japy__wbd] = 1 + min(arr[cld__ijkt, 
                    japy__wbd - 1], arr[vsa__kgs, japy__wbd], arr[vsa__kgs,
                    japy__wbd - 1])
        cld__ijkt, vsa__kgs = vsa__kgs, cld__ijkt
    return arr[hfiot__cych % 2, mua__jkc]


@register_jitable
def min_edit_distance_with_max(s, t, maxDistance):
    if maxDistance < 0:
        return 0
    if len(s) > len(t):
        s, t = t, s
    mua__jkc, hfiot__cych = len(s), len(t)
    if mua__jkc <= maxDistance and hfiot__cych <= maxDistance:
        return min_edit_distance(s, t)
    cld__ijkt, vsa__kgs = 1, 0
    arr = np.zeros((2, mua__jkc + 1), dtype=np.uint32)
    arr[0, :] = np.arange(mua__jkc + 1)
    for izhcv__wetur in range(1, hfiot__cych + 1):
        arr[cld__ijkt, 0] = izhcv__wetur
        for japy__wbd in range(1, mua__jkc + 1):
            if s[japy__wbd - 1] == t[izhcv__wetur - 1]:
                arr[cld__ijkt, japy__wbd] = arr[vsa__kgs, japy__wbd - 1]
            else:
                arr[cld__ijkt, japy__wbd] = 1 + min(arr[cld__ijkt, 
                    japy__wbd - 1], arr[vsa__kgs, japy__wbd], arr[vsa__kgs,
                    japy__wbd - 1])
        if (arr[cld__ijkt] >= maxDistance).all():
            return maxDistance
        cld__ijkt, vsa__kgs = vsa__kgs, cld__ijkt
    return min(arr[hfiot__cych % 2, mua__jkc], maxDistance)


@numba.generated_jit(nopython=True)
def editdistance_no_max_util(s, t):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    org__pkv = ['s', 't']
    fnym__fkold = [s, t]
    bkh__cpfrp = [True] * 2
    toaid__cwd = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance(arg0, arg1)'
        )
    llklu__zbz = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def editdistance_with_max_util(s, t, maxDistance):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    verify_int_arg(maxDistance, 'editdistance_no_max', 't')
    org__pkv = ['s', 't', 'maxDistance']
    fnym__fkold = [s, t, maxDistance]
    bkh__cpfrp = [True] * 3
    toaid__cwd = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance_with_max(arg0, arg1, arg2)'
        )
    llklu__zbz = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def format_util(arr, places):
    verify_int_float_arg(arr, 'FORMAT', 'arr')
    verify_int_arg(places, 'FORMAT', 'places')
    org__pkv = ['arr', 'places']
    fnym__fkold = [arr, places]
    bkh__cpfrp = [True] * 2
    toaid__cwd = 'prec = max(arg1, 0)\n'
    toaid__cwd += "res[i] = format(arg0, f',.{prec}f')"
    llklu__zbz = bodo.string_array_type
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


def left_util(arr, n_chars):
    return


def right_util(arr, n_chars):
    return


def create_left_right_util_overload(func_name):

    def overload_left_right_util(arr, n_chars):
        rypxj__khvf = verify_string_binary_arg(arr, func_name, 'arr')
        verify_int_arg(n_chars, func_name, 'n_chars')
        hjp__bhtet = "''" if rypxj__khvf else "b''"
        org__pkv = ['arr', 'n_chars']
        fnym__fkold = [arr, n_chars]
        bkh__cpfrp = [True] * 2
        toaid__cwd = 'if arg1 <= 0:\n'
        toaid__cwd += f'   res[i] = {hjp__bhtet}\n'
        toaid__cwd += 'else:\n'
        if func_name == 'LEFT':
            toaid__cwd += '   res[i] = arg0[:arg1]'
        elif func_name == 'RIGHT':
            toaid__cwd += '   res[i] = arg0[-arg1:]'
        llklu__zbz = (bodo.string_array_type if rypxj__khvf else bodo.
            binary_array_type)
        return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
            llklu__zbz)
    return overload_left_right_util


def _install_left_right_overload():
    for xqzv__vakyf, func_name in zip((left_util, right_util), ('LEFT',
        'RIGHT')):
        xlkky__qalhn = create_left_right_util_overload(func_name)
        overload(xqzv__vakyf)(xlkky__qalhn)


_install_left_right_overload()


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        aneto__vsfc = verify_string_binary_arg(pad_string, func_name,
            'pad_string')
        rypxj__khvf = verify_string_binary_arg(arr, func_name, 'arr')
        if rypxj__khvf != aneto__vsfc:
            raise bodo.utils.typing.BodoError(
                'Pad string and arr must be the same type!')
        llklu__zbz = (bodo.string_array_type if rypxj__khvf else bodo.
            binary_array_type)
        verify_int_arg(length, func_name, 'length')
        verify_string_binary_arg(pad_string, func_name,
            f'{func_name.lower()}_string')
        if func_name == 'LPAD':
            mbc__ogmr = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            mbc__ogmr = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        org__pkv = ['arr', 'length', 'pad_string']
        fnym__fkold = [arr, length, pad_string]
        bkh__cpfrp = [True] * 3
        hjp__bhtet = "''" if rypxj__khvf else "b''"
        toaid__cwd = f"""                if arg1 <= 0:
                    res[i] = {hjp__bhtet}
                elif len(arg2) == 0:
                    res[i] = arg0
                elif len(arg0) >= arg1:
                    res[i] = arg0[:arg1]
                else:
                    quotient = (arg1 - len(arg0)) // len(arg2)
                    remainder = (arg1 - len(arg0)) % len(arg2)
                    res[i] = {mbc__ogmr}"""
        return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
            llklu__zbz)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for xqzv__vakyf, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')
        ):
        xlkky__qalhn = create_lpad_rpad_util_overload(func_name)
        overload(xqzv__vakyf)(xlkky__qalhn)


_install_lpad_rpad_overload()


@numba.generated_jit(nopython=True)
def ord_ascii_util(arr):
    verify_string_arg(arr, 'ORD', 'arr')
    org__pkv = ['arr']
    fnym__fkold = [arr]
    bkh__cpfrp = [True]
    toaid__cwd = 'if len(arg0) == 0:\n'
    toaid__cwd += '   bodo.libs.array_kernels.setna(res, i)\n'
    toaid__cwd += 'else:\n'
    toaid__cwd += '   res[i] = ord(arg0[0])'
    llklu__zbz = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def repeat_util(arr, repeats):
    verify_string_arg(arr, 'REPEAT', 'arr')
    verify_int_arg(repeats, 'REPEAT', 'repeats')
    org__pkv = ['arr', 'repeats']
    fnym__fkold = [arr, repeats]
    bkh__cpfrp = [True] * 2
    toaid__cwd = 'if arg1 <= 0:\n'
    toaid__cwd += "   res[i] = ''\n"
    toaid__cwd += 'else:\n'
    toaid__cwd += '   res[i] = arg0 * arg1'
    llklu__zbz = bodo.string_array_type
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def replace_util(arr, to_replace, replace_with):
    verify_string_arg(arr, 'REPLACE', 'arr')
    verify_string_arg(to_replace, 'REPLACE', 'to_replace')
    verify_string_arg(replace_with, 'REPLACE', 'replace_with')
    org__pkv = ['arr', 'to_replace', 'replace_with']
    fnym__fkold = [arr, to_replace, replace_with]
    bkh__cpfrp = [True] * 3
    toaid__cwd = "if arg1 == '':\n"
    toaid__cwd += '   res[i] = arg0\n'
    toaid__cwd += 'else:\n'
    toaid__cwd += '   res[i] = arg0.replace(arg1, arg2)'
    llklu__zbz = bodo.string_array_type
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def reverse_util(arr):
    rypxj__khvf = verify_string_binary_arg(arr, 'REVERSE', 'arr')
    org__pkv = ['arr']
    fnym__fkold = [arr]
    bkh__cpfrp = [True]
    toaid__cwd = 'res[i] = arg0[::-1]'
    llklu__zbz = bodo.string_array_type
    llklu__zbz = (bodo.string_array_type if rypxj__khvf else bodo.
        binary_array_type)
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def space_util(n_chars):
    verify_int_arg(n_chars, 'SPACE', 'n_chars')
    org__pkv = ['n_chars']
    fnym__fkold = [n_chars]
    bkh__cpfrp = [True]
    toaid__cwd = 'if arg0 <= 0:\n'
    toaid__cwd += "   res[i] = ''\n"
    toaid__cwd += 'else:\n'
    toaid__cwd += "   res[i] = ' ' * arg0"
    llklu__zbz = bodo.string_array_type
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def strcmp_util(arr0, arr1):
    verify_string_arg(arr0, 'strcmp', 'arr0')
    verify_string_arg(arr1, 'strcmp', 'arr1')
    org__pkv = ['arr0', 'arr1']
    fnym__fkold = [arr0, arr1]
    bkh__cpfrp = [True] * 2
    toaid__cwd = 'if arg0 < arg1:\n'
    toaid__cwd += '   res[i] = -1\n'
    toaid__cwd += 'elif arg0 > arg1:\n'
    toaid__cwd += '   res[i] = 1\n'
    toaid__cwd += 'else:\n'
    toaid__cwd += '   res[i] = 0\n'
    llklu__zbz = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def substring_util(arr, start, length):
    rypxj__khvf = verify_string_binary_arg(arr, 'SUBSTRING', 'arr')
    verify_int_arg(start, 'SUBSTRING', 'start')
    verify_int_arg(length, 'SUBSTRING', 'length')
    llklu__zbz = (bodo.string_array_type if rypxj__khvf else bodo.
        binary_array_type)
    org__pkv = ['arr', 'start', 'length']
    fnym__fkold = [arr, start, length]
    bkh__cpfrp = [True] * 3
    toaid__cwd = 'if arg2 <= 0:\n'
    toaid__cwd += "   res[i] = ''\n" if rypxj__khvf else "   res[i] = b''\n"
    toaid__cwd += 'elif arg1 < 0 and arg1 + arg2 >= 0:\n'
    toaid__cwd += '   res[i] = arg0[arg1:]\n'
    toaid__cwd += 'else:\n'
    toaid__cwd += '   if arg1 > 0: arg1 -= 1\n'
    toaid__cwd += '   res[i] = arg0[arg1:arg1+arg2]\n'
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)


@numba.generated_jit(nopython=True)
def substring_index_util(arr, delimiter, occurrences):
    verify_string_arg(arr, 'SUBSTRING_INDEX', 'arr')
    verify_string_arg(delimiter, 'SUBSTRING_INDEX', 'delimiter')
    verify_int_arg(occurrences, 'SUBSTRING_INDEX', 'occurrences')
    org__pkv = ['arr', 'delimiter', 'occurrences']
    fnym__fkold = [arr, delimiter, occurrences]
    bkh__cpfrp = [True] * 3
    toaid__cwd = "if arg1 == '' or arg2 == 0:\n"
    toaid__cwd += "   res[i] = ''\n"
    toaid__cwd += 'elif arg2 >= 0:\n'
    toaid__cwd += '   res[i] = arg1.join(arg0.split(arg1, arg2+1)[:arg2])\n'
    toaid__cwd += 'else:\n'
    toaid__cwd += '   res[i] = arg1.join(arg0.split(arg1)[arg2:])\n'
    llklu__zbz = bodo.string_array_type
    return gen_vectorized(org__pkv, fnym__fkold, bkh__cpfrp, toaid__cwd,
        llklu__zbz)
