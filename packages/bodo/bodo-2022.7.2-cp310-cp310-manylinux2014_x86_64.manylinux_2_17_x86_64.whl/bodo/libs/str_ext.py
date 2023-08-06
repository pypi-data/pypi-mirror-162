import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, bound_function, infer_getattr, infer_global, signature
from numba.extending import intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_str, is_overload_constant_int, is_overload_constant_str


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


ll.add_symbol('del_str', hstr_ext.del_str)
ll.add_symbol('unicode_to_utf8', hstr_ext.unicode_to_utf8)
ll.add_symbol('memcmp', hstr_ext.memcmp)
ll.add_symbol('int_to_hex', hstr_ext.int_to_hex)
string_type = types.unicode_type


@numba.njit
def contains_regex(e, in_str):
    with numba.objmode(res='bool_'):
        res = bool(e.search(in_str))
    return res


@numba.generated_jit
def str_findall_count(regex, in_str):

    def _str_findall_count_impl(regex, in_str):
        with numba.objmode(res='int64'):
            res = len(regex.findall(in_str))
        return res
    return _str_findall_count_impl


utf8_str_type = types.ArrayCTypes(types.Array(types.uint8, 1, 'C'))


@intrinsic
def unicode_to_utf8_and_len(typingctx, str_typ):
    assert str_typ in (string_type, types.Optional(string_type)) or isinstance(
        str_typ, types.StringLiteral)
    hzyai__hvm = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        uwsu__jeyco, = args
        imyo__atn = cgutils.create_struct_proxy(string_type)(context,
            builder, value=uwsu__jeyco)
        htbyq__aki = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        wgl__phfg = cgutils.create_struct_proxy(hzyai__hvm)(context, builder)
        is_ascii = builder.icmp_unsigned('==', imyo__atn.is_ascii, lir.
            Constant(imyo__atn.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (uwmiy__ccr, oqr__qupg):
            with uwmiy__ccr:
                context.nrt.incref(builder, string_type, uwsu__jeyco)
                htbyq__aki.data = imyo__atn.data
                htbyq__aki.meminfo = imyo__atn.meminfo
                wgl__phfg.f1 = imyo__atn.length
            with oqr__qupg:
                xro__euh = lir.FunctionType(lir.IntType(64), [lir.IntType(8
                    ).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                csla__izpcg = cgutils.get_or_insert_function(builder.module,
                    xro__euh, name='unicode_to_utf8')
                xwhh__hwuhn = context.get_constant_null(types.voidptr)
                akabf__kggy = builder.call(csla__izpcg, [xwhh__hwuhn,
                    imyo__atn.data, imyo__atn.length, imyo__atn.kind])
                wgl__phfg.f1 = akabf__kggy
                asovi__gzh = builder.add(akabf__kggy, lir.Constant(lir.
                    IntType(64), 1))
                htbyq__aki.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=asovi__gzh, align=32)
                htbyq__aki.data = context.nrt.meminfo_data(builder,
                    htbyq__aki.meminfo)
                builder.call(csla__izpcg, [htbyq__aki.data, imyo__atn.data,
                    imyo__atn.length, imyo__atn.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    htbyq__aki.data, [akabf__kggy]))
        wgl__phfg.f0 = htbyq__aki._getvalue()
        return wgl__phfg._getvalue()
    return hzyai__hvm(string_type), codegen


def unicode_to_utf8(s):
    return s


@overload(unicode_to_utf8)
def overload_unicode_to_utf8(s):
    return lambda s: unicode_to_utf8_and_len(s)[0]


@overload(max)
def overload_builtin_max(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload(min)
def overload_builtin_min(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@intrinsic
def memcmp(typingctx, dest_t, src_t, count_t=None):

    def codegen(context, builder, sig, args):
        xro__euh = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        xsx__dkrs = cgutils.get_or_insert_function(builder.module, xro__euh,
            name='memcmp')
        return builder.call(xsx__dkrs, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    gdq__pmoe = n(10)

    def impl(n):
        if n == 0:
            return 1
        wjr__hss = 0
        if n < 0:
            n = -n
            wjr__hss += 1
        while n > 0:
            n = n // gdq__pmoe
            wjr__hss += 1
        return wjr__hss
    return impl


class StdStringType(types.Opaque):

    def __init__(self):
        super(StdStringType, self).__init__(name='StdStringType')


std_str_type = StdStringType()
register_model(StdStringType)(models.OpaqueModel)
del_str = types.ExternalFunction('del_str', types.void(std_str_type))
get_c_str = types.ExternalFunction('get_c_str', types.voidptr(std_str_type))
dummy_use = numba.njit(lambda a: None)


@overload(int)
def int_str_overload(in_str, base=10):
    if in_str == string_type:
        if is_overload_constant_int(base) and get_overload_const_int(base
            ) == 10:

            def _str_to_int_impl(in_str, base=10):
                val = _str_to_int64(in_str._data, in_str._length)
                dummy_use(in_str)
                return val
            return _str_to_int_impl

        def _str_to_int_base_impl(in_str, base=10):
            val = _str_to_int64_base(in_str._data, in_str._length, base)
            dummy_use(in_str)
            return val
        return _str_to_int_base_impl


@infer_global(float)
class StrToFloat(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        [cfhf__hrb] = args
        if isinstance(cfhf__hrb, StdStringType):
            return signature(types.float64, cfhf__hrb)
        if cfhf__hrb == string_type:
            return signature(types.float64, cfhf__hrb)


ll.add_symbol('init_string_const', hstr_ext.init_string_const)
ll.add_symbol('get_c_str', hstr_ext.get_c_str)
ll.add_symbol('str_to_int64', hstr_ext.str_to_int64)
ll.add_symbol('str_to_uint64', hstr_ext.str_to_uint64)
ll.add_symbol('str_to_int64_base', hstr_ext.str_to_int64_base)
ll.add_symbol('str_to_float64', hstr_ext.str_to_float64)
ll.add_symbol('str_to_float32', hstr_ext.str_to_float32)
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('str_from_float32', hstr_ext.str_from_float32)
ll.add_symbol('str_from_float64', hstr_ext.str_from_float64)
get_std_str_len = types.ExternalFunction('get_str_len', signature(types.
    intp, std_str_type))
init_string_from_chars = types.ExternalFunction('init_string_const',
    std_str_type(types.voidptr, types.intp))
_str_to_int64 = types.ExternalFunction('str_to_int64', signature(types.
    int64, types.voidptr, types.int64))
_str_to_uint64 = types.ExternalFunction('str_to_uint64', signature(types.
    uint64, types.voidptr, types.int64))
_str_to_int64_base = types.ExternalFunction('str_to_int64_base', signature(
    types.int64, types.voidptr, types.int64, types.int64))


def gen_unicode_to_std_str(context, builder, unicode_val):
    imyo__atn = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    xro__euh = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(8
        ).as_pointer(), lir.IntType(64)])
    blcj__czjz = cgutils.get_or_insert_function(builder.module, xro__euh,
        name='init_string_const')
    return builder.call(blcj__czjz, [imyo__atn.data, imyo__atn.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        osts__dfx = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(osts__dfx._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return osts__dfx
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    imyo__atn = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return imyo__atn.data


@intrinsic
def unicode_to_std_str(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_unicode_to_std_str(context, builder, args[0])
    return std_str_type(string_type), codegen


@intrinsic
def std_str_to_unicode(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_std_str_to_unicode(context, builder, args[0], True)
    return string_type(std_str_type), codegen


class RandomAccessStringArrayType(types.ArrayCompatible):

    def __init__(self):
        super(RandomAccessStringArrayType, self).__init__(name=
            'RandomAccessStringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    def copy(self):
        RandomAccessStringArrayType()


random_access_string_array = RandomAccessStringArrayType()


@register_model(RandomAccessStringArrayType)
class RandomAccessStringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yyrc__uwqd = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, yyrc__uwqd)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        mca__svqw, = args
        yflx__lto = types.List(string_type)
        biud__jpwn = numba.cpython.listobj.ListInstance.allocate(context,
            builder, yflx__lto, mca__svqw)
        biud__jpwn.size = mca__svqw
        vmdlm__ard = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        vmdlm__ard.data = biud__jpwn.value
        return vmdlm__ard._getvalue()
    return random_access_string_array(types.intp), codegen


@overload(operator.getitem, no_unliteral=True)
def random_access_str_arr_getitem(A, ind):
    if A != random_access_string_array:
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]


@overload(operator.setitem)
def random_access_str_arr_setitem(A, idx, val):
    if A != random_access_string_array:
        return
    if isinstance(idx, types.Integer):
        assert val == string_type

        def impl_scalar(A, idx, val):
            A._data[idx] = val
        return impl_scalar


@overload(len, no_unliteral=True)
def overload_str_arr_len(A):
    if A == random_access_string_array:
        return lambda A: len(A._data)


@overload_attribute(RandomAccessStringArrayType, 'shape')
def overload_str_arr_shape(A):
    return lambda A: (len(A._data),)


def alloc_random_access_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_str_ext_alloc_random_access_string_array
    ) = alloc_random_access_str_arr_equiv
str_from_float32 = types.ExternalFunction('str_from_float32', types.void(
    types.voidptr, types.float32))
str_from_float64 = types.ExternalFunction('str_from_float64', types.void(
    types.voidptr, types.float64))


def float_to_str(s, v):
    pass


@overload(float_to_str)
def float_to_str_overload(s, v):
    assert isinstance(v, types.Float)
    if v == types.float32:
        return lambda s, v: str_from_float32(s._data, v)
    return lambda s, v: str_from_float64(s._data, v)


@overload(str)
def float_str_overload(v):
    if isinstance(v, types.Float):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(v):
            if v == 0:
                return '0.0'
            xzg__yjdxp = 0
            mdaa__dkbn = v
            if mdaa__dkbn < 0:
                xzg__yjdxp = 1
                mdaa__dkbn = -mdaa__dkbn
            if mdaa__dkbn < 1:
                qhnge__lbsg = 1
            else:
                qhnge__lbsg = 1 + int(np.floor(np.log10(mdaa__dkbn)))
            length = xzg__yjdxp + qhnge__lbsg + 1 + 6
            s = numba.cpython.unicode._malloc_string(kind, 1, length, True)
            float_to_str(s, v)
            return s
        return impl


@overload(format, no_unliteral=True)
def overload_format(value, format_spec=''):
    if is_overload_constant_str(format_spec) and get_overload_const_str(
        format_spec) == '':

        def impl_fast(value, format_spec=''):
            return str(value)
        return impl_fast

    def impl(value, format_spec=''):
        with numba.objmode(res='string'):
            res = format(value, format_spec)
        return res
    return impl


@lower_cast(StdStringType, types.float64)
def cast_str_to_float64(context, builder, fromty, toty, val):
    xro__euh = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).as_pointer()]
        )
    blcj__czjz = cgutils.get_or_insert_function(builder.module, xro__euh,
        name='str_to_float64')
    res = builder.call(blcj__czjz, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    xro__euh = lir.FunctionType(lir.FloatType(), [lir.IntType(8).as_pointer()])
    blcj__czjz = cgutils.get_or_insert_function(builder.module, xro__euh,
        name='str_to_float32')
    res = builder.call(blcj__czjz, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.float64)
def cast_unicode_str_to_float64(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float64(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.float32)
def cast_unicode_str_to_float32(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float32(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.int64)
@lower_cast(string_type, types.int32)
@lower_cast(string_type, types.int16)
@lower_cast(string_type, types.int8)
def cast_unicode_str_to_int64(context, builder, fromty, toty, val):
    imyo__atn = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    xro__euh = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8)
        .as_pointer(), lir.IntType(64)])
    blcj__czjz = cgutils.get_or_insert_function(builder.module, xro__euh,
        name='str_to_int64')
    res = builder.call(blcj__czjz, (imyo__atn.data, imyo__atn.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    imyo__atn = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    xro__euh = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8)
        .as_pointer(), lir.IntType(64)])
    blcj__czjz = cgutils.get_or_insert_function(builder.module, xro__euh,
        name='str_to_uint64')
    res = builder.call(blcj__czjz, (imyo__atn.data, imyo__atn.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        bsr__btwph = ', '.join('e{}'.format(rwqf__dwmbf) for rwqf__dwmbf in
            range(len(args)))
        if bsr__btwph:
            bsr__btwph += ', '
        xozz__gvwjj = ', '.join("{} = ''".format(a) for a in kws.keys())
        qmbml__stj = f'def format_stub(string, {bsr__btwph} {xozz__gvwjj}):\n'
        qmbml__stj += '    pass\n'
        dgmk__vjq = {}
        exec(qmbml__stj, {}, dgmk__vjq)
        dbqgh__owec = dgmk__vjq['format_stub']
        xzqjs__drr = numba.core.utils.pysignature(dbqgh__owec)
        ikp__hch = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, ikp__hch).replace(pysig=xzqjs__drr)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    ahlt__trcze = pat is not None and len(pat) > 1
    if ahlt__trcze:
        kmayi__tdolb = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    biud__jpwn = len(arr)
    kgywt__qtmnw = 0
    dlgqj__tui = 0
    for rwqf__dwmbf in numba.parfors.parfor.internal_prange(biud__jpwn):
        if bodo.libs.array_kernels.isna(arr, rwqf__dwmbf):
            continue
        if ahlt__trcze:
            dcsf__flpm = kmayi__tdolb.split(arr[rwqf__dwmbf], maxsplit=n)
        elif pat == '':
            dcsf__flpm = [''] + list(arr[rwqf__dwmbf]) + ['']
        else:
            dcsf__flpm = arr[rwqf__dwmbf].split(pat, n)
        kgywt__qtmnw += len(dcsf__flpm)
        for s in dcsf__flpm:
            dlgqj__tui += bodo.libs.str_arr_ext.get_utf8_size(s)
    eakus__nzzvq = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        biud__jpwn, (kgywt__qtmnw, dlgqj__tui), bodo.libs.str_arr_ext.
        string_array_type)
    gzl__hmxb = bodo.libs.array_item_arr_ext.get_offsets(eakus__nzzvq)
    iyvl__wulxy = bodo.libs.array_item_arr_ext.get_null_bitmap(eakus__nzzvq)
    xtpq__fog = bodo.libs.array_item_arr_ext.get_data(eakus__nzzvq)
    vxunp__bed = 0
    for qcx__tqgt in numba.parfors.parfor.internal_prange(biud__jpwn):
        gzl__hmxb[qcx__tqgt] = vxunp__bed
        if bodo.libs.array_kernels.isna(arr, qcx__tqgt):
            bodo.libs.int_arr_ext.set_bit_to_arr(iyvl__wulxy, qcx__tqgt, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(iyvl__wulxy, qcx__tqgt, 1)
        if ahlt__trcze:
            dcsf__flpm = kmayi__tdolb.split(arr[qcx__tqgt], maxsplit=n)
        elif pat == '':
            dcsf__flpm = [''] + list(arr[qcx__tqgt]) + ['']
        else:
            dcsf__flpm = arr[qcx__tqgt].split(pat, n)
        aon__yvs = len(dcsf__flpm)
        for loqva__pplax in range(aon__yvs):
            s = dcsf__flpm[loqva__pplax]
            xtpq__fog[vxunp__bed] = s
            vxunp__bed += 1
    gzl__hmxb[biud__jpwn] = vxunp__bed
    return eakus__nzzvq


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                syl__yvoje = '-0x'
                x = x * -1
            else:
                syl__yvoje = '0x'
            x = np.uint64(x)
            if x == 0:
                pur__xqx = 1
            else:
                pur__xqx = fast_ceil_log2(x + 1)
                pur__xqx = (pur__xqx + 3) // 4
            length = len(syl__yvoje) + pur__xqx
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, syl__yvoje._data,
                len(syl__yvoje), 1)
            int_to_hex(output, pur__xqx, len(syl__yvoje), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    tcxg__swlqd = 0 if x & x - 1 == 0 else 1
    enshl__lfha = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    jtwgi__way = 32
    for rwqf__dwmbf in range(len(enshl__lfha)):
        awd__ytflm = 0 if x & enshl__lfha[rwqf__dwmbf] == 0 else jtwgi__way
        tcxg__swlqd = tcxg__swlqd + awd__ytflm
        x = x >> awd__ytflm
        jtwgi__way = jtwgi__way >> 1
    return tcxg__swlqd


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        txvdy__ptxgf = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        xro__euh = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        iybrq__ishb = cgutils.get_or_insert_function(builder.module,
            xro__euh, name='int_to_hex')
        pmbpr__cygu = builder.inttoptr(builder.add(builder.ptrtoint(
            txvdy__ptxgf.data, lir.IntType(64)), header_len), lir.IntType(8
            ).as_pointer())
        builder.call(iybrq__ishb, (pmbpr__cygu, out_len, int_val))
    return types.void(output, out_len, header_len, int_val), codegen


def alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    pass


@overload(alloc_empty_bytes_or_string_data)
def overload_alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    typ = typ.instance_type if isinstance(typ, types.TypeRef) else typ
    if typ == bodo.bytes_type:
        return lambda typ, kind, length, is_ascii=0: np.empty(length, np.uint8)
    if typ == string_type:
        return (lambda typ, kind, length, is_ascii=0: numba.cpython.unicode
            ._empty_string(kind, length, is_ascii))
    raise BodoError(
        f'Internal Error: Expected Bytes or String type, found {typ}')


def get_unicode_or_numpy_data(val):
    pass


@overload(get_unicode_or_numpy_data)
def overload_get_unicode_or_numpy_data(val):
    if val == string_type:
        return lambda val: val._data
    if isinstance(val, types.Array):
        return lambda val: val.ctypes
    raise BodoError(
        f'Internal Error: Expected String or Numpy Array, found {val}')
