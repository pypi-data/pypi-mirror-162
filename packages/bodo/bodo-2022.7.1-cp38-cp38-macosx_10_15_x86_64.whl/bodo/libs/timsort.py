import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    huzu__trvf = hi - lo
    if huzu__trvf < 2:
        return
    if huzu__trvf < MIN_MERGE:
        plz__zwb = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + plz__zwb, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    rcnr__saebb = minRunLength(huzu__trvf)
    while True:
        kje__hso = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if kje__hso < rcnr__saebb:
            ppghy__lqgqq = (huzu__trvf if huzu__trvf <= rcnr__saebb else
                rcnr__saebb)
            binarySort(key_arrs, lo, lo + ppghy__lqgqq, lo + kje__hso, data)
            kje__hso = ppghy__lqgqq
        stackSize = pushRun(stackSize, runBase, runLen, lo, kje__hso)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += kje__hso
        huzu__trvf -= kje__hso
        if huzu__trvf == 0:
            break
    assert lo == hi
    stackSize, tmpLength, tmp, tmp_data, minGallop = mergeForceCollapse(
        stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
        tmp_data, minGallop)
    assert stackSize == 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def binarySort(key_arrs, lo, hi, start, data):
    assert lo <= start and start <= hi
    if start == lo:
        start += 1
    while start < hi:
        bnu__okw = getitem_arr_tup(key_arrs, start)
        uxrp__fdvo = getitem_arr_tup(data, start)
        slf__srsy = lo
        joxr__iaraq = start
        assert slf__srsy <= joxr__iaraq
        while slf__srsy < joxr__iaraq:
            fyys__bmxky = slf__srsy + joxr__iaraq >> 1
            if bnu__okw < getitem_arr_tup(key_arrs, fyys__bmxky):
                joxr__iaraq = fyys__bmxky
            else:
                slf__srsy = fyys__bmxky + 1
        assert slf__srsy == joxr__iaraq
        n = start - slf__srsy
        copyRange_tup(key_arrs, slf__srsy, key_arrs, slf__srsy + 1, n)
        copyRange_tup(data, slf__srsy, data, slf__srsy + 1, n)
        setitem_arr_tup(key_arrs, slf__srsy, bnu__okw)
        setitem_arr_tup(data, slf__srsy, uxrp__fdvo)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    ugoc__kytsa = lo + 1
    if ugoc__kytsa == hi:
        return 1
    if getitem_arr_tup(key_arrs, ugoc__kytsa) < getitem_arr_tup(key_arrs, lo):
        ugoc__kytsa += 1
        while ugoc__kytsa < hi and getitem_arr_tup(key_arrs, ugoc__kytsa
            ) < getitem_arr_tup(key_arrs, ugoc__kytsa - 1):
            ugoc__kytsa += 1
        reverseRange(key_arrs, lo, ugoc__kytsa, data)
    else:
        ugoc__kytsa += 1
        while ugoc__kytsa < hi and getitem_arr_tup(key_arrs, ugoc__kytsa
            ) >= getitem_arr_tup(key_arrs, ugoc__kytsa - 1):
            ugoc__kytsa += 1
    return ugoc__kytsa - lo


