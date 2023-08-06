"""Helper information to keep table column deletion
pass organized. This contains information about all
table operations for optimizations.
"""
from typing import Dict, Tuple
from numba.core import ir, types
from bodo.hiframes.table import TableType
table_usecol_funcs = {('get_table_data', 'bodo.hiframes.table'), (
    'table_filter', 'bodo.hiframes.table'), ('table_subset',
    'bodo.hiframes.table'), ('set_table_data', 'bodo.hiframes.table'), (
    'set_table_data_null', 'bodo.hiframes.table'), (
    'generate_mappable_table_func', 'bodo.utils.table_utils'), (
    'table_astype', 'bodo.utils.table_utils'), ('generate_table_nbytes',
    'bodo.utils.table_utils'), ('table_concat', 'bodo.utils.table_utils'),
    ('py_data_to_cpp_table', 'bodo.libs.array'), ('logical_table_to_table',
    'bodo.hiframes.table')}


def is_table_use_column_ops(fdef: Tuple[str, str], args, typemap):
    return fdef in table_usecol_funcs and len(args) > 0 and isinstance(typemap
        [args[0].name], TableType)


def get_table_used_columns(fdef: Tuple[str, str], call_expr: ir.Expr,
    typemap: Dict[str, types.Type]):
    if fdef == ('get_table_data', 'bodo.hiframes.table'):
        ltvur__wbd = typemap[call_expr.args[1].name].literal_value
        return {ltvur__wbd}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        xhipz__smank = dict(call_expr.kws)
        if 'used_cols' in xhipz__smank:
            lcyo__zcpv = xhipz__smank['used_cols']
            wtqco__qbx = typemap[lcyo__zcpv.name]
            wtqco__qbx = wtqco__qbx.instance_type
            return set(wtqco__qbx.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        lcyo__zcpv = call_expr.args[1]
        wtqco__qbx = typemap[lcyo__zcpv.name]
        wtqco__qbx = wtqco__qbx.instance_type
        return set(wtqco__qbx.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        rsqjm__ucbla = call_expr.args[1]
        mjxc__ezxg = typemap[rsqjm__ucbla.name]
        mjxc__ezxg = mjxc__ezxg.instance_type
        ccrot__zop = mjxc__ezxg.meta
        xhipz__smank = dict(call_expr.kws)
        if 'used_cols' in xhipz__smank:
            lcyo__zcpv = xhipz__smank['used_cols']
            wtqco__qbx = typemap[lcyo__zcpv.name]
            wtqco__qbx = wtqco__qbx.instance_type
            fgydk__gzesy = set(wtqco__qbx.meta)
            uwfeb__xhmua = set()
            for gnbm__izlz, bqw__zfvz in enumerate(ccrot__zop):
                if gnbm__izlz in fgydk__gzesy:
                    uwfeb__xhmua.add(bqw__zfvz)
            return uwfeb__xhmua
        else:
            return set(ccrot__zop)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        yub__xuc = typemap[call_expr.args[2].name].instance_type.meta
        wjs__vvwv = len(typemap[call_expr.args[0].name].arr_types)
        return set(gnbm__izlz for gnbm__izlz in yub__xuc if gnbm__izlz <
            wjs__vvwv)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        iroch__wtesn = typemap[call_expr.args[2].name].instance_type.meta
        fjra__lhnql = len(typemap[call_expr.args[0].name].arr_types)
        xhipz__smank = dict(call_expr.kws)
        if 'used_cols' in xhipz__smank:
            fgydk__gzesy = set(typemap[xhipz__smank['used_cols'].name].
                instance_type.meta)
            mwdkn__getk = set()
            for pqw__mnwe, whul__blv in enumerate(iroch__wtesn):
                if pqw__mnwe in fgydk__gzesy and whul__blv < fjra__lhnql:
                    mwdkn__getk.add(whul__blv)
            return mwdkn__getk
        else:
            return set(gnbm__izlz for gnbm__izlz in iroch__wtesn if 
                gnbm__izlz < fjra__lhnql)
    return None
