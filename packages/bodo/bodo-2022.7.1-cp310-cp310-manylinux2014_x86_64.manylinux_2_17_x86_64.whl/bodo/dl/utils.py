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
    pto__kgxb = MPI.COMM_WORLD
    gvvyo__ltsa = pto__kgxb.Get_rank()
    ugx__ced = get_host_ranks()
    agv__yivr = get_nodes_first_ranks()
    if gvvyo__ltsa in agv__yivr:
        try:
            skio__dafbw = get_num_gpus(framework)
        except Exception as rgrp__wzlw:
            skio__dafbw = rgrp__wzlw
        ryr__dmbyi = create_subcomm_mpi4py(agv__yivr)
        wssou__hymsv = ryr__dmbyi.gather(skio__dafbw)
        if gvvyo__ltsa == 0:
            gpu_ranks = []
            kqwb__fwyel = None
            for gfs__egvcp, alhq__zklq in enumerate(ugx__ced.values()):
                yjcbn__nuh = wssou__hymsv[gfs__egvcp]
                if isinstance(yjcbn__nuh, Exception):
                    kqwb__fwyel = yjcbn__nuh
                    break
                if yjcbn__nuh == 0:
                    continue
                ryqwo__hdsf = len(alhq__zklq) // yjcbn__nuh
                for zgyr__lyffr, xsgc__lrs in enumerate(alhq__zklq):
                    if zgyr__lyffr % ryqwo__hdsf == 0:
                        amzs__rfdk = zgyr__lyffr / ryqwo__hdsf
                        if amzs__rfdk < yjcbn__nuh:
                            gpu_ranks.append(xsgc__lrs)
            if kqwb__fwyel:
                pto__kgxb.bcast(kqwb__fwyel)
                raise kqwb__fwyel
            else:
                pto__kgxb.bcast(gpu_ranks)
    if gvvyo__ltsa != 0:
        gpu_ranks = pto__kgxb.bcast(None)
        if isinstance(gpu_ranks, Exception):
            rgrp__wzlw = gpu_ranks
            raise rgrp__wzlw
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
    zkt__mhvfs = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        ryr__dmbyi = MPI.COMM_WORLD.Split(color=0 if zkt__mhvfs in
            gpu_ranks else MPI.UNDEFINED, key=zkt__mhvfs)
        if ryr__dmbyi != MPI.COMM_NULL:
            hvd.init(comm=ryr__dmbyi)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                ehra__fld = tf.config.experimental.list_physical_devices('GPU')
                for hlmx__ope in ehra__fld:
                    tf.config.experimental.set_memory_growth(hlmx__ope, True)
                tf.config.experimental.set_visible_devices(ehra__fld[hvd.
                    local_rank()], 'GPU')
    else:
        if zkt__mhvfs == 0:
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
        rwk__xerm = 17
        pto__kgxb = MPI.COMM_WORLD
        murbk__zyk = MPI.Get_processor_name()
        uuau__sdk = get_host_ranks()[murbk__zyk]
        assert_dl_initialized()
        if bodo.get_rank() == uuau__sdk[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for gvvyo__ltsa in uuau__sdk[1:]:
                pto__kgxb.isend(1, dest=gvvyo__ltsa, tag=rwk__xerm)
        else:
            while True:
                vpeyv__dhnqz = MPI.Status()
                fzu__nnkk = pto__kgxb.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    vpeyv__dhnqz)
                if fzu__nnkk:
                    assert vpeyv__dhnqz.source == uuau__sdk[0]
                    assert vpeyv__dhnqz.tag == rwk__xerm
                    pto__kgxb.recv(source=0, tag=rwk__xerm)
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
