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
    aglhs__mhywq = context.get_python_api(builder)
    return aglhs__mhywq.unserialize(aglhs__mhywq.serialize_object(pyval))


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
        yjmw__qixsn = ', '.join('e{}'.format(sss__adc) for sss__adc in
            range(len(args)))
        if yjmw__qixsn:
            yjmw__qixsn += ', '
        xdwxc__iro = ', '.join("{} = ''".format(ffp__nrun) for ffp__nrun in
            kws.keys())
        zaqsb__fteqq = (
            f'def format_stub(string, {yjmw__qixsn} {xdwxc__iro}):\n')
        zaqsb__fteqq += '    pass\n'
        jawrm__demk = {}
        exec(zaqsb__fteqq, {}, jawrm__demk)
        xtsr__hbh = jawrm__demk['format_stub']
        rzpyo__gbh = numba.core.utils.pysignature(xtsr__hbh)
        ryjzc__edgq = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, ryjzc__edgq).replace(pysig=rzpyo__gbh)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for wnm__gnfe in ('logging.Logger', 'logging.RootLogger'):
        for eewcv__cxj in func_names:
            brfzv__vxtmy = f'@bound_function("{wnm__gnfe}.{eewcv__cxj}")\n'
            brfzv__vxtmy += (
                f'def resolve_{eewcv__cxj}(self, logger_typ, args, kws):\n')
            brfzv__vxtmy += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(brfzv__vxtmy)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for xlum__dfkck in logging_logger_unsupported_attrs:
        ylz__auz = 'logging.Logger.' + xlum__dfkck
        overload_attribute(LoggingLoggerType, xlum__dfkck)(
            create_unsupported_overload(ylz__auz))
    for dxbcr__xozas in logging_logger_unsupported_methods:
        ylz__auz = 'logging.Logger.' + dxbcr__xozas
        overload_method(LoggingLoggerType, dxbcr__xozas)(
            create_unsupported_overload(ylz__auz))


_install_logging_logger_unsupported_objects()