@numba.njit(no_cpython_wrapper=True, cache=True)
def reverseRange(key_arrs, lo, hi, data):
    hi -= 1
    while lo < hi:
        swap_arrs(key_arrs, lo, hi)
        swap_arrs(data, lo, hi)
        lo += 1
        hi -= 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def minRunLength(n):
    assert n >= 0
    ccc__xvw = 0
    while n >= MIN_MERGE:
        ccc__xvw |= n & 1
        n >>= 1
    return n + ccc__xvw


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    rxaab__eaevr = len(key_arrs[0])
    tmpLength = (rxaab__eaevr >> 1 if rxaab__eaevr < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    vrj__uchga = (5 if rxaab__eaevr < 120 else 10 if rxaab__eaevr < 1542 else
        19 if rxaab__eaevr < 119151 else 40)
    runBase = np.empty(vrj__uchga, np.int64)
    runLen = np.empty(vrj__uchga, np.int64)
    return stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def pushRun(stackSize, runBase, runLen, runBase_val, runLen_val):
    runBase[stackSize] = runBase_val
    runLen[stackSize] = runLen_val
    stackSize += 1
    return stackSize


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeCollapse(stackSize, runBase, runLen, key_arrs, data, tmpLength,
    tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n >= 1 and runLen[n - 1] <= runLen[n] + runLen[n + 1
            ] or n >= 2 and runLen[n - 2] <= runLen[n] + runLen[n - 1]:
            if runLen[n - 1] < runLen[n + 1]:
                n -= 1
        elif runLen[n] > runLen[n + 1]:
            break
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeForceCollapse(stackSize, runBase, runLen, key_arrs, data,
    tmpLength, tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n > 0 and runLen[n - 1] < runLen[n + 1]:
            n -= 1
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeAt(stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
    tmp_data, minGallop, i):
    assert stackSize >= 2
    assert i >= 0
    assert i == stackSize - 2 or i == stackSize - 3
    base1 = runBase[i]
    len1 = runLen[i]
    base2 = runBase[i + 1]
    len2 = runLen[i + 1]
    assert len1 > 0 and len2 > 0
    assert base1 + len1 == base2
    runLen[i] = len1 + len2
    if i == stackSize - 3:
        runBase[i + 1] = runBase[i + 2]
        runLen[i + 1] = runLen[i + 2]
    stackSize -= 1
    cfu__tun = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert cfu__tun >= 0
    base1 += cfu__tun
    len1 -= cfu__tun
    if len1 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    len2 = gallopLeft(getitem_arr_tup(key_arrs, base1 + len1 - 1), key_arrs,
        base2, len2, len2 - 1)
    assert len2 >= 0
    if len2 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    if len1 <= len2:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len1)
        minGallop = mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    else:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len2)
        minGallop = mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopLeft(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    cbn__wnic = 0
    fvwtp__xjqjc = 1
    if key > getitem_arr_tup(arr, base + hint):
        gpkke__ttakn = _len - hint
        while fvwtp__xjqjc < gpkke__ttakn and key > getitem_arr_tup(arr, 
            base + hint + fvwtp__xjqjc):
            cbn__wnic = fvwtp__xjqjc
            fvwtp__xjqjc = (fvwtp__xjqjc << 1) + 1
            if fvwtp__xjqjc <= 0:
                fvwtp__xjqjc = gpkke__ttakn
        if fvwtp__xjqjc > gpkke__ttakn:
            fvwtp__xjqjc = gpkke__ttakn
        cbn__wnic += hint
        fvwtp__xjqjc += hint
    else:
        gpkke__ttakn = hint + 1
        while fvwtp__xjqjc < gpkke__ttakn and key <= getitem_arr_tup(arr, 
            base + hint - fvwtp__xjqjc):
            cbn__wnic = fvwtp__xjqjc
            fvwtp__xjqjc = (fvwtp__xjqjc << 1) + 1
            if fvwtp__xjqjc <= 0:
                fvwtp__xjqjc = gpkke__ttakn
        if fvwtp__xjqjc > gpkke__ttakn:
            fvwtp__xjqjc = gpkke__ttakn
        tmp = cbn__wnic
        cbn__wnic = hint - fvwtp__xjqjc
        fvwtp__xjqjc = hint - tmp
    assert -1 <= cbn__wnic and cbn__wnic < fvwtp__xjqjc and fvwtp__xjqjc <= _len
    cbn__wnic += 1
    while cbn__wnic < fvwtp__xjqjc:
        pccc__xheeo = cbn__wnic + (fvwtp__xjqjc - cbn__wnic >> 1)
        if key > getitem_arr_tup(arr, base + pccc__xheeo):
            cbn__wnic = pccc__xheeo + 1
        else:
            fvwtp__xjqjc = pccc__xheeo
    assert cbn__wnic == fvwtp__xjqjc
    return fvwtp__xjqjc


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    fvwtp__xjqjc = 1
    cbn__wnic = 0
    if key < getitem_arr_tup(arr, base + hint):
        gpkke__ttakn = hint + 1
        while fvwtp__xjqjc < gpkke__ttakn and key < getitem_arr_tup(arr, 
            base + hint - fvwtp__xjqjc):
            cbn__wnic = fvwtp__xjqjc
            fvwtp__xjqjc = (fvwtp__xjqjc << 1) + 1
            if fvwtp__xjqjc <= 0:
                fvwtp__xjqjc = gpkke__ttakn
        if fvwtp__xjqjc > gpkke__ttakn:
            fvwtp__xjqjc = gpkke__ttakn
        tmp = cbn__wnic
        cbn__wnic = hint - fvwtp__xjqjc
        fvwtp__xjqjc = hint - tmp
    else:
        gpkke__ttakn = _len - hint
        while fvwtp__xjqjc < gpkke__ttakn and key >= getitem_arr_tup(arr, 
            base + hint + fvwtp__xjqjc):
            cbn__wnic = fvwtp__xjqjc
            fvwtp__xjqjc = (fvwtp__xjqjc << 1) + 1
            if fvwtp__xjqjc <= 0:
                fvwtp__xjqjc = gpkke__ttakn
        if fvwtp__xjqjc > gpkke__ttakn:
            fvwtp__xjqjc = gpkke__ttakn
        cbn__wnic += hint
        fvwtp__xjqjc += hint
    assert -1 <= cbn__wnic and cbn__wnic < fvwtp__xjqjc and fvwtp__xjqjc <= _len
    cbn__wnic += 1
    while cbn__wnic < fvwtp__xjqjc:
        pccc__xheeo = cbn__wnic + (fvwtp__xjqjc - cbn__wnic >> 1)
        if key < getitem_arr_tup(arr, base + pccc__xheeo):
            fvwtp__xjqjc = pccc__xheeo
        else:
            cbn__wnic = pccc__xheeo + 1
    assert cbn__wnic == fvwtp__xjqjc
    return fvwtp__xjqjc


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base1, tmp, 0, len1)
    copyRange_tup(arr_data, base1, tmp_data, 0, len1)
    cursor1 = 0
    cursor2 = base2
    dest = base1
    setitem_arr_tup(arr, dest, getitem_arr_tup(arr, cursor2))
    copyElement_tup(arr_data, cursor2, arr_data, dest)
    cursor2 += 1
    dest += 1
    len2 -= 1
    if len2 == 0:
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
        return minGallop
    if len1 == 1:
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
        return minGallop
    len1, len2, cursor1, cursor2, dest, minGallop = mergeLo_inner(key_arrs,
        data, tmp_data, len1, len2, tmp, cursor1, cursor2, dest, minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len1 == 1:
        assert len2 > 0
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
    elif len1 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len2 == 0
        assert len1 > 1
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo_inner(arr, arr_data, tmp_data, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        kreo__anw = 0
        ivarm__gcz = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                ivarm__gcz += 1
                kreo__anw = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                kreo__anw += 1
                ivarm__gcz = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not kreo__anw | ivarm__gcz < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            kreo__anw = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if kreo__anw != 0:
                copyRange_tup(tmp, cursor1, arr, dest, kreo__anw)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, kreo__anw)
                dest += kreo__anw
                cursor1 += kreo__anw
                len1 -= kreo__anw
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            ivarm__gcz = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if ivarm__gcz != 0:
                copyRange_tup(arr, cursor2, arr, dest, ivarm__gcz)
                copyRange_tup(arr_data, cursor2, arr_data, dest, ivarm__gcz)
                dest += ivarm__gcz
                cursor2 += ivarm__gcz
                len2 -= ivarm__gcz
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor1, arr, dest)
            copyElement_tup(tmp_data, cursor1, arr_data, dest)
            cursor1 += 1
            dest += 1
            len1 -= 1
            if len1 == 1:
                return len1, len2, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not kreo__anw >= MIN_GALLOP | ivarm__gcz >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base2, tmp, 0, len2)
    copyRange_tup(arr_data, base2, tmp_data, 0, len2)
    cursor1 = base1 + len1 - 1
    cursor2 = len2 - 1
    dest = base2 + len2 - 1
    copyElement_tup(arr, cursor1, arr, dest)
    copyElement_tup(arr_data, cursor1, arr_data, dest)
    cursor1 -= 1
    dest -= 1
    len1 -= 1
    if len1 == 0:
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
        return minGallop
    if len2 == 1:
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
        return minGallop
    len1, len2, tmp, cursor1, cursor2, dest, minGallop = mergeHi_inner(key_arrs
        , data, tmp_data, base1, len1, len2, tmp, cursor1, cursor2, dest,
        minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len2 == 1:
        assert len1 > 0
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
    elif len2 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len1 == 0
        assert len2 > 0
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi_inner(arr, arr_data, tmp_data, base1, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        kreo__anw = 0
        ivarm__gcz = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                kreo__anw += 1
                ivarm__gcz = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                ivarm__gcz += 1
                kreo__anw = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not kreo__anw | ivarm__gcz < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            kreo__anw = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if kreo__anw != 0:
                dest -= kreo__anw
                cursor1 -= kreo__anw
                len1 -= kreo__anw
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, kreo__anw)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    kreo__anw)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            ivarm__gcz = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if ivarm__gcz != 0:
                dest -= ivarm__gcz
                cursor2 -= ivarm__gcz
                len2 -= ivarm__gcz
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, ivarm__gcz)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    ivarm__gcz)
                if len2 <= 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor1, arr, dest)
            copyElement_tup(arr_data, cursor1, arr_data, dest)
            cursor1 -= 1
            dest -= 1
            len1 -= 1
            if len1 == 0:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not kreo__anw >= MIN_GALLOP | ivarm__gcz >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    xki__knbem = len(key_arrs[0])
    if tmpLength < minCapacity:
        ngs__wtsln = minCapacity
        ngs__wtsln |= ngs__wtsln >> 1
        ngs__wtsln |= ngs__wtsln >> 2
        ngs__wtsln |= ngs__wtsln >> 4
        ngs__wtsln |= ngs__wtsln >> 8
        ngs__wtsln |= ngs__wtsln >> 16
        ngs__wtsln += 1
        if ngs__wtsln < 0:
            ngs__wtsln = minCapacity
        else:
            ngs__wtsln = min(ngs__wtsln, xki__knbem >> 1)
        tmp = alloc_arr_tup(ngs__wtsln, key_arrs)
        tmp_data = alloc_arr_tup(ngs__wtsln, data)
        tmpLength = ngs__wtsln
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        atk__cwda = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = atk__cwda


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    mdx__bjmmn = arr_tup.count
    fftrk__rxh = 'def f(arr_tup, lo, hi):\n'
    for i in range(mdx__bjmmn):
        fftrk__rxh += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        fftrk__rxh += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        fftrk__rxh += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    fftrk__rxh += '  return\n'
    iqktu__ggtx = {}
    exec(fftrk__rxh, {}, iqktu__ggtx)
    ydvfn__wciy = iqktu__ggtx['f']
    return ydvfn__wciy


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    mdx__bjmmn = src_arr_tup.count
    assert mdx__bjmmn == dst_arr_tup.count
    fftrk__rxh = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(mdx__bjmmn):
        fftrk__rxh += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    fftrk__rxh += '  return\n'
    iqktu__ggtx = {}
    exec(fftrk__rxh, {'copyRange': copyRange}, iqktu__ggtx)
    uhdlf__jwar = iqktu__ggtx['f']
    return uhdlf__jwar


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    mdx__bjmmn = src_arr_tup.count
    assert mdx__bjmmn == dst_arr_tup.count
    fftrk__rxh = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(mdx__bjmmn):
        fftrk__rxh += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    fftrk__rxh += '  return\n'
    iqktu__ggtx = {}
    exec(fftrk__rxh, {'copyElement': copyElement}, iqktu__ggtx)
    uhdlf__jwar = iqktu__ggtx['f']
    return uhdlf__jwar


