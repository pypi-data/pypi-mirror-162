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
            owhl__cdf = set()
            nqsd__suzg = list(self.context._get_attribute_templates(self.key))
            abql__lkfrx = nqsd__suzg.index(self) + 1
            for cyclj__msjmg in range(abql__lkfrx, len(nqsd__suzg)):
                if isinstance(nqsd__suzg[cyclj__msjmg], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    owhl__cdf.add(nqsd__suzg[cyclj__msjmg]._attr)
            self._attr_set = owhl__cdf
        return attr_name in self._attr_set
