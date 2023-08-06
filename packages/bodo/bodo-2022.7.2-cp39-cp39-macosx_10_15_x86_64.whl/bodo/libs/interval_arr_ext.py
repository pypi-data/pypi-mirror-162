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
        pqxc__rhy = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, pqxc__rhy)


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
        isok__rpywz, gsc__dkm = args
        ieoh__hdp = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        ieoh__hdp.left = isok__rpywz
        ieoh__hdp.right = gsc__dkm
        context.nrt.incref(builder, signature.args[0], isok__rpywz)
        context.nrt.incref(builder, signature.args[1], gsc__dkm)
        return ieoh__hdp._getvalue()
    kvnhe__xguo = IntervalArrayType(left)
    lmnhu__klsgh = kvnhe__xguo(left, right)
    return lmnhu__klsgh, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ylbj__gyinz = []
    for qgru__hpesg in args:
        kot__gfim = equiv_set.get_shape(qgru__hpesg)
        if kot__gfim is not None:
            ylbj__gyinz.append(kot__gfim[0])
    if len(ylbj__gyinz) > 1:
        equiv_set.insert_equiv(*ylbj__gyinz)
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
    ieoh__hdp = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, ieoh__hdp.left)
    vafk__bimz = c.pyapi.from_native_value(typ.arr_type, ieoh__hdp.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, ieoh__hdp.right)
    jlo__bqatc = c.pyapi.from_native_value(typ.arr_type, ieoh__hdp.right, c
        .env_manager)
    utq__nwj = c.context.insert_const_string(c.builder.module, 'pandas')
    cqp__fum = c.pyapi.import_module_noblock(utq__nwj)
    qyzc__xiu = c.pyapi.object_getattr_string(cqp__fum, 'arrays')
    evek__grkwx = c.pyapi.object_getattr_string(qyzc__xiu, 'IntervalArray')
    njtev__hajpy = c.pyapi.call_method(evek__grkwx, 'from_arrays', (
        vafk__bimz, jlo__bqatc))
    c.pyapi.decref(vafk__bimz)
    c.pyapi.decref(jlo__bqatc)
    c.pyapi.decref(cqp__fum)
    c.pyapi.decref(qyzc__xiu)
    c.pyapi.decref(evek__grkwx)
    c.context.nrt.decref(c.builder, typ, val)
    return njtev__hajpy


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    vafk__bimz = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, vafk__bimz).value
    c.pyapi.decref(vafk__bimz)
    jlo__bqatc = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, jlo__bqatc).value
    c.pyapi.decref(jlo__bqatc)
    ieoh__hdp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ieoh__hdp.left = left
    ieoh__hdp.right = right
    uii__nscd = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ieoh__hdp._getvalue(), is_error=uii__nscd)


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
