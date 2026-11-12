# Set up your laptop

Simulations run on Hoffman2, which is Linux, so everything you type on Hoffman2 is the same whatever laptop you have. Your laptop only needs to:

1. connect to Hoffman2 (SSH),
2. move files back and forth,
3. analyse and look at results (Python, OVITO).

Pick your system in the tabs below. Choosing a tab on one block switches every block on the site to it.

## What you'll install

| Tool | What for | Required? |
|---|---|---|
| Terminal + SSH | Log in to Hoffman2 | |
| `scp` (and `rsync` where available) | Upload / download files | |
| Git | Get this guide's files; keep inputs in version control | Recommended |
| Python 3.11+ | `plot_thermo.py`, `analyze_orientation.py` | for analysis |
| OVITO (desktop app) | Look at structures | |
| VS Code | Edit input files; open Hoffman2 folders directly | Recommended |

## 1. Terminal and SSH

=== "macOS"

    Open Terminal (⌘+Space → type "Terminal"). SSH, `scp` and `rsync` are built in. Check:

    ```bash
    ssh -V
    ```

=== "Windows"

    Open Windows Terminal or PowerShell (Start → type "PowerShell"). Windows 10 and 11 include OpenSSH, which OARC recommends as the first choice. Check:

    ```powershell
    ssh -V
    ```

    If it says `ssh` isn't recognized: Settings → System → Optional features → Add a feature → OpenSSH Client.

    `scp` is included. `rsync` is not. Use `scp -r` for folders, or install WSL (below) to get `rsync` and a full Linux shell.

=== "Linux"

    Open your terminal. Install SSH and rsync if missing:

    ```bash
    sudo apt install openssh-client rsync        # Ubuntu / Debian
    sudo dnf install openssh-clients rsync       # Fedora
    ssh -V
    ```

Then log in to test (details on [Account & login](account-and-login.md)):

```bash
ssh <username>@hoffman2.oarc.ucla.edu
```

Type `exit` to come back to your laptop.

### Optional on Windows: WSL (a Linux shell inside Windows)

If you'd rather type exactly the same commands as Mac/Linux users:

```powershell
wsl --install
```

Restart, open Ubuntu from the Start menu, then follow the Linux tabs on this site. Your Windows files are under `/mnt/c/Users/<you>/` inside WSL.

## 2. Git

=== "macOS"

    ```bash
    xcode-select --install       # installs git and other developer tools
    git --version
    ```

