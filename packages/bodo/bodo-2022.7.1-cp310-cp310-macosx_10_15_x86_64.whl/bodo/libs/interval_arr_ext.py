"""
Array of intervals corresponding to IntervalArray of Pandas.
Used for IntervalIndex, which is necessary for Series.value_counts() with 'bins'
argument.
"""
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo


class IntervalType(types.Type):

    def __init__(self):
        super(IntervalType, self).__init__('IntervalType()')


class IntervalArrayType(types.ArrayCompatible):

    def __init__(self, arr_type):
        self.arr_type = arr_type
        self.dtype = IntervalType()
        super(IntervalArrayType, self).__init__(name=
            f'IntervalArrayType({arr_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntervalArrayType(self.arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(IntervalArrayType)
class IntervalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pyp__yoaq = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, pyp__yoaq)


make_attribute_wrapper(IntervalArrayType, 'left', '_left')
make_attribute_wrapper(IntervalArrayType, 'right', '_right')


@typeof_impl.register(pd.arrays.IntervalArray)
def typeof_interval_array(val, c):
    arr_type = bodo.typeof(val._left)
    return IntervalArrayType(arr_type)


@intrinsic
def init_interval_array(typingctx, left, right=None):
    assert left == right, 'Interval left/right array types should be the same'

    def codegen(context, builder, signature, args):
        zjq__rmm, diyxr__ucnk = args
        hdu__qdt = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        hdu__qdt.left = zjq__rmm
        hdu__qdt.right = diyxr__ucnk
        context.nrt.incref(builder, signature.args[0], zjq__rmm)
        context.nrt.incref(builder, signature.args[1], diyxr__ucnk)
        return hdu__qdt._getvalue()
    kgt__mhekl = IntervalArrayType(left)
    bjo__fvg = kgt__mhekl(left, right)
    return bjo__fvg, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    jfhoi__imkr = []
    for pjq__xjrq in args:
        thn__sey = equiv_set.get_shape(pjq__xjrq)
        if thn__sey is not None:
            jfhoi__imkr.append(thn__sey[0])
    if len(jfhoi__imkr) > 1:
        equiv_set.insert_equiv(*jfhoi__imkr)
    left = args[0]
    if equiv_set.has_shape(left):
        return ArrayAnalysis.AnalyzeResult(shape=left, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_libs_interval_arr_ext_init_interval_array
    ) = init_interval_array_equiv


def alias_ext_init_interval_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_interval_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_interval_array


@box(IntervalArrayType)
def box_interval_arr(typ, val, c):
    hdu__qdt = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, hdu__qdt.left)
    xkydv__qpkvy = c.pyapi.from_native_value(typ.arr_type, hdu__qdt.left, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, hdu__qdt.right)
    sup__dhd = c.pyapi.from_native_value(typ.arr_type, hdu__qdt.right, c.
        env_manager)
    zmh__xgk = c.context.insert_const_string(c.builder.module, 'pandas')
    ctktd__zzh = c.pyapi.import_module_noblock(zmh__xgk)
    ndvrx__keg = c.pyapi.object_getattr_string(ctktd__zzh, 'arrays')
    nonxu__ogf = c.pyapi.object_getattr_string(ndvrx__keg, 'IntervalArray')
    bbn__wcxat = c.pyapi.call_method(nonxu__ogf, 'from_arrays', (
        xkydv__qpkvy, sup__dhd))
    c.pyapi.decref(xkydv__qpkvy)
    c.pyapi.decref(sup__dhd)
    c.pyapi.decref(ctktd__zzh)
    c.pyapi.decref(ndvrx__keg)
    c.pyapi.decref(nonxu__ogf)
    c.context.nrt.decref(c.builder, typ, val)
    return bbn__wcxat


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    xkydv__qpkvy = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, xkydv__qpkvy).value
    c.pyapi.decref(xkydv__qpkvy)
    sup__dhd = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, sup__dhd).value
    c.pyapi.decref(sup__dhd)
    hdu__qdt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hdu__qdt.left = left
    hdu__qdt.right = right
    nggq__xjis = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(hdu__qdt._getvalue(), is_error=nggq__xjis)


@overload(len, no_unliteral=True)
def overload_interval_arr_len(A):
    if isinstance(A, IntervalArrayType):
        return lambda A: len(A._left)


@overload_attribute(IntervalArrayType, 'shape')
def overload_interval_arr_shape(A):
    return lambda A: (len(A._left),)


@overload_attribute(IntervalArrayType, 'ndim')
def overload_interval_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntervalArrayType, 'nbytes')
def overload_interval_arr_nbytes(A):
    return lambda A: A._left.nbytes + A._right.nbytes


@overload_method(IntervalArrayType, 'copy', no_unliteral=True)
def overload_interval_arr_copy(A):
    return lambda A: bodo.libs.interval_arr_ext.init_interval_array(A._left
        .copy(), A._right.copy())
