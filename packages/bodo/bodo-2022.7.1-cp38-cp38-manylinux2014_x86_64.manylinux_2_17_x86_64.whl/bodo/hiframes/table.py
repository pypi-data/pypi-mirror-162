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
            mcrs__fbhy = 0
            xuh__ohjao = []
            for i in range(usecols[-1] + 1):
                if i == usecols[mcrs__fbhy]:
                    xuh__ohjao.append(arrs[mcrs__fbhy])
                    mcrs__fbhy += 1
                else:
                    xuh__ohjao.append(None)
            for pgnd__wjq in range(usecols[-1] + 1, num_arrs):
                xuh__ohjao.append(None)
            self.arrays = xuh__ohjao
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((ykiwx__qrzg == mvd__tcm).all() for ykiwx__qrzg,
            mvd__tcm in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        rpes__wqio = len(self.arrays)
        zugr__cdw = dict(zip(range(rpes__wqio), self.arrays))
        df = pd.DataFrame(zugr__cdw, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        qtkpf__oye = []
        bfv__uiyf = []
        vkbcg__orasi = {}
        oqmqj__txg = {}
        guw__iuxcp = defaultdict(int)
        aja__thhp = defaultdict(list)
        if not has_runtime_cols:
            for i, jmk__qmndo in enumerate(arr_types):
                if jmk__qmndo not in vkbcg__orasi:
                    mmz__nah = len(vkbcg__orasi)
                    vkbcg__orasi[jmk__qmndo] = mmz__nah
                    oqmqj__txg[mmz__nah] = jmk__qmndo
                qrv__qhbav = vkbcg__orasi[jmk__qmndo]
                qtkpf__oye.append(qrv__qhbav)
                bfv__uiyf.append(guw__iuxcp[qrv__qhbav])
                guw__iuxcp[qrv__qhbav] += 1
                aja__thhp[qrv__qhbav].append(i)
        self.block_nums = qtkpf__oye
        self.block_offsets = bfv__uiyf
        self.type_to_blk = vkbcg__orasi
        self.blk_to_type = oqmqj__txg
        self.block_to_arr_ind = aja__thhp
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
            lymib__hsb = [(f'block_{i}', types.List(jmk__qmndo)) for i,
                jmk__qmndo in enumerate(fe_type.arr_types)]
        else:
            lymib__hsb = [(f'block_{qrv__qhbav}', types.List(jmk__qmndo)) for
                jmk__qmndo, qrv__qhbav in fe_type.type_to_blk.items()]
        lymib__hsb.append(('parent', types.pyobject))
        lymib__hsb.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, lymib__hsb)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    lzcn__ctdrv = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    jioy__ytgz = c.pyapi.make_none()
    evgsu__ncn = c.context.get_constant(types.int64, 0)
    xdfy__ooxsg = cgutils.alloca_once_value(c.builder, evgsu__ncn)
    for jmk__qmndo, qrv__qhbav in typ.type_to_blk.items():
        hdovd__iklt = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[qrv__qhbav]))
        pgnd__wjq, cany__ngvz = ListInstance.allocate_ex(c.context, c.
            builder, types.List(jmk__qmndo), hdovd__iklt)
        cany__ngvz.size = hdovd__iklt
        orpxx__byh = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[qrv__qhbav],
            dtype=np.int64))
        fibi__xtif = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, orpxx__byh)
        with cgutils.for_range(c.builder, hdovd__iklt) as jmdb__xkg:
            i = jmdb__xkg.index
            blg__boq = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), fibi__xtif, i)
            sudc__vknhl = c.pyapi.long_from_longlong(blg__boq)
            ugg__joty = c.pyapi.object_getitem(lzcn__ctdrv, sudc__vknhl)
            dfy__hfhut = c.builder.icmp_unsigned('==', ugg__joty, jioy__ytgz)
            with c.builder.if_else(dfy__hfhut) as (jaygk__cofl, tsr__oqto):
                with jaygk__cofl:
                    glmm__fdmry = c.context.get_constant_null(jmk__qmndo)
                    cany__ngvz.inititem(i, glmm__fdmry, incref=False)
                with tsr__oqto:
                    cmsd__vwsl = c.pyapi.call_method(ugg__joty, '__len__', ())
                    bql__xexy = c.pyapi.long_as_longlong(cmsd__vwsl)
                    c.builder.store(bql__xexy, xdfy__ooxsg)
                    c.pyapi.decref(cmsd__vwsl)
                    arr = c.pyapi.to_native_value(jmk__qmndo, ugg__joty).value
                    cany__ngvz.inititem(i, arr, incref=False)
            c.pyapi.decref(ugg__joty)
            c.pyapi.decref(sudc__vknhl)
        setattr(table, f'block_{qrv__qhbav}', cany__ngvz.value)
    table.len = c.builder.load(xdfy__ooxsg)
    c.pyapi.decref(lzcn__ctdrv)
    c.pyapi.decref(jioy__ytgz)
    gzyvn__qcgvx = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=gzyvn__qcgvx)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        kyahd__epm = c.context.get_constant(types.int64, 0)
        for i, jmk__qmndo in enumerate(typ.arr_types):
            xuh__ohjao = getattr(table, f'block_{i}')
            gwe__lgr = ListInstance(c.context, c.builder, types.List(
                jmk__qmndo), xuh__ohjao)
            kyahd__epm = c.builder.add(kyahd__epm, gwe__lgr.size)
        xamqb__gkzcp = c.pyapi.list_new(kyahd__epm)
        jtj__tvz = c.context.get_constant(types.int64, 0)
        for i, jmk__qmndo in enumerate(typ.arr_types):
            xuh__ohjao = getattr(table, f'block_{i}')
            gwe__lgr = ListInstance(c.context, c.builder, types.List(
                jmk__qmndo), xuh__ohjao)
            with cgutils.for_range(c.builder, gwe__lgr.size) as jmdb__xkg:
                i = jmdb__xkg.index
                arr = gwe__lgr.getitem(i)
                c.context.nrt.incref(c.builder, jmk__qmndo, arr)
                idx = c.builder.add(jtj__tvz, i)
                c.pyapi.list_setitem(xamqb__gkzcp, idx, c.pyapi.
                    from_native_value(jmk__qmndo, arr, c.env_manager))
            jtj__tvz = c.builder.add(jtj__tvz, gwe__lgr.size)
        lmpr__mscn = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        xhnq__pbyh = c.pyapi.call_function_objargs(lmpr__mscn, (xamqb__gkzcp,))
        c.pyapi.decref(lmpr__mscn)
        c.pyapi.decref(xamqb__gkzcp)
        c.context.nrt.decref(c.builder, typ, val)
        return xhnq__pbyh
    xamqb__gkzcp = c.pyapi.list_new(c.context.get_constant(types.int64, len
        (typ.arr_types)))
    ijhlj__jcu = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for jmk__qmndo, qrv__qhbav in typ.type_to_blk.items():
        xuh__ohjao = getattr(table, f'block_{qrv__qhbav}')
        gwe__lgr = ListInstance(c.context, c.builder, types.List(jmk__qmndo
            ), xuh__ohjao)
        orpxx__byh = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[qrv__qhbav],
            dtype=np.int64))
        fibi__xtif = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, orpxx__byh)
        with cgutils.for_range(c.builder, gwe__lgr.size) as jmdb__xkg:
            i = jmdb__xkg.index
            blg__boq = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), fibi__xtif, i)
            arr = gwe__lgr.getitem(i)
            lzpl__yzqds = cgutils.alloca_once_value(c.builder, arr)
            nwt__uaa = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(jmk__qmndo))
            is_null = is_ll_eq(c.builder, lzpl__yzqds, nwt__uaa)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (jaygk__cofl, tsr__oqto):
                with jaygk__cofl:
                    jioy__ytgz = c.pyapi.make_none()
                    c.pyapi.list_setitem(xamqb__gkzcp, blg__boq, jioy__ytgz)
                with tsr__oqto:
                    ugg__joty = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, ijhlj__jcu)
                        ) as (khhkp__ujptg, volg__nhx):
                        with khhkp__ujptg:
                            xjtri__qhvok = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                blg__boq, jmk__qmndo)
                            c.builder.store(xjtri__qhvok, ugg__joty)
                        with volg__nhx:
                            c.context.nrt.incref(c.builder, jmk__qmndo, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                jmk__qmndo, arr, c.env_manager), ugg__joty)
                    c.pyapi.list_setitem(xamqb__gkzcp, blg__boq, c.builder.
                        load(ugg__joty))
    lmpr__mscn = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    xhnq__pbyh = c.pyapi.call_function_objargs(lmpr__mscn, (xamqb__gkzcp,))
    c.pyapi.decref(lmpr__mscn)
    c.pyapi.decref(xamqb__gkzcp)
    c.context.nrt.decref(c.builder, typ, val)
    return xhnq__pbyh


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
        eqvd__rpgej = context.get_constant(types.int64, 0)
        for i, jmk__qmndo in enumerate(table_type.arr_types):
            xuh__ohjao = getattr(table, f'block_{i}')
            gwe__lgr = ListInstance(context, builder, types.List(jmk__qmndo
                ), xuh__ohjao)
            eqvd__rpgej = builder.add(eqvd__rpgej, gwe__lgr.size)
        return eqvd__rpgej
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    qrv__qhbav = table_type.block_nums[col_ind]
    qag__rps = table_type.block_offsets[col_ind]
    xuh__ohjao = getattr(table, f'block_{qrv__qhbav}')
    nybl__qfgmw = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    zgb__yrsa = context.get_constant(types.int64, col_ind)
    fnaol__bkdl = context.get_constant(types.int64, qag__rps)
    qmn__ggp = table_arg, xuh__ohjao, fnaol__bkdl, zgb__yrsa
    ensure_column_unboxed_codegen(context, builder, nybl__qfgmw, qmn__ggp)
    gwe__lgr = ListInstance(context, builder, types.List(arr_type), xuh__ohjao)
    arr = gwe__lgr.getitem(qag__rps)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, pgnd__wjq = args
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
    gobx__ios = list(ind_typ.instance_type.meta)
    goyvl__shafc = defaultdict(list)
    for ind in gobx__ios:
        goyvl__shafc[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, pgnd__wjq = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for qrv__qhbav, qxnkk__qfhoy in goyvl__shafc.items():
            arr_type = table_type.blk_to_type[qrv__qhbav]
            xuh__ohjao = getattr(table, f'block_{qrv__qhbav}')
            gwe__lgr = ListInstance(context, builder, types.List(arr_type),
                xuh__ohjao)
            glmm__fdmry = context.get_constant_null(arr_type)
            if len(qxnkk__qfhoy) == 1:
                qag__rps = qxnkk__qfhoy[0]
                arr = gwe__lgr.getitem(qag__rps)
                context.nrt.decref(builder, arr_type, arr)
                gwe__lgr.inititem(qag__rps, glmm__fdmry, incref=False)
            else:
                hdovd__iklt = context.get_constant(types.int64, len(
                    qxnkk__qfhoy))
                ggs__owmev = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(qxnkk__qfhoy,
                    dtype=np.int64))
                bnww__aolwb = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, ggs__owmev)
                with cgutils.for_range(builder, hdovd__iklt) as jmdb__xkg:
                    i = jmdb__xkg.index
                    qag__rps = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        bnww__aolwb, i)
                    arr = gwe__lgr.getitem(qag__rps)
                    context.nrt.decref(builder, arr_type, arr)
                    gwe__lgr.inititem(qag__rps, glmm__fdmry, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    evgsu__ncn = context.get_constant(types.int64, 0)
    gxcwz__kvfw = context.get_constant(types.int64, 1)
    bhayc__vhuc = arr_type not in in_table_type.type_to_blk
    for jmk__qmndo, qrv__qhbav in out_table_type.type_to_blk.items():
        if jmk__qmndo in in_table_type.type_to_blk:
            uhcq__vglp = in_table_type.type_to_blk[jmk__qmndo]
            cany__ngvz = ListInstance(context, builder, types.List(
                jmk__qmndo), getattr(in_table, f'block_{uhcq__vglp}'))
            context.nrt.incref(builder, types.List(jmk__qmndo), cany__ngvz.
                value)
            setattr(out_table, f'block_{qrv__qhbav}', cany__ngvz.value)
    if bhayc__vhuc:
        pgnd__wjq, cany__ngvz = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), gxcwz__kvfw)
        cany__ngvz.size = gxcwz__kvfw
        cany__ngvz.inititem(evgsu__ncn, arr_arg, incref=True)
        qrv__qhbav = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{qrv__qhbav}', cany__ngvz.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        qrv__qhbav = out_table_type.type_to_blk[arr_type]
        cany__ngvz = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{qrv__qhbav}'))
        if is_new_col:
            n = cany__ngvz.size
            oenr__wqb = builder.add(n, gxcwz__kvfw)
            cany__ngvz.resize(oenr__wqb)
            cany__ngvz.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            alj__xqb = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            cany__ngvz.setitem(alj__xqb, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            alj__xqb = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = cany__ngvz.size
            oenr__wqb = builder.add(n, gxcwz__kvfw)
            cany__ngvz.resize(oenr__wqb)
            context.nrt.incref(builder, arr_type, cany__ngvz.getitem(alj__xqb))
            cany__ngvz.move(builder.add(alj__xqb, gxcwz__kvfw), alj__xqb,
                builder.sub(n, alj__xqb))
            cany__ngvz.setitem(alj__xqb, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    pwxo__zjpxe = in_table_type.arr_types[col_ind]
    if pwxo__zjpxe in out_table_type.type_to_blk:
        qrv__qhbav = out_table_type.type_to_blk[pwxo__zjpxe]
        xbd__msvoq = getattr(out_table, f'block_{qrv__qhbav}')
        ruodg__unc = types.List(pwxo__zjpxe)
        alj__xqb = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        amkt__rpaa = ruodg__unc.dtype(ruodg__unc, types.intp)
        ebcru__ied = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), amkt__rpaa, (xbd__msvoq, alj__xqb))
        context.nrt.decref(builder, pwxo__zjpxe, ebcru__ied)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    disp__szi = list(table.arr_types)
    if ind == len(disp__szi):
        dkz__dretz = None
        disp__szi.append(arr_type)
    else:
        dkz__dretz = table.arr_types[ind]
        disp__szi[ind] = arr_type
    qflz__hdjv = TableType(tuple(disp__szi))
    yhjsr__kckj = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': qflz__hdjv}
    eaz__wpsa = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    eaz__wpsa += f'  T2 = init_table(out_table_typ, False)\n'
    eaz__wpsa += f'  T2 = set_table_len(T2, len(table))\n'
    eaz__wpsa += f'  T2 = set_table_parent(T2, table)\n'
    for typ, qrv__qhbav in qflz__hdjv.type_to_blk.items():
        if typ in table.type_to_blk:
            swzbp__krnl = table.type_to_blk[typ]
            eaz__wpsa += (
                f'  arr_list_{qrv__qhbav} = get_table_block(table, {swzbp__krnl})\n'
                )
            eaz__wpsa += f"""  out_arr_list_{qrv__qhbav} = alloc_list_like(arr_list_{qrv__qhbav}, {len(qflz__hdjv.block_to_arr_ind[qrv__qhbav])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[swzbp__krnl]
                ) & used_cols:
                eaz__wpsa += f'  for i in range(len(arr_list_{qrv__qhbav})):\n'
                if typ not in (dkz__dretz, arr_type):
                    eaz__wpsa += (
                        f'    out_arr_list_{qrv__qhbav}[i] = arr_list_{qrv__qhbav}[i]\n'
                        )
                else:
                    hdgac__cpp = table.block_to_arr_ind[swzbp__krnl]
                    seie__znca = np.empty(len(hdgac__cpp), np.int64)
                    dwr__joha = False
                    for pwto__sipa, blg__boq in enumerate(hdgac__cpp):
                        if blg__boq != ind:
                            zeppc__adcz = qflz__hdjv.block_offsets[blg__boq]
                        else:
                            zeppc__adcz = -1
                            dwr__joha = True
                        seie__znca[pwto__sipa] = zeppc__adcz
                    yhjsr__kckj[f'out_idxs_{qrv__qhbav}'] = np.array(seie__znca
                        , np.int64)
                    eaz__wpsa += f'    out_idx = out_idxs_{qrv__qhbav}[i]\n'
                    if dwr__joha:
                        eaz__wpsa += f'    if out_idx == -1:\n'
                        eaz__wpsa += f'      continue\n'
                    eaz__wpsa += f"""    out_arr_list_{qrv__qhbav}[out_idx] = arr_list_{qrv__qhbav}[i]
