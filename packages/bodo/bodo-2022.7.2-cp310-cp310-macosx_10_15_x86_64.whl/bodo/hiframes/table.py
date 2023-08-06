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
            hqxt__zbij = 0
            ruh__uvi = []
            for i in range(usecols[-1] + 1):
                if i == usecols[hqxt__zbij]:
                    ruh__uvi.append(arrs[hqxt__zbij])
                    hqxt__zbij += 1
                else:
                    ruh__uvi.append(None)
            for bbjje__kico in range(usecols[-1] + 1, num_arrs):
                ruh__uvi.append(None)
            self.arrays = ruh__uvi
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((dhrt__evaho == pqbj__unbgd).all() for 
            dhrt__evaho, pqbj__unbgd in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        hole__ynlxh = len(self.arrays)
        iopdl__lpj = dict(zip(range(hole__ynlxh), self.arrays))
        df = pd.DataFrame(iopdl__lpj, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        xtrqf__nonfw = []
        zyqfw__xzdw = []
        iuxwg__mfkod = {}
        lkda__ajwq = {}
        cdcot__hwm = defaultdict(int)
        clckj__ncx = defaultdict(list)
        if not has_runtime_cols:
            for i, ydwjp__wxj in enumerate(arr_types):
                if ydwjp__wxj not in iuxwg__mfkod:
                    gwedl__wvxt = len(iuxwg__mfkod)
                    iuxwg__mfkod[ydwjp__wxj] = gwedl__wvxt
                    lkda__ajwq[gwedl__wvxt] = ydwjp__wxj
                zxjr__oyt = iuxwg__mfkod[ydwjp__wxj]
                xtrqf__nonfw.append(zxjr__oyt)
                zyqfw__xzdw.append(cdcot__hwm[zxjr__oyt])
                cdcot__hwm[zxjr__oyt] += 1
                clckj__ncx[zxjr__oyt].append(i)
        self.block_nums = xtrqf__nonfw
        self.block_offsets = zyqfw__xzdw
        self.type_to_blk = iuxwg__mfkod
        self.blk_to_type = lkda__ajwq
        self.block_to_arr_ind = clckj__ncx
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
            rxxvh__vvo = [(f'block_{i}', types.List(ydwjp__wxj)) for i,
                ydwjp__wxj in enumerate(fe_type.arr_types)]
        else:
            rxxvh__vvo = [(f'block_{zxjr__oyt}', types.List(ydwjp__wxj)) for
                ydwjp__wxj, zxjr__oyt in fe_type.type_to_blk.items()]
        rxxvh__vvo.append(('parent', types.pyobject))
        rxxvh__vvo.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, rxxvh__vvo)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    cuxyn__xymuu = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    rhc__bcf = c.pyapi.make_none()
    ipki__dnhw = c.context.get_constant(types.int64, 0)
    kphv__iinzx = cgutils.alloca_once_value(c.builder, ipki__dnhw)
    for ydwjp__wxj, zxjr__oyt in typ.type_to_blk.items():
        keku__dwiic = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[zxjr__oyt]))
        bbjje__kico, zpw__rjfl = ListInstance.allocate_ex(c.context, c.
            builder, types.List(ydwjp__wxj), keku__dwiic)
        zpw__rjfl.size = keku__dwiic
        mqtyc__rjw = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[zxjr__oyt],
            dtype=np.int64))
        qtv__gsqc = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, mqtyc__rjw)
        with cgutils.for_range(c.builder, keku__dwiic) as cmhk__zyqv:
            i = cmhk__zyqv.index
            jhzy__afb = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), qtv__gsqc, i)
            zylxl__aia = c.pyapi.long_from_longlong(jhzy__afb)
            iaa__hni = c.pyapi.object_getitem(cuxyn__xymuu, zylxl__aia)
            fihr__xebbk = c.builder.icmp_unsigned('==', iaa__hni, rhc__bcf)
            with c.builder.if_else(fihr__xebbk) as (rywk__kvc, dmm__ncscb):
                with rywk__kvc:
                    eff__njbso = c.context.get_constant_null(ydwjp__wxj)
                    zpw__rjfl.inititem(i, eff__njbso, incref=False)
                with dmm__ncscb:
                    yxbtq__vwar = c.pyapi.call_method(iaa__hni, '__len__', ())
                    qpt__wnv = c.pyapi.long_as_longlong(yxbtq__vwar)
                    c.builder.store(qpt__wnv, kphv__iinzx)
                    c.pyapi.decref(yxbtq__vwar)
                    arr = c.pyapi.to_native_value(ydwjp__wxj, iaa__hni).value
                    zpw__rjfl.inititem(i, arr, incref=False)
            c.pyapi.decref(iaa__hni)
            c.pyapi.decref(zylxl__aia)
        setattr(table, f'block_{zxjr__oyt}', zpw__rjfl.value)
    table.len = c.builder.load(kphv__iinzx)
    c.pyapi.decref(cuxyn__xymuu)
    c.pyapi.decref(rhc__bcf)
    qgnn__jydv = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=qgnn__jydv)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        vrrhq__keqv = c.context.get_constant(types.int64, 0)
        for i, ydwjp__wxj in enumerate(typ.arr_types):
            ruh__uvi = getattr(table, f'block_{i}')
            ihii__exodi = ListInstance(c.context, c.builder, types.List(
                ydwjp__wxj), ruh__uvi)
            vrrhq__keqv = c.builder.add(vrrhq__keqv, ihii__exodi.size)
        ugou__cuuj = c.pyapi.list_new(vrrhq__keqv)
        lmee__svpa = c.context.get_constant(types.int64, 0)
        for i, ydwjp__wxj in enumerate(typ.arr_types):
            ruh__uvi = getattr(table, f'block_{i}')
            ihii__exodi = ListInstance(c.context, c.builder, types.List(
                ydwjp__wxj), ruh__uvi)
            with cgutils.for_range(c.builder, ihii__exodi.size) as cmhk__zyqv:
                i = cmhk__zyqv.index
                arr = ihii__exodi.getitem(i)
                c.context.nrt.incref(c.builder, ydwjp__wxj, arr)
                idx = c.builder.add(lmee__svpa, i)
                c.pyapi.list_setitem(ugou__cuuj, idx, c.pyapi.
                    from_native_value(ydwjp__wxj, arr, c.env_manager))
            lmee__svpa = c.builder.add(lmee__svpa, ihii__exodi.size)
        xvr__miyjr = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        iihlr__fnu = c.pyapi.call_function_objargs(xvr__miyjr, (ugou__cuuj,))
        c.pyapi.decref(xvr__miyjr)
        c.pyapi.decref(ugou__cuuj)
        c.context.nrt.decref(c.builder, typ, val)
        return iihlr__fnu
    ugou__cuuj = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    kjzx__tkeui = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for ydwjp__wxj, zxjr__oyt in typ.type_to_blk.items():
        ruh__uvi = getattr(table, f'block_{zxjr__oyt}')
        ihii__exodi = ListInstance(c.context, c.builder, types.List(
            ydwjp__wxj), ruh__uvi)
        mqtyc__rjw = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[zxjr__oyt],
            dtype=np.int64))
        qtv__gsqc = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, mqtyc__rjw)
        with cgutils.for_range(c.builder, ihii__exodi.size) as cmhk__zyqv:
            i = cmhk__zyqv.index
            jhzy__afb = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), qtv__gsqc, i)
            arr = ihii__exodi.getitem(i)
            bxp__oig = cgutils.alloca_once_value(c.builder, arr)
            dpe__mklsw = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(ydwjp__wxj))
            is_null = is_ll_eq(c.builder, bxp__oig, dpe__mklsw)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (rywk__kvc, dmm__ncscb):
                with rywk__kvc:
                    rhc__bcf = c.pyapi.make_none()
                    c.pyapi.list_setitem(ugou__cuuj, jhzy__afb, rhc__bcf)
                with dmm__ncscb:
                    iaa__hni = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, kjzx__tkeui)
                        ) as (kuooy__ukrf, onpi__fbwk):
                        with kuooy__ukrf:
                            ytw__ispvq = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                jhzy__afb, ydwjp__wxj)
                            c.builder.store(ytw__ispvq, iaa__hni)
                        with onpi__fbwk:
                            c.context.nrt.incref(c.builder, ydwjp__wxj, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                ydwjp__wxj, arr, c.env_manager), iaa__hni)
                    c.pyapi.list_setitem(ugou__cuuj, jhzy__afb, c.builder.
                        load(iaa__hni))
    xvr__miyjr = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    iihlr__fnu = c.pyapi.call_function_objargs(xvr__miyjr, (ugou__cuuj,))
    c.pyapi.decref(xvr__miyjr)
    c.pyapi.decref(ugou__cuuj)
    c.context.nrt.decref(c.builder, typ, val)
    return iihlr__fnu


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
        lbat__ovcle = context.get_constant(types.int64, 0)
        for i, ydwjp__wxj in enumerate(table_type.arr_types):
            ruh__uvi = getattr(table, f'block_{i}')
            ihii__exodi = ListInstance(context, builder, types.List(
                ydwjp__wxj), ruh__uvi)
            lbat__ovcle = builder.add(lbat__ovcle, ihii__exodi.size)
        return lbat__ovcle
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    zxjr__oyt = table_type.block_nums[col_ind]
    ifdr__kfdqi = table_type.block_offsets[col_ind]
    ruh__uvi = getattr(table, f'block_{zxjr__oyt}')
    skqx__gkr = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    awjjn__aobnk = context.get_constant(types.int64, col_ind)
    lvaor__gmymc = context.get_constant(types.int64, ifdr__kfdqi)
    xnp__ihawh = table_arg, ruh__uvi, lvaor__gmymc, awjjn__aobnk
    ensure_column_unboxed_codegen(context, builder, skqx__gkr, xnp__ihawh)
    ihii__exodi = ListInstance(context, builder, types.List(arr_type), ruh__uvi
        )
    arr = ihii__exodi.getitem(ifdr__kfdqi)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, bbjje__kico = args
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
    vmfyv__ufhvx = list(ind_typ.instance_type.meta)
    rpq__qjsa = defaultdict(list)
    for ind in vmfyv__ufhvx:
        rpq__qjsa[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, bbjje__kico = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for zxjr__oyt, phe__szq in rpq__qjsa.items():
            arr_type = table_type.blk_to_type[zxjr__oyt]
            ruh__uvi = getattr(table, f'block_{zxjr__oyt}')
            ihii__exodi = ListInstance(context, builder, types.List(
                arr_type), ruh__uvi)
            eff__njbso = context.get_constant_null(arr_type)
            if len(phe__szq) == 1:
                ifdr__kfdqi = phe__szq[0]
                arr = ihii__exodi.getitem(ifdr__kfdqi)
                context.nrt.decref(builder, arr_type, arr)
                ihii__exodi.inititem(ifdr__kfdqi, eff__njbso, incref=False)
            else:
                keku__dwiic = context.get_constant(types.int64, len(phe__szq))
                kydmi__znqhd = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(phe__szq, dtype=np
                    .int64))
                lsvqo__jxx = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, kydmi__znqhd)
                with cgutils.for_range(builder, keku__dwiic) as cmhk__zyqv:
                    i = cmhk__zyqv.index
                    ifdr__kfdqi = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), lsvqo__jxx, i)
                    arr = ihii__exodi.getitem(ifdr__kfdqi)
                    context.nrt.decref(builder, arr_type, arr)
                    ihii__exodi.inititem(ifdr__kfdqi, eff__njbso, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    ipki__dnhw = context.get_constant(types.int64, 0)
    vpult__qam = context.get_constant(types.int64, 1)
    xjom__khw = arr_type not in in_table_type.type_to_blk
    for ydwjp__wxj, zxjr__oyt in out_table_type.type_to_blk.items():
        if ydwjp__wxj in in_table_type.type_to_blk:
            acghv__efxk = in_table_type.type_to_blk[ydwjp__wxj]
            zpw__rjfl = ListInstance(context, builder, types.List(
                ydwjp__wxj), getattr(in_table, f'block_{acghv__efxk}'))
            context.nrt.incref(builder, types.List(ydwjp__wxj), zpw__rjfl.value
                )
            setattr(out_table, f'block_{zxjr__oyt}', zpw__rjfl.value)
    if xjom__khw:
        bbjje__kico, zpw__rjfl = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), vpult__qam)
        zpw__rjfl.size = vpult__qam
        zpw__rjfl.inititem(ipki__dnhw, arr_arg, incref=True)
        zxjr__oyt = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{zxjr__oyt}', zpw__rjfl.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        zxjr__oyt = out_table_type.type_to_blk[arr_type]
        zpw__rjfl = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{zxjr__oyt}'))
        if is_new_col:
            n = zpw__rjfl.size
            xpucj__ssuli = builder.add(n, vpult__qam)
            zpw__rjfl.resize(xpucj__ssuli)
            zpw__rjfl.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            snj__sivoj = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            zpw__rjfl.setitem(snj__sivoj, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            snj__sivoj = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = zpw__rjfl.size
            xpucj__ssuli = builder.add(n, vpult__qam)
            zpw__rjfl.resize(xpucj__ssuli)
            context.nrt.incref(builder, arr_type, zpw__rjfl.getitem(snj__sivoj)
                )
            zpw__rjfl.move(builder.add(snj__sivoj, vpult__qam), snj__sivoj,
                builder.sub(n, snj__sivoj))
            zpw__rjfl.setitem(snj__sivoj, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    hvhx__qmrnf = in_table_type.arr_types[col_ind]
    if hvhx__qmrnf in out_table_type.type_to_blk:
        zxjr__oyt = out_table_type.type_to_blk[hvhx__qmrnf]
        igoc__ksooq = getattr(out_table, f'block_{zxjr__oyt}')
        tuh__ebi = types.List(hvhx__qmrnf)
        snj__sivoj = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        tpqpl__uau = tuh__ebi.dtype(tuh__ebi, types.intp)
        jjrh__bxa = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), tpqpl__uau, (igoc__ksooq, snj__sivoj))
        context.nrt.decref(builder, hvhx__qmrnf, jjrh__bxa)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    dlcxx__fqcy = list(table.arr_types)
    if ind == len(dlcxx__fqcy):
        xnwxl__ksvpz = None
        dlcxx__fqcy.append(arr_type)
    else:
        xnwxl__ksvpz = table.arr_types[ind]
        dlcxx__fqcy[ind] = arr_type
    xdzps__tbjhm = TableType(tuple(dlcxx__fqcy))
    qek__gyi = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': xdzps__tbjhm}
    laay__dbq = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    laay__dbq += f'  T2 = init_table(out_table_typ, False)\n'
    laay__dbq += f'  T2 = set_table_len(T2, len(table))\n'
    laay__dbq += f'  T2 = set_table_parent(T2, table)\n'
    for typ, zxjr__oyt in xdzps__tbjhm.type_to_blk.items():
        if typ in table.type_to_blk:
            gehk__nlcyu = table.type_to_blk[typ]
            laay__dbq += (
                f'  arr_list_{zxjr__oyt} = get_table_block(table, {gehk__nlcyu})\n'
                )
            laay__dbq += f"""  out_arr_list_{zxjr__oyt} = alloc_list_like(arr_list_{zxjr__oyt}, {len(xdzps__tbjhm.block_to_arr_ind[zxjr__oyt])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[gehk__nlcyu]
                ) & used_cols:
                laay__dbq += f'  for i in range(len(arr_list_{zxjr__oyt})):\n'
                if typ not in (xnwxl__ksvpz, arr_type):
                    laay__dbq += (
                        f'    out_arr_list_{zxjr__oyt}[i] = arr_list_{zxjr__oyt}[i]\n'
                        )
                else:
                    zgx__rwg = table.block_to_arr_ind[gehk__nlcyu]
                    vpgr__pthi = np.empty(len(zgx__rwg), np.int64)
                    nskm__xnt = False
                    for obato__ybg, jhzy__afb in enumerate(zgx__rwg):
                        if jhzy__afb != ind:
                            eqg__wysag = xdzps__tbjhm.block_offsets[jhzy__afb]
                        else:
                            eqg__wysag = -1
                            nskm__xnt = True
                        vpgr__pthi[obato__ybg] = eqg__wysag
                    qek__gyi[f'out_idxs_{zxjr__oyt}'] = np.array(vpgr__pthi,
                        np.int64)
                    laay__dbq += f'    out_idx = out_idxs_{zxjr__oyt}[i]\n'
                    if nskm__xnt:
                        laay__dbq += f'    if out_idx == -1:\n'
                        laay__dbq += f'      continue\n'
                    laay__dbq += f"""    out_arr_list_{zxjr__oyt}[out_idx] = arr_list_{zxjr__oyt}[i]
