"""
Support for PySpark APIs in Bodo JIT functions
"""
from collections import namedtuple
import numba
import numba.cpython.tupleobj
import numpy as np
import pyspark
import pyspark.sql.functions as F
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, infer_global, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, dtype_to_array_type, get_overload_const_list, get_overload_const_str, is_overload_constant_list, is_overload_constant_str, is_overload_true
ANON_SENTINEL = 'bodo_field_'


class SparkSessionType(types.Opaque):

    def __init__(self):
        super(SparkSessionType, self).__init__(name='SparkSessionType')


spark_session_type = SparkSessionType()
register_model(SparkSessionType)(models.OpaqueModel)


class SparkSessionBuilderType(types.Opaque):

    def __init__(self):
        super(SparkSessionBuilderType, self).__init__(name=
            'SparkSessionBuilderType')


spark_session_builder_type = SparkSessionBuilderType()
register_model(SparkSessionBuilderType)(models.OpaqueModel)


@intrinsic
def init_session(typingctx=None):

    def codegen(context, builder, signature, args):
        return context.get_constant_null(spark_session_type)
    return spark_session_type(), codegen


@intrinsic
def init_session_builder(typingctx=None):

    def codegen(context, builder, signature, args):
        return context.get_constant_null(spark_session_builder_type)
    return spark_session_builder_type(), codegen


@overload_method(SparkSessionBuilderType, 'appName', no_unliteral=True)
def overload_appName(A, s):
    return lambda A, s: A


@overload_method(SparkSessionBuilderType, 'getOrCreate', inline='always',
    no_unliteral=True)
def overload_getOrCreate(A):
    return lambda A: bodo.libs.pyspark_ext.init_session()


@typeof_impl.register(pyspark.sql.session.SparkSession)
def typeof_session(val, c):
    return spark_session_type


@box(SparkSessionType)
def box_spark_session(typ, val, c):
    wbh__ivan = c.context.insert_const_string(c.builder.module, 'pyspark')
    inga__mupuj = c.pyapi.import_module_noblock(wbh__ivan)
    ialzg__ayqkf = c.pyapi.object_getattr_string(inga__mupuj, 'sql')
    speq__kyq = c.pyapi.object_getattr_string(ialzg__ayqkf, 'SparkSession')
    rnl__juj = c.pyapi.object_getattr_string(speq__kyq, 'builder')
    hunp__wthyj = c.pyapi.call_method(rnl__juj, 'getOrCreate', ())
    c.pyapi.decref(inga__mupuj)
    c.pyapi.decref(ialzg__ayqkf)
    c.pyapi.decref(speq__kyq)
    c.pyapi.decref(rnl__juj)
    return hunp__wthyj


@unbox(SparkSessionType)
def unbox_spark_session(typ, obj, c):
    return NativeValue(c.context.get_constant_null(spark_session_type))


@lower_constant(SparkSessionType)
def lower_constant_spark_session(context, builder, ty, pyval):
    return context.get_constant_null(spark_session_type)


class RowType(types.BaseNamedTuple):

    def __init__(self, types, fields):
        self.types = tuple(types)
        self.count = len(self.types)
        self.fields = tuple(fields)
        self.instance_class = namedtuple('Row', fields)
        elx__dyb = 'Row({})'.format(', '.join(f'{cirw__icju}:{haq__htx}' for
            cirw__icju, haq__htx in zip(self.fields, self.types)))
        super(RowType, self).__init__(elx__dyb)

    @property
    def key(self):
        return self.fields, self.types

    def __getitem__(self, i):
        return self.types[i]

    def __len__(self):
        return len(self.types)

    def __iter__(self):
        return iter(self.types)


@register_model(RowType)
class RowModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qydmf__kgw = [(cirw__icju, haq__htx) for cirw__icju, haq__htx in
            zip(fe_type.fields, fe_type.types)]
        super(RowModel, self).__init__(dmm, fe_type, qydmf__kgw)


@typeof_impl.register(pyspark.sql.types.Row)
def typeof_row(val, c):
    fields = val.__fields__ if hasattr(val, '__fields__') else tuple(
        f'{ANON_SENTINEL}{i}' for i in range(len(val)))
    return RowType(tuple(numba.typeof(uxf__iyz) for uxf__iyz in val), fields)