"""
            if typ == arr_type and not is_null:
                eaz__wpsa += (
                    f'  out_arr_list_{qrv__qhbav}[{qflz__hdjv.block_offsets[ind]}] = arr\n'
                    )
        else:
            yhjsr__kckj[f'arr_list_typ_{qrv__qhbav}'] = types.List(arr_type)
            eaz__wpsa += f"""  out_arr_list_{qrv__qhbav} = alloc_list_like(arr_list_typ_{qrv__qhbav}, 1, False)
"""
            if not is_null:
                eaz__wpsa += f'  out_arr_list_{qrv__qhbav}[0] = arr\n'
        eaz__wpsa += (
            f'  T2 = set_table_block(T2, out_arr_list_{qrv__qhbav}, {qrv__qhbav})\n'
            )
    eaz__wpsa += f'  return T2\n'
    tcdf__jete = {}
    exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
    return tcdf__jete['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        fanhy__ehq = None
    else:
        fanhy__ehq = set(used_cols.instance_type.meta)
    gzv__int = get_overload_const_int(ind)
    return generate_set_table_data_code(table, gzv__int, arr, fanhy__ehq)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    gzv__int = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        fanhy__ehq = None
    else:
        fanhy__ehq = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, gzv__int, arr_type,
        fanhy__ehq, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    dodg__ocr = args[0]
    if equiv_set.has_shape(dodg__ocr):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            dodg__ocr)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    dhnqa__mrfxz = []
    for jmk__qmndo, qrv__qhbav in table_type.type_to_blk.items():
        gkhd__wnih = len(table_type.block_to_arr_ind[qrv__qhbav])
        fotg__xnbl = []
        for i in range(gkhd__wnih):
            blg__boq = table_type.block_to_arr_ind[qrv__qhbav][i]
            fotg__xnbl.append(pyval.arrays[blg__boq])
        dhnqa__mrfxz.append(context.get_constant_generic(builder, types.
            List(jmk__qmndo), fotg__xnbl))
    vxiux__hmlmx = context.get_constant_null(types.pyobject)
    hzmy__saqf = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(dhnqa__mrfxz + [vxiux__hmlmx,
        hzmy__saqf])


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
        for jmk__qmndo, qrv__qhbav in out_table_type.type_to_blk.items():
            okrkt__mlrzl = context.get_constant_null(types.List(jmk__qmndo))
            setattr(table, f'block_{qrv__qhbav}', okrkt__mlrzl)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    xtfn__wbrgf = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        xtfn__wbrgf[typ.dtype] = i
    lxxtv__qdc = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(lxxtv__qdc, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        fyl__fdqf, pgnd__wjq = args
        table = cgutils.create_struct_proxy(lxxtv__qdc)(context, builder)
        for jmk__qmndo, qrv__qhbav in lxxtv__qdc.type_to_blk.items():
            idx = xtfn__wbrgf[jmk__qmndo]
            rpl__fwiv = signature(types.List(jmk__qmndo),
                tuple_of_lists_type, types.literal(idx))
            yjj__wxnpl = fyl__fdqf, idx
            tumvf__wnxza = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, rpl__fwiv, yjj__wxnpl)
            setattr(table, f'block_{qrv__qhbav}', tumvf__wnxza)
        return table._getvalue()
    sig = lxxtv__qdc(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    qrv__qhbav = get_overload_const_int(blk_type)
    arr_type = None
    for jmk__qmndo, mvd__tcm in table_type.type_to_blk.items():
        if mvd__tcm == qrv__qhbav:
            arr_type = jmk__qmndo
            break
    assert arr_type is not None, 'invalid table type block'
    hvb__fwz = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        xuh__ohjao = getattr(table, f'block_{qrv__qhbav}')
        return impl_ret_borrowed(context, builder, hvb__fwz, xuh__ohjao)
    sig = hvb__fwz(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, oxexj__avmgp = args
        ixh__nnw = context.get_python_api(builder)
        yodb__rgmry = used_cols_typ == types.none
        if not yodb__rgmry:
            ctlqu__ftf = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), oxexj__avmgp)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for jmk__qmndo, qrv__qhbav in table_type.type_to_blk.items():
            hdovd__iklt = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[qrv__qhbav]))
            orpxx__byh = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                qrv__qhbav], dtype=np.int64))
            fibi__xtif = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, orpxx__byh)
            xuh__ohjao = getattr(table, f'block_{qrv__qhbav}')
            with cgutils.for_range(builder, hdovd__iklt) as jmdb__xkg:
                i = jmdb__xkg.index
                blg__boq = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    fibi__xtif, i)
                nybl__qfgmw = types.none(table_type, types.List(jmk__qmndo),
                    types.int64, types.int64)
                qmn__ggp = table_arg, xuh__ohjao, i, blg__boq
                if yodb__rgmry:
                    ensure_column_unboxed_codegen(context, builder,
                        nybl__qfgmw, qmn__ggp)
                else:
                    egcrm__wjd = ctlqu__ftf.contains(blg__boq)
                    with builder.if_then(egcrm__wjd):
                        ensure_column_unboxed_codegen(context, builder,
                            nybl__qfgmw, qmn__ggp)
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
    table_arg, zbqg__vbbqm, baez__ixwfh, pvdv__rug = args
    ixh__nnw = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    ijhlj__jcu = cgutils.is_not_null(builder, table.parent)
    gwe__lgr = ListInstance(context, builder, sig.args[1], zbqg__vbbqm)
    zod__rrpe = gwe__lgr.getitem(baez__ixwfh)
    lzpl__yzqds = cgutils.alloca_once_value(builder, zod__rrpe)
    nwt__uaa = cgutils.alloca_once_value(builder, context.get_constant_null
        (sig.args[1].dtype))
    is_null = is_ll_eq(builder, lzpl__yzqds, nwt__uaa)
    with builder.if_then(is_null):
        with builder.if_else(ijhlj__jcu) as (jaygk__cofl, tsr__oqto):
            with jaygk__cofl:
                ugg__joty = get_df_obj_column_codegen(context, builder,
                    ixh__nnw, table.parent, pvdv__rug, sig.args[1].dtype)
                arr = ixh__nnw.to_native_value(sig.args[1].dtype, ugg__joty
                    ).value
                gwe__lgr.inititem(baez__ixwfh, arr, incref=False)
                ixh__nnw.decref(ugg__joty)
            with tsr__oqto:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    qrv__qhbav = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, bvrjm__prndz, pgnd__wjq = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{qrv__qhbav}', bvrjm__prndz)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, pvaeu__kkghv = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = pvaeu__kkghv
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        ckjt__glv, ljx__svap = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, ljx__svap)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, ckjt__glv)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    hvb__fwz = list_type.instance_type if isinstance(list_type, types.TypeRef
        ) else list_type
    assert isinstance(hvb__fwz, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        hvb__fwz = types.List(to_str_arr_if_dict_array(hvb__fwz.dtype))

    def codegen(context, builder, sig, args):
        epj__rewy = args[1]
        pgnd__wjq, cany__ngvz = ListInstance.allocate_ex(context, builder,
            hvb__fwz, epj__rewy)
        cany__ngvz.size = epj__rewy
        return cany__ngvz.value
    sig = hvb__fwz(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    cwx__vfl = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(cwx__vfl)

    def codegen(context, builder, sig, args):
        epj__rewy, pgnd__wjq = args
        pgnd__wjq, cany__ngvz = ListInstance.allocate_ex(context, builder,
            list_type, epj__rewy)
        cany__ngvz.size = epj__rewy
        return cany__ngvz.value
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
        ewh__aquv = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(ewh__aquv)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    yhjsr__kckj = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        nsf__yopeh = used_cols.instance_type
        cooot__sddek = np.array(nsf__yopeh.meta, dtype=np.int64)
        yhjsr__kckj['used_cols_vals'] = cooot__sddek
        pzzzx__epj = set([T.block_nums[i] for i in cooot__sddek])
    else:
        cooot__sddek = None
    eaz__wpsa = 'def table_filter_func(T, idx, used_cols=None):\n'
    eaz__wpsa += f'  T2 = init_table(T, False)\n'
    eaz__wpsa += f'  l = 0\n'
    if cooot__sddek is not None and len(cooot__sddek) == 0:
        eaz__wpsa += f'  l = _get_idx_length(idx, len(T))\n'
        eaz__wpsa += f'  T2 = set_table_len(T2, l)\n'
        eaz__wpsa += f'  return T2\n'
        tcdf__jete = {}
        exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
        return tcdf__jete['table_filter_func']
    if cooot__sddek is not None:
        eaz__wpsa += f'  used_set = set(used_cols_vals)\n'
    for qrv__qhbav in T.type_to_blk.values():
        eaz__wpsa += (
            f'  arr_list_{qrv__qhbav} = get_table_block(T, {qrv__qhbav})\n')
        eaz__wpsa += f"""  out_arr_list_{qrv__qhbav} = alloc_list_like(arr_list_{qrv__qhbav}, len(arr_list_{qrv__qhbav}), False)