"""
            if typ == arr_type and not is_null:
                laay__dbq += f"""  out_arr_list_{zxjr__oyt}[{xdzps__tbjhm.block_offsets[ind]}] = arr
"""
        else:
            qek__gyi[f'arr_list_typ_{zxjr__oyt}'] = types.List(arr_type)
            laay__dbq += f"""  out_arr_list_{zxjr__oyt} = alloc_list_like(arr_list_typ_{zxjr__oyt}, 1, False)
"""
            if not is_null:
                laay__dbq += f'  out_arr_list_{zxjr__oyt}[0] = arr\n'
        laay__dbq += (
            f'  T2 = set_table_block(T2, out_arr_list_{zxjr__oyt}, {zxjr__oyt})\n'
            )
    laay__dbq += f'  return T2\n'
    pcfnz__anhzd = {}
    exec(laay__dbq, qek__gyi, pcfnz__anhzd)
    return pcfnz__anhzd['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        mue__copgf = None
    else:
        mue__copgf = set(used_cols.instance_type.meta)
    dwzoo__ltvsa = get_overload_const_int(ind)
    return generate_set_table_data_code(table, dwzoo__ltvsa, arr, mue__copgf)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    dwzoo__ltvsa = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        mue__copgf = None
    else:
        mue__copgf = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, dwzoo__ltvsa, arr_type,
        mue__copgf, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    eecox__rgow = args[0]
    if equiv_set.has_shape(eecox__rgow):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            eecox__rgow)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    eebsq__fjdte = []
    for ydwjp__wxj, zxjr__oyt in table_type.type_to_blk.items():
        unk__ifj = len(table_type.block_to_arr_ind[zxjr__oyt])
        cix__apyd = []
        for i in range(unk__ifj):
            jhzy__afb = table_type.block_to_arr_ind[zxjr__oyt][i]
            cix__apyd.append(pyval.arrays[jhzy__afb])
        eebsq__fjdte.append(context.get_constant_generic(builder, types.
            List(ydwjp__wxj), cix__apyd))
    xlua__vvlgf = context.get_constant_null(types.pyobject)
    kcyah__nsl = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(eebsq__fjdte + [xlua__vvlgf, kcyah__nsl]
        )


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
        for ydwjp__wxj, zxjr__oyt in out_table_type.type_to_blk.items():
            ajuqc__vzvb = context.get_constant_null(types.List(ydwjp__wxj))
            setattr(table, f'block_{zxjr__oyt}', ajuqc__vzvb)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    xevuf__wjvl = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        xevuf__wjvl[typ.dtype] = i
    imq__cjz = table_type.instance_type if isinstance(table_type, types.TypeRef
        ) else table_type
    assert isinstance(imq__cjz, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        vxerh__bdqzn, bbjje__kico = args
        table = cgutils.create_struct_proxy(imq__cjz)(context, builder)
        for ydwjp__wxj, zxjr__oyt in imq__cjz.type_to_blk.items():
            idx = xevuf__wjvl[ydwjp__wxj]
            qpoq__goixd = signature(types.List(ydwjp__wxj),
                tuple_of_lists_type, types.literal(idx))
            uthq__jjhfz = vxerh__bdqzn, idx
            ipw__hygrb = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, qpoq__goixd, uthq__jjhfz)
            setattr(table, f'block_{zxjr__oyt}', ipw__hygrb)
        return table._getvalue()
    sig = imq__cjz(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    zxjr__oyt = get_overload_const_int(blk_type)
    arr_type = None
    for ydwjp__wxj, pqbj__unbgd in table_type.type_to_blk.items():
        if pqbj__unbgd == zxjr__oyt:
            arr_type = ydwjp__wxj
            break
    assert arr_type is not None, 'invalid table type block'
    epew__nrta = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        ruh__uvi = getattr(table, f'block_{zxjr__oyt}')
        return impl_ret_borrowed(context, builder, epew__nrta, ruh__uvi)
    sig = epew__nrta(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, utkr__cqulf = args
        piujt__hzmt = context.get_python_api(builder)
        alrap__fzsv = used_cols_typ == types.none
        if not alrap__fzsv:
            yoxkz__orv = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), utkr__cqulf)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for ydwjp__wxj, zxjr__oyt in table_type.type_to_blk.items():
            keku__dwiic = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[zxjr__oyt]))
            mqtyc__rjw = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                zxjr__oyt], dtype=np.int64))
            qtv__gsqc = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, mqtyc__rjw)
            ruh__uvi = getattr(table, f'block_{zxjr__oyt}')
            with cgutils.for_range(builder, keku__dwiic) as cmhk__zyqv:
                i = cmhk__zyqv.index
                jhzy__afb = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), qtv__gsqc, i
                    )
                skqx__gkr = types.none(table_type, types.List(ydwjp__wxj),
                    types.int64, types.int64)
                xnp__ihawh = table_arg, ruh__uvi, i, jhzy__afb
                if alrap__fzsv:
                    ensure_column_unboxed_codegen(context, builder,
                        skqx__gkr, xnp__ihawh)
                else:
                    nezu__tyso = yoxkz__orv.contains(jhzy__afb)
                    with builder.if_then(nezu__tyso):
                        ensure_column_unboxed_codegen(context, builder,
                            skqx__gkr, xnp__ihawh)
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
    table_arg, fab__atv, vtngt__ejn, fecp__nmjim = args
    piujt__hzmt = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    kjzx__tkeui = cgutils.is_not_null(builder, table.parent)
    ihii__exodi = ListInstance(context, builder, sig.args[1], fab__atv)
    jgy__edx = ihii__exodi.getitem(vtngt__ejn)
    bxp__oig = cgutils.alloca_once_value(builder, jgy__edx)
    dpe__mklsw = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, bxp__oig, dpe__mklsw)
    with builder.if_then(is_null):
        with builder.if_else(kjzx__tkeui) as (rywk__kvc, dmm__ncscb):
            with rywk__kvc:
                iaa__hni = get_df_obj_column_codegen(context, builder,
                    piujt__hzmt, table.parent, fecp__nmjim, sig.args[1].dtype)
                arr = piujt__hzmt.to_native_value(sig.args[1].dtype, iaa__hni
                    ).value
                ihii__exodi.inititem(vtngt__ejn, arr, incref=False)
                piujt__hzmt.decref(iaa__hni)
            with dmm__ncscb:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    zxjr__oyt = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, utoya__zuu, bbjje__kico = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{zxjr__oyt}', utoya__zuu)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, txg__ttj = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = txg__ttj
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        mlr__vwhwl, dtob__rak = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, dtob__rak)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, mlr__vwhwl)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    epew__nrta = list_type.instance_type if isinstance(list_type, types.TypeRef
        ) else list_type
    assert isinstance(epew__nrta, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        epew__nrta = types.List(to_str_arr_if_dict_array(epew__nrta.dtype))

    def codegen(context, builder, sig, args):
        svnlw__llfp = args[1]
        bbjje__kico, zpw__rjfl = ListInstance.allocate_ex(context, builder,
            epew__nrta, svnlw__llfp)
        zpw__rjfl.size = svnlw__llfp
        return zpw__rjfl.value
    sig = epew__nrta(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    bfh__ytevr = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(bfh__ytevr)

    def codegen(context, builder, sig, args):
        svnlw__llfp, bbjje__kico = args
        bbjje__kico, zpw__rjfl = ListInstance.allocate_ex(context, builder,
            list_type, svnlw__llfp)
        zpw__rjfl.size = svnlw__llfp
        return zpw__rjfl.value
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
        mgbn__efo = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(mgbn__efo)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    qek__gyi = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        ulqyx__gcabj = used_cols.instance_type
        wpqvm__kszf = np.array(ulqyx__gcabj.meta, dtype=np.int64)
        qek__gyi['used_cols_vals'] = wpqvm__kszf
        rhvkf__okj = set([T.block_nums[i] for i in wpqvm__kszf])
    else:
        wpqvm__kszf = None
    laay__dbq = 'def table_filter_func(T, idx, used_cols=None):\n'
    laay__dbq += f'  T2 = init_table(T, False)\n'
    laay__dbq += f'  l = 0\n'
    if wpqvm__kszf is not None and len(wpqvm__kszf) == 0:
        laay__dbq += f'  l = _get_idx_length(idx, len(T))\n'
        laay__dbq += f'  T2 = set_table_len(T2, l)\n'
        laay__dbq += f'  return T2\n'
        pcfnz__anhzd = {}
        exec(laay__dbq, qek__gyi, pcfnz__anhzd)
        return pcfnz__anhzd['table_filter_func']
    if wpqvm__kszf is not None:
        laay__dbq += f'  used_set = set(used_cols_vals)\n'
    for zxjr__oyt in T.type_to_blk.values():
        laay__dbq += (
            f'  arr_list_{zxjr__oyt} = get_table_block(T, {zxjr__oyt})\n')
        laay__dbq += f"""  out_arr_list_{zxjr__oyt} = alloc_list_like(arr_list_{zxjr__oyt}, len(arr_list_{zxjr__oyt}), False)
