"""
Implements miscellaneous array kernels that are specific to BodoSQL
"""
import numba
from numba.core import types
import bodo
from bodo.libs.bodosql_array_kernel_utils import *
from bodo.utils.typing import raise_bodo_error


@numba.generated_jit(nopython=True)
def booland(A, B):
    args = [A, B]
    for xwu__uer in range(2):
        if isinstance(args[xwu__uer], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.booland',
                ['A', 'B'], xwu__uer)

    def impl(A, B):
        return booland_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolor(A, B):
    args = [A, B]
    for xwu__uer in range(2):
        if isinstance(args[xwu__uer], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolor',
                ['A', 'B'], xwu__uer)

    def impl(A, B):
        return boolor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolxor(A, B):
    args = [A, B]
    for xwu__uer in range(2):
        if isinstance(args[xwu__uer], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolxor',
                ['A', 'B'], xwu__uer)

    def impl(A, B):
        return boolxor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolnot(A):
    if isinstance(A, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.boolnot_util',
            ['A'], 0)

    def impl(A):
        return boolnot_util(A)
    return impl


@numba.generated_jit(nopython=True)
def cond(arr, ifbranch, elsebranch):
    args = [arr, ifbranch, elsebranch]
    for xwu__uer in range(3):
        if isinstance(args[xwu__uer], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.cond', [
                'arr', 'ifbranch', 'elsebranch'], xwu__uer)

    def impl(arr, ifbranch, elsebranch):
        return cond_util(arr, ifbranch, elsebranch)
    return impl


@numba.generated_jit(nopython=True)
def equal_null(A, B):
    args = [A, B]
    for xwu__uer in range(2):
        if isinstance(args[xwu__uer], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.equal_null',
                ['A', 'B'], xwu__uer)

    def impl(A, B):
        return equal_null_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def booland_util(A, B):
    verify_int_float_arg(A, 'BOOLAND', 'A')
    verify_int_float_arg(B, 'BOOLAND', 'B')
    pzxj__vgmlb = ['A', 'B']
    wdec__azel = [A, B]
    olr__ajtzl = [False] * 2
    if A == bodo.none:
        olr__ajtzl = [False, True]
        rfkxd__bhbgl = 'if arg1 != 0:\n'
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
        rfkxd__bhbgl += 'else:\n'
        rfkxd__bhbgl += '   res[i] = False\n'
    elif B == bodo.none:
        olr__ajtzl = [True, False]
        rfkxd__bhbgl = 'if arg0 != 0:\n'
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
        rfkxd__bhbgl += 'else:\n'
        rfkxd__bhbgl += '   res[i] = False\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            rfkxd__bhbgl = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += 'else:\n'
            rfkxd__bhbgl += '   res[i] = (arg0 != 0) and (arg1 != 0)'
        else:
            rfkxd__bhbgl = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += 'else:\n'
            rfkxd__bhbgl += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        rfkxd__bhbgl = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
        rfkxd__bhbgl += 'else:\n'
        rfkxd__bhbgl += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    else:
        rfkxd__bhbgl = 'res[i] = (arg0 != 0) and (arg1 != 0)'
    ays__jelt = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(pzxj__vgmlb, wdec__azel, olr__ajtzl, rfkxd__bhbgl,
        ays__jelt)