"""
        if cooot__sddek is None or qrv__qhbav in pzzzx__epj:
            yhjsr__kckj[f'arr_inds_{qrv__qhbav}'] = np.array(T.
                block_to_arr_ind[qrv__qhbav], dtype=np.int64)
            eaz__wpsa += f'  for i in range(len(arr_list_{qrv__qhbav})):\n'
            eaz__wpsa += (
                f'    arr_ind_{qrv__qhbav} = arr_inds_{qrv__qhbav}[i]\n')
            if cooot__sddek is not None:
                eaz__wpsa += (
                    f'    if arr_ind_{qrv__qhbav} not in used_set: continue\n')
            eaz__wpsa += f"""    ensure_column_unboxed(T, arr_list_{qrv__qhbav}, i, arr_ind_{qrv__qhbav})
"""
            eaz__wpsa += f"""    out_arr_{qrv__qhbav} = ensure_contig_if_np(arr_list_{qrv__qhbav}[i][idx])
"""
            eaz__wpsa += f'    l = len(out_arr_{qrv__qhbav})\n'
            eaz__wpsa += (
                f'    out_arr_list_{qrv__qhbav}[i] = out_arr_{qrv__qhbav}\n')
        eaz__wpsa += (
            f'  T2 = set_table_block(T2, out_arr_list_{qrv__qhbav}, {qrv__qhbav})\n'
            )
    eaz__wpsa += f'  T2 = set_table_len(T2, l)\n'
    eaz__wpsa += f'  return T2\n'
    tcdf__jete = {}
    exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
    return tcdf__jete['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    dxff__nizw = list(idx.instance_type.meta)
    disp__szi = tuple(np.array(T.arr_types, dtype=object)[dxff__nizw])
    qflz__hdjv = TableType(disp__szi)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    wov__opbwg = is_overload_true(copy_arrs)
    yhjsr__kckj = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': qflz__hdjv}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        fsxe__ahffj = set(kept_cols)
        yhjsr__kckj['kept_cols'] = np.array(kept_cols, np.int64)
        gxl__hjor = True
    else:
        gxl__hjor = False
    fptq__ccl = {i: c for i, c in enumerate(dxff__nizw)}
    eaz__wpsa = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    eaz__wpsa += f'  T2 = init_table(out_table_typ, False)\n'
    eaz__wpsa += f'  T2 = set_table_len(T2, len(T))\n'
    if gxl__hjor and len(fsxe__ahffj) == 0:
        eaz__wpsa += f'  return T2\n'
        tcdf__jete = {}
        exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
        return tcdf__jete['table_subset']
    if gxl__hjor:
        eaz__wpsa += f'  kept_cols_set = set(kept_cols)\n'
    for typ, qrv__qhbav in qflz__hdjv.type_to_blk.items():
        swzbp__krnl = T.type_to_blk[typ]
        eaz__wpsa += (
            f'  arr_list_{qrv__qhbav} = get_table_block(T, {swzbp__krnl})\n')
        eaz__wpsa += f"""  out_arr_list_{qrv__qhbav} = alloc_list_like(arr_list_{qrv__qhbav}, {len(qflz__hdjv.block_to_arr_ind[qrv__qhbav])}, False)
