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
        xtvrv__tub = typemap[call_expr.args[1].name].literal_value
        return {xtvrv__tub}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        uizs__qyrzx = dict(call_expr.kws)
        if 'used_cols' in uizs__qyrzx:
            rwjsd__kqdov = uizs__qyrzx['used_cols']
            fgeu__pvh = typemap[rwjsd__kqdov.name]
            fgeu__pvh = fgeu__pvh.instance_type
            return set(fgeu__pvh.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        rwjsd__kqdov = call_expr.args[1]
        fgeu__pvh = typemap[rwjsd__kqdov.name]
        fgeu__pvh = fgeu__pvh.instance_type
        return set(fgeu__pvh.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        ximjz__zwo = call_expr.args[1]
        zcuv__omx = typemap[ximjz__zwo.name]
        zcuv__omx = zcuv__omx.instance_type
        cprdd__naon = zcuv__omx.meta
        uizs__qyrzx = dict(call_expr.kws)
        if 'used_cols' in uizs__qyrzx:
            rwjsd__kqdov = uizs__qyrzx['used_cols']
            fgeu__pvh = typemap[rwjsd__kqdov.name]
            fgeu__pvh = fgeu__pvh.instance_type
            xpsm__mtwj = set(fgeu__pvh.meta)
            hun__lje = set()
            for dkl__iwh, pcb__qubv in enumerate(cprdd__naon):
                if dkl__iwh in xpsm__mtwj:
                    hun__lje.add(pcb__qubv)
            return hun__lje
        else:
            return set(cprdd__naon)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        mcl__aoe = typemap[call_expr.args[2].name].instance_type.meta
        alcd__gyu = len(typemap[call_expr.args[0].name].arr_types)
        return set(dkl__iwh for dkl__iwh in mcl__aoe if dkl__iwh < alcd__gyu)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        bixyy__bdv = typemap[call_expr.args[2].name].instance_type.meta
        ykooy__ppqc = len(typemap[call_expr.args[0].name].arr_types)
        uizs__qyrzx = dict(call_expr.kws)
        if 'used_cols' in uizs__qyrzx:
            xpsm__mtwj = set(typemap[uizs__qyrzx['used_cols'].name].
                instance_type.meta)
            fiqmx__acf = set()
            for analm__vfzo, grz__fiol in enumerate(bixyy__bdv):
                if analm__vfzo in xpsm__mtwj and grz__fiol < ykooy__ppqc:
                    fiqmx__acf.add(grz__fiol)
            return fiqmx__acf
        else:
            return set(dkl__iwh for dkl__iwh in bixyy__bdv if dkl__iwh <
                ykooy__ppqc)
    return None
