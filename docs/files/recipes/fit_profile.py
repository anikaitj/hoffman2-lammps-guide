#!/usr/bin/env python3
"""
fit_profile.py: read a LAMMPS 'fix ave/chunk' profile (the last time block),
fit a straight line between the swap slabs, and turn the slope into a
transport coefficient for the Muller-Plathe recipes.

    viscosity:            eta   = |flux / (d vx / dz)|
    thermal conductivity: kappa = |flux / (d T / dz)|

Usage (macOS/Linux: python3, Windows: py):
    python3 fit_profile.py vx_profile.dat --flux -0.0305
    python3 fit_profile.py temp_profile.dat --flux 0.012 --column v_temp
    python3 fit_profile.py vprofile.dat --parabola --force 0.02     # Poiseuille
    python3 fit_profile.py vprofile.dat --show          # just print the profile

Poiseuille (body force F per atom, number density rho, channel along y):
    vx(y) = c0 + c1*y + c2*y^2  with  c2 = -rho*F/(2*eta)   ->   eta = -rho*F/(2*c2)

Coordinates in the file are reduced (0-1) if the chunk used 'units reduced'
(viscosity and thermal-conductivity recipes) and are distances otherwise
(Poiseuille recipe).
Give --length (the box length along the profile) so slopes are per unit
distance. Each recipe prints the exact fit_profile.py command to run.
"""
import argparse, sys

def last_block(path):
    cols, block, rows_left = None, [], 0
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                if "Chunk" in line:
                    cols = line[1:].split()
                continue
            p = line.split()
            if not p:
                continue
            if rows_left == 0:                 # block header: Timestep Nchunks ...
                rows_left = int(p[1]); block = []
                continue
            block.append([float(x) for x in p]); rows_left -= 1
    if cols is None or not block:
        sys.exit(f"{path}: not a fix ave/chunk file")
    return cols, block

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("file")
ap.add_argument("--column", default=None, help="value column to fit (default: last column)")
ap.add_argument("--flux", type=float, help="flux printed by the LAMMPS recipe")
ap.add_argument("--length", type=float, default=1.0, help="box length along the profile (if coords are reduced)")
ap.add_argument("--show", action="store_true", help="print the profile table")
ap.add_argument("--parabola", action="store_true", help="Poiseuille mode: fit vx = c0+c1*y+c2*y^2")
ap.add_argument("--force", type=float, help="body force per atom (Poiseuille mode)")
a = ap.parse_args()

cols, rows = last_block(a.file)
ci = cols.index(a.column) if a.column else len(cols) - 1
x = [r[1] * a.length for r in rows]; y = [r[ci] for r in rows]
if a.show:
    print(f"{cols[1]:>12} {cols[ci]:>12}")
    for xi, yi in zip(x, y): print(f"{xi:12.4f} {yi:12.5f}")
def lstsq(xs, ys, deg):
    # normal equations for a polynomial fit (no numpy needed)
    n = deg + 1
    A = [[sum(x ** (i + j) for x in xs) for j in range(n)] for i in range(n)]
    b = [sum(y * x ** i for x, y in zip(xs, ys)) for i in range(n)]
    for i in range(n):                                     # Gaussian elimination
        p = max(range(i, n), key=lambda r: abs(A[r][i])); A[i], A[p] = A[p], A[i]; b[i], b[p] = b[p], b[i]
        for r in range(i + 1, n):
            f = A[r][i] / A[i][i]; b[r] -= f * b[i]
            for c in range(i, n): A[r][c] -= f * A[i][c]
    c = [0.0] * n
    for i in reversed(range(n)):
        c[i] = (b[i] - sum(A[i][k] * c[k] for k in range(i + 1, n))) / A[i][i]
    return c

if a.parabola:
    vi = cols.index(a.column or "vx"); di = cols.index("density/number") if "density/number" in cols else None
    keep = [k for k, r in enumerate(rows) if (di is None or r[di] > 0)]
    keep = keep[1:-1]                                    # drop the layers touching the walls
    xs = [x[k] for k in keep]; ys = [rows[k][vi] for k in keep]
    c0, c1, c2 = lstsq(xs, ys, 2)
    print(f"fit {len(xs)} layers: vx = {c0:.4g} + {c1:.4g}*y + {c2:.4g}*y^2")
    if a.force is not None and di is not None:
        rho = sum(rows[k][di] for k in keep) / len(keep)
        print(f"mean number density = {rho:.4g};  viscosity eta = -rho*F/(2*c2) = {-rho * a.force / (2 * c2):.4g}")
    sys.exit()

# Muller-Plathe: swap slabs at the bottom (bin 0) and middle; fit the linear
# region of the lower half, skipping two bins next to each slab.
n = len(x); lo, hi = 2, n // 2 - 2
c0, slope = lstsq(x[lo:hi], y[lo:hi], 1)
print(f"fit bins {lo}-{hi - 1} of {n}: slope d({cols[ci]})/d({cols[1]}) = {slope:.5g}")
if a.flux is not None:
    # fix viscosity and fix thermal/conductivity report the swapped amount
    # with different sign conventions; the transport coefficient is the magnitude
    print(f"coefficient = |flux / slope| = {abs(a.flux / slope):.5g}")