"""
        glpep__eiq = True
        if gxl__hjor:
            zggui__zep = set(qflz__hdjv.block_to_arr_ind[qrv__qhbav])
            deoeu__jotrd = zggui__zep & fsxe__ahffj
            glpep__eiq = len(deoeu__jotrd) > 0
        if glpep__eiq:
            yhjsr__kckj[f'out_arr_inds_{qrv__qhbav}'] = np.array(qflz__hdjv
                .block_to_arr_ind[qrv__qhbav], dtype=np.int64)
            eaz__wpsa += f'  for i in range(len(out_arr_list_{qrv__qhbav})):\n'
            eaz__wpsa += (
                f'    out_arr_ind_{qrv__qhbav} = out_arr_inds_{qrv__qhbav}[i]\n'
                )
            if gxl__hjor:
                eaz__wpsa += (
                    f'    if out_arr_ind_{qrv__qhbav} not in kept_cols_set: continue\n'
                    )
            ddvkx__flup = []
            zapv__rbvnj = []
            for mdsc__qrxau in qflz__hdjv.block_to_arr_ind[qrv__qhbav]:
                wzarb__cbwq = fptq__ccl[mdsc__qrxau]
                ddvkx__flup.append(wzarb__cbwq)
                xol__pmu = T.block_offsets[wzarb__cbwq]
                zapv__rbvnj.append(xol__pmu)
            yhjsr__kckj[f'in_logical_idx_{qrv__qhbav}'] = np.array(ddvkx__flup,
                dtype=np.int64)
            yhjsr__kckj[f'in_physical_idx_{qrv__qhbav}'] = np.array(zapv__rbvnj
                , dtype=np.int64)
            eaz__wpsa += (
                f'    logical_idx_{qrv__qhbav} = in_logical_idx_{qrv__qhbav}[i]\n'
                )
            eaz__wpsa += (
                f'    physical_idx_{qrv__qhbav} = in_physical_idx_{qrv__qhbav}[i]\n'
                )
            eaz__wpsa += f"""    ensure_column_unboxed(T, arr_list_{qrv__qhbav}, physical_idx_{qrv__qhbav}, logical_idx_{qrv__qhbav})
