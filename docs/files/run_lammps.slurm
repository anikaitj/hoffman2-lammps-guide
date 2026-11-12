#!/bin/bash
# =====================================================================
# run_lammps.slurm: Slurm job script for LAMMPS on Hoffman2
# (hoffman2.oarc.ucla.edu). Copy into your run folder, edit the
# lines marked EDIT, check with `h2 validate run_lammps.slurm`,
# then submit with `sbatch run_lammps.slurm`.
#
# ⚠ Untested on Hoffman2 as of Nov 2026: OARC's software page says LAMMPS
#   is not yet installed on the Slurm cluster. Use this with your own build
#   (see "Getting LAMMPS" in the guide) or with the OARC module once it exists.
# =====================================================================
#SBATCH --job-name=cu_test               # EDIT: name shown in squeue
#SBATCH --account=pi_CHANGEME            # EDIT: your Slurm account (run: h2 whoami)
#SBATCH --time=12:00:00                  # EDIT: max 24:00:00 on campus/shared, 14 days with highp
#SBATCH --nodes=1                        # keep on one node unless you need more cores
#SBATCH --ntasks=8                       # EDIT: number of MPI ranks (cores)
#SBATCH --mem-per-cpu=2G                 # always set memory (no default on Slurm)
#SBATCH --output=joblog.%j               # %j = job ID
##SBATCH --qos=highp                     # uncomment ONLY if the group's nodes are on Slurm
##SBATCH -C intel-gold-6342              # optional: pin a CPU type (same as your build)
##SBATCH --mail-type=END,FAIL            # optional: email when done/failed
##SBATCH --mail-user=you@ucla.edu

# --- environment: load the SAME modules you built LAMMPS with ---
module purge
module load intel/2026.0.0               # EDIT if you built with something else

# --- EDIT: path to the LAMMPS executable ---
LMP=$HOME/software/lammps/build/lmp      # your own build
# LMP=lmp                                # if an OARC module provides it

echo "Job $SLURM_JOB_ID on $(hostname) with $SLURM_NTASKS tasks, started $(date)"

# Use mpirun (not srun) for MPI programs on Hoffman2
mpirun -n $SLURM_NTASKS $LMP -in in.cu_test -log log.lammps     # EDIT: input file

echo "Finished $(date)"
