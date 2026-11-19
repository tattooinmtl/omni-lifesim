# omni-lifesim

A three.js garden where two fruit flies forage among flowers, each driven by the same small simulated brain. The brain is modelled on real *Drosophila* circuits, and a live viewer shows real brain-region meshes from [Virtual Fly Brain](https://www.virtualflybrain.org/) lighting up as the selected fly's neurons fire.

Open `index.html` in a browser. Everything is in that one file, including the mesh data; only three.js loads from a CDN.

## What's in the brain

A rate-neuron model, with neurons named after the real cell types:

- **Smell:** olfactory receptor neurons, left and right (Or42b for esters, a terpene receptor, Or56a for geosmin), feeding projection neurons with divisive normalization.
- **Lateral horn:** innate attraction and aversion.
- **Mushroom body:** 30 Kenyon cells with a sparse top-5 code, feeding approach and avoid output neurons (MBON+ and MBON−).
- **Dopamine:** PAM neurons (sugar reward) and PPL1 neurons (bitter taste or a threat) weaken Kenyon-cell-to-MBON synapses, so each fly learns which flowers to seek or avoid. The weights slowly drift back over time, so the flies also forget.
- **Vision:** LPLC2 looming detectors trigger a Giant Fiber escape; LC10 detects the other fly.
- **Descending neurons:** forward, turn left or right, land, feed.

Flowers: clover (ester and sugar), lily (ester, terpene and bitter), rotting fruit (ester, geosmin and bitter). Each fly card has lesion switches (Or56a knockout, block learning, silence the Giant Fiber) so you can see how the two flies diverge.

## Controls

- **Left-click a fly:** swoop a looming shadow at it.
- **Right-click a fly:** the camera follows it. **Right-click the ground** to go back to the free camera.
- Drag to orbit, scroll to zoom.

## Brain meshes

The region meshes come from the JRC2018Unisex template on Virtual Fly Brain: the whole brain, antennal lobe, lateral horn, mushroom-body calyx, peduncle and lobes, medulla, lobula, lobula plate and gnathal ganglia. They were downloaded as OBJ files and shrunk with `tools/shrink.py` (vertex-clustering decimation, 16-bit quantized, base64 inline).

To rebuild the meshes, put the `.obj` files in a folder and run `python tools/shrink.py <mesh_dir> brain-meshes.json`.

Virtual Fly Brain data is shared under CC BY 4.0. Please credit Virtual Fly Brain and the JRC2018 templates (Bogovic et al., 2020) if you reuse them.

The brain model is a toy for exploration. It borrows the names and wiring logic of real circuits but is not a faithful simulation of them.
