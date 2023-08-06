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
    dgjt__kxz = MPI.COMM_WORLD
    gdtt__zum = dgjt__kxz.Get_rank()
    oas__sfy = get_host_ranks()
    adrtd__orncg = get_nodes_first_ranks()
    if gdtt__zum in adrtd__orncg:
        try:
            hoii__owaw = get_num_gpus(framework)
        except Exception as dsiji__ihb:
            hoii__owaw = dsiji__ihb
        kkmx__zoj = create_subcomm_mpi4py(adrtd__orncg)
        pet__mazq = kkmx__zoj.gather(hoii__owaw)
        if gdtt__zum == 0:
            gpu_ranks = []
            gxcen__obblg = None
            for pdol__bopi, tsoyd__ugeq in enumerate(oas__sfy.values()):
                cczrk__ijlq = pet__mazq[pdol__bopi]
                if isinstance(cczrk__ijlq, Exception):
                    gxcen__obblg = cczrk__ijlq
                    break
                if cczrk__ijlq == 0:
                    continue
                vtxw__wrw = len(tsoyd__ugeq) // cczrk__ijlq
                for jfj__mtud, wzgg__inbu in enumerate(tsoyd__ugeq):
                    if jfj__mtud % vtxw__wrw == 0:
                        ktqj__ttly = jfj__mtud / vtxw__wrw
                        if ktqj__ttly < cczrk__ijlq:
                            gpu_ranks.append(wzgg__inbu)
            if gxcen__obblg:
                dgjt__kxz.bcast(gxcen__obblg)
                raise gxcen__obblg
            else:
                dgjt__kxz.bcast(gpu_ranks)
    if gdtt__zum != 0:
        gpu_ranks = dgjt__kxz.bcast(None)
        if isinstance(gpu_ranks, Exception):
            dsiji__ihb = gpu_ranks
            raise dsiji__ihb
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
    gmo__side = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        kkmx__zoj = MPI.COMM_WORLD.Split(color=0 if gmo__side in gpu_ranks else
            MPI.UNDEFINED, key=gmo__side)
        if kkmx__zoj != MPI.COMM_NULL:
            hvd.init(comm=kkmx__zoj)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                ccrsa__ekuu = tf.config.experimental.list_physical_devices(
                    'GPU')
                for pbcpd__rnvl in ccrsa__ekuu:
                    tf.config.experimental.set_memory_growth(pbcpd__rnvl, True)
                tf.config.experimental.set_visible_devices(ccrsa__ekuu[hvd.
                    local_rank()], 'GPU')
    else:
        if gmo__side == 0:
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
        oss__oajr = 17
        dgjt__kxz = MPI.COMM_WORLD
        silv__tab = MPI.Get_processor_name()
        czvdv__whto = get_host_ranks()[silv__tab]
        assert_dl_initialized()
        if bodo.get_rank() == czvdv__whto[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for gdtt__zum in czvdv__whto[1:]:
                dgjt__kxz.isend(1, dest=gdtt__zum, tag=oss__oajr)
        else:
            while True:
                eqz__cwa = MPI.Status()
                faz__iti = dgjt__kxz.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    eqz__cwa)
                if faz__iti:
                    assert eqz__cwa.source == czvdv__whto[0]
                    assert eqz__cwa.tag == oss__oajr
                    dgjt__kxz.recv(source=0, tag=oss__oajr)
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
