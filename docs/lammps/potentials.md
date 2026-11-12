# Potentials

The interatomic potential tells LAMMPS how atoms push and pull on each other. It decides almost everything physical: lattice constant, melting point, surface energies, stacking-fault energy. Choosing it is a scientific decision, not a formality.

The potential file must be in the run folder (or referenced by full path).

## Copper potentials the lab uses

| | Foiles `Cu_u3.eam` | Mishin `Cu_mishin1.eam.alloy` |
|---|---|---|
| Reference | Foiles, Baskes & Daw, *Phys. Rev. B* 33, 7983 (1986) | Mishin et al., *Phys. Rev. B* 63, 224106 (2001) |
| `pair_style` | `eam` | `eam/alloy` |
| `pair_coeff` | `pair_coeff * * Cu_u3.eam` | `pair_coeff * * Cu_mishin1.eam.alloy Cu` |
| Lattice constant | 3.615 Å | 3.615 Å |
| Cutoff | 4.95 Å | — |
| Melting in our tests | ≈ 1300 K (real Cu: 1358 K) | different; check before you rely on it |
| Typical use | Matching papers that cite Foiles (e.g. Shao et al.) | Melt-and-cool and other runs where stacking-fault and surface energies matter |
| Strengths | Standard LAMMPS file; what Shao et al. cite | Generally better stacking-fault and surface energies |

Whichever you use, say which file in every report.

!!! warning "Melting point depends on the potential"

    With Cu_u3.eam, 1300 K is right at melting, and thin films melt more easily than bulk, so a 1300 K anneal of a Cu_u3 film can melt it. Always check whether a run melted ([Melting & thermo](../analysis/melting-and-thermo.md)) instead of trusting the experimental melting point.

## Download (on Hoffman2, in your run folder)

```bash
# Foiles Cu_u3 (pair_style eam)
curl -sL -o Cu_u3.eam \
  https://raw.githubusercontent.com/lammps/lammps/develop/bench/Cu_u3.eam

# Mishin 2001 (pair_style eam/alloy)
curl -sL -o Cu_mishin1.eam.alloy \
  https://raw.githubusercontent.com/lammps/lammps/develop/potentials/Cu_mishin1.eam.alloy
```

Check them:

```bash
head -2 Cu_u3.eam                 # should mention Foiles ... Phys Rev B, 33, 7983 (1986)
head -3 Cu_mishin1.eam.alloy      # should mention Mishin, Phys Rev B, 63, 224106 (2001)
```

If `head` shows `<!DOCTYPE html>` or `404: Not Found`, the download failed.

!!! tip "Keep one copy"

    Put potentials in `$HOME/potentials/` and reference them by full path, or symlink them into each run folder: `ln -s ~/potentials/Cu_u3.eam .`

## `eam` vs `eam/alloy`

- `eam` (funcfl format, e.g. `Cu_u3.eam`): one element per file. `pair_coeff` takes atom type pairs (`* *` or `1 1`).
- `eam/alloy` (setfl format, e.g. `*.eam.alloy`): can hold several elements. `pair_coeff * * file El1 El2 ...` maps atom types → elements in order.

If you have two atom types that are both Cu (e.g. film = type 1, template = type 2), list Cu twice for `eam/alloy`:

```
pair_coeff * * Cu_mishin1.eam.alloy Cu Cu
```

With `eam`, `pair_coeff * * Cu_u3.eam` covers all types.

## Finding other potentials

- NIST Interatomic Potentials Repository: searchable by element, with references: <https://www.ctcms.nist.gov/potentials/>
- OpenKIM: tested potentials with property predictions: <https://openkim.org/>
- The LAMMPS `potentials/` folder on GitHub

When you pick one, look up what it predicts for the properties your question depends on (melting point, surface energy, stacking-fault energy) and compare with experiment.

## ReaxFF (reactive, C/H/O etc.)

See the [ReaxFF example](../examples/reaxff-cho.md). Different units (`real`), atom style (`charge`), a required charge-equilibration fix, and a ~0.25 fs timestep.

## Common potential mistakes

- Wrong element order in `pair_coeff` for multi-element files. It doesn't crash; it silently gives wrong physics.
- Mixing up `eam` and `eam/alloy` → `ERROR: ... Invalid ... file` or nonsense energies.
- Forgetting `mass` with `pair_style eam` when atoms come from `create_atoms` with several types: the funcfl file sets the mass, but if in doubt add `mass * 63.546`.
- Comparing runs with different potentials as if only temperature changed.
