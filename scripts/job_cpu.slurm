#!/bin/bash
#SBATCH --job-name=mc_pi_cpu
#SBATCH --output=results/%x_%j.out
#SBATCH --error=results/%x_%j.err
#SBATCH --time=00:20:00
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G

# module load python/3.10
# module load openmpi

srun mpirun -np $SLURM_NTASKS python3 src/main.py --points 100000000
