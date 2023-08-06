"""
S3 & Hadoop file system supports, and file system dependent calls
"""
import glob
import os
import warnings
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
from fsspec.implementations.arrow import ArrowFile, ArrowFSWrapper, wrap_exceptions
from numba.core import types
from numba.extending import NativeValue, models, overload, register_model, unbox
import bodo
from bodo.io import csv_cpp
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.str_ext import unicode_to_utf8, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, BodoWarning, get_overload_constant_dict
from bodo.utils.utils import check_java_installation


def fsspec_arrowfswrapper__open(self, path, mode='rb', block_size=None, **
    kwargs):
    if mode == 'rb':
        try:
            dgbvm__bxwiy = self.fs.open_input_file(path)
        except:
            dgbvm__bxwiy = self.fs.open_input_stream(path)
    elif mode == 'wb':
        dgbvm__bxwiy = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, dgbvm__bxwiy, path, mode, block_size, **kwargs)


ArrowFSWrapper._open = wrap_exceptions(fsspec_arrowfswrapper__open)
_csv_write = types.ExternalFunction('csv_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.voidptr,
    types.voidptr))
ll.add_symbol('csv_write', csv_cpp.csv_write)
bodo_error_msg = """
    Some possible causes:
        (1) Incorrect path: Specified file/directory doesn't exist or is unreachable.
        (2) Missing credentials: You haven't provided S3 credentials, neither through 
            environment variables, nor through a local AWS setup 
            that makes the credentials available at ~/.aws/credentials.
        (3) Incorrect credentials: Your S3 credentials are incorrect or do not have
            the correct permissions.
        (4) Wrong bucket region is used. Set AWS_DEFAULT_REGION variable with correct bucket region.
    """


def get_proxy_uri_from_env_vars():
    return os.environ.get('http_proxy', None) or os.environ.get('https_proxy',
        None) or os.environ.get('HTTP_PROXY', None) or os.environ.get(
        'HTTPS_PROXY', None)