@numba.generated_jit(nopython=True)
def boolor_util(A, B):
    verify_int_float_arg(A, 'BOOLOR', 'A')
    verify_int_float_arg(B, 'BOOLOR', 'B')
    pzxj__vgmlb = ['A', 'B']
    wdec__azel = [A, B]
    olr__ajtzl = [False] * 2
    if A == bodo.none:
        olr__ajtzl = [False, True]
        rfkxd__bhbgl = 'if arg1 == 0:\n'
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
        rfkxd__bhbgl += 'else:\n'
        rfkxd__bhbgl += '   res[i] = True\n'
    elif B == bodo.none:
        olr__ajtzl = [True, False]
        rfkxd__bhbgl = 'if arg0 == 0:\n'
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
        rfkxd__bhbgl += 'else:\n'
        rfkxd__bhbgl += '   res[i] = True\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            rfkxd__bhbgl = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            rfkxd__bhbgl += '   res[i] = True\n'
            rfkxd__bhbgl += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            rfkxd__bhbgl += '   res[i] = True\n'
            rfkxd__bhbgl += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += 'else:\n'
            rfkxd__bhbgl += '   res[i] = (arg0 != 0) or (arg1 != 0)'
        else:
            rfkxd__bhbgl = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            rfkxd__bhbgl += '   res[i] = True\n'
            rfkxd__bhbgl += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += 'else:\n'
            rfkxd__bhbgl += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        rfkxd__bhbgl = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        rfkxd__bhbgl += '   res[i] = True\n'
        rfkxd__bhbgl += (
            'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
        rfkxd__bhbgl += 'else:\n'
        rfkxd__bhbgl += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    else:
        rfkxd__bhbgl = 'res[i] = (arg0 != 0) or (arg1 != 0)'
    ays__jelt = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(pzxj__vgmlb, wdec__azel, olr__ajtzl, rfkxd__bhbgl,
        ays__jelt)


@numba.generated_jit(nopython=True)
def boolxor_util(A, B):
    verify_int_float_arg(A, 'BOOLXOR', 'A')
    verify_int_float_arg(B, 'BOOLXOR', 'B')
    pzxj__vgmlb = ['A', 'B']
    wdec__azel = [A, B]
    olr__ajtzl = [True] * 2
    rfkxd__bhbgl = 'res[i] = (arg0 == 0) != (arg1 == 0)'
    ays__jelt = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(pzxj__vgmlb, wdec__azel, olr__ajtzl, rfkxd__bhbgl,
        ays__jelt)


@numba.generated_jit(nopython=True)
def boolnot_util(A):
    verify_int_float_arg(A, 'BOOLNOT', 'A')
    pzxj__vgmlb = ['A']
    wdec__azel = [A]
    olr__ajtzl = [True]
    rfkxd__bhbgl = 'res[i] = arg0 == 0'
    ays__jelt = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(pzxj__vgmlb, wdec__azel, olr__ajtzl, rfkxd__bhbgl,
        ays__jelt)


@numba.generated_jit(nopython=True)
def nullif(arr0, arr1):
    args = [arr0, arr1]
    for xwu__uer in range(2):
        if isinstance(args[xwu__uer], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.nullif',
                ['arr0', 'arr1'], xwu__uer)

    def impl(arr0, arr1):
        return nullif_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def regr_valx(y, x):
    args = [y, x]
    for xwu__uer in range(2):
        if isinstance(args[xwu__uer], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valx',
                ['y', 'x'], xwu__uer)

    def impl(y, x):
        return regr_valx_util(y, x)
    return impl


@numba.generated_jit(nopython=True)
def regr_valy(y, x):
    args = [y, x]
    for xwu__uer in range(2):
        if isinstance(args[xwu__uer], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valy',
                ['y', 'x'], xwu__uer)

    def impl(y, x):
        return regr_valx(x, y)
    return impl


@numba.generated_jit(nopython=True)
def cond_util(arr, ifbranch, elsebranch):
    verify_boolean_arg(arr, 'cond', 'arr')
    if bodo.utils.utils.is_array_typ(arr, True
        ) and ifbranch == bodo.none and elsebranch == bodo.none:
        raise_bodo_error('Both branches of IF() cannot be scalar NULL')
    pzxj__vgmlb = ['arr', 'ifbranch', 'elsebranch']
    wdec__azel = [arr, ifbranch, elsebranch]
    olr__ajtzl = [False] * 3
    if bodo.utils.utils.is_array_typ(arr, True):
        rfkxd__bhbgl = (
            'if (not bodo.libs.array_kernels.isna(arr, i)) and arg0:\n')
    elif arr != bodo.none:
        rfkxd__bhbgl = 'if arg0:\n'
    else:
        rfkxd__bhbgl = ''
    if arr != bodo.none:
        if bodo.utils.utils.is_array_typ(ifbranch, True):
            rfkxd__bhbgl += (
                '   if bodo.libs.array_kernels.isna(ifbranch, i):\n')
            rfkxd__bhbgl += '      bodo.libs.array_kernels.setna(res, i)\n'
            rfkxd__bhbgl += '   else:\n'
            rfkxd__bhbgl += '      res[i] = arg1\n'
        elif ifbranch == bodo.none:
            rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
        else:
            rfkxd__bhbgl += '   res[i] = arg1\n'
        rfkxd__bhbgl += 'else:\n'
    if bodo.utils.utils.is_array_typ(elsebranch, True):
        rfkxd__bhbgl += '   if bodo.libs.array_kernels.isna(elsebranch, i):\n'
        rfkxd__bhbgl += '      bodo.libs.array_kernels.setna(res, i)\n'
        rfkxd__bhbgl += '   else:\n'
        rfkxd__bhbgl += '      res[i] = arg2\n'
    elif elsebranch == bodo.none:
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)\n'
    else:
        rfkxd__bhbgl += '   res[i] = arg2\n'
    ays__jelt = get_common_broadcasted_type([ifbranch, elsebranch], 'IF')
    return gen_vectorized(pzxj__vgmlb, wdec__azel, olr__ajtzl, rfkxd__bhbgl,
        ays__jelt)


