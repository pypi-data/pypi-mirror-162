import hashlib
import inspect
import warnings
import pandas as pd
pandas_version = tuple(map(int, pd.__version__.split('.')[:2]))
_check_pandas_change = False
if pandas_version < (1, 4):

    def _set_noconvert_columns(self):
        assert self.orig_names is not None
        hbcd__ejjt = {uiaso__hobk: wfeuf__pnnt for wfeuf__pnnt, uiaso__hobk in
            enumerate(self.orig_names)}
        jmoz__xgijc = [hbcd__ejjt[uiaso__hobk] for uiaso__hobk in self.names]
        ionrt__rmfi = self._set_noconvert_dtype_columns(jmoz__xgijc, self.names
            )
        for gzn__xyrg in ionrt__rmfi:
            self._reader.set_noconvert(gzn__xyrg)
    if _check_pandas_change:
        lines = inspect.getsource(pd.io.parsers.c_parser_wrapper.
            CParserWrapper._set_noconvert_columns)
        if (hashlib.sha256(lines.encode()).hexdigest() !=
            'afc2d738f194e3976cf05d61cb16dc4224b0139451f08a1cf49c578af6f975d3'
            ):
            warnings.warn(
                'pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns has changed'
                )
    (pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns
        ) = _set_noconvert_columns