def get_s3_fs(region=None, storage_options=None):
    from pyarrow.fs import S3FileSystem
    klux__pttbs = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    cceky__vsjeo = False
    bcl__muf = get_proxy_uri_from_env_vars()
    if storage_options:
        cceky__vsjeo = storage_options.get('anon', False)
    return S3FileSystem(anonymous=cceky__vsjeo, region=region,
        endpoint_override=klux__pttbs, proxy_options=bcl__muf)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    klux__pttbs = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    cceky__vsjeo = False
    bcl__muf = get_proxy_uri_from_env_vars()
    if storage_options:
        cceky__vsjeo = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=klux__pttbs,
        anonymous=cceky__vsjeo, proxy_options=bcl__muf)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    xvn__kub = urlparse(path)
    if xvn__kub.scheme in ('abfs', 'abfss'):
        yma__tngat = path
        if xvn__kub.port is None:
            bctt__mml = 0
        else:
            bctt__mml = xvn__kub.port
        blrl__igcs = None
    else:
        yma__tngat = xvn__kub.hostname
        bctt__mml = xvn__kub.port
        blrl__igcs = xvn__kub.username
    try:
        fs = HdFS(host=yma__tngat, port=bctt__mml, user=blrl__igcs)
    except Exception as rehw__pcgtl:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            rehw__pcgtl))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        fna__ohlap = fs.isdir(path)
    except gcsfs.utils.HttpError as rehw__pcgtl:
        raise BodoError(
            f'{rehw__pcgtl}. Make sure your google cloud credentials are set!')
    return fna__ohlap


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [cucww__zyzyu.split('/')[-1] for cucww__zyzyu in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        xvn__kub = urlparse(path)
        susce__qovnx = (xvn__kub.netloc + xvn__kub.path).rstrip('/')
        ujdhw__tcnuy = fs.get_file_info(susce__qovnx)
        if ujdhw__tcnuy.type in (pa_fs.FileType.NotFound, pa_fs.FileType.
            Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not ujdhw__tcnuy.size and ujdhw__tcnuy.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as rehw__pcgtl:
        raise
    except BodoError as xixs__vzbi:
        raise
    except Exception as rehw__pcgtl:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(rehw__pcgtl).__name__}: {str(rehw__pcgtl)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    akgxv__ownh = None
    try:
        if s3_is_directory(fs, path):
            xvn__kub = urlparse(path)
            susce__qovnx = (xvn__kub.netloc + xvn__kub.path).rstrip('/')
            xgepn__omm = pa_fs.FileSelector(susce__qovnx, recursive=False)
            buw__jyp = fs.get_file_info(xgepn__omm)
            if buw__jyp and buw__jyp[0].path in [susce__qovnx,
                f'{susce__qovnx}/'] and int(buw__jyp[0].size or 0) == 0:
                buw__jyp = buw__jyp[1:]
            akgxv__ownh = [ctrs__yau.base_name for ctrs__yau in buw__jyp]
    except BodoError as xixs__vzbi:
        raise
    except Exception as rehw__pcgtl:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(rehw__pcgtl).__name__}: {str(rehw__pcgtl)}
{bodo_error_msg}"""
            )
    return akgxv__ownh


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    xvn__kub = urlparse(path)
    yucr__sut = xvn__kub.path
    try:
        zsgar__ryol = HadoopFileSystem.from_uri(path)
    except Exception as rehw__pcgtl:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            rehw__pcgtl))
    cqgql__chmyq = zsgar__ryol.get_file_info([yucr__sut])
    if cqgql__chmyq[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not cqgql__chmyq[0].size and cqgql__chmyq[0].type == FileType.Directory:
        return zsgar__ryol, True
    return zsgar__ryol, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    akgxv__ownh = None
    zsgar__ryol, fna__ohlap = hdfs_is_directory(path)
    if fna__ohlap:
        xvn__kub = urlparse(path)
        yucr__sut = xvn__kub.path
        xgepn__omm = FileSelector(yucr__sut, recursive=True)
        try:
            buw__jyp = zsgar__ryol.get_file_info(xgepn__omm)
        except Exception as rehw__pcgtl:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(yucr__sut, rehw__pcgtl))
        akgxv__ownh = [ctrs__yau.base_name for ctrs__yau in buw__jyp]
    return zsgar__ryol, akgxv__ownh


def abfs_is_directory(path):
    zsgar__ryol = get_hdfs_fs(path)
    try:
        cqgql__chmyq = zsgar__ryol.info(path)
    except OSError as xixs__vzbi:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if cqgql__chmyq['size'] == 0 and cqgql__chmyq['kind'].lower(
        ) == 'directory':
        return zsgar__ryol, True
    return zsgar__ryol, False


def abfs_list_dir_fnames(path):
    akgxv__ownh = None
    zsgar__ryol, fna__ohlap = abfs_is_directory(path)
    if fna__ohlap:
        xvn__kub = urlparse(path)
        yucr__sut = xvn__kub.path
        try:
            gxpzq__fdv = zsgar__ryol.ls(yucr__sut)
        except Exception as rehw__pcgtl:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(yucr__sut, rehw__pcgtl))
        akgxv__ownh = [fname[fname.rindex('/') + 1:] for fname in gxpzq__fdv]
    return zsgar__ryol, akgxv__ownh


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    xxm__nrh = urlparse(path)
    fname = path
    fs = None
    rnbdd__lbjl = 'read_json' if ftype == 'json' else 'read_csv'
    bbpb__ndjpe = (
        f'pd.{rnbdd__lbjl}(): there is no {ftype} file in directory: {fname}')
    fps__vofzh = directory_of_files_common_filter
    if xxm__nrh.scheme == 's3':
        ptw__kffvn = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        muwn__ilw = s3_list_dir_fnames(fs, path)
        susce__qovnx = (xxm__nrh.netloc + xxm__nrh.path).rstrip('/')
        fname = susce__qovnx
        if muwn__ilw:
            muwn__ilw = [(susce__qovnx + '/' + cucww__zyzyu) for
                cucww__zyzyu in sorted(filter(fps__vofzh, muwn__ilw))]
            vuqbz__rmx = [cucww__zyzyu for cucww__zyzyu in muwn__ilw if int
                (fs.get_file_info(cucww__zyzyu).size or 0) > 0]
            if len(vuqbz__rmx) == 0:
                raise BodoError(bbpb__ndjpe)
            fname = vuqbz__rmx[0]
        rwza__ndyq = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        shwpc__hcmu = fs._open(fname)
    elif xxm__nrh.scheme == 'hdfs':
        ptw__kffvn = True
        fs, muwn__ilw = hdfs_list_dir_fnames(path)
        rwza__ndyq = fs.get_file_info([xxm__nrh.path])[0].size
        if muwn__ilw:
            path = path.rstrip('/')
            muwn__ilw = [(path + '/' + cucww__zyzyu) for cucww__zyzyu in
                sorted(filter(fps__vofzh, muwn__ilw))]
            vuqbz__rmx = [cucww__zyzyu for cucww__zyzyu in muwn__ilw if fs.
                get_file_info([urlparse(cucww__zyzyu).path])[0].size > 0]
            if len(vuqbz__rmx) == 0:
                raise BodoError(bbpb__ndjpe)
            fname = vuqbz__rmx[0]
            fname = urlparse(fname).path
            rwza__ndyq = fs.get_file_info([fname])[0].size
        shwpc__hcmu = fs.open_input_file(fname)
    elif xxm__nrh.scheme in ('abfs', 'abfss'):
        ptw__kffvn = True
        fs, muwn__ilw = abfs_list_dir_fnames(path)
        rwza__ndyq = fs.info(fname)['size']
        if muwn__ilw:
            path = path.rstrip('/')
            muwn__ilw = [(path + '/' + cucww__zyzyu) for cucww__zyzyu in
                sorted(filter(fps__vofzh, muwn__ilw))]
            vuqbz__rmx = [cucww__zyzyu for cucww__zyzyu in muwn__ilw if fs.
                info(cucww__zyzyu)['size'] > 0]
            if len(vuqbz__rmx) == 0:
                raise BodoError(bbpb__ndjpe)
            fname = vuqbz__rmx[0]
            rwza__ndyq = fs.info(fname)['size']
            fname = urlparse(fname).path
        shwpc__hcmu = fs.open(fname, 'rb')
    else:
        if xxm__nrh.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {xxm__nrh.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        ptw__kffvn = False
        if os.path.isdir(path):
            gxpzq__fdv = filter(fps__vofzh, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            vuqbz__rmx = [cucww__zyzyu for cucww__zyzyu in sorted(
                gxpzq__fdv) if os.path.getsize(cucww__zyzyu) > 0]
            if len(vuqbz__rmx) == 0:
                raise BodoError(bbpb__ndjpe)
            fname = vuqbz__rmx[0]
        rwza__ndyq = os.path.getsize(fname)
        shwpc__hcmu = fname
    return ptw__kffvn, shwpc__hcmu, rwza__ndyq, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    ejmrq__jnwb = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            huh__yow, wsob__pbufy = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = huh__yow.region
        except Exception as rehw__pcgtl:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{rehw__pcgtl}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = ejmrq__jnwb.bcast(bucket_loc)
    return bucket_loc


@numba.njit()
def get_s3_bucket_region_njit(s3_filepath, parallel):
    with numba.objmode(bucket_loc='unicode_type'):
        bucket_loc = ''
        if isinstance(s3_filepath, list):
            s3_filepath = s3_filepath[0]
        if s3_filepath.startswith('s3://'):
            bucket_loc = get_s3_bucket_region(s3_filepath, parallel)
    return bucket_loc


def csv_write(path_or_buf, D, filename_prefix, is_parallel=False):
    return None


@overload(csv_write, no_unliteral=True)
def csv_write_overload(path_or_buf, D, filename_prefix, is_parallel=False):

    def impl(path_or_buf, D, filename_prefix, is_parallel=False):
        eql__fpqz = get_s3_bucket_region_njit(path_or_buf, parallel=is_parallel
            )
        wwzwe__jro, lkp__rifs = unicode_to_utf8_and_len(D)
        zxnc__vhak = 0
        if is_parallel:
            zxnc__vhak = bodo.libs.distributed_api.dist_exscan(lkp__rifs,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), wwzwe__jro, zxnc__vhak,
            lkp__rifs, is_parallel, unicode_to_utf8(eql__fpqz),
            unicode_to_utf8(filename_prefix))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl


class StorageOptionsDictType(types.Opaque):

    def __init__(self):
        super(StorageOptionsDictType, self).__init__(name=
            'StorageOptionsDictType')


storage_options_dict_type = StorageOptionsDictType()
types.storage_options_dict_type = storage_options_dict_type
register_model(StorageOptionsDictType)(models.OpaqueModel)


@unbox(StorageOptionsDictType)
def unbox_storage_options_dict_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    nqu__mjop = get_overload_constant_dict(storage_options)
    djatm__nozp = 'def impl(storage_options):\n'
    djatm__nozp += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    djatm__nozp += f'    storage_options_py = {str(nqu__mjop)}\n'
    djatm__nozp += '  return storage_options_py\n'
    pdz__wkn = {}
    exec(djatm__nozp, globals(), pdz__wkn)
    return pdz__wkn['impl']
