import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    bnp__vhfd = hi - lo
    if bnp__vhfd < 2:
        return
    if bnp__vhfd < MIN_MERGE:
        iqgt__axpiu = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + iqgt__axpiu, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    rfb__hubpy = minRunLength(bnp__vhfd)
    while True:
        qyqk__mgm = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if qyqk__mgm < rfb__hubpy:
            fxcwc__bgwpf = bnp__vhfd if bnp__vhfd <= rfb__hubpy else rfb__hubpy
            binarySort(key_arrs, lo, lo + fxcwc__bgwpf, lo + qyqk__mgm, data)
            qyqk__mgm = fxcwc__bgwpf
        stackSize = pushRun(stackSize, runBase, runLen, lo, qyqk__mgm)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += qyqk__mgm
        bnp__vhfd -= qyqk__mgm
        if bnp__vhfd == 0:
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
        qcoin__ribz = getitem_arr_tup(key_arrs, start)
        fec__dwojh = getitem_arr_tup(data, start)
        pwy__ofxso = lo
        jyhs__scl = start
        assert pwy__ofxso <= jyhs__scl
        while pwy__ofxso < jyhs__scl:
            bfrak__vmerq = pwy__ofxso + jyhs__scl >> 1
            if qcoin__ribz < getitem_arr_tup(key_arrs, bfrak__vmerq):
                jyhs__scl = bfrak__vmerq
            else:
                pwy__ofxso = bfrak__vmerq + 1
        assert pwy__ofxso == jyhs__scl
        n = start - pwy__ofxso
        copyRange_tup(key_arrs, pwy__ofxso, key_arrs, pwy__ofxso + 1, n)
        copyRange_tup(data, pwy__ofxso, data, pwy__ofxso + 1, n)
        setitem_arr_tup(key_arrs, pwy__ofxso, qcoin__ribz)
        setitem_arr_tup(data, pwy__ofxso, fec__dwojh)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    hrjzo__anddp = lo + 1
    if hrjzo__anddp == hi:
        return 1
    if getitem_arr_tup(key_arrs, hrjzo__anddp) < getitem_arr_tup(key_arrs, lo):
        hrjzo__anddp += 1
        while hrjzo__anddp < hi and getitem_arr_tup(key_arrs, hrjzo__anddp
            ) < getitem_arr_tup(key_arrs, hrjzo__anddp - 1):
            hrjzo__anddp += 1
        reverseRange(key_arrs, lo, hrjzo__anddp, data)
    else:
        hrjzo__anddp += 1
        while hrjzo__anddp < hi and getitem_arr_tup(key_arrs, hrjzo__anddp
            ) >= getitem_arr_tup(key_arrs, hrjzo__anddp - 1):
            hrjzo__anddp += 1
    return hrjzo__anddp - lo


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
    cdnne__rdr = 0
    while n >= MIN_MERGE:
        cdnne__rdr |= n & 1
        n >>= 1
    return n + cdnne__rdr


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    bduqq__qif = len(key_arrs[0])
    tmpLength = (bduqq__qif >> 1 if bduqq__qif < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    fkge__kczjr = (5 if bduqq__qif < 120 else 10 if bduqq__qif < 1542 else 
        19 if bduqq__qif < 119151 else 40)
    runBase = np.empty(fkge__kczjr, np.int64)
    runLen = np.empty(fkge__kczjr, np.int64)
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
    fzg__gfuej = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert fzg__gfuej >= 0
    base1 += fzg__gfuej
    len1 -= fzg__gfuej
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
    wgy__rnxx = 0
    wuah__pxpoo = 1
    if key > getitem_arr_tup(arr, base + hint):
        lbg__leznu = _len - hint
        while wuah__pxpoo < lbg__leznu and key > getitem_arr_tup(arr, base +
            hint + wuah__pxpoo):
            wgy__rnxx = wuah__pxpoo
            wuah__pxpoo = (wuah__pxpoo << 1) + 1
            if wuah__pxpoo <= 0:
                wuah__pxpoo = lbg__leznu
        if wuah__pxpoo > lbg__leznu:
            wuah__pxpoo = lbg__leznu
        wgy__rnxx += hint
        wuah__pxpoo += hint
    else:
        lbg__leznu = hint + 1
        while wuah__pxpoo < lbg__leznu and key <= getitem_arr_tup(arr, base +
            hint - wuah__pxpoo):
            wgy__rnxx = wuah__pxpoo
            wuah__pxpoo = (wuah__pxpoo << 1) + 1
            if wuah__pxpoo <= 0:
                wuah__pxpoo = lbg__leznu
        if wuah__pxpoo > lbg__leznu:
            wuah__pxpoo = lbg__leznu
        tmp = wgy__rnxx
        wgy__rnxx = hint - wuah__pxpoo
        wuah__pxpoo = hint - tmp
    assert -1 <= wgy__rnxx and wgy__rnxx < wuah__pxpoo and wuah__pxpoo <= _len
    wgy__rnxx += 1
    while wgy__rnxx < wuah__pxpoo:
        vtq__uzc = wgy__rnxx + (wuah__pxpoo - wgy__rnxx >> 1)
        if key > getitem_arr_tup(arr, base + vtq__uzc):
            wgy__rnxx = vtq__uzc + 1
        else:
            wuah__pxpoo = vtq__uzc
    assert wgy__rnxx == wuah__pxpoo
    return wuah__pxpoo


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    wuah__pxpoo = 1
    wgy__rnxx = 0
    if key < getitem_arr_tup(arr, base + hint):
        lbg__leznu = hint + 1
        while wuah__pxpoo < lbg__leznu and key < getitem_arr_tup(arr, base +
            hint - wuah__pxpoo):
            wgy__rnxx = wuah__pxpoo
            wuah__pxpoo = (wuah__pxpoo << 1) + 1
            if wuah__pxpoo <= 0:
                wuah__pxpoo = lbg__leznu
        if wuah__pxpoo > lbg__leznu:
            wuah__pxpoo = lbg__leznu
        tmp = wgy__rnxx
        wgy__rnxx = hint - wuah__pxpoo
        wuah__pxpoo = hint - tmp
    else:
        lbg__leznu = _len - hint
        while wuah__pxpoo < lbg__leznu and key >= getitem_arr_tup(arr, base +
            hint + wuah__pxpoo):
            wgy__rnxx = wuah__pxpoo
            wuah__pxpoo = (wuah__pxpoo << 1) + 1
            if wuah__pxpoo <= 0:
                wuah__pxpoo = lbg__leznu
        if wuah__pxpoo > lbg__leznu:
            wuah__pxpoo = lbg__leznu
        wgy__rnxx += hint
        wuah__pxpoo += hint
    assert -1 <= wgy__rnxx and wgy__rnxx < wuah__pxpoo and wuah__pxpoo <= _len
    wgy__rnxx += 1
    while wgy__rnxx < wuah__pxpoo:
        vtq__uzc = wgy__rnxx + (wuah__pxpoo - wgy__rnxx >> 1)
        if key < getitem_arr_tup(arr, base + vtq__uzc):
            wuah__pxpoo = vtq__uzc
        else:
            wgy__rnxx = vtq__uzc + 1
    assert wgy__rnxx == wuah__pxpoo
    return wuah__pxpoo


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
        wrh__hlgq = 0
        psrf__jdjwk = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                psrf__jdjwk += 1
                wrh__hlgq = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                wrh__hlgq += 1
                psrf__jdjwk = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not wrh__hlgq | psrf__jdjwk < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            wrh__hlgq = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if wrh__hlgq != 0:
                copyRange_tup(tmp, cursor1, arr, dest, wrh__hlgq)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, wrh__hlgq)
                dest += wrh__hlgq
                cursor1 += wrh__hlgq
                len1 -= wrh__hlgq
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            psrf__jdjwk = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if psrf__jdjwk != 0:
                copyRange_tup(arr, cursor2, arr, dest, psrf__jdjwk)
                copyRange_tup(arr_data, cursor2, arr_data, dest, psrf__jdjwk)
                dest += psrf__jdjwk
                cursor2 += psrf__jdjwk
                len2 -= psrf__jdjwk
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
            if not wrh__hlgq >= MIN_GALLOP | psrf__jdjwk >= MIN_GALLOP:
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
        wrh__hlgq = 0
        psrf__jdjwk = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                wrh__hlgq += 1
                psrf__jdjwk = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                psrf__jdjwk += 1
                wrh__hlgq = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not wrh__hlgq | psrf__jdjwk < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            wrh__hlgq = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if wrh__hlgq != 0:
                dest -= wrh__hlgq
                cursor1 -= wrh__hlgq
                len1 -= wrh__hlgq
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, wrh__hlgq)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    wrh__hlgq)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            psrf__jdjwk = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if psrf__jdjwk != 0:
                dest -= psrf__jdjwk
                cursor2 -= psrf__jdjwk
                len2 -= psrf__jdjwk
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, psrf__jdjwk)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    psrf__jdjwk)
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
            if not wrh__hlgq >= MIN_GALLOP | psrf__jdjwk >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    cof__aczs = len(key_arrs[0])
    if tmpLength < minCapacity:
        saxy__orhx = minCapacity
        saxy__orhx |= saxy__orhx >> 1
        saxy__orhx |= saxy__orhx >> 2
        saxy__orhx |= saxy__orhx >> 4
        saxy__orhx |= saxy__orhx >> 8
        saxy__orhx |= saxy__orhx >> 16
        saxy__orhx += 1
        if saxy__orhx < 0:
            saxy__orhx = minCapacity
        else:
            saxy__orhx = min(saxy__orhx, cof__aczs >> 1)
        tmp = alloc_arr_tup(saxy__orhx, key_arrs)
        tmp_data = alloc_arr_tup(saxy__orhx, data)
        tmpLength = saxy__orhx
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        sdaf__paoyr = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = sdaf__paoyr


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    qrm__lvd = arr_tup.count
    bhg__ipwaz = 'def f(arr_tup, lo, hi):\n'
    for i in range(qrm__lvd):
        bhg__ipwaz += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        bhg__ipwaz += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        bhg__ipwaz += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    bhg__ipwaz += '  return\n'
    sxspf__zdbu = {}
    exec(bhg__ipwaz, {}, sxspf__zdbu)
    yow__wiule = sxspf__zdbu['f']
    return yow__wiule


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    qrm__lvd = src_arr_tup.count
    assert qrm__lvd == dst_arr_tup.count
    bhg__ipwaz = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(qrm__lvd):
        bhg__ipwaz += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    bhg__ipwaz += '  return\n'
    sxspf__zdbu = {}
    exec(bhg__ipwaz, {'copyRange': copyRange}, sxspf__zdbu)
    rrt__azmj = sxspf__zdbu['f']
    return rrt__azmj


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    qrm__lvd = src_arr_tup.count
    assert qrm__lvd == dst_arr_tup.count
    bhg__ipwaz = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(qrm__lvd):
        bhg__ipwaz += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    bhg__ipwaz += '  return\n'
    sxspf__zdbu = {}
    exec(bhg__ipwaz, {'copyElement': copyElement}, sxspf__zdbu)
    rrt__azmj = sxspf__zdbu['f']
    return rrt__azmj


