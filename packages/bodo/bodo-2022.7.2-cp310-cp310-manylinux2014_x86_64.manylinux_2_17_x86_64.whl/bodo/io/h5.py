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
        pam__xqdpy = self._get_h5_type(lhs, rhs)
        if pam__xqdpy is not None:
            vtrlc__dqonu = str(pam__xqdpy.dtype)
            olt__burjc = 'def _h5_read_impl(dset, index):\n'
            olt__burjc += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(pam__xqdpy.ndim, vtrlc__dqonu))
            sqmik__pou = {}
            exec(olt__burjc, {}, sqmik__pou)
            new__iaxcn = sqmik__pou['_h5_read_impl']
            owe__ocyag = compile_to_numba_ir(new__iaxcn, {'bodo': bodo}
                ).blocks.popitem()[1]
            uge__lzbkp = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(owe__ocyag, [rhs.value, uge__lzbkp])
            tgqg__bpi = owe__ocyag.body[:-3]
            tgqg__bpi[-1].target = assign.target
            return tgqg__bpi
        return None

    def _get_h5_type(self, lhs, rhs):
        pam__xqdpy = self._get_h5_type_locals(lhs)
        if pam__xqdpy is not None:
            return pam__xqdpy
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        uge__lzbkp = rhs.index if rhs.op == 'getitem' else rhs.index_var
        dpin__tms = guard(find_const, self.func_ir, uge__lzbkp)
        require(not isinstance(dpin__tms, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            vsrj__pei = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            fzrs__ufo = get_const_value_inner(self.func_ir, vsrj__pei,
                arg_types=self.arg_types)
            obj_name_list.append(fzrs__ufo)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        vupwi__hrvqx = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        jhjp__ubiex = h5py.File(vupwi__hrvqx, 'r')
        hxx__owk = jhjp__ubiex
        for fzrs__ufo in obj_name_list:
            hxx__owk = hxx__owk[fzrs__ufo]
        require(isinstance(hxx__owk, h5py.Dataset))
        wle__jjfet = len(hxx__owk.shape)
        lvmja__uom = numba.np.numpy_support.from_dtype(hxx__owk.dtype)
        jhjp__ubiex.close()
        return types.Array(lvmja__uom, wle__jjfet, 'C')

    def _get_h5_type_locals(self, varname):
        zslh__hduwk = self.locals.pop(varname, None)
        if zslh__hduwk is None and varname is not None:
            zslh__hduwk = self.flags.h5_types.get(varname, None)
        return zslh__hduwk
