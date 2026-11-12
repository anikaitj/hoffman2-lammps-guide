# Account & login

## 1. Get a Hoffman2 account

You can't do anything until your account is approved.

1. Go to sim.idre.ucla.edu → Request a cluster account. You need a UCLA Logon ID. (If you're on the Mednet network, connect to the campus VPN first.)
2. As sponsor, pick your PI (the lab's sponsor) so you land in the lab's resource group. Ask a lab member for the group's name if SIM asks.
    - If the PI isn't in the list, they must first register with SIM as a sponsor.
3. The sponsor has to log in to SIM and approve your request. Ping them so it doesn't sit.

!!! note "ColdFront"

    OARC also runs coldfront.hoffman2.oarc.ucla.edu, which handles account requests, approvals and the Slurm password. If SIM sends you there, use it.

## 2. Passwords: there are two

Since the Slurm cluster went to production, the Slurm and legacy passwords are separate:

- Legacy (`hoffman2.idre.ucla.edu`): change it in SIM.
- Slurm (`hoffman2.oarc.ucla.edu`): change it on the ColdFront password page.

If one login works and the other doesn't, this is usually why.

## 3. Log in

Open a terminal on your laptop (first time? see [Laptop setup](laptop-setup.md)):

=== "macOS"

    Terminal app:

    ```bash
    ssh <username>@hoffman2.oarc.ucla.edu     # Slurm cluster (current)
    ssh <username>@hoffman2.idre.ucla.edu     # legacy Grid Engine cluster
    ```

=== "Windows"

    PowerShell or Windows Terminal (built-in OpenSSH, OARC's recommended option):

    ```powershell
    ssh <username>@hoffman2.oarc.ucla.edu     # Slurm cluster (current)
    ssh <username>@hoffman2.idre.ucla.edu     # legacy Grid Engine cluster
    ```

    Alternatives OARC lists: MobaXterm, Git Bash, Cygwin, WSL.

=== "Linux"

    Any terminal:

    ```bash
    ssh <username>@hoffman2.oarc.ucla.edu     # Slurm cluster (current)
    ssh <username>@hoffman2.idre.ucla.edu     # legacy Grid Engine cluster
    ```

The first time, ssh asks whether to trust the host: type `yes`. Then type your password; nothing appears while you type, which is normal. You'll land on a login node with a prompt like `[<username>@login1 ~]$`.

A warning about "post-quantum key exchange" is harmless.

### Stop idle disconnects

```bash
ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=5 <username>@hoffman2.oarc.ucla.edu
```

### Shortcut: `ssh hoffman2`

Set up an SSH config file once and type `ssh hoffman2` instead of the full address. Where the file lives differs by system: see [Laptop setup → SSH shortcut](laptop-setup.md#6-shortcut-ssh-hoffman2-optional).

### Graphical programs (rarely needed)

- macOS: install XQuartz, run `defaults write org.xquartz.X11 enable_iglx -bool true`, reboot, then `ssh -Y ...` (OARC's instructions).
- Linux: `ssh -X ...`. Windows: MobaXterm handles it automatically.
- OARC also offers a DCV remote desktop on Slurm (`dcv1.hoffman2.oarc.ucla.edu`). For our work, run OVITO on your laptop instead.

## 4. Two terminals: the #1 beginner mistake

From now on there are two machines:

| Where | Prompt looks like | What you do there |
|---|---|---|
| Your laptop | `you@Laptop ~ %` | `scp`/`rsync` files, open OVITO, plot |
| Hoffman2 | `[<username>@login1 ~]$` | make files, submit jobs, check logs |

Every command in this guide says which one to use. Running a command on the wrong one is the most common mistake (for example, running `scp` inside the Hoffman2 session).

## 5. Find your folders

```bash
echo $HOME       # /u/home/<l>/<username>
echo $SCRATCH    # /u/scratch/<l>/<username>   ← run simulations here
myquota          # how much space you're using
```

`<l>` is the first letter of your username (e.g. `/u/scratch/j/joebruin`). Details on [Storage](storage.md).