"""
            plyw__upvki = '.copy()' if wov__opbwg else ''
            eaz__wpsa += f"""    out_arr_list_{qrv__qhbav}[i] = arr_list_{qrv__qhbav}[physical_idx_{qrv__qhbav}]{plyw__upvki}
"""
        eaz__wpsa += (
            f'  T2 = set_table_block(T2, out_arr_list_{qrv__qhbav}, {qrv__qhbav})\n'
            )
    eaz__wpsa += f'  return T2\n'
    tcdf__jete = {}
    exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
    return tcdf__jete['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    dodg__ocr = args[0]
    if equiv_set.has_shape(dodg__ocr):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=dodg__ocr, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (dodg__ocr)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    dodg__ocr = args[0]
    if equiv_set.has_shape(dodg__ocr):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            dodg__ocr)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    eaz__wpsa = 'def impl(T):\n'
    eaz__wpsa += f'  T2 = init_table(T, True)\n'
    eaz__wpsa += f'  l = len(T)\n'
    yhjsr__kckj = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for qrv__qhbav in T.type_to_blk.values():
        yhjsr__kckj[f'arr_inds_{qrv__qhbav}'] = np.array(T.block_to_arr_ind
            [qrv__qhbav], dtype=np.int64)
        eaz__wpsa += (
            f'  arr_list_{qrv__qhbav} = get_table_block(T, {qrv__qhbav})\n')
        eaz__wpsa += f"""  out_arr_list_{qrv__qhbav} = alloc_list_like(arr_list_{qrv__qhbav}, len(arr_list_{qrv__qhbav}), True)
