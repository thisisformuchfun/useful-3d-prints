# Waterpik-style two-tip holder

A one-piece, adhesive-mounted rack for two oral-irrigator jet tips. Each stem slides in from the front, while its wider collar rests on the shelf. Open slots allow drainage.

## Files

- `Waterpik_dual_holder.stl`: printable holder mesh.
- `Waterpik_dual_holder.3mf`: the same geometry in millimetres, not a pre-sliced printer/profile project.
- `Waterpik_dual_holder.step`: editable CAD solid.
- `build_holder.py`: parametric CadQuery source.
- `Optional_fit_gauge.stl`: a small sample of one matching slot to check fit before printing the holder.

## Size and fit

The mounted holder is 44 mm wide, 24 mm high, and projects 23 mm from the tile. Tip centres are 20 mm apart. The shelf is 3 mm thick. Slots taper from a rounded 5 mm inner seat to a 9.5 mm opening. These are slot dimensions, not a guaranteed compatibility range.

Each stem must slide freely into a slot, with its collar securely supported on both edges. Do not force a stem into the taper or depend on a snap fit. Check that tips stand securely and lift out easily. The optional gauge measures 16 × 21 × 3 mm and is a fit-test piece, not an assembly part.

## Printing

The large flat tape face is already on the build plate. Keep units in millimetres; do not scale the whole model to change slot fit.

Suggested starting settings: PETG, 0.20 mm layers, 3 walls, 15% infill, 4 top/bottom layers, and supports off. Use a suitable filament profile. A smooth build surface can improve tape contact. These are starting suggestions, not physically validated print settings. No printer-specific G-code is included.

## Mounting

A roughly 38 × 18 mm patch of double-sided mounting tape fits inside the rounded backplate. Select tape suitable for your tile, plastic, and damp-room conditions. Clean and dry both surfaces and follow the tape manufacturer's pressure, temperature, and dwell-time instructions. Keep tape away from the drain slots.

This is a lightweight tip rack, not a hook for an irrigator or hose. Adhesive strength and wet-service life have not been verified.

## Editing

The source requires CadQuery 2.7 and NumPy. Edit `PARAMETERS` in `build_holder.py`, then run `python build_holder.py` in an environment with those dependencies. It writes STL, STEP, and 3MF outputs and a geometry-check report beside the script, replacing matching output files. Preserve a copy of original files before regenerating.

## Limitations

This is a prototype, not a claim of universal Waterpik compatibility. It has not been physically printed, fit-tested, load-tested, or adhesion-tested. No CAD regeneration or hardware testing was performed for this publication. The original geometry is preserved; creation timestamps were removed from STEP and 3MF metadata for public distribution.

No license is granted by inclusion here. Contact the repository owner about reuse permissions.
