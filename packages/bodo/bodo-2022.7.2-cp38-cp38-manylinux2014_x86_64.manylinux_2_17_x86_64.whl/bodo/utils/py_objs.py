from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    tzq__ogcn = f'class {class_name}(types.Opaque):\n'
    tzq__ogcn += f'    def __init__(self):\n'
    tzq__ogcn += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    tzq__ogcn += f'    def __reduce__(self):\n'
    tzq__ogcn += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    vhye__wra = {}
    exec(tzq__ogcn, {'types': types, 'models': models}, vhye__wra)
    srvgt__keslo = vhye__wra[class_name]
    setattr(module, class_name, srvgt__keslo)
    class_instance = srvgt__keslo()
    setattr(types, types_name, class_instance)
    tzq__ogcn = f'class {model_name}(models.StructModel):\n'
    tzq__ogcn += f'    def __init__(self, dmm, fe_type):\n'
    tzq__ogcn += f'        members = [\n'
    tzq__ogcn += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    tzq__ogcn += f"            ('pyobj', types.voidptr),\n"
    tzq__ogcn += f'        ]\n'
    tzq__ogcn += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(tzq__ogcn, {'types': types, 'models': models, types_name:
        class_instance}, vhye__wra)
    zjs__vgy = vhye__wra[model_name]
    setattr(module, model_name, zjs__vgy)
    register_model(srvgt__keslo)(zjs__vgy)
    make_attribute_wrapper(srvgt__keslo, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(srvgt__keslo)(unbox_py_obj)
    box(srvgt__keslo)(box_py_obj)
    return srvgt__keslo


def box_py_obj(typ, val, c):
    aih__pqxt = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = aih__pqxt.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    aih__pqxt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    aih__pqxt.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    aih__pqxt.pyobj = obj
    return NativeValue(aih__pqxt._getvalue())
