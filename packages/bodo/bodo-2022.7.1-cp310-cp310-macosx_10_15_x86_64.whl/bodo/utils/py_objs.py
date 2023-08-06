from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    apel__zfnnh = f'class {class_name}(types.Opaque):\n'
    apel__zfnnh += f'    def __init__(self):\n'
    apel__zfnnh += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    apel__zfnnh += f'    def __reduce__(self):\n'
    apel__zfnnh += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    pukoe__unc = {}
    exec(apel__zfnnh, {'types': types, 'models': models}, pukoe__unc)
    jegwk__klwa = pukoe__unc[class_name]
    setattr(module, class_name, jegwk__klwa)
    class_instance = jegwk__klwa()
    setattr(types, types_name, class_instance)
    apel__zfnnh = f'class {model_name}(models.StructModel):\n'
    apel__zfnnh += f'    def __init__(self, dmm, fe_type):\n'
    apel__zfnnh += f'        members = [\n'
    apel__zfnnh += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    apel__zfnnh += f"            ('pyobj', types.voidptr),\n"
    apel__zfnnh += f'        ]\n'
    apel__zfnnh += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(apel__zfnnh, {'types': types, 'models': models, types_name:
        class_instance}, pukoe__unc)
    zxxa__kizz = pukoe__unc[model_name]
    setattr(module, model_name, zxxa__kizz)
    register_model(jegwk__klwa)(zxxa__kizz)
    make_attribute_wrapper(jegwk__klwa, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(jegwk__klwa)(unbox_py_obj)
    box(jegwk__klwa)(box_py_obj)
    return jegwk__klwa


def box_py_obj(typ, val, c):
    vqh__oey = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = vqh__oey.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    vqh__oey = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vqh__oey.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    vqh__oey.pyobj = obj
    return NativeValue(vqh__oey._getvalue())
