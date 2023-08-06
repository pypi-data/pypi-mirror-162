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
    xpu__umzb = context.get_python_api(builder)
    return xpu__umzb.unserialize(xpu__umzb.serialize_object(pyval))


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
        hhpy__zzj = ', '.join('e{}'.format(qdu__loer) for qdu__loer in
            range(len(args)))
        if hhpy__zzj:
            hhpy__zzj += ', '
        ybr__clh = ', '.join("{} = ''".format(pydlw__pvj) for pydlw__pvj in
            kws.keys())
        isr__mhh = f'def format_stub(string, {hhpy__zzj} {ybr__clh}):\n'
        isr__mhh += '    pass\n'
        couje__ijyl = {}
        exec(isr__mhh, {}, couje__ijyl)
        zynr__twy = couje__ijyl['format_stub']
        phz__ffpqr = numba.core.utils.pysignature(zynr__twy)
        nznbc__jaxf = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, nznbc__jaxf).replace(pysig=phz__ffpqr)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for isbv__szsxv in ('logging.Logger', 'logging.RootLogger'):
        for pldmj__wrt in func_names:
            zew__htz = f'@bound_function("{isbv__szsxv}.{pldmj__wrt}")\n'
            zew__htz += (
                f'def resolve_{pldmj__wrt}(self, logger_typ, args, kws):\n')
            zew__htz += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(zew__htz)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for hbjx__srn in logging_logger_unsupported_attrs:
        mbzd__joae = 'logging.Logger.' + hbjx__srn
        overload_attribute(LoggingLoggerType, hbjx__srn)(
            create_unsupported_overload(mbzd__joae))
    for jdgk__eirkt in logging_logger_unsupported_methods:
        mbzd__joae = 'logging.Logger.' + jdgk__eirkt
        overload_method(LoggingLoggerType, jdgk__eirkt)(
            create_unsupported_overload(mbzd__joae))


_install_logging_logger_unsupported_objects()
