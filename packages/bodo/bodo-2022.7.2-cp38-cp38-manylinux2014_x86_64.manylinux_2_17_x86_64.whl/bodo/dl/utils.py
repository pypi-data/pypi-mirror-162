"""Support distributed deep learning with Horovod
"""
import time
import numba
import numpy as np
from mpi4py import MPI
import bodo
from bodo.libs.distributed_api import create_subcomm_mpi4py, get_host_ranks, get_nodes_first_ranks
dl_status = None


def assert_dl_initialized():
    assert dl_status is not None, 'Horovod has not been initialized. Call bodo.dl.start() first'


class DLStatus(object):

    def __init__(self, framework, gpu_ranks):
        self.framework = framework
        self.gpu_ranks = gpu_ranks


def get_num_gpus(framework):
    if framework == 'torch':
        import torch
        return torch.cuda.device_count()
    elif framework == 'tensorflow':
        import tensorflow as tf
        return len(tf.config.experimental.list_physical_devices('GPU'))
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))


def get_gpu_ranks(framework):
    lpn__xruvf = MPI.COMM_WORLD
    nda__xqus = lpn__xruvf.Get_rank()
    uhkub__odr = get_host_ranks()
    qlq__fzpn = get_nodes_first_ranks()
    if nda__xqus in qlq__fzpn:
        try:
            oyx__qefhs = get_num_gpus(framework)
        except Exception as ixb__swt:
            oyx__qefhs = ixb__swt
        fysn__bqhh = create_subcomm_mpi4py(qlq__fzpn)
        ypgl__avnr = fysn__bqhh.gather(oyx__qefhs)
        if nda__xqus == 0:
            gpu_ranks = []
            gcm__bae = None
            for yzsz__qwhj, nrglt__mhr in enumerate(uhkub__odr.values()):
                tdm__olod = ypgl__avnr[yzsz__qwhj]
                if isinstance(tdm__olod, Exception):
                    gcm__bae = tdm__olod
                    break
                if tdm__olod == 0:
                    continue
                csyjt__ogfrb = len(nrglt__mhr) // tdm__olod
                for ksbp__gmf, pjol__rtowi in enumerate(nrglt__mhr):
                    if ksbp__gmf % csyjt__ogfrb == 0:
                        ukf__dugrn = ksbp__gmf / csyjt__ogfrb
                        if ukf__dugrn < tdm__olod:
                            gpu_ranks.append(pjol__rtowi)
            if gcm__bae:
                lpn__xruvf.bcast(gcm__bae)
                raise gcm__bae
            else:
                lpn__xruvf.bcast(gpu_ranks)
    if nda__xqus != 0:
        gpu_ranks = lpn__xruvf.bcast(None)
        if isinstance(gpu_ranks, Exception):
            ixb__swt = gpu_ranks
            raise ixb__swt
    return gpu_ranks


def is_cuda_available():
    assert_dl_initialized()
    return len(dl_status.gpu_ranks) > 0


def initialize_horovod(framework):
    global dl_status
    if dl_status is not None:
        assert dl_status.framework == framework, 'Attempted to initialize Horovod with different DL frameworks'
        return np.array(dl_status.gpu_ranks, dtype=np.int32)
    gpu_ranks = get_gpu_ranks(framework)
    if framework == 'torch':
        import horovod.torch as hvd
        import torch
        torch.set_num_threads(1)
    elif framework == 'tensorflow':
        import horovod.tensorflow as hvd
        import tensorflow as tf
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))
    eng__scw = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        fysn__bqhh = MPI.COMM_WORLD.Split(color=0 if eng__scw in gpu_ranks else
            MPI.UNDEFINED, key=eng__scw)
        if fysn__bqhh != MPI.COMM_NULL:
            hvd.init(comm=fysn__bqhh)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                baafe__dek = tf.config.experimental.list_physical_devices('GPU'
                    )
                for kmi__jrbb in baafe__dek:
                    tf.config.experimental.set_memory_growth(kmi__jrbb, True)
                tf.config.experimental.set_visible_devices(baafe__dek[hvd.
                    local_rank()], 'GPU')
    else:
        if eng__scw == 0:
            print('[BODO-DL]: No GPUs found in cluster. Using CPUs')
        hvd.init()
    dl_status = DLStatus(framework, np.array(gpu_ranks, dtype=np.int32))


@numba.njit
def start(framework):
    with numba.objmode:
        initialize_horovod(framework)


@numba.njit
def end():
    with numba.objmode:
        end_py()


def end_py():
    if is_cuda_available():
        azwb__jucv = 17
        lpn__xruvf = MPI.COMM_WORLD
        dgqd__qqx = MPI.Get_processor_name()
        kdd__fszo = get_host_ranks()[dgqd__qqx]
        assert_dl_initialized()
        if bodo.get_rank() == kdd__fszo[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for nda__xqus in kdd__fszo[1:]:
                lpn__xruvf.isend(1, dest=nda__xqus, tag=azwb__jucv)
        else:
            while True:
                kobr__pwny = MPI.Status()
                thgnz__hveoy = lpn__xruvf.Iprobe(MPI.ANY_SOURCE, MPI.
                    ANY_TAG, kobr__pwny)
                if thgnz__hveoy:
                    assert kobr__pwny.source == kdd__fszo[0]
                    assert kobr__pwny.tag == azwb__jucv
                    lpn__xruvf.recv(source=0, tag=azwb__jucv)
                    break
                time.sleep(1.0)
    else:
        bodo.barrier()


def _prepare_data_get_gpu_ranks():
    assert_dl_initialized()
    return dl_status.gpu_ranks


@numba.njit
def prepare_data(data):
    with numba.objmode(gpu_ranks='int32[:]'):
        gpu_ranks = _prepare_data_get_gpu_ranks()
    if len(gpu_ranks) > 0:
        data = bodo.rebalance(data, dests=list(gpu_ranks), parallel=True)
    else:
        data = bodo.rebalance(data, parallel=True)
    return data
