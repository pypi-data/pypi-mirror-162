"""Table data type for storing dataframe column arrays. Supports storing many columns
(e.g. >10k) efficiently.
"""
import operator
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.ir_utils import guard
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from numba.np.arrayobj import _getitem_array_single_int
from numba.parfors.array_analysis import ArrayAnalysis
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_none, is_overload_true, raise_bodo_error, to_str_arr_if_dict_array, unwrap_typeref
from bodo.utils.utils import is_whole_slice


class Table:

    def __init__(self, arrs, usecols=None, num_arrs=-1):
        if usecols is not None:
            assert num_arrs != -1, 'num_arrs must be provided if usecols is not None'
            xhyek__jfxaf = 0
            ijhro__tkois = []
            for i in range(usecols[-1] + 1):
                if i == usecols[xhyek__jfxaf]:
                    ijhro__tkois.append(arrs[xhyek__jfxaf])
                    xhyek__jfxaf += 1
                else:
                    ijhro__tkois.append(None)
            for mjsjz__zufw in range(usecols[-1] + 1, num_arrs):
                ijhro__tkois.append(None)
            self.arrays = ijhro__tkois
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((ljw__uqzi == fkaj__xxyrs).all() for ljw__uqzi,
            fkaj__xxyrs in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        jwy__zvru = len(self.arrays)
        ryq__ibd = dict(zip(range(jwy__zvru), self.arrays))
        df = pd.DataFrame(ryq__ibd, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        vdy__uedi = []
        dlhbz__bdot = []
        gsn__jxsip = {}
        twwn__vtnoy = {}
        vwyy__iud = defaultdict(int)
        hcs__nslfp = defaultdict(list)
        if not has_runtime_cols:
            for i, lqa__okayt in enumerate(arr_types):
                if lqa__okayt not in gsn__jxsip:
                    uhcf__mso = len(gsn__jxsip)
                    gsn__jxsip[lqa__okayt] = uhcf__mso
                    twwn__vtnoy[uhcf__mso] = lqa__okayt
                unj__mgap = gsn__jxsip[lqa__okayt]
                vdy__uedi.append(unj__mgap)
                dlhbz__bdot.append(vwyy__iud[unj__mgap])
                vwyy__iud[unj__mgap] += 1
                hcs__nslfp[unj__mgap].append(i)
        self.block_nums = vdy__uedi
        self.block_offsets = dlhbz__bdot
        self.type_to_blk = gsn__jxsip
        self.blk_to_type = twwn__vtnoy
        self.block_to_arr_ind = hcs__nslfp
        super(TableType, self).__init__(name=
            f'TableType({arr_types}, {has_runtime_cols})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return self.arr_types, self.has_runtime_cols

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(Table)
def typeof_table(val, c):
    return TableType(tuple(numba.typeof(arr) for arr in val.arrays))


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            cwhc__lzma = [(f'block_{i}', types.List(lqa__okayt)) for i,
                lqa__okayt in enumerate(fe_type.arr_types)]
        else:
            cwhc__lzma = [(f'block_{unj__mgap}', types.List(lqa__okayt)) for
                lqa__okayt, unj__mgap in fe_type.type_to_blk.items()]
        cwhc__lzma.append(('parent', types.pyobject))
        cwhc__lzma.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, cwhc__lzma)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    bvz__vcr = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    tzff__ptpwb = c.pyapi.make_none()
    uuxe__qsgm = c.context.get_constant(types.int64, 0)
    zob__orjyq = cgutils.alloca_once_value(c.builder, uuxe__qsgm)
    for lqa__okayt, unj__mgap in typ.type_to_blk.items():
        dgr__bvk = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[unj__mgap]))
        mjsjz__zufw, ezdo__soe = ListInstance.allocate_ex(c.context, c.
            builder, types.List(lqa__okayt), dgr__bvk)
        ezdo__soe.size = dgr__bvk
        jigwa__hfyu = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[unj__mgap],
            dtype=np.int64))
        hznvz__fgjd = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, jigwa__hfyu)
        with cgutils.for_range(c.builder, dgr__bvk) as sokm__utmfn:
            i = sokm__utmfn.index
            sbdy__cnig = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), hznvz__fgjd, i)
            rhmpo__bri = c.pyapi.long_from_longlong(sbdy__cnig)
            vdb__dgif = c.pyapi.object_getitem(bvz__vcr, rhmpo__bri)
            ubt__lmbl = c.builder.icmp_unsigned('==', vdb__dgif, tzff__ptpwb)
            with c.builder.if_else(ubt__lmbl) as (wzzun__qxpqt, cjh__vpfl):
                with wzzun__qxpqt:
                    blgwx__mwtj = c.context.get_constant_null(lqa__okayt)
                    ezdo__soe.inititem(i, blgwx__mwtj, incref=False)
                with cjh__vpfl:
                    gjjg__xzxya = c.pyapi.call_method(vdb__dgif, '__len__', ())
                    jpgjv__qox = c.pyapi.long_as_longlong(gjjg__xzxya)
                    c.builder.store(jpgjv__qox, zob__orjyq)
                    c.pyapi.decref(gjjg__xzxya)
                    arr = c.pyapi.to_native_value(lqa__okayt, vdb__dgif).value
                    ezdo__soe.inititem(i, arr, incref=False)
            c.pyapi.decref(vdb__dgif)
            c.pyapi.decref(rhmpo__bri)
        setattr(table, f'block_{unj__mgap}', ezdo__soe.value)
    table.len = c.builder.load(zob__orjyq)
    c.pyapi.decref(bvz__vcr)
    c.pyapi.decref(tzff__ptpwb)
    yqmo__xke = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=yqmo__xke)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        oakc__qpxqs = c.context.get_constant(types.int64, 0)
        for i, lqa__okayt in enumerate(typ.arr_types):
            ijhro__tkois = getattr(table, f'block_{i}')
            ixo__srjyk = ListInstance(c.context, c.builder, types.List(
                lqa__okayt), ijhro__tkois)
            oakc__qpxqs = c.builder.add(oakc__qpxqs, ixo__srjyk.size)
        pmx__lvzar = c.pyapi.list_new(oakc__qpxqs)
        ltau__nmqot = c.context.get_constant(types.int64, 0)
        for i, lqa__okayt in enumerate(typ.arr_types):
            ijhro__tkois = getattr(table, f'block_{i}')
            ixo__srjyk = ListInstance(c.context, c.builder, types.List(
                lqa__okayt), ijhro__tkois)
            with cgutils.for_range(c.builder, ixo__srjyk.size) as sokm__utmfn:
                i = sokm__utmfn.index
                arr = ixo__srjyk.getitem(i)
                c.context.nrt.incref(c.builder, lqa__okayt, arr)
                idx = c.builder.add(ltau__nmqot, i)
                c.pyapi.list_setitem(pmx__lvzar, idx, c.pyapi.
                    from_native_value(lqa__okayt, arr, c.env_manager))
            ltau__nmqot = c.builder.add(ltau__nmqot, ixo__srjyk.size)
        czajs__svphm = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        mxsl__czys = c.pyapi.call_function_objargs(czajs__svphm, (pmx__lvzar,))
        c.pyapi.decref(czajs__svphm)
        c.pyapi.decref(pmx__lvzar)
        c.context.nrt.decref(c.builder, typ, val)
        return mxsl__czys
    pmx__lvzar = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    ftgs__pcfa = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for lqa__okayt, unj__mgap in typ.type_to_blk.items():
        ijhro__tkois = getattr(table, f'block_{unj__mgap}')
        ixo__srjyk = ListInstance(c.context, c.builder, types.List(
            lqa__okayt), ijhro__tkois)
        jigwa__hfyu = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[unj__mgap],
            dtype=np.int64))
        hznvz__fgjd = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, jigwa__hfyu)
        with cgutils.for_range(c.builder, ixo__srjyk.size) as sokm__utmfn:
            i = sokm__utmfn.index
            sbdy__cnig = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), hznvz__fgjd, i)
            arr = ixo__srjyk.getitem(i)
            xtndu__zkznp = cgutils.alloca_once_value(c.builder, arr)
            qapeb__xvp = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(lqa__okayt))
            is_null = is_ll_eq(c.builder, xtndu__zkznp, qapeb__xvp)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (wzzun__qxpqt, cjh__vpfl):
                with wzzun__qxpqt:
                    tzff__ptpwb = c.pyapi.make_none()
                    c.pyapi.list_setitem(pmx__lvzar, sbdy__cnig, tzff__ptpwb)
                with cjh__vpfl:
                    vdb__dgif = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, ftgs__pcfa)
                        ) as (xme__westo, ued__xym):
                        with xme__westo:
                            bcg__hhn = get_df_obj_column_codegen(c.context,
                                c.builder, c.pyapi, table.parent,
                                sbdy__cnig, lqa__okayt)
                            c.builder.store(bcg__hhn, vdb__dgif)
                        with ued__xym:
                            c.context.nrt.incref(c.builder, lqa__okayt, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                lqa__okayt, arr, c.env_manager), vdb__dgif)
                    c.pyapi.list_setitem(pmx__lvzar, sbdy__cnig, c.builder.
                        load(vdb__dgif))
    czajs__svphm = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    mxsl__czys = c.pyapi.call_function_objargs(czajs__svphm, (pmx__lvzar,))
    c.pyapi.decref(czajs__svphm)
    c.pyapi.decref(pmx__lvzar)
    c.context.nrt.decref(c.builder, typ, val)
    return mxsl__czys


