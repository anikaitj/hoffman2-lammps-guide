# Glossary

| Term | Meaning |
|---|---|
| AGG | Abnormal grain growth: one grain grows much faster than the rest and consumes them |
| Atom type | Integer label in LAMMPS (1, 2, ...). Several types can be the same element (e.g. film vs template) |
| Barostat | Algorithm that controls pressure (in `fix npt`) |
| Bulk | Fully periodic box: no surfaces |
| CNA | Common Neighbor Analysis. Structure classifier; mislabels FCC Cu as HCP. Don't use |
| Compute | LAMMPS command that calculates a quantity (temperature, MSD, RDF...) |
| Data file | Text snapshot of atoms (`write_data` / `read_data`) |
| DTN | Data transfer node, `dtn.hoffman2.idre.ucla.edu`, for moving big files |
| Dump | Trajectory output (`traj.lammpstrj`) for OVITO |
| EAM | Embedded-atom method: standard interatomic potential type for metals |
| Ensemble | What's held constant: NVE (energy), NVT (temperature), NPT (temperature + pressure) |
| FENE | Finitely extensible nonlinear elastic spring: the bond in bead-spring polymer models |
| FCC | Face-centred cubic: copper's crystal structure. ABCABC stacking of (111) layers |
| Film | Box periodic in x/y with vacuum above and below in z: free surfaces |
| Fix | LAMMPS command that does something every step (integrate, thermostat, freeze atoms) |
| GPU / KOKKOS packages | LAMMPS add-ons that run (parts of) a simulation on graphics cards |
| Grain | A region of crystal with one orientation |
| Grain boundary (GB) | Where two differently oriented grains meet |
| Grid Engine / SGE / UGE | The legacy Hoffman2 scheduler (`qsub`, `qstat`) |
| HCP | Hexagonal close-packed. In FCC Cu, HCP-labelled atoms mark stacking faults and twin boundaries |
| highp | Running on the group's own nodes: longer time limits (14 days) |
| Job array | One submission that runs many similar jobs (e.g. a temperature sweep) |
| Login node | Where you land after `ssh`. Light work only |
| Miller indices (hkl) | Name a crystal plane; [hkl] names a direction |
| Minimization | Moving atoms to the nearest energy minimum (`minimize`) before dynamics |
| Module | Software package you load on the cluster (`module load ...`) |
| Müller-Plathe method | Measuring viscosity or thermal conductivity by swapping momentum or energy between slabs and reading off the steady gradient |
| MPI | How LAMMPS runs on many cores at once (`mpirun -n 8 ...`) |
| MSD | Mean squared displacement (Å²). Thousands = melted |
| OARC / IDRE | UCLA Office of Advanced Research Computing (formerly IDRE), runs Hoffman2 |
| OVITO | Visualization and analysis program for atomistic data |
| Poiseuille flow | Pressure-driven flow between two walls; the velocity profile is a parabola |
| PPPM | Particle-particle particle-mesh: fast long-range electrostatics (`kspace_style pppm`) |
| Periodic boundary | Atoms leaving one side re-enter the other; no surfaces in that direction |
| Potential | File + model describing how atoms interact |
| PTM | Polyhedral template matching. Per-atom structure + orientation in OVITO. The lab's standard |
| QOS | Slurm "quality of service": e.g. `highp` |
| Quaternion | Four numbers describing a 3D rotation; PTM's per-atom orientation |
| RDF | Radial distribution function. Shows structure (FCC), not orientation |
| ReaxFF | Reactive force field: bonds break and form, charges change |
| Restart file | Binary exact snapshot to continue a run (`write_restart` / `read_restart`) |
| Scratch | Big, temporary storage (`$SCRATCH`); purged after 14 days |
| SHAKE | Constraint algorithm keeping bonds/angles rigid (e.g. water), allowing a 2 fs timestep |
| Seed (random) | Number setting initial velocities; change it for independent repeats |
| Seed / template (structural) | Layers of (111) crystal placed to guide the film's orientation |
| Slurm | The new Hoffman2 scheduler (`sbatch`, `squeue`) |
| Stacking fault | One (111) layer in the wrong position (ABCAB\|ABC) |
| Texture | Most grains share one orientation (e.g. (111) texture), but it's not one single crystal |
| Thermo | The table LAMMPS prints to `log.lammps` |
| Thermostat | Algorithm controlling temperature (Nosé–Hoover in `fix nvt`) |
| Timestep | Time per MD step: 1 fs for Cu |
| Twin | Mirror-related (111) domains, rotated 60° about [111]; stacking reverses ABC\|CBA |
| WCA | Purely repulsive LJ potential (cut at its minimum, 2^(1/6)σ), used for polymer beads |
| Walltime | Real-world time limit for a job |
