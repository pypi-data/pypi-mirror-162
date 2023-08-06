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
    for kzgzy__jukm in range(2):
        if isinstance(args[kzgzy__jukm], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.booland',
                ['A', 'B'], kzgzy__jukm)

    def impl(A, B):
        return booland_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolor(A, B):
    args = [A, B]
    for kzgzy__jukm in range(2):
        if isinstance(args[kzgzy__jukm], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolor',
                ['A', 'B'], kzgzy__jukm)

    def impl(A, B):
        return boolor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolxor(A, B):
    args = [A, B]
    for kzgzy__jukm in range(2):
        if isinstance(args[kzgzy__jukm], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolxor',
                ['A', 'B'], kzgzy__jukm)

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
    for kzgzy__jukm in range(3):
        if isinstance(args[kzgzy__jukm], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.cond', [
                'arr', 'ifbranch', 'elsebranch'], kzgzy__jukm)

    def impl(arr, ifbranch, elsebranch):
        return cond_util(arr, ifbranch, elsebranch)
    return impl


@numba.generated_jit(nopython=True)
def equal_null(A, B):
    args = [A, B]
    for kzgzy__jukm in range(2):
        if isinstance(args[kzgzy__jukm], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.equal_null',
                ['A', 'B'], kzgzy__jukm)

    def impl(A, B):
        return equal_null_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def booland_util(A, B):
    verify_int_float_arg(A, 'BOOLAND', 'A')
    verify_int_float_arg(B, 'BOOLAND', 'B')
    gnyv__cdjc = ['A', 'B']
    tkqeo__odp = [A, B]
    qvrd__oftd = [False] * 2
    if A == bodo.none:
        qvrd__oftd = [False, True]
        dahg__kbvsp = 'if arg1 != 0:\n'
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
        dahg__kbvsp += 'else:\n'
        dahg__kbvsp += '   res[i] = False\n'
    elif B == bodo.none:
        qvrd__oftd = [True, False]
        dahg__kbvsp = 'if arg0 != 0:\n'
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
        dahg__kbvsp += 'else:\n'
        dahg__kbvsp += '   res[i] = False\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            dahg__kbvsp = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += 'else:\n'
            dahg__kbvsp += '   res[i] = (arg0 != 0) and (arg1 != 0)'
        else:
            dahg__kbvsp = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += 'else:\n'
            dahg__kbvsp += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        dahg__kbvsp = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
        dahg__kbvsp += 'else:\n'
        dahg__kbvsp += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    else:
        dahg__kbvsp = 'res[i] = (arg0 != 0) and (arg1 != 0)'
    qgn__ocxdf = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(gnyv__cdjc, tkqeo__odp, qvrd__oftd, dahg__kbvsp,
        qgn__ocxdf)


