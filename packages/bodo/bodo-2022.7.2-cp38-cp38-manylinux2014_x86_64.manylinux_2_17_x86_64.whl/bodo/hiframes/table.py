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
            mavg__cetcb = 0
            ckcjs__ggpdx = []
            for i in range(usecols[-1] + 1):
                if i == usecols[mavg__cetcb]:
                    ckcjs__ggpdx.append(arrs[mavg__cetcb])
                    mavg__cetcb += 1
                else:
                    ckcjs__ggpdx.append(None)
            for qovvy__fshmt in range(usecols[-1] + 1, num_arrs):
                ckcjs__ggpdx.append(None)
            self.arrays = ckcjs__ggpdx
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((jycit__ftoo == gymrc__lkkf).all() for 
            jycit__ftoo, gymrc__lkkf in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        ffgq__zuk = len(self.arrays)
        zbnf__fjy = dict(zip(range(ffgq__zuk), self.arrays))
        df = pd.DataFrame(zbnf__fjy, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        mlizb__yfkbz = []
        gslg__fgzq = []
        gko__zznbl = {}
        puw__rwp = {}
        xxcyy__rfpp = defaultdict(int)
        vmaz__rrdy = defaultdict(list)
        if not has_runtime_cols:
            for i, lhgfy__oor in enumerate(arr_types):
                if lhgfy__oor not in gko__zznbl:
                    umw__etph = len(gko__zznbl)
                    gko__zznbl[lhgfy__oor] = umw__etph
                    puw__rwp[umw__etph] = lhgfy__oor
                fmjhl__zhxvj = gko__zznbl[lhgfy__oor]
                mlizb__yfkbz.append(fmjhl__zhxvj)
                gslg__fgzq.append(xxcyy__rfpp[fmjhl__zhxvj])
                xxcyy__rfpp[fmjhl__zhxvj] += 1
                vmaz__rrdy[fmjhl__zhxvj].append(i)
        self.block_nums = mlizb__yfkbz
        self.block_offsets = gslg__fgzq
        self.type_to_blk = gko__zznbl
        self.blk_to_type = puw__rwp
        self.block_to_arr_ind = vmaz__rrdy
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
            ztb__jvc = [(f'block_{i}', types.List(lhgfy__oor)) for i,
                lhgfy__oor in enumerate(fe_type.arr_types)]
        else:
            ztb__jvc = [(f'block_{fmjhl__zhxvj}', types.List(lhgfy__oor)) for
                lhgfy__oor, fmjhl__zhxvj in fe_type.type_to_blk.items()]
        ztb__jvc.append(('parent', types.pyobject))
        ztb__jvc.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, ztb__jvc)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    zon__xqa = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    qmae__icat = c.pyapi.make_none()
    mrjef__ubq = c.context.get_constant(types.int64, 0)
    enm__zfn = cgutils.alloca_once_value(c.builder, mrjef__ubq)
    for lhgfy__oor, fmjhl__zhxvj in typ.type_to_blk.items():
        ogl__ads = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[fmjhl__zhxvj]))
        qovvy__fshmt, efzb__irvb = ListInstance.allocate_ex(c.context, c.
            builder, types.List(lhgfy__oor), ogl__ads)
        efzb__irvb.size = ogl__ads
        vrnzg__fly = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            fmjhl__zhxvj], dtype=np.int64))
        ypdt__jdrg = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, vrnzg__fly)
        with cgutils.for_range(c.builder, ogl__ads) as mmdpm__ouc:
            i = mmdpm__ouc.index
            ughq__hhc = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), ypdt__jdrg, i)
            eqyil__sxyff = c.pyapi.long_from_longlong(ughq__hhc)
            ens__rnhb = c.pyapi.object_getitem(zon__xqa, eqyil__sxyff)
            kotn__mxcat = c.builder.icmp_unsigned('==', ens__rnhb, qmae__icat)
            with c.builder.if_else(kotn__mxcat) as (uemr__udqrn, iecp__gsow):
                with uemr__udqrn:
                    gbn__vbd = c.context.get_constant_null(lhgfy__oor)
                    efzb__irvb.inititem(i, gbn__vbd, incref=False)
                with iecp__gsow:
                    pwprb__tiutk = c.pyapi.call_method(ens__rnhb, '__len__', ()
                        )
                    rakf__vllb = c.pyapi.long_as_longlong(pwprb__tiutk)
                    c.builder.store(rakf__vllb, enm__zfn)
                    c.pyapi.decref(pwprb__tiutk)
                    arr = c.pyapi.to_native_value(lhgfy__oor, ens__rnhb).value
                    efzb__irvb.inititem(i, arr, incref=False)
            c.pyapi.decref(ens__rnhb)
            c.pyapi.decref(eqyil__sxyff)
        setattr(table, f'block_{fmjhl__zhxvj}', efzb__irvb.value)
    table.len = c.builder.load(enm__zfn)
    c.pyapi.decref(zon__xqa)
    c.pyapi.decref(qmae__icat)
    fucuf__clmy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=fucuf__clmy)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        del__qah = c.context.get_constant(types.int64, 0)
        for i, lhgfy__oor in enumerate(typ.arr_types):
            ckcjs__ggpdx = getattr(table, f'block_{i}')
            syv__kkyw = ListInstance(c.context, c.builder, types.List(
                lhgfy__oor), ckcjs__ggpdx)
            del__qah = c.builder.add(del__qah, syv__kkyw.size)
        dlxe__plilg = c.pyapi.list_new(del__qah)
        ejut__nqyt = c.context.get_constant(types.int64, 0)
        for i, lhgfy__oor in enumerate(typ.arr_types):
            ckcjs__ggpdx = getattr(table, f'block_{i}')
            syv__kkyw = ListInstance(c.context, c.builder, types.List(
                lhgfy__oor), ckcjs__ggpdx)
            with cgutils.for_range(c.builder, syv__kkyw.size) as mmdpm__ouc:
                i = mmdpm__ouc.index
                arr = syv__kkyw.getitem(i)
                c.context.nrt.incref(c.builder, lhgfy__oor, arr)
                idx = c.builder.add(ejut__nqyt, i)
                c.pyapi.list_setitem(dlxe__plilg, idx, c.pyapi.
                    from_native_value(lhgfy__oor, arr, c.env_manager))
            ejut__nqyt = c.builder.add(ejut__nqyt, syv__kkyw.size)
        xusgg__jotx = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        tff__wnn = c.pyapi.call_function_objargs(xusgg__jotx, (dlxe__plilg,))
        c.pyapi.decref(xusgg__jotx)
        c.pyapi.decref(dlxe__plilg)
        c.context.nrt.decref(c.builder, typ, val)
        return tff__wnn
    dlxe__plilg = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    wmup__uywa = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for lhgfy__oor, fmjhl__zhxvj in typ.type_to_blk.items():
        ckcjs__ggpdx = getattr(table, f'block_{fmjhl__zhxvj}')
        syv__kkyw = ListInstance(c.context, c.builder, types.List(
            lhgfy__oor), ckcjs__ggpdx)
        vrnzg__fly = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            fmjhl__zhxvj], dtype=np.int64))
        ypdt__jdrg = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, vrnzg__fly)
        with cgutils.for_range(c.builder, syv__kkyw.size) as mmdpm__ouc:
            i = mmdpm__ouc.index
            ughq__hhc = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), ypdt__jdrg, i)
            arr = syv__kkyw.getitem(i)
            bgg__ugs = cgutils.alloca_once_value(c.builder, arr)
            yyz__fnney = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(lhgfy__oor))
            is_null = is_ll_eq(c.builder, bgg__ugs, yyz__fnney)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (uemr__udqrn, iecp__gsow):
                with uemr__udqrn:
                    qmae__icat = c.pyapi.make_none()
                    c.pyapi.list_setitem(dlxe__plilg, ughq__hhc, qmae__icat)
                with iecp__gsow:
                    ens__rnhb = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, wmup__uywa)
                        ) as (suo__jdrln, xxkl__dgigq):
                        with suo__jdrln:
                            azjc__alc = get_df_obj_column_codegen(c.context,
                                c.builder, c.pyapi, table.parent, ughq__hhc,
                                lhgfy__oor)
                            c.builder.store(azjc__alc, ens__rnhb)
                        with xxkl__dgigq:
                            c.context.nrt.incref(c.builder, lhgfy__oor, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                lhgfy__oor, arr, c.env_manager), ens__rnhb)
                    c.pyapi.list_setitem(dlxe__plilg, ughq__hhc, c.builder.
                        load(ens__rnhb))
    xusgg__jotx = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    tff__wnn = c.pyapi.call_function_objargs(xusgg__jotx, (dlxe__plilg,))
    c.pyapi.decref(xusgg__jotx)
    c.pyapi.decref(dlxe__plilg)
    c.context.nrt.decref(c.builder, typ, val)
    return tff__wnn


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
        ssdwm__bcex = context.get_constant(types.int64, 0)
        for i, lhgfy__oor in enumerate(table_type.arr_types):
            ckcjs__ggpdx = getattr(table, f'block_{i}')
            syv__kkyw = ListInstance(context, builder, types.List(
                lhgfy__oor), ckcjs__ggpdx)
            ssdwm__bcex = builder.add(ssdwm__bcex, syv__kkyw.size)
        return ssdwm__bcex
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    fmjhl__zhxvj = table_type.block_nums[col_ind]
    kax__lvnb = table_type.block_offsets[col_ind]
    ckcjs__ggpdx = getattr(table, f'block_{fmjhl__zhxvj}')
    ids__yek = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    ybaix__kqd = context.get_constant(types.int64, col_ind)
    zqprn__mtz = context.get_constant(types.int64, kax__lvnb)
    lencf__nyrms = table_arg, ckcjs__ggpdx, zqprn__mtz, ybaix__kqd
    ensure_column_unboxed_codegen(context, builder, ids__yek, lencf__nyrms)
    syv__kkyw = ListInstance(context, builder, types.List(arr_type),
        ckcjs__ggpdx)
    arr = syv__kkyw.getitem(kax__lvnb)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, qovvy__fshmt = args
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
    xkxmt__qzzci = list(ind_typ.instance_type.meta)
    wuo__npf = defaultdict(list)
    for ind in xkxmt__qzzci:
        wuo__npf[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, qovvy__fshmt = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for fmjhl__zhxvj, mqly__ylyb in wuo__npf.items():
            arr_type = table_type.blk_to_type[fmjhl__zhxvj]
            ckcjs__ggpdx = getattr(table, f'block_{fmjhl__zhxvj}')
            syv__kkyw = ListInstance(context, builder, types.List(arr_type),
                ckcjs__ggpdx)
            gbn__vbd = context.get_constant_null(arr_type)
            if len(mqly__ylyb) == 1:
                kax__lvnb = mqly__ylyb[0]
                arr = syv__kkyw.getitem(kax__lvnb)
                context.nrt.decref(builder, arr_type, arr)
                syv__kkyw.inititem(kax__lvnb, gbn__vbd, incref=False)
            else:
                ogl__ads = context.get_constant(types.int64, len(mqly__ylyb))
                fxcw__rfsi = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(mqly__ylyb, dtype=
                    np.int64))
                feb__unynw = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, fxcw__rfsi)
                with cgutils.for_range(builder, ogl__ads) as mmdpm__ouc:
                    i = mmdpm__ouc.index
                    kax__lvnb = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        feb__unynw, i)
                    arr = syv__kkyw.getitem(kax__lvnb)
                    context.nrt.decref(builder, arr_type, arr)
                    syv__kkyw.inititem(kax__lvnb, gbn__vbd, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    mrjef__ubq = context.get_constant(types.int64, 0)
    zzva__kwzc = context.get_constant(types.int64, 1)
    majbs__senc = arr_type not in in_table_type.type_to_blk
    for lhgfy__oor, fmjhl__zhxvj in out_table_type.type_to_blk.items():
        if lhgfy__oor in in_table_type.type_to_blk:
            jhg__fci = in_table_type.type_to_blk[lhgfy__oor]
            efzb__irvb = ListInstance(context, builder, types.List(
                lhgfy__oor), getattr(in_table, f'block_{jhg__fci}'))
            context.nrt.incref(builder, types.List(lhgfy__oor), efzb__irvb.
                value)
            setattr(out_table, f'block_{fmjhl__zhxvj}', efzb__irvb.value)
    if majbs__senc:
        qovvy__fshmt, efzb__irvb = ListInstance.allocate_ex(context,
            builder, types.List(arr_type), zzva__kwzc)
        efzb__irvb.size = zzva__kwzc
        efzb__irvb.inititem(mrjef__ubq, arr_arg, incref=True)
        fmjhl__zhxvj = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{fmjhl__zhxvj}', efzb__irvb.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        fmjhl__zhxvj = out_table_type.type_to_blk[arr_type]
        efzb__irvb = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{fmjhl__zhxvj}'))
        if is_new_col:
            n = efzb__irvb.size
            itkfg__gya = builder.add(n, zzva__kwzc)
            efzb__irvb.resize(itkfg__gya)
            efzb__irvb.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            nxwbq__tqoaf = context.get_constant(types.int64, out_table_type
                .block_offsets[col_ind])
            efzb__irvb.setitem(nxwbq__tqoaf, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            nxwbq__tqoaf = context.get_constant(types.int64, out_table_type
                .block_offsets[col_ind])
            n = efzb__irvb.size
            itkfg__gya = builder.add(n, zzva__kwzc)
            efzb__irvb.resize(itkfg__gya)
            context.nrt.incref(builder, arr_type, efzb__irvb.getitem(
                nxwbq__tqoaf))
            efzb__irvb.move(builder.add(nxwbq__tqoaf, zzva__kwzc),
                nxwbq__tqoaf, builder.sub(n, nxwbq__tqoaf))
            efzb__irvb.setitem(nxwbq__tqoaf, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    nkln__lrq = in_table_type.arr_types[col_ind]
    if nkln__lrq in out_table_type.type_to_blk:
        fmjhl__zhxvj = out_table_type.type_to_blk[nkln__lrq]
        nsdje__hqjf = getattr(out_table, f'block_{fmjhl__zhxvj}')
        uxie__flot = types.List(nkln__lrq)
        nxwbq__tqoaf = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        oay__llch = uxie__flot.dtype(uxie__flot, types.intp)
        gmrck__szwj = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), oay__llch, (nsdje__hqjf, nxwbq__tqoaf))
        context.nrt.decref(builder, nkln__lrq, gmrck__szwj)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    fsdm__dxms = list(table.arr_types)
    if ind == len(fsdm__dxms):
        yhsjq__plx = None
        fsdm__dxms.append(arr_type)
    else:
        yhsjq__plx = table.arr_types[ind]
        fsdm__dxms[ind] = arr_type
    lqt__vep = TableType(tuple(fsdm__dxms))
    gfhf__rlr = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': lqt__vep}
    tjn__nueh = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    tjn__nueh += f'  T2 = init_table(out_table_typ, False)\n'
    tjn__nueh += f'  T2 = set_table_len(T2, len(table))\n'
    tjn__nueh += f'  T2 = set_table_parent(T2, table)\n'
    for typ, fmjhl__zhxvj in lqt__vep.type_to_blk.items():
        if typ in table.type_to_blk:
            bpbc__zzzh = table.type_to_blk[typ]
            tjn__nueh += (
                f'  arr_list_{fmjhl__zhxvj} = get_table_block(table, {bpbc__zzzh})\n'
                )
            tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj} = alloc_list_like(arr_list_{fmjhl__zhxvj}, {len(lqt__vep.block_to_arr_ind[fmjhl__zhxvj])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[bpbc__zzzh]
                ) & used_cols:
                tjn__nueh += (
                    f'  for i in range(len(arr_list_{fmjhl__zhxvj})):\n')
                if typ not in (yhsjq__plx, arr_type):
                    tjn__nueh += f"""    out_arr_list_{fmjhl__zhxvj}[i] = arr_list_{fmjhl__zhxvj}[i]
"""
                else:
                    khi__gnpt = table.block_to_arr_ind[bpbc__zzzh]
                    lkjfz__itfqy = np.empty(len(khi__gnpt), np.int64)
                    afn__cbh = False
                    for jcr__ghb, ughq__hhc in enumerate(khi__gnpt):
                        if ughq__hhc != ind:
                            wdayi__bnrk = lqt__vep.block_offsets[ughq__hhc]
                        else:
                            wdayi__bnrk = -1
                            afn__cbh = True
                        lkjfz__itfqy[jcr__ghb] = wdayi__bnrk
                    gfhf__rlr[f'out_idxs_{fmjhl__zhxvj}'] = np.array(
                        lkjfz__itfqy, np.int64)
                    tjn__nueh += f'    out_idx = out_idxs_{fmjhl__zhxvj}[i]\n'
                    if afn__cbh:
                        tjn__nueh += f'    if out_idx == -1:\n'
                        tjn__nueh += f'      continue\n'
                    tjn__nueh += f"""    out_arr_list_{fmjhl__zhxvj}[out_idx] = arr_list_{fmjhl__zhxvj}[i]
"""
            if typ == arr_type and not is_null:
                tjn__nueh += (
                    f'  out_arr_list_{fmjhl__zhxvj}[{lqt__vep.block_offsets[ind]}] = arr\n'
                    )
        else:
            gfhf__rlr[f'arr_list_typ_{fmjhl__zhxvj}'] = types.List(arr_type)
            tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj} = alloc_list_like(arr_list_typ_{fmjhl__zhxvj}, 1, False)
