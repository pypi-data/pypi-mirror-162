from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    nti__qxpwq = f'class {class_name}(types.Opaque):\n'
    nti__qxpwq += f'    def __init__(self):\n'
    nti__qxpwq += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    nti__qxpwq += f'    def __reduce__(self):\n'
    nti__qxpwq += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    yeucx__cgk = {}
    exec(nti__qxpwq, {'types': types, 'models': models}, yeucx__cgk)
    aznp__bsh = yeucx__cgk[class_name]
    setattr(module, class_name, aznp__bsh)
    class_instance = aznp__bsh()
    setattr(types, types_name, class_instance)
    nti__qxpwq = f'class {model_name}(models.StructModel):\n'
    nti__qxpwq += f'    def __init__(self, dmm, fe_type):\n'
    nti__qxpwq += f'        members = [\n'
    nti__qxpwq += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    nti__qxpwq += f"            ('pyobj', types.voidptr),\n"
    nti__qxpwq += f'        ]\n'
    nti__qxpwq += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(nti__qxpwq, {'types': types, 'models': models, types_name:
        class_instance}, yeucx__cgk)
    wnjw__nlzh = yeucx__cgk[model_name]
    setattr(module, model_name, wnjw__nlzh)
    register_model(aznp__bsh)(wnjw__nlzh)
    make_attribute_wrapper(aznp__bsh, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(aznp__bsh)(unbox_py_obj)
    box(aznp__bsh)(box_py_obj)
    return aznp__bsh


def box_py_obj(typ, val, c):
    spn__uywoq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = spn__uywoq.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    spn__uywoq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    spn__uywoq.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    spn__uywoq.pyobj = obj
    return NativeValue(spn__uywoq._getvalue())
