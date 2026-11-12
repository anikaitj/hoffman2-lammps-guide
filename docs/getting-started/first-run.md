# Your first simulation, start to finish

A complete walkthrough: from a fresh laptop to a plotted result and a picture in OVITO. It uses the small [Cu test](../examples/cu-eam-test.md) (~4,000 atoms, a few minutes). Every step says where to type it.

Before you start: a Hoffman2 account ([Account & login](account-and-login.md)) and your laptop set up ([Laptop setup](laptop-setup.md)).

!!! info "Which cluster?"

    LAMMPS is only installed on the legacy cluster right now (Nov 2026). Steps 3–5 show both: use Legacy today, and Slurm once LAMMPS is there or you've [built it](../lammps/getting-lammps.md).

---

## Step 1: Log in · *laptop*

=== "macOS"

    Open Terminal:

    ```bash
    ssh <username>@hoffman2.idre.ucla.edu
    ```

=== "Windows"

    Open PowerShell:

    ```powershell
    ssh <username>@hoffman2.idre.ucla.edu
    ```

=== "Linux"

    Open a terminal:

    ```bash
    ssh <username>@hoffman2.idre.ucla.edu
    ```

Type your password (nothing shows while you type; that's normal). You're on Hoffman2 when the prompt looks like `[<username>@login1 ~]$`.

(Use `hoffman2.oarc.ucla.edu` instead for the Slurm cluster.)

## Step 2: Get the files · *Hoffman2*

From here until step 6, everything is typed on Hoffman2, so it's the same on every laptop.

```bash
cd ~
git clone https://github.com/anikaitj/hoffman2-lammps-guide.git

mkdir -p $SCRATCH/cu_test
cd $SCRATCH/cu_test
cp ~/hoffman2-lammps-guide/docs/files/in.cu_test .

curl -sL -o Cu_mishin1.eam.alloy \
  https://raw.githubusercontent.com/lammps/lammps/develop/potentials/Cu_mishin1.eam.alloy

ls
head -3 Cu_mishin1.eam.alloy
```

You should see: `Cu_mishin1.eam.alloy  in.cu_test`, and a header mentioning Mishin ... (2001).

## Step 3: Make the job script · *Hoffman2*

=== "Legacy (works today)"

    ```bash
    cp ~/hoffman2-lammps-guide/docs/files/make_jobscript_sge.sh .
    bash make_jobscript_sge.sh cu_test in.cu_test 8 00:30:00
    ```

    You should see the generated `run_cu_test.sh` printed, with `arch=intel-gold*` and full paths to `mpirun` and `lmp_mpi` on the last line.

=== "Slurm"

    ```bash
    cp ~/hoffman2-lammps-guide/docs/files/run_lammps.slurm .
    h2 whoami                       # note your account, e.g. pi_xxxx
    nano run_lammps.slurm
    ```

    In nano, change: `--account=pi_CHANGEME` → your account; `--time=12:00:00` → `--time=00:30:00`. Leave `-in in.cu_test`. Save: Ctrl+O, Enter, Ctrl+X.

    ```bash
    h2 validate run_lammps.slurm
    ```

## Step 4: Submit · *Hoffman2*

=== "Legacy (works today)"

    ```bash
    qsub run_cu_test.sh
    qstat -u $USER
    ```

    `qw` = waiting, `r` = running.

=== "Slurm"

    ```bash
    sbatch run_lammps.slurm
    squeue --me
    ```

    `PD` = waiting, `R` = running.

## Step 5: Watch it and check it finished · *Hoffman2*

```bash
tail -5 log.lammps          # run again every minute; step numbers should go up
grep DONE log.lammps        # prints === DONE === when finished
```

When the job is gone from `qstat`/`squeue` and `grep DONE` prints `=== DONE ===`, it worked. If not → [Troubleshooting](../help/troubleshooting.md).

Then leave Hoffman2:

```bash
exit
```

## Step 6: Download the results · *laptop*

=== "macOS"

    ```bash
    mkdir -p ~/md-runs/cu_test && cd ~/md-runs/cu_test
    scp <username>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<username>/cu_test/log.lammps .
    scp <username>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<username>/cu_test/traj.lammpstrj .
    ls
    ```

=== "Windows"

    ```powershell
    mkdir $HOME\md-runs\cu_test -Force; cd $HOME\md-runs\cu_test
    scp <username>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<username>/cu_test/log.lammps .
    scp <username>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<username>/cu_test/traj.lammpstrj .
    ls
    ```

=== "Linux"

    ```bash
    mkdir -p ~/md-runs/cu_test && cd ~/md-runs/cu_test
    scp <username>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<username>/cu_test/log.lammps .
    scp <username>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<username>/cu_test/traj.lammpstrj .
    ls
    ```

`<l>` is the first letter of your username (e.g. `/u/scratch/j/joebruin/`).

## Step 7: Plot temperature and density · *laptop*

Copy `plot_thermo.py` from your clone of the repo (`hoffman2-lammps-guide/docs/files/`) into this folder, activate your Python environment, and run it:

=== "macOS"

    ```bash
    cp ~/hoffman2-lammps-guide/docs/files/plot_thermo.py .
    source ~/md-env/bin/activate
    python3 plot_thermo.py log.lammps --cols temp density
    open thermo.png
    ```

=== "Windows"

    ```powershell
    copy $HOME\hoffman2-lammps-guide\docs\files\plot_thermo.py .
    & $HOME\md-env\Scripts\Activate.ps1
    py plot_thermo.py log.lammps --cols temp density
    start thermo.png
    ```

=== "Linux"

    ```bash
    cp ~/hoffman2-lammps-guide/docs/files/plot_thermo.py .
    source ~/md-env/bin/activate
    python3 plot_thermo.py log.lammps --cols temp density
    xdg-open thermo.png
    ```

You should see: temperature fluctuating around 300 K and density around 8.8–8.9 g/cm³. The numbers are also in `thermo.csv` (opens in Excel/Numbers/LibreOffice).

## Step 8: Look at it in OVITO · *laptop*

1. Open OVITO → File → Load File → `traj.lammpstrj`.
2. Add modification… → Polyhedral template matching.
3. Almost every atom should be green (FCC). Press ▶ to play through the frames.

Or measure it with the script (needs the `ovito` Python module):

=== "macOS"

    ```bash
    cp ~/hoffman2-lammps-guide/docs/files/analyze_orientation.py .
    python3 analyze_orientation.py traj.lammpstrj
    ```

=== "Windows"

    ```powershell
    copy $HOME\hoffman2-lammps-guide\docs\files\analyze_orientation.py .
    py analyze_orientation.py traj.lammpstrj
    ```

=== "Linux"

    ```bash
    cp ~/hoffman2-lammps-guide/docs/files/analyze_orientation.py .
    python3 analyze_orientation.py traj.lammpstrj
    ```

This box is a perfect `[100]`-oriented crystal, so expect FCC near 100% and (100) near 100%.

## Done

You've used every part of the workflow. Next:

- Understand what the input did: [MD basics](../lammps/md-basics.md) and [Input scripts](../lammps/input-scripts.md)
- A research-style run: [Film on a (111) template](../examples/film-template.md)
- Every file and how to run it: [Files & scripts reference](../help/files-reference.md)

### Checklist

- [ ] Logged in to Hoffman2
- [ ] Cloned the repo and made a run folder in `$SCRATCH`
- [ ] Downloaded the potential
- [ ] Made and submitted a job script
- [ ] Saw `=== DONE ===`
- [ ] Downloaded `log.lammps` and `traj.lammpstrj`
- [ ] Plotted with `plot_thermo.py`
- [ ] Opened the trajectory in OVITO