@lower_builtin(len, TableType)
def table_len_lower(context, builder, sig, args):
    impl = table_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def table_len_overload(T):
    if not isinstance(T, TableType):
        return

    def impl(T):
        return T._len
    return impl


@lower_getattr(TableType, 'shape')
def lower_table_shape(context, builder, typ, val):
    impl = table_shape_overload(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def table_shape_overload(T):
    if T.has_runtime_cols:

        def impl(T):
            return T._len, compute_num_runtime_columns(T)
        return impl
    ncols = len(T.arr_types)
    return lambda T: (T._len, types.int64(ncols))


@intrinsic
def compute_num_runtime_columns(typingctx, table_type):
    assert isinstance(table_type, TableType)

    def codegen(context, builder, sig, args):
        table_arg, = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        ikjqz__ucb = context.get_constant(types.int64, 0)
        for i, lqa__okayt in enumerate(table_type.arr_types):
            ijhro__tkois = getattr(table, f'block_{i}')
            ixo__srjyk = ListInstance(context, builder, types.List(
                lqa__okayt), ijhro__tkois)
            ikjqz__ucb = builder.add(ikjqz__ucb, ixo__srjyk.size)
        return ikjqz__ucb
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    unj__mgap = table_type.block_nums[col_ind]
    vcdp__bivw = table_type.block_offsets[col_ind]
    ijhro__tkois = getattr(table, f'block_{unj__mgap}')
    dfc__zpe = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    nmwb__pqqt = context.get_constant(types.int64, col_ind)
    khib__cxk = context.get_constant(types.int64, vcdp__bivw)
    deb__zmzf = table_arg, ijhro__tkois, khib__cxk, nmwb__pqqt
    ensure_column_unboxed_codegen(context, builder, dfc__zpe, deb__zmzf)
    ixo__srjyk = ListInstance(context, builder, types.List(arr_type),
        ijhro__tkois)
    arr = ixo__srjyk.getitem(vcdp__bivw)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, mjsjz__zufw = args
        arr = get_table_data_codegen(context, builder, table_arg, col_ind,
            table_type)
        return impl_ret_borrowed(context, builder, arr_type, arr)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType
        ), 'Can only delete columns from a table'
    assert isinstance(ind_typ, types.TypeRef) and isinstance(ind_typ.
        instance_type, MetaType), 'ind_typ must be a typeref for a meta type'
    avauf__vyef = list(ind_typ.instance_type.meta)
    ife__oom = defaultdict(list)
    for ind in avauf__vyef:
        ife__oom[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, mjsjz__zufw = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for unj__mgap, acim__dqeta in ife__oom.items():
            arr_type = table_type.blk_to_type[unj__mgap]
            ijhro__tkois = getattr(table, f'block_{unj__mgap}')
            ixo__srjyk = ListInstance(context, builder, types.List(arr_type
                ), ijhro__tkois)
            blgwx__mwtj = context.get_constant_null(arr_type)
            if len(acim__dqeta) == 1:
                vcdp__bivw = acim__dqeta[0]
                arr = ixo__srjyk.getitem(vcdp__bivw)
                context.nrt.decref(builder, arr_type, arr)
                ixo__srjyk.inititem(vcdp__bivw, blgwx__mwtj, incref=False)
            else:
                dgr__bvk = context.get_constant(types.int64, len(acim__dqeta))
                qexk__lssj = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(acim__dqeta, dtype
                    =np.int64))
                xbsi__cyg = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, qexk__lssj)
                with cgutils.for_range(builder, dgr__bvk) as sokm__utmfn:
                    i = sokm__utmfn.index
                    vcdp__bivw = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        xbsi__cyg, i)
                    arr = ixo__srjyk.getitem(vcdp__bivw)
                    context.nrt.decref(builder, arr_type, arr)
                    ixo__srjyk.inititem(vcdp__bivw, blgwx__mwtj, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    uuxe__qsgm = context.get_constant(types.int64, 0)
    ufa__osxt = context.get_constant(types.int64, 1)
    hle__qikh = arr_type not in in_table_type.type_to_blk
    for lqa__okayt, unj__mgap in out_table_type.type_to_blk.items():
        if lqa__okayt in in_table_type.type_to_blk:
            mkbj__ciuk = in_table_type.type_to_blk[lqa__okayt]
            ezdo__soe = ListInstance(context, builder, types.List(
                lqa__okayt), getattr(in_table, f'block_{mkbj__ciuk}'))
            context.nrt.incref(builder, types.List(lqa__okayt), ezdo__soe.value
                )
            setattr(out_table, f'block_{unj__mgap}', ezdo__soe.value)
    if hle__qikh:
        mjsjz__zufw, ezdo__soe = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), ufa__osxt)
        ezdo__soe.size = ufa__osxt
        ezdo__soe.inititem(uuxe__qsgm, arr_arg, incref=True)
        unj__mgap = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{unj__mgap}', ezdo__soe.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        unj__mgap = out_table_type.type_to_blk[arr_type]
        ezdo__soe = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{unj__mgap}'))
        if is_new_col:
            n = ezdo__soe.size
            ejsxi__csg = builder.add(n, ufa__osxt)
            ezdo__soe.resize(ejsxi__csg)
            ezdo__soe.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            jit__jsg = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            ezdo__soe.setitem(jit__jsg, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            jit__jsg = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = ezdo__soe.size
            ejsxi__csg = builder.add(n, ufa__osxt)
            ezdo__soe.resize(ejsxi__csg)
            context.nrt.incref(builder, arr_type, ezdo__soe.getitem(jit__jsg))
            ezdo__soe.move(builder.add(jit__jsg, ufa__osxt), jit__jsg,
                builder.sub(n, jit__jsg))
            ezdo__soe.setitem(jit__jsg, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    ltyx__hph = in_table_type.arr_types[col_ind]
    if ltyx__hph in out_table_type.type_to_blk:
        unj__mgap = out_table_type.type_to_blk[ltyx__hph]
        wuqrt__ipjdk = getattr(out_table, f'block_{unj__mgap}')
        obx__qfgem = types.List(ltyx__hph)
        jit__jsg = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        erxdg__ewo = obx__qfgem.dtype(obx__qfgem, types.intp)
        kvja__azz = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), erxdg__ewo, (wuqrt__ipjdk, jit__jsg))
        context.nrt.decref(builder, ltyx__hph, kvja__azz)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    hyaq__zayr = list(table.arr_types)
    if ind == len(hyaq__zayr):
        jtxzm__xtz = None
        hyaq__zayr.append(arr_type)
    else:
        jtxzm__xtz = table.arr_types[ind]
        hyaq__zayr[ind] = arr_type
    rtbg__mjfr = TableType(tuple(hyaq__zayr))
    uiwhf__cfhbi = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': rtbg__mjfr}
    rwzln__ngv = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    rwzln__ngv += f'  T2 = init_table(out_table_typ, False)\n'
    rwzln__ngv += f'  T2 = set_table_len(T2, len(table))\n'
    rwzln__ngv += f'  T2 = set_table_parent(T2, table)\n'
    for typ, unj__mgap in rtbg__mjfr.type_to_blk.items():
        if typ in table.type_to_blk:
            ypq__eyz = table.type_to_blk[typ]
            rwzln__ngv += (
                f'  arr_list_{unj__mgap} = get_table_block(table, {ypq__eyz})\n'
                )
            rwzln__ngv += f"""  out_arr_list_{unj__mgap} = alloc_list_like(arr_list_{unj__mgap}, {len(rtbg__mjfr.block_to_arr_ind[unj__mgap])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[ypq__eyz]
                ) & used_cols:
                rwzln__ngv += f'  for i in range(len(arr_list_{unj__mgap})):\n'
                if typ not in (jtxzm__xtz, arr_type):
                    rwzln__ngv += (
                        f'    out_arr_list_{unj__mgap}[i] = arr_list_{unj__mgap}[i]\n'
                        )
                else:
                    jzzs__zghot = table.block_to_arr_ind[ypq__eyz]
                    olt__rklm = np.empty(len(jzzs__zghot), np.int64)
                    cme__mts = False
                    for chz__wokkk, sbdy__cnig in enumerate(jzzs__zghot):
                        if sbdy__cnig != ind:
                            kaai__cpsx = rtbg__mjfr.block_offsets[sbdy__cnig]
                        else:
                            kaai__cpsx = -1
                            cme__mts = True
                        olt__rklm[chz__wokkk] = kaai__cpsx
                    uiwhf__cfhbi[f'out_idxs_{unj__mgap}'] = np.array(olt__rklm,
                        np.int64)
                    rwzln__ngv += f'    out_idx = out_idxs_{unj__mgap}[i]\n'
                    if cme__mts:
                        rwzln__ngv += f'    if out_idx == -1:\n'
                        rwzln__ngv += f'      continue\n'
                    rwzln__ngv += f"""    out_arr_list_{unj__mgap}[out_idx] = arr_list_{unj__mgap}[i]
