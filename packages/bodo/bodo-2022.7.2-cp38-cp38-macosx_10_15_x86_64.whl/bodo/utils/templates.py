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
            vujb__hhpzx = set()
            jjt__clpyn = list(self.context._get_attribute_templates(self.key))
            tpinz__ljlk = jjt__clpyn.index(self) + 1
            for kpo__qpsmy in range(tpinz__ljlk, len(jjt__clpyn)):
                if isinstance(jjt__clpyn[kpo__qpsmy], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    vujb__hhpzx.add(jjt__clpyn[kpo__qpsmy]._attr)
            self._attr_set = vujb__hhpzx
        return attr_name in self._attr_set
