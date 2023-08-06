import gc
import inspect
import sys
import types as pytypes
import bodo
master_mode_on = False
MASTER_RANK = 0


class MasterModeDispatcher(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def __call__(self, *args, **kwargs):
        assert bodo.get_rank() == MASTER_RANK
        return master_wrapper(self.dispatcher, *args, **kwargs)

    def __getstate__(self):
        assert bodo.get_rank() == MASTER_RANK
        return self.dispatcher.py_func

    def __setstate__(self, state):
        assert bodo.get_rank() != MASTER_RANK
        axo__zwbxp = state
        ulqzn__tdg = inspect.getsourcelines(axo__zwbxp)[0][0]
        assert ulqzn__tdg.startswith('@bodo.jit') or ulqzn__tdg.startswith(
            '@jit')
        henap__alirz = eval(ulqzn__tdg[1:])
        self.dispatcher = henap__alirz(axo__zwbxp)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    ijje__hxbbz = MPI.COMM_WORLD
    while True:
        mkmu__idcvp = ijje__hxbbz.bcast(None, root=MASTER_RANK)
        if mkmu__idcvp[0] == 'exec':
            axo__zwbxp = pickle.loads(mkmu__idcvp[1])
            for mqo__ccsh, pnscq__vlfq in list(axo__zwbxp.__globals__.items()):
                if isinstance(pnscq__vlfq, MasterModeDispatcher):
                    axo__zwbxp.__globals__[mqo__ccsh] = pnscq__vlfq.dispatcher
            if axo__zwbxp.__module__ not in sys.modules:
                sys.modules[axo__zwbxp.__module__] = pytypes.ModuleType(
                    axo__zwbxp.__module__)
            ulqzn__tdg = inspect.getsourcelines(axo__zwbxp)[0][0]
            assert ulqzn__tdg.startswith('@bodo.jit') or ulqzn__tdg.startswith(
                '@jit')
            henap__alirz = eval(ulqzn__tdg[1:])
            func = henap__alirz(axo__zwbxp)
            sdoi__vhri = mkmu__idcvp[2]
            hbqk__iprz = mkmu__idcvp[3]
            sdtek__maxu = []
            for sdw__qnhn in sdoi__vhri:
                if sdw__qnhn == 'scatter':
                    sdtek__maxu.append(bodo.scatterv(None))
                elif sdw__qnhn == 'bcast':
                    sdtek__maxu.append(ijje__hxbbz.bcast(None, root=
                        MASTER_RANK))
            jnbea__eru = {}
            for argname, sdw__qnhn in hbqk__iprz.items():
                if sdw__qnhn == 'scatter':
                    jnbea__eru[argname] = bodo.scatterv(None)
                elif sdw__qnhn == 'bcast':
                    jnbea__eru[argname] = ijje__hxbbz.bcast(None, root=
                        MASTER_RANK)
            lfw__wsjdu = func(*sdtek__maxu, **jnbea__eru)
            if lfw__wsjdu is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(lfw__wsjdu)
            del (mkmu__idcvp, axo__zwbxp, func, henap__alirz, sdoi__vhri,
                hbqk__iprz, sdtek__maxu, jnbea__eru, lfw__wsjdu)
            gc.collect()
        elif mkmu__idcvp[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    ijje__hxbbz = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        sdoi__vhri = ['scatter' for yfawg__ojsl in range(len(args))]
        hbqk__iprz = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        syhc__vlhlt = func.py_func.__code__.co_varnames
        ttg__vcgh = func.targetoptions

        def get_distribution(argname):
            if argname in ttg__vcgh.get('distributed', []
                ) or argname in ttg__vcgh.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        sdoi__vhri = [get_distribution(argname) for argname in syhc__vlhlt[
            :len(args)]]
        hbqk__iprz = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    hina__apm = pickle.dumps(func.py_func)
    ijje__hxbbz.bcast(['exec', hina__apm, sdoi__vhri, hbqk__iprz])
    sdtek__maxu = []
    for xidn__izhx, sdw__qnhn in zip(args, sdoi__vhri):
        if sdw__qnhn == 'scatter':
            sdtek__maxu.append(bodo.scatterv(xidn__izhx))
        elif sdw__qnhn == 'bcast':
            ijje__hxbbz.bcast(xidn__izhx)
            sdtek__maxu.append(xidn__izhx)
    jnbea__eru = {}
    for argname, xidn__izhx in kwargs.items():
        sdw__qnhn = hbqk__iprz[argname]
        if sdw__qnhn == 'scatter':
            jnbea__eru[argname] = bodo.scatterv(xidn__izhx)
        elif sdw__qnhn == 'bcast':
            ijje__hxbbz.bcast(xidn__izhx)
            jnbea__eru[argname] = xidn__izhx
    mvmhd__dtm = []
    for mqo__ccsh, pnscq__vlfq in list(func.py_func.__globals__.items()):
        if isinstance(pnscq__vlfq, MasterModeDispatcher):
            mvmhd__dtm.append((func.py_func.__globals__, mqo__ccsh, func.
                py_func.__globals__[mqo__ccsh]))
            func.py_func.__globals__[mqo__ccsh] = pnscq__vlfq.dispatcher
    lfw__wsjdu = func(*sdtek__maxu, **jnbea__eru)
    for hyt__dgh, mqo__ccsh, pnscq__vlfq in mvmhd__dtm:
        hyt__dgh[mqo__ccsh] = pnscq__vlfq
    if lfw__wsjdu is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        lfw__wsjdu = bodo.gatherv(lfw__wsjdu)
    return lfw__wsjdu


def init_master_mode():
    if bodo.get_size() == 1:
        return
    global master_mode_on
    assert master_mode_on is False, 'init_master_mode can only be called once on each process'
    master_mode_on = True
    assert sys.version_info[:2] >= (3, 8
        ), 'Python 3.8+ required for master mode'
    from bodo import jit
    globals()['jit'] = jit
    import cloudpickle
    from mpi4py import MPI
    globals()['pickle'] = cloudpickle
    globals()['MPI'] = MPI

    def master_exit():
        MPI.COMM_WORLD.bcast(['exit'])
    if bodo.get_rank() == MASTER_RANK:
        import atexit
        atexit.register(master_exit)
    else:
        worker_loop()