@numba.generated_jit(nopython=True)
def equal_null_util(A, B):
    get_common_broadcasted_type([A, B], 'EQUAL_NULL')
    pzxj__vgmlb = ['A', 'B']
    wdec__azel = [A, B]
    olr__ajtzl = [False] * 2
    if A == bodo.none:
        if B == bodo.none:
            rfkxd__bhbgl = 'res[i] = True'
        elif bodo.utils.utils.is_array_typ(B, True):
            rfkxd__bhbgl = 'res[i] = bodo.libs.array_kernels.isna(B, i)'
        else:
            rfkxd__bhbgl = 'res[i] = False'
    elif B == bodo.none:
        if bodo.utils.utils.is_array_typ(A, True):
            rfkxd__bhbgl = 'res[i] = bodo.libs.array_kernels.isna(A, i)'
        else:
            rfkxd__bhbgl = 'res[i] = False'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            rfkxd__bhbgl = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            rfkxd__bhbgl += '   res[i] = True\n'
            rfkxd__bhbgl += """elif bodo.libs.array_kernels.isna(A, i) or bodo.libs.array_kernels.isna(B, i):
"""
            rfkxd__bhbgl += '   res[i] = False\n'
            rfkxd__bhbgl += 'else:\n'
            rfkxd__bhbgl += '   res[i] = arg0 == arg1'
        else:
            rfkxd__bhbgl = (
                'res[i] = (not bodo.libs.array_kernels.isna(A, i)) and arg0 == arg1'
                )
    elif bodo.utils.utils.is_array_typ(B, True):
        rfkxd__bhbgl = (
            'res[i] = (not bodo.libs.array_kernels.isna(B, i)) and arg0 == arg1'
            )
    else:
        rfkxd__bhbgl = 'res[i] = arg0 == arg1'
    ays__jelt = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(pzxj__vgmlb, wdec__azel, olr__ajtzl, rfkxd__bhbgl,
        ays__jelt)


@numba.generated_jit(nopython=True)
def nullif_util(arr0, arr1):
    pzxj__vgmlb = ['arr0', 'arr1']
    wdec__azel = [arr0, arr1]
    olr__ajtzl = [True, False]
    if arr1 == bodo.none:
        rfkxd__bhbgl = 'res[i] = arg0\n'
    elif bodo.utils.utils.is_array_typ(arr1, True):
        rfkxd__bhbgl = (
            'if bodo.libs.array_kernels.isna(arr1, i) or arg0 != arg1:\n')
        rfkxd__bhbgl += '   res[i] = arg0\n'
        rfkxd__bhbgl += 'else:\n'
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)'
    else:
        rfkxd__bhbgl = 'if arg0 != arg1:\n'
        rfkxd__bhbgl += '   res[i] = arg0\n'
        rfkxd__bhbgl += 'else:\n'
        rfkxd__bhbgl += '   bodo.libs.array_kernels.setna(res, i)'
    ays__jelt = get_common_broadcasted_type([arr0, arr1], 'NULLIF')
    return gen_vectorized(pzxj__vgmlb, wdec__azel, olr__ajtzl, rfkxd__bhbgl,
        ays__jelt)


@numba.generated_jit(nopython=True)
def regr_valx_util(y, x):
    verify_int_float_arg(y, 'regr_valx', 'y')
    verify_int_float_arg(x, 'regr_valx', 'x')
    pzxj__vgmlb = ['y', 'x']
    wdec__azel = [y, x]
    svnuo__bnpn = [True] * 2
    rfkxd__bhbgl = 'res[i] = arg1'
    ays__jelt = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(pzxj__vgmlb, wdec__azel, svnuo__bnpn,
        rfkxd__bhbgl, ays__jelt)
