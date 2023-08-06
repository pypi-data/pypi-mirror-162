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
    for alo__iala in range(len(A)):
        if isinstance(A[alo__iala], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.coalesce',
                ['A'], alo__iala, container_length=len(A))

    def impl(A):
        return coalesce_util(A)
    return impl


def coalesce_util(A):
    return


@overload(coalesce_util, no_unliteral=True)
def overload_coalesce_util(A):
    if len(A) == 0:
        raise_bodo_error('Cannot coalesce 0 columns')
    qpo__jpazz = None
    gqens__htma = []
    for alo__iala in range(len(A)):
        if A[alo__iala] == bodo.none:
            gqens__htma.append(alo__iala)
        elif not bodo.utils.utils.is_array_typ(A[alo__iala]):
            for jzb__vfstv in range(alo__iala + 1, len(A)):
                gqens__htma.append(jzb__vfstv)
                if bodo.utils.utils.is_array_typ(A[jzb__vfstv]):
                    qpo__jpazz = f'A[{jzb__vfstv}]'
            break
    hstnt__pxq = [f'A{alo__iala}' for alo__iala in range(len(A)) if 
        alo__iala not in gqens__htma]
    ujnc__hsbi = [A[alo__iala] for alo__iala in range(len(A)) if alo__iala
         not in gqens__htma]
    wlef__gjikz = [False] * (len(A) - len(gqens__htma))
    djz__mylau = ''
    vyklm__pta = True
    wgdf__ctm = False
    qnit__ghf = 0
    for alo__iala in range(len(A)):
        if alo__iala in gqens__htma:
            qnit__ghf += 1
            continue
        elif bodo.utils.utils.is_array_typ(A[alo__iala]):
            cytit__gjwl = 'if' if vyklm__pta else 'elif'
            djz__mylau += (
                f'{cytit__gjwl} not bodo.libs.array_kernels.isna(A{alo__iala}, i):\n'
                )
            djz__mylau += f'   res[i] = arg{alo__iala - qnit__ghf}\n'
            vyklm__pta = False
        else:
            assert not wgdf__ctm, 'should not encounter more than one scalar due to dead column pruning'
            if vyklm__pta:
                djz__mylau += f'res[i] = arg{alo__iala - qnit__ghf}\n'
            else:
                djz__mylau += 'else:\n'
                djz__mylau += f'   res[i] = arg{alo__iala - qnit__ghf}\n'
            wgdf__ctm = True
            break
    if not wgdf__ctm:
        if not vyklm__pta:
            djz__mylau += 'else:\n'
            djz__mylau += '   bodo.libs.array_kernels.setna(res, i)'
        else:
            djz__mylau += 'bodo.libs.array_kernels.setna(res, i)'
    ieia__ydrsf = 'A'
    qvde__uank = {f'A{alo__iala}': f'A[{alo__iala}]' for alo__iala in range
        (len(A)) if alo__iala not in gqens__htma}
    eqcm__rom = get_common_broadcasted_type(ujnc__hsbi, 'COALESCE')
    return gen_vectorized(hstnt__pxq, ujnc__hsbi, wlef__gjikz, djz__mylau,
        eqcm__rom, ieia__ydrsf, qvde__uank, qpo__jpazz,
        support_dict_encoding=False)


@numba.generated_jit(nopython=True)
def decode(A):
    if not isinstance(A, (types.Tuple, types.UniTuple)):
        raise_bodo_error('Decode argument must be a tuple')
    for alo__iala in range(len(A)):
        if isinstance(A[alo__iala], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.decode',
                ['A'], alo__iala, container_length=len(A))

    def impl(A):
        return decode_util(A)
    return impl