@numba.generated_jit(nopython=True)
def boolor_util(A, B):
    verify_int_float_arg(A, 'BOOLOR', 'A')
    verify_int_float_arg(B, 'BOOLOR', 'B')
    gnyv__cdjc = ['A', 'B']
    tkqeo__odp = [A, B]
    qvrd__oftd = [False] * 2
    if A == bodo.none:
        qvrd__oftd = [False, True]
        dahg__kbvsp = 'if arg1 == 0:\n'
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
        dahg__kbvsp += 'else:\n'
        dahg__kbvsp += '   res[i] = True\n'
    elif B == bodo.none:
        qvrd__oftd = [True, False]
        dahg__kbvsp = 'if arg0 == 0:\n'
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
        dahg__kbvsp += 'else:\n'
        dahg__kbvsp += '   res[i] = True\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            dahg__kbvsp = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            dahg__kbvsp += '   res[i] = True\n'
            dahg__kbvsp += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            dahg__kbvsp += '   res[i] = True\n'
            dahg__kbvsp += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += 'else:\n'
            dahg__kbvsp += '   res[i] = (arg0 != 0) or (arg1 != 0)'
        else:
            dahg__kbvsp = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            dahg__kbvsp += '   res[i] = True\n'
            dahg__kbvsp += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += 'else:\n'
            dahg__kbvsp += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        dahg__kbvsp = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        dahg__kbvsp += '   res[i] = True\n'
        dahg__kbvsp += (
            'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
        dahg__kbvsp += 'else:\n'
        dahg__kbvsp += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    else:
        dahg__kbvsp = 'res[i] = (arg0 != 0) or (arg1 != 0)'
    qgn__ocxdf = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(gnyv__cdjc, tkqeo__odp, qvrd__oftd, dahg__kbvsp,
        qgn__ocxdf)


@numba.generated_jit(nopython=True)
def boolxor_util(A, B):
    verify_int_float_arg(A, 'BOOLXOR', 'A')
    verify_int_float_arg(B, 'BOOLXOR', 'B')
    gnyv__cdjc = ['A', 'B']
    tkqeo__odp = [A, B]
    qvrd__oftd = [True] * 2
    dahg__kbvsp = 'res[i] = (arg0 == 0) != (arg1 == 0)'
    qgn__ocxdf = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(gnyv__cdjc, tkqeo__odp, qvrd__oftd, dahg__kbvsp,
        qgn__ocxdf)


@numba.generated_jit(nopython=True)
def boolnot_util(A):
    verify_int_float_arg(A, 'BOOLNOT', 'A')
    gnyv__cdjc = ['A']
    tkqeo__odp = [A]
    qvrd__oftd = [True]
    dahg__kbvsp = 'res[i] = arg0 == 0'
    qgn__ocxdf = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(gnyv__cdjc, tkqeo__odp, qvrd__oftd, dahg__kbvsp,
        qgn__ocxdf)


@numba.generated_jit(nopython=True)
def nullif(arr0, arr1):
    args = [arr0, arr1]
    for kzgzy__jukm in range(2):
        if isinstance(args[kzgzy__jukm], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.nullif',
                ['arr0', 'arr1'], kzgzy__jukm)

    def impl(arr0, arr1):
        return nullif_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def regr_valx(y, x):
    args = [y, x]
    for kzgzy__jukm in range(2):
        if isinstance(args[kzgzy__jukm], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valx',
                ['y', 'x'], kzgzy__jukm)

    def impl(y, x):
        return regr_valx_util(y, x)
    return impl


@numba.generated_jit(nopython=True)
def regr_valy(y, x):
    args = [y, x]
    for kzgzy__jukm in range(2):
        if isinstance(args[kzgzy__jukm], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valy',
                ['y', 'x'], kzgzy__jukm)

    def impl(y, x):
        return regr_valx(x, y)
    return impl


@numba.generated_jit(nopython=True)
def cond_util(arr, ifbranch, elsebranch):
    verify_boolean_arg(arr, 'cond', 'arr')
    if bodo.utils.utils.is_array_typ(arr, True
        ) and ifbranch == bodo.none and elsebranch == bodo.none:
        raise_bodo_error('Both branches of IF() cannot be scalar NULL')
    gnyv__cdjc = ['arr', 'ifbranch', 'elsebranch']
    tkqeo__odp = [arr, ifbranch, elsebranch]
    qvrd__oftd = [False] * 3
    if bodo.utils.utils.is_array_typ(arr, True):
        dahg__kbvsp = (
            'if (not bodo.libs.array_kernels.isna(arr, i)) and arg0:\n')
    elif arr != bodo.none:
        dahg__kbvsp = 'if arg0:\n'
    else:
        dahg__kbvsp = ''
    if arr != bodo.none:
        if bodo.utils.utils.is_array_typ(ifbranch, True):
            dahg__kbvsp += '   if bodo.libs.array_kernels.isna(ifbranch, i):\n'
            dahg__kbvsp += '      bodo.libs.array_kernels.setna(res, i)\n'
            dahg__kbvsp += '   else:\n'
            dahg__kbvsp += '      res[i] = arg1\n'
        elif ifbranch == bodo.none:
            dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
        else:
            dahg__kbvsp += '   res[i] = arg1\n'
        dahg__kbvsp += 'else:\n'
    if bodo.utils.utils.is_array_typ(elsebranch, True):
        dahg__kbvsp += '   if bodo.libs.array_kernels.isna(elsebranch, i):\n'
        dahg__kbvsp += '      bodo.libs.array_kernels.setna(res, i)\n'
        dahg__kbvsp += '   else:\n'
        dahg__kbvsp += '      res[i] = arg2\n'
    elif elsebranch == bodo.none:
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)\n'
    else:
        dahg__kbvsp += '   res[i] = arg2\n'
    qgn__ocxdf = get_common_broadcasted_type([ifbranch, elsebranch], 'IF')
    return gen_vectorized(gnyv__cdjc, tkqeo__odp, qvrd__oftd, dahg__kbvsp,
        qgn__ocxdf)