"""
            if not is_null:
                tjn__nueh += f'  out_arr_list_{fmjhl__zhxvj}[0] = arr\n'
        tjn__nueh += (
            f'  T2 = set_table_block(T2, out_arr_list_{fmjhl__zhxvj}, {fmjhl__zhxvj})\n'
            )
    tjn__nueh += f'  return T2\n'
    gpjoi__uqnc = {}
    exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
    return gpjoi__uqnc['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        rymb__ujaik = None
    else:
        rymb__ujaik = set(used_cols.instance_type.meta)
    dcoz__smcql = get_overload_const_int(ind)
    return generate_set_table_data_code(table, dcoz__smcql, arr, rymb__ujaik)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    dcoz__smcql = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        rymb__ujaik = None
    else:
        rymb__ujaik = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, dcoz__smcql, arr_type,
        rymb__ujaik, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    kesu__fdtqo = args[0]
    if equiv_set.has_shape(kesu__fdtqo):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            kesu__fdtqo)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    gdwai__ozhlq = []
    for lhgfy__oor, fmjhl__zhxvj in table_type.type_to_blk.items():
        yov__xwz = len(table_type.block_to_arr_ind[fmjhl__zhxvj])
        nzo__ohf = []
        for i in range(yov__xwz):
            ughq__hhc = table_type.block_to_arr_ind[fmjhl__zhxvj][i]
            nzo__ohf.append(pyval.arrays[ughq__hhc])
        gdwai__ozhlq.append(context.get_constant_generic(builder, types.
            List(lhgfy__oor), nzo__ohf))
    vuq__ciw = context.get_constant_null(types.pyobject)
    okf__wukkj = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(gdwai__ozhlq + [vuq__ciw, okf__wukkj])


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
        for lhgfy__oor, fmjhl__zhxvj in out_table_type.type_to_blk.items():
            uooe__wiiu = context.get_constant_null(types.List(lhgfy__oor))
            setattr(table, f'block_{fmjhl__zhxvj}', uooe__wiiu)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    ifm__zmea = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        ifm__zmea[typ.dtype] = i
    pzua__wlxt = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(pzua__wlxt, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        akpl__vygw, qovvy__fshmt = args
        table = cgutils.create_struct_proxy(pzua__wlxt)(context, builder)
        for lhgfy__oor, fmjhl__zhxvj in pzua__wlxt.type_to_blk.items():
            idx = ifm__zmea[lhgfy__oor]
            qcuq__agg = signature(types.List(lhgfy__oor),
                tuple_of_lists_type, types.literal(idx))
            ntjle__cazf = akpl__vygw, idx
            qqs__vjz = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, qcuq__agg, ntjle__cazf)
            setattr(table, f'block_{fmjhl__zhxvj}', qqs__vjz)
        return table._getvalue()
    sig = pzua__wlxt(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    fmjhl__zhxvj = get_overload_const_int(blk_type)
    arr_type = None
    for lhgfy__oor, gymrc__lkkf in table_type.type_to_blk.items():
        if gymrc__lkkf == fmjhl__zhxvj:
            arr_type = lhgfy__oor
            break
    assert arr_type is not None, 'invalid table type block'
    pilo__dnvv = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        ckcjs__ggpdx = getattr(table, f'block_{fmjhl__zhxvj}')
        return impl_ret_borrowed(context, builder, pilo__dnvv, ckcjs__ggpdx)
    sig = pilo__dnvv(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, guinr__eku = args
        opg__geswv = context.get_python_api(builder)
        rfgx__abl = used_cols_typ == types.none
        if not rfgx__abl:
            ism__pfya = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), guinr__eku)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for lhgfy__oor, fmjhl__zhxvj in table_type.type_to_blk.items():
            ogl__ads = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[fmjhl__zhxvj]))
            vrnzg__fly = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                fmjhl__zhxvj], dtype=np.int64))
            ypdt__jdrg = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, vrnzg__fly)
            ckcjs__ggpdx = getattr(table, f'block_{fmjhl__zhxvj}')
            with cgutils.for_range(builder, ogl__ads) as mmdpm__ouc:
                i = mmdpm__ouc.index
                ughq__hhc = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    ypdt__jdrg, i)
                ids__yek = types.none(table_type, types.List(lhgfy__oor),
                    types.int64, types.int64)
                lencf__nyrms = table_arg, ckcjs__ggpdx, i, ughq__hhc
                if rfgx__abl:
                    ensure_column_unboxed_codegen(context, builder,
                        ids__yek, lencf__nyrms)
                else:
                    bmbph__ycd = ism__pfya.contains(ughq__hhc)
                    with builder.if_then(bmbph__ycd):
                        ensure_column_unboxed_codegen(context, builder,
                            ids__yek, lencf__nyrms)
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
    table_arg, vkocp__kohe, dtyxb__cvy, iskce__grom = args
    opg__geswv = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    wmup__uywa = cgutils.is_not_null(builder, table.parent)
    syv__kkyw = ListInstance(context, builder, sig.args[1], vkocp__kohe)
    syu__uisrv = syv__kkyw.getitem(dtyxb__cvy)
    bgg__ugs = cgutils.alloca_once_value(builder, syu__uisrv)
    yyz__fnney = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, bgg__ugs, yyz__fnney)
    with builder.if_then(is_null):
        with builder.if_else(wmup__uywa) as (uemr__udqrn, iecp__gsow):
            with uemr__udqrn:
                ens__rnhb = get_df_obj_column_codegen(context, builder,
                    opg__geswv, table.parent, iskce__grom, sig.args[1].dtype)
                arr = opg__geswv.to_native_value(sig.args[1].dtype, ens__rnhb
                    ).value
                syv__kkyw.inititem(dtyxb__cvy, arr, incref=False)
                opg__geswv.decref(ens__rnhb)
            with iecp__gsow:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    fmjhl__zhxvj = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, vnws__wfq, qovvy__fshmt = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{fmjhl__zhxvj}', vnws__wfq)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, ophli__djn = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = ophli__djn
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        jqdci__ohm, qvl__mnk = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, qvl__mnk)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, jqdci__ohm)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    pilo__dnvv = list_type.instance_type if isinstance(list_type, types.TypeRef
        ) else list_type
    assert isinstance(pilo__dnvv, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        pilo__dnvv = types.List(to_str_arr_if_dict_array(pilo__dnvv.dtype))

    def codegen(context, builder, sig, args):
        ufew__bouu = args[1]
        qovvy__fshmt, efzb__irvb = ListInstance.allocate_ex(context,
            builder, pilo__dnvv, ufew__bouu)
        efzb__irvb.size = ufew__bouu
        return efzb__irvb.value
    sig = pilo__dnvv(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    rew__enfpt = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(rew__enfpt)

    def codegen(context, builder, sig, args):
        ufew__bouu, qovvy__fshmt = args
        qovvy__fshmt, efzb__irvb = ListInstance.allocate_ex(context,
            builder, list_type, ufew__bouu)
        efzb__irvb.size = ufew__bouu
        return efzb__irvb.value
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
        qmmv__ywt = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(qmmv__ywt)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    gfhf__rlr = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        piv__cpy = used_cols.instance_type
        wdu__itkrm = np.array(piv__cpy.meta, dtype=np.int64)
        gfhf__rlr['used_cols_vals'] = wdu__itkrm
        zpjyd__mvxor = set([T.block_nums[i] for i in wdu__itkrm])
    else:
        wdu__itkrm = None
    tjn__nueh = 'def table_filter_func(T, idx, used_cols=None):\n'
    tjn__nueh += f'  T2 = init_table(T, False)\n'
    tjn__nueh += f'  l = 0\n'
    if wdu__itkrm is not None and len(wdu__itkrm) == 0:
        tjn__nueh += f'  l = _get_idx_length(idx, len(T))\n'
        tjn__nueh += f'  T2 = set_table_len(T2, l)\n'
        tjn__nueh += f'  return T2\n'
        gpjoi__uqnc = {}
        exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
        return gpjoi__uqnc['table_filter_func']
    if wdu__itkrm is not None:
        tjn__nueh += f'  used_set = set(used_cols_vals)\n'
    for fmjhl__zhxvj in T.type_to_blk.values():
        tjn__nueh += (
            f'  arr_list_{fmjhl__zhxvj} = get_table_block(T, {fmjhl__zhxvj})\n'
            )
        tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj} = alloc_list_like(arr_list_{fmjhl__zhxvj}, len(arr_list_{fmjhl__zhxvj}), False)
"""
        if wdu__itkrm is None or fmjhl__zhxvj in zpjyd__mvxor:
            gfhf__rlr[f'arr_inds_{fmjhl__zhxvj}'] = np.array(T.
                block_to_arr_ind[fmjhl__zhxvj], dtype=np.int64)
            tjn__nueh += f'  for i in range(len(arr_list_{fmjhl__zhxvj})):\n'
            tjn__nueh += (
                f'    arr_ind_{fmjhl__zhxvj} = arr_inds_{fmjhl__zhxvj}[i]\n')
            if wdu__itkrm is not None:
                tjn__nueh += (
                    f'    if arr_ind_{fmjhl__zhxvj} not in used_set: continue\n'
                    )
            tjn__nueh += f"""    ensure_column_unboxed(T, arr_list_{fmjhl__zhxvj}, i, arr_ind_{fmjhl__zhxvj})
"""
            tjn__nueh += f"""    out_arr_{fmjhl__zhxvj} = ensure_contig_if_np(arr_list_{fmjhl__zhxvj}[i][idx])
"""
            tjn__nueh += f'    l = len(out_arr_{fmjhl__zhxvj})\n'
            tjn__nueh += (
                f'    out_arr_list_{fmjhl__zhxvj}[i] = out_arr_{fmjhl__zhxvj}\n'
                )
        tjn__nueh += (
            f'  T2 = set_table_block(T2, out_arr_list_{fmjhl__zhxvj}, {fmjhl__zhxvj})\n'
            )
    tjn__nueh += f'  T2 = set_table_len(T2, l)\n'
    tjn__nueh += f'  return T2\n'
    gpjoi__uqnc = {}
    exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
    return gpjoi__uqnc['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    oymni__yzuow = list(idx.instance_type.meta)
    fsdm__dxms = tuple(np.array(T.arr_types, dtype=object)[oymni__yzuow])
    lqt__vep = TableType(fsdm__dxms)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    swa__rtlk = is_overload_true(copy_arrs)
    gfhf__rlr = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': lqt__vep}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        btoc__xur = set(kept_cols)
        gfhf__rlr['kept_cols'] = np.array(kept_cols, np.int64)
        bplrk__jhuy = True
    else:
        bplrk__jhuy = False
    aurs__gumlk = {i: c for i, c in enumerate(oymni__yzuow)}
    tjn__nueh = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    tjn__nueh += f'  T2 = init_table(out_table_typ, False)\n'
    tjn__nueh += f'  T2 = set_table_len(T2, len(T))\n'
    if bplrk__jhuy and len(btoc__xur) == 0:
        tjn__nueh += f'  return T2\n'
        gpjoi__uqnc = {}
        exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
        return gpjoi__uqnc['table_subset']
    if bplrk__jhuy:
        tjn__nueh += f'  kept_cols_set = set(kept_cols)\n'
    for typ, fmjhl__zhxvj in lqt__vep.type_to_blk.items():
        bpbc__zzzh = T.type_to_blk[typ]
        tjn__nueh += (
            f'  arr_list_{fmjhl__zhxvj} = get_table_block(T, {bpbc__zzzh})\n')
        tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj} = alloc_list_like(arr_list_{fmjhl__zhxvj}, {len(lqt__vep.block_to_arr_ind[fmjhl__zhxvj])}, False)