"""
        eaz__wpsa += f'  for i in range(len(arr_list_{qrv__qhbav})):\n'
        eaz__wpsa += f'    arr_ind_{qrv__qhbav} = arr_inds_{qrv__qhbav}[i]\n'
        eaz__wpsa += f"""    ensure_column_unboxed(T, arr_list_{qrv__qhbav}, i, arr_ind_{qrv__qhbav})
"""
        eaz__wpsa += (
            f'    out_arr_{qrv__qhbav} = decode_if_dict_array(arr_list_{qrv__qhbav}[i])\n'
            )
        eaz__wpsa += (
            f'    out_arr_list_{qrv__qhbav}[i] = out_arr_{qrv__qhbav}\n')
        eaz__wpsa += (
            f'  T2 = set_table_block(T2, out_arr_list_{qrv__qhbav}, {qrv__qhbav})\n'
            )
    eaz__wpsa += f'  T2 = set_table_len(T2, l)\n'
    eaz__wpsa += f'  return T2\n'
    tcdf__jete = {}
    exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
    return tcdf__jete['impl']


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
        berek__enn = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        berek__enn = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            berek__enn.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        cnqv__xdz, bhoo__chsj = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = bhoo__chsj
        dhnqa__mrfxz = cgutils.unpack_tuple(builder, cnqv__xdz)
        for i, xuh__ohjao in enumerate(dhnqa__mrfxz):
            setattr(table, f'block_{i}', xuh__ohjao)
            context.nrt.incref(builder, types.List(berek__enn[i]), xuh__ohjao)
        return table._getvalue()
    table_type = TableType(tuple(berek__enn), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    yhjsr__kckj = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        yhjsr__kckj['kept_cols'] = np.array(list(kept_cols), np.int64)
        gxl__hjor = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        gxl__hjor = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    ecwfs__tar = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        ecwfs__tar else extra_arrs_t.types[i - ecwfs__tar] for i in
        in_col_inds)) if is_overload_none(out_table_type_t
        ) else unwrap_typeref(out_table_type_t)
    eaz__wpsa = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    eaz__wpsa += f'  T1 = in_table_t\n'
    eaz__wpsa += f'  T2 = init_table(out_table_type, False)\n'
    eaz__wpsa += f'  T2 = set_table_len(T2, len(T1))\n'
    if gxl__hjor and len(kept_cols) == 0:
        eaz__wpsa += f'  return T2\n'
        tcdf__jete = {}
        exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
        return tcdf__jete['impl']
    if gxl__hjor:
        eaz__wpsa += f'  kept_cols_set = set(kept_cols)\n'
    for typ, qrv__qhbav in out_table_type.type_to_blk.items():
        yhjsr__kckj[f'arr_list_typ_{qrv__qhbav}'] = types.List(typ)
        hdovd__iklt = len(out_table_type.block_to_arr_ind[qrv__qhbav])
        eaz__wpsa += f"""  out_arr_list_{qrv__qhbav} = alloc_list_like(arr_list_typ_{qrv__qhbav}, {hdovd__iklt}, False)
