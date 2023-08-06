"""
Implements miscellaneous array kernels that are specific to BodoSQL
"""
import numba
from numba.core import types
import bodo
from bodo.libs.bodosql_array_kernel_utils import *
from bodo.utils.typing import raise_bodo_error


@numba.generated_jit(nopython=True)
def cond(arr, ifbranch, elsebranch):
    args = [arr, ifbranch, elsebranch]
    for wapbt__bglc in range(3):
        if isinstance(args[wapbt__bglc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.cond', [
                'arr', 'ifbranch', 'elsebranch'], wapbt__bglc)

    def impl(arr, ifbranch, elsebranch):
        return cond_util(arr, ifbranch, elsebranch)
    return impl


@numba.generated_jit(nopython=True)
def nullif(arr0, arr1):
    args = [arr0, arr1]
    for wapbt__bglc in range(2):
        if isinstance(args[wapbt__bglc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.nullif',
                ['arr0', 'arr1'], wapbt__bglc)

    def impl(arr0, arr1):
        return nullif_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def cond_util(arr, ifbranch, elsebranch):
    verify_boolean_arg(arr, 'cond', 'arr')
    if bodo.utils.utils.is_array_typ(arr, True
        ) and ifbranch == bodo.none and elsebranch == bodo.none:
        raise_bodo_error('Both branches of IF() cannot be scalar NULL')
    ogeqp__ogfc = ['arr', 'ifbranch', 'elsebranch']
    kgqqd__rplz = [arr, ifbranch, elsebranch]
    gjvm__yjnev = [False] * 3
    if bodo.utils.utils.is_array_typ(arr, True):
        fqbvk__xwi = (
            'if (not bodo.libs.array_kernels.isna(arr, i)) and arg0:\n')
    elif arr != bodo.none:
        fqbvk__xwi = 'if arg0:\n'
    else:
        fqbvk__xwi = ''
    if arr != bodo.none:
        if bodo.utils.utils.is_array_typ(ifbranch, True):
            fqbvk__xwi += '   if bodo.libs.array_kernels.isna(ifbranch, i):\n'
            fqbvk__xwi += '      bodo.libs.array_kernels.setna(res, i)\n'
            fqbvk__xwi += '   else:\n'
            fqbvk__xwi += '      res[i] = arg1\n'
        elif ifbranch == bodo.none:
            fqbvk__xwi += '   bodo.libs.array_kernels.setna(res, i)\n'
        else:
            fqbvk__xwi += '   res[i] = arg1\n'
        fqbvk__xwi += 'else:\n'
    if bodo.utils.utils.is_array_typ(elsebranch, True):
        fqbvk__xwi += '   if bodo.libs.array_kernels.isna(elsebranch, i):\n'
        fqbvk__xwi += '      bodo.libs.array_kernels.setna(res, i)\n'
        fqbvk__xwi += '   else:\n'
        fqbvk__xwi += '      res[i] = arg2\n'
    elif elsebranch == bodo.none:
        fqbvk__xwi += '   bodo.libs.array_kernels.setna(res, i)\n'
    else:
        fqbvk__xwi += '   res[i] = arg2\n'
    csj__bousj = get_common_broadcasted_type([ifbranch, elsebranch], 'IF')
    return gen_vectorized(ogeqp__ogfc, kgqqd__rplz, gjvm__yjnev, fqbvk__xwi,
        csj__bousj)


@numba.generated_jit(nopython=True)
def nullif_util(arr0, arr1):
    ogeqp__ogfc = ['arr0', 'arr1']
    kgqqd__rplz = [arr0, arr1]
    gjvm__yjnev = [True, False]
    if arr1 == bodo.none:
        fqbvk__xwi = 'res[i] = arg0\n'
    elif bodo.utils.utils.is_array_typ(arr1, True):
        fqbvk__xwi = (
            'if bodo.libs.array_kernels.isna(arr1, i) or arg0 != arg1:\n')
        fqbvk__xwi += '   res[i] = arg0\n'
        fqbvk__xwi += 'else:\n'
        fqbvk__xwi += '   bodo.libs.array_kernels.setna(res, i)'
    else:
        fqbvk__xwi = 'if arg0 != arg1:\n'
        fqbvk__xwi += '   res[i] = arg0\n'
        fqbvk__xwi += 'else:\n'
        fqbvk__xwi += '   bodo.libs.array_kernels.setna(res, i)'
    csj__bousj = get_common_broadcasted_type([arr0, arr1], 'NULLIF')
    return gen_vectorized(ogeqp__ogfc, kgqqd__rplz, gjvm__yjnev, fqbvk__xwi,
        csj__bousj)