"""
            if typ == arr_type and not is_null:
                rwzln__ngv += (
                    f'  out_arr_list_{unj__mgap}[{rtbg__mjfr.block_offsets[ind]}] = arr\n'
                    )
        else:
            uiwhf__cfhbi[f'arr_list_typ_{unj__mgap}'] = types.List(arr_type)
            rwzln__ngv += f"""  out_arr_list_{unj__mgap} = alloc_list_like(arr_list_typ_{unj__mgap}, 1, False)
"""
            if not is_null:
                rwzln__ngv += f'  out_arr_list_{unj__mgap}[0] = arr\n'
        rwzln__ngv += (
            f'  T2 = set_table_block(T2, out_arr_list_{unj__mgap}, {unj__mgap})\n'
            )
    rwzln__ngv += f'  return T2\n'
    uzfn__jnh = {}
    exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
    return uzfn__jnh['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        hxjy__vas = None
    else:
        hxjy__vas = set(used_cols.instance_type.meta)
    aodz__eczr = get_overload_const_int(ind)
    return generate_set_table_data_code(table, aodz__eczr, arr, hxjy__vas)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    aodz__eczr = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        hxjy__vas = None
    else:
        hxjy__vas = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, aodz__eczr, arr_type,
        hxjy__vas, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    wws__stxid = args[0]
    if equiv_set.has_shape(wws__stxid):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wws__stxid)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    dnik__petmn = []
    for lqa__okayt, unj__mgap in table_type.type_to_blk.items():
        gsbs__rmd = len(table_type.block_to_arr_ind[unj__mgap])
        fou__aec = []
        for i in range(gsbs__rmd):
            sbdy__cnig = table_type.block_to_arr_ind[unj__mgap][i]
            fou__aec.append(pyval.arrays[sbdy__cnig])
        dnik__petmn.append(context.get_constant_generic(builder, types.List
            (lqa__okayt), fou__aec))
    qbd__jlhad = context.get_constant_null(types.pyobject)
    gkzi__gmhf = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(dnik__petmn + [qbd__jlhad, gkzi__gmhf])


@intrinsic
def init_table(typingctx, table_type, to_str_if_dict_t):
    out_table_type = table_type.instance_type if isinstance(table_type,
        types.TypeRef) else table_type
    assert isinstance(out_table_type, TableType
        ), 'table type or typeref expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        out_table_type = to_str_arr_if_dict_array(out_table_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(out_table_type)(context, builder)
        for lqa__okayt, unj__mgap in out_table_type.type_to_blk.items():
            lqux__ska = context.get_constant_null(types.List(lqa__okayt))
            setattr(table, f'block_{unj__mgap}', lqux__ska)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    msgrm__haqx = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        msgrm__haqx[typ.dtype] = i
    ycv__igcmy = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(ycv__igcmy, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        aevq__gedii, mjsjz__zufw = args
        table = cgutils.create_struct_proxy(ycv__igcmy)(context, builder)
        for lqa__okayt, unj__mgap in ycv__igcmy.type_to_blk.items():
            idx = msgrm__haqx[lqa__okayt]
            ttu__yzo = signature(types.List(lqa__okayt),
                tuple_of_lists_type, types.literal(idx))
            mezhf__jiyiq = aevq__gedii, idx
            itcaf__did = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, ttu__yzo, mezhf__jiyiq)
            setattr(table, f'block_{unj__mgap}', itcaf__did)
        return table._getvalue()
    sig = ycv__igcmy(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    unj__mgap = get_overload_const_int(blk_type)
    arr_type = None
    for lqa__okayt, fkaj__xxyrs in table_type.type_to_blk.items():
        if fkaj__xxyrs == unj__mgap:
            arr_type = lqa__okayt
            break
    assert arr_type is not None, 'invalid table type block'
    gbav__xsbvq = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        ijhro__tkois = getattr(table, f'block_{unj__mgap}')
        return impl_ret_borrowed(context, builder, gbav__xsbvq, ijhro__tkois)
    sig = gbav__xsbvq(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, bkin__bygt = args
        aumw__vvys = context.get_python_api(builder)
        qsbgh__gbgqv = used_cols_typ == types.none
        if not qsbgh__gbgqv:
            zek__spjdw = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), bkin__bygt)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for lqa__okayt, unj__mgap in table_type.type_to_blk.items():
            dgr__bvk = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[unj__mgap]))
            jigwa__hfyu = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                unj__mgap], dtype=np.int64))
            hznvz__fgjd = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, jigwa__hfyu)
            ijhro__tkois = getattr(table, f'block_{unj__mgap}')
            with cgutils.for_range(builder, dgr__bvk) as sokm__utmfn:
                i = sokm__utmfn.index
                sbdy__cnig = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    hznvz__fgjd, i)
                dfc__zpe = types.none(table_type, types.List(lqa__okayt),
                    types.int64, types.int64)
                deb__zmzf = table_arg, ijhro__tkois, i, sbdy__cnig
                if qsbgh__gbgqv:
                    ensure_column_unboxed_codegen(context, builder,
                        dfc__zpe, deb__zmzf)
                else:
                    bhknc__rhw = zek__spjdw.contains(sbdy__cnig)
                    with builder.if_then(bhknc__rhw):
                        ensure_column_unboxed_codegen(context, builder,
                            dfc__zpe, deb__zmzf)
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, used_cols_typ)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t, arr_ind_t):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, abski__gnv, icvqp__nfx, jfrt__roswq = args
    aumw__vvys = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    ftgs__pcfa = cgutils.is_not_null(builder, table.parent)
    ixo__srjyk = ListInstance(context, builder, sig.args[1], abski__gnv)
    jrttw__ijc = ixo__srjyk.getitem(icvqp__nfx)
    xtndu__zkznp = cgutils.alloca_once_value(builder, jrttw__ijc)
    qapeb__xvp = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, xtndu__zkznp, qapeb__xvp)
    with builder.if_then(is_null):
        with builder.if_else(ftgs__pcfa) as (wzzun__qxpqt, cjh__vpfl):
            with wzzun__qxpqt:
                vdb__dgif = get_df_obj_column_codegen(context, builder,
                    aumw__vvys, table.parent, jfrt__roswq, sig.args[1].dtype)
                arr = aumw__vvys.to_native_value(sig.args[1].dtype, vdb__dgif
                    ).value
                ixo__srjyk.inititem(icvqp__nfx, arr, incref=False)
                aumw__vvys.decref(vdb__dgif)
            with cjh__vpfl:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    unj__mgap = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, gfc__agr, mjsjz__zufw = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{unj__mgap}', gfc__agr)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, vnuf__msxfy = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = vnuf__msxfy
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        hvcl__neq, fow__kytfn = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, fow__kytfn)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, hvcl__neq)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    gbav__xsbvq = list_type.instance_type if isinstance(list_type, types.
        TypeRef) else list_type
    assert isinstance(gbav__xsbvq, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        gbav__xsbvq = types.List(to_str_arr_if_dict_array(gbav__xsbvq.dtype))

    def codegen(context, builder, sig, args):
        rdh__wagws = args[1]
        mjsjz__zufw, ezdo__soe = ListInstance.allocate_ex(context, builder,
            gbav__xsbvq, rdh__wagws)
        ezdo__soe.size = rdh__wagws
        return ezdo__soe.value
    sig = gbav__xsbvq(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    srxd__iko = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(srxd__iko)

    def codegen(context, builder, sig, args):
        rdh__wagws, mjsjz__zufw = args
        mjsjz__zufw, ezdo__soe = ListInstance.allocate_ex(context, builder,
            list_type, rdh__wagws)
        ezdo__soe.size = rdh__wagws
        return ezdo__soe.value
    sig = list_type(size_typ, data_typ)
    return sig, codegen


def _get_idx_length(idx):
    pass


@overload(_get_idx_length)
def overload_get_idx_length(idx, n):
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        return lambda idx, n: idx.sum()
    assert isinstance(idx, types.SliceType), 'slice index expected'

    def impl(idx, n):
        xtc__rgrj = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(xtc__rgrj)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    uiwhf__cfhbi = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        iekh__zvntv = used_cols.instance_type
        ifsr__omt = np.array(iekh__zvntv.meta, dtype=np.int64)
        uiwhf__cfhbi['used_cols_vals'] = ifsr__omt
        wuyxh__mock = set([T.block_nums[i] for i in ifsr__omt])
    else:
        ifsr__omt = None
    rwzln__ngv = 'def table_filter_func(T, idx, used_cols=None):\n'
    rwzln__ngv += f'  T2 = init_table(T, False)\n'
    rwzln__ngv += f'  l = 0\n'
    if ifsr__omt is not None and len(ifsr__omt) == 0:
        rwzln__ngv += f'  l = _get_idx_length(idx, len(T))\n'
        rwzln__ngv += f'  T2 = set_table_len(T2, l)\n'
        rwzln__ngv += f'  return T2\n'
        uzfn__jnh = {}
        exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
        return uzfn__jnh['table_filter_func']
    if ifsr__omt is not None:
        rwzln__ngv += f'  used_set = set(used_cols_vals)\n'
    for unj__mgap in T.type_to_blk.values():
        rwzln__ngv += (
            f'  arr_list_{unj__mgap} = get_table_block(T, {unj__mgap})\n')
        rwzln__ngv += f"""  out_arr_list_{unj__mgap} = alloc_list_like(arr_list_{unj__mgap}, len(arr_list_{unj__mgap}), False)