"""
        if wpqvm__kszf is None or zxjr__oyt in rhvkf__okj:
            qek__gyi[f'arr_inds_{zxjr__oyt}'] = np.array(T.block_to_arr_ind
                [zxjr__oyt], dtype=np.int64)
            laay__dbq += f'  for i in range(len(arr_list_{zxjr__oyt})):\n'
            laay__dbq += f'    arr_ind_{zxjr__oyt} = arr_inds_{zxjr__oyt}[i]\n'
            if wpqvm__kszf is not None:
                laay__dbq += (
                    f'    if arr_ind_{zxjr__oyt} not in used_set: continue\n')
            laay__dbq += f"""    ensure_column_unboxed(T, arr_list_{zxjr__oyt}, i, arr_ind_{zxjr__oyt})
"""
            laay__dbq += f"""    out_arr_{zxjr__oyt} = ensure_contig_if_np(arr_list_{zxjr__oyt}[i][idx])
"""
            laay__dbq += f'    l = len(out_arr_{zxjr__oyt})\n'
            laay__dbq += (
                f'    out_arr_list_{zxjr__oyt}[i] = out_arr_{zxjr__oyt}\n')
        laay__dbq += (
            f'  T2 = set_table_block(T2, out_arr_list_{zxjr__oyt}, {zxjr__oyt})\n'
            )
    laay__dbq += f'  T2 = set_table_len(T2, l)\n'
    laay__dbq += f'  return T2\n'
    pcfnz__anhzd = {}
    exec(laay__dbq, qek__gyi, pcfnz__anhzd)
    return pcfnz__anhzd['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    obdc__qfui = list(idx.instance_type.meta)
    dlcxx__fqcy = tuple(np.array(T.arr_types, dtype=object)[obdc__qfui])
    xdzps__tbjhm = TableType(dlcxx__fqcy)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    vas__kwrgr = is_overload_true(copy_arrs)
    qek__gyi = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': xdzps__tbjhm}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        nambm__arep = set(kept_cols)
        qek__gyi['kept_cols'] = np.array(kept_cols, np.int64)
        huumc__mjzm = True
    else:
        huumc__mjzm = False
    akirl__hsel = {i: c for i, c in enumerate(obdc__qfui)}
    laay__dbq = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    laay__dbq += f'  T2 = init_table(out_table_typ, False)\n'
    laay__dbq += f'  T2 = set_table_len(T2, len(T))\n'
    if huumc__mjzm and len(nambm__arep) == 0:
        laay__dbq += f'  return T2\n'
        pcfnz__anhzd = {}
        exec(laay__dbq, qek__gyi, pcfnz__anhzd)
        return pcfnz__anhzd['table_subset']
    if huumc__mjzm:
        laay__dbq += f'  kept_cols_set = set(kept_cols)\n'
    for typ, zxjr__oyt in xdzps__tbjhm.type_to_blk.items():
        gehk__nlcyu = T.type_to_blk[typ]
        laay__dbq += (
            f'  arr_list_{zxjr__oyt} = get_table_block(T, {gehk__nlcyu})\n')
        laay__dbq += f"""  out_arr_list_{zxjr__oyt} = alloc_list_like(arr_list_{zxjr__oyt}, {len(xdzps__tbjhm.block_to_arr_ind[zxjr__oyt])}, False)
