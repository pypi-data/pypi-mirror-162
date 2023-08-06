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
            vfs__bjleb = self.fs.open_input_file(path)
        except:
            vfs__bjleb = self.fs.open_input_stream(path)
    elif mode == 'wb':
        vfs__bjleb = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, vfs__bjleb, path, mode, block_size, **kwargs)


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
    jwgcz__zef = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    uus__mxq = False
    rvjjd__hflsm = get_proxy_uri_from_env_vars()
    if storage_options:
        uus__mxq = storage_options.get('anon', False)
    return S3FileSystem(anonymous=uus__mxq, region=region,
        endpoint_override=jwgcz__zef, proxy_options=rvjjd__hflsm)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    jwgcz__zef = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    uus__mxq = False
    rvjjd__hflsm = get_proxy_uri_from_env_vars()
    if storage_options:
        uus__mxq = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=jwgcz__zef,
        anonymous=uus__mxq, proxy_options=rvjjd__hflsm)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    xqubd__saq = urlparse(path)
    if xqubd__saq.scheme in ('abfs', 'abfss'):
        msvp__dfq = path
        if xqubd__saq.port is None:
            gpusc__qbcb = 0
        else:
            gpusc__qbcb = xqubd__saq.port
        vyv__gve = None
    else:
        msvp__dfq = xqubd__saq.hostname
        gpusc__qbcb = xqubd__saq.port
        vyv__gve = xqubd__saq.username
    try:
        fs = HdFS(host=msvp__dfq, port=gpusc__qbcb, user=vyv__gve)
    except Exception as lpmkx__ilol:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            lpmkx__ilol))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        rdo__tnoi = fs.isdir(path)
    except gcsfs.utils.HttpError as lpmkx__ilol:
        raise BodoError(
            f'{lpmkx__ilol}. Make sure your google cloud credentials are set!')
    return rdo__tnoi


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [rwvg__zad.split('/')[-1] for rwvg__zad in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        xqubd__saq = urlparse(path)
        gsd__xik = (xqubd__saq.netloc + xqubd__saq.path).rstrip('/')
        ybto__wbeez = fs.get_file_info(gsd__xik)
        if ybto__wbeez.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not ybto__wbeez.size and ybto__wbeez.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as lpmkx__ilol:
        raise
    except BodoError as zzj__ykuo:
        raise
    except Exception as lpmkx__ilol:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(lpmkx__ilol).__name__}: {str(lpmkx__ilol)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    awmr__sxyho = None
    try:
        if s3_is_directory(fs, path):
            xqubd__saq = urlparse(path)
            gsd__xik = (xqubd__saq.netloc + xqubd__saq.path).rstrip('/')
            sqpa__uduqd = pa_fs.FileSelector(gsd__xik, recursive=False)
            tgrth__euyz = fs.get_file_info(sqpa__uduqd)
            if tgrth__euyz and tgrth__euyz[0].path in [gsd__xik, f'{gsd__xik}/'
                ] and int(tgrth__euyz[0].size or 0) == 0:
                tgrth__euyz = tgrth__euyz[1:]
            awmr__sxyho = [uhiz__jyy.base_name for uhiz__jyy in tgrth__euyz]
    except BodoError as zzj__ykuo:
        raise
    except Exception as lpmkx__ilol:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(lpmkx__ilol).__name__}: {str(lpmkx__ilol)}
{bodo_error_msg}"""
            )
    return awmr__sxyho


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    xqubd__saq = urlparse(path)
    hke__vyo = xqubd__saq.path
    try:
        xqyr__sjm = HadoopFileSystem.from_uri(path)
    except Exception as lpmkx__ilol:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            lpmkx__ilol))
    vziu__cde = xqyr__sjm.get_file_info([hke__vyo])
    if vziu__cde[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not vziu__cde[0].size and vziu__cde[0].type == FileType.Directory:
        return xqyr__sjm, True
    return xqyr__sjm, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    awmr__sxyho = None
    xqyr__sjm, rdo__tnoi = hdfs_is_directory(path)
    if rdo__tnoi:
        xqubd__saq = urlparse(path)
        hke__vyo = xqubd__saq.path
        sqpa__uduqd = FileSelector(hke__vyo, recursive=True)
        try:
            tgrth__euyz = xqyr__sjm.get_file_info(sqpa__uduqd)
        except Exception as lpmkx__ilol:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(hke__vyo, lpmkx__ilol))
        awmr__sxyho = [uhiz__jyy.base_name for uhiz__jyy in tgrth__euyz]
    return xqyr__sjm, awmr__sxyho


def abfs_is_directory(path):
    xqyr__sjm = get_hdfs_fs(path)
    try:
        vziu__cde = xqyr__sjm.info(path)
    except OSError as zzj__ykuo:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if vziu__cde['size'] == 0 and vziu__cde['kind'].lower() == 'directory':
        return xqyr__sjm, True
    return xqyr__sjm, False


def abfs_list_dir_fnames(path):
    awmr__sxyho = None
    xqyr__sjm, rdo__tnoi = abfs_is_directory(path)
    if rdo__tnoi:
        xqubd__saq = urlparse(path)
        hke__vyo = xqubd__saq.path
        try:
            hmr__cdx = xqyr__sjm.ls(hke__vyo)
        except Exception as lpmkx__ilol:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(hke__vyo, lpmkx__ilol))
        awmr__sxyho = [fname[fname.rindex('/') + 1:] for fname in hmr__cdx]
    return xqyr__sjm, awmr__sxyho


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    ngx__wifr = urlparse(path)
    fname = path
    fs = None
    rujfs__bocdj = 'read_json' if ftype == 'json' else 'read_csv'
    qmc__squj = (
        f'pd.{rujfs__bocdj}(): there is no {ftype} file in directory: {fname}')
    ooyx__alh = directory_of_files_common_filter
    if ngx__wifr.scheme == 's3':
        dpq__hae = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        vsbf__uxusv = s3_list_dir_fnames(fs, path)
        gsd__xik = (ngx__wifr.netloc + ngx__wifr.path).rstrip('/')
        fname = gsd__xik
        if vsbf__uxusv:
            vsbf__uxusv = [(gsd__xik + '/' + rwvg__zad) for rwvg__zad in
                sorted(filter(ooyx__alh, vsbf__uxusv))]
            btzu__wagag = [rwvg__zad for rwvg__zad in vsbf__uxusv if int(fs
                .get_file_info(rwvg__zad).size or 0) > 0]
            if len(btzu__wagag) == 0:
                raise BodoError(qmc__squj)
            fname = btzu__wagag[0]
        hlb__tjl = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        ehdp__dcs = fs._open(fname)
    elif ngx__wifr.scheme == 'hdfs':
        dpq__hae = True
        fs, vsbf__uxusv = hdfs_list_dir_fnames(path)
        hlb__tjl = fs.get_file_info([ngx__wifr.path])[0].size
        if vsbf__uxusv:
            path = path.rstrip('/')
            vsbf__uxusv = [(path + '/' + rwvg__zad) for rwvg__zad in sorted
                (filter(ooyx__alh, vsbf__uxusv))]
            btzu__wagag = [rwvg__zad for rwvg__zad in vsbf__uxusv if fs.
                get_file_info([urlparse(rwvg__zad).path])[0].size > 0]
            if len(btzu__wagag) == 0:
                raise BodoError(qmc__squj)
            fname = btzu__wagag[0]
            fname = urlparse(fname).path
            hlb__tjl = fs.get_file_info([fname])[0].size
        ehdp__dcs = fs.open_input_file(fname)
    elif ngx__wifr.scheme in ('abfs', 'abfss'):
        dpq__hae = True
        fs, vsbf__uxusv = abfs_list_dir_fnames(path)
        hlb__tjl = fs.info(fname)['size']
        if vsbf__uxusv:
            path = path.rstrip('/')
            vsbf__uxusv = [(path + '/' + rwvg__zad) for rwvg__zad in sorted
                (filter(ooyx__alh, vsbf__uxusv))]
            btzu__wagag = [rwvg__zad for rwvg__zad in vsbf__uxusv if fs.
                info(rwvg__zad)['size'] > 0]
            if len(btzu__wagag) == 0:
                raise BodoError(qmc__squj)
            fname = btzu__wagag[0]
            hlb__tjl = fs.info(fname)['size']
            fname = urlparse(fname).path
        ehdp__dcs = fs.open(fname, 'rb')
    else:
        if ngx__wifr.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {ngx__wifr.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        dpq__hae = False
        if os.path.isdir(path):
            hmr__cdx = filter(ooyx__alh, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            btzu__wagag = [rwvg__zad for rwvg__zad in sorted(hmr__cdx) if 
                os.path.getsize(rwvg__zad) > 0]
            if len(btzu__wagag) == 0:
                raise BodoError(qmc__squj)
            fname = btzu__wagag[0]
        hlb__tjl = os.path.getsize(fname)
        ehdp__dcs = fname
    return dpq__hae, ehdp__dcs, hlb__tjl, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    srq__pziu = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            iobn__ryc, dvzu__ovt = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = iobn__ryc.region
        except Exception as lpmkx__ilol:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{lpmkx__ilol}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = srq__pziu.bcast(bucket_loc)
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
        mcajl__deoh = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        wbdb__heuu, gyk__sevwg = unicode_to_utf8_and_len(D)
        gaan__nkrvd = 0
        if is_parallel:
            gaan__nkrvd = bodo.libs.distributed_api.dist_exscan(gyk__sevwg,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), wbdb__heuu, gaan__nkrvd,
            gyk__sevwg, is_parallel, unicode_to_utf8(mcajl__deoh),
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
    edamc__wza = get_overload_constant_dict(storage_options)
    tpclh__kczk = 'def impl(storage_options):\n'
    tpclh__kczk += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    tpclh__kczk += f'    storage_options_py = {str(edamc__wza)}\n'
    tpclh__kczk += '  return storage_options_py\n'
    xxgp__ierul = {}
    exec(tpclh__kczk, globals(), xxgp__ierul)
    return xxgp__ierul['impl']
