"""
JIT support for Python's logging module
"""
import logging
import numba
from numba.core import types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import bound_function
from numba.core.typing.templates import AttributeTemplate, infer_getattr, signature
from numba.extending import NativeValue, box, models, overload_attribute, overload_method, register_model, typeof_impl, unbox
from bodo.utils.typing import create_unsupported_overload, gen_objmode_attr_overload


class LoggingLoggerType(types.Type):

    def __init__(self, is_root=False):
        self.is_root = is_root
        super(LoggingLoggerType, self).__init__(name=
            f'LoggingLoggerType(is_root={is_root})')


@typeof_impl.register(logging.RootLogger)
@typeof_impl.register(logging.Logger)
def typeof_logging(val, c):
    if isinstance(val, logging.RootLogger):
        return LoggingLoggerType(is_root=True)
    else:
        return LoggingLoggerType(is_root=False)


register_model(LoggingLoggerType)(models.OpaqueModel)


@box(LoggingLoggerType)
def box_logging_logger(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(LoggingLoggerType)
def unbox_logging_logger(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@lower_constant(LoggingLoggerType)
def lower_constant_logger(context, builder, ty, pyval):
    rtwv__shcs = context.get_python_api(builder)
    return rtwv__shcs.unserialize(rtwv__shcs.serialize_object(pyval))


gen_objmode_attr_overload(LoggingLoggerType, 'level', None, types.int64)
gen_objmode_attr_overload(LoggingLoggerType, 'name', None, 'unicode_type')
gen_objmode_attr_overload(LoggingLoggerType, 'propagate', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'disabled', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'parent', None,
    LoggingLoggerType())
gen_objmode_attr_overload(LoggingLoggerType, 'root', None,
    LoggingLoggerType(is_root=True))


@infer_getattr
class LoggingLoggerAttribute(AttributeTemplate):
    key = LoggingLoggerType

    def _resolve_helper(self, logger_typ, args, kws):
        kws = dict(kws)
        mtg__jilfm = ', '.join('e{}'.format(fux__wnppg) for fux__wnppg in
            range(len(args)))
        if mtg__jilfm:
            mtg__jilfm += ', '
        evwo__sbni = ', '.join("{} = ''".format(rtjrv__jfhl) for
            rtjrv__jfhl in kws.keys())
        crds__xmpnh = f'def format_stub(string, {mtg__jilfm} {evwo__sbni}):\n'
        crds__xmpnh += '    pass\n'
        gymjc__xxujz = {}
        exec(crds__xmpnh, {}, gymjc__xxujz)
        nzmg__djbvf = gymjc__xxujz['format_stub']
        bqoqx__muaul = numba.core.utils.pysignature(nzmg__djbvf)
        jqm__lrzkh = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, jqm__lrzkh).replace(pysig=bqoqx__muaul)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for hniew__ehla in ('logging.Logger', 'logging.RootLogger'):
        for ueon__dsno in func_names:
            hrzk__tmnaq = f'@bound_function("{hniew__ehla}.{ueon__dsno}")\n'
            hrzk__tmnaq += (
                f'def resolve_{ueon__dsno}(self, logger_typ, args, kws):\n')
            hrzk__tmnaq += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(hrzk__tmnaq)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for fvj__xtbjb in logging_logger_unsupported_attrs:
        bvgf__hrgy = 'logging.Logger.' + fvj__xtbjb
        overload_attribute(LoggingLoggerType, fvj__xtbjb)(
            create_unsupported_overload(bvgf__hrgy))
    for pye__uufq in logging_logger_unsupported_methods:
        bvgf__hrgy = 'logging.Logger.' + pye__uufq
        overload_method(LoggingLoggerType, pye__uufq)(
            create_unsupported_overload(bvgf__hrgy))


_install_logging_logger_unsupported_objects()