"""
        if ifsr__omt is None or unj__mgap in wuyxh__mock:
            uiwhf__cfhbi[f'arr_inds_{unj__mgap}'] = np.array(T.
                block_to_arr_ind[unj__mgap], dtype=np.int64)
            rwzln__ngv += f'  for i in range(len(arr_list_{unj__mgap})):\n'
            rwzln__ngv += (
                f'    arr_ind_{unj__mgap} = arr_inds_{unj__mgap}[i]\n')
            if ifsr__omt is not None:
                rwzln__ngv += (
                    f'    if arr_ind_{unj__mgap} not in used_set: continue\n')
            rwzln__ngv += f"""    ensure_column_unboxed(T, arr_list_{unj__mgap}, i, arr_ind_{unj__mgap})
"""
            rwzln__ngv += f"""    out_arr_{unj__mgap} = ensure_contig_if_np(arr_list_{unj__mgap}[i][idx])
"""
            rwzln__ngv += f'    l = len(out_arr_{unj__mgap})\n'
            rwzln__ngv += (
                f'    out_arr_list_{unj__mgap}[i] = out_arr_{unj__mgap}\n')
        rwzln__ngv += (
            f'  T2 = set_table_block(T2, out_arr_list_{unj__mgap}, {unj__mgap})\n'
            )
    rwzln__ngv += f'  T2 = set_table_len(T2, l)\n'
    rwzln__ngv += f'  return T2\n'
    uzfn__jnh = {}
    exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
    return uzfn__jnh['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    byuuq__vfv = list(idx.instance_type.meta)
    hyaq__zayr = tuple(np.array(T.arr_types, dtype=object)[byuuq__vfv])
    rtbg__mjfr = TableType(hyaq__zayr)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    mtksj__wxj = is_overload_true(copy_arrs)
    uiwhf__cfhbi = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': rtbg__mjfr}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        dgavc__hguqa = set(kept_cols)
        uiwhf__cfhbi['kept_cols'] = np.array(kept_cols, np.int64)
        oxx__lap = True
    else:
        oxx__lap = False
    rgf__ajj = {i: c for i, c in enumerate(byuuq__vfv)}
    rwzln__ngv = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    rwzln__ngv += f'  T2 = init_table(out_table_typ, False)\n'
    rwzln__ngv += f'  T2 = set_table_len(T2, len(T))\n'
    if oxx__lap and len(dgavc__hguqa) == 0:
        rwzln__ngv += f'  return T2\n'
        uzfn__jnh = {}
        exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
        return uzfn__jnh['table_subset']
    if oxx__lap:
        rwzln__ngv += f'  kept_cols_set = set(kept_cols)\n'
    for typ, unj__mgap in rtbg__mjfr.type_to_blk.items():
        ypq__eyz = T.type_to_blk[typ]
        rwzln__ngv += (
            f'  arr_list_{unj__mgap} = get_table_block(T, {ypq__eyz})\n')
        rwzln__ngv += f"""  out_arr_list_{unj__mgap} = alloc_list_like(arr_list_{unj__mgap}, {len(rtbg__mjfr.block_to_arr_ind[unj__mgap])}, False)
