# Job scripts: Grid Engine (legacy)

The legacy cluster (`hoffman2.idre.ucla.edu`, scheduler: Altair Grid Engine) is where all the lab's runs through Oct 2026 happened, and the only place with a LAMMPS module right now.

!!! warning "OARC is retiring this"

    OARC's Nov 2026 notices ask users not to submit new Grid Engine jobs unless their group has an exception, and the legacy cluster had shrunk to 49 nodes by Nov 5. Use [Slurm](slurm.md) where you can. This page documents the setup that's known to work, for as long as it's available.

## The easy way: the helper script

[`make_jobscript_sge.sh`](../files/make_jobscript_sge.sh) writes a working job script. On the legacy login node, in your run folder:

```bash
bash make_jobscript_sge.sh <job_name> <input_file> [cores=8] [walltime=12:00:00] [mem_per_core=2G]
bash make_jobscript_sge.sh cu_test in.cu_test 8 01:00:00
cat run_cu_test.sh          # always look before submitting
qsub run_cu_test.sh
```

It loads `lammps/29Sep2021_MB` on the login node, finds the full paths to `mpirun` and `lmp_mpi`, and writes them into the script.

## What it generates

```bash
#!/bin/bash
#$ -cwd
#$ -o joblog.$JOB_ID
#$ -j y
#$ -N cu_test
#$ -l h_rt=01:00:00,h_data=2G,arch=intel-gold*
#$ -pe shared 8

export LD_LIBRARY_PATH=/u/local/...            # copied from the login node
/u/local/.../mpirun -n $NSLOTS /u/local/.../lmp_mpi -in in.cu_test -log log.lammps
```

| Line | Meaning |
|---|---|
| `#$ -cwd` | Run in the submission folder |
| `#$ -o joblog.$JOB_ID` / `-j y` | All scheduler output and errors in one file |
| `#$ -N` | Job name in `qstat` |
| `h_rt` | Wall-time limit (default 2 h if not set) |
| `h_data` | Memory per core (default 1 GB) |
| `arch=intel-gold*` | Required for `lammps/29Sep2021_MB`: it crashes with `Illegal instruction` on other nodes and writes multi-GB `core.*` files |
| `-pe shared 8` | 8 cores on one node; `$NSLOTS` = 8 |
| `LD_LIBRARY_PATH` | Lets `mpirun`/`lmp_mpi` find their libraries without `module load` |

## Why full paths instead of `module load`?

The textbook script:

```bash
. /u/local/Modules/default/init/modules.sh
module load lammps/29Sep2021_MB
mpirun -n $NSLOTS lmp_mpi -in in.cu_test -log log.lammps
```

fails on some compute nodes (hit on node n6661):

```
ERROR: Unable to locate a modulefile for 'lammps/29Sep2021_MB'
line 11: mpirun: command not found
```

Resolving the paths on the login node and writing them in avoids that. By hand:

```bash
. /u/local/Modules/default/init/modules.sh
module load lammps/29Sep2021_MB
which mpirun lmp_mpi        # copy these paths into the script
```

## Group nodes (`highp`)

- The lab's group nodes are older E5-2650v4 chips (not intel-gold).
- Never combine `highp` with `arch=intel-gold*`: no node matches both, so the job waits forever.
- ⚠️ Whether `lammps/29Sep2021_MB` runs correctly on those nodes was never confirmed. Test with a 30-minute job before trusting it:
    ```bash
    #$ -l h_rt=00:30:00,h_data=2G,highp
    #$ -pe shared 12
    ```

## Other parallel environments

| `-pe` | Meaning |
|---|---|
| `shared n` | n cores on one node (what the lab uses) |
| `dc* n` | n cores on any nodes (multi-node MPI) |
| `node n` + `-l exclusive` | n whole nodes |

## Commands

```bash
qsub run.sh                 # submit
qstat -u $USER              # status: qw waiting, r running, Eqw error
myjobs                      # your jobs
qstat -j <id>               # details / why it's waiting
qdel <id>                   # cancel
qacct -j <id>               # stats after it finished (check maxvmem)
groupjobs                   # your group's pending jobs
myresources                 # what you're allowed to use
modify_resources_of_pending_job   # change a queued job's request
```

## Job arrays

```bash
#$ -t 1-4
#$ -o joblog.$JOB_ID.$TASK_ID
TEMPS=(0 900 1000 1100 1200)          # index 0 unused; tasks start at 1
T=${TEMPS[$SGE_TASK_ID]}
```

## Interactive (legacy)

```bash
qrsh -l h_rt=1:00:00,h_data=2G -pe shared 8
. /u/local/bin/set_qrsh_env.sh        # sets $NSLOTS etc. for MPI
```

See [Interactive sessions](interactive.md).