"""
        pgje__riab = True
        if huumc__mjzm:
            iszvy__kdnu = set(xdzps__tbjhm.block_to_arr_ind[zxjr__oyt])
            oou__qad = iszvy__kdnu & nambm__arep
            pgje__riab = len(oou__qad) > 0
        if pgje__riab:
            qek__gyi[f'out_arr_inds_{zxjr__oyt}'] = np.array(xdzps__tbjhm.
                block_to_arr_ind[zxjr__oyt], dtype=np.int64)
            laay__dbq += f'  for i in range(len(out_arr_list_{zxjr__oyt})):\n'
            laay__dbq += (
                f'    out_arr_ind_{zxjr__oyt} = out_arr_inds_{zxjr__oyt}[i]\n')
            if huumc__mjzm:
                laay__dbq += (
                    f'    if out_arr_ind_{zxjr__oyt} not in kept_cols_set: continue\n'
                    )
            jti__unpb = []
            vii__pzjw = []
            for dsxrn__uqi in xdzps__tbjhm.block_to_arr_ind[zxjr__oyt]:
                whh__mhm = akirl__hsel[dsxrn__uqi]
                jti__unpb.append(whh__mhm)
                epr__qdcz = T.block_offsets[whh__mhm]
                vii__pzjw.append(epr__qdcz)
            qek__gyi[f'in_logical_idx_{zxjr__oyt}'] = np.array(jti__unpb,
                dtype=np.int64)
            qek__gyi[f'in_physical_idx_{zxjr__oyt}'] = np.array(vii__pzjw,
                dtype=np.int64)
            laay__dbq += (
                f'    logical_idx_{zxjr__oyt} = in_logical_idx_{zxjr__oyt}[i]\n'
                )
            laay__dbq += (
                f'    physical_idx_{zxjr__oyt} = in_physical_idx_{zxjr__oyt}[i]\n'
                )
            laay__dbq += f"""    ensure_column_unboxed(T, arr_list_{zxjr__oyt}, physical_idx_{zxjr__oyt}, logical_idx_{zxjr__oyt})
