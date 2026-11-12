# Contributing

This guide only stays useful if people update it. Especially wanted:

- The first working LAMMPS job on Slurm: commit the job script to `docs/files/` and update [Getting LAMMPS](../lammps/getting-lammps.md) and [Slurm](../jobs/slurm.md).
- Whether `lammps/29Sep2021_MB` has REAXFF, and whether it runs on the group's highp nodes.
- New errors and fixes for [Troubleshooting](troubleshooting.md).
- Timing numbers for [Performance](../jobs/performance.md).
- New simulation recipes, with the result you got from a test run.

## How the site works

- Every page is a Markdown file in `docs/`.
- The sidebar menu is the `nav:` list in `mkdocs.yml`. A new page must be added there to appear in the menu.
- Downloadable files live in `docs/files/`.
- Pushing to `main` rebuilds and publishes the site automatically (GitHub Actions).

## Edit on GitHub (easiest)

Open the file on GitHub → pencil icon → edit → Commit changes (or "Propose changes" to open a pull request for review).

## Edit locally with a preview

=== "macOS"

    ```bash
    git clone https://github.com/anikaitj/hoffman2-lammps-guide.git
    cd hoffman2-lammps-guide
    python3 -m venv .venv && source .venv/bin/activate
    pip install mkdocs-material
    mkdocs serve                 # open http://127.0.0.1:8000; updates as you save
    ```

=== "Windows"

    ```powershell
    git clone https://github.com/anikaitj/hoffman2-lammps-guide.git
    cd hoffman2-lammps-guide
    py -m venv .venv; & .venv\Scripts\Activate.ps1
    pip install mkdocs-material
    mkdocs serve                 # open http://127.0.0.1:8000; updates as you save
    ```

=== "Linux"

    ```bash
    git clone https://github.com/anikaitj/hoffman2-lammps-guide.git
    cd hoffman2-lammps-guide
    python3 -m venv .venv && source .venv/bin/activate
    pip install mkdocs-material
    mkdocs serve                 # open http://127.0.0.1:8000; updates as you save
    ```

Before pushing, check for broken links:

```bash
mkdocs build --strict
```

## OS tabs

Laptop-side commands use tabs so each reader sees their system:

~~~~markdown
=== "macOS"

    ```bash
    python3 script.py
    ```

=== "Windows"

    ```powershell
    py script.py
    ```

=== "Linux"

    ```bash
    python3 script.py
    ```
~~~~

Commands typed on Hoffman2 don't need tabs: they're the same for everyone.

## Writing style

- Commands people can copy, in code blocks, saying where to run them (laptop or Hoffman2).
- Only what's been checked. If something is unconfirmed, mark it ⚠️ and say what would confirm it.
- Say which cluster (Slurm or legacy) something applies to.

## Callout boxes

```markdown
!!! warning "Title"

    Indented text inside the box.
```

Types: `note`, `tip`, `info`, `warning`, `danger`, `success`.