"""
        avc__myrz = True
        if bplrk__jhuy:
            meagw__izm = set(lqt__vep.block_to_arr_ind[fmjhl__zhxvj])
            ret__siga = meagw__izm & btoc__xur
            avc__myrz = len(ret__siga) > 0
        if avc__myrz:
            gfhf__rlr[f'out_arr_inds_{fmjhl__zhxvj}'] = np.array(lqt__vep.
                block_to_arr_ind[fmjhl__zhxvj], dtype=np.int64)
            tjn__nueh += (
                f'  for i in range(len(out_arr_list_{fmjhl__zhxvj})):\n')
            tjn__nueh += (
                f'    out_arr_ind_{fmjhl__zhxvj} = out_arr_inds_{fmjhl__zhxvj}[i]\n'
                )
            if bplrk__jhuy:
                tjn__nueh += (
                    f'    if out_arr_ind_{fmjhl__zhxvj} not in kept_cols_set: continue\n'
                    )
            wiu__ffyg = []
            kgcz__old = []
            for xvxz__ozyxp in lqt__vep.block_to_arr_ind[fmjhl__zhxvj]:
                neige__ipl = aurs__gumlk[xvxz__ozyxp]
                wiu__ffyg.append(neige__ipl)
                xywmn__ljp = T.block_offsets[neige__ipl]
                kgcz__old.append(xywmn__ljp)
            gfhf__rlr[f'in_logical_idx_{fmjhl__zhxvj}'] = np.array(wiu__ffyg,
                dtype=np.int64)
            gfhf__rlr[f'in_physical_idx_{fmjhl__zhxvj}'] = np.array(kgcz__old,
                dtype=np.int64)
            tjn__nueh += (
                f'    logical_idx_{fmjhl__zhxvj} = in_logical_idx_{fmjhl__zhxvj}[i]\n'
                )
            tjn__nueh += (
                f'    physical_idx_{fmjhl__zhxvj} = in_physical_idx_{fmjhl__zhxvj}[i]\n'
                )
            tjn__nueh += f"""    ensure_column_unboxed(T, arr_list_{fmjhl__zhxvj}, physical_idx_{fmjhl__zhxvj}, logical_idx_{fmjhl__zhxvj})