@box(RowType)
def box_row(typ, val, c):
    gzekh__eua = c.pyapi.unserialize(c.pyapi.serialize_object(pyspark.sql.
        types.Row))
    if all(cirw__icju.startswith(ANON_SENTINEL) for cirw__icju in typ.fields):
        qtlg__pov = [c.box(haq__htx, c.builder.extract_value(val, i)) for i,
            haq__htx in enumerate(typ.types)]
        tdv__qtssi = c.pyapi.call_function_objargs(gzekh__eua, qtlg__pov)
        for obj in qtlg__pov:
            c.pyapi.decref(obj)
        c.pyapi.decref(gzekh__eua)
        return tdv__qtssi
    args = c.pyapi.tuple_pack([])
    qtlg__pov = []
    vyun__trbj = []
    for i, haq__htx in enumerate(typ.types):
        tfpsk__zydl = c.builder.extract_value(val, i)
        obj = c.box(haq__htx, tfpsk__zydl)
        vyun__trbj.append((typ.fields[i], obj))
        qtlg__pov.append(obj)
    kws = c.pyapi.dict_pack(vyun__trbj)
    tdv__qtssi = c.pyapi.call(gzekh__eua, args, kws)
    for obj in qtlg__pov:
        c.pyapi.decref(obj)
    c.pyapi.decref(gzekh__eua)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    return tdv__qtssi


@infer_global(pyspark.sql.types.Row)
class RowConstructor(AbstractTemplate):

    def generic(self, args, kws):
        if args and kws:
            raise BodoError(
                'pyspark.sql.types.Row: Cannot use both args and kwargs to create Row'
                )
        syiu__bjdlf = ', '.join(f'arg{i}' for i in range(len(args)))
        bonjf__rcsfw = ', '.join(f"{htgtw__qhr} = ''" for htgtw__qhr in kws)
        func_text = f'def row_stub({syiu__bjdlf}{bonjf__rcsfw}):\n'
        func_text += '    pass\n'
        pxrl__tzcdz = {}
        exec(func_text, {}, pxrl__tzcdz)
        znauc__uiq = pxrl__tzcdz['row_stub']
        vquv__nqx = numba.core.utils.pysignature(znauc__uiq)
        if args:
            nlki__evtx = RowType(args, tuple(f'{ANON_SENTINEL}{i}' for i in
                range(len(args))))
            return signature(nlki__evtx, *args).replace(pysig=vquv__nqx)
        kws = dict(kws)
        nlki__evtx = RowType(tuple(kws.values()), tuple(kws.keys()))
        return signature(nlki__evtx, *kws.values()).replace(pysig=vquv__nqx)


lower_builtin(pyspark.sql.types.Row, types.VarArg(types.Any))(numba.cpython
    .tupleobj.namedtuple_constructor)


class SparkDataFrameType(types.Type):

    def __init__(self, df):
        self.df = df
        super(SparkDataFrameType, self).__init__(f'SparkDataFrame({df})')

    @property
    def key(self):
        return self.df

    def copy(self):
        return SparkDataFrameType(self.df)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SparkDataFrameType)
class SparkDataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qydmf__kgw = [('df', fe_type.df)]
        super(SparkDataFrameModel, self).__init__(dmm, fe_type, qydmf__kgw)


make_attribute_wrapper(SparkDataFrameType, 'df', '_df')


@intrinsic
def init_spark_df(typingctx, df_typ=None):

    def codegen(context, builder, sig, args):
        df, = args
        spark_df = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        spark_df.df = df
        context.nrt.incref(builder, sig.args[0], df)
        return spark_df._getvalue()
    return SparkDataFrameType(df_typ)(df_typ), codegen


@overload_method(SparkSessionType, 'createDataFrame', inline='always',
    no_unliteral=True)
