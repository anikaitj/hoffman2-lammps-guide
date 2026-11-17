# Running LAMMPS on Hoffman2

A complete guide for members of UCLA's Nano Transport Research Group (NTRG) to running molecular dynamics (MD) simulations in LAMMPS on the Hoffman2 cluster: from getting an account to measuring Cu(111) orientation in OVITO, plus tested recipes for fluids, water, flow, polymers, mechanical tests, surface and grain-boundary energies, and GPU runs.

It's built from the group's own runs (May–Nov 2026), OARC's official Hoffman2 documentation, and the LAMMPS manual. Example inputs and scripts were tested before being added. Anything not yet confirmed is marked ⚠️.

You can follow it from a Mac, a Windows PC or a Linux laptop. Simulations run on Hoffman2 (Linux), so cluster commands are the same for everyone. Every step you run on your own computer has tabs for macOS, Windows and Linux: pick yours once and the whole site follows.

!!! warning "Hoffman2 is switching schedulers (Nov 2026)"

    ~94% of Hoffman2 has moved from Grid Engine (`qsub`) to Slurm (`sbatch`), and OARC asks users not to submit new Grid Engine jobs. But LAMMPS isn't installed on Slurm yet. Read [Getting LAMMPS](lammps/getting-lammps.md) first for the current options.

## New here? Follow this path

1. [MD basics in plain language](lammps/md-basics.md): what a simulation is, no equations
2. [Hoffman2 overview](getting-started/hoffman2-overview.md): how the cluster works, Slurm vs legacy
3. [Set up your laptop](getting-started/laptop-setup.md): macOS, Windows or Linux
4. [Get an account and log in](getting-started/account-and-login.md)
5. [Your first simulation, start to finish](getting-started/first-run.md): an 8-step walkthrough with what you should see at each step
6. [Linux basics](getting-started/linux-basics.md) and [Storage](getting-started/storage.md)
7. Learn [Input scripts](lammps/input-scripts.md) and [Building structures](lammps/building-structures.md)
8. Run the [film-on-template example](examples/film-template.md) and analyse it ([OVITO](analysis/ovito.md), [Measuring orientation](analysis/orientation.md))
9. Doing something else (liquids, polymers, mechanics...)? Start from [Simulation recipes](recipes/index.md)

## Quick reference

| Task | Slurm (`hoffman2.oarc.ucla.edu`) | Legacy (`hoffman2.idre.ucla.edu`) |
|---|---|---|
| Log in | `ssh <user>@hoffman2.oarc.ucla.edu` | `ssh <user>@hoffman2.idre.ucla.edu` |
| Submit | `sbatch run_lammps.slurm` | `qsub run.sh` |
| My jobs | `squeue --me` | `qstat -u $USER` |
| Cancel | `scancel <id>` | `qdel <id>` |
| Interactive | `srun --time=1:00:00 --ntasks=4 --mem-per-cpu=2G --pty bash -l` | `qrsh -l h_rt=1:00:00,h_data=2G -pe shared 4` |
| Run folder | `$SCRATCH` (purged after 14 days) | same |
| Big transfers | `dtn.hoffman2.idre.ucla.edu` | same |

## Downloads

| File | What it is |
|---|---|
| [`run_lammps.slurm`](files/run_lammps.slurm) | Slurm job script template for LAMMPS |
| [`build_lammps.sh`](files/build_lammps.sh) | Build your own LAMMPS on Slurm (⚠️ untested on Hoffman2) |
| [`make_jobscript_sge.sh`](files/make_jobscript_sge.sh) | Writes a working legacy Grid Engine job script |
| [`in.cu_test`](files/in.cu_test) | Small Cu test (~4,000 atoms, 50 ps) |
| [`in.film_template`](files/in.film_template) | Polycrystalline Cu film on a (111) template, annealed below melting |
| [`in.cho`](files/in.cho) | ReaxFF C/H/O example |
| [`plot_thermo.py`](files/plot_thermo.py) | Turns `log.lammps` into a CSV and plots (macOS/Windows/Linux) |
| [`analyze_orientation.py`](files/analyze_orientation.py) | FCC/HCP %, (111) % and grain count per frame (macOS/Windows/Linux) |
| [`select_111_atoms.txt`](files/select_111_atoms.txt) | OVITO expression that selects (111) atoms (5° window) |

How to run each one on your system: [Files & scripts reference](help/files-reference.md).

## Rules that save the most time

!!! danger "Read these before your first job"

    1. Never run LAMMPS on a login node. Use a job or an interactive session.
    2. Run in `$SCRATCH`, and download results within 14 days (scratch is purged).
    3. Always set time and memory in job scripts. Slurm defaults to 2 hours and has no memory default.
    4. Films (`p p f` + vacuum), not fully periodic boxes, for anything about surface orientation.
    5. Check melting with MSD in every run; Cu_u3.eam melts at ~1300 K.
    6. Orientation from PTM (5° window), never from RDF peaks.
    7. 3+ random seeds before calling something a result.
    8. Legacy cluster only: use `lammps/29Sep2021_MB` with `arch=intel-gold*`, never with `highp`.

## Maintainers

Anikait Jain (NTRG). If something here is wrong or out of date, especially after the Slurm switch, see [Contributing](help/contributing.md).
