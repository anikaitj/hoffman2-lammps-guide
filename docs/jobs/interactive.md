# Interactive sessions

An interactive session gives you a shell on a compute node, so you can test inputs, build software or run short jobs by hand without breaking the login-node rules.

## Slurm

```bash
# 2 hours, 4 GB, 1 core
srun --time=02:00:00 --mem=4G --pty bash -l

# 2 hours, 8 MPI ranks for a LAMMPS test
srun --time=02:00:00 --ntasks=8 --mem-per-cpu=2G --pty bash -l

# on the group's nodes, 1 day (only if they're on Slurm)
srun --qos=highp --time=1-00:00:00 --cpus-per-task=4 --mem=16G --pty bash -l
```

Add `-A pi_<PI>` if you have more than one account. Then, inside the session:

```bash
module purge && module load intel/2026.0.0
cd $SCRATCH/test_run
mpirun -n 8 ~/software/lammps/build/lmp -in in.cu_test -var ... -log log.test
exit                        # ALWAYS exit when done, to free the cores
```

`salloc` is the other style: it reserves resources, and you run commands inside with `srun`/`mpirun`, then `exit`.

```bash
salloc --time=02:00:00 --ntasks=4 --mem-per-cpu=4G
```

## Legacy Grid Engine

```bash
qrsh -l h_rt=1:00:00,h_data=2G -pe shared 8
. /u/local/bin/set_qrsh_env.sh              # needed for MPI: sets $NSLOTS etc.
`which mpirun` -n $NSLOTS lmp_mpi -in in.cu_test
exit
```

Add `-now n` to wait in the queue instead of giving up when nodes aren't free right away. Don't forget `arch=intel-gold*` for the `_MB` LAMMPS module:

```bash
qrsh -l h_rt=1:00:00,h_data=2G,arch=intel-gold* -pe shared 8 -now n
```

## What to use interactive sessions for

- Testing a new input: run a few hundred steps (`-var hold_ps 1`) and check the log and frame 0 before a 12-hour job.
- Building LAMMPS ([Getting LAMMPS](../lammps/getting-lammps.md)).
- Timing: run 1,000–5,000 steps with 4, 8 and 16 cores and compare the `Performance:` lines ([Performance](performance.md)).
- Quick analysis on the cluster (e.g. Python over a big trajectory) instead of downloading it.

!!! tip "Short and small starts faster"

    The scheduler fits small, short requests into gaps. A 1-hour, 4-core session usually starts much sooner than an 8-hour, 24-core one.

!!! warning "A dropped connection ends the session"

    If your Wi-Fi blips, the session (and anything running in it) dies. For anything longer than a test, submit a batch job.
