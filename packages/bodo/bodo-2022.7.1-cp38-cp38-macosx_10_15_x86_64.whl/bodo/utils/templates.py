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
            tuh__gxm = set()
            ybd__bmf = list(self.context._get_attribute_templates(self.key))
            gomou__kin = ybd__bmf.index(self) + 1
            for gpttc__hmr in range(gomou__kin, len(ybd__bmf)):
                if isinstance(ybd__bmf[gpttc__hmr], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    tuh__gxm.add(ybd__bmf[gpttc__hmr]._attr)
            self._attr_set = tuh__gxm
        return attr_name in self._attr_set