"""
            zntol__yrfc = '.copy()' if swa__rtlk else ''
            tjn__nueh += f"""    out_arr_list_{fmjhl__zhxvj}[i] = arr_list_{fmjhl__zhxvj}[physical_idx_{fmjhl__zhxvj}]{zntol__yrfc}
"""
        tjn__nueh += (
            f'  T2 = set_table_block(T2, out_arr_list_{fmjhl__zhxvj}, {fmjhl__zhxvj})\n'
            )
    tjn__nueh += f'  return T2\n'
    gpjoi__uqnc = {}
    exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
    return gpjoi__uqnc['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    kesu__fdtqo = args[0]
    if equiv_set.has_shape(kesu__fdtqo):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=kesu__fdtqo, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (kesu__fdtqo)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    kesu__fdtqo = args[0]
    if equiv_set.has_shape(kesu__fdtqo):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            kesu__fdtqo)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    tjn__nueh = 'def impl(T):\n'
    tjn__nueh += f'  T2 = init_table(T, True)\n'
    tjn__nueh += f'  l = len(T)\n'
    gfhf__rlr = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for fmjhl__zhxvj in T.type_to_blk.values():
        gfhf__rlr[f'arr_inds_{fmjhl__zhxvj}'] = np.array(T.block_to_arr_ind
            [fmjhl__zhxvj], dtype=np.int64)
        tjn__nueh += (
            f'  arr_list_{fmjhl__zhxvj} = get_table_block(T, {fmjhl__zhxvj})\n'
            )
        tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj} = alloc_list_like(arr_list_{fmjhl__zhxvj}, len(arr_list_{fmjhl__zhxvj}), True)
"""
        tjn__nueh += f'  for i in range(len(arr_list_{fmjhl__zhxvj})):\n'
        tjn__nueh += (
            f'    arr_ind_{fmjhl__zhxvj} = arr_inds_{fmjhl__zhxvj}[i]\n')
        tjn__nueh += f"""    ensure_column_unboxed(T, arr_list_{fmjhl__zhxvj}, i, arr_ind_{fmjhl__zhxvj})
"""
        tjn__nueh += f"""    out_arr_{fmjhl__zhxvj} = decode_if_dict_array(arr_list_{fmjhl__zhxvj}[i])
"""
        tjn__nueh += (
            f'    out_arr_list_{fmjhl__zhxvj}[i] = out_arr_{fmjhl__zhxvj}\n')
        tjn__nueh += (
            f'  T2 = set_table_block(T2, out_arr_list_{fmjhl__zhxvj}, {fmjhl__zhxvj})\n'
            )
    tjn__nueh += f'  T2 = set_table_len(T2, l)\n'
    tjn__nueh += f'  return T2\n'
    gpjoi__uqnc = {}
    exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
    return gpjoi__uqnc['impl']


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
        olk__eunb = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        olk__eunb = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            olk__eunb.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        fjaf__ltkod, dfb__dfgvc = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = dfb__dfgvc
        gdwai__ozhlq = cgutils.unpack_tuple(builder, fjaf__ltkod)
        for i, ckcjs__ggpdx in enumerate(gdwai__ozhlq):
            setattr(table, f'block_{i}', ckcjs__ggpdx)
            context.nrt.incref(builder, types.List(olk__eunb[i]), ckcjs__ggpdx)
        return table._getvalue()
    table_type = TableType(tuple(olk__eunb), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    gfhf__rlr = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        gfhf__rlr['kept_cols'] = np.array(list(kept_cols), np.int64)
        bplrk__jhuy = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        bplrk__jhuy = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    hyo__rhw = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        hyo__rhw else extra_arrs_t.types[i - hyo__rhw] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    tjn__nueh = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    tjn__nueh += f'  T1 = in_table_t\n'
    tjn__nueh += f'  T2 = init_table(out_table_type, False)\n'
    tjn__nueh += f'  T2 = set_table_len(T2, len(T1))\n'
    if bplrk__jhuy and len(kept_cols) == 0:
        tjn__nueh += f'  return T2\n'
        gpjoi__uqnc = {}
        exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
        return gpjoi__uqnc['impl']
    if bplrk__jhuy:
        tjn__nueh += f'  kept_cols_set = set(kept_cols)\n'
    for typ, fmjhl__zhxvj in out_table_type.type_to_blk.items():
        gfhf__rlr[f'arr_list_typ_{fmjhl__zhxvj}'] = types.List(typ)
        ogl__ads = len(out_table_type.block_to_arr_ind[fmjhl__zhxvj])
        tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj} = alloc_list_like(arr_list_typ_{fmjhl__zhxvj}, {ogl__ads}, False)