@numba.generated_jit(nopython=True)
def equal_null_util(A, B):
    get_common_broadcasted_type([A, B], 'EQUAL_NULL')
    gnyv__cdjc = ['A', 'B']
    tkqeo__odp = [A, B]
    qvrd__oftd = [False] * 2
    if A == bodo.none:
        if B == bodo.none:
            dahg__kbvsp = 'res[i] = True'
        elif bodo.utils.utils.is_array_typ(B, True):
            dahg__kbvsp = 'res[i] = bodo.libs.array_kernels.isna(B, i)'
        else:
            dahg__kbvsp = 'res[i] = False'
    elif B == bodo.none:
        if bodo.utils.utils.is_array_typ(A, True):
            dahg__kbvsp = 'res[i] = bodo.libs.array_kernels.isna(A, i)'
        else:
            dahg__kbvsp = 'res[i] = False'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            dahg__kbvsp = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            dahg__kbvsp += '   res[i] = True\n'
            dahg__kbvsp += """elif bodo.libs.array_kernels.isna(A, i) or bodo.libs.array_kernels.isna(B, i):
"""
            dahg__kbvsp += '   res[i] = False\n'
            dahg__kbvsp += 'else:\n'
            dahg__kbvsp += '   res[i] = arg0 == arg1'
        else:
            dahg__kbvsp = (
                'res[i] = (not bodo.libs.array_kernels.isna(A, i)) and arg0 == arg1'
                )
    elif bodo.utils.utils.is_array_typ(B, True):
        dahg__kbvsp = (
            'res[i] = (not bodo.libs.array_kernels.isna(B, i)) and arg0 == arg1'
            )
    else:
        dahg__kbvsp = 'res[i] = arg0 == arg1'
    qgn__ocxdf = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(gnyv__cdjc, tkqeo__odp, qvrd__oftd, dahg__kbvsp,
        qgn__ocxdf)


@numba.generated_jit(nopython=True)
def nullif_util(arr0, arr1):
    gnyv__cdjc = ['arr0', 'arr1']
    tkqeo__odp = [arr0, arr1]
    qvrd__oftd = [True, False]
    if arr1 == bodo.none:
        dahg__kbvsp = 'res[i] = arg0\n'
    elif bodo.utils.utils.is_array_typ(arr1, True):
        dahg__kbvsp = (
            'if bodo.libs.array_kernels.isna(arr1, i) or arg0 != arg1:\n')
        dahg__kbvsp += '   res[i] = arg0\n'
        dahg__kbvsp += 'else:\n'
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)'
    else:
        dahg__kbvsp = 'if arg0 != arg1:\n'
        dahg__kbvsp += '   res[i] = arg0\n'
        dahg__kbvsp += 'else:\n'
        dahg__kbvsp += '   bodo.libs.array_kernels.setna(res, i)'
    qgn__ocxdf = get_common_broadcasted_type([arr0, arr1], 'NULLIF')
    return gen_vectorized(gnyv__cdjc, tkqeo__odp, qvrd__oftd, dahg__kbvsp,
        qgn__ocxdf)


@numba.generated_jit(nopython=True)
def regr_valx_util(y, x):
    verify_int_float_arg(y, 'regr_valx', 'y')
    verify_int_float_arg(x, 'regr_valx', 'x')
    gnyv__cdjc = ['y', 'x']
    tkqeo__odp = [y, x]
    yycv__lduy = [True] * 2
    dahg__kbvsp = 'res[i] = arg1'
    qgn__ocxdf = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(gnyv__cdjc, tkqeo__odp, yycv__lduy, dahg__kbvsp,
        qgn__ocxdf)
