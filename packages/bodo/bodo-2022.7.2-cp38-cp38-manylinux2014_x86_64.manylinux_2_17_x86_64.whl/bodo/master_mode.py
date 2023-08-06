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
        xae__jswc = state
        zkbbw__djjr = inspect.getsourcelines(xae__jswc)[0][0]
        assert zkbbw__djjr.startswith('@bodo.jit') or zkbbw__djjr.startswith(
            '@jit')
        vlj__pwbgp = eval(zkbbw__djjr[1:])
        self.dispatcher = vlj__pwbgp(xae__jswc)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    esmf__ozf = MPI.COMM_WORLD
    while True:
        zpmco__ppdob = esmf__ozf.bcast(None, root=MASTER_RANK)
        if zpmco__ppdob[0] == 'exec':
            xae__jswc = pickle.loads(zpmco__ppdob[1])
            for oscx__vjsit, voaph__vyp in list(xae__jswc.__globals__.items()):
                if isinstance(voaph__vyp, MasterModeDispatcher):
                    xae__jswc.__globals__[oscx__vjsit] = voaph__vyp.dispatcher
            if xae__jswc.__module__ not in sys.modules:
                sys.modules[xae__jswc.__module__] = pytypes.ModuleType(
                    xae__jswc.__module__)
            zkbbw__djjr = inspect.getsourcelines(xae__jswc)[0][0]
            assert zkbbw__djjr.startswith('@bodo.jit'
                ) or zkbbw__djjr.startswith('@jit')
            vlj__pwbgp = eval(zkbbw__djjr[1:])
            func = vlj__pwbgp(xae__jswc)
            kkoh__dna = zpmco__ppdob[2]
            jbnv__cdz = zpmco__ppdob[3]
            vym__jfh = []
            for utziq__qvg in kkoh__dna:
                if utziq__qvg == 'scatter':
                    vym__jfh.append(bodo.scatterv(None))
                elif utziq__qvg == 'bcast':
                    vym__jfh.append(esmf__ozf.bcast(None, root=MASTER_RANK))
            nkrjq__iju = {}
            for argname, utziq__qvg in jbnv__cdz.items():
                if utziq__qvg == 'scatter':
                    nkrjq__iju[argname] = bodo.scatterv(None)
                elif utziq__qvg == 'bcast':
                    nkrjq__iju[argname] = esmf__ozf.bcast(None, root=
                        MASTER_RANK)
            klxis__huxe = func(*vym__jfh, **nkrjq__iju)
            if klxis__huxe is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(klxis__huxe)
            del (zpmco__ppdob, xae__jswc, func, vlj__pwbgp, kkoh__dna,
                jbnv__cdz, vym__jfh, nkrjq__iju, klxis__huxe)
            gc.collect()
        elif zpmco__ppdob[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    esmf__ozf = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        kkoh__dna = ['scatter' for pchgx__geft in range(len(args))]
        jbnv__cdz = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        kxp__qejj = func.py_func.__code__.co_varnames
        ttgx__uuv = func.targetoptions

        def get_distribution(argname):
            if argname in ttgx__uuv.get('distributed', []
                ) or argname in ttgx__uuv.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        kkoh__dna = [get_distribution(argname) for argname in kxp__qejj[:
            len(args)]]
        jbnv__cdz = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    cdokp__ujlo = pickle.dumps(func.py_func)
    esmf__ozf.bcast(['exec', cdokp__ujlo, kkoh__dna, jbnv__cdz])
    vym__jfh = []
    for oedk__eoy, utziq__qvg in zip(args, kkoh__dna):
        if utziq__qvg == 'scatter':
            vym__jfh.append(bodo.scatterv(oedk__eoy))
        elif utziq__qvg == 'bcast':
            esmf__ozf.bcast(oedk__eoy)
            vym__jfh.append(oedk__eoy)
    nkrjq__iju = {}
    for argname, oedk__eoy in kwargs.items():
        utziq__qvg = jbnv__cdz[argname]
        if utziq__qvg == 'scatter':
            nkrjq__iju[argname] = bodo.scatterv(oedk__eoy)
        elif utziq__qvg == 'bcast':
            esmf__ozf.bcast(oedk__eoy)
            nkrjq__iju[argname] = oedk__eoy
    snv__bbtx = []
    for oscx__vjsit, voaph__vyp in list(func.py_func.__globals__.items()):
        if isinstance(voaph__vyp, MasterModeDispatcher):
            snv__bbtx.append((func.py_func.__globals__, oscx__vjsit, func.
                py_func.__globals__[oscx__vjsit]))
            func.py_func.__globals__[oscx__vjsit] = voaph__vyp.dispatcher
    klxis__huxe = func(*vym__jfh, **nkrjq__iju)
    for kxlwx__oqbld, oscx__vjsit, voaph__vyp in snv__bbtx:
        kxlwx__oqbld[oscx__vjsit] = voaph__vyp
    if klxis__huxe is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        klxis__huxe = bodo.gatherv(klxis__huxe)
    return klxis__huxe


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
