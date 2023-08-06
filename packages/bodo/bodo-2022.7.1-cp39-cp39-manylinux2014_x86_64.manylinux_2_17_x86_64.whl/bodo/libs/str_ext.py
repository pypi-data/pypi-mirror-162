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
    uaayg__lxj = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        qay__thpm, = args
        jqtyk__ofdpk = cgutils.create_struct_proxy(string_type)(context,
            builder, value=qay__thpm)
        sexz__jqdw = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        omi__jlcr = cgutils.create_struct_proxy(uaayg__lxj)(context, builder)
        is_ascii = builder.icmp_unsigned('==', jqtyk__ofdpk.is_ascii, lir.
            Constant(jqtyk__ofdpk.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (omjsp__akk, nkr__dytcd):
            with omjsp__akk:
                context.nrt.incref(builder, string_type, qay__thpm)
                sexz__jqdw.data = jqtyk__ofdpk.data
                sexz__jqdw.meminfo = jqtyk__ofdpk.meminfo
                omi__jlcr.f1 = jqtyk__ofdpk.length
            with nkr__dytcd:
                ocimh__uzigw = lir.FunctionType(lir.IntType(64), [lir.
                    IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                    lir.IntType(64), lir.IntType(32)])
                xffqs__auoxo = cgutils.get_or_insert_function(builder.
                    module, ocimh__uzigw, name='unicode_to_utf8')
                olv__lyqbe = context.get_constant_null(types.voidptr)
                aomjz__ahh = builder.call(xffqs__auoxo, [olv__lyqbe,
                    jqtyk__ofdpk.data, jqtyk__ofdpk.length, jqtyk__ofdpk.kind])
                omi__jlcr.f1 = aomjz__ahh
                fnqhc__bta = builder.add(aomjz__ahh, lir.Constant(lir.
                    IntType(64), 1))
                sexz__jqdw.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=fnqhc__bta, align=32)
                sexz__jqdw.data = context.nrt.meminfo_data(builder,
                    sexz__jqdw.meminfo)
                builder.call(xffqs__auoxo, [sexz__jqdw.data, jqtyk__ofdpk.
                    data, jqtyk__ofdpk.length, jqtyk__ofdpk.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    sexz__jqdw.data, [aomjz__ahh]))
        omi__jlcr.f0 = sexz__jqdw._getvalue()
        return omi__jlcr._getvalue()
    return uaayg__lxj(string_type), codegen


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
        ocimh__uzigw = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        gpywc__wnpp = cgutils.get_or_insert_function(builder.module,
            ocimh__uzigw, name='memcmp')
        return builder.call(gpywc__wnpp, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    ckr__xfaxq = n(10)

    def impl(n):
        if n == 0:
            return 1
        dsg__aov = 0
        if n < 0:
            n = -n
            dsg__aov += 1
        while n > 0:
            n = n // ckr__xfaxq
            dsg__aov += 1
        return dsg__aov
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
        [jrn__zcjzy] = args
        if isinstance(jrn__zcjzy, StdStringType):
            return signature(types.float64, jrn__zcjzy)
        if jrn__zcjzy == string_type:
            return signature(types.float64, jrn__zcjzy)


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
    jqtyk__ofdpk = cgutils.create_struct_proxy(string_type)(context,
        builder, value=unicode_val)
    ocimh__uzigw = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    fbg__soci = cgutils.get_or_insert_function(builder.module, ocimh__uzigw,
        name='init_string_const')
    return builder.call(fbg__soci, [jqtyk__ofdpk.data, jqtyk__ofdpk.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        igcp__hprpa = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(igcp__hprpa._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return igcp__hprpa
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    jqtyk__ofdpk = cgutils.create_struct_proxy(string_type)(context,
        builder, value=unicode_val)
    return jqtyk__ofdpk.data


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
        gnf__kwem = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, gnf__kwem)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        ptg__xsdry, = args
        samwn__usia = types.List(string_type)
        zzfl__mek = numba.cpython.listobj.ListInstance.allocate(context,
            builder, samwn__usia, ptg__xsdry)
        zzfl__mek.size = ptg__xsdry
        ohhi__bgif = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        ohhi__bgif.data = zzfl__mek.value
        return ohhi__bgif._getvalue()
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
            nrseh__ubewg = 0
            yxbn__dilhn = v
            if yxbn__dilhn < 0:
                nrseh__ubewg = 1
                yxbn__dilhn = -yxbn__dilhn
            if yxbn__dilhn < 1:
                lcm__jwtav = 1
            else:
                lcm__jwtav = 1 + int(np.floor(np.log10(yxbn__dilhn)))
            length = nrseh__ubewg + lcm__jwtav + 1 + 6
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
    ocimh__uzigw = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    fbg__soci = cgutils.get_or_insert_function(builder.module, ocimh__uzigw,
        name='str_to_float64')
    res = builder.call(fbg__soci, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    ocimh__uzigw = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    fbg__soci = cgutils.get_or_insert_function(builder.module, ocimh__uzigw,
        name='str_to_float32')
    res = builder.call(fbg__soci, (val,))
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
    jqtyk__ofdpk = cgutils.create_struct_proxy(string_type)(context,
        builder, value=val)
    ocimh__uzigw = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    fbg__soci = cgutils.get_or_insert_function(builder.module, ocimh__uzigw,
        name='str_to_int64')
    res = builder.call(fbg__soci, (jqtyk__ofdpk.data, jqtyk__ofdpk.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    jqtyk__ofdpk = cgutils.create_struct_proxy(string_type)(context,
        builder, value=val)
    ocimh__uzigw = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    fbg__soci = cgutils.get_or_insert_function(builder.module, ocimh__uzigw,
        name='str_to_uint64')
    res = builder.call(fbg__soci, (jqtyk__ofdpk.data, jqtyk__ofdpk.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        jpjwf__yvhin = ', '.join('e{}'.format(riovv__ifhe) for riovv__ifhe in
            range(len(args)))
        if jpjwf__yvhin:
            jpjwf__yvhin += ', '
        ugc__zjrm = ', '.join("{} = ''".format(a) for a in kws.keys())
        lcjv__bypfs = f'def format_stub(string, {jpjwf__yvhin} {ugc__zjrm}):\n'
        lcjv__bypfs += '    pass\n'
        djs__eqjy = {}
        exec(lcjv__bypfs, {}, djs__eqjy)
        mzz__igr = djs__eqjy['format_stub']
        fvpi__ykrz = numba.core.utils.pysignature(mzz__igr)
        lsxk__crsb = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, lsxk__crsb).replace(pysig=fvpi__ykrz)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    cruz__qtyf = pat is not None and len(pat) > 1
    if cruz__qtyf:
        mhkp__gvr = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    zzfl__mek = len(arr)
    tdozk__moypd = 0
    qgh__izt = 0
    for riovv__ifhe in numba.parfors.parfor.internal_prange(zzfl__mek):
        if bodo.libs.array_kernels.isna(arr, riovv__ifhe):
            continue
        if cruz__qtyf:
            rkjpo__rdtuo = mhkp__gvr.split(arr[riovv__ifhe], maxsplit=n)
        elif pat == '':
            rkjpo__rdtuo = [''] + list(arr[riovv__ifhe]) + ['']
        else:
            rkjpo__rdtuo = arr[riovv__ifhe].split(pat, n)
        tdozk__moypd += len(rkjpo__rdtuo)
        for s in rkjpo__rdtuo:
            qgh__izt += bodo.libs.str_arr_ext.get_utf8_size(s)
    vqtoy__fxksd = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        zzfl__mek, (tdozk__moypd, qgh__izt), bodo.libs.str_arr_ext.
        string_array_type)
    wuy__pkn = bodo.libs.array_item_arr_ext.get_offsets(vqtoy__fxksd)
    ilsu__bdwjy = bodo.libs.array_item_arr_ext.get_null_bitmap(vqtoy__fxksd)
    gyk__sal = bodo.libs.array_item_arr_ext.get_data(vqtoy__fxksd)
    fktuy__uswux = 0
    for qcfzi__exutg in numba.parfors.parfor.internal_prange(zzfl__mek):
        wuy__pkn[qcfzi__exutg] = fktuy__uswux
        if bodo.libs.array_kernels.isna(arr, qcfzi__exutg):
            bodo.libs.int_arr_ext.set_bit_to_arr(ilsu__bdwjy, qcfzi__exutg, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(ilsu__bdwjy, qcfzi__exutg, 1)
        if cruz__qtyf:
            rkjpo__rdtuo = mhkp__gvr.split(arr[qcfzi__exutg], maxsplit=n)
        elif pat == '':
            rkjpo__rdtuo = [''] + list(arr[qcfzi__exutg]) + ['']
        else:
            rkjpo__rdtuo = arr[qcfzi__exutg].split(pat, n)
        iwc__xdw = len(rkjpo__rdtuo)
        for cmm__vpws in range(iwc__xdw):
            s = rkjpo__rdtuo[cmm__vpws]
            gyk__sal[fktuy__uswux] = s
            fktuy__uswux += 1
    wuy__pkn[zzfl__mek] = fktuy__uswux
    return vqtoy__fxksd


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                zpt__iwo = '-0x'
                x = x * -1
            else:
                zpt__iwo = '0x'
            x = np.uint64(x)
            if x == 0:
                utn__thiye = 1
            else:
                utn__thiye = fast_ceil_log2(x + 1)
                utn__thiye = (utn__thiye + 3) // 4
            length = len(zpt__iwo) + utn__thiye
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, zpt__iwo._data, len
                (zpt__iwo), 1)
            int_to_hex(output, utn__thiye, len(zpt__iwo), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    aosjq__qpqj = 0 if x & x - 1 == 0 else 1
    tzzxy__hjppb = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    ytjxz__pjdip = 32
    for riovv__ifhe in range(len(tzzxy__hjppb)):
        romx__ctat = 0 if x & tzzxy__hjppb[riovv__ifhe] == 0 else ytjxz__pjdip
        aosjq__qpqj = aosjq__qpqj + romx__ctat
        x = x >> romx__ctat
        ytjxz__pjdip = ytjxz__pjdip >> 1
    return aosjq__qpqj


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        nsgu__llyxx = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        ocimh__uzigw = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        claw__fto = cgutils.get_or_insert_function(builder.module,
            ocimh__uzigw, name='int_to_hex')
        mrjbn__vxaev = builder.inttoptr(builder.add(builder.ptrtoint(
            nsgu__llyxx.data, lir.IntType(64)), header_len), lir.IntType(8)
            .as_pointer())
        builder.call(claw__fto, (mrjbn__vxaev, out_len, int_val))
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
