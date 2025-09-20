#!/usr/bin/env python3
"""Estimativa de pi por Monte Carlo.
Suporta: mpi4py (quando executado com mpirun/srun) ou multiprocessing como fallback.
Saída: grava JSON em results/ com tempos e métricas.
"""

import argparse, time, os, math, random, json
from time import perf_counter

# try import mpi4py
MPI_AVAILABLE = False
try:
    from mpi4py import MPI
    MPI_AVAILABLE = True
except Exception:
    MPI_AVAILABLE = False

def estimate_count(n_points, seed):
    rng = random.Random(seed)
    cnt = 0
    for _ in range(n_points):
        x = rng.random(); y = rng.random()
        if x*x + y*y <= 1.0:
            cnt += 1
    return cnt

def run_serial(total_points, seed=0):
    t0 = perf_counter()
    cnt = estimate_count(total_points, seed)
    t1 = perf_counter()
    return {'time': t1-t0, 'count': cnt}

def run_multiprocessing(total_points, workers, seed=0):
    from concurrent.futures import ProcessPoolExecutor
    chunk = total_points // workers
    t0 = perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as exe:
        futures = []
        for i in range(workers):
            n = chunk + (1 if i == workers-1 and total_points % workers != 0 else 0)
            futures.append(exe.submit(estimate_count, n, seed + i))
        counts = sum(f.result() for f in futures)
    t1 = perf_counter()
    return {'time': t1-t0, 'count': counts}

def run_mpi(total_points, seed=0):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank(); size = comm.Get_size()
    chunk = total_points // size
    n = chunk + (total_points % size if rank == size-1 else 0)
    t0 = perf_counter()
    local_count = estimate_count(n, seed + rank)
    # reduce
    total_count = comm.reduce(local_count, op=MPI.SUM, root=0)
    t1 = perf_counter()
    if rank == 0:
        return {'time': t1-t0, 'count': total_count, 'procs': size}
    else:
        return None

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--points', type=int, default=1000000)
    parser.add_argument('--workers', type=int, default=4, help='used when no MPI available')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--outfile', type=str, default=None)
    args = parser.parse_args()

    ensure_dir('results')

    if MPI_AVAILABLE:
        # if running under mpirun, use MPI
        res = run_mpi(args.points, seed=args.seed)
        if res is not None:
            pi = 4 * res['count'] / args.points
            out = {
                'pi_estimate': pi,
                'count': res['count'],
                'points': args.points,
                'time_s': res['time'],
                'procs': res.get('procs', None)
            }
            fname = args.outfile or f"results/result_mpi_{int(time.time())}.json"
            with open(fname, 'w') as f:
                json.dump(out, f, indent=2)
            print(json.dumps(out, indent=2))
    else:
        # fallback: multiprocessing
        res = run_multiprocessing(args.points, args.workers, seed=args.seed)
        pi = 4 * res['count'] / args.points
        out = {
            'pi_estimate': pi,
            'count': res['count'],
            'points': args.points,
            'time_s': res['time'],
            'workers': args.workers
        }
        fname = args.outfile or f"results/result_mp_{int(time.time())}.json"
        with open(fname, 'w') as f:
            json.dump(out, f, indent=2)
        print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
