"""
Analysis and transformation for HDF5 support.
"""
import types as pytypes
import numba
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, find_callname, find_const, get_definition, guard, replace_arg_nodes, require
import bodo
import bodo.io
from bodo.utils.transform import get_const_value_inner


class H5_IO:

    def __init__(self, func_ir, _locals, flags, arg_types):
        self.func_ir = func_ir
        self.locals = _locals
        self.flags = flags
        self.arg_types = arg_types

    def handle_possible_h5_read(self, assign, lhs, rhs):
        mbgq__ecqyk = self._get_h5_type(lhs, rhs)
        if mbgq__ecqyk is not None:
            ijyx__uzln = str(mbgq__ecqyk.dtype)
            ddld__wax = 'def _h5_read_impl(dset, index):\n'
            ddld__wax += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(mbgq__ecqyk.ndim, ijyx__uzln))
            xvplm__qlawd = {}
            exec(ddld__wax, {}, xvplm__qlawd)
            xzjtd__gfq = xvplm__qlawd['_h5_read_impl']
            ndv__oiw = compile_to_numba_ir(xzjtd__gfq, {'bodo': bodo}
                ).blocks.popitem()[1]
            xuc__ndil = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(ndv__oiw, [rhs.value, xuc__ndil])
            aagd__hlkzf = ndv__oiw.body[:-3]
            aagd__hlkzf[-1].target = assign.target
            return aagd__hlkzf
        return None

    def _get_h5_type(self, lhs, rhs):
        mbgq__ecqyk = self._get_h5_type_locals(lhs)
        if mbgq__ecqyk is not None:
            return mbgq__ecqyk
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        xuc__ndil = rhs.index if rhs.op == 'getitem' else rhs.index_var
        aib__oone = guard(find_const, self.func_ir, xuc__ndil)
        require(not isinstance(aib__oone, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            egpl__cfm = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            jbkg__suo = get_const_value_inner(self.func_ir, egpl__cfm,
                arg_types=self.arg_types)
            obj_name_list.append(jbkg__suo)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        djbtf__lzx = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        uiax__ovlu = h5py.File(djbtf__lzx, 'r')
        komg__lrjuy = uiax__ovlu
        for jbkg__suo in obj_name_list:
            komg__lrjuy = komg__lrjuy[jbkg__suo]
        require(isinstance(komg__lrjuy, h5py.Dataset))
        mju__pdu = len(komg__lrjuy.shape)
        eqy__gdcq = numba.np.numpy_support.from_dtype(komg__lrjuy.dtype)
        uiax__ovlu.close()
        return types.Array(eqy__gdcq, mju__pdu, 'C')

    def _get_h5_type_locals(self, varname):
        ldu__nheb = self.locals.pop(varname, None)
        if ldu__nheb is None and varname is not None:
            ldu__nheb = self.flags.h5_types.get(varname, None)
        return ldu__nheb