def getitem_arr_tup(arr_tup, ind):
    adw__whn = [arr[ind] for arr in arr_tup]
    return tuple(adw__whn)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    mdx__bjmmn = arr_tup.count
    fftrk__rxh = 'def f(arr_tup, ind):\n'
    fftrk__rxh += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(mdx__bjmmn)]), ',' if mdx__bjmmn == 1 else '')
    iqktu__ggtx = {}
    exec(fftrk__rxh, {}, iqktu__ggtx)
    qake__rpznl = iqktu__ggtx['f']
    return qake__rpznl


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, rnmai__ibcj in zip(arr_tup, val_tup):
        arr[ind] = rnmai__ibcj


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    mdx__bjmmn = arr_tup.count
    fftrk__rxh = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(mdx__bjmmn):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            fftrk__rxh += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            fftrk__rxh += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    fftrk__rxh += '  return\n'
    iqktu__ggtx = {}
    exec(fftrk__rxh, {}, iqktu__ggtx)
    qake__rpznl = iqktu__ggtx['f']
    return qake__rpznl


def test():
    import time
    fvx__xenvt = time.time()
    cti__jmvc = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((cti__jmvc,), 0, 3, data)
    print('compile time', time.time() - fvx__xenvt)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    pvqaw__bln = np.random.ranf(n)
    nff__acefq = pd.DataFrame({'A': pvqaw__bln, 'B': data[0], 'C': data[1]})
    fvx__xenvt = time.time()
    xuvy__szna = nff__acefq.sort_values('A', inplace=False)
    ayxld__pge = time.time()
    sort((pvqaw__bln,), 0, n, data)
    print('Bodo', time.time() - ayxld__pge, 'Numpy', ayxld__pge - fvx__xenvt)
    np.testing.assert_almost_equal(data[0], xuvy__szna.B.values)
    np.testing.assert_almost_equal(data[1], xuvy__szna.C.values)


if __name__ == '__main__':
    test()
