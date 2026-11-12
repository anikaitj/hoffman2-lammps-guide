# Melting checks & thermo plots

## Did it melt? Use MSD

Mean squared displacement (MSD) = how far atoms have moved on average, in Å². Add it to your input (define it after `minimize`):

```
compute         msd film msd com yes
thermo_style    custom step time temp pe c_msd[4]
```

`c_msd[4]` is the total MSD. `com yes` removes drift of the whole film.

| Max MSD | Meaning |
|---|---|
| Tens of Å² | Solid; atoms only vibrate |
| ~100–340 Å² | Still solid, for a film: surface atoms hop around |
| Thousands of Å² | Liquid |

!!! warning "Don't use FCC% to decide melting"

    At high temperature, PTM labels many vibrating atoms "Other" even in a solid, so FCC% drops a lot without melting. MSD separates solid from liquid cleanly.

Other signs:

- Density (bulk NPT runs) drops noticeably on melting.
- Potential energy per atom jumps up at melting (latent heat) during a heating ramp.
- RDF first-peak height g(r) falls below ~2.7 for a liquid.
- In OVITO, a melted region turns mostly white.

## Melting depends on the potential and the geometry

- Cu_u3.eam melts at about 1300 K in our tests (real Cu: 1358 K). A "1300 K anneal" sits right at melting.
- Films melt more easily than bulk, because melting starts at the surface.
- Pressure raises the melting point, so a run under compression needs a higher temperature to melt.

Always check every run instead of assuming.

## Plotting the thermo output

[`plot_thermo.py`](../files/plot_thermo.py) reads `log.lammps`, joins the heat/hold/cool stages, writes a CSV, and plots every column against time with dashed lines at stage boundaries. It skips minimization output automatically.

On your laptop (Python 3 + matplotlib; see [Laptop setup](../getting-started/laptop-setup.md#3-python-311-or-newer)), in the folder with the downloaded `log.lammps`:

=== "macOS"

    ```bash
    source ~/md-env/bin/activate
    python3 plot_thermo.py log.lammps                          # all columns → thermo.csv, thermo.png
    python3 plot_thermo.py log.lammps --cols temp 'c_msd[4]'   # just these (quote names with [ ])
    python3 plot_thermo.py log.lammps --out T1100_s1           # T1100_s1.csv / .png
    open thermo.png
    ```

=== "Windows"

    ```powershell
    & $HOME\md-env\Scripts\Activate.ps1
    py plot_thermo.py log.lammps                               # all columns → thermo.csv, thermo.png
    py plot_thermo.py log.lammps --cols temp 'c_msd[4]'        # just these
    py plot_thermo.py log.lammps --out T1100_s1                # T1100_s1.csv / .png
    start thermo.png
    ```

=== "Linux"

    ```bash
    source ~/md-env/bin/activate
    python3 plot_thermo.py log.lammps                          # all columns → thermo.csv, thermo.png
    python3 plot_thermo.py log.lammps --cols temp 'c_msd[4]'   # just these (quote names with [ ])
    python3 plot_thermo.py log.lammps --out T1100_s1           # T1100_s1.csv / .png
    xdg-open thermo.png
    ```

Example output (from `python3 plot_thermo.py log.film1`):

```
note: skipped 1 thermo block(s) with different columns (e.g. minimization)
5 rows, columns: Step Time Temp PotEng v_pe_atom c_msd[4]
wrote film1.csv
wrote film1.png
```

### What to look at

| Column | Healthy | Warning sign |
|---|---|---|
| `Temp` | Follows the ramp/hold you set | Far from target → thermostat on wrong group, or `thermo_modify temp` missing |
| `PotEng` / `v_pe_atom` | Drifts down as grains coarsen and defects anneal | Sudden jump → melting; NaN → simulation blew up |
| `c_msd[4]` | Slow rise (solid) | Steep, steady climb into 1000s → melting |
| `Press` (bulk) | Fluctuates around target | Huge values → overlapping atoms, bad box |
| `Density` (bulk) | ~8.8–8.9 g/cm³ at 300 K for Cu | Drop during heating → melting |

## Comparing runs

=== "macOS"

    ```bash
    for d in T900 T1000 T1100 T1200; do
      python3 plot_thermo.py $d/log.lammps --cols 'c_msd[4]' --out $d
    done
    ```

=== "Windows"

    ```powershell
    foreach ($d in "T900","T1000","T1100","T1200") {
      py plot_thermo.py "$d\log.lammps" --cols 'c_msd[4]' --out $d
    }
    ```

=== "Linux"

    ```bash
    for d in T900 T1000 T1100 T1200; do
      python3 plot_thermo.py $d/log.lammps --cols 'c_msd[4]' --out $d
    done
    ```

The CSVs open in Excel, Numbers, LibreOffice or Python/pandas for overlay plots.