"""
        xzdqx__iccwc = True
        if oxx__lap:
            yqpd__udbw = set(rtbg__mjfr.block_to_arr_ind[unj__mgap])
            ufif__dtsma = yqpd__udbw & dgavc__hguqa
            xzdqx__iccwc = len(ufif__dtsma) > 0
        if xzdqx__iccwc:
            uiwhf__cfhbi[f'out_arr_inds_{unj__mgap}'] = np.array(rtbg__mjfr
                .block_to_arr_ind[unj__mgap], dtype=np.int64)
            rwzln__ngv += f'  for i in range(len(out_arr_list_{unj__mgap})):\n'
            rwzln__ngv += (
                f'    out_arr_ind_{unj__mgap} = out_arr_inds_{unj__mgap}[i]\n')
            if oxx__lap:
                rwzln__ngv += (
                    f'    if out_arr_ind_{unj__mgap} not in kept_cols_set: continue\n'
                    )
            jrdy__fes = []
            qea__fpm = []
            for omp__dwz in rtbg__mjfr.block_to_arr_ind[unj__mgap]:
                dbv__kmec = rgf__ajj[omp__dwz]
                jrdy__fes.append(dbv__kmec)
                bupib__zzi = T.block_offsets[dbv__kmec]
                qea__fpm.append(bupib__zzi)
            uiwhf__cfhbi[f'in_logical_idx_{unj__mgap}'] = np.array(jrdy__fes,
                dtype=np.int64)
            uiwhf__cfhbi[f'in_physical_idx_{unj__mgap}'] = np.array(qea__fpm,
                dtype=np.int64)
            rwzln__ngv += (
                f'    logical_idx_{unj__mgap} = in_logical_idx_{unj__mgap}[i]\n'
                )
            rwzln__ngv += (
                f'    physical_idx_{unj__mgap} = in_physical_idx_{unj__mgap}[i]\n'
                )
            rwzln__ngv += f"""    ensure_column_unboxed(T, arr_list_{unj__mgap}, physical_idx_{unj__mgap}, logical_idx_{unj__mgap})
