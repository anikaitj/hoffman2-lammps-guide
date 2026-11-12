# Hoffman2 overview

Hoffman2 is UCLA's shared high-performance computing (HPC) cluster, run by the Office of Advanced Research Computing (OARC), formerly IDRE. It's free for the group in both shared and highp modes (IDRE confirmed this in Oct 2026).

## Two clusters right now (Nov 2026)

Hoffman2 is part-way through moving from the Altair Grid Engine scheduler to Slurm. Both run at the same time and share your files.

| | Slurm cluster (current) | Legacy Grid Engine cluster |
|---|---|---|
| Login | `hoffman2.oarc.ucla.edu` | `hoffman2.idre.ucla.edu` |
| Submit / watch / cancel | `sbatch` / `squeue --me` / `scancel` | `qsub` / `qstat` / `qdel` |
| Size (OARC news, Nov 5 2026) | ~94% of nodes: 777 nodes, 30,904 cores, 33 GPU nodes | 49 nodes, 2,300 cores, 7 GPU nodes |
| LAMMPS module | Not installed yet (see [Getting LAMMPS](../lammps/getting-lammps.md)) | `lammps/29Sep2021_MB` (what the lab has used) |
| Password | Set in ColdFront | Set in SIM |
| OARC's position | Use this | "Do not submit new jobs with Grid Engine" unless your group has an exception |

!!! warning "What this means for us"

    All the lab's working runs so far used the legacy cluster. OARC is asking everyone to move to Slurm, but LAMMPS isn't on Slurm yet. Until it is, the options are on [Getting LAMMPS](../lammps/getting-lammps.md). Your `$HOME`, `$SCRATCH` and project folders are the same on both clusters, so files don't need to move.

## How a cluster works (the mental model)

```
 your laptop ──ssh──▶ LOGIN NODE ──sbatch/qsub──▶ SCHEDULER ──▶ COMPUTE NODES
                      (edit files,                (queues jobs,   (actually run
                       submit jobs,                picks nodes)    LAMMPS)
                       light work only)
```

- Login node: where you land after `ssh`. Shared by everyone. Only for editing, moving files, compiling small things and submitting jobs. Never run simulations here.
- Scheduler: you describe what you need (cores, memory, time) in a job script; it queues the job and runs it when resources are free.
- Compute nodes: the machines that run your job. You don't log into them directly (except through an [interactive session](../jobs/interactive.md)).
- Data transfer nodes (`dtn.hoffman2.idre.ucla.edu`): for moving large files. See [Moving files](../jobs/moving-files.md).

## Node types on Slurm

From OARC's Slurm page (`CLUSTER_AT_A_GLANCE`, partial list):

| CPU type | Nodes | Cores/node | GB RAM/core |
|---|---|---|---|
| `intel-gold-6342` | 42 | 48 | 10.4 |
| `intel-xeon6-6736P` | 56 | 72 | 6.9 |
| `amd-epyc-9634` | 12 | 84 | 4.5 |

A request bigger than one node's cores or memory never starts. Pin a type with `-C <cpu-type>` (e.g. `-C intel-gold-6342`).

## Where jobs run (Slurm)

| Job type | How you get it | Max time | Runs on |
|---|---|---|---|
| campus | Automatic, for groups with no nodes on Slurm | 24 h | OARC-owned nodes |
| shared | Automatic, for groups whose nodes have moved | 24 h | Other groups' idle nodes |
| highp | `--qos=highp` | 14 days | Your group's own nodes |

Don't set `--partition` or `--qos` yourself otherwise; Slurm routes jobs automatically. Default time is 2 h if you don't ask for more.

Our lab has its own group of highp nodes (older Intel E5-2650v4 chips) on the legacy cluster.

## Useful OARC helper commands

| Command | Cluster | What it does |
|---|---|---|
| `h2 whoami` | Slurm | Your Slurm accounts, QOS and limits |
| `h2 validate job.sh` | Slurm | Checks a job script before you submit |
| `h2 convert-uge old.sh` | Slurm | Converts a Grid Engine script to Slurm |
| `h2 why-pending <id>` | Slurm | Why a job is still waiting |
| `h2 diagnose <id>` | Slurm | What happened to a finished job |
| `h2 modules <name>` | Slurm | Find a module and how to load it |
| `myquota` | both | Your disk usage and quotas |
| `myjobs` / `groupjobs` / `myresources` | legacy | Your jobs / group's jobs / what you can use |

## Policies worth knowing

- Login nodes are for light work only. Heavy processes there can be killed.
- No personal or sensitive data on the cluster.
- If you publish results computed on Hoffman2, OARC asks you to acknowledge the cluster (see [References](../help/references.md)).