=== "Windows"

    ```powershell
    winget install --id Git.Git -e
    ```

    Close and reopen PowerShell, then `git --version`. (Or download from <https://git-scm.com/download/win>.)

=== "Linux"

    ```bash
    sudo apt install git         # or: sudo dnf install git
    git --version
    ```

Get this guide's files onto your laptop:

```bash
git clone https://github.com/anikaitj/hoffman2-lammps-guide.git
```

The scripts and inputs are in `hoffman2-lammps-guide/docs/files/`.

## 3. Python 3.11 or newer

OVITO's Python module needs 3.11+.

=== "macOS"

    Download the installer from <https://www.python.org/downloads/macos/>, or with Homebrew: `brew install python`. Check:

    ```bash
    python3 --version
    ```

=== "Windows"

    ```powershell
    winget install --id Python.Python.3.13 -e
    ```

    Or use the installer from <https://www.python.org/downloads/windows/> and tick "Add python.exe to PATH". Close and reopen PowerShell, then:

    ```powershell
    py --version
    ```

    On Windows the command is `py` (or `python`), **not** `python3`.

=== "Linux"

    ```bash
    sudo apt install python3 python3-pip python3-venv
    python3 --version
    ```

    If your distro's Python is older than 3.11, install a newer one (e.g. `sudo apt install python3.12 python3.12-venv`) and use `python3.12` below.

### Create a Python environment for the lab tools

A virtual environment keeps these packages separate from the rest of your system. Do this once:

=== "macOS"

    ```bash
    python3 -m venv ~/md-env
    source ~/md-env/bin/activate
    pip install --upgrade pip
    pip install numpy matplotlib ovito
    ```

=== "Windows"

    ```powershell
    py -m venv $HOME\md-env
    & $HOME\md-env\Scripts\Activate.ps1
    pip install --upgrade pip
    pip install numpy matplotlib ovito
    ```

    If activation fails with "running scripts is disabled", run this once, then try again:

    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
    ```

=== "Linux"

    ```bash
    python3 -m venv ~/md-env
    source ~/md-env/bin/activate
    pip install --upgrade pip
    pip install numpy matplotlib ovito
    ```

Each new terminal: activate again (the `source` / `Activate.ps1` line). Your prompt shows `(md-env)` when it's active.

!!! warning "Intel Macs and the `ovito` Python module"

    OVITO's pip package (3.17.2, Nov 2026) has wheels for Apple-silicon Macs (macOS 14.4+), Windows and Linux, but **not Intel Macs**. On an Intel Mac, skip `ovito` in the pip line: `plot_thermo.py` still works, and you can do the orientation analysis in the OVITO desktop app ([Measuring orientation](../analysis/orientation.md)) or run `analyze_orientation.py` on Hoffman2.

### Optional: LAMMPS on your laptop, for small tests

`pip install lammps` has wheels for macOS (Intel and Apple silicon), Windows and Linux, with most packages, including MANYBODY and REAXFF. Good for checking an input runs before using cluster time. Not for production runs.

```bash
pip install lammps
```

Run a test input (from the folder with the input and potential):

=== "macOS"

    ```bash
    python3 -c "from lammps import lammps; L=lammps(); L.file('in.cu_test')"
    ```

=== "Windows"

    ```powershell
    py -c "from lammps import lammps; L=lammps(); L.file('in.cu_test')"
    ```

=== "Linux"

    ```bash
    python3 -c "from lammps import lammps; L=lammps(); L.file('in.cu_test')"
    ```

If it complains about MPI, use `pip install "lammps[mpi]"`. Windows wheels use Microsoft MPI; Mac/Linux use MPICH.

## 4. OVITO (desktop app)

Download OVITO Basic (free) from the download section of <https://www.ovito.org/> for your system (macOS, Windows or Linux) and install it normally. Everything in this guide works with OVITO Basic.

## 5. VS Code (recommended editor)

Download from <https://code.visualstudio.com/>. Then install the Remote - SSH extension: you can open folders on Hoffman2 and edit files there as if they were local.

1. Install the extension (Extensions panel → search "Remote - SSH").
2. ⇧⌘P / Ctrl+Shift+P → Remote-SSH: Connect to Host → `<username>@hoffman2.oarc.ucla.edu`.
3. File → Open Folder → `/u/scratch/<l>/<username>/`.

!!! danger "Windows line endings break Hoffman2 scripts"

    Windows editors may save files with CRLF line endings. On Hoffman2 (Linux), a script with CRLF fails with errors like `/bin/bash^M: bad interpreter` or `$'\r': command not found`, and LAMMPS may misread commands.

    - In VS Code: bottom-right status bar → click CRLF → choose LF before saving.
    - Git: this repo's `.gitattributes` forces LF for files you clone.
    - Already uploaded a CRLF file? Fix it on Hoffman2: `sed -i 's/\r$//' run_lammps.slurm`

## 6. Shortcut: `ssh hoffman2` (optional)

Save typing with an SSH config file. Create or edit it at:

=== "macOS"

    `~/.ssh/config`:

    ```bash
    mkdir -p ~/.ssh && nano ~/.ssh/config
    ```

=== "Windows"

    `C:\Users\<you>\.ssh\config` (no file extension):

    ```powershell
    mkdir $HOME\.ssh -Force; notepad $HOME\.ssh\config
    ```

    When saving in Notepad, choose Save as type: All files so it doesn't add `.txt`.

=== "Linux"

    `~/.ssh/config`:

    ```bash
    mkdir -p ~/.ssh && nano ~/.ssh/config
    ```

Contents (same on all systems):

```
Host hoffman2
  HostName hoffman2.oarc.ucla.edu
  User <username>
  ServerAliveInterval 30
  ServerAliveCountMax 5

Host hoffman2-legacy
  HostName hoffman2.idre.ucla.edu
  User <username>
  ServerAliveInterval 30

Host h2dtn
  HostName dtn.hoffman2.idre.ucla.edu
  User <username>
```

Now `ssh hoffman2`, `ssh hoffman2-legacy` and `scp file h2dtn:/u/scratch/<l>/<username>/` work.

## Command cheat sheet: laptop side

The same job on each system. Hoffman2 commands never change.

| Task | macOS / Linux | Windows PowerShell |
|---|---|---|
| Python | `python3 script.py` | `py script.py` |
| Activate env | `source ~/md-env/bin/activate` | `& $HOME\md-env\Scripts\Activate.ps1` |
| Download a file from the web | `curl -L -o file URL` | `curl.exe -L -o file URL` (use `curl.exe`: plain `curl` may be an alias for `Invoke-WebRequest`) |
| First lines of a file | `head -5 file` | `Get-Content file -TotalCount 5` |
| Last lines of a file | `tail -5 file` | `Get-Content file -Tail 5` |
| Search in a file | `grep DONE log.lammps` | `Select-String DONE log.lammps` |
| List files | `ls -lh` | `ls` (or `dir`) |
| Make folder | `mkdir -p a/b` | `mkdir a\b -Force` |
| Copy folder from Hoffman2 | `rsync -av h2dtn:/path/ ./dir/` | `scp -r h2dtn:/path ./` |
| Home folder | `~` | `$HOME` (= `C:\Users\<you>`) |
| Path separator | `/` | `\` (PowerShell also accepts `/`) |
| Brackets in arguments | quote them: `'c_msd[4]'` (zsh needs this) | quote them: `'c_msd[4]'` |
