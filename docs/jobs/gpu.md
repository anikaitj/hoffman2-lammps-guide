# GPU and multithreaded runs

Large systems (hundreds of thousands of atoms and up) can run much faster on GPUs. Hoffman2's Slurm cluster has GPU nodes; LAMMPS can use them through its GPU or KOKKOS packages.

!!! warning "Not yet tested by the lab"

    Nobody in the group has run LAMMPS on Hoffman2 GPUs yet, and OARC has no LAMMPS module on Slurm (Nov 2026). The Hoffman2 parts below come from OARC's Slurm page and the LAMMPS parts from the LAMMPS manual. Test with a short job before relying on it, and update this page.

## Do you need a GPU?

| System | Usually best on |
|---|---|
| < ~50,000 atoms (most lab runs so far) | CPU cores (8–48 on one node) |
| ~10⁵–10⁷ atoms, pair-heavy potentials (LJ, EAM) | GPU |
| Long-range charges (PPPM) | GPU helps for the pair part; the FFTs may stay on the CPU |

Measure before switching: run 1,000–5,000 steps both ways and compare `hours/ns` in the `Performance:` line.

## Requesting GPUs on Hoffman2 (Slurm)

From OARC's Slurm page:

- Request cards with `--gres=gpu:N` and the card type with `-C`. Jobs without `--gres=gpu` only run on CPU nodes.
- Interactive session with one A100:
    ```bash
    srun --time=02:00:00 --mem=16G --gres=gpu:1 -C A100 --pty bash -l
    ```
- In a batch script:
    ```bash
    #SBATCH --gres=gpu:1
    #SBATCH -C A100
    ```
- You can also select by compute capability or GPU memory, e.g. `-C cuda_cc_8_0` or `-C "gpu&vmem40G"`.
- To see which GPU types exist and which are free: `h2 gpus`, `GPU_NODES_AT_A_GLANCE`, `GPU_NODES_AT_A_GLANCE_WITH_USED_GPUs`. A free GPU in that list isn't necessarily available to you.
- Load CUDA before running GPU code: the page names `module load cuda/12.8`. Start scripts with `module purge`.
- Your GPU limit: `h2 whoami`.

## Building LAMMPS for GPUs

Do this in an interactive GPU session, with `cuda/12.8` loaded, using the same clone as [`build_lammps.sh`](../files/build_lammps.sh). Use a separate build folder so your CPU build stays intact.

### Option 1: GPU package (simplest)

From the LAMMPS build docs, for A100 cards (Ampere, `sm_80`):

```bash
module purge && module load cuda/12.8 && module load intel/2026.0.0
cd ~/software/lammps
cmake -S cmake -B build-gpu -C cmake/presets/most.cmake \
  -D PKG_GPU=on -D GPU_API=cuda -D GPU_ARCH=sm_80 -D GPU_PREC=mixed \
  -D BUILD_MPI=on
cmake --build build-gpu --parallel 8
```

`GPU_PREC` is `mixed` by default; use `double` if you need full double precision.

### Option 2: KOKKOS (runs more of the simulation on the GPU)

```bash
cmake -S cmake -B build-kokkos -C cmake/presets/most.cmake \
  -D PKG_KOKKOS=yes -D BUILD_OMP=yes \
  -D Kokkos_ARCH_HOSTARCH=yes -D Kokkos_ARCH_AMPERE80=yes \
  -D Kokkos_ENABLE_CUDA=yes -D Kokkos_ENABLE_OPENMP=yes \
  -D BUILD_MPI=on
cmake --build build-kokkos --parallel 8
```

Replace `HOSTARCH` with the CPU architecture ID from the LAMMPS manual's KOKKOS table for the GPU node's CPU. The manual says Kokkos can also auto-detect a CUDA configuration.

## Running

GPU package: add `-sf gpu -pk gpu N` (N = GPUs per node). The manual recommends 2–10 MPI tasks per GPU:

```bash
mpirun -n 4 ~/software/lammps/build-gpu/lmp -sf gpu -pk gpu 1 -in in.cu_test -log log.lammps
```

KOKKOS: one MPI task per GPU:

```bash
mpirun -n 1 ~/software/lammps/build-kokkos/lmp -k on g 1 -sf kk -pk kokkos newton on neigh half \
       -in in.cu_test -log log.lammps
```

(The manual says half neighbor lists with Newton on "may be faster" on Pascal and newer GPUs.)

`-sf gpu` / `-sf kk` switches every style that has a GPU version (e.g. `lj/cut` → `lj/cut/gpu`) and leaves the rest on the CPU. `log.lammps` lists which styles were accelerated. Check yours has the styles you need with `lmp -h` (look for `/gpu` or `/kk` versions, e.g. of `eam`).

## Example GPU job script

```bash
#!/bin/bash
#SBATCH --job-name=lmp_gpu
#SBATCH --account=pi_CHANGEME
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH -C A100
#SBATCH --output=joblog.%j

module purge
module load cuda/12.8
module load intel/2026.0.0

mpirun -n $SLURM_NTASKS $HOME/software/lammps/build-gpu/lmp -sf gpu -pk gpu 1 \
       -in in.cu_test -log log.lammps
```

## Multithreading on CPUs (OPENMP)

Without GPUs, the OPENMP package lets each MPI task use several threads. It's sometimes faster than pure MPI for small systems or many cores per node. [`build_lammps.sh`](../files/build_lammps.sh) includes it.

```bash
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=4
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
mpirun -n $SLURM_NTASKS $LMP -sf omp -pk omp $OMP_NUM_THREADS -in in.film_template -log log.lammps
```

Compare `hours/ns` with a plain MPI run on the same 16 cores; keep whichever is faster.
