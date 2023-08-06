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
            ocbo__vxnjx = self.fs.open_input_file(path)
        except:
            ocbo__vxnjx = self.fs.open_input_stream(path)
    elif mode == 'wb':
        ocbo__vxnjx = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, ocbo__vxnjx, path, mode, block_size, **kwargs)


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
    ecgwj__pcycd = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    wga__voiwu = False
    bvm__ujyfl = get_proxy_uri_from_env_vars()
    if storage_options:
        wga__voiwu = storage_options.get('anon', False)
    return S3FileSystem(anonymous=wga__voiwu, region=region,
        endpoint_override=ecgwj__pcycd, proxy_options=bvm__ujyfl)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    ecgwj__pcycd = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    wga__voiwu = False
    bvm__ujyfl = get_proxy_uri_from_env_vars()
    if storage_options:
        wga__voiwu = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=ecgwj__pcycd,
        anonymous=wga__voiwu, proxy_options=bvm__ujyfl)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    mwy__joups = urlparse(path)
    if mwy__joups.scheme in ('abfs', 'abfss'):
        ehgu__obrgd = path
        if mwy__joups.port is None:
            nxlw__gme = 0
        else:
            nxlw__gme = mwy__joups.port
        gfpo__ybwyk = None
    else:
        ehgu__obrgd = mwy__joups.hostname
        nxlw__gme = mwy__joups.port
        gfpo__ybwyk = mwy__joups.username
    try:
        fs = HdFS(host=ehgu__obrgd, port=nxlw__gme, user=gfpo__ybwyk)
    except Exception as lcolj__xcrr:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            lcolj__xcrr))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        iptvg__qbe = fs.isdir(path)
    except gcsfs.utils.HttpError as lcolj__xcrr:
        raise BodoError(
            f'{lcolj__xcrr}. Make sure your google cloud credentials are set!')
    return iptvg__qbe


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [sbs__sce.split('/')[-1] for sbs__sce in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        mwy__joups = urlparse(path)
        sbpqy__xhku = (mwy__joups.netloc + mwy__joups.path).rstrip('/')
        fmd__wosz = fs.get_file_info(sbpqy__xhku)
        if fmd__wosz.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not fmd__wosz.size and fmd__wosz.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as lcolj__xcrr:
        raise
    except BodoError as wltom__wympa:
        raise
    except Exception as lcolj__xcrr:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(lcolj__xcrr).__name__}: {str(lcolj__xcrr)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    lwy__xkl = None
    try:
        if s3_is_directory(fs, path):
            mwy__joups = urlparse(path)
            sbpqy__xhku = (mwy__joups.netloc + mwy__joups.path).rstrip('/')
            rtij__qkqq = pa_fs.FileSelector(sbpqy__xhku, recursive=False)
            xtii__fmmw = fs.get_file_info(rtij__qkqq)
            if xtii__fmmw and xtii__fmmw[0].path in [sbpqy__xhku,
                f'{sbpqy__xhku}/'] and int(xtii__fmmw[0].size or 0) == 0:
                xtii__fmmw = xtii__fmmw[1:]
            lwy__xkl = [vair__ljaah.base_name for vair__ljaah in xtii__fmmw]
    except BodoError as wltom__wympa:
        raise
    except Exception as lcolj__xcrr:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(lcolj__xcrr).__name__}: {str(lcolj__xcrr)}
{bodo_error_msg}"""
            )
    return lwy__xkl


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    mwy__joups = urlparse(path)
    qortj__wyxt = mwy__joups.path
    try:
        aib__lko = HadoopFileSystem.from_uri(path)
    except Exception as lcolj__xcrr:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            lcolj__xcrr))
    uig__nlq = aib__lko.get_file_info([qortj__wyxt])
    if uig__nlq[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not uig__nlq[0].size and uig__nlq[0].type == FileType.Directory:
        return aib__lko, True
    return aib__lko, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    lwy__xkl = None
    aib__lko, iptvg__qbe = hdfs_is_directory(path)
    if iptvg__qbe:
        mwy__joups = urlparse(path)
        qortj__wyxt = mwy__joups.path
        rtij__qkqq = FileSelector(qortj__wyxt, recursive=True)
        try:
            xtii__fmmw = aib__lko.get_file_info(rtij__qkqq)
        except Exception as lcolj__xcrr:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(qortj__wyxt, lcolj__xcrr))
        lwy__xkl = [vair__ljaah.base_name for vair__ljaah in xtii__fmmw]
    return aib__lko, lwy__xkl


def abfs_is_directory(path):
    aib__lko = get_hdfs_fs(path)
    try:
        uig__nlq = aib__lko.info(path)
    except OSError as wltom__wympa:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if uig__nlq['size'] == 0 and uig__nlq['kind'].lower() == 'directory':
        return aib__lko, True
    return aib__lko, False


def abfs_list_dir_fnames(path):
    lwy__xkl = None
    aib__lko, iptvg__qbe = abfs_is_directory(path)
    if iptvg__qbe:
        mwy__joups = urlparse(path)
        qortj__wyxt = mwy__joups.path
        try:
            bkese__zvhx = aib__lko.ls(qortj__wyxt)
        except Exception as lcolj__xcrr:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(qortj__wyxt, lcolj__xcrr))
        lwy__xkl = [fname[fname.rindex('/') + 1:] for fname in bkese__zvhx]
    return aib__lko, lwy__xkl


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    wrn__hjff = urlparse(path)
    fname = path
    fs = None
    szwj__pds = 'read_json' if ftype == 'json' else 'read_csv'
    raqal__gktwf = (
        f'pd.{szwj__pds}(): there is no {ftype} file in directory: {fname}')
    cnhb__kcc = directory_of_files_common_filter
    if wrn__hjff.scheme == 's3':
        iamb__dtrvo = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        gteom__ynsz = s3_list_dir_fnames(fs, path)
        sbpqy__xhku = (wrn__hjff.netloc + wrn__hjff.path).rstrip('/')
        fname = sbpqy__xhku
        if gteom__ynsz:
            gteom__ynsz = [(sbpqy__xhku + '/' + sbs__sce) for sbs__sce in
                sorted(filter(cnhb__kcc, gteom__ynsz))]
            pwf__muk = [sbs__sce for sbs__sce in gteom__ynsz if int(fs.
                get_file_info(sbs__sce).size or 0) > 0]
            if len(pwf__muk) == 0:
                raise BodoError(raqal__gktwf)
            fname = pwf__muk[0]
        qxkps__hhsnt = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        wpua__bzplm = fs._open(fname)
    elif wrn__hjff.scheme == 'hdfs':
        iamb__dtrvo = True
        fs, gteom__ynsz = hdfs_list_dir_fnames(path)
        qxkps__hhsnt = fs.get_file_info([wrn__hjff.path])[0].size
        if gteom__ynsz:
            path = path.rstrip('/')
            gteom__ynsz = [(path + '/' + sbs__sce) for sbs__sce in sorted(
                filter(cnhb__kcc, gteom__ynsz))]
            pwf__muk = [sbs__sce for sbs__sce in gteom__ynsz if fs.
                get_file_info([urlparse(sbs__sce).path])[0].size > 0]
            if len(pwf__muk) == 0:
                raise BodoError(raqal__gktwf)
            fname = pwf__muk[0]
            fname = urlparse(fname).path
            qxkps__hhsnt = fs.get_file_info([fname])[0].size
        wpua__bzplm = fs.open_input_file(fname)
    elif wrn__hjff.scheme in ('abfs', 'abfss'):
        iamb__dtrvo = True
        fs, gteom__ynsz = abfs_list_dir_fnames(path)
        qxkps__hhsnt = fs.info(fname)['size']
        if gteom__ynsz:
            path = path.rstrip('/')
            gteom__ynsz = [(path + '/' + sbs__sce) for sbs__sce in sorted(
                filter(cnhb__kcc, gteom__ynsz))]
            pwf__muk = [sbs__sce for sbs__sce in gteom__ynsz if fs.info(
                sbs__sce)['size'] > 0]
            if len(pwf__muk) == 0:
                raise BodoError(raqal__gktwf)
            fname = pwf__muk[0]
            qxkps__hhsnt = fs.info(fname)['size']
            fname = urlparse(fname).path
        wpua__bzplm = fs.open(fname, 'rb')
    else:
        if wrn__hjff.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {wrn__hjff.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        iamb__dtrvo = False
        if os.path.isdir(path):
            bkese__zvhx = filter(cnhb__kcc, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            pwf__muk = [sbs__sce for sbs__sce in sorted(bkese__zvhx) if os.
                path.getsize(sbs__sce) > 0]
            if len(pwf__muk) == 0:
                raise BodoError(raqal__gktwf)
            fname = pwf__muk[0]
        qxkps__hhsnt = os.path.getsize(fname)
        wpua__bzplm = fname
    return iamb__dtrvo, wpua__bzplm, qxkps__hhsnt, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    jveff__faj = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            bhut__izyh, duspv__hvz = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = bhut__izyh.region
        except Exception as lcolj__xcrr:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{lcolj__xcrr}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = jveff__faj.bcast(bucket_loc)
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
        jble__nxmud = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        hvdox__brr, kjo__bqmbc = unicode_to_utf8_and_len(D)
        ofkr__gts = 0
        if is_parallel:
            ofkr__gts = bodo.libs.distributed_api.dist_exscan(kjo__bqmbc,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), hvdox__brr, ofkr__gts,
            kjo__bqmbc, is_parallel, unicode_to_utf8(jble__nxmud),
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
    wedu__jjgka = get_overload_constant_dict(storage_options)
    mmo__ledgu = 'def impl(storage_options):\n'
    mmo__ledgu += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    mmo__ledgu += f'    storage_options_py = {str(wedu__jjgka)}\n'
    mmo__ledgu += '  return storage_options_py\n'
    bcx__cuer = {}
    exec(mmo__ledgu, globals(), bcx__cuer)
    return bcx__cuer['impl']
