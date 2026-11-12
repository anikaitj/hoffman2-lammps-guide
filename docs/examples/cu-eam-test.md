# Example: Cu EAM test run

The first thing every new member should run: ~4,000 Cu atoms at 300 K and 0 bar for 50 ps. It finishes in minutes. If it works, your whole setup (login, files, LAMMPS, job script, download, OVITO) works.

Input: [`in.cu_test`](../files/in.cu_test) · Potential: `Cu_mishin1.eam.alloy`

!!! success "Tested"

    Runs to `=== DONE ===` with LAMMPS 22 Jul 2025 on a workstation (short test).

## Steps on Hoffman2

```bash
# 1. Get this repo (once)
cd ~ && git clone https://github.com/anikaitj/hoffman2-lammps-guide.git

# 2. Make a run folder in scratch
mkdir -p $SCRATCH/cu_test && cd $SCRATCH/cu_test
cp ~/hoffman2-lammps-guide/docs/files/in.cu_test .

# 3. Get the potential and check it
curl -sL -o Cu_mishin1.eam.alloy \
  https://raw.githubusercontent.com/lammps/lammps/develop/potentials/Cu_mishin1.eam.alloy
head -3 Cu_mishin1.eam.alloy        # should mention Mishin ... (2001)
```

### 4a. Slurm (`hoffman2.oarc.ucla.edu`)

Needs LAMMPS on Slurm ([Getting LAMMPS](../lammps/getting-lammps.md)).

```bash
cp ~/hoffman2-lammps-guide/docs/files/run_lammps.slurm .
nano run_lammps.slurm        # set --account; set --time=00:30:00
h2 validate run_lammps.slurm
sbatch run_lammps.slurm
squeue --me
```

### 4b. Legacy Grid Engine (`hoffman2.idre.ucla.edu`)

```bash
cp ~/hoffman2-lammps-guide/docs/files/make_jobscript_sge.sh .
bash make_jobscript_sge.sh cu_test in.cu_test 8 01:00:00
qsub run_cu_test.sh
qstat -u $USER
```

## Done when

```bash
grep DONE log.lammps      # → === DONE ===
tail -3 log.lammps
```

Temperature should hover around 300 K and density around 8.8–8.9 g/cm³ (the workstation test gave 8.80–8.94 in the first 2 ps).

## On your laptop

Full step-by-step version, with what you should see after each step: [Your first simulation](../getting-started/first-run.md).

=== "macOS"

    ```bash
    mkdir -p ~/md-runs/cu_test && cd ~/md-runs/cu_test
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/cu_test/{traj.lammpstrj,log.lammps} .
    source ~/md-env/bin/activate
    python3 ~/hoffman2-lammps-guide/docs/files/plot_thermo.py log.lammps --cols temp density
    python3 ~/hoffman2-lammps-guide/docs/files/analyze_orientation.py traj.lammpstrj
    ```

=== "Windows"

    ```powershell
    mkdir $HOME\md-runs\cu_test -Force; cd $HOME\md-runs\cu_test
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/cu_test/traj.lammpstrj .
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/cu_test/log.lammps .
    & $HOME\md-env\Scripts\Activate.ps1
    py $HOME\hoffman2-lammps-guide\docs\files\plot_thermo.py log.lammps --cols temp density
    py $HOME\hoffman2-lammps-guide\docs\files\analyze_orientation.py traj.lammpstrj
    ```

=== "Linux"

    ```bash
    mkdir -p ~/md-runs/cu_test && cd ~/md-runs/cu_test
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/cu_test/{traj.lammpstrj,log.lammps} .
    source ~/md-env/bin/activate
    python3 ~/hoffman2-lammps-guide/docs/files/plot_thermo.py log.lammps --cols temp density
    python3 ~/hoffman2-lammps-guide/docs/files/analyze_orientation.py traj.lammpstrj
    ```

Expected (checked on a 10 ps version of this run): temperature ~300 K, density ~8.81 g/cm³; `analyze_orientation.py` → FCC 100%, (100) 100%, (111) 0%. This box is a plain `[100]` crystal, so that's right.

Open `traj.lammpstrj` in OVITO and add Polyhedral template matching: all green (FCC). The box is fully periodic (`p p p`), so there are no surfaces and no white skin.
