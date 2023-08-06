import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    rwud__hvpt = hi - lo
    if rwud__hvpt < 2:
        return
    if rwud__hvpt < MIN_MERGE:
        gbijw__jjro = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + gbijw__jjro, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    eza__lhs = minRunLength(rwud__hvpt)
    while True:
        vpg__kan = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if vpg__kan < eza__lhs:
            gcuv__neiyk = rwud__hvpt if rwud__hvpt <= eza__lhs else eza__lhs
            binarySort(key_arrs, lo, lo + gcuv__neiyk, lo + vpg__kan, data)
            vpg__kan = gcuv__neiyk
        stackSize = pushRun(stackSize, runBase, runLen, lo, vpg__kan)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += vpg__kan
        rwud__hvpt -= vpg__kan
        if rwud__hvpt == 0:
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
        bhnc__rkyhs = getitem_arr_tup(key_arrs, start)
        uiyc__uqajo = getitem_arr_tup(data, start)
        wpyyo__afk = lo
        all__kmi = start
        assert wpyyo__afk <= all__kmi
        while wpyyo__afk < all__kmi:
            dssy__pnwa = wpyyo__afk + all__kmi >> 1
            if bhnc__rkyhs < getitem_arr_tup(key_arrs, dssy__pnwa):
                all__kmi = dssy__pnwa
            else:
                wpyyo__afk = dssy__pnwa + 1
        assert wpyyo__afk == all__kmi
        n = start - wpyyo__afk
        copyRange_tup(key_arrs, wpyyo__afk, key_arrs, wpyyo__afk + 1, n)
        copyRange_tup(data, wpyyo__afk, data, wpyyo__afk + 1, n)
        setitem_arr_tup(key_arrs, wpyyo__afk, bhnc__rkyhs)
        setitem_arr_tup(data, wpyyo__afk, uiyc__uqajo)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    wyefc__xfq = lo + 1
    if wyefc__xfq == hi:
        return 1
    if getitem_arr_tup(key_arrs, wyefc__xfq) < getitem_arr_tup(key_arrs, lo):
        wyefc__xfq += 1
        while wyefc__xfq < hi and getitem_arr_tup(key_arrs, wyefc__xfq
            ) < getitem_arr_tup(key_arrs, wyefc__xfq - 1):
            wyefc__xfq += 1
        reverseRange(key_arrs, lo, wyefc__xfq, data)
    else:
        wyefc__xfq += 1
        while wyefc__xfq < hi and getitem_arr_tup(key_arrs, wyefc__xfq
            ) >= getitem_arr_tup(key_arrs, wyefc__xfq - 1):
            wyefc__xfq += 1
    return wyefc__xfq - lo


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
    bnhey__uoe = 0
    while n >= MIN_MERGE:
        bnhey__uoe |= n & 1
        n >>= 1
    return n + bnhey__uoe


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    ari__zhfy = len(key_arrs[0])
    tmpLength = (ari__zhfy >> 1 if ari__zhfy < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    mteo__vuxbw = (5 if ari__zhfy < 120 else 10 if ari__zhfy < 1542 else 19 if
        ari__zhfy < 119151 else 40)
    runBase = np.empty(mteo__vuxbw, np.int64)
    runLen = np.empty(mteo__vuxbw, np.int64)
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
    itb__locm = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert itb__locm >= 0
    base1 += itb__locm
    len1 -= itb__locm
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
    nkog__htab = 0
    ahyjn__yoxx = 1
    if key > getitem_arr_tup(arr, base + hint):
        dlg__kxoqp = _len - hint
        while ahyjn__yoxx < dlg__kxoqp and key > getitem_arr_tup(arr, base +
            hint + ahyjn__yoxx):
            nkog__htab = ahyjn__yoxx
            ahyjn__yoxx = (ahyjn__yoxx << 1) + 1
            if ahyjn__yoxx <= 0:
                ahyjn__yoxx = dlg__kxoqp
        if ahyjn__yoxx > dlg__kxoqp:
            ahyjn__yoxx = dlg__kxoqp
        nkog__htab += hint
        ahyjn__yoxx += hint
    else:
        dlg__kxoqp = hint + 1
        while ahyjn__yoxx < dlg__kxoqp and key <= getitem_arr_tup(arr, base +
            hint - ahyjn__yoxx):
            nkog__htab = ahyjn__yoxx
            ahyjn__yoxx = (ahyjn__yoxx << 1) + 1
            if ahyjn__yoxx <= 0:
                ahyjn__yoxx = dlg__kxoqp
        if ahyjn__yoxx > dlg__kxoqp:
            ahyjn__yoxx = dlg__kxoqp
        tmp = nkog__htab
        nkog__htab = hint - ahyjn__yoxx
        ahyjn__yoxx = hint - tmp
    assert -1 <= nkog__htab and nkog__htab < ahyjn__yoxx and ahyjn__yoxx <= _len
    nkog__htab += 1
    while nkog__htab < ahyjn__yoxx:
        ffd__mih = nkog__htab + (ahyjn__yoxx - nkog__htab >> 1)
        if key > getitem_arr_tup(arr, base + ffd__mih):
            nkog__htab = ffd__mih + 1
        else:
            ahyjn__yoxx = ffd__mih
    assert nkog__htab == ahyjn__yoxx
    return ahyjn__yoxx


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    ahyjn__yoxx = 1
    nkog__htab = 0
    if key < getitem_arr_tup(arr, base + hint):
        dlg__kxoqp = hint + 1
        while ahyjn__yoxx < dlg__kxoqp and key < getitem_arr_tup(arr, base +
            hint - ahyjn__yoxx):
            nkog__htab = ahyjn__yoxx
            ahyjn__yoxx = (ahyjn__yoxx << 1) + 1
            if ahyjn__yoxx <= 0:
                ahyjn__yoxx = dlg__kxoqp
        if ahyjn__yoxx > dlg__kxoqp:
            ahyjn__yoxx = dlg__kxoqp
        tmp = nkog__htab
        nkog__htab = hint - ahyjn__yoxx
        ahyjn__yoxx = hint - tmp
    else:
        dlg__kxoqp = _len - hint
        while ahyjn__yoxx < dlg__kxoqp and key >= getitem_arr_tup(arr, base +
            hint + ahyjn__yoxx):
            nkog__htab = ahyjn__yoxx
            ahyjn__yoxx = (ahyjn__yoxx << 1) + 1
            if ahyjn__yoxx <= 0:
                ahyjn__yoxx = dlg__kxoqp
        if ahyjn__yoxx > dlg__kxoqp:
            ahyjn__yoxx = dlg__kxoqp
        nkog__htab += hint
        ahyjn__yoxx += hint
    assert -1 <= nkog__htab and nkog__htab < ahyjn__yoxx and ahyjn__yoxx <= _len
    nkog__htab += 1
    while nkog__htab < ahyjn__yoxx:
        ffd__mih = nkog__htab + (ahyjn__yoxx - nkog__htab >> 1)
        if key < getitem_arr_tup(arr, base + ffd__mih):
            ahyjn__yoxx = ffd__mih
        else:
            nkog__htab = ffd__mih + 1
    assert nkog__htab == ahyjn__yoxx
    return ahyjn__yoxx


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
        lljry__ema = 0
        ylh__lmpp = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                ylh__lmpp += 1
                lljry__ema = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                lljry__ema += 1
                ylh__lmpp = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not lljry__ema | ylh__lmpp < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            lljry__ema = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if lljry__ema != 0:
                copyRange_tup(tmp, cursor1, arr, dest, lljry__ema)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, lljry__ema)
                dest += lljry__ema
                cursor1 += lljry__ema
                len1 -= lljry__ema
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            ylh__lmpp = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if ylh__lmpp != 0:
                copyRange_tup(arr, cursor2, arr, dest, ylh__lmpp)
                copyRange_tup(arr_data, cursor2, arr_data, dest, ylh__lmpp)
                dest += ylh__lmpp
                cursor2 += ylh__lmpp
                len2 -= ylh__lmpp
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
            if not lljry__ema >= MIN_GALLOP | ylh__lmpp >= MIN_GALLOP:
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
        lljry__ema = 0
        ylh__lmpp = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                lljry__ema += 1
                ylh__lmpp = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                ylh__lmpp += 1
                lljry__ema = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not lljry__ema | ylh__lmpp < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            lljry__ema = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if lljry__ema != 0:
                dest -= lljry__ema
                cursor1 -= lljry__ema
                len1 -= lljry__ema
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, lljry__ema)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    lljry__ema)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            ylh__lmpp = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if ylh__lmpp != 0:
                dest -= ylh__lmpp
                cursor2 -= ylh__lmpp
                len2 -= ylh__lmpp
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, ylh__lmpp)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    ylh__lmpp)
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
            if not lljry__ema >= MIN_GALLOP | ylh__lmpp >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    clrf__pybq = len(key_arrs[0])
    if tmpLength < minCapacity:
        cvgh__uwuhb = minCapacity
        cvgh__uwuhb |= cvgh__uwuhb >> 1
        cvgh__uwuhb |= cvgh__uwuhb >> 2
        cvgh__uwuhb |= cvgh__uwuhb >> 4
        cvgh__uwuhb |= cvgh__uwuhb >> 8
        cvgh__uwuhb |= cvgh__uwuhb >> 16
        cvgh__uwuhb += 1
        if cvgh__uwuhb < 0:
            cvgh__uwuhb = minCapacity
        else:
            cvgh__uwuhb = min(cvgh__uwuhb, clrf__pybq >> 1)
        tmp = alloc_arr_tup(cvgh__uwuhb, key_arrs)
        tmp_data = alloc_arr_tup(cvgh__uwuhb, data)
        tmpLength = cvgh__uwuhb
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        azhzb__vmtk = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = azhzb__vmtk


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    pens__xfb = arr_tup.count
    gprxc__ahlp = 'def f(arr_tup, lo, hi):\n'
    for i in range(pens__xfb):
        gprxc__ahlp += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        gprxc__ahlp += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        gprxc__ahlp += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    gprxc__ahlp += '  return\n'
    snhl__vchu = {}
    exec(gprxc__ahlp, {}, snhl__vchu)
    nvzd__nde = snhl__vchu['f']
    return nvzd__nde


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    pens__xfb = src_arr_tup.count
    assert pens__xfb == dst_arr_tup.count
    gprxc__ahlp = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(pens__xfb):
        gprxc__ahlp += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    gprxc__ahlp += '  return\n'
    snhl__vchu = {}
    exec(gprxc__ahlp, {'copyRange': copyRange}, snhl__vchu)
    basfi__uxacy = snhl__vchu['f']
    return basfi__uxacy


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    pens__xfb = src_arr_tup.count
    assert pens__xfb == dst_arr_tup.count
    gprxc__ahlp = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(pens__xfb):
        gprxc__ahlp += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    gprxc__ahlp += '  return\n'
    snhl__vchu = {}
    exec(gprxc__ahlp, {'copyElement': copyElement}, snhl__vchu)
    basfi__uxacy = snhl__vchu['f']
    return basfi__uxacy


