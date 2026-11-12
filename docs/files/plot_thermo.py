#!/usr/bin/env python3
"""
plot_thermo.py: read the thermo output from a LAMMPS log file, save it as CSV,
and plot every column against time (or step).

Usage (on your laptop, after downloading log.lammps):
    python3 plot_thermo.py log.lammps
    python3 plot_thermo.py log.lammps --cols temp density      # only some columns
    python3 plot_thermo.py log.lammps --out myrun               # myrun.csv / myrun.png

Needs: Python 3 with matplotlib  (pip install matplotlib)

Handles logs with several 'run' commands (heat / hold / cool stages): every
thermo block is read and joined, and stage boundaries are drawn as dashed lines.
"""
import argparse
import csv
import sys


def read_blocks(path):
    """Return a list of (header, rows) for every thermo block in the log."""
    blocks, cur = [], None
    with open(path, errors="replace") as fh:
        for line in fh:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "Step":                       # start of a thermo block
                cur = (parts, [])
                blocks.append(cur)
                continue
            if cur is None:
                continue
            try:
                vals = [float(p) for p in parts]
            except ValueError:
                cur = None                               # "Loop time ..." etc. ends the block
                continue
            if len(vals) == len(cur[0]):
                cur[1].append(vals)
    return [b for b in blocks if b[1]]


def read_thermo(path):
    """Join the MD thermo blocks into one timeline.

    Uses the column layout of the LAST block (the production MD), so blocks with
    other columns (e.g. the default output during an earlier 'minimize') are
    skipped. If the step counter goes backwards (reset_timestep), earlier rows
    are dropped. Returns (header, rows, stage_start_indices).
    """
    blocks = read_blocks(path)
    if not blocks:
        sys.exit(f"No thermo output ('Step ...' header) found in {path}")
    header = blocks[-1][0]
    skipped = sum(1 for h, _ in blocks if h != header)
    if skipped:
        print(f"note: skipped {skipped} thermo block(s) with different columns "
              "(e.g. minimization)", file=sys.stderr)
    rows, stages = [], []
    for h, brows in blocks:
        if h != header:
            continue
        if rows and brows[0][0] < rows[-1][0]:
            print("note: timestep was reset; earlier rows dropped", file=sys.stderr)
            rows, stages = [], []
        stages.append(len(rows))
        for vals in brows:
            # consecutive runs repeat the boundary step; keep it once
            if rows and vals[0] == rows[-1][0]:
                continue
            rows.append(vals)
    return header, rows, stages[1:]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", help="LAMMPS log file, e.g. log.lammps")
    ap.add_argument("--cols", nargs="*", help="columns to plot (default: all)")
    ap.add_argument("--out", default=None, help="output name without extension")
    args = ap.parse_args()

    header, rows, stages = read_thermo(args.log)
    if args.out:
        out = args.out
    else:
        import os
        base = os.path.basename(args.log)
        if base.startswith("log."):
            base = base[4:]
        if base.endswith(".lammps"):
            base = base[:-7]
        out = base if base and base not in ("lammps", "log") else "thermo"

    with open(out + ".csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"{len(rows)} rows, columns: {' '.join(header)}")
    print(f"wrote {out}.csv")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: skipping plot (pip install matplotlib)")
        return

    xname = "Time" if "Time" in header else "Step"
    xi = header.index(xname)
    want = args.cols or [h for h in header if h not in ("Step", "Time")]
    lower = {h.lower(): h for h in header}
    cols = [lower[c.lower()] for c in want if c.lower() in lower]
    missing = [c for c in want if c.lower() not in lower]
    if missing:
        print(f"not in log, skipped: {' '.join(missing)}")
    if not cols:
        sys.exit("nothing to plot")

    x = [r[xi] for r in rows]
    fig, axes = plt.subplots(len(cols), 1, figsize=(8, 2.2 * len(cols)), sharex=True)
    if len(cols) == 1:
        axes = [axes]
    for ax, c in zip(axes, cols):
        ci = header.index(c)
        ax.plot(x, [r[ci] for r in rows], lw=1)
        ax.set_ylabel(c)
        for s in stages:
            if 0 < s < len(x):
                ax.axvline(x[s], color="grey", ls="--", lw=0.8)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("time (ps)" if xname == "Time" else "step")
    fig.tight_layout()
    fig.savefig(out + ".png", dpi=150)
    print(f"wrote {out}.png")


if __name__ == "__main__":
    main()