"""
            xlpn__gvqs = '.copy()' if mtksj__wxj else ''
            rwzln__ngv += f"""    out_arr_list_{unj__mgap}[i] = arr_list_{unj__mgap}[physical_idx_{unj__mgap}]{xlpn__gvqs}
"""
        rwzln__ngv += (
            f'  T2 = set_table_block(T2, out_arr_list_{unj__mgap}, {unj__mgap})\n'
            )
    rwzln__ngv += f'  return T2\n'
    uzfn__jnh = {}
    exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
    return uzfn__jnh['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    wws__stxid = args[0]
    if equiv_set.has_shape(wws__stxid):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=wws__stxid, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (wws__stxid)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    wws__stxid = args[0]
    if equiv_set.has_shape(wws__stxid):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            wws__stxid)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    rwzln__ngv = 'def impl(T):\n'
    rwzln__ngv += f'  T2 = init_table(T, True)\n'
    rwzln__ngv += f'  l = len(T)\n'
    uiwhf__cfhbi = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for unj__mgap in T.type_to_blk.values():
        uiwhf__cfhbi[f'arr_inds_{unj__mgap}'] = np.array(T.block_to_arr_ind
            [unj__mgap], dtype=np.int64)
        rwzln__ngv += (
            f'  arr_list_{unj__mgap} = get_table_block(T, {unj__mgap})\n')
        rwzln__ngv += f"""  out_arr_list_{unj__mgap} = alloc_list_like(arr_list_{unj__mgap}, len(arr_list_{unj__mgap}), True)
