# Troubleshooting

Every error here is one the lab has hit, or one OARC documents. First steps for almost anything:

```bash
cat joblog.<jobid>              # scheduler output + errors
tail -30 log.lammps             # where LAMMPS stopped
sacct -j <jobid> --format=JobID,State,Elapsed,ExitCode   # Slurm: how it ended
```

## Login and accounts

### Password works on one cluster but not the other

Slurm and legacy passwords are separate now. Slurm: change in ColdFront. Legacy: change in SIM.

### `Permission denied` / can't log in at all

Account not approved yet (sponsor must approve in SIM/ColdFront), or wrong host. Slurm is `hoffman2.oarc.ucla.edu`; legacy is `hoffman2.idre.ucla.edu`.

### `mkdir: cannot create directory '/u/scratch/...': Permission denied`

Wrong scratch path, e.g. using your UCLA email name instead of your Hoffman2 username. Run `echo $SCRATCH`.

## Slurm

### Job rejected: account problem

You belong to more than one account. Add `#SBATCH -A pi_<PI>` (find it with `h2 whoami`).

### Job pending for a long time

```bash
h2 why-pending <jobid>
squeue --me            # REASON column
```

- Asked for more cores/memory than one node has → never starts. Reduce, or check node sizes ([overview](../getting-started/hoffman2-overview.md#node-types-on-slurm)).
- Asked for `--qos=highp` but the group's nodes aren't on Slurm → won't run.
- Large or long requests wait longer. Try fewer cores or a shorter time.

### Job killed at 2 hours

No `--time` → default is 2 h. Set `#SBATCH --time=...`.

### `OUT_OF_MEMORY` in `sacct`

Raise `--mem-per-cpu`. (On Slurm, `MaxRSS` is empty; measure memory with `/usr/bin/time -v` in an interactive session.)

### `$SCRATCH` in an `#SBATCH` line didn't work

Variables aren't expanded in `#SBATCH` lines. Use a full path, or submit from the run folder and omit the path.

### `srun` gives weird MPI behaviour

Use `mpirun`, not `srun`, for MPI programs on Hoffman2 (OARC: `srun` breaks Intel MPI; with Open MPI it runs independent copies).

### `qsub` / `qstat` just print help on the Slurm cluster

On the Slurm login nodes those commands only print the Slurm equivalents. Use `sbatch`, `squeue`, `scancel`, or log into the legacy host.

## Legacy Grid Engine

### `ERROR: Unable to locate a modulefile for 'lammps/29Sep2021_MB'` + `mpirun: command not found`

Job landed on a node without the module. Use full paths instead of `module load`: regenerate with [`make_jobscript_sge.sh`](../files/make_jobscript_sge.sh). See [Grid Engine](../jobs/grid-engine-legacy.md#why-full-paths-instead-of-module-load).

### `Illegal instruction` (signal 4), and huge `core.*` files appear

Ran on a node type the binary wasn't built for (`_MB` module needs `arch=intel-gold*`), or ran on the login node. Fix the `-l` line, then clean up:

```bash
find . -name "core.*" -size +100M          # list first
find . -name "core.*" -size +100M -delete  # then delete
```

With your own Slurm build: don't compile with `-march=native`, or pin jobs to that CPU type with `-C`.

### Job sits in `qw` forever

- `highp` and `arch=intel-gold*` together (no node has both). Remove one.
- Request too big or too long.
- `qstat -j <id>` shows scheduling info at the bottom.

### Job vanished within a minute, no `log.lammps`

Crashed before LAMMPS started. `cat joblog.<id>` has the reason (module, path or arch).

## LAMMPS errors

### `Unrecognized pair style 'eam'` / `'eam/alloy'`

Build without MANYBODY (e.g. legacy `lammps/29Sep2021` without `_MB`). Use `_MB`, or build with `-D PKG_MANYBODY=on`.

### `Unrecognized pair style 'reaxff'`

Build without REAXFF. Check with `lmp -h`; build with `-D PKG_REAXFF=on`. Old inputs using `reax/c` need renaming to `reaxff`.

### `ERROR: Thermo style does not use temp`

`thermo_modify temp X` needs the keyword `temp` in `thermo_style`. Write `thermo_style custom step time temp ...` (not `c_X`).

### `Lost atoms` / `Out of range atoms` / energies explode to `nan`

Atoms too close (missing `delete_atoms overlap`), no `minimize` before dynamics, timestep too large, or atoms flying out of a non-periodic box. Fix the structure, minimize, keep 1 fs (0.25 fs ReaxFF).

### `Cannot open file Cu_u3.eam` (or any potential)

Potential not in the run folder. `ls`, or use a full path in `pair_coeff`. If the file exists but is HTML, the download failed; re-download.

### `Lattice orient vectors are not orthogonal` / `not right-handed`

Check x·y = y·z = x·z = 0 and that x × y points along z. Use the [orientation table](../lammps/building-structures.md#orientation-sets-for-every-grain-type-we-use).

### Regions in the wrong place with a rotated lattice

`units lattice` with `orient`. Use `units box` (Å).

### `WARNING: Using fix shake with minimization`

Expected in the water recipe: SHAKE constraints are only approximately applied during `minimize`. Harmless.

### `ERROR: Molecule auto special bond generation overflow`

`create_box` didn't reserve enough room for bonded neighbours. Raise `extra/special/per/atom` (the polymer recipe uses 10).

### `ERROR: Thermo keyword pxx in variable requires thermo to use/init press`

A variable used `pxx` (etc.) but thermo doesn't print pressure. Define `compute p all pressure thermo_temp` and use `c_p[1]` instead, as in the tensile recipe.

### `ERROR: Unknown create_atoms command option`

`create_atoms 1 b` treats `b` as an option. Write `create_atoms 1 box` (the special word) or `create_atoms 1 region b`.

### `WARNING: Communication cutoff ... is shorter than a bond length based estimate`

Bonds can be longer than the pair cutoff. Add `comm_modify cutoff 2.0` (or more) for bonded models with short pair cutoffs.

### `Non-numeric atom coords - simulation unstable` right after building

Two atoms sit on top of each other, often because two `create_atoms` regions share a boundary plane. Leave a gap between regions (half a lattice spacing) or use `delete_atoms overlap`.

### `WARNING: Temperature for thermo pressure is not for group all`

After `thermo_modify temp` with a subgroup. Harmless for films.

## Laptop (macOS / Windows / Linux)

### `/bin/bash^M: bad interpreter` or `$'\r': command not found` on Hoffman2

The file has Windows (CRLF) line endings, usually because it was edited on Windows. Fix on Hoffman2:

```bash
sed -i 's/\r$//' run_lammps.slurm       # any affected file
```

Prevent it: in VS Code, click CRLF in the status bar and choose LF. This repo's `.gitattributes` keeps cloned files LF.

### Windows: `ssh` (or `scp`) is not recognized

Install OpenSSH Client: Settings → System → Optional features → Add a feature → OpenSSH Client. Reopen PowerShell.

### Windows: `python3` opens the Microsoft Store or isn't found

Use `py` (or `python`). Install Python from python.org or `winget install --id Python.Python.3.13 -e`.

### Windows: `curl` gives a strange error or a PowerShell table

In Windows PowerShell 5.1, `curl` is an alias for `Invoke-WebRequest`. Use `curl.exe`.

### Windows: `Activate.ps1 cannot be loaded because running scripts is disabled`

Run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again.

### Windows: `rsync` not found

Not included with Windows. Use `scp -r`, a GUI (WinSCP/FileZilla), or WSL ([Moving files](../jobs/moving-files.md)).

### `pip install ovito` fails

- Needs Python 3.11+: check `python3 --version` / `py --version`.
- No wheel for Intel Macs: use the OVITO desktop app, or run `analyze_orientation.py` on Hoffman2 or another machine.

### `ModuleNotFoundError: No module named 'ovito'` (or `matplotlib`, `lammps`)

Your virtual environment isn't active (no `(md-env)` in the prompt). Activate it ([Laptop setup](../getting-started/laptop-setup.md#create-a-python-environment-for-the-lab-tools)) or `pip install` the package into it.

### macOS: `xcrun: error: invalid active developer path`

Run `xcode-select --install` (needed for git).

### macOS `zsh: no matches found: c_msd[4]`

zsh treats `[ ]` as a pattern. Quote it: `'c_msd[4]'`.

## Files and transfers

### Lots of `command not found` after pasting

File contents pasted into the shell instead of into `nano` / `cat > file << 'EOF'`. Recreate the file properly ([Linux basics](../getting-started/linux-basics.md)).

### `scp: ... No such file or directory` when downloading

The job hasn't finished, or never ran. On Hoffman2: `ls` the folder and `grep DONE log.lammps` first. Also check you ran `scp` on your laptop.

### Files disappeared from scratch

Scratch purges files older than 14 days. Download results promptly; keep inputs in home or git.

## Results look wrong

Checklist from past Cu runs:

- Fully periodic (`p p p`) → no surface driving force for (111).
- Above the potential's melting point (Cu_u3 ≈ 1300 K), or never melted when you meant to. Check MSD.
- Cooling far too fast.
- Element order in `pair_coeff` doesn't match atom types.
- Gaps between grains collapsing and twisting the structure.
- Orientation judged from RDF or a 15° window.
- Only one random seed.

## Still stuck?

Post in the group chat with: the job script, `cat joblog.<id>`, `tail -30 log.lammps`, and which cluster you're on. For cluster problems, OARC [Technical support](https://www.hoffman2.idre.ucla.edu/Education-And-Support/Technical-support.html).
