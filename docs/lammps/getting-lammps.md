# Getting LAMMPS on Hoffman2

!!! warning "Status, Nov 10 2026"

    OARC's software page says LAMMPS is installed on the legacy Grid Engine cluster only. It is **not yet on the Slurm cluster**, and OARC asks people to request it with a support ticket. Meanwhile OARC has asked users to stop submitting new Grid Engine jobs, and the legacy cluster is shrinking (49 nodes on Nov 5). So right now there are three routes.

## Which route?

| Route | Works today? | Effort | Notes |
|---|---|---|---|
| A. Ask OARC to install LAMMPS on Slurm | Takes days | 5 min | Best long-term. Do this regardless. |
| B. Build your own LAMMPS on Slurm | ⚠️ Untested here | ~30–60 min once | Full control of packages. One build can serve the whole lab. |
| C. Keep using the legacy module | Proven by the lab | None | OARC discourages new GE jobs; capacity is shrinking. |

## Route A: ask OARC

Open a ticket at the OARC [Technical support](https://www.hoffman2.idre.ucla.edu/Education-And-Support/Technical-support.html) page. Something like:

> Could LAMMPS be installed as a module on the Slurm cluster? We use the MANYBODY (EAM) and REAXFF packages and run with MPI. On the legacy cluster we used `lammps/29Sep2021_MB`. A current stable release (30 Sep 2026) would be ideal. Group: <your lab's resource group>.

When it's installed, find it with:

```bash
module spider lammps        # or: h2 modules lammps
```

## Route B: build your own (Slurm)

LAMMPS builds with CMake. The lab-tested parts are the CMake package flags; the Hoffman2-specific module names come from OARC's docs, and this exact recipe hasn't been run on Hoffman2 yet.

1. Start an interactive session on a compute node (building on the login node is a bad idea):
    ```bash
    srun --time=02:00:00 --cpus-per-task=8 --mem=16G --pty bash -l
    ```
2. Get the build script and run it:
    ```bash
    cp ~/hoffman2-lammps-guide/docs/files/build_lammps.sh .
    bash build_lammps.sh
    ```
    It loads `intel/2026.0.0` (Intel compilers + Intel MPI), clones the latest stable LAMMPS, and builds `$HOME/software/lammps/build/lmp` with MANYBODY, REAXFF, EXTRA-COMPUTE, MOLECULE and KSPACE.
3. Check it:
    ```bash
    ~/software/lammps/build/lmp -h | grep -A15 "Installed packages"
    ```
    `MANYBODY` and `REAXFF` must be listed.
4. In job scripts, load the same module you built with, and call the full path to `lmp`. [`run_lammps.slurm`](../files/run_lammps.slurm) is set up for this.

!!! tip "Build once for the whole lab"

    If the PI has project space, build into `/u/project/<group>/shared/lammps` instead of `$HOME`, so everyone uses the same binary and results are comparable.

!!! warning "Don't use `-march=native`"

    Hoffman2's Slurm nodes are a mix of Intel Gold, Intel Xeon 6 and AMD EPYC. A binary tuned to one chip can crash with `Illegal instruction` on another (this is exactly what happened with the legacy `_MB` module on non-intel-gold nodes). The default `Release` build is portable. If you do tune it, pin jobs to that CPU type with `-C`.

If CMake or the compiler isn't found, run `module spider cmake` and `module spider intel` and adjust the `module load` lines. LAMMPS needs CMake ≥ 3.20.

### Quick option for small tests: `pip` (any laptop, or Hoffman2)

`pip install lammps` has ready-made builds for macOS (Intel and Apple silicon), Windows and Linux, with most packages, including MANYBODY and REAXFF. This guide's example inputs were all tested with it (LAMMPS 22 Jul 2025). Use it to check an input runs before spending cluster time; use a proper MPI build for production runs.

Setup and commands for each system: [Laptop setup → LAMMPS on your laptop](../getting-started/laptop-setup.md#optional-lammps-on-your-laptop-for-small-tests).

## Route C: legacy Grid Engine module

What the lab used through Oct 2026. Full details on [Job scripts: Grid Engine](../jobs/grid-engine-legacy.md). Summary:

| Module | Use? | Why |
|---|---|---|
| `lammps/29Sep2021_MB` | | Has MANYBODY (needed for EAM) |
| `lammps/29Sep2021` | No | No MANYBODY: `pair_style eam` fails |

- Executable: `lmp_mpi`
- Needs `arch=intel-gold*` (crashes with `Illegal instruction` elsewhere)
- Use full paths to `mpirun`/`lmp_mpi` in job scripts (`module load` fails on some nodes)
- ⚠️ Not confirmed whether this build includes REAXFF

## Which version am I running?

The first line of every `log.lammps` says, e.g. `LAMMPS (29 Sep 2021 - Update 2)`. Record it in your notes: results can shift slightly between versions, and syntax changes (e.g. `reax/c` was renamed `reaxff` in 2021).

```bash
head -1 log.lammps
lmp -h | head -20         # version, packages, compile options
```