"""
        rwzln__ngv += f'  for i in range(len(arr_list_{unj__mgap})):\n'
        rwzln__ngv += f'    arr_ind_{unj__mgap} = arr_inds_{unj__mgap}[i]\n'
        rwzln__ngv += f"""    ensure_column_unboxed(T, arr_list_{unj__mgap}, i, arr_ind_{unj__mgap})
"""
        rwzln__ngv += (
            f'    out_arr_{unj__mgap} = decode_if_dict_array(arr_list_{unj__mgap}[i])\n'
            )
        rwzln__ngv += (
            f'    out_arr_list_{unj__mgap}[i] = out_arr_{unj__mgap}\n')
        rwzln__ngv += (
            f'  T2 = set_table_block(T2, out_arr_list_{unj__mgap}, {unj__mgap})\n'
            )
    rwzln__ngv += f'  T2 = set_table_len(T2, l)\n'
    rwzln__ngv += f'  return T2\n'
    uzfn__jnh = {}
    exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
    return uzfn__jnh['impl']


@overload(operator.getitem, no_unliteral=True, inline='always')
def overload_table_getitem(T, idx):
    if not isinstance(T, TableType):
        return
    return lambda T, idx: table_filter(T, idx)


@intrinsic
def init_runtime_table_from_lists(typingctx, arr_list_tup_typ, nrows_typ=None):
    assert isinstance(arr_list_tup_typ, types.BaseTuple
        ), 'init_runtime_table_from_lists requires a tuple of list of arrays'
    if isinstance(arr_list_tup_typ, types.UniTuple):
        if arr_list_tup_typ.dtype.dtype == types.undefined:
            return
        pkn__lej = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        pkn__lej = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            pkn__lej.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        wbhbq__dyp, iwuie__vyj = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = iwuie__vyj
        dnik__petmn = cgutils.unpack_tuple(builder, wbhbq__dyp)
        for i, ijhro__tkois in enumerate(dnik__petmn):
            setattr(table, f'block_{i}', ijhro__tkois)
            context.nrt.incref(builder, types.List(pkn__lej[i]), ijhro__tkois)
        return table._getvalue()
    table_type = TableType(tuple(pkn__lej), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    uiwhf__cfhbi = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        uiwhf__cfhbi['kept_cols'] = np.array(list(kept_cols), np.int64)
        oxx__lap = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        oxx__lap = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    fsbmu__apah = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        fsbmu__apah else extra_arrs_t.types[i - fsbmu__apah] for i in
        in_col_inds)) if is_overload_none(out_table_type_t
        ) else unwrap_typeref(out_table_type_t)
    rwzln__ngv = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    rwzln__ngv += f'  T1 = in_table_t\n'
    rwzln__ngv += f'  T2 = init_table(out_table_type, False)\n'
    rwzln__ngv += f'  T2 = set_table_len(T2, len(T1))\n'
    if oxx__lap and len(kept_cols) == 0:
        rwzln__ngv += f'  return T2\n'
        uzfn__jnh = {}
        exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
        return uzfn__jnh['impl']
    if oxx__lap:
        rwzln__ngv += f'  kept_cols_set = set(kept_cols)\n'
    for typ, unj__mgap in out_table_type.type_to_blk.items():
        uiwhf__cfhbi[f'arr_list_typ_{unj__mgap}'] = types.List(typ)
        dgr__bvk = len(out_table_type.block_to_arr_ind[unj__mgap])
        rwzln__ngv += f"""  out_arr_list_{unj__mgap} = alloc_list_like(arr_list_typ_{unj__mgap}, {dgr__bvk}, False)