"""
        if typ in in_table_t.type_to_blk:
            faxl__nrl = in_table_t.type_to_blk[typ]
            baij__knpc = []
            vek__wufxv = []
            for pbj__ovwfm in out_table_type.block_to_arr_ind[qrv__qhbav]:
                kno__awk = in_col_inds[pbj__ovwfm]
                if kno__awk < ecwfs__tar:
                    baij__knpc.append(in_table_t.block_offsets[kno__awk])
                    vek__wufxv.append(kno__awk)
                else:
                    baij__knpc.append(-1)
                    vek__wufxv.append(-1)
            yhjsr__kckj[f'in_idxs_{qrv__qhbav}'] = np.array(baij__knpc, np.
                int64)
            yhjsr__kckj[f'in_arr_inds_{qrv__qhbav}'] = np.array(vek__wufxv,
                np.int64)
            if gxl__hjor:
                yhjsr__kckj[f'out_arr_inds_{qrv__qhbav}'] = np.array(
                    out_table_type.block_to_arr_ind[qrv__qhbav], dtype=np.int64
                    )
            eaz__wpsa += (
                f'  in_arr_list_{qrv__qhbav} = get_table_block(T1, {faxl__nrl})\n'
                )
            eaz__wpsa += f'  for i in range(len(out_arr_list_{qrv__qhbav})):\n'
            eaz__wpsa += (
                f'    in_offset_{qrv__qhbav} = in_idxs_{qrv__qhbav}[i]\n')
            eaz__wpsa += f'    if in_offset_{qrv__qhbav} == -1:\n'
            eaz__wpsa += f'      continue\n'
            eaz__wpsa += (
                f'    in_arr_ind_{qrv__qhbav} = in_arr_inds_{qrv__qhbav}[i]\n')
            if gxl__hjor:
                eaz__wpsa += (
                    f'    if out_arr_inds_{qrv__qhbav}[i] not in kept_cols_set: continue\n'
                    )
            eaz__wpsa += f"""    ensure_column_unboxed(T1, in_arr_list_{qrv__qhbav}, in_offset_{qrv__qhbav}, in_arr_ind_{qrv__qhbav})