def getitem_arr_tup(arr_tup, ind):
    yfguz__zetr = [arr[ind] for arr in arr_tup]
    return tuple(yfguz__zetr)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    qrm__lvd = arr_tup.count
    bhg__ipwaz = 'def f(arr_tup, ind):\n'
    bhg__ipwaz += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(qrm__lvd)]), ',' if qrm__lvd == 1 else '')
    sxspf__zdbu = {}
    exec(bhg__ipwaz, {}, sxspf__zdbu)
    hxjo__xvty = sxspf__zdbu['f']
    return hxjo__xvty


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, yip__ekjre in zip(arr_tup, val_tup):
        arr[ind] = yip__ekjre


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    qrm__lvd = arr_tup.count
    bhg__ipwaz = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(qrm__lvd):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            bhg__ipwaz += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            bhg__ipwaz += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    bhg__ipwaz += '  return\n'
    sxspf__zdbu = {}
    exec(bhg__ipwaz, {}, sxspf__zdbu)
    hxjo__xvty = sxspf__zdbu['f']
    return hxjo__xvty


def test():
    import time
    osjw__xpqj = time.time()
    nzs__rze = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((nzs__rze,), 0, 3, data)
    print('compile time', time.time() - osjw__xpqj)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    ylfhm__rvj = np.random.ranf(n)
    wtb__jnt = pd.DataFrame({'A': ylfhm__rvj, 'B': data[0], 'C': data[1]})
    osjw__xpqj = time.time()
    nvuai__pbmx = wtb__jnt.sort_values('A', inplace=False)
    vhhg__ztqnd = time.time()
    sort((ylfhm__rvj,), 0, n, data)
    print('Bodo', time.time() - vhhg__ztqnd, 'Numpy', vhhg__ztqnd - osjw__xpqj)
    np.testing.assert_almost_equal(data[0], nvuai__pbmx.B.values)
    np.testing.assert_almost_equal(data[1], nvuai__pbmx.C.values)


if __name__ == '__main__':
    test()