def overload_create_df(sp_session, data, schema=None, samplingRatio=None,
    verifySchema=True):
    check_runtime_cols_unsupported(data, 'spark.createDataFrame()')
    if isinstance(data, DataFrameType):

        def impl_df(sp_session, data, schema=None, samplingRatio=None,
            verifySchema=True):
            data = bodo.scatterv(data, warn_if_dist=False)
            return bodo.libs.pyspark_ext.init_spark_df(data)
        return impl_df
    if not (isinstance(data, types.List) and isinstance(data.dtype, RowType)):
        raise BodoError(
            f"SparkSession.createDataFrame(): 'data' should be a Pandas dataframe or list of Rows, not {data}"
            )
    qfugw__zywvz = data.dtype.fields
    uzkbl__dajln = len(data.dtype.types)
    func_text = (
        'def impl(sp_session, data, schema=None, samplingRatio=None, verifySchema=True):\n'
        )
    func_text += f'  n = len(data)\n'
    oqa__omq = []
    for i, haq__htx in enumerate(data.dtype.types):
        oajc__hcyb = dtype_to_array_type(haq__htx)
        func_text += (
            f'  A{i} = bodo.utils.utils.alloc_type(n, arr_typ{i}, (-1,))\n')
        oqa__omq.append(oajc__hcyb)
    func_text += f'  for i in range(n):\n'
    func_text += f'    r = data[i]\n'
    for i in range(uzkbl__dajln):
        func_text += (
            f'    A{i}[i] = bodo.utils.conversion.unbox_if_timestamp(r[{i}])\n'
            )
    bapyi__nlhb = '({}{})'.format(', '.join(f'A{i}' for i in range(
        uzkbl__dajln)), ',' if len(qfugw__zywvz) == 1 else '')
    func_text += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)\n'
        )
    func_text += f"""  pdf = bodo.hiframes.pd_dataframe_ext.init_dataframe({bapyi__nlhb}, index, __col_name_meta_value_create_df)
"""
    func_text += f'  pdf = bodo.scatterv(pdf)\n'
    func_text += f'  return bodo.libs.pyspark_ext.init_spark_df(pdf)\n'
    pxrl__tzcdz = {}
    yxt__zjglf = {'bodo': bodo, '__col_name_meta_value_create_df':
        ColNamesMetaType(tuple(qfugw__zywvz))}
    for i in range(uzkbl__dajln):
        yxt__zjglf[f'arr_typ{i}'] = oqa__omq[i]
    exec(func_text, yxt__zjglf, pxrl__tzcdz)
    impl = pxrl__tzcdz['impl']
    return impl


@overload_method(SparkDataFrameType, 'toPandas', inline='always',
    no_unliteral=True)
def overload_to_pandas(spark_df, _is_bodo_dist=False):
    if is_overload_true(_is_bodo_dist):
        return lambda spark_df, _is_bodo_dist=False: spark_df._df

    def impl(spark_df, _is_bodo_dist=False):
        return bodo.gatherv(spark_df._df, warn_if_rep=False)
    return impl


@overload_method(SparkDataFrameType, 'limit', inline='always', no_unliteral
    =True)
def overload_limit(spark_df, num):

    def impl(spark_df, num):
        return bodo.libs.pyspark_ext.init_spark_df(spark_df._df.iloc[:num])
    return impl


def _df_to_rows(df):
    pass


