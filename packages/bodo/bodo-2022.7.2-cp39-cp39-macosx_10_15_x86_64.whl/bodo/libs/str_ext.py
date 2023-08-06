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
    kxedx__cym = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        pcya__txuxc, = args
        ecc__wqtad = cgutils.create_struct_proxy(string_type)(context,
            builder, value=pcya__txuxc)
        cmvbv__reu = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        hmk__dnp = cgutils.create_struct_proxy(kxedx__cym)(context, builder)
        is_ascii = builder.icmp_unsigned('==', ecc__wqtad.is_ascii, lir.
            Constant(ecc__wqtad.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (yemz__gtse, eius__pmdry):
            with yemz__gtse:
                context.nrt.incref(builder, string_type, pcya__txuxc)
                cmvbv__reu.data = ecc__wqtad.data
                cmvbv__reu.meminfo = ecc__wqtad.meminfo
                hmk__dnp.f1 = ecc__wqtad.length
            with eius__pmdry:
                ouhzt__azkr = lir.FunctionType(lir.IntType(64), [lir.
                    IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                    lir.IntType(64), lir.IntType(32)])
                awj__czsax = cgutils.get_or_insert_function(builder.module,
                    ouhzt__azkr, name='unicode_to_utf8')
                teca__rdksf = context.get_constant_null(types.voidptr)
                psb__cuvmn = builder.call(awj__czsax, [teca__rdksf,
                    ecc__wqtad.data, ecc__wqtad.length, ecc__wqtad.kind])
                hmk__dnp.f1 = psb__cuvmn
                nmaus__obegn = builder.add(psb__cuvmn, lir.Constant(lir.
                    IntType(64), 1))
                cmvbv__reu.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=nmaus__obegn, align=32)
                cmvbv__reu.data = context.nrt.meminfo_data(builder,
                    cmvbv__reu.meminfo)
                builder.call(awj__czsax, [cmvbv__reu.data, ecc__wqtad.data,
                    ecc__wqtad.length, ecc__wqtad.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    cmvbv__reu.data, [psb__cuvmn]))
        hmk__dnp.f0 = cmvbv__reu._getvalue()
        return hmk__dnp._getvalue()
    return kxedx__cym(string_type), codegen


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
        ouhzt__azkr = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        qibc__tlhzc = cgutils.get_or_insert_function(builder.module,
            ouhzt__azkr, name='memcmp')
        return builder.call(qibc__tlhzc, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    wxjy__xoufb = n(10)

    def impl(n):
        if n == 0:
            return 1
        cjea__jmbhz = 0
        if n < 0:
            n = -n
            cjea__jmbhz += 1
        while n > 0:
            n = n // wxjy__xoufb
            cjea__jmbhz += 1
        return cjea__jmbhz
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
        [ycyo__txc] = args
        if isinstance(ycyo__txc, StdStringType):
            return signature(types.float64, ycyo__txc)
        if ycyo__txc == string_type:
            return signature(types.float64, ycyo__txc)


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
    ecc__wqtad = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    ouhzt__azkr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    act__chi = cgutils.get_or_insert_function(builder.module, ouhzt__azkr,
        name='init_string_const')
    return builder.call(act__chi, [ecc__wqtad.data, ecc__wqtad.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        ucbrm__xaqva = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(ucbrm__xaqva._data, bodo.libs.str_ext
            .get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return ucbrm__xaqva
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    ecc__wqtad = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return ecc__wqtad.data


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
        mdu__trk = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, mdu__trk)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        jfeto__tmpg, = args
        lbwor__yvhyx = types.List(string_type)
        pgej__pkqcw = numba.cpython.listobj.ListInstance.allocate(context,
            builder, lbwor__yvhyx, jfeto__tmpg)
        pgej__pkqcw.size = jfeto__tmpg
        sttpq__acmxx = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        sttpq__acmxx.data = pgej__pkqcw.value
        return sttpq__acmxx._getvalue()
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
            szlmx__tqe = 0
            egr__nig = v
            if egr__nig < 0:
                szlmx__tqe = 1
                egr__nig = -egr__nig
            if egr__nig < 1:
                dpul__qin = 1
            else:
                dpul__qin = 1 + int(np.floor(np.log10(egr__nig)))
            length = szlmx__tqe + dpul__qin + 1 + 6
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
    ouhzt__azkr = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    act__chi = cgutils.get_or_insert_function(builder.module, ouhzt__azkr,
        name='str_to_float64')
    res = builder.call(act__chi, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    ouhzt__azkr = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    act__chi = cgutils.get_or_insert_function(builder.module, ouhzt__azkr,
        name='str_to_float32')
    res = builder.call(act__chi, (val,))
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
    ecc__wqtad = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    ouhzt__azkr = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    act__chi = cgutils.get_or_insert_function(builder.module, ouhzt__azkr,
        name='str_to_int64')
    res = builder.call(act__chi, (ecc__wqtad.data, ecc__wqtad.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    ecc__wqtad = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    ouhzt__azkr = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    act__chi = cgutils.get_or_insert_function(builder.module, ouhzt__azkr,
        name='str_to_uint64')
    res = builder.call(act__chi, (ecc__wqtad.data, ecc__wqtad.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        oxhte__opwel = ', '.join('e{}'.format(fsdhb__hmcp) for fsdhb__hmcp in
            range(len(args)))
        if oxhte__opwel:
            oxhte__opwel += ', '
        sor__kcr = ', '.join("{} = ''".format(a) for a in kws.keys())
        obupk__hrkei = f'def format_stub(string, {oxhte__opwel} {sor__kcr}):\n'
        obupk__hrkei += '    pass\n'
        oskxy__bdnc = {}
        exec(obupk__hrkei, {}, oskxy__bdnc)
        jyx__knt = oskxy__bdnc['format_stub']
        luzjm__uwc = numba.core.utils.pysignature(jyx__knt)
        thwi__ppdq = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, thwi__ppdq).replace(pysig=luzjm__uwc)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    lndic__kunh = pat is not None and len(pat) > 1
    if lndic__kunh:
        hlnz__wrx = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    pgej__pkqcw = len(arr)
    dkgjs__chun = 0
    zeg__nvbg = 0
    for fsdhb__hmcp in numba.parfors.parfor.internal_prange(pgej__pkqcw):
        if bodo.libs.array_kernels.isna(arr, fsdhb__hmcp):
            continue
        if lndic__kunh:
            jjfx__fiboa = hlnz__wrx.split(arr[fsdhb__hmcp], maxsplit=n)
        elif pat == '':
            jjfx__fiboa = [''] + list(arr[fsdhb__hmcp]) + ['']
        else:
            jjfx__fiboa = arr[fsdhb__hmcp].split(pat, n)
        dkgjs__chun += len(jjfx__fiboa)
        for s in jjfx__fiboa:
            zeg__nvbg += bodo.libs.str_arr_ext.get_utf8_size(s)
    mcca__xfjm = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        pgej__pkqcw, (dkgjs__chun, zeg__nvbg), bodo.libs.str_arr_ext.
        string_array_type)
    gjvap__dlutl = bodo.libs.array_item_arr_ext.get_offsets(mcca__xfjm)
    hlclk__uslvo = bodo.libs.array_item_arr_ext.get_null_bitmap(mcca__xfjm)
    ejiev__dvae = bodo.libs.array_item_arr_ext.get_data(mcca__xfjm)
    ktep__ehubh = 0
    for brk__drlw in numba.parfors.parfor.internal_prange(pgej__pkqcw):
        gjvap__dlutl[brk__drlw] = ktep__ehubh
        if bodo.libs.array_kernels.isna(arr, brk__drlw):
            bodo.libs.int_arr_ext.set_bit_to_arr(hlclk__uslvo, brk__drlw, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(hlclk__uslvo, brk__drlw, 1)
        if lndic__kunh:
            jjfx__fiboa = hlnz__wrx.split(arr[brk__drlw], maxsplit=n)
        elif pat == '':
            jjfx__fiboa = [''] + list(arr[brk__drlw]) + ['']
        else:
            jjfx__fiboa = arr[brk__drlw].split(pat, n)
        ojjv__cfi = len(jjfx__fiboa)
        for fhbix__gpg in range(ojjv__cfi):
            s = jjfx__fiboa[fhbix__gpg]
            ejiev__dvae[ktep__ehubh] = s
            ktep__ehubh += 1
    gjvap__dlutl[pgej__pkqcw] = ktep__ehubh
    return mcca__xfjm


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                esk__ujz = '-0x'
                x = x * -1
            else:
                esk__ujz = '0x'
            x = np.uint64(x)
            if x == 0:
                tvo__qes = 1
            else:
                tvo__qes = fast_ceil_log2(x + 1)
                tvo__qes = (tvo__qes + 3) // 4
            length = len(esk__ujz) + tvo__qes
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, esk__ujz._data, len
                (esk__ujz), 1)
            int_to_hex(output, tvo__qes, len(esk__ujz), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    ffndh__bxtx = 0 if x & x - 1 == 0 else 1
    yuope__htlt = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    oaevf__int = 32
    for fsdhb__hmcp in range(len(yuope__htlt)):
        yvz__cpl = 0 if x & yuope__htlt[fsdhb__hmcp] == 0 else oaevf__int
        ffndh__bxtx = ffndh__bxtx + yvz__cpl
        x = x >> yvz__cpl
        oaevf__int = oaevf__int >> 1
    return ffndh__bxtx


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        msn__ljt = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        ouhzt__azkr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        xtkob__ufug = cgutils.get_or_insert_function(builder.module,
            ouhzt__azkr, name='int_to_hex')
        sznd__ryphs = builder.inttoptr(builder.add(builder.ptrtoint(
            msn__ljt.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(xtkob__ufug, (sznd__ryphs, out_len, int_val))
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