def getitem_arr_tup(arr_tup, ind):
    ifs__twm = [arr[ind] for arr in arr_tup]
    return tuple(ifs__twm)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    pens__xfb = arr_tup.count
    gprxc__ahlp = 'def f(arr_tup, ind):\n'
    gprxc__ahlp += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(pens__xfb)]), ',' if pens__xfb == 1 else '')
    snhl__vchu = {}
    exec(gprxc__ahlp, {}, snhl__vchu)
    lei__yqf = snhl__vchu['f']
    return lei__yqf


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, hcfg__jxp in zip(arr_tup, val_tup):
        arr[ind] = hcfg__jxp


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    pens__xfb = arr_tup.count
    gprxc__ahlp = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(pens__xfb):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            gprxc__ahlp += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            gprxc__ahlp += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    gprxc__ahlp += '  return\n'
    snhl__vchu = {}
    exec(gprxc__ahlp, {}, snhl__vchu)
    lei__yqf = snhl__vchu['f']
    return lei__yqf


def test():
    import time
    diog__cwl = time.time()
    chz__bootr = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((chz__bootr,), 0, 3, data)
    print('compile time', time.time() - diog__cwl)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    tomf__uwrkv = np.random.ranf(n)
    rfi__icwwv = pd.DataFrame({'A': tomf__uwrkv, 'B': data[0], 'C': data[1]})
    diog__cwl = time.time()
    nzqw__ibrpv = rfi__icwwv.sort_values('A', inplace=False)
    nolbt__vnco = time.time()
    sort((tomf__uwrkv,), 0, n, data)
    print('Bodo', time.time() - nolbt__vnco, 'Numpy', nolbt__vnco - diog__cwl)
    np.testing.assert_almost_equal(data[0], nzqw__ibrpv.B.values)
    np.testing.assert_almost_equal(data[1], nzqw__ibrpv.C.values)


if __name__ == '__main__':
    test()
