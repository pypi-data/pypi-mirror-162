from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    rssub__yamf = f'class {class_name}(types.Opaque):\n'
    rssub__yamf += f'    def __init__(self):\n'
    rssub__yamf += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    rssub__yamf += f'    def __reduce__(self):\n'
    rssub__yamf += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    cnirs__axw = {}
    exec(rssub__yamf, {'types': types, 'models': models}, cnirs__axw)
    gcxx__eiv = cnirs__axw[class_name]
    setattr(module, class_name, gcxx__eiv)
    class_instance = gcxx__eiv()
    setattr(types, types_name, class_instance)
    rssub__yamf = f'class {model_name}(models.StructModel):\n'
    rssub__yamf += f'    def __init__(self, dmm, fe_type):\n'
    rssub__yamf += f'        members = [\n'
    rssub__yamf += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    rssub__yamf += f"            ('pyobj', types.voidptr),\n"
    rssub__yamf += f'        ]\n'
    rssub__yamf += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(rssub__yamf, {'types': types, 'models': models, types_name:
        class_instance}, cnirs__axw)
    qqayo__rizxn = cnirs__axw[model_name]
    setattr(module, model_name, qqayo__rizxn)
    register_model(gcxx__eiv)(qqayo__rizxn)
    make_attribute_wrapper(gcxx__eiv, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(gcxx__eiv)(unbox_py_obj)
    box(gcxx__eiv)(box_py_obj)
    return gcxx__eiv


def box_py_obj(typ, val, c):
    wtz__ddah = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = wtz__ddah.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    wtz__ddah = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wtz__ddah.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    wtz__ddah.pyobj = obj
    return NativeValue(wtz__ddah._getvalue())
