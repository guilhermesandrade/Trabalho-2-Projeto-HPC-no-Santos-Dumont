#!/usr/bin/env bash
set -e
N=${1:-1000000}
WORKERS=${2:-4}
if which mpirun >/dev/null 2>&1; then
  mpirun -np ${WORKERS} python3 src/main.py --points $N
else
  python3 src/main.py --points $N --workers ${WORKERS}
fi
