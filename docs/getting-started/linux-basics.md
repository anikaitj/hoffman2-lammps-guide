# Linux basics

Hoffman2 runs Linux. You only need a small set of commands.

!!! info "Same for every laptop"

    These commands are typed on Hoffman2 after you `ssh` in, so they work identically whether your laptop is a Mac, a Windows PC or Linux. For commands on your own computer, see the [laptop cheat sheet](laptop-setup.md#command-cheat-sheet-laptop-side).

## Moving around and looking at files

```bash
pwd                     # where am I?
ls                      # what's here?
ls -lh                  # with sizes and dates
ls -lt | head           # newest first
cd folder               # go into a folder
cd ..                   # go up one level
cd ~                    # go home
cd $SCRATCH             # go to scratch
mkdir -p a/b/c          # make folders (and any missing parents)
```

## Reading files

```bash
cat file                # print whole file
less file               # scroll (q to quit, / to search)
head -20 file           # first 20 lines
tail -5 file            # last 5 lines
tail -f log.lammps      # follow a growing file (Ctrl+C to stop)
grep DONE log.lammps    # find lines containing DONE
grep -c ERROR file      # count matching lines
wc -l file              # count lines
```

## Copying, moving, deleting

```bash
cp a b                  # copy file
cp -r dirA dirB         # copy folder
mv a b                  # move / rename
rm file                 # delete: there is NO undo and NO trash
rm -r folder            # delete a folder and everything in it (careful)
```

!!! danger "`rm` is permanent"

    Scratch isn't backed up at all, and home backups don't protect against accidental deletion. Double-check the path before any `rm -r`. Never run `rm -rf *` unless you've run `pwd` first.

## Disk space

```bash
du -sh *                # size of each item here
du -sh .                # size of this folder
myquota                 # your quotas (Hoffman2 command)
```

## Making and editing files on Hoffman2

### `nano` (easiest editor)

```bash
nano in.my_run
```

Type or paste, then Ctrl+O, Enter (save), Ctrl+X (exit). Ctrl+W searches.

### Heredoc (paste one whole block)

```bash
cat > in.my_run << 'EOF'
units  metal
...rest of the file...
EOF
```

Everything between the two `EOF` lines goes into the file. Keep the quotes on `'EOF'` so `$` and `${...}` (used in LAMMPS variables) are written literally instead of being expanded by the shell.

!!! danger "Don't paste file contents straight into the terminal"

    If you paste the *contents* of a file without `nano` or `cat >`, the shell tries to run every line as a command. No file gets created, and lines like `mpirun ...` run on the login node, which you must never do. A pile of `command not found` errors means this happened.

### Or write files on your laptop

Often easier: edit in VS Code (or any editor) and upload with `scp`/`rsync` ([Moving files](../jobs/moving-files.md)). VS Code's Remote-SSH extension can also open Hoffman2 folders directly.

## Running many commands at once

```bash
for d in run_1100K run_1200K run_1300K; do
  echo "== $d"; tail -1 $d/log.lammps
done
```

`for` loops like this are how the lab checks several runs at once.

## Permissions and scripts

```bash
chmod u+x script.sh     # make a script executable
./script.sh             # run it (or: bash script.sh)
```

## Keeping things running when you disconnect

Batch jobs keep running after you log out; that's the point of the scheduler. For long *interactive* work on a login node (e.g. a big `rsync`), `tmux` keeps your session alive:

```bash
tmux new -s work        # start
# ... Ctrl+B then D to detach; log out safely ...
tmux attach -t work     # come back later
```

## Getting help on a command

```bash
man ls                  # manual page (q to quit)
ls --help
```

OARC's own guide: [Unix command line](https://www.hoffman2.idre.ucla.edu/Using-H2/Command-line/Unix-command-line.html).
