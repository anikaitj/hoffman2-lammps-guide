# Example: polycrystalline film on a (111) template

A polycrystalline film on a (111) template. Four differently oriented grains sit on three layers of Cu(111) and are annealed below the melting point.

Input: [`in.film_template`](../files/in.film_template) · Potential: `Cu_u3.eam` · Size: 9,734 atoms after overlap removal

!!! success "Tested"

    Runs to `=== DONE ===` with both a frozen and a mobile template (short schedule, LAMMPS 22 Jul 2025, workstation). A full-length run on Hoffman2 hasn't been done with this exact file yet.

## Layout

```
 z ▲
   │   vacuum (25+ Å)
31 ┤ ┌──────────┬──────────┐
   │ │  (122)   │  (569)   │   4 columnar grains, 25 Å thick
   │ ├──────────┼──────────┤   (2×2 in x-y; each ~31 × 31 Å)
   │ │  (100)   │  (110)   │
 6 ┤ ├──────────┴──────────┤
   │ │ Cu(111) template, 3 │   type 2 (frozen or mobile)
 0 ┤ └─────────────────────┘
   │   vacuum
```

Box: 61.35 × 61.98 Å in x-y (12 × 7 whole (111) repeats), periodic in x and y, free surfaces in z.

## Settings you can change from the command line

| Variable | Default | Meaning |
|---|---|---|
| `T_hold` | 1100 | Anneal temperature (K). Stay below ~1300 K for Cu_u3 to avoid melting |
| `heat_ps` | 100 | Ramp 300 K → T_hold |
| `hold_ps` | 400 | Hold at T_hold |
| `cool_ps` | 100 | Ramp back to 300 K |
| `frozen` | 1 | 1 = template frozen, 0 = template moves |
| `vseed` | 482917 | Velocity random seed (change for repeats) |
| `dump_ps` | 20 | Time between trajectory frames |

```bash
mpirun -n 8 $LMP -in in.film_template -var T_hold 1000 -var frozen 0 -var vseed 111234 -log log.lammps
```

## Running it

On Hoffman2 (Slurm), in a fresh folder:

```bash
mkdir -p $SCRATCH/film_T1100 && cd $SCRATCH/film_T1100
cp ~/hoffman2-lammps-guide/docs/files/in.film_template .
cp ~/hoffman2-lammps-guide/docs/files/run_lammps.slurm .
curl -sL -o Cu_u3.eam https://raw.githubusercontent.com/lammps/lammps/develop/bench/Cu_u3.eam
nano run_lammps.slurm      # set account, job name, and change the input to in.film_template
h2 validate run_lammps.slurm
sbatch run_lammps.slurm
```

How long: on one workstation core it ran at 2.09 hours/ns, so the default 0.6 ns schedule is ~1.3 h on 1 core and much less on 8. Read the `Performance:` line of your own run.

## What the input does, step by step

1. Builds the box, then the (111) template (type 2) and four grains (type 1) with rotated lattices.
2. `delete_atoms overlap 2.0 film all`: removes 687 atoms that landed too close at grain boundaries.
3. Freezes the template (`setforce 0`) if `frozen = 1`.
4. Minimizes, then resets the step counter and writes `data.initial`.
5. Defines MSD after minimization so it starts at zero.
6. NVT: heat → hold → cool, writing `data.after_heat`, `data.after_hold`, `data.final`.
7. Prints `=== DONE ===`.

## Checking the result

Download `log.lammps` and `traj.lammpstrj` to your laptop ([Moving files](../jobs/moving-files.md)), then:

=== "macOS"

    ```bash
    source ~/md-env/bin/activate
    python3 plot_thermo.py log.lammps --cols temp 'c_msd[4]'
    python3 analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

=== "Windows"

    ```powershell
    & $HOME\md-env\Scripts\Activate.ps1
    py plot_thermo.py log.lammps --cols temp 'c_msd[4]'
    py analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

=== "Linux"

    ```bash
    source ~/md-env/bin/activate
    python3 plot_thermo.py log.lammps --cols temp 'c_msd[4]'
    python3 analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

1. Melted? MSD (`c_msd[4]`) should stay in the tens to low hundreds of Å². Thousands = melted.
2. (111) fraction of the film over time: `111_of_FCC_%` column. Frame 0 should be low (none of the four grains is (111)): in our test, 3.5%.
3. Template check: `--type 2` gives the template alone. In our test, 100% of its FCC-classified atoms were (111). Only ~37% of template atoms count as FCC, because a 3-layer slab is mostly surface and interface.
4. In OVITO: PTM (orientations on) → Grain segmentation (min 50) → Expression selection with [`select_111_atoms.txt`](../files/select_111_atoms.txt). Compare frame 0 with the last frame.
5. Faults: HCP % on the last (cooled) frame, with the default RMSD cutoff 0.1.

## Things to try

- `frozen 0` vs `frozen 1` (the lab found mobile templates gave fewer faults).
- A temperature sweep 700–1200 K with a [job array](../jobs/slurm.md#temperature-sweeps-and-repeats-with-job-arrays).
- 3 seeds per condition.
- Thicker film: raise `zf` (and the box top) for a 50 or 100 Å film.
- Remove the template (delete the template lines) as a control.