@numba.generated_jit(nopython=True)
def decode_util(A):
    if len(A) < 3:
        raise_bodo_error('Need at least 3 arguments to DECODE')
    hstnt__pxq = [f'A{alo__iala}' for alo__iala in range(len(A))]
    ujnc__hsbi = [A[alo__iala] for alo__iala in range(len(A))]
    wlef__gjikz = [False] * len(A)
    djz__mylau = ''
    for alo__iala in range(1, len(A) - 1, 2):
        cytit__gjwl = 'if' if len(djz__mylau) == 0 else 'elif'
        if A[alo__iala + 1] == bodo.none:
            lur__vxkm = '   bodo.libs.array_kernels.setna(res, i)\n'
        elif bodo.utils.utils.is_array_typ(A[alo__iala + 1]):
            lur__vxkm = (
                f'   if bodo.libs.array_kernels.isna({hstnt__pxq[alo__iala + 1]}, i):\n'
                )
            lur__vxkm += f'      bodo.libs.array_kernels.setna(res, i)\n'
            lur__vxkm += f'   else:\n'
            lur__vxkm += f'      res[i] = arg{alo__iala + 1}\n'
        else:
            lur__vxkm = f'   res[i] = arg{alo__iala + 1}\n'
        if A[0] == bodo.none and (bodo.utils.utils.is_array_typ(A[alo__iala
            ]) or A[alo__iala] == bodo.none):
            if A[alo__iala] == bodo.none:
                djz__mylau += f'{cytit__gjwl} True:\n'
                djz__mylau += lur__vxkm
                break
            else:
                djz__mylau += f"""{cytit__gjwl} bodo.libs.array_kernels.isna({hstnt__pxq[alo__iala]}, i):
"""
                djz__mylau += lur__vxkm
        elif A[0] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[0]):
            if bodo.utils.utils.is_array_typ(A[alo__iala]):
                djz__mylau += f"""{cytit__gjwl} (bodo.libs.array_kernels.isna({hstnt__pxq[0]}, i) and bodo.libs.array_kernels.isna({hstnt__pxq[alo__iala]}, i)) or (not bodo.libs.array_kernels.isna({hstnt__pxq[0]}, i) and not bodo.libs.array_kernels.isna({hstnt__pxq[alo__iala]}, i) and arg0 == arg{alo__iala}):
"""
                djz__mylau += lur__vxkm
            elif A[alo__iala] == bodo.none:
                djz__mylau += (
                    f'{cytit__gjwl} bodo.libs.array_kernels.isna({hstnt__pxq[0]}, i):\n'
                    )
                djz__mylau += lur__vxkm
            else:
                djz__mylau += f"""{cytit__gjwl} (not bodo.libs.array_kernels.isna({hstnt__pxq[0]}, i)) and arg0 == arg{alo__iala}:
"""
                djz__mylau += lur__vxkm
        elif A[alo__iala] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[alo__iala]):
            djz__mylau += f"""{cytit__gjwl} (not bodo.libs.array_kernels.isna({hstnt__pxq[alo__iala]}, i)) and arg0 == arg{alo__iala}:
"""
            djz__mylau += lur__vxkm
        else:
            djz__mylau += f'{cytit__gjwl} arg0 == arg{alo__iala}:\n'
            djz__mylau += lur__vxkm
    if len(djz__mylau) > 0:
        djz__mylau += 'else:\n'
    if len(A) % 2 == 0 and A[-1] != bodo.none:
        if bodo.utils.utils.is_array_typ(A[-1]):
            djz__mylau += (
                f'   if bodo.libs.array_kernels.isna({hstnt__pxq[-1]}, i):\n')
            djz__mylau += '      bodo.libs.array_kernels.setna(res, i)\n'
            djz__mylau += '   else:\n'
        djz__mylau += f'      res[i] = arg{len(A) - 1}'
    else:
        djz__mylau += '   bodo.libs.array_kernels.setna(res, i)'
    ieia__ydrsf = 'A'
    qvde__uank = {f'A{alo__iala}': f'A[{alo__iala}]' for alo__iala in range
        (len(A))}
    if len(ujnc__hsbi) % 2 == 0:
        zzqyq__xbyvy = [ujnc__hsbi[0]] + ujnc__hsbi[1:-1:2]
        gfz__ofw = ujnc__hsbi[2::2] + [ujnc__hsbi[-1]]
    else:
        zzqyq__xbyvy = [ujnc__hsbi[0]] + ujnc__hsbi[1::2]
        gfz__ofw = ujnc__hsbi[2::2]
    twbx__kmis = get_common_broadcasted_type(zzqyq__xbyvy, 'DECODE')
    eqcm__rom = get_common_broadcasted_type(gfz__ofw, 'DECODE')
    if eqcm__rom == bodo.none:
        eqcm__rom = twbx__kmis
    pnxu__cfnpm = bodo.utils.utils.is_array_typ(A[0]
        ) and bodo.none not in zzqyq__xbyvy and len(ujnc__hsbi) % 2 == 1
    return gen_vectorized(hstnt__pxq, ujnc__hsbi, wlef__gjikz, djz__mylau,
        eqcm__rom, ieia__ydrsf, qvde__uank, support_dict_encoding=pnxu__cfnpm)