"""
            eaz__wpsa += f"""    out_arr_list_{qrv__qhbav}[i] = in_arr_list_{qrv__qhbav}[in_offset_{qrv__qhbav}]
"""
        for i, pbj__ovwfm in enumerate(out_table_type.block_to_arr_ind[
            qrv__qhbav]):
            if pbj__ovwfm not in kept_cols:
                continue
            kno__awk = in_col_inds[pbj__ovwfm]
            if kno__awk >= ecwfs__tar:
                eaz__wpsa += f"""  out_arr_list_{qrv__qhbav}[{i}] = extra_arrs_t[{kno__awk - ecwfs__tar}]
"""
        eaz__wpsa += (
            f'  T2 = set_table_block(T2, out_arr_list_{qrv__qhbav}, {qrv__qhbav})\n'
            )
    eaz__wpsa += f'  return T2\n'
    yhjsr__kckj.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    tcdf__jete = {}
    exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
    return tcdf__jete['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    ecwfs__tar = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < ecwfs__tar else
        extra_arrs_t.types[i - ecwfs__tar] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    pvf__lwo = None
    if not is_overload_none(in_table_t):
        for i, jmk__qmndo in enumerate(in_table_t.types):
            if jmk__qmndo != types.none:
                pvf__lwo = f'in_table_t[{i}]'
                break
    if pvf__lwo is None:
        for i, jmk__qmndo in enumerate(extra_arrs_t.types):
            if jmk__qmndo != types.none:
                pvf__lwo = f'extra_arrs_t[{i}]'
                break
    assert pvf__lwo is not None, 'no array found in input data'
    eaz__wpsa = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    eaz__wpsa += f'  T1 = in_table_t\n'
    eaz__wpsa += f'  T2 = init_table(out_table_type, False)\n'
    eaz__wpsa += f'  T2 = set_table_len(T2, len({pvf__lwo}))\n'
    yhjsr__kckj = {}
    for typ, qrv__qhbav in out_table_type.type_to_blk.items():
        yhjsr__kckj[f'arr_list_typ_{qrv__qhbav}'] = types.List(typ)
        hdovd__iklt = len(out_table_type.block_to_arr_ind[qrv__qhbav])
        eaz__wpsa += f"""  out_arr_list_{qrv__qhbav} = alloc_list_like(arr_list_typ_{qrv__qhbav}, {hdovd__iklt}, False)
"""
        for i, pbj__ovwfm in enumerate(out_table_type.block_to_arr_ind[
            qrv__qhbav]):
            if pbj__ovwfm not in kept_cols:
                continue
            kno__awk = in_col_inds[pbj__ovwfm]
            if kno__awk < ecwfs__tar:
                eaz__wpsa += (
                    f'  out_arr_list_{qrv__qhbav}[{i}] = T1[{kno__awk}]\n')
            else:
                eaz__wpsa += f"""  out_arr_list_{qrv__qhbav}[{i}] = extra_arrs_t[{kno__awk - ecwfs__tar}]
"""
        eaz__wpsa += (
            f'  T2 = set_table_block(T2, out_arr_list_{qrv__qhbav}, {qrv__qhbav})\n'
            )
    eaz__wpsa += f'  return T2\n'
    yhjsr__kckj.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    tcdf__jete = {}
    exec(eaz__wpsa, yhjsr__kckj, tcdf__jete)
    return tcdf__jete['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    agmf__phqnp = args[0]
    xcz__xds = args[1]
    if equiv_set.has_shape(agmf__phqnp):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            agmf__phqnp)[0], None), pre=[])
    if equiv_set.has_shape(xcz__xds):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            xcz__xds)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
