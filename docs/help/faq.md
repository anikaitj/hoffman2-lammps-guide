# FAQ

**Does Hoffman2 cost anything?**
No. IDRE confirmed in Oct 2026 that the group's use is free in both shared and highp modes, with no need to limit submissions.

**Slurm or Grid Engine?**
Slurm (`hoffman2.oarc.ucla.edu`) is where OARC wants new jobs. LAMMPS isn't installed there yet, so see [Getting LAMMPS](../lammps/getting-lammps.md) for the options.

**Can I run other kinds of simulation (liquids, water, polymers, mechanics) on Hoffman2?**
Yes. Anything LAMMPS can do runs on Hoffman2, as long as your LAMMPS build has the package it needs. Start from a tested [recipe](../recipes/index.md) or an official example ([More simulation types](../recipes/more-types.md)).

**Should I use a GPU?**
For the lab's usual 10k–50k-atom runs, CPU cores are usually enough. For hundreds of thousands of atoms and up, try a GPU and compare speeds: see [GPU & multithreaded runs](../jobs/gpu.md).

**Can I run LAMMPS on my laptop?**
For small tests, yes: `pip install lammps` or the LAMMPS binary installers. Production runs belong on Hoffman2.

**How big should my system be?**
Big enough that grains aren't tiny compared with the effect you're studying, small enough to run in a day. The lab's films were 10k–30k atoms; grains of 25–35 Å are far smaller than real ones (~40 nm), which is a known limitation.

**How long should I simulate?**
Until the quantity you care about stops changing: e.g. (111) fraction flat for the last few hundred ps. Template conversion took ~200–1,000 ps; twin removal may need 10+ ns.

**What timestep?**
1 fs (`timestep 0.001` in `metal` units) for Cu. 0.25 fs for ReaxFF (`timestep 0.25` in `real` units).

**Why NVT for films and NPT for bulk?**
A film has vacuum along z, so "pressure" along z is meaningless and a barostat would squash or stretch the box. Bulk boxes should be at zero pressure, so NPT.

**What's a random seed and why change it?**
The number in `velocity ... create 300 <seed>`. Different seeds give statistically independent runs of the same setup. Grain growth is random; one run isn't a result. Do 3+.

**Is (111) in OVITO the same as FCC?**
No. FCC (green in PTM) is the crystal structure; (111) is which way the crystal faces. See [Measuring orientation](../analysis/orientation.md).

**Why are there 2 grains if everything is (111)?**
Usually twins: both (111) up, rotated 60° about [111]. Grain segmentation counts them separately.

**Why is the top and bottom of my film white in OVITO?**
Surface atoms are missing neighbours, so PTM can't classify them. Normal.

**Can I use CNA instead of PTM?**
Don't: CNA mislabels FCC Cu as HCP and doesn't give orientation.

**Which potential should I use?**
Foiles `Cu_u3.eam` is the file Shao et al. cite and the one most of this guide uses; Mishin `Cu_mishin1.eam.alloy` is a common alternative. State which one in every report. See [Potentials](../lammps/potentials.md).

**Can I apply heat to only one side of the film?**
Yes, in principle: thermostat only a region (e.g. `group hot region top` and apply `fix nvt` or `fix langevin` to that group), and let heat flow through the rest. The lab hasn't run this yet.

**Where do I keep my results long-term?**
Not scratch (14-day purge). Download to your laptop or put them in project space; keep inputs in git.

**How do I cite Hoffman2 / LAMMPS?**
See [References](references.md).