"""
        if typ in in_table_t.type_to_blk:
            aeoh__qzyfb = in_table_t.type_to_blk[typ]
            zfb__ytby = []
            fgf__grz = []
            for iinir__clblz in out_table_type.block_to_arr_ind[unj__mgap]:
                ffbnq__hndbl = in_col_inds[iinir__clblz]
                if ffbnq__hndbl < fsbmu__apah:
                    zfb__ytby.append(in_table_t.block_offsets[ffbnq__hndbl])
                    fgf__grz.append(ffbnq__hndbl)
                else:
                    zfb__ytby.append(-1)
                    fgf__grz.append(-1)
            uiwhf__cfhbi[f'in_idxs_{unj__mgap}'] = np.array(zfb__ytby, np.int64
                )
            uiwhf__cfhbi[f'in_arr_inds_{unj__mgap}'] = np.array(fgf__grz,
                np.int64)
            if oxx__lap:
                uiwhf__cfhbi[f'out_arr_inds_{unj__mgap}'] = np.array(
                    out_table_type.block_to_arr_ind[unj__mgap], dtype=np.int64)
            rwzln__ngv += (
                f'  in_arr_list_{unj__mgap} = get_table_block(T1, {aeoh__qzyfb})\n'
                )
            rwzln__ngv += f'  for i in range(len(out_arr_list_{unj__mgap})):\n'
            rwzln__ngv += (
                f'    in_offset_{unj__mgap} = in_idxs_{unj__mgap}[i]\n')
            rwzln__ngv += f'    if in_offset_{unj__mgap} == -1:\n'
            rwzln__ngv += f'      continue\n'
            rwzln__ngv += (
                f'    in_arr_ind_{unj__mgap} = in_arr_inds_{unj__mgap}[i]\n')
            if oxx__lap:
                rwzln__ngv += (
                    f'    if out_arr_inds_{unj__mgap}[i] not in kept_cols_set: continue\n'
                    )
            rwzln__ngv += f"""    ensure_column_unboxed(T1, in_arr_list_{unj__mgap}, in_offset_{unj__mgap}, in_arr_ind_{unj__mgap})
"""
            rwzln__ngv += f"""    out_arr_list_{unj__mgap}[i] = in_arr_list_{unj__mgap}[in_offset_{unj__mgap}]
"""
        for i, iinir__clblz in enumerate(out_table_type.block_to_arr_ind[
            unj__mgap]):
            if iinir__clblz not in kept_cols:
                continue
            ffbnq__hndbl = in_col_inds[iinir__clblz]
            if ffbnq__hndbl >= fsbmu__apah:
                rwzln__ngv += f"""  out_arr_list_{unj__mgap}[{i}] = extra_arrs_t[{ffbnq__hndbl - fsbmu__apah}]
"""
        rwzln__ngv += (
            f'  T2 = set_table_block(T2, out_arr_list_{unj__mgap}, {unj__mgap})\n'
            )
    rwzln__ngv += f'  return T2\n'
    uiwhf__cfhbi.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    uzfn__jnh = {}
    exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
    return uzfn__jnh['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    fsbmu__apah = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < fsbmu__apah
         else extra_arrs_t.types[i - fsbmu__apah] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    iswx__lph = None
    if not is_overload_none(in_table_t):
        for i, lqa__okayt in enumerate(in_table_t.types):
            if lqa__okayt != types.none:
                iswx__lph = f'in_table_t[{i}]'
                break
    if iswx__lph is None:
        for i, lqa__okayt in enumerate(extra_arrs_t.types):
            if lqa__okayt != types.none:
                iswx__lph = f'extra_arrs_t[{i}]'
                break
    assert iswx__lph is not None, 'no array found in input data'
    rwzln__ngv = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    rwzln__ngv += f'  T1 = in_table_t\n'
    rwzln__ngv += f'  T2 = init_table(out_table_type, False)\n'
    rwzln__ngv += f'  T2 = set_table_len(T2, len({iswx__lph}))\n'
    uiwhf__cfhbi = {}
    for typ, unj__mgap in out_table_type.type_to_blk.items():
        uiwhf__cfhbi[f'arr_list_typ_{unj__mgap}'] = types.List(typ)
        dgr__bvk = len(out_table_type.block_to_arr_ind[unj__mgap])
        rwzln__ngv += f"""  out_arr_list_{unj__mgap} = alloc_list_like(arr_list_typ_{unj__mgap}, {dgr__bvk}, False)
"""
        for i, iinir__clblz in enumerate(out_table_type.block_to_arr_ind[
            unj__mgap]):
            if iinir__clblz not in kept_cols:
                continue
            ffbnq__hndbl = in_col_inds[iinir__clblz]
            if ffbnq__hndbl < fsbmu__apah:
                rwzln__ngv += (
                    f'  out_arr_list_{unj__mgap}[{i}] = T1[{ffbnq__hndbl}]\n')
            else:
                rwzln__ngv += f"""  out_arr_list_{unj__mgap}[{i}] = extra_arrs_t[{ffbnq__hndbl - fsbmu__apah}]
"""
        rwzln__ngv += (
            f'  T2 = set_table_block(T2, out_arr_list_{unj__mgap}, {unj__mgap})\n'
            )
    rwzln__ngv += f'  return T2\n'
    uiwhf__cfhbi.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    uzfn__jnh = {}
    exec(rwzln__ngv, uiwhf__cfhbi, uzfn__jnh)
    return uzfn__jnh['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    epxkb__zgite = args[0]
    imgf__hzosc = args[1]
    if equiv_set.has_shape(epxkb__zgite):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            epxkb__zgite)[0], None), pre=[])
    if equiv_set.has_shape(imgf__hzosc):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            imgf__hzosc)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
