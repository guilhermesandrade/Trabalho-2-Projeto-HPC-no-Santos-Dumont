#!/usr/bin/env bash
set -e
mkdir -p results
TOTAL=400000
for W in 1 2 4 8; do
  echo "Executando workers=$W"
  python3 src/main.py --points $TOTAL --workers $W --outfile results/result_mp_${W}.json
done
echo "Perfilamento concluído. Resultados em results/*.json"
