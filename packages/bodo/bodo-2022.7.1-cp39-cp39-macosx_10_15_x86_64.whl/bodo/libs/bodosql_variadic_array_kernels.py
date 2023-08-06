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
    for ttdvb__wcchg in range(len(A)):
        if isinstance(A[ttdvb__wcchg], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.coalesce',
                ['A'], ttdvb__wcchg, container_length=len(A))

    def impl(A):
        return coalesce_util(A)
    return impl


def coalesce_util(A):
    return


@overload(coalesce_util, no_unliteral=True)
def overload_coalesce_util(A):
    if len(A) == 0:
        raise_bodo_error('Cannot coalesce 0 columns')
    mgr__gijtr = None
    akuao__tyl = []
    for ttdvb__wcchg in range(len(A)):
        if A[ttdvb__wcchg] == bodo.none:
            akuao__tyl.append(ttdvb__wcchg)
        elif not bodo.utils.utils.is_array_typ(A[ttdvb__wcchg]):
            for gqcig__xny in range(ttdvb__wcchg + 1, len(A)):
                akuao__tyl.append(gqcig__xny)
                if bodo.utils.utils.is_array_typ(A[gqcig__xny]):
                    mgr__gijtr = f'A[{gqcig__xny}]'
            break
    dviz__orf = [f'A{ttdvb__wcchg}' for ttdvb__wcchg in range(len(A)) if 
        ttdvb__wcchg not in akuao__tyl]
    oyv__ajgq = [A[ttdvb__wcchg] for ttdvb__wcchg in range(len(A)) if 
        ttdvb__wcchg not in akuao__tyl]
    awxe__rjqr = [False] * (len(A) - len(akuao__tyl))
    cwp__dqhv = ''
    lci__mxhi = True
    jukqx__cmpox = False
    rgyor__sfy = 0
    for ttdvb__wcchg in range(len(A)):
        if ttdvb__wcchg in akuao__tyl:
            rgyor__sfy += 1
            continue
        elif bodo.utils.utils.is_array_typ(A[ttdvb__wcchg]):
            wiva__vdju = 'if' if lci__mxhi else 'elif'
            cwp__dqhv += (
                f'{wiva__vdju} not bodo.libs.array_kernels.isna(A{ttdvb__wcchg}, i):\n'
                )
            cwp__dqhv += f'   res[i] = arg{ttdvb__wcchg - rgyor__sfy}\n'
            lci__mxhi = False
        else:
            assert not jukqx__cmpox, 'should not encounter more than one scalar due to dead column pruning'
            if lci__mxhi:
                cwp__dqhv += f'res[i] = arg{ttdvb__wcchg - rgyor__sfy}\n'
            else:
                cwp__dqhv += 'else:\n'
                cwp__dqhv += f'   res[i] = arg{ttdvb__wcchg - rgyor__sfy}\n'
            jukqx__cmpox = True
            break
    if not jukqx__cmpox:
        if not lci__mxhi:
            cwp__dqhv += 'else:\n'
            cwp__dqhv += '   bodo.libs.array_kernels.setna(res, i)'
        else:
            cwp__dqhv += 'bodo.libs.array_kernels.setna(res, i)'
    mrbnd__dxlak = 'A'
    uzi__ztaig = {f'A{ttdvb__wcchg}': f'A[{ttdvb__wcchg}]' for ttdvb__wcchg in
        range(len(A)) if ttdvb__wcchg not in akuao__tyl}
    deemi__odry = get_common_broadcasted_type(oyv__ajgq, 'COALESCE')
    return gen_vectorized(dviz__orf, oyv__ajgq, awxe__rjqr, cwp__dqhv,
        deemi__odry, mrbnd__dxlak, uzi__ztaig, mgr__gijtr,
        support_dict_encoding=False)
