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
        jfe__acd = self._get_h5_type(lhs, rhs)
        if jfe__acd is not None:
            xbrfg__hjo = str(jfe__acd.dtype)
            ujdbn__fyugr = 'def _h5_read_impl(dset, index):\n'
            ujdbn__fyugr += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(jfe__acd.ndim, xbrfg__hjo))
            ffdhu__ptg = {}
            exec(ujdbn__fyugr, {}, ffdhu__ptg)
            elmgk__ogr = ffdhu__ptg['_h5_read_impl']
            sno__pwluw = compile_to_numba_ir(elmgk__ogr, {'bodo': bodo}
                ).blocks.popitem()[1]
            plp__zvhfz = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(sno__pwluw, [rhs.value, plp__zvhfz])
            cpzd__eaz = sno__pwluw.body[:-3]
            cpzd__eaz[-1].target = assign.target
            return cpzd__eaz
        return None

    def _get_h5_type(self, lhs, rhs):
        jfe__acd = self._get_h5_type_locals(lhs)
        if jfe__acd is not None:
            return jfe__acd
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        plp__zvhfz = rhs.index if rhs.op == 'getitem' else rhs.index_var
        jiy__eqmx = guard(find_const, self.func_ir, plp__zvhfz)
        require(not isinstance(jiy__eqmx, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            uafo__oqgbx = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            sbw__cejib = get_const_value_inner(self.func_ir, uafo__oqgbx,
                arg_types=self.arg_types)
            obj_name_list.append(sbw__cejib)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        urx__azbnj = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        ekpve__tavjx = h5py.File(urx__azbnj, 'r')
        lnmqy__ksh = ekpve__tavjx
        for sbw__cejib in obj_name_list:
            lnmqy__ksh = lnmqy__ksh[sbw__cejib]
        require(isinstance(lnmqy__ksh, h5py.Dataset))
        pgsa__dfe = len(lnmqy__ksh.shape)
        zjh__znh = numba.np.numpy_support.from_dtype(lnmqy__ksh.dtype)
        ekpve__tavjx.close()
        return types.Array(zjh__znh, pgsa__dfe, 'C')

    def _get_h5_type_locals(self, varname):
        ekob__qwahj = self.locals.pop(varname, None)
        if ekob__qwahj is None and varname is not None:
            ekob__qwahj = self.flags.h5_types.get(varname, None)
        return ekob__qwahj
