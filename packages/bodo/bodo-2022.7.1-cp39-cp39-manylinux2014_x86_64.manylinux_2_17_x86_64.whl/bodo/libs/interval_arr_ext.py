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
        wcthu__bzic = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, wcthu__bzic)


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
        mtxib__kqoia, svif__gnhfw = args
        qmaqb__pvsrc = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        qmaqb__pvsrc.left = mtxib__kqoia
        qmaqb__pvsrc.right = svif__gnhfw
        context.nrt.incref(builder, signature.args[0], mtxib__kqoia)
        context.nrt.incref(builder, signature.args[1], svif__gnhfw)
        return qmaqb__pvsrc._getvalue()
    fsz__kdabl = IntervalArrayType(left)
    jgfph__ekm = fsz__kdabl(left, right)
    return jgfph__ekm, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    kmkb__wtyp = []
    for jard__ded in args:
        nrr__ril = equiv_set.get_shape(jard__ded)
        if nrr__ril is not None:
            kmkb__wtyp.append(nrr__ril[0])
    if len(kmkb__wtyp) > 1:
        equiv_set.insert_equiv(*kmkb__wtyp)
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
    qmaqb__pvsrc = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, qmaqb__pvsrc.left)
    ztd__nhgmu = c.pyapi.from_native_value(typ.arr_type, qmaqb__pvsrc.left,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, qmaqb__pvsrc.right)
    zzjxw__tde = c.pyapi.from_native_value(typ.arr_type, qmaqb__pvsrc.right,
        c.env_manager)
    uvtco__rwu = c.context.insert_const_string(c.builder.module, 'pandas')
    yyo__vihpn = c.pyapi.import_module_noblock(uvtco__rwu)
    nae__xjqip = c.pyapi.object_getattr_string(yyo__vihpn, 'arrays')
    pjd__jgt = c.pyapi.object_getattr_string(nae__xjqip, 'IntervalArray')
    alunk__sfjpv = c.pyapi.call_method(pjd__jgt, 'from_arrays', (ztd__nhgmu,
        zzjxw__tde))
    c.pyapi.decref(ztd__nhgmu)
    c.pyapi.decref(zzjxw__tde)
    c.pyapi.decref(yyo__vihpn)
    c.pyapi.decref(nae__xjqip)
    c.pyapi.decref(pjd__jgt)
    c.context.nrt.decref(c.builder, typ, val)
    return alunk__sfjpv


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    ztd__nhgmu = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, ztd__nhgmu).value
    c.pyapi.decref(ztd__nhgmu)
    zzjxw__tde = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, zzjxw__tde).value
    c.pyapi.decref(zzjxw__tde)
    qmaqb__pvsrc = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qmaqb__pvsrc.left = left
    qmaqb__pvsrc.right = right
    cddw__khf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qmaqb__pvsrc._getvalue(), is_error=cddw__khf)


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
