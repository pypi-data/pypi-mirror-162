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
    utnw__tsv = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        mjp__iolnk, = args
        tuk__zlrrh = cgutils.create_struct_proxy(string_type)(context,
            builder, value=mjp__iolnk)
        etjik__mda = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        gbsd__twnbw = cgutils.create_struct_proxy(utnw__tsv)(context, builder)
        is_ascii = builder.icmp_unsigned('==', tuk__zlrrh.is_ascii, lir.
            Constant(tuk__zlrrh.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (pgvd__heyfm, hrc__nrxeg):
            with pgvd__heyfm:
                context.nrt.incref(builder, string_type, mjp__iolnk)
                etjik__mda.data = tuk__zlrrh.data
                etjik__mda.meminfo = tuk__zlrrh.meminfo
                gbsd__twnbw.f1 = tuk__zlrrh.length
            with hrc__nrxeg:
                bzrs__nqwu = lir.FunctionType(lir.IntType(64), [lir.IntType
                    (8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                jlaxh__nuytz = cgutils.get_or_insert_function(builder.
                    module, bzrs__nqwu, name='unicode_to_utf8')
                gsao__azko = context.get_constant_null(types.voidptr)
                eqcuw__mbkts = builder.call(jlaxh__nuytz, [gsao__azko,
                    tuk__zlrrh.data, tuk__zlrrh.length, tuk__zlrrh.kind])
                gbsd__twnbw.f1 = eqcuw__mbkts
                hlgnd__wwj = builder.add(eqcuw__mbkts, lir.Constant(lir.
                    IntType(64), 1))
                etjik__mda.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=hlgnd__wwj, align=32)
                etjik__mda.data = context.nrt.meminfo_data(builder,
                    etjik__mda.meminfo)
                builder.call(jlaxh__nuytz, [etjik__mda.data, tuk__zlrrh.
                    data, tuk__zlrrh.length, tuk__zlrrh.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    etjik__mda.data, [eqcuw__mbkts]))
        gbsd__twnbw.f0 = etjik__mda._getvalue()
        return gbsd__twnbw._getvalue()
    return utnw__tsv(string_type), codegen


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
        bzrs__nqwu = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        tll__brnqx = cgutils.get_or_insert_function(builder.module,
            bzrs__nqwu, name='memcmp')
        return builder.call(tll__brnqx, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    mylx__gtxvl = n(10)

    def impl(n):
        if n == 0:
            return 1
        mrzh__nffv = 0
        if n < 0:
            n = -n
            mrzh__nffv += 1
        while n > 0:
            n = n // mylx__gtxvl
            mrzh__nffv += 1
        return mrzh__nffv
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
        [kpwkp__gjmwf] = args
        if isinstance(kpwkp__gjmwf, StdStringType):
            return signature(types.float64, kpwkp__gjmwf)
        if kpwkp__gjmwf == string_type:
            return signature(types.float64, kpwkp__gjmwf)


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
    tuk__zlrrh = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    bzrs__nqwu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    dipa__fww = cgutils.get_or_insert_function(builder.module, bzrs__nqwu,
        name='init_string_const')
    return builder.call(dipa__fww, [tuk__zlrrh.data, tuk__zlrrh.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        rink__rjw = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(rink__rjw._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return rink__rjw
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    tuk__zlrrh = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return tuk__zlrrh.data


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
        ydug__xgb = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, ydug__xgb)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        izivw__eiw, = args
        kwmm__sdwty = types.List(string_type)
        zkdh__gpyq = numba.cpython.listobj.ListInstance.allocate(context,
            builder, kwmm__sdwty, izivw__eiw)
        zkdh__gpyq.size = izivw__eiw
        etgtz__rkmkt = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        etgtz__rkmkt.data = zkdh__gpyq.value
        return etgtz__rkmkt._getvalue()
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
            sgpq__aviyh = 0
            amu__nobmj = v
            if amu__nobmj < 0:
                sgpq__aviyh = 1
                amu__nobmj = -amu__nobmj
            if amu__nobmj < 1:
                pzcf__vvlci = 1
            else:
                pzcf__vvlci = 1 + int(np.floor(np.log10(amu__nobmj)))
            length = sgpq__aviyh + pzcf__vvlci + 1 + 6
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
    bzrs__nqwu = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    dipa__fww = cgutils.get_or_insert_function(builder.module, bzrs__nqwu,
        name='str_to_float64')
    res = builder.call(dipa__fww, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    bzrs__nqwu = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    dipa__fww = cgutils.get_or_insert_function(builder.module, bzrs__nqwu,
        name='str_to_float32')
    res = builder.call(dipa__fww, (val,))
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
    tuk__zlrrh = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    bzrs__nqwu = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    dipa__fww = cgutils.get_or_insert_function(builder.module, bzrs__nqwu,
        name='str_to_int64')
    res = builder.call(dipa__fww, (tuk__zlrrh.data, tuk__zlrrh.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    tuk__zlrrh = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    bzrs__nqwu = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    dipa__fww = cgutils.get_or_insert_function(builder.module, bzrs__nqwu,
        name='str_to_uint64')
    res = builder.call(dipa__fww, (tuk__zlrrh.data, tuk__zlrrh.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        pesaw__hcsu = ', '.join('e{}'.format(wgdbu__iqs) for wgdbu__iqs in
            range(len(args)))
        if pesaw__hcsu:
            pesaw__hcsu += ', '
        cbk__scbwv = ', '.join("{} = ''".format(a) for a in kws.keys())
        nnx__tgxgs = f'def format_stub(string, {pesaw__hcsu} {cbk__scbwv}):\n'
        nnx__tgxgs += '    pass\n'
        svhp__ucuto = {}
        exec(nnx__tgxgs, {}, svhp__ucuto)
        mkx__gmy = svhp__ucuto['format_stub']
        qvtqi__ysle = numba.core.utils.pysignature(mkx__gmy)
        fewx__kph = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, fewx__kph).replace(pysig=qvtqi__ysle)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    xjvh__jwjq = pat is not None and len(pat) > 1
    if xjvh__jwjq:
        dfuj__omxu = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    zkdh__gpyq = len(arr)
    orok__yqn = 0
    wkya__xmal = 0
    for wgdbu__iqs in numba.parfors.parfor.internal_prange(zkdh__gpyq):
        if bodo.libs.array_kernels.isna(arr, wgdbu__iqs):
            continue
        if xjvh__jwjq:
            qku__etkg = dfuj__omxu.split(arr[wgdbu__iqs], maxsplit=n)
        elif pat == '':
            qku__etkg = [''] + list(arr[wgdbu__iqs]) + ['']
        else:
            qku__etkg = arr[wgdbu__iqs].split(pat, n)
        orok__yqn += len(qku__etkg)
        for s in qku__etkg:
            wkya__xmal += bodo.libs.str_arr_ext.get_utf8_size(s)
    vuql__kzyrm = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        zkdh__gpyq, (orok__yqn, wkya__xmal), bodo.libs.str_arr_ext.
        string_array_type)
    ybdo__vbg = bodo.libs.array_item_arr_ext.get_offsets(vuql__kzyrm)
    ffil__uoo = bodo.libs.array_item_arr_ext.get_null_bitmap(vuql__kzyrm)
    koh__peybg = bodo.libs.array_item_arr_ext.get_data(vuql__kzyrm)
    zwrpa__dwu = 0
    for ejjzg__irhbp in numba.parfors.parfor.internal_prange(zkdh__gpyq):
        ybdo__vbg[ejjzg__irhbp] = zwrpa__dwu
        if bodo.libs.array_kernels.isna(arr, ejjzg__irhbp):
            bodo.libs.int_arr_ext.set_bit_to_arr(ffil__uoo, ejjzg__irhbp, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(ffil__uoo, ejjzg__irhbp, 1)
        if xjvh__jwjq:
            qku__etkg = dfuj__omxu.split(arr[ejjzg__irhbp], maxsplit=n)
        elif pat == '':
            qku__etkg = [''] + list(arr[ejjzg__irhbp]) + ['']
        else:
            qku__etkg = arr[ejjzg__irhbp].split(pat, n)
        yehh__clrim = len(qku__etkg)
        for ghry__tsf in range(yehh__clrim):
            s = qku__etkg[ghry__tsf]
            koh__peybg[zwrpa__dwu] = s
            zwrpa__dwu += 1
    ybdo__vbg[zkdh__gpyq] = zwrpa__dwu
    return vuql__kzyrm


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                gnh__pmsy = '-0x'
                x = x * -1
            else:
                gnh__pmsy = '0x'
            x = np.uint64(x)
            if x == 0:
                atayz__dlyxk = 1
            else:
                atayz__dlyxk = fast_ceil_log2(x + 1)
                atayz__dlyxk = (atayz__dlyxk + 3) // 4
            length = len(gnh__pmsy) + atayz__dlyxk
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, gnh__pmsy._data,
                len(gnh__pmsy), 1)
            int_to_hex(output, atayz__dlyxk, len(gnh__pmsy), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    cii__afecv = 0 if x & x - 1 == 0 else 1
    bnqwq__cwetj = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    gaa__jakk = 32
    for wgdbu__iqs in range(len(bnqwq__cwetj)):
        vlxwt__zcac = 0 if x & bnqwq__cwetj[wgdbu__iqs] == 0 else gaa__jakk
        cii__afecv = cii__afecv + vlxwt__zcac
        x = x >> vlxwt__zcac
        gaa__jakk = gaa__jakk >> 1
    return cii__afecv


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        vnue__jbm = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        bzrs__nqwu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        gith__dey = cgutils.get_or_insert_function(builder.module,
            bzrs__nqwu, name='int_to_hex')
        zdx__eqnk = builder.inttoptr(builder.add(builder.ptrtoint(vnue__jbm
            .data, lir.IntType(64)), header_len), lir.IntType(8).as_pointer())
        builder.call(gith__dey, (zdx__eqnk, out_len, int_val))
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
