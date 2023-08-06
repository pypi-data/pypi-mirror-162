import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    cpyqj__ytxh = hi - lo
    if cpyqj__ytxh < 2:
        return
    if cpyqj__ytxh < MIN_MERGE:
        anmdf__beqi = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + anmdf__beqi, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    kxkso__nkkli = minRunLength(cpyqj__ytxh)
    while True:
        qupi__pbz = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if qupi__pbz < kxkso__nkkli:
            elac__zyqey = (cpyqj__ytxh if cpyqj__ytxh <= kxkso__nkkli else
                kxkso__nkkli)
            binarySort(key_arrs, lo, lo + elac__zyqey, lo + qupi__pbz, data)
            qupi__pbz = elac__zyqey
        stackSize = pushRun(stackSize, runBase, runLen, lo, qupi__pbz)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += qupi__pbz
        cpyqj__ytxh -= qupi__pbz
        if cpyqj__ytxh == 0:
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
        rcypp__imt = getitem_arr_tup(key_arrs, start)
        bamtj__bbwcw = getitem_arr_tup(data, start)
        dsipi__bpmze = lo
        wazs__makeb = start
        assert dsipi__bpmze <= wazs__makeb
        while dsipi__bpmze < wazs__makeb:
            jckaq__vtbl = dsipi__bpmze + wazs__makeb >> 1
            if rcypp__imt < getitem_arr_tup(key_arrs, jckaq__vtbl):
                wazs__makeb = jckaq__vtbl
            else:
                dsipi__bpmze = jckaq__vtbl + 1
        assert dsipi__bpmze == wazs__makeb
        n = start - dsipi__bpmze
        copyRange_tup(key_arrs, dsipi__bpmze, key_arrs, dsipi__bpmze + 1, n)
        copyRange_tup(data, dsipi__bpmze, data, dsipi__bpmze + 1, n)
        setitem_arr_tup(key_arrs, dsipi__bpmze, rcypp__imt)
        setitem_arr_tup(data, dsipi__bpmze, bamtj__bbwcw)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    sgkze__btw = lo + 1
    if sgkze__btw == hi:
        return 1
    if getitem_arr_tup(key_arrs, sgkze__btw) < getitem_arr_tup(key_arrs, lo):
        sgkze__btw += 1
        while sgkze__btw < hi and getitem_arr_tup(key_arrs, sgkze__btw
            ) < getitem_arr_tup(key_arrs, sgkze__btw - 1):
            sgkze__btw += 1
        reverseRange(key_arrs, lo, sgkze__btw, data)
    else:
        sgkze__btw += 1
        while sgkze__btw < hi and getitem_arr_tup(key_arrs, sgkze__btw
            ) >= getitem_arr_tup(key_arrs, sgkze__btw - 1):
            sgkze__btw += 1
    return sgkze__btw - lo


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
    ayg__rawa = 0
    while n >= MIN_MERGE:
        ayg__rawa |= n & 1
        n >>= 1
    return n + ayg__rawa


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    fqm__bhrq = len(key_arrs[0])
    tmpLength = (fqm__bhrq >> 1 if fqm__bhrq < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    pxz__fkup = (5 if fqm__bhrq < 120 else 10 if fqm__bhrq < 1542 else 19 if
        fqm__bhrq < 119151 else 40)
    runBase = np.empty(pxz__fkup, np.int64)
    runLen = np.empty(pxz__fkup, np.int64)
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
    tpcjp__atidw = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert tpcjp__atidw >= 0
    base1 += tpcjp__atidw
    len1 -= tpcjp__atidw
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
    vuq__ifv = 0
    gmkbz__gger = 1
    if key > getitem_arr_tup(arr, base + hint):
        tnhs__mhb = _len - hint
        while gmkbz__gger < tnhs__mhb and key > getitem_arr_tup(arr, base +
            hint + gmkbz__gger):
            vuq__ifv = gmkbz__gger
            gmkbz__gger = (gmkbz__gger << 1) + 1
            if gmkbz__gger <= 0:
                gmkbz__gger = tnhs__mhb
        if gmkbz__gger > tnhs__mhb:
            gmkbz__gger = tnhs__mhb
        vuq__ifv += hint
        gmkbz__gger += hint
    else:
        tnhs__mhb = hint + 1
        while gmkbz__gger < tnhs__mhb and key <= getitem_arr_tup(arr, base +
            hint - gmkbz__gger):
            vuq__ifv = gmkbz__gger
            gmkbz__gger = (gmkbz__gger << 1) + 1
            if gmkbz__gger <= 0:
                gmkbz__gger = tnhs__mhb
        if gmkbz__gger > tnhs__mhb:
            gmkbz__gger = tnhs__mhb
        tmp = vuq__ifv
        vuq__ifv = hint - gmkbz__gger
        gmkbz__gger = hint - tmp
    assert -1 <= vuq__ifv and vuq__ifv < gmkbz__gger and gmkbz__gger <= _len
    vuq__ifv += 1
    while vuq__ifv < gmkbz__gger:
        bfv__hmlej = vuq__ifv + (gmkbz__gger - vuq__ifv >> 1)
        if key > getitem_arr_tup(arr, base + bfv__hmlej):
            vuq__ifv = bfv__hmlej + 1
        else:
            gmkbz__gger = bfv__hmlej
    assert vuq__ifv == gmkbz__gger
    return gmkbz__gger


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    gmkbz__gger = 1
    vuq__ifv = 0
    if key < getitem_arr_tup(arr, base + hint):
        tnhs__mhb = hint + 1
        while gmkbz__gger < tnhs__mhb and key < getitem_arr_tup(arr, base +
            hint - gmkbz__gger):
            vuq__ifv = gmkbz__gger
            gmkbz__gger = (gmkbz__gger << 1) + 1
            if gmkbz__gger <= 0:
                gmkbz__gger = tnhs__mhb
        if gmkbz__gger > tnhs__mhb:
            gmkbz__gger = tnhs__mhb
        tmp = vuq__ifv
        vuq__ifv = hint - gmkbz__gger
        gmkbz__gger = hint - tmp
    else:
        tnhs__mhb = _len - hint
        while gmkbz__gger < tnhs__mhb and key >= getitem_arr_tup(arr, base +
            hint + gmkbz__gger):
            vuq__ifv = gmkbz__gger
            gmkbz__gger = (gmkbz__gger << 1) + 1
            if gmkbz__gger <= 0:
                gmkbz__gger = tnhs__mhb
        if gmkbz__gger > tnhs__mhb:
            gmkbz__gger = tnhs__mhb
        vuq__ifv += hint
        gmkbz__gger += hint
    assert -1 <= vuq__ifv and vuq__ifv < gmkbz__gger and gmkbz__gger <= _len
    vuq__ifv += 1
    while vuq__ifv < gmkbz__gger:
        bfv__hmlej = vuq__ifv + (gmkbz__gger - vuq__ifv >> 1)
        if key < getitem_arr_tup(arr, base + bfv__hmlej):
            gmkbz__gger = bfv__hmlej
        else:
            vuq__ifv = bfv__hmlej + 1
    assert vuq__ifv == gmkbz__gger
    return gmkbz__gger


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
        frkcd__uzfc = 0
        azw__huge = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                azw__huge += 1
                frkcd__uzfc = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                frkcd__uzfc += 1
                azw__huge = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not frkcd__uzfc | azw__huge < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            frkcd__uzfc = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if frkcd__uzfc != 0:
                copyRange_tup(tmp, cursor1, arr, dest, frkcd__uzfc)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, frkcd__uzfc)
                dest += frkcd__uzfc
                cursor1 += frkcd__uzfc
                len1 -= frkcd__uzfc
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            azw__huge = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if azw__huge != 0:
                copyRange_tup(arr, cursor2, arr, dest, azw__huge)
                copyRange_tup(arr_data, cursor2, arr_data, dest, azw__huge)
                dest += azw__huge
                cursor2 += azw__huge
                len2 -= azw__huge
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
            if not frkcd__uzfc >= MIN_GALLOP | azw__huge >= MIN_GALLOP:
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
        frkcd__uzfc = 0
        azw__huge = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                frkcd__uzfc += 1
                azw__huge = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                azw__huge += 1
                frkcd__uzfc = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not frkcd__uzfc | azw__huge < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            frkcd__uzfc = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if frkcd__uzfc != 0:
                dest -= frkcd__uzfc
                cursor1 -= frkcd__uzfc
                len1 -= frkcd__uzfc
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, frkcd__uzfc)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    frkcd__uzfc)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            azw__huge = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if azw__huge != 0:
                dest -= azw__huge
                cursor2 -= azw__huge
                len2 -= azw__huge
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, azw__huge)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    azw__huge)
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
            if not frkcd__uzfc >= MIN_GALLOP | azw__huge >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    kzoq__oswsf = len(key_arrs[0])
    if tmpLength < minCapacity:
        fqml__vttsq = minCapacity
        fqml__vttsq |= fqml__vttsq >> 1
        fqml__vttsq |= fqml__vttsq >> 2
        fqml__vttsq |= fqml__vttsq >> 4
        fqml__vttsq |= fqml__vttsq >> 8
        fqml__vttsq |= fqml__vttsq >> 16
        fqml__vttsq += 1
        if fqml__vttsq < 0:
            fqml__vttsq = minCapacity
        else:
            fqml__vttsq = min(fqml__vttsq, kzoq__oswsf >> 1)
        tmp = alloc_arr_tup(fqml__vttsq, key_arrs)
        tmp_data = alloc_arr_tup(fqml__vttsq, data)
        tmpLength = fqml__vttsq
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        fmjh__sqb = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = fmjh__sqb


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    xst__qfxwb = arr_tup.count
    irtie__cbpd = 'def f(arr_tup, lo, hi):\n'
    for i in range(xst__qfxwb):
        irtie__cbpd += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        irtie__cbpd += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        irtie__cbpd += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    irtie__cbpd += '  return\n'
    iapb__imzq = {}
    exec(irtie__cbpd, {}, iapb__imzq)
    bljdx__llo = iapb__imzq['f']
    return bljdx__llo


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    xst__qfxwb = src_arr_tup.count
    assert xst__qfxwb == dst_arr_tup.count
    irtie__cbpd = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(xst__qfxwb):
        irtie__cbpd += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    irtie__cbpd += '  return\n'
    iapb__imzq = {}
    exec(irtie__cbpd, {'copyRange': copyRange}, iapb__imzq)
    cwo__gmr = iapb__imzq['f']
    return cwo__gmr


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    xst__qfxwb = src_arr_tup.count
    assert xst__qfxwb == dst_arr_tup.count
    irtie__cbpd = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(xst__qfxwb):
        irtie__cbpd += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    irtie__cbpd += '  return\n'
    iapb__imzq = {}
    exec(irtie__cbpd, {'copyElement': copyElement}, iapb__imzq)
    cwo__gmr = iapb__imzq['f']
    return cwo__gmr


