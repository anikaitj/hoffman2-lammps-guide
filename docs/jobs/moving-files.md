# Moving files

Run these on your laptop, not inside an SSH session. OARC recommends starting transfers from your own computer, because laptops are usually behind firewalls that block connections coming in.

For anything big, use the data transfer node `dtn.hoffman2.idre.ucla.edu` instead of the login node. It's load-balanced across `dtn1` and `dtn2`, and sees the same files as the login nodes (both clusters).

In the commands below, replace `<user>` with your Hoffman2 username and `<l>` with its first letter.

## Upload: laptop → Hoffman2

=== "macOS"

    ```bash
    cd ~/md-inputs                     # folder with your files
    scp in.film_template Cu_u3.eam <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/
    scp -r my_inputs <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/
    ```

=== "Windows"

    ```powershell
    cd $HOME\md-inputs                 # folder with your files
    scp in.film_template Cu_u3.eam <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/
    scp -r my_inputs <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/
    ```

    Hoffman2 paths always use `/`, even from Windows.

=== "Linux"

    ```bash
    cd ~/md-inputs                     # folder with your files
    scp in.film_template Cu_u3.eam <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/
    scp -r my_inputs <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/
    ```

The destination folder must already exist on Hoffman2 (`mkdir -p $SCRATCH/run1` there first).

!!! warning "Edited on Windows? Check line endings"

    Files saved with Windows (CRLF) line endings can break scripts on Hoffman2. Save as LF in your editor, or fix after uploading: `sed -i 's/\r$//' <file>` on Hoffman2. See [Laptop setup](../getting-started/laptop-setup.md#5-vs-code-recommended-editor).

## Download: Hoffman2 → laptop

### One or a few files

=== "macOS"

    ```bash
    mkdir -p ~/md-runs/run1 && cd ~/md-runs/run1
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/log.lammps .
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/traj.lammpstrj .
    ```

=== "Windows"

    ```powershell
    mkdir $HOME\md-runs\run1 -Force; cd $HOME\md-runs\run1
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/log.lammps .
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/traj.lammpstrj .
    ```

=== "Linux"

    ```bash
    mkdir -p ~/md-runs/run1 && cd ~/md-runs/run1
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/log.lammps .
    scp <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/traj.lammpstrj .
    ```

The `.` at the end means "into the current folder".

### A whole run folder

=== "macOS"

    `rsync` copies only what's new or changed, so you can re-run it:

    ```bash
    rsync -av <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/ ~/md-runs/run1/
    ```

=== "Windows"

    PowerShell has no `rsync`; use `scp -r` (copies everything every time):

    ```powershell
    scp -r <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1 $HOME\md-runs\
    ```

    In WSL (Ubuntu), the macOS/Linux `rsync` command works, e.g. into `/mnt/c/Users/<you>/md-runs/`.

=== "Linux"

    `rsync` copies only what's new or changed, so you can re-run it:

    ```bash
    rsync -av <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/run1/ ~/md-runs/run1/
    ```

!!! tip "Trailing slashes in rsync"

    `run1/` (with slash) copies the *contents* of run1. `rsync -av .../run1/ ./run1/` is the safe pattern. Add `-n` for a dry run that shows what would be copied.

### Only the small files from every run (logs, final structures)

Pull every run's `log.lammps` and `data.final` without the big trajectories:

=== "macOS"

    ```bash
    rsync -av --include='*/' --include='log.lammps' --include='data.final' --exclude='*' \
      <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/ ~/md-runs/h2_logs/
    ```

=== "Windows"

    No `rsync` in PowerShell. Bundle the files on Hoffman2 first, then download one archive:

    ```bash
    # on Hoffman2:
    cd $SCRATCH
    find . -maxdepth 2 \( -name log.lammps -o -name data.final \) | tar czf ~/logs.tgz -T -
    ```

    ```powershell
    # on Windows:
    scp <user>@dtn.hoffman2.idre.ucla.edu:logs.tgz $HOME\md-runs\
    cd $HOME\md-runs; tar xzf logs.tgz
    ```

    (`tar` is built into Windows 10/11.)

=== "Linux"

    ```bash
    rsync -av --include='*/' --include='log.lammps' --include='data.final' --exclude='*' \
      <user>@dtn.hoffman2.idre.ucla.edu:/u/scratch/<l>/<user>/ ~/md-runs/h2_logs/
    ```

## Drag-and-drop apps

| | macOS | Windows | Linux |
|---|---|---|---|
| App | Cyberduck, FileZilla | WinSCP, FileZilla, MobaXterm | FileZilla, or the file manager's "Connect to Server" (`sftp://`) |
| Protocol | SFTP | SFTP | SFTP |
| Host | `dtn.hoffman2.idre.ucla.edu` | same | same |
| Port | 22 | 22 | 22 |

VS Code with Remote - SSH also lets you drag files in and out of a Hoffman2 folder.

Globus for very large data: collection "Official UCLA Hoffman2 Cluster", with Globus Connect Personal on your laptop (all three systems).

## With the SSH config shortcut

If you set up the config file ([Laptop setup](../getting-started/laptop-setup.md#6-shortcut-ssh-hoffman2-optional)), `h2dtn` replaces `<user>@dtn.hoffman2.idre.ucla.edu` on every system:

```bash
scp h2dtn:/u/scratch/<l>/<user>/run1/log.lammps .
```

## Getting this repo onto Hoffman2

```bash
# on Hoffman2
cd ~ && git clone https://github.com/anikaitj/hoffman2-lammps-guide.git
cd ~/hoffman2-lammps-guide && git pull       # later, to update
```

## Before downloading

- Make sure the run finished: `grep DONE log.lammps` on Hoffman2. Otherwise you get `No such file or directory` or a half-written file.
- Check sizes: `ls -lh` or `du -sh *` on Hoffman2. Trajectories can be GBs.
- Scratch is purged after 14 days: download what you need soon after a run.

## Rules

- No personal or sensitive data on the cluster (OARC policy).
- Big transfers through the DTN, not the login nodes.