"""
            pgxs__hterp = '.copy()' if vas__kwrgr else ''
            laay__dbq += f"""    out_arr_list_{zxjr__oyt}[i] = arr_list_{zxjr__oyt}[physical_idx_{zxjr__oyt}]{pgxs__hterp}
"""
        laay__dbq += (
            f'  T2 = set_table_block(T2, out_arr_list_{zxjr__oyt}, {zxjr__oyt})\n'
            )
    laay__dbq += f'  return T2\n'
    pcfnz__anhzd = {}
    exec(laay__dbq, qek__gyi, pcfnz__anhzd)
    return pcfnz__anhzd['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    eecox__rgow = args[0]
    if equiv_set.has_shape(eecox__rgow):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=eecox__rgow, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (eecox__rgow)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    eecox__rgow = args[0]
    if equiv_set.has_shape(eecox__rgow):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            eecox__rgow)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    laay__dbq = 'def impl(T):\n'
    laay__dbq += f'  T2 = init_table(T, True)\n'
    laay__dbq += f'  l = len(T)\n'
    qek__gyi = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for zxjr__oyt in T.type_to_blk.values():
        qek__gyi[f'arr_inds_{zxjr__oyt}'] = np.array(T.block_to_arr_ind[
            zxjr__oyt], dtype=np.int64)
        laay__dbq += (
            f'  arr_list_{zxjr__oyt} = get_table_block(T, {zxjr__oyt})\n')
        laay__dbq += f"""  out_arr_list_{zxjr__oyt} = alloc_list_like(arr_list_{zxjr__oyt}, len(arr_list_{zxjr__oyt}), True)
