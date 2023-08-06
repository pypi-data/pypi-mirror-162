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
        diys__ctt = typemap[call_expr.args[1].name].literal_value
        return {diys__ctt}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        dtetj__erjc = dict(call_expr.kws)
        if 'used_cols' in dtetj__erjc:
            kgz__xqt = dtetj__erjc['used_cols']
            ikbc__ybgm = typemap[kgz__xqt.name]
            ikbc__ybgm = ikbc__ybgm.instance_type
            return set(ikbc__ybgm.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        kgz__xqt = call_expr.args[1]
        ikbc__ybgm = typemap[kgz__xqt.name]
        ikbc__ybgm = ikbc__ybgm.instance_type
        return set(ikbc__ybgm.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        lgfsz__cspb = call_expr.args[1]
        kfy__ixr = typemap[lgfsz__cspb.name]
        kfy__ixr = kfy__ixr.instance_type
        kofdh__pqgiw = kfy__ixr.meta
        dtetj__erjc = dict(call_expr.kws)
        if 'used_cols' in dtetj__erjc:
            kgz__xqt = dtetj__erjc['used_cols']
            ikbc__ybgm = typemap[kgz__xqt.name]
            ikbc__ybgm = ikbc__ybgm.instance_type
            xlbe__nji = set(ikbc__ybgm.meta)
            dnnwl__smx = set()
            for ora__gopbo, mrhkt__ejkff in enumerate(kofdh__pqgiw):
                if ora__gopbo in xlbe__nji:
                    dnnwl__smx.add(mrhkt__ejkff)
            return dnnwl__smx
        else:
            return set(kofdh__pqgiw)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        zuoki__ivo = typemap[call_expr.args[2].name].instance_type.meta
        lcw__zpx = len(typemap[call_expr.args[0].name].arr_types)
        return set(ora__gopbo for ora__gopbo in zuoki__ivo if ora__gopbo <
            lcw__zpx)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        mgxq__jrfk = typemap[call_expr.args[2].name].instance_type.meta
        jdl__jpxy = len(typemap[call_expr.args[0].name].arr_types)
        dtetj__erjc = dict(call_expr.kws)
        if 'used_cols' in dtetj__erjc:
            xlbe__nji = set(typemap[dtetj__erjc['used_cols'].name].
                instance_type.meta)
            ncnea__dob = set()
            for vhtzz__kgdax, pta__aikw in enumerate(mgxq__jrfk):
                if vhtzz__kgdax in xlbe__nji and pta__aikw < jdl__jpxy:
                    ncnea__dob.add(pta__aikw)
            return ncnea__dob
        else:
            return set(ora__gopbo for ora__gopbo in mgxq__jrfk if 
                ora__gopbo < jdl__jpxy)
    return None
