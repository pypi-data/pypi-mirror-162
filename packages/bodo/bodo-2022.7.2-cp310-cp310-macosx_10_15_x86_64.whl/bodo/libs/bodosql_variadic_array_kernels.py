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
    for dtk__cse in range(len(A)):
        if isinstance(A[dtk__cse], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.coalesce',
                ['A'], dtk__cse, container_length=len(A))

    def impl(A):
        return coalesce_util(A)
    return impl


def coalesce_util(A):
    return


@overload(coalesce_util, no_unliteral=True)
def overload_coalesce_util(A):
    if len(A) == 0:
        raise_bodo_error('Cannot coalesce 0 columns')
    qisbk__lelk = None
    nns__mlmmd = []
    for dtk__cse in range(len(A)):
        if A[dtk__cse] == bodo.none:
            nns__mlmmd.append(dtk__cse)
        elif not bodo.utils.utils.is_array_typ(A[dtk__cse]):
            for wwvy__glj in range(dtk__cse + 1, len(A)):
                nns__mlmmd.append(wwvy__glj)
                if bodo.utils.utils.is_array_typ(A[wwvy__glj]):
                    qisbk__lelk = f'A[{wwvy__glj}]'
            break
    asj__kxxhf = [f'A{dtk__cse}' for dtk__cse in range(len(A)) if dtk__cse
         not in nns__mlmmd]
    ohxqc__isads = [A[dtk__cse] for dtk__cse in range(len(A)) if dtk__cse
         not in nns__mlmmd]
    ugr__ohlid = [False] * (len(A) - len(nns__mlmmd))
    pai__kjt = ''
    dqop__lhlj = True
    ffhx__yts = False
    rfqw__gxcrg = 0
    for dtk__cse in range(len(A)):
        if dtk__cse in nns__mlmmd:
            rfqw__gxcrg += 1
            continue
        elif bodo.utils.utils.is_array_typ(A[dtk__cse]):
            plf__dnub = 'if' if dqop__lhlj else 'elif'
            pai__kjt += (
                f'{plf__dnub} not bodo.libs.array_kernels.isna(A{dtk__cse}, i):\n'
                )
            pai__kjt += f'   res[i] = arg{dtk__cse - rfqw__gxcrg}\n'
            dqop__lhlj = False
        else:
            assert not ffhx__yts, 'should not encounter more than one scalar due to dead column pruning'
            if dqop__lhlj:
                pai__kjt += f'res[i] = arg{dtk__cse - rfqw__gxcrg}\n'
            else:
                pai__kjt += 'else:\n'
                pai__kjt += f'   res[i] = arg{dtk__cse - rfqw__gxcrg}\n'
            ffhx__yts = True
            break
    if not ffhx__yts:
        if not dqop__lhlj:
            pai__kjt += 'else:\n'
            pai__kjt += '   bodo.libs.array_kernels.setna(res, i)'
        else:
            pai__kjt += 'bodo.libs.array_kernels.setna(res, i)'
    qupwb__ronic = 'A'
    ven__rotb = {f'A{dtk__cse}': f'A[{dtk__cse}]' for dtk__cse in range(len
        (A)) if dtk__cse not in nns__mlmmd}
    tjb__aqq = get_common_broadcasted_type(ohxqc__isads, 'COALESCE')
    return gen_vectorized(asj__kxxhf, ohxqc__isads, ugr__ohlid, pai__kjt,
        tjb__aqq, qupwb__ronic, ven__rotb, qisbk__lelk,
        support_dict_encoding=False)


@numba.generated_jit(nopython=True)
def decode(A):
    if not isinstance(A, (types.Tuple, types.UniTuple)):
        raise_bodo_error('Decode argument must be a tuple')
    for dtk__cse in range(len(A)):
        if isinstance(A[dtk__cse], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.decode',
                ['A'], dtk__cse, container_length=len(A))

    def impl(A):
        return decode_util(A)
    return impl