@overload(_df_to_rows)
def overload_df_to_rows(df):
    func_text = 'def impl(df):\n'
    for i in range(len(df.columns)):
        func_text += (
            f'  A{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    func_text += '  n = len(df)\n'
    func_text += '  out = []\n'
    func_text += '  for i in range(n):\n'
    lkhpl__luh = ', '.join(f'{c}=A{i}[i]' for i, c in enumerate(df.columns))
    func_text += f'    out.append(Row({lkhpl__luh}))\n'
    func_text += '  return out\n'
    pxrl__tzcdz = {}
    yxt__zjglf = {'bodo': bodo, 'Row': pyspark.sql.types.Row}
    exec(func_text, yxt__zjglf, pxrl__tzcdz)
    impl = pxrl__tzcdz['impl']
    return impl


@overload_method(SparkDataFrameType, 'collect', inline='always',
    no_unliteral=True)
def overload_collect(spark_df):

    def impl(spark_df):
        data = bodo.gatherv(spark_df._df, warn_if_rep=False)
        return _df_to_rows(data)
    return impl


@overload_method(SparkDataFrameType, 'take', inline='always', no_unliteral=True
    )
def overload_take(spark_df, num):

    def impl(spark_df, num):
        return spark_df.limit(num).collect()
    return impl


@infer_getattr
class SparkDataFrameAttribute(AttributeTemplate):
    key = SparkDataFrameType

    def generic_resolve(self, sdf, attr):
        if attr in sdf.df.columns:
            return ColumnType(ExprType('col', (attr,)))


SparkDataFrameAttribute._no_unliteral = True


@overload_method(SparkDataFrameType, 'select', no_unliteral=True)
def overload_df_select(spark_df, *cols):
    return _gen_df_select(spark_df, cols)


def _gen_df_select(spark_df, cols, avoid_stararg=False):
    df_type = spark_df.df
    if isinstance(cols, tuple) and len(cols) == 1 and isinstance(cols[0], (
        types.StarArgTuple, types.StarArgUniTuple)):
        cols = cols[0]
    if len(cols) == 1 and is_overload_constant_list(cols[0]):
        cols = get_overload_const_list(cols[0])
    func_text = f"def impl(spark_df, {'' if avoid_stararg else '*cols'}):\n"
    func_text += '  df = spark_df._df\n'
    out_col_names = []
    out_data = []
    for col in cols:
        col = get_overload_const_str(col) if is_overload_constant_str(col
            ) else col
        out_col_names.append(_get_col_name(col))
        data, hpx__bqsb = _gen_col_code(col, df_type)
        func_text += hpx__bqsb
        out_data.append(data)
    return _gen_init_spark_df(func_text, out_data, out_col_names)


def _gen_init_spark_df(func_text, out_data, out_col_names):
    bapyi__nlhb = '({}{})'.format(', '.join(out_data), ',' if len(out_data) ==
        1 else '')
    rfaov__uip = '0' if not out_data else f'len({out_data[0]})'
    func_text += f'  n = {rfaov__uip}\n'
    func_text += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)\n'
        )
    func_text += f"""  pdf = bodo.hiframes.pd_dataframe_ext.init_dataframe({bapyi__nlhb}, index, __col_name_meta_value_init_spark_df)
"""
    func_text += f'  return bodo.libs.pyspark_ext.init_spark_df(pdf)\n'
    pxrl__tzcdz = {}
    yxt__zjglf = {'bodo': bodo, 'np': np,
        '__col_name_meta_value_init_spark_df': ColNamesMetaType(tuple(
        out_col_names))}
    exec(func_text, yxt__zjglf, pxrl__tzcdz)
    impl = pxrl__tzcdz['impl']
    return impl


@overload_method(SparkDataFrameType, 'show', inline='always', no_unliteral=True
    )
def overload_show(spark_df, n=20, truncate=True, vertical=False):
    ghmmd__qfcrb = dict(truncate=truncate, vertical=vertical)
    uikoh__dtucy = dict(truncate=True, vertical=False)
    check_unsupported_args('SparkDataFrameType.show', ghmmd__qfcrb,
        uikoh__dtucy)

    def impl(spark_df, n=20, truncate=True, vertical=False):
        print(spark_df._df.head(n))
    return impl


@overload_method(SparkDataFrameType, 'printSchema', inline='always',
    no_unliteral=True)
def overload_print_schema(spark_df):

    def impl(spark_df):
        print(spark_df._df.dtypes)
    return impl


@overload_method(SparkDataFrameType, 'withColumn', inline='always',
    no_unliteral=True)
def overload_with_column(spark_df, colName, col):
    _check_column(col)
    if not is_overload_constant_str(colName):
        raise BodoError(
            f"SparkDataFrame.withColumn(): 'colName' should be a constant string, not {colName}"
            )
    col_name = get_overload_const_str(colName)
    jtiy__bbup = spark_df.df.columns
    xjrcy__cfloy = jtiy__bbup if col_name in jtiy__bbup else jtiy__bbup + (
        col_name,)
    gxik__dxhdy, yka__hjf = _gen_col_code(col, spark_df.df)
    out_data = [(gxik__dxhdy if c == col_name else
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {jtiy__bbup.index(c)})'
        ) for c in xjrcy__cfloy]
    func_text = 'def impl(spark_df, colName, col):\n'
    func_text += '  df = spark_df._df\n'
    func_text += yka__hjf
    return _gen_init_spark_df(func_text, out_data, xjrcy__cfloy)


@overload_method(SparkDataFrameType, 'withColumnRenamed', inline='always',
    no_unliteral=True)
