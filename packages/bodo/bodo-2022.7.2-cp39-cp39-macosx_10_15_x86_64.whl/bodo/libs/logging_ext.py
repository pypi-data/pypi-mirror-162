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
    qtk__ovnl = context.get_python_api(builder)
    return qtk__ovnl.unserialize(qtk__ovnl.serialize_object(pyval))


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
        kce__pqkm = ', '.join('e{}'.format(vho__zyn) for vho__zyn in range(
            len(args)))
        if kce__pqkm:
            kce__pqkm += ', '
        hah__losye = ', '.join("{} = ''".format(gdkv__lelr) for gdkv__lelr in
            kws.keys())
        tsnf__kwa = f'def format_stub(string, {kce__pqkm} {hah__losye}):\n'
        tsnf__kwa += '    pass\n'
        qrflu__qrw = {}
        exec(tsnf__kwa, {}, qrflu__qrw)
        jfwq__unri = qrflu__qrw['format_stub']
        uvhkj__zkc = numba.core.utils.pysignature(jfwq__unri)
        cjw__kdhzl = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, cjw__kdhzl).replace(pysig=uvhkj__zkc)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for lab__idl in ('logging.Logger', 'logging.RootLogger'):
        for abb__kxy in func_names:
            cayl__rls = f'@bound_function("{lab__idl}.{abb__kxy}")\n'
            cayl__rls += (
                f'def resolve_{abb__kxy}(self, logger_typ, args, kws):\n')
            cayl__rls += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(cayl__rls)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for pmqw__dcwi in logging_logger_unsupported_attrs:
        jggxw__bynr = 'logging.Logger.' + pmqw__dcwi
        overload_attribute(LoggingLoggerType, pmqw__dcwi)(
            create_unsupported_overload(jggxw__bynr))
    for xmnb__dvos in logging_logger_unsupported_methods:
        jggxw__bynr = 'logging.Logger.' + xmnb__dvos
        overload_method(LoggingLoggerType, xmnb__dvos)(
            create_unsupported_overload(jggxw__bynr))


_install_logging_logger_unsupported_objects()
