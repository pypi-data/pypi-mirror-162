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
    for ypg__ssz in range(3):
        if isinstance(args[ypg__ssz], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.cond', [
                'arr', 'ifbranch', 'elsebranch'], ypg__ssz)

    def impl(arr, ifbranch, elsebranch):
        return cond_util(arr, ifbranch, elsebranch)
    return impl


@numba.generated_jit(nopython=True)
def nullif(arr0, arr1):
    args = [arr0, arr1]
    for ypg__ssz in range(2):
        if isinstance(args[ypg__ssz], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.nullif',
                ['arr0', 'arr1'], ypg__ssz)

    def impl(arr0, arr1):
        return nullif_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def cond_util(arr, ifbranch, elsebranch):
    verify_boolean_arg(arr, 'cond', 'arr')
    if bodo.utils.utils.is_array_typ(arr, True
        ) and ifbranch == bodo.none and elsebranch == bodo.none:
        raise_bodo_error('Both branches of IF() cannot be scalar NULL')
    wbodk__vetvs = ['arr', 'ifbranch', 'elsebranch']
    xkpjc__pda = [arr, ifbranch, elsebranch]
    vpj__zcnzm = [False] * 3
    if bodo.utils.utils.is_array_typ(arr, True):
        bnns__mxiy = (
            'if (not bodo.libs.array_kernels.isna(arr, i)) and arg0:\n')
    elif arr != bodo.none:
        bnns__mxiy = 'if arg0:\n'
    else:
        bnns__mxiy = ''
    if arr != bodo.none:
        if bodo.utils.utils.is_array_typ(ifbranch, True):
            bnns__mxiy += '   if bodo.libs.array_kernels.isna(ifbranch, i):\n'
            bnns__mxiy += '      bodo.libs.array_kernels.setna(res, i)\n'
            bnns__mxiy += '   else:\n'
            bnns__mxiy += '      res[i] = arg1\n'
        elif ifbranch == bodo.none:
            bnns__mxiy += '   bodo.libs.array_kernels.setna(res, i)\n'
        else:
            bnns__mxiy += '   res[i] = arg1\n'
        bnns__mxiy += 'else:\n'
    if bodo.utils.utils.is_array_typ(elsebranch, True):
        bnns__mxiy += '   if bodo.libs.array_kernels.isna(elsebranch, i):\n'
        bnns__mxiy += '      bodo.libs.array_kernels.setna(res, i)\n'
        bnns__mxiy += '   else:\n'
        bnns__mxiy += '      res[i] = arg2\n'
    elif elsebranch == bodo.none:
        bnns__mxiy += '   bodo.libs.array_kernels.setna(res, i)\n'
    else:
        bnns__mxiy += '   res[i] = arg2\n'
    uugxk__vqpg = get_common_broadcasted_type([ifbranch, elsebranch], 'IF')
    return gen_vectorized(wbodk__vetvs, xkpjc__pda, vpj__zcnzm, bnns__mxiy,
        uugxk__vqpg)


@numba.generated_jit(nopython=True)
def nullif_util(arr0, arr1):
    wbodk__vetvs = ['arr0', 'arr1']
    xkpjc__pda = [arr0, arr1]
    vpj__zcnzm = [True, False]
    if arr1 == bodo.none:
        bnns__mxiy = 'res[i] = arg0\n'
    elif bodo.utils.utils.is_array_typ(arr1, True):
        bnns__mxiy = (
            'if bodo.libs.array_kernels.isna(arr1, i) or arg0 != arg1:\n')
        bnns__mxiy += '   res[i] = arg0\n'
        bnns__mxiy += 'else:\n'
        bnns__mxiy += '   bodo.libs.array_kernels.setna(res, i)'
    else:
        bnns__mxiy = 'if arg0 != arg1:\n'
        bnns__mxiy += '   res[i] = arg0\n'
        bnns__mxiy += 'else:\n'
        bnns__mxiy += '   bodo.libs.array_kernels.setna(res, i)'
    uugxk__vqpg = get_common_broadcasted_type([arr0, arr1], 'NULLIF')
    return gen_vectorized(wbodk__vetvs, xkpjc__pda, vpj__zcnzm, bnns__mxiy,
        uugxk__vqpg)