def overload_with_column_renamed(spark_df, existing, new):
    if not (is_overload_constant_str(existing) and is_overload_constant_str
        (new)):
        raise BodoError(
            f"SparkDataFrame.withColumnRenamed(): 'existing' and 'new' should be a constant strings, not ({existing}, {new})"
            )
    ptty__ovo = get_overload_const_str(existing)
    orgjb__hdqa = get_overload_const_str(new)
    jtiy__bbup = spark_df.df.columns
    xjrcy__cfloy = tuple(orgjb__hdqa if c == ptty__ovo else c for c in
        jtiy__bbup)
    out_data = [f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
         for i in range(len(jtiy__bbup))]
    func_text = 'def impl(spark_df, existing, new):\n'
    func_text += '  df = spark_df._df\n'
    return _gen_init_spark_df(func_text, out_data, xjrcy__cfloy)


@overload_attribute(SparkDataFrameType, 'columns', inline='always')
def overload_dataframe_columns(spark_df):
    szbpk__enxa = list(str(htgtw__qhr) for htgtw__qhr in spark_df.df.columns)
    func_text = 'def impl(spark_df):\n'
    func_text += f'  return {szbpk__enxa}\n'
    pxrl__tzcdz = {}
    exec(func_text, {}, pxrl__tzcdz)
    impl = pxrl__tzcdz['impl']
    return impl


class ColumnType(types.Type):

    def __init__(self, expr):
        self.expr = expr
        super(ColumnType, self).__init__(f'Column({expr})')

    @property
    def key(self):
        return self.expr

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


register_model(ColumnType)(models.OpaqueModel)


class ExprType(types.Type):

    def __init__(self, op, children):
        self.op = op
        self.children = children
        super(ExprType, self).__init__(f'{op}({children})')

    @property
    def key(self):
        return self.op, self.children

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


register_model(ExprType)(models.OpaqueModel)


@intrinsic
def init_col_from_name(typingctx, col=None):
    assert is_overload_constant_str(col)
    xengp__sydit = get_overload_const_str(col)
    pyv__kzeja = ColumnType(ExprType('col', (xengp__sydit,)))

    def codegen(context, builder, signature, args):
        return context.get_constant_null(pyv__kzeja)
    return pyv__kzeja(col), codegen


@overload(F.col, no_unliteral=True)
@overload(F.column, no_unliteral=True)
def overload_f_col(col):
    if not is_overload_constant_str(col):
        raise BodoError(
            f'pyspark.sql.functions.col(): column name should be a constant string, not {col}'
            )
    return lambda col: init_col_from_name(col)


@intrinsic
def init_f_sum(typingctx, col=None):
    pyv__kzeja = ColumnType(ExprType('sum', (col.expr,)))

    def codegen(context, builder, signature, args):
        return context.get_constant_null(pyv__kzeja)
    return pyv__kzeja(col), codegen


@overload(F.sum, no_unliteral=True)
def overload_f_sum(col):
    if is_overload_constant_str(col):
        return lambda col: init_f_sum(init_col_from_name(col))
    if not isinstance(col, ColumnType):
        raise BodoError(
            f'pyspark.sql.functions.sum(): input should be a Column object or a constant string, not {col}'
            )
    return lambda col: init_f_sum(col)


def _get_col_name(col):
    if isinstance(col, str):
        return col
    _check_column(col)
    return _get_col_name_exr(col.expr)


def _get_col_name_exr(expr):
    if expr.op == 'sum':
        return f'sum({_get_col_name_exr(expr.children[0])})'
    assert expr.op == 'col'
    return expr.children[0]


def _gen_col_code(col, df_type):
    if isinstance(col, str):
        return _gen_col_code_colname(col, df_type)
    _check_column(col)
    return _gen_col_code_expr(col.expr, df_type)


def _gen_col_code_expr(expr, df_type):
    if expr.op == 'col':
        return _gen_col_code_colname(expr.children[0], df_type)
    if expr.op == 'sum':
        gwi__chrgp, fifki__jrje = _gen_col_code_expr(expr.children[0], df_type)
        i = ir_utils.next_label()
        func_text = f"""  A{i} = np.asarray([bodo.libs.array_ops.array_op_sum({gwi__chrgp}, True, 0)])
"""
        return f'A{i}', fifki__jrje + func_text


def _gen_col_code_colname(col_name, df_type):
    ofz__ost = df_type.columns.index(col_name)
    i = ir_utils.next_label()
    func_text = (
        f'  A{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ofz__ost})\n'
        )
    return f'A{i}', func_text


def _check_column(col):
    if not isinstance(col, ColumnType):
        raise BodoError('Column object expected')
