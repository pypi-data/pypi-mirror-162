"""
Implements array kernels that are specific to BodoSQL which have a variable
number of arguments
"""
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.bodosql_array_kernel_utils import *
from bodo.utils.typing import raise_bodo_error


def coalesce(A):
    return


@overload(coalesce)
def overload_coalesce(A):
    if not isinstance(A, (types.Tuple, types.UniTuple)):
        raise_bodo_error('Coalesce argument must be a tuple')
    for qevh__nxj in range(len(A)):
        if isinstance(A[qevh__nxj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.coalesce',
                ['A'], qevh__nxj, container_length=len(A))

    def impl(A):
        return coalesce_util(A)
    return impl


def coalesce_util(A):
    return


@overload(coalesce_util, no_unliteral=True)
def overload_coalesce_util(A):
    if len(A) == 0:
        raise_bodo_error('Cannot coalesce 0 columns')
    gfle__jttbt = None
    ykvv__niyzn = []
    for qevh__nxj in range(len(A)):
        if A[qevh__nxj] == bodo.none:
            ykvv__niyzn.append(qevh__nxj)
        elif not bodo.utils.utils.is_array_typ(A[qevh__nxj]):
            for gxbg__ekiv in range(qevh__nxj + 1, len(A)):
                ykvv__niyzn.append(gxbg__ekiv)
                if bodo.utils.utils.is_array_typ(A[gxbg__ekiv]):
                    gfle__jttbt = f'A[{gxbg__ekiv}]'
            break
    abbty__lkb = [f'A{qevh__nxj}' for qevh__nxj in range(len(A)) if 
        qevh__nxj not in ykvv__niyzn]
    lntui__irtzi = [A[qevh__nxj] for qevh__nxj in range(len(A)) if 
        qevh__nxj not in ykvv__niyzn]
    znnw__oha = [False] * (len(A) - len(ykvv__niyzn))
    uxe__xqsts = ''
    zskt__ktoq = True
    gkfhk__lqk = False
    nmeb__ehp = 0
    for qevh__nxj in range(len(A)):
        if qevh__nxj in ykvv__niyzn:
            nmeb__ehp += 1
            continue
        elif bodo.utils.utils.is_array_typ(A[qevh__nxj]):
            mvyva__lhcie = 'if' if zskt__ktoq else 'elif'
            uxe__xqsts += (
                f'{mvyva__lhcie} not bodo.libs.array_kernels.isna(A{qevh__nxj}, i):\n'
                )
            uxe__xqsts += f'   res[i] = arg{qevh__nxj - nmeb__ehp}\n'
            zskt__ktoq = False
        else:
            assert not gkfhk__lqk, 'should not encounter more than one scalar due to dead column pruning'
            if zskt__ktoq:
                uxe__xqsts += f'res[i] = arg{qevh__nxj - nmeb__ehp}\n'
            else:
                uxe__xqsts += 'else:\n'
                uxe__xqsts += f'   res[i] = arg{qevh__nxj - nmeb__ehp}\n'
            gkfhk__lqk = True
            break
    if not gkfhk__lqk:
        if not zskt__ktoq:
            uxe__xqsts += 'else:\n'
            uxe__xqsts += '   bodo.libs.array_kernels.setna(res, i)'
        else:
            uxe__xqsts += 'bodo.libs.array_kernels.setna(res, i)'
    nwy__euu = 'A'
    qldu__gxq = {f'A{qevh__nxj}': f'A[{qevh__nxj}]' for qevh__nxj in range(
        len(A)) if qevh__nxj not in ykvv__niyzn}
    ioqmg__fyx = get_common_broadcasted_type(lntui__irtzi, 'COALESCE')
    return gen_vectorized(abbty__lkb, lntui__irtzi, znnw__oha, uxe__xqsts,
        ioqmg__fyx, nwy__euu, qldu__gxq, gfle__jttbt, support_dict_encoding
        =False)