"""
        if typ in in_table_t.type_to_blk:
            jvdey__bvd = in_table_t.type_to_blk[typ]
            ugboi__xhs = []
            zcf__jae = []
            for ihokg__yrd in out_table_type.block_to_arr_ind[fmjhl__zhxvj]:
                cigg__ocs = in_col_inds[ihokg__yrd]
                if cigg__ocs < hyo__rhw:
                    ugboi__xhs.append(in_table_t.block_offsets[cigg__ocs])
                    zcf__jae.append(cigg__ocs)
                else:
                    ugboi__xhs.append(-1)
                    zcf__jae.append(-1)
            gfhf__rlr[f'in_idxs_{fmjhl__zhxvj}'] = np.array(ugboi__xhs, np.
                int64)
            gfhf__rlr[f'in_arr_inds_{fmjhl__zhxvj}'] = np.array(zcf__jae,
                np.int64)
            if bplrk__jhuy:
                gfhf__rlr[f'out_arr_inds_{fmjhl__zhxvj}'] = np.array(
                    out_table_type.block_to_arr_ind[fmjhl__zhxvj], dtype=np
                    .int64)
            tjn__nueh += (
                f'  in_arr_list_{fmjhl__zhxvj} = get_table_block(T1, {jvdey__bvd})\n'
                )
            tjn__nueh += (
                f'  for i in range(len(out_arr_list_{fmjhl__zhxvj})):\n')
            tjn__nueh += (
                f'    in_offset_{fmjhl__zhxvj} = in_idxs_{fmjhl__zhxvj}[i]\n')
            tjn__nueh += f'    if in_offset_{fmjhl__zhxvj} == -1:\n'
            tjn__nueh += f'      continue\n'
            tjn__nueh += (
                f'    in_arr_ind_{fmjhl__zhxvj} = in_arr_inds_{fmjhl__zhxvj}[i]\n'
                )
            if bplrk__jhuy:
                tjn__nueh += f"""    if out_arr_inds_{fmjhl__zhxvj}[i] not in kept_cols_set: continue
