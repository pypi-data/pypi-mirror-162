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
            xxida__izqr = self.fs.open_input_file(path)
        except:
            xxida__izqr = self.fs.open_input_stream(path)
    elif mode == 'wb':
        xxida__izqr = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, xxida__izqr, path, mode, block_size, **kwargs)


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
    fku__lmvnh = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    hkr__fcl = False
    fdv__iut = get_proxy_uri_from_env_vars()
    if storage_options:
        hkr__fcl = storage_options.get('anon', False)
    return S3FileSystem(anonymous=hkr__fcl, region=region,
        endpoint_override=fku__lmvnh, proxy_options=fdv__iut)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    fku__lmvnh = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    hkr__fcl = False
    fdv__iut = get_proxy_uri_from_env_vars()
    if storage_options:
        hkr__fcl = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=fku__lmvnh,
        anonymous=hkr__fcl, proxy_options=fdv__iut)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    gixoo__zfmxj = urlparse(path)
    if gixoo__zfmxj.scheme in ('abfs', 'abfss'):
        tgeii__hhxus = path
        if gixoo__zfmxj.port is None:
            vjnkd__dafs = 0
        else:
            vjnkd__dafs = gixoo__zfmxj.port
        tqfqv__ahi = None
    else:
        tgeii__hhxus = gixoo__zfmxj.hostname
        vjnkd__dafs = gixoo__zfmxj.port
        tqfqv__ahi = gixoo__zfmxj.username
    try:
        fs = HdFS(host=tgeii__hhxus, port=vjnkd__dafs, user=tqfqv__ahi)
    except Exception as yrrf__swiv:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            yrrf__swiv))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        lia__aixmq = fs.isdir(path)
    except gcsfs.utils.HttpError as yrrf__swiv:
        raise BodoError(
            f'{yrrf__swiv}. Make sure your google cloud credentials are set!')
    return lia__aixmq


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [jgy__bljem.split('/')[-1] for jgy__bljem in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        gixoo__zfmxj = urlparse(path)
        mglki__aaquj = (gixoo__zfmxj.netloc + gixoo__zfmxj.path).rstrip('/')
        pjg__dvo = fs.get_file_info(mglki__aaquj)
        if pjg__dvo.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not pjg__dvo.size and pjg__dvo.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as yrrf__swiv:
        raise
    except BodoError as vsr__idowy:
        raise
    except Exception as yrrf__swiv:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(yrrf__swiv).__name__}: {str(yrrf__swiv)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    gftt__iykv = None
    try:
        if s3_is_directory(fs, path):
            gixoo__zfmxj = urlparse(path)
            mglki__aaquj = (gixoo__zfmxj.netloc + gixoo__zfmxj.path).rstrip('/'
                )
            aoa__ypc = pa_fs.FileSelector(mglki__aaquj, recursive=False)
            udwl__pec = fs.get_file_info(aoa__ypc)
            if udwl__pec and udwl__pec[0].path in [mglki__aaquj,
                f'{mglki__aaquj}/'] and int(udwl__pec[0].size or 0) == 0:
                udwl__pec = udwl__pec[1:]
            gftt__iykv = [orgpu__ohrul.base_name for orgpu__ohrul in udwl__pec]
    except BodoError as vsr__idowy:
        raise
    except Exception as yrrf__swiv:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(yrrf__swiv).__name__}: {str(yrrf__swiv)}
{bodo_error_msg}"""
            )
    return gftt__iykv


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    gixoo__zfmxj = urlparse(path)
    qsm__aas = gixoo__zfmxj.path
    try:
        oatrj__jvzj = HadoopFileSystem.from_uri(path)
    except Exception as yrrf__swiv:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            yrrf__swiv))
    jyat__fwged = oatrj__jvzj.get_file_info([qsm__aas])
    if jyat__fwged[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not jyat__fwged[0].size and jyat__fwged[0].type == FileType.Directory:
        return oatrj__jvzj, True
    return oatrj__jvzj, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    gftt__iykv = None
    oatrj__jvzj, lia__aixmq = hdfs_is_directory(path)
    if lia__aixmq:
        gixoo__zfmxj = urlparse(path)
        qsm__aas = gixoo__zfmxj.path
        aoa__ypc = FileSelector(qsm__aas, recursive=True)
        try:
            udwl__pec = oatrj__jvzj.get_file_info(aoa__ypc)
        except Exception as yrrf__swiv:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(qsm__aas, yrrf__swiv))
        gftt__iykv = [orgpu__ohrul.base_name for orgpu__ohrul in udwl__pec]
    return oatrj__jvzj, gftt__iykv


def abfs_is_directory(path):
    oatrj__jvzj = get_hdfs_fs(path)
    try:
        jyat__fwged = oatrj__jvzj.info(path)
    except OSError as vsr__idowy:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if jyat__fwged['size'] == 0 and jyat__fwged['kind'].lower() == 'directory':
        return oatrj__jvzj, True
    return oatrj__jvzj, False


def abfs_list_dir_fnames(path):
    gftt__iykv = None
    oatrj__jvzj, lia__aixmq = abfs_is_directory(path)
    if lia__aixmq:
        gixoo__zfmxj = urlparse(path)
        qsm__aas = gixoo__zfmxj.path
        try:
            vwem__cnm = oatrj__jvzj.ls(qsm__aas)
        except Exception as yrrf__swiv:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(qsm__aas, yrrf__swiv))
        gftt__iykv = [fname[fname.rindex('/') + 1:] for fname in vwem__cnm]
    return oatrj__jvzj, gftt__iykv


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    ggy__ihiq = urlparse(path)
    fname = path
    fs = None
    zqx__ans = 'read_json' if ftype == 'json' else 'read_csv'
    nrbrm__vgenf = (
        f'pd.{zqx__ans}(): there is no {ftype} file in directory: {fname}')
    wddys__diknk = directory_of_files_common_filter
    if ggy__ihiq.scheme == 's3':
        tih__iqcri = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        aae__txfx = s3_list_dir_fnames(fs, path)
        mglki__aaquj = (ggy__ihiq.netloc + ggy__ihiq.path).rstrip('/')
        fname = mglki__aaquj
        if aae__txfx:
            aae__txfx = [(mglki__aaquj + '/' + jgy__bljem) for jgy__bljem in
                sorted(filter(wddys__diknk, aae__txfx))]
            rod__jef = [jgy__bljem for jgy__bljem in aae__txfx if int(fs.
                get_file_info(jgy__bljem).size or 0) > 0]
            if len(rod__jef) == 0:
                raise BodoError(nrbrm__vgenf)
            fname = rod__jef[0]
        dhfpt__qmps = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        gmd__cpstc = fs._open(fname)
    elif ggy__ihiq.scheme == 'hdfs':
        tih__iqcri = True
        fs, aae__txfx = hdfs_list_dir_fnames(path)
        dhfpt__qmps = fs.get_file_info([ggy__ihiq.path])[0].size
        if aae__txfx:
            path = path.rstrip('/')
            aae__txfx = [(path + '/' + jgy__bljem) for jgy__bljem in sorted
                (filter(wddys__diknk, aae__txfx))]
            rod__jef = [jgy__bljem for jgy__bljem in aae__txfx if fs.
                get_file_info([urlparse(jgy__bljem).path])[0].size > 0]
            if len(rod__jef) == 0:
                raise BodoError(nrbrm__vgenf)
            fname = rod__jef[0]
            fname = urlparse(fname).path
            dhfpt__qmps = fs.get_file_info([fname])[0].size
        gmd__cpstc = fs.open_input_file(fname)
    elif ggy__ihiq.scheme in ('abfs', 'abfss'):
        tih__iqcri = True
        fs, aae__txfx = abfs_list_dir_fnames(path)
        dhfpt__qmps = fs.info(fname)['size']
        if aae__txfx:
            path = path.rstrip('/')
            aae__txfx = [(path + '/' + jgy__bljem) for jgy__bljem in sorted
                (filter(wddys__diknk, aae__txfx))]
            rod__jef = [jgy__bljem for jgy__bljem in aae__txfx if fs.info(
                jgy__bljem)['size'] > 0]
            if len(rod__jef) == 0:
                raise BodoError(nrbrm__vgenf)
            fname = rod__jef[0]
            dhfpt__qmps = fs.info(fname)['size']
            fname = urlparse(fname).path
        gmd__cpstc = fs.open(fname, 'rb')
    else:
        if ggy__ihiq.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {ggy__ihiq.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        tih__iqcri = False
        if os.path.isdir(path):
            vwem__cnm = filter(wddys__diknk, glob.glob(os.path.join(os.path
                .abspath(path), '*')))
            rod__jef = [jgy__bljem for jgy__bljem in sorted(vwem__cnm) if 
                os.path.getsize(jgy__bljem) > 0]
            if len(rod__jef) == 0:
                raise BodoError(nrbrm__vgenf)
            fname = rod__jef[0]
        dhfpt__qmps = os.path.getsize(fname)
        gmd__cpstc = fname
    return tih__iqcri, gmd__cpstc, dhfpt__qmps, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    lfcvs__buh = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            gwdzr__syvfr, mukhl__ven = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = gwdzr__syvfr.region
        except Exception as yrrf__swiv:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{yrrf__swiv}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = lfcvs__buh.bcast(bucket_loc)
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
        qoz__oirp = get_s3_bucket_region_njit(path_or_buf, parallel=is_parallel
            )
        gnidi__mle, skhzm__wbxl = unicode_to_utf8_and_len(D)
        syevj__loom = 0
        if is_parallel:
            syevj__loom = bodo.libs.distributed_api.dist_exscan(skhzm__wbxl,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), gnidi__mle, syevj__loom,
            skhzm__wbxl, is_parallel, unicode_to_utf8(qoz__oirp),
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
    dudty__crgmd = get_overload_constant_dict(storage_options)
    trjdr__igfic = 'def impl(storage_options):\n'
    trjdr__igfic += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    trjdr__igfic += f'    storage_options_py = {str(dudty__crgmd)}\n'
    trjdr__igfic += '  return storage_options_py\n'
    qvwu__ubkx = {}
    exec(trjdr__igfic, globals(), qvwu__ubkx)
    return qvwu__ubkx['impl']