def getitem_arr_tup(arr_tup, ind):
    mzar__ymewy = [arr[ind] for arr in arr_tup]
    return tuple(mzar__ymewy)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    xst__qfxwb = arr_tup.count
    irtie__cbpd = 'def f(arr_tup, ind):\n'
    irtie__cbpd += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(xst__qfxwb)]), ',' if xst__qfxwb == 1 else '')
    iapb__imzq = {}
    exec(irtie__cbpd, {}, iapb__imzq)
    dztok__ojue = iapb__imzq['f']
    return dztok__ojue


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, eoetd__losdi in zip(arr_tup, val_tup):
        arr[ind] = eoetd__losdi


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    xst__qfxwb = arr_tup.count
    irtie__cbpd = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(xst__qfxwb):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            irtie__cbpd += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            irtie__cbpd += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    irtie__cbpd += '  return\n'
    iapb__imzq = {}
    exec(irtie__cbpd, {}, iapb__imzq)
    dztok__ojue = iapb__imzq['f']
    return dztok__ojue


def test():
    import time
    jeb__nra = time.time()
    qjsq__cecfk = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((qjsq__cecfk,), 0, 3, data)
    print('compile time', time.time() - jeb__nra)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    ttem__cecc = np.random.ranf(n)
    wdu__gro = pd.DataFrame({'A': ttem__cecc, 'B': data[0], 'C': data[1]})
    jeb__nra = time.time()
    yznk__sjp = wdu__gro.sort_values('A', inplace=False)
    kks__mep = time.time()
    sort((ttem__cecc,), 0, n, data)
    print('Bodo', time.time() - kks__mep, 'Numpy', kks__mep - jeb__nra)
    np.testing.assert_almost_equal(data[0], yznk__sjp.B.values)
    np.testing.assert_almost_equal(data[1], yznk__sjp.C.values)


if __name__ == '__main__':
    test()
