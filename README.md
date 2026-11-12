# NTRG · LAMMPS on Hoffman2

Lab guide for running LAMMPS molecular dynamics simulations on UCLA's Hoffman2 cluster: accounts, Slurm and legacy Grid Engine job scripts, building structures, OVITO orientation analysis, and the group's Cu(111) findings.

**Read the site: <https://anikaitj.github.io/hoffman2-lammps-guide/>**

The pages are Markdown files in [`docs/`](docs/) and also read fine on GitHub. Start at [`docs/index.md`](docs/index.md).

## Editing the guide

Every page is a Markdown file in `docs/`. The sidebar menu is the `nav:` section of `mkdocs.yml`. See [`docs/help/contributing.md`](docs/help/contributing.md).

Preview locally:

```bash
pip install mkdocs-material
mkdocs serve          # open http://127.0.0.1:8000
mkdocs build --strict # check for broken links before pushing
```

Push to `main` and the GitHub Action (`.github/workflows/docs.yml`) rebuilds and publishes the site.

## First-time GitHub Pages setup

1. Push this repo to GitHub.
2. Repo Settings → Pages → Source: GitHub Actions.
3. Push any commit (or run the `docs` workflow manually). The site URL appears in the Action's output.
4. Fill in `site_url` and `repo_url` in `mkdocs.yml` and the link above.

## Layout

```
├── mkdocs.yml                  # site settings + sidebar menu
├── docs/
│   ├── index.md                # home page
│   ├── getting-started/        # cluster overview, login, Linux, storage
│   ├── lammps/                 # getting LAMMPS, potentials, inputs, structures
│   ├── jobs/                   # Slurm, Grid Engine, interactive, monitoring, performance, restarts, transfers
│   ├── analysis/               # OVITO, orientation, melting & thermo
│   ├── examples/               # Cu test, film on (111) template, ReaxFF
│   ├── help/                   # troubleshooting, FAQ, glossary, references, contributing
│   └── files/                  # downloadable inputs and scripts
└── .github/workflows/docs.yml  # auto-deploy to GitHub Pages
```

Maintainer: Anikait Jain (NTRG)