"""
        laay__dbq += f'  for i in range(len(arr_list_{zxjr__oyt})):\n'
        laay__dbq += f'    arr_ind_{zxjr__oyt} = arr_inds_{zxjr__oyt}[i]\n'
        laay__dbq += (
            f'    ensure_column_unboxed(T, arr_list_{zxjr__oyt}, i, arr_ind_{zxjr__oyt})\n'
            )
        laay__dbq += (
            f'    out_arr_{zxjr__oyt} = decode_if_dict_array(arr_list_{zxjr__oyt}[i])\n'
            )
        laay__dbq += f'    out_arr_list_{zxjr__oyt}[i] = out_arr_{zxjr__oyt}\n'
        laay__dbq += (
            f'  T2 = set_table_block(T2, out_arr_list_{zxjr__oyt}, {zxjr__oyt})\n'
            )
    laay__dbq += f'  T2 = set_table_len(T2, l)\n'
    laay__dbq += f'  return T2\n'
    pcfnz__anhzd = {}
    exec(laay__dbq, qek__gyi, pcfnz__anhzd)
    return pcfnz__anhzd['impl']


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
        kpdcw__ybh = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        kpdcw__ybh = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            kpdcw__ybh.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        qda__xogm, jnuq__pbnp = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = jnuq__pbnp
        eebsq__fjdte = cgutils.unpack_tuple(builder, qda__xogm)
        for i, ruh__uvi in enumerate(eebsq__fjdte):
            setattr(table, f'block_{i}', ruh__uvi)
            context.nrt.incref(builder, types.List(kpdcw__ybh[i]), ruh__uvi)
        return table._getvalue()
    table_type = TableType(tuple(kpdcw__ybh), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    qek__gyi = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        qek__gyi['kept_cols'] = np.array(list(kept_cols), np.int64)
        huumc__mjzm = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        huumc__mjzm = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    dris__dao = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        dris__dao else extra_arrs_t.types[i - dris__dao] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    laay__dbq = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    laay__dbq += f'  T1 = in_table_t\n'
    laay__dbq += f'  T2 = init_table(out_table_type, False)\n'
    laay__dbq += f'  T2 = set_table_len(T2, len(T1))\n'
    if huumc__mjzm and len(kept_cols) == 0:
        laay__dbq += f'  return T2\n'
        pcfnz__anhzd = {}
        exec(laay__dbq, qek__gyi, pcfnz__anhzd)
        return pcfnz__anhzd['impl']
    if huumc__mjzm:
        laay__dbq += f'  kept_cols_set = set(kept_cols)\n'
    for typ, zxjr__oyt in out_table_type.type_to_blk.items():
        qek__gyi[f'arr_list_typ_{zxjr__oyt}'] = types.List(typ)
        keku__dwiic = len(out_table_type.block_to_arr_ind[zxjr__oyt])
        laay__dbq += f"""  out_arr_list_{zxjr__oyt} = alloc_list_like(arr_list_typ_{zxjr__oyt}, {keku__dwiic}, False)
