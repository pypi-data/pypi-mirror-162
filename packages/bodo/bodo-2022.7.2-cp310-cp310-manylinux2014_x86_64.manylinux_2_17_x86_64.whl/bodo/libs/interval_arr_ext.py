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
        svs__pgv = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, svs__pgv)


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
        roazk__yky, uej__gkco = args
        vfys__azapr = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        vfys__azapr.left = roazk__yky
        vfys__azapr.right = uej__gkco
        context.nrt.incref(builder, signature.args[0], roazk__yky)
        context.nrt.incref(builder, signature.args[1], uej__gkco)
        return vfys__azapr._getvalue()
    uelxk__puwg = IntervalArrayType(left)
    wee__ssu = uelxk__puwg(left, right)
    return wee__ssu, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    syzc__mspcn = []
    for lbd__dve in args:
        qyxw__qugnp = equiv_set.get_shape(lbd__dve)
        if qyxw__qugnp is not None:
            syzc__mspcn.append(qyxw__qugnp[0])
    if len(syzc__mspcn) > 1:
        equiv_set.insert_equiv(*syzc__mspcn)
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
    vfys__azapr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, vfys__azapr.left)
    cwfu__jnlf = c.pyapi.from_native_value(typ.arr_type, vfys__azapr.left,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, vfys__azapr.right)
    tzcad__cyxvs = c.pyapi.from_native_value(typ.arr_type, vfys__azapr.
        right, c.env_manager)
    hdevz__icyzo = c.context.insert_const_string(c.builder.module, 'pandas')
    cyo__jbor = c.pyapi.import_module_noblock(hdevz__icyzo)
    cmez__sgu = c.pyapi.object_getattr_string(cyo__jbor, 'arrays')
    syndl__povbp = c.pyapi.object_getattr_string(cmez__sgu, 'IntervalArray')
    pbsmf__aok = c.pyapi.call_method(syndl__povbp, 'from_arrays', (
        cwfu__jnlf, tzcad__cyxvs))
    c.pyapi.decref(cwfu__jnlf)
    c.pyapi.decref(tzcad__cyxvs)
    c.pyapi.decref(cyo__jbor)
    c.pyapi.decref(cmez__sgu)
    c.pyapi.decref(syndl__povbp)
    c.context.nrt.decref(c.builder, typ, val)
    return pbsmf__aok


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    cwfu__jnlf = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, cwfu__jnlf).value
    c.pyapi.decref(cwfu__jnlf)
    tzcad__cyxvs = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, tzcad__cyxvs).value
    c.pyapi.decref(tzcad__cyxvs)
    vfys__azapr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vfys__azapr.left = left
    vfys__azapr.right = right
    rrcsf__jiao = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vfys__azapr._getvalue(), is_error=rrcsf__jiao)


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
