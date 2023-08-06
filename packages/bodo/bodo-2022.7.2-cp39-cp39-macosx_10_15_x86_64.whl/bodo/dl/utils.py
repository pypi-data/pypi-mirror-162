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
    sji__uxch = MPI.COMM_WORLD
    xekx__onbbg = sji__uxch.Get_rank()
    sic__iwhr = get_host_ranks()
    lyr__zakc = get_nodes_first_ranks()
    if xekx__onbbg in lyr__zakc:
        try:
            bgyk__zry = get_num_gpus(framework)
        except Exception as dwuau__qleyi:
            bgyk__zry = dwuau__qleyi
        epr__veu = create_subcomm_mpi4py(lyr__zakc)
        wfz__qklk = epr__veu.gather(bgyk__zry)
        if xekx__onbbg == 0:
            gpu_ranks = []
            kyvnh__bcbyf = None
            for wwnfq__vgp, xgm__mbbf in enumerate(sic__iwhr.values()):
                ozj__iujdd = wfz__qklk[wwnfq__vgp]
                if isinstance(ozj__iujdd, Exception):
                    kyvnh__bcbyf = ozj__iujdd
                    break
                if ozj__iujdd == 0:
                    continue
                bogww__uzrjl = len(xgm__mbbf) // ozj__iujdd
                for pihg__gxsh, yzmr__hauk in enumerate(xgm__mbbf):
                    if pihg__gxsh % bogww__uzrjl == 0:
                        nzpih__qypop = pihg__gxsh / bogww__uzrjl
                        if nzpih__qypop < ozj__iujdd:
                            gpu_ranks.append(yzmr__hauk)
            if kyvnh__bcbyf:
                sji__uxch.bcast(kyvnh__bcbyf)
                raise kyvnh__bcbyf
            else:
                sji__uxch.bcast(gpu_ranks)
    if xekx__onbbg != 0:
        gpu_ranks = sji__uxch.bcast(None)
        if isinstance(gpu_ranks, Exception):
            dwuau__qleyi = gpu_ranks
            raise dwuau__qleyi
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
    cue__lvxx = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        epr__veu = MPI.COMM_WORLD.Split(color=0 if cue__lvxx in gpu_ranks else
            MPI.UNDEFINED, key=cue__lvxx)
        if epr__veu != MPI.COMM_NULL:
            hvd.init(comm=epr__veu)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                qsa__fhokf = tf.config.experimental.list_physical_devices('GPU'
                    )
                for deoe__ylk in qsa__fhokf:
                    tf.config.experimental.set_memory_growth(deoe__ylk, True)
                tf.config.experimental.set_visible_devices(qsa__fhokf[hvd.
                    local_rank()], 'GPU')
    else:
        if cue__lvxx == 0:
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
        efztv__nyeuz = 17
        sji__uxch = MPI.COMM_WORLD
        xvs__rloh = MPI.Get_processor_name()
        jcnq__rgf = get_host_ranks()[xvs__rloh]
        assert_dl_initialized()
        if bodo.get_rank() == jcnq__rgf[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for xekx__onbbg in jcnq__rgf[1:]:
                sji__uxch.isend(1, dest=xekx__onbbg, tag=efztv__nyeuz)
        else:
            while True:
                cwkvp__wjn = MPI.Status()
                flnut__hict = sji__uxch.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    cwkvp__wjn)
                if flnut__hict:
                    assert cwkvp__wjn.source == jcnq__rgf[0]
                    assert cwkvp__wjn.tag == efztv__nyeuz
                    sji__uxch.recv(source=0, tag=efztv__nyeuz)
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