"""
            tjn__nueh += f"""    ensure_column_unboxed(T1, in_arr_list_{fmjhl__zhxvj}, in_offset_{fmjhl__zhxvj}, in_arr_ind_{fmjhl__zhxvj})
"""
            tjn__nueh += f"""    out_arr_list_{fmjhl__zhxvj}[i] = in_arr_list_{fmjhl__zhxvj}[in_offset_{fmjhl__zhxvj}]
"""
        for i, ihokg__yrd in enumerate(out_table_type.block_to_arr_ind[
            fmjhl__zhxvj]):
            if ihokg__yrd not in kept_cols:
                continue
            cigg__ocs = in_col_inds[ihokg__yrd]
            if cigg__ocs >= hyo__rhw:
                tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj}[{i}] = extra_arrs_t[{cigg__ocs - hyo__rhw}]
"""
        tjn__nueh += (
            f'  T2 = set_table_block(T2, out_arr_list_{fmjhl__zhxvj}, {fmjhl__zhxvj})\n'
            )
    tjn__nueh += f'  return T2\n'
    gfhf__rlr.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    gpjoi__uqnc = {}
    exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
    return gpjoi__uqnc['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    hyo__rhw = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < hyo__rhw else
        extra_arrs_t.types[i - hyo__rhw] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    vuf__jdyhu = None
    if not is_overload_none(in_table_t):
        for i, lhgfy__oor in enumerate(in_table_t.types):
            if lhgfy__oor != types.none:
                vuf__jdyhu = f'in_table_t[{i}]'
                break
    if vuf__jdyhu is None:
        for i, lhgfy__oor in enumerate(extra_arrs_t.types):
            if lhgfy__oor != types.none:
                vuf__jdyhu = f'extra_arrs_t[{i}]'
                break
    assert vuf__jdyhu is not None, 'no array found in input data'
    tjn__nueh = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    tjn__nueh += f'  T1 = in_table_t\n'
    tjn__nueh += f'  T2 = init_table(out_table_type, False)\n'
    tjn__nueh += f'  T2 = set_table_len(T2, len({vuf__jdyhu}))\n'
    gfhf__rlr = {}
    for typ, fmjhl__zhxvj in out_table_type.type_to_blk.items():
        gfhf__rlr[f'arr_list_typ_{fmjhl__zhxvj}'] = types.List(typ)
        ogl__ads = len(out_table_type.block_to_arr_ind[fmjhl__zhxvj])
        tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj} = alloc_list_like(arr_list_typ_{fmjhl__zhxvj}, {ogl__ads}, False)
