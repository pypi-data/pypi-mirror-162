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
        ofg__bjg = state
        ytaw__osf = inspect.getsourcelines(ofg__bjg)[0][0]
        assert ytaw__osf.startswith('@bodo.jit') or ytaw__osf.startswith('@jit'
            )
        mhr__yhpcu = eval(ytaw__osf[1:])
        self.dispatcher = mhr__yhpcu(ofg__bjg)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    osbg__ukx = MPI.COMM_WORLD
    while True:
        zomv__yxvh = osbg__ukx.bcast(None, root=MASTER_RANK)
        if zomv__yxvh[0] == 'exec':
            ofg__bjg = pickle.loads(zomv__yxvh[1])
            for vqso__ztdfq, ivg__vaxd in list(ofg__bjg.__globals__.items()):
                if isinstance(ivg__vaxd, MasterModeDispatcher):
                    ofg__bjg.__globals__[vqso__ztdfq] = ivg__vaxd.dispatcher
            if ofg__bjg.__module__ not in sys.modules:
                sys.modules[ofg__bjg.__module__] = pytypes.ModuleType(ofg__bjg
                    .__module__)
            ytaw__osf = inspect.getsourcelines(ofg__bjg)[0][0]
            assert ytaw__osf.startswith('@bodo.jit') or ytaw__osf.startswith(
                '@jit')
            mhr__yhpcu = eval(ytaw__osf[1:])
            func = mhr__yhpcu(ofg__bjg)
            gjes__aypp = zomv__yxvh[2]
            ulmq__bftj = zomv__yxvh[3]
            pojw__mzv = []
            for fec__dyk in gjes__aypp:
                if fec__dyk == 'scatter':
                    pojw__mzv.append(bodo.scatterv(None))
                elif fec__dyk == 'bcast':
                    pojw__mzv.append(osbg__ukx.bcast(None, root=MASTER_RANK))
            posye__pquv = {}
            for argname, fec__dyk in ulmq__bftj.items():
                if fec__dyk == 'scatter':
                    posye__pquv[argname] = bodo.scatterv(None)
                elif fec__dyk == 'bcast':
                    posye__pquv[argname] = osbg__ukx.bcast(None, root=
                        MASTER_RANK)
            ajp__geiz = func(*pojw__mzv, **posye__pquv)
            if ajp__geiz is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(ajp__geiz)
            del (zomv__yxvh, ofg__bjg, func, mhr__yhpcu, gjes__aypp,
                ulmq__bftj, pojw__mzv, posye__pquv, ajp__geiz)
            gc.collect()
        elif zomv__yxvh[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    osbg__ukx = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        gjes__aypp = ['scatter' for rpc__vvtjt in range(len(args))]
        ulmq__bftj = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        lrcro__ybkka = func.py_func.__code__.co_varnames
        wmd__yxx = func.targetoptions

        def get_distribution(argname):
            if argname in wmd__yxx.get('distributed', []
                ) or argname in wmd__yxx.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        gjes__aypp = [get_distribution(argname) for argname in lrcro__ybkka
            [:len(args)]]
        ulmq__bftj = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    zpggd__bxgyj = pickle.dumps(func.py_func)
    osbg__ukx.bcast(['exec', zpggd__bxgyj, gjes__aypp, ulmq__bftj])
    pojw__mzv = []
    for mxv__urtd, fec__dyk in zip(args, gjes__aypp):
        if fec__dyk == 'scatter':
            pojw__mzv.append(bodo.scatterv(mxv__urtd))
        elif fec__dyk == 'bcast':
            osbg__ukx.bcast(mxv__urtd)
            pojw__mzv.append(mxv__urtd)
    posye__pquv = {}
    for argname, mxv__urtd in kwargs.items():
        fec__dyk = ulmq__bftj[argname]
        if fec__dyk == 'scatter':
            posye__pquv[argname] = bodo.scatterv(mxv__urtd)
        elif fec__dyk == 'bcast':
            osbg__ukx.bcast(mxv__urtd)
            posye__pquv[argname] = mxv__urtd
    gyzpf__oelm = []
    for vqso__ztdfq, ivg__vaxd in list(func.py_func.__globals__.items()):
        if isinstance(ivg__vaxd, MasterModeDispatcher):
            gyzpf__oelm.append((func.py_func.__globals__, vqso__ztdfq, func
                .py_func.__globals__[vqso__ztdfq]))
            func.py_func.__globals__[vqso__ztdfq] = ivg__vaxd.dispatcher
    ajp__geiz = func(*pojw__mzv, **posye__pquv)
    for gshfv__kkjxw, vqso__ztdfq, ivg__vaxd in gyzpf__oelm:
        gshfv__kkjxw[vqso__ztdfq] = ivg__vaxd
    if ajp__geiz is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        ajp__geiz = bodo.gatherv(ajp__geiz)
    return ajp__geiz


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