"""
        if typ in in_table_t.type_to_blk:
            myh__apbar = in_table_t.type_to_blk[typ]
            yint__bhxi = []
            zlrxf__dfzm = []
            for glxas__irk in out_table_type.block_to_arr_ind[zxjr__oyt]:
                lkss__nia = in_col_inds[glxas__irk]
                if lkss__nia < dris__dao:
                    yint__bhxi.append(in_table_t.block_offsets[lkss__nia])
                    zlrxf__dfzm.append(lkss__nia)
                else:
                    yint__bhxi.append(-1)
                    zlrxf__dfzm.append(-1)
            qek__gyi[f'in_idxs_{zxjr__oyt}'] = np.array(yint__bhxi, np.int64)
            qek__gyi[f'in_arr_inds_{zxjr__oyt}'] = np.array(zlrxf__dfzm, np
                .int64)
            if huumc__mjzm:
                qek__gyi[f'out_arr_inds_{zxjr__oyt}'] = np.array(out_table_type
                    .block_to_arr_ind[zxjr__oyt], dtype=np.int64)
            laay__dbq += (
                f'  in_arr_list_{zxjr__oyt} = get_table_block(T1, {myh__apbar})\n'
                )
            laay__dbq += f'  for i in range(len(out_arr_list_{zxjr__oyt})):\n'
            laay__dbq += (
                f'    in_offset_{zxjr__oyt} = in_idxs_{zxjr__oyt}[i]\n')
            laay__dbq += f'    if in_offset_{zxjr__oyt} == -1:\n'
            laay__dbq += f'      continue\n'
            laay__dbq += (
                f'    in_arr_ind_{zxjr__oyt} = in_arr_inds_{zxjr__oyt}[i]\n')
            if huumc__mjzm:
                laay__dbq += (
                    f'    if out_arr_inds_{zxjr__oyt}[i] not in kept_cols_set: continue\n'
                    )
            laay__dbq += f"""    ensure_column_unboxed(T1, in_arr_list_{zxjr__oyt}, in_offset_{zxjr__oyt}, in_arr_ind_{zxjr__oyt})