"""
        for i, ihokg__yrd in enumerate(out_table_type.block_to_arr_ind[
            fmjhl__zhxvj]):
            if ihokg__yrd not in kept_cols:
                continue
            cigg__ocs = in_col_inds[ihokg__yrd]
            if cigg__ocs < hyo__rhw:
                tjn__nueh += (
                    f'  out_arr_list_{fmjhl__zhxvj}[{i}] = T1[{cigg__ocs}]\n')
            else:
                tjn__nueh += f"""  out_arr_list_{fmjhl__zhxvj}[{i}] = extra_arrs_t[{cigg__ocs - hyo__rhw}]
"""
        tjn__nueh += (
            f'  T2 = set_table_block(T2, out_arr_list_{fmjhl__zhxvj}, {fmjhl__zhxvj})\n'
            )
    tjn__nueh += f'  return T2\n'
    gfhf__rlr.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    gpjoi__uqnc = {}
    exec(tjn__nueh, gfhf__rlr, gpjoi__uqnc)
    return gpjoi__uqnc['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    yyod__eyz = args[0]
    egqi__cot = args[1]
    if equiv_set.has_shape(yyod__eyz):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            yyod__eyz)[0], None), pre=[])
    if equiv_set.has_shape(egqi__cot):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            egqi__cot)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
