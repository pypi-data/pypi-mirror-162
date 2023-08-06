"""
Helper functions and classes to simplify Template Generation
for Bodo classes.
"""
import numba
from numba.core.typing.templates import AttributeTemplate


class OverloadedKeyAttributeTemplate(AttributeTemplate):
    _attr_set = None

    def _is_existing_attr(self, attr_name):
        if self._attr_set is None:
            vsx__lmx = set()
            rcrs__uvgt = list(self.context._get_attribute_templates(self.key))
            vckt__exs = rcrs__uvgt.index(self) + 1
            for jhex__sln in range(vckt__exs, len(rcrs__uvgt)):
                if isinstance(rcrs__uvgt[jhex__sln], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    vsx__lmx.add(rcrs__uvgt[jhex__sln]._attr)
            self._attr_set = vsx__lmx
        return attr_name in self._attr_set
