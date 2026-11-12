# Files & scripts reference

Every file in the repo's `docs/files/` folder: what it is, where it runs, how to run it on each system, and what you should see.

!!! tip "Where do these files come from?"

    - On Hoffman2: `git clone` the repo once into your home folder; the files are in `~/hoffman2-lammps-guide/docs/files/`.
    - On your laptop: clone the repo there too ([Laptop setup](../getting-started/laptop-setup.md#2-git)), or click a file on this site to download it.

## At a glance

| File | Type | Runs on | Needs |
|---|---|---|---|
| [`in.cu_test`](../files/in.cu_test) | LAMMPS input | Hoffman2 (or laptop via pip LAMMPS) | `Cu_mishin1.eam.alloy` |
| [`in.film_template`](../files/in.film_template) | LAMMPS input | Hoffman2 (or laptop for short tests) | `Cu_u3.eam` |
| [`in.cho`](../files/in.cho) | LAMMPS input | Hoffman2 (or laptop) | `data.CHO`, `ffield.reax.cho`, REAXFF |
| [`run_lammps.slurm`](../files/run_lammps.slurm) | Job script | Hoffman2 Slurm cluster | LAMMPS on Slurm |
| [`make_jobscript_sge.sh`](../files/make_jobscript_sge.sh) | Bash helper | Hoffman2 legacy login node | legacy `lammps/29Sep2021_MB` |
| [`build_lammps.sh`](../files/build_lammps.sh) | Bash build script | Hoffman2 Slurm compute node | interactive session ⚠️ untested |
| [`plot_thermo.py`](../files/plot_thermo.py) | Python | Any: macOS, Windows, Linux, Hoffman2 | Python 3; matplotlib for the plot |
| [`analyze_orientation.py`](../files/analyze_orientation.py) | Python | macOS (Apple silicon), Windows, Linux, Hoffman2 | Python 3.11+, `ovito`, `numpy` |
| [`select_111_atoms.txt`](../files/select_111_atoms.txt) | Text | OVITO desktop (any OS) | PTM with orientations |
| `recipes/in.*` (9 inputs) | LAMMPS inputs | Hoffman2 (or laptop via pip LAMMPS) | see [Simulation recipes](../recipes/index.md) |
| [`recipes/water.mol`](../files/recipes/water.mol) | Molecule template | used by `in.water_spce` | — |
| [`recipes/fit_profile.py`](../files/recipes/fit_profile.py) | Python | Any: macOS, Windows, Linux, Hoffman2 | Python 3 only |

Anything that runs on Hoffman2 works the same whatever laptop you use, since you're typing into Linux over SSH. Only the Python tools run on your laptop, and those work on all three systems.

---

## `in.cu_test`

Small Cu crystal (4,000 atoms) at 300 K and 0 bar for 50 ps. The "is my setup working?" test. Walkthrough: [Your first simulation](../getting-started/first-run.md).

On Hoffman2 (in the run folder, with the potential there):

```bash
# legacy:
bash make_jobscript_sge.sh cu_test in.cu_test 8 00:30:00 && qsub run_cu_test.sh
# Slurm: set -in in.cu_test in run_lammps.slurm, then
sbatch run_lammps.slurm
```

On a laptop (pip LAMMPS, for a quick check):

=== "macOS"

    ```bash
    python3 -c "from lammps import lammps; L=lammps(); L.file('in.cu_test')"
    ```

=== "Windows"

    ```powershell
    py -c "from lammps import lammps; L=lammps(); L.file('in.cu_test')"
    ```

=== "Linux"

    ```bash
    python3 -c "from lammps import lammps; L=lammps(); L.file('in.cu_test')"
    ```

Expected: `=== DONE ===` at the end of `log.lammps`; T ≈ 300 K; density ≈ 8.8 g/cm³; `analyze_orientation.py` → 100% FCC, 100% (100).

## `in.film_template`

Four differently oriented grains on a 3-layer Cu(111) template, annealed below melting. Settings via `-var`. Walkthrough: [Film on a (111) template](../examples/film-template.md).

```bash
mpirun -n 8 $LMP -in in.film_template -var T_hold 1000 -var frozen 0 -var vseed 111234 -log log.lammps
```

Quick laptop check (shortened schedule, a minute or two):

=== "macOS"

    ```bash
    python3 -c "from lammps import lammps; L=lammps(cmdargs=['-var','heat_ps','2','-var','hold_ps','1','-var','cool_ps','1','-var','dump_ps','1']); L.file('in.film_template')"
    ```

=== "Windows"

    ```powershell
    py -c "from lammps import lammps; L=lammps(cmdargs=['-var','heat_ps','2','-var','hold_ps','1','-var','cool_ps','1','-var','dump_ps','1']); L.file('in.film_template')"
    ```

=== "Linux"

    ```bash
    python3 -c "from lammps import lammps; L=lammps(cmdargs=['-var','heat_ps','2','-var','hold_ps','1','-var','cool_ps','1','-var','dump_ps','1']); L.file('in.film_template')"
    ```

Expected: `Deleted 687 atoms, new total = 9734`; energy per atom after minimization −3.43 eV; `=== DONE ===`.

## `in.cho`

ReaxFF C/H/O example: 105 atoms at 500 K for 0.75 ps. Needs the two data files downloaded next to it ([ReaxFF example](../examples/reaxff-cho.md)).

Expected: `=== DONE ===`. Temperature starts at 0 K (the input sets no initial velocities) and the thermostat pulls it up toward 500 K: about 550 K at the last step in our test. `Unrecognized pair style 'reaxff'` means your LAMMPS lacks REAXFF.

## `run_lammps.slurm`

Slurm job script template. Runs on the Slurm cluster only.

1. Copy into the run folder: `cp ~/hoffman2-lammps-guide/docs/files/run_lammps.slurm .`
2. Edit (`nano run_lammps.slurm`): `--account`, `--job-name`, `--time`, `--ntasks`, the `LMP=` path, and the `-in` input file.
3. Check and submit: `h2 validate run_lammps.slurm` then `sbatch run_lammps.slurm`.

Expected: `Submitted batch job <id>`; then `joblog.<id>` starts with `Job <id> on <node> with N tasks`.

If you edited it on Windows and get `/bin/bash^M: bad interpreter`: `sed -i 's/\r$//' run_lammps.slurm`.

## `make_jobscript_sge.sh`

Writes a working Grid Engine job script for the legacy cluster, with full paths to `mpirun`/`lmp_mpi`.

```bash
bash make_jobscript_sge.sh <job_name> <input_file> [cores=8] [walltime=12:00:00] [mem_per_core=2G]
```

Expected: prints the new `run_<job_name>.sh`, ending with `Check it, then submit with:  qsub run_<job_name>.sh`. If it says `could not find mpirun and/or lmp_mpi`, you're not on the legacy cluster or the module name changed (`module avail lammps`).

## `build_lammps.sh`

Builds LAMMPS (latest stable) into `~/software/lammps/build/lmp` on the Slurm cluster, with MANYBODY, REAXFF, EXTRA-COMPUTE, MOLECULE, KSPACE. ⚠️ Not yet run on Hoffman2.

```bash
srun --time=02:00:00 --cpus-per-task=8 --mem=16G --pty bash -l     # get a compute node
bash ~/hoffman2-lammps-guide/docs/files/build_lammps.sh
```

Expected: ends with `Built: /u/home/.../software/lammps/build/lmp` and a package list including MANYBODY and REAXFF.

## `plot_thermo.py`

Reads `log.lammps`, joins all run stages, skips minimization output, writes a CSV and a PNG plot.

=== "macOS"

    ```bash
    python3 plot_thermo.py log.lammps
    python3 plot_thermo.py log.lammps --cols temp 'c_msd[4]' --out T1100_s1
    open thermo.png
    ```

=== "Windows"

    ```powershell
    py plot_thermo.py log.lammps
    py plot_thermo.py log.lammps --cols temp 'c_msd[4]' --out T1100_s1
    start thermo.png
    ```

=== "Linux"

    ```bash
    python3 plot_thermo.py log.lammps
    python3 plot_thermo.py log.lammps --cols temp 'c_msd[4]' --out T1100_s1
    xdg-open thermo.png
    ```

| Option | Meaning |
|---|---|
| `--cols a b c` | Only these columns (names from the log header; case doesn't matter) |
| `--out NAME` | Output `NAME.csv` and `NAME.png` (default: from the log name, e.g. `log.film1` → `film1`, `log.lammps` → `thermo`) |

Expected output:

```
note: skipped 1 thermo block(s) with different columns (e.g. minimization)
5 rows, columns: Step Time Temp PotEng v_pe_atom c_msd[4]
wrote film1.csv
wrote film1.png
```

Works without matplotlib too (writes only the CSV). Also runs on Hoffman2. If `python3` there has no matplotlib, `pip install --user matplotlib` once, or just use the CSV.

## `analyze_orientation.py`

Per-frame structure and orientation, the lab's standard numbers: FCC/HCP/BCC/Other %, % of FCC atoms with (111) within 5° of z, % (100), and optionally the grain count.

=== "macOS"

    ```bash
    python3 analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

=== "Windows"

    ```powershell
    py analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

=== "Linux"

    ```bash
    python3 analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

| Option | Default | Meaning |
|---|---|---|
| `--type N ...` | all | Only count these atom types (e.g. `--type 1` = film without the type-2 template) |
| `--window DEG` | 5 | Angle window for (111)/(100) |
| `--rmsd X` | 0.1 | PTM RMSD cutoff. `0` = classify every atom (see [the note on cutoff 0](../analysis/ovito.md#rmsd-cutoff-0-vs-01)) |
| `--grains` | off | Also run grain segmentation (min 50 atoms); slower |
| `--every N` | 1 | Only every Nth frame |
| `--out FILE` | `<input>_orientation.csv` | CSV name |

Expected output (film example, film atoms only, short test run):

```
traj.lammpstrj: 5 frame(s); window 5 deg; PTM RMSD cutoff 0.1; atom types [1]
       frame      timestep         atoms         FCC_%         HCP_%  ...  111_of_FCC_%  100_of_FCC_%
           0             0          7718          48.3           3.6  ...           3.5          21.5
```

Checked on perfect crystals: (111) → 100% (111); (100) → 100% (100); (569), (122), (110) → 0% (111) at 5°. At 15°, (569) wrongly counts as 99% (111), which is why the lab uses 5°.

Needs Python 3.11+ and `pip install ovito numpy`. No `ovito` wheel for Intel Macs: run it on Hoffman2 or another machine instead.

## `select_111_atoms.txt`

One long OVITO expression that selects FCC atoms with (111) facing up (5° window).

1. In OVITO: Polyhedral template matching with Output orientations on.
2. Add modification → Expression selection → paste the whole line.
3. The count at the bottom of the panel = number of (111) atoms. Add Assign color to highlight them.

Same on every OS. Details: [Measuring orientation](../analysis/orientation.md#in-ovito-highlight-the-111-atoms).

## Recipe inputs (`recipes/`)

Each recipe input starts with a header saying what it does, how to run it, the `-var` settings for a quick test, and what it writes. Summary:

| File | What | Needs | Quick test |
|---|---|---|---|
| [`in.lj_liquid`](../files/recipes/in.lj_liquid) | LJ liquid: RDF, MSD, diffusion | — | `-var neq 2000 -var nprod 2000` |
| [`in.water_spce`](../files/recipes/in.water_spce) | SPC/E water at 300 K, 1 atm | `water.mol` | `-var nmol 216 -var nnpt 2000 -var nprod 1000` |
| [`in.poiseuille`](../files/recipes/in.poiseuille) | Pressure-driven channel flow | — | `-var neq 2000 -var nprod 4000` |
| [`in.viscosity_mp`](../files/recipes/in.viscosity_mp) | Viscosity (Müller-Plathe) | — | `-var neq 2000 -var nprod 5000` |
| [`in.thermal_conductivity`](../files/recipes/in.thermal_conductivity) | Thermal conductivity (Müller-Plathe) | — | `-var neq 2000 -var nprod 5000` |
| [`in.polymer_melt`](../files/recipes/in.polymer_melt) | Bead-spring polymer melt | — | `-var nchains 50 -var nsoft 2000 -var neq 5000` |
| [`in.cu_tensile`](../files/recipes/in.cu_tensile) | Cu tensile test, stress–strain | `Cu_u3.eam` | `-var nx 6 -var neq 2000 -var strain 0.05` |
| [`in.cu_surface_energy`](../files/recipes/in.cu_surface_energy) | γ(111), γ(100), γ(110) | `Cu_u3.eam` | runs in seconds as is |
| [`in.cu_gb_energy`](../files/recipes/in.cu_gb_energy) | Σ5 grain-boundary energy with shift scan | `Cu_u3.eam` | ~35 s as is |

`fit_profile.py` turns the flow and transport profiles into a viscosity or thermal conductivity; each of those inputs prints the exact command at the end. Usage on each OS: [Fluids → fit_profile.py](../recipes/fluids.md#fit_profilepy).

## Files you download separately

| File | Get it with (on Hoffman2) | Used by |
|---|---|---|
| `Cu_u3.eam` | `curl -sL -o Cu_u3.eam https://raw.githubusercontent.com/lammps/lammps/develop/bench/Cu_u3.eam` | `in.film_template` |
| `Cu_mishin1.eam.alloy` | `curl -sL -o Cu_mishin1.eam.alloy https://raw.githubusercontent.com/lammps/lammps/develop/potentials/Cu_mishin1.eam.alloy` | `in.cu_test` |
| `data.CHO`, `ffield.reax.cho` | see [ReaxFF example](../examples/reaxff-cho.md#running-it) | `in.cho` |

On a Windows laptop, use `curl.exe` instead of `curl` in PowerShell.

## Files LAMMPS writes

| File | What | Keep? |
|---|---|---|
| `log.lammps` | Everything printed: thermo table, warnings, timing | Always |
| `traj.lammpstrj` | Trajectory (dump) | Download, then delete from scratch if big |
| `data.initial`, `data.after_*`, `data.final` | Snapshots after each stage | Keep `data.final` at least |
| `restart.*` | Binary restart files | Until the run is complete |
| `joblog.<id>` | Scheduler output/errors | Until the run is checked |
| `core.*` | Crash dumps, GBs | Delete |
| `log.cite` | Papers to cite for the features you used | Glance at it when writing up |
