#!/bin/bash
# =====================================================================
# build_lammps.sh: build your own LAMMPS on the Hoffman2 Slurm cluster
#
# ⚠ UNTESTED on Hoffman2. The steps follow the official LAMMPS CMake
#   instructions (docs.lammps.org/Build_cmake.html). Module names come from
#   OARC's Slurm page. If a step fails, stop and check `module spider cmake`
#   and `module spider intel`, or ask OARC.
#
# Run it on a COMPUTE node, not the login node:
#   srun --time=02:00:00 --cpus-per-task=8 --mem=16G --pty bash -l
#   bash build_lammps.sh
#
# Result: $HOME/software/lammps/build/lmp
# Packages: LAMMPS's "most" preset ("enable most packages") plus the ones
#           listed explicitly below, which every recipe in this guide needs.
#           See exactly what you got with:  lmp -h
# =====================================================================
set -e

PREFIX=$HOME/software
NCORES=${SLURM_CPUS_PER_TASK:-4}

module purge
module load intel/2026.0.0          # Intel compilers + Intel MPI (OARC's MPI example uses this)
module load cmake 2>/dev/null || echo "note: no cmake module loaded; using system cmake: $(cmake --version | head -1)"
# LAMMPS needs CMake >= 3.20

mkdir -p "$PREFIX" && cd "$PREFIX"
if [ ! -d lammps ]; then
  # 'stable' always points at the latest stable release
  git clone --depth 1 -b stable https://github.com/lammps/lammps.git lammps
fi
cd lammps
git log -1 --format='Building LAMMPS from: %D (%cs)'

cmake -S cmake -B build \
  -C cmake/presets/most.cmake \
  -D CMAKE_BUILD_TYPE=Release \
  -D CMAKE_CXX_COMPILER=mpiicpx \
  -D CMAKE_C_COMPILER=mpiicx \
  -D BUILD_MPI=on \
  -D BUILD_OMP=on \
  -D PKG_MANYBODY=on \
  -D PKG_MOLECULE=on \
  -D PKG_KSPACE=on \
  -D PKG_RIGID=on \
  -D PKG_REAXFF=on \
  -D PKG_EXTRA-FIX=on \
  -D PKG_EXTRA-COMPUTE=on \
  -D PKG_OPENMP=on

cmake --build build --parallel "$NCORES"

echo
echo "Built: $PREFIX/lammps/build/lmp"
"$PREFIX/lammps/build/lmp" -h | sed -n '/Installed packages/,/^$/p'
