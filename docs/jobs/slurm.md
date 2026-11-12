# Job scripts: Slurm

The Slurm cluster (`hoffman2.oarc.ucla.edu`) is where OARC wants all new jobs. Everything here is from OARC's [Computing with Slurm](https://www.hoffman2.idre.ucla.edu/Using-H2/Computing/Computing-Slurm.html) page.

!!! warning "LAMMPS on Slurm"

    As of Nov 10 2026, LAMMPS isn't installed on the Slurm cluster. These scripts assume you've built it ([Getting LAMMPS](../lammps/getting-lammps.md), route B) or that OARC has added a module. ⚠️ The lab hasn't run a LAMMPS job on Slurm yet. Whoever does first: update this page.

## Step 0: find your account

```bash
h2 whoami
sacctmgr -nP show assoc user=$USER format=account,qos
```

Your Slurm account looks like `pi_<PI username>`. It's not your login name. If you belong to more than one account, every job needs `-A <account>`, or it's rejected.

## The LAMMPS job script

[`run_lammps.slurm`](../files/run_lammps.slurm):

```bash
#!/bin/bash
#SBATCH --job-name=cu_test
#SBATCH --account=pi_CHANGEME            # from h2 whoami
#SBATCH --time=12:00:00                  # max 24 h (campus/shared), 14 days (highp)
#SBATCH --nodes=1
#SBATCH --ntasks=8                       # MPI ranks = cores
#SBATCH --mem-per-cpu=2G                 # ALWAYS set memory
#SBATCH --output=joblog.%j
##SBATCH --qos=highp                     # only if the group's nodes are on Slurm
##SBATCH -C intel-gold-6342              # optional: pin CPU type

module purge
module load intel/2026.0.0               # same modules as your LAMMPS build

LMP=$HOME/software/lammps/build/lmp

mpirun -n $SLURM_NTASKS $LMP -in in.cu_test -log log.lammps
```

Lines starting `##SBATCH` are switched off; remove one `#` to switch them on.

### Line by line

| Line | Meaning |
|---|---|
| `--job-name` | Name in `squeue` |
| `--account` | Which allocation the job charges to (free for us, but required) |
| `--time` | Wall-time limit, `HH:MM:SS` or `D-HH:MM:SS`. Killed at the limit. Default is only 2 h. |
| `--nodes=1` | Keep the job on one node (faster communication; OARC recommends it when the job fits) |
| `--ntasks` | Number of MPI processes. `$SLURM_NTASKS` holds it. |
| `--mem-per-cpu` | Memory per core. Slurm has no default: without it the job takes all the node's memory. `--mem` is per node instead. |
| `--output=joblog.%j` | Scheduler output file; `%j` = job ID. Errors go here too. |
| `--qos=highp` | Run on the group's own nodes (up to 14 days). Only works if those nodes have moved to Slurm. |
| `-C <type>` | Restrict to a CPU type (`intel-gold-6342`, `intel-xeon6-6736P`, `amd-epyc-9634`) |
| `module purge` | Start clean: every shell loads `intel/2026.2.0` by default, which can clash |
| `mpirun -n ...` | Use `mpirun`, not `srun`, for MPI programs on Hoffman2 (OARC: `srun` breaks Intel MPI) |

!!! danger "No `$SCRATCH` in `#SBATCH` lines"

    Variables aren't expanded in `#SBATCH` lines. Use a full path, or (simplest) leave the path off and submit from the run folder: Slurm starts the job in the folder you submitted from.

## Check, submit, watch

```bash
h2 validate run_lammps.slurm      # catches mistakes before you wait in the queue
sbatch run_lammps.slurm           # → Submitted batch job 1234567
squeue --me                       # your jobs
tail -f log.lammps                # live progress (Ctrl+C to stop watching)
```

More on [Submit & monitor](monitoring.md).

## How many cores and how much memory?

- Memory: EAM copper uses very little, well under 1 GB per core for systems up to ~100k atoms. `--mem-per-cpu=2G` is plenty. ReaxFF needs more.
- Cores: 8–24 for 10k–50k atoms is a sensible starting range. Once each core has only a few hundred atoms, adding more cores helps less and less. Measure it rather than guessing: [Performance](performance.md).
- Time: run a short test first and read the `Performance:` line in `log.lammps` to estimate. Ask for ~1.5× what you expect.

## Temperature sweeps and repeats with job arrays

One script, many runs. Each array task gets a different `$SLURM_ARRAY_TASK_ID`.

```bash
#!/bin/bash
#SBATCH --job-name=Tsweep
#SBATCH --account=pi_CHANGEME
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem-per-cpu=2G
#SBATCH --array=0-3
#SBATCH --output=joblog.%A_%a          # %A = array ID, %a = task index

module purge
module load intel/2026.0.0
LMP=$HOME/software/lammps/build/lmp

TEMPS=(900 1000 1100 1200)
T=${TEMPS[$SLURM_ARRAY_TASK_ID]}
D=T${T}
mkdir -p $D && cd $D
cp ../in.film_template ../Cu_u3.eam .

mpirun -n $SLURM_NTASKS $LMP -in in.film_template -var T_hold $T -log log.lammps
```

For repeats with different random seeds (needed before claiming a result), swap the list:

```bash
SEEDS=(482917 111234 221234 331234)
S=${SEEDS[$SLURM_ARRAY_TASK_ID]}
... -var vseed $S ...
```

Max array index is 1000. Don't use `--mail-type=ARRAY_TASKS` (one email per task).

## Chaining jobs (run B after A finishes)

```bash
jid=$(sbatch --parsable stage1.slurm)
sbatch --dependency=afterok:$jid stage2.slurm
```

`afterok` starts stage 2 only if stage 1 succeeded. Useful with [restarts](restarts-long-runs.md) for runs longer than 24 h.

## Email when a job ends

```bash
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=you@ucla.edu
```

## Converting an old Grid Engine script

```bash
h2 convert-uge run_old.sh > run_new.slurm
# then add:  #SBATCH -A pi_<PI>   (and --qos=highp only for group nodes)
h2 validate run_new.slurm
```

| Grid Engine | Slurm |
|---|---|
| `#$ -l h_rt=8:00:00` | `#SBATCH --time=8:00:00` |
| `#$ -l h_data=4G` | `#SBATCH --mem-per-cpu=4G` |
| `#$ -pe shared 4` (threads) | `#SBATCH --ntasks=1` + `--cpus-per-task=4` |
| `#$ -pe dc* 32` (MPI) | `#SBATCH --ntasks=32` |
| `#$ -pe shared 8` used with `mpirun -n $NSLOTS` (what the lab did) | `#SBATCH --nodes=1` + `--ntasks=8`, and `mpirun -n $SLURM_NTASKS` |
| `#$ -l highp` | `#SBATCH --qos=highp` |
| `#$ -l arch=intel-gold*` | `#SBATCH -C intel-gold-6342` (if needed) |
| `#$ -o joblog.$JOB_ID` + `#$ -j y` | `#SBATCH --output=joblog.%j` |
| `#$ -cwd` | not needed |
| `#$ -t 1-100` | `#SBATCH --array=1-100` |
| `$JOB_ID` / `$SGE_TASK_ID` / `$NSLOTS` | `$SLURM_JOB_ID` / `$SLURM_ARRAY_TASK_ID` / `$SLURM_NTASKS` |

!!! note "Our old scripts used `-pe shared` for MPI"

    `h2 convert-uge` will translate `-pe shared 8` as 1 task × 8 threads, which is wrong for an MPI LAMMPS run. Change it to `--ntasks=8` by hand.