"""
            laay__dbq += f"""    out_arr_list_{zxjr__oyt}[i] = in_arr_list_{zxjr__oyt}[in_offset_{zxjr__oyt}]
"""
        for i, glxas__irk in enumerate(out_table_type.block_to_arr_ind[
            zxjr__oyt]):
            if glxas__irk not in kept_cols:
                continue
            lkss__nia = in_col_inds[glxas__irk]
            if lkss__nia >= dris__dao:
                laay__dbq += f"""  out_arr_list_{zxjr__oyt}[{i}] = extra_arrs_t[{lkss__nia - dris__dao}]
"""
        laay__dbq += (
            f'  T2 = set_table_block(T2, out_arr_list_{zxjr__oyt}, {zxjr__oyt})\n'
            )
    laay__dbq += f'  return T2\n'
    qek__gyi.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    pcfnz__anhzd = {}
    exec(laay__dbq, qek__gyi, pcfnz__anhzd)
    return pcfnz__anhzd['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    dris__dao = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < dris__dao else
        extra_arrs_t.types[i - dris__dao] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    wvph__lps = None
    if not is_overload_none(in_table_t):
        for i, ydwjp__wxj in enumerate(in_table_t.types):
            if ydwjp__wxj != types.none:
                wvph__lps = f'in_table_t[{i}]'
                break
    if wvph__lps is None:
        for i, ydwjp__wxj in enumerate(extra_arrs_t.types):
            if ydwjp__wxj != types.none:
                wvph__lps = f'extra_arrs_t[{i}]'
                break
    assert wvph__lps is not None, 'no array found in input data'
    laay__dbq = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    laay__dbq += f'  T1 = in_table_t\n'
    laay__dbq += f'  T2 = init_table(out_table_type, False)\n'
    laay__dbq += f'  T2 = set_table_len(T2, len({wvph__lps}))\n'
    qek__gyi = {}
    for typ, zxjr__oyt in out_table_type.type_to_blk.items():
        qek__gyi[f'arr_list_typ_{zxjr__oyt}'] = types.List(typ)
        keku__dwiic = len(out_table_type.block_to_arr_ind[zxjr__oyt])
        laay__dbq += f"""  out_arr_list_{zxjr__oyt} = alloc_list_like(arr_list_typ_{zxjr__oyt}, {keku__dwiic}, False)
"""
        for i, glxas__irk in enumerate(out_table_type.block_to_arr_ind[
            zxjr__oyt]):
            if glxas__irk not in kept_cols:
                continue
            lkss__nia = in_col_inds[glxas__irk]
            if lkss__nia < dris__dao:
                laay__dbq += (
                    f'  out_arr_list_{zxjr__oyt}[{i}] = T1[{lkss__nia}]\n')
            else:
                laay__dbq += f"""  out_arr_list_{zxjr__oyt}[{i}] = extra_arrs_t[{lkss__nia - dris__dao}]
"""
        laay__dbq += (
            f'  T2 = set_table_block(T2, out_arr_list_{zxjr__oyt}, {zxjr__oyt})\n'
            )
    laay__dbq += f'  return T2\n'
    qek__gyi.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    pcfnz__anhzd = {}
    exec(laay__dbq, qek__gyi, pcfnz__anhzd)
    return pcfnz__anhzd['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    fyr__xjmh = args[0]
    mtg__qmrt = args[1]
    if equiv_set.has_shape(fyr__xjmh):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            fyr__xjmh)[0], None), pre=[])
    if equiv_set.has_shape(mtg__qmrt):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            mtg__qmrt)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
