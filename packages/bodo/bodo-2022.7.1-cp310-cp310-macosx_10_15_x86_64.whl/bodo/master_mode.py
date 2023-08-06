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
        nhsue__pnau = state
        dqwxy__zbc = inspect.getsourcelines(nhsue__pnau)[0][0]
        assert dqwxy__zbc.startswith('@bodo.jit') or dqwxy__zbc.startswith(
            '@jit')
        ixvec__ebhid = eval(dqwxy__zbc[1:])
        self.dispatcher = ixvec__ebhid(nhsue__pnau)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    cqrx__iwkf = MPI.COMM_WORLD
    while True:
        lmw__tfju = cqrx__iwkf.bcast(None, root=MASTER_RANK)
        if lmw__tfju[0] == 'exec':
            nhsue__pnau = pickle.loads(lmw__tfju[1])
            for wejag__gvhdy, soylp__xogmg in list(nhsue__pnau.__globals__.
                items()):
                if isinstance(soylp__xogmg, MasterModeDispatcher):
                    nhsue__pnau.__globals__[wejag__gvhdy
                        ] = soylp__xogmg.dispatcher
            if nhsue__pnau.__module__ not in sys.modules:
                sys.modules[nhsue__pnau.__module__] = pytypes.ModuleType(
                    nhsue__pnau.__module__)
            dqwxy__zbc = inspect.getsourcelines(nhsue__pnau)[0][0]
            assert dqwxy__zbc.startswith('@bodo.jit') or dqwxy__zbc.startswith(
                '@jit')
            ixvec__ebhid = eval(dqwxy__zbc[1:])
            func = ixvec__ebhid(nhsue__pnau)
            cbt__vpm = lmw__tfju[2]
            yxh__qmq = lmw__tfju[3]
            nsuf__vuv = []
            for pie__nax in cbt__vpm:
                if pie__nax == 'scatter':
                    nsuf__vuv.append(bodo.scatterv(None))
                elif pie__nax == 'bcast':
                    nsuf__vuv.append(cqrx__iwkf.bcast(None, root=MASTER_RANK))
            gvmci__felm = {}
            for argname, pie__nax in yxh__qmq.items():
                if pie__nax == 'scatter':
                    gvmci__felm[argname] = bodo.scatterv(None)
                elif pie__nax == 'bcast':
                    gvmci__felm[argname] = cqrx__iwkf.bcast(None, root=
                        MASTER_RANK)
            gjn__xhi = func(*nsuf__vuv, **gvmci__felm)
            if gjn__xhi is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(gjn__xhi)
            del (lmw__tfju, nhsue__pnau, func, ixvec__ebhid, cbt__vpm,
                yxh__qmq, nsuf__vuv, gvmci__felm, gjn__xhi)
            gc.collect()
        elif lmw__tfju[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    cqrx__iwkf = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        cbt__vpm = ['scatter' for adfq__hwj in range(len(args))]
        yxh__qmq = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        prvsr__lbqcl = func.py_func.__code__.co_varnames
        pyynr__emj = func.targetoptions

        def get_distribution(argname):
            if argname in pyynr__emj.get('distributed', []
                ) or argname in pyynr__emj.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        cbt__vpm = [get_distribution(argname) for argname in prvsr__lbqcl[:
            len(args)]]
        yxh__qmq = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    tmfjh__yqo = pickle.dumps(func.py_func)
    cqrx__iwkf.bcast(['exec', tmfjh__yqo, cbt__vpm, yxh__qmq])
    nsuf__vuv = []
    for znmo__vtof, pie__nax in zip(args, cbt__vpm):
        if pie__nax == 'scatter':
            nsuf__vuv.append(bodo.scatterv(znmo__vtof))
        elif pie__nax == 'bcast':
            cqrx__iwkf.bcast(znmo__vtof)
            nsuf__vuv.append(znmo__vtof)
    gvmci__felm = {}
    for argname, znmo__vtof in kwargs.items():
        pie__nax = yxh__qmq[argname]
        if pie__nax == 'scatter':
            gvmci__felm[argname] = bodo.scatterv(znmo__vtof)
        elif pie__nax == 'bcast':
            cqrx__iwkf.bcast(znmo__vtof)
            gvmci__felm[argname] = znmo__vtof
    ufyz__dli = []
    for wejag__gvhdy, soylp__xogmg in list(func.py_func.__globals__.items()):
        if isinstance(soylp__xogmg, MasterModeDispatcher):
            ufyz__dli.append((func.py_func.__globals__, wejag__gvhdy, func.
                py_func.__globals__[wejag__gvhdy]))
            func.py_func.__globals__[wejag__gvhdy] = soylp__xogmg.dispatcher
    gjn__xhi = func(*nsuf__vuv, **gvmci__felm)
    for vzvta__ngz, wejag__gvhdy, soylp__xogmg in ufyz__dli:
        vzvta__ngz[wejag__gvhdy] = soylp__xogmg
    if gjn__xhi is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        gjn__xhi = bodo.gatherv(gjn__xhi)
    return gjn__xhi


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
