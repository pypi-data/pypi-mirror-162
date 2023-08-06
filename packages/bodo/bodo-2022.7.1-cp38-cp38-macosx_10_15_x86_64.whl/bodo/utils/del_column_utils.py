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
        gcoi__rzqf = typemap[call_expr.args[1].name].literal_value
        return {gcoi__rzqf}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        pie__uvl = dict(call_expr.kws)
        if 'used_cols' in pie__uvl:
            swqn__ohr = pie__uvl['used_cols']
            piodq__szpfp = typemap[swqn__ohr.name]
            piodq__szpfp = piodq__szpfp.instance_type
            return set(piodq__szpfp.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        swqn__ohr = call_expr.args[1]
        piodq__szpfp = typemap[swqn__ohr.name]
        piodq__szpfp = piodq__szpfp.instance_type
        return set(piodq__szpfp.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        uspz__gsq = call_expr.args[1]
        bjzjz__ncbb = typemap[uspz__gsq.name]
        bjzjz__ncbb = bjzjz__ncbb.instance_type
        fzh__vxga = bjzjz__ncbb.meta
        pie__uvl = dict(call_expr.kws)
        if 'used_cols' in pie__uvl:
            swqn__ohr = pie__uvl['used_cols']
            piodq__szpfp = typemap[swqn__ohr.name]
            piodq__szpfp = piodq__szpfp.instance_type
            edwz__ojo = set(piodq__szpfp.meta)
            xvu__ibspa = set()
            for ifh__rpm, nnh__tesm in enumerate(fzh__vxga):
                if ifh__rpm in edwz__ojo:
                    xvu__ibspa.add(nnh__tesm)
            return xvu__ibspa
        else:
            return set(fzh__vxga)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        vuelg__lwyme = typemap[call_expr.args[2].name].instance_type.meta
        smg__mwvup = len(typemap[call_expr.args[0].name].arr_types)
        return set(ifh__rpm for ifh__rpm in vuelg__lwyme if ifh__rpm <
            smg__mwvup)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        fhal__hkeiq = typemap[call_expr.args[2].name].instance_type.meta
        wisc__zhtt = len(typemap[call_expr.args[0].name].arr_types)
        pie__uvl = dict(call_expr.kws)
        if 'used_cols' in pie__uvl:
            edwz__ojo = set(typemap[pie__uvl['used_cols'].name].
                instance_type.meta)
            lguf__ali = set()
            for quvml__tyt, lda__oouo in enumerate(fhal__hkeiq):
                if quvml__tyt in edwz__ojo and lda__oouo < wisc__zhtt:
                    lguf__ali.add(lda__oouo)
            return lguf__ali
        else:
            return set(ifh__rpm for ifh__rpm in fhal__hkeiq if ifh__rpm <
                wisc__zhtt)
    return None