@numba.generated_jit(nopython=True)
def decode_util(A):
    if len(A) < 3:
        raise_bodo_error('Need at least 3 arguments to DECODE')
    asj__kxxhf = [f'A{dtk__cse}' for dtk__cse in range(len(A))]
    ohxqc__isads = [A[dtk__cse] for dtk__cse in range(len(A))]
    ugr__ohlid = [False] * len(A)
    pai__kjt = ''
    for dtk__cse in range(1, len(A) - 1, 2):
        plf__dnub = 'if' if len(pai__kjt) == 0 else 'elif'
        if A[dtk__cse + 1] == bodo.none:
            ixkvl__nagax = '   bodo.libs.array_kernels.setna(res, i)\n'
        elif bodo.utils.utils.is_array_typ(A[dtk__cse + 1]):
            ixkvl__nagax = (
                f'   if bodo.libs.array_kernels.isna({asj__kxxhf[dtk__cse + 1]}, i):\n'
                )
            ixkvl__nagax += f'      bodo.libs.array_kernels.setna(res, i)\n'
            ixkvl__nagax += f'   else:\n'
            ixkvl__nagax += f'      res[i] = arg{dtk__cse + 1}\n'
        else:
            ixkvl__nagax = f'   res[i] = arg{dtk__cse + 1}\n'
        if A[0] == bodo.none and (bodo.utils.utils.is_array_typ(A[dtk__cse]
            ) or A[dtk__cse] == bodo.none):
            if A[dtk__cse] == bodo.none:
                pai__kjt += f'{plf__dnub} True:\n'
                pai__kjt += ixkvl__nagax
                break
            else:
                pai__kjt += f"""{plf__dnub} bodo.libs.array_kernels.isna({asj__kxxhf[dtk__cse]}, i):
"""
                pai__kjt += ixkvl__nagax
        elif A[0] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[0]):
            if bodo.utils.utils.is_array_typ(A[dtk__cse]):
                pai__kjt += f"""{plf__dnub} (bodo.libs.array_kernels.isna({asj__kxxhf[0]}, i) and bodo.libs.array_kernels.isna({asj__kxxhf[dtk__cse]}, i)) or (not bodo.libs.array_kernels.isna({asj__kxxhf[0]}, i) and not bodo.libs.array_kernels.isna({asj__kxxhf[dtk__cse]}, i) and arg0 == arg{dtk__cse}):
"""
                pai__kjt += ixkvl__nagax
            elif A[dtk__cse] == bodo.none:
                pai__kjt += (
                    f'{plf__dnub} bodo.libs.array_kernels.isna({asj__kxxhf[0]}, i):\n'
                    )
                pai__kjt += ixkvl__nagax
            else:
                pai__kjt += f"""{plf__dnub} (not bodo.libs.array_kernels.isna({asj__kxxhf[0]}, i)) and arg0 == arg{dtk__cse}:
"""
                pai__kjt += ixkvl__nagax
        elif A[dtk__cse] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[dtk__cse]):
            pai__kjt += f"""{plf__dnub} (not bodo.libs.array_kernels.isna({asj__kxxhf[dtk__cse]}, i)) and arg0 == arg{dtk__cse}:
"""
            pai__kjt += ixkvl__nagax
        else:
            pai__kjt += f'{plf__dnub} arg0 == arg{dtk__cse}:\n'
            pai__kjt += ixkvl__nagax
    if len(pai__kjt) > 0:
        pai__kjt += 'else:\n'
    if len(A) % 2 == 0 and A[-1] != bodo.none:
        if bodo.utils.utils.is_array_typ(A[-1]):
            pai__kjt += (
                f'   if bodo.libs.array_kernels.isna({asj__kxxhf[-1]}, i):\n')
            pai__kjt += '      bodo.libs.array_kernels.setna(res, i)\n'
            pai__kjt += '   else:\n'
        pai__kjt += f'      res[i] = arg{len(A) - 1}'
    else:
        pai__kjt += '   bodo.libs.array_kernels.setna(res, i)'
    qupwb__ronic = 'A'
    ven__rotb = {f'A{dtk__cse}': f'A[{dtk__cse}]' for dtk__cse in range(len(A))
        }
    if len(ohxqc__isads) % 2 == 0:
        qjpk__mcq = [ohxqc__isads[0]] + ohxqc__isads[1:-1:2]
        pybzw__phmhb = ohxqc__isads[2::2] + [ohxqc__isads[-1]]
    else:
        qjpk__mcq = [ohxqc__isads[0]] + ohxqc__isads[1::2]
        pybzw__phmhb = ohxqc__isads[2::2]
    pexd__epbz = get_common_broadcasted_type(qjpk__mcq, 'DECODE')
    tjb__aqq = get_common_broadcasted_type(pybzw__phmhb, 'DECODE')
    if tjb__aqq == bodo.none:
        tjb__aqq = pexd__epbz
    olcom__krglo = bodo.utils.utils.is_array_typ(A[0]
        ) and bodo.none not in qjpk__mcq and len(ohxqc__isads) % 2 == 1
    return gen_vectorized(asj__kxxhf, ohxqc__isads, ugr__ohlid, pai__kjt,
        tjb__aqq, qupwb__ronic, ven__rotb, support_dict_encoding=olcom__krglo)
