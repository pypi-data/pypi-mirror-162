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
        bqs__gbfho = self._get_h5_type(lhs, rhs)
        if bqs__gbfho is not None:
            jhroh__jskg = str(bqs__gbfho.dtype)
            cdv__caf = 'def _h5_read_impl(dset, index):\n'
            cdv__caf += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(bqs__gbfho.ndim, jhroh__jskg))
            rgpq__mcs = {}
            exec(cdv__caf, {}, rgpq__mcs)
            qpcfm__vheu = rgpq__mcs['_h5_read_impl']
            dgrdf__ejtb = compile_to_numba_ir(qpcfm__vheu, {'bodo': bodo}
                ).blocks.popitem()[1]
            fdpg__jbu = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(dgrdf__ejtb, [rhs.value, fdpg__jbu])
            ucn__ayh = dgrdf__ejtb.body[:-3]
            ucn__ayh[-1].target = assign.target
            return ucn__ayh
        return None

    def _get_h5_type(self, lhs, rhs):
        bqs__gbfho = self._get_h5_type_locals(lhs)
        if bqs__gbfho is not None:
            return bqs__gbfho
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        fdpg__jbu = rhs.index if rhs.op == 'getitem' else rhs.index_var
        mies__jjzs = guard(find_const, self.func_ir, fdpg__jbu)
        require(not isinstance(mies__jjzs, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            trn__yhh = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            iani__fkaux = get_const_value_inner(self.func_ir, trn__yhh,
                arg_types=self.arg_types)
            obj_name_list.append(iani__fkaux)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        ugn__xssqk = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        gta__szvas = h5py.File(ugn__xssqk, 'r')
        evog__lbwwm = gta__szvas
        for iani__fkaux in obj_name_list:
            evog__lbwwm = evog__lbwwm[iani__fkaux]
        require(isinstance(evog__lbwwm, h5py.Dataset))
        mtff__avnu = len(evog__lbwwm.shape)
        xok__lzaf = numba.np.numpy_support.from_dtype(evog__lbwwm.dtype)
        gta__szvas.close()
        return types.Array(xok__lzaf, mtff__avnu, 'C')

    def _get_h5_type_locals(self, varname):
        kjno__jxjo = self.locals.pop(varname, None)
        if kjno__jxjo is None and varname is not None:
            kjno__jxjo = self.flags.h5_types.get(varname, None)
        return kjno__jxjo
