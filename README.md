# omni-lifesim

A three.js garden where two fruit flies forage among flowers, each driven by the same small simulated brain. The brain is modelled on real *Drosophila* circuits, and a live viewer shows real brain-region meshes from [Virtual Fly Brain](https://www.virtualflybrain.org/) lighting up as the selected fly's neurons fire.

**Play it:** https://tattooinmtl.github.io/omni-lifesim/

Or open `index.html` in a browser. Everything is in that one file, including the mesh data; only three.js loads from a CDN.

## What's in the brain

A rate-neuron model, with neurons named after the real cell types:

- **Smell:** olfactory receptor neurons, left and right (Or42b for esters, a terpene receptor, Or56a for geosmin), feeding projection neurons with divisive normalization.
- **Lateral horn:** innate attraction and aversion.
- **Mushroom body:** 30 Kenyon cells with a sparse top-5 code, feeding approach and avoid output neurons (MBON+ and MBON−).
- **Dopamine:** PAM neurons (sugar reward) and PPL1 neurons (bitter taste or a threat) weaken Kenyon-cell-to-MBON synapses, so each fly learns which flowers to seek or avoid. The weights slowly drift back over time, so the flies also forget.
- **Vision:** LPLC2 looming detectors trigger a Giant Fiber escape; LC10 detects the other fly.
- **Descending neurons:** forward, turn left or right, land, feed.

Flowers: clover (ester and sugar), lily (ester, terpene and bitter), rotting fruit (ester, geosmin and bitter). Each fly card has lesion switches (Or56a knockout, block learning, silence the Giant Fiber) so you can see how the two flies diverge.

## Generations

**Play it:** https://tattooinmtl.github.io/omni-lifesim/generations/

A second version in `generations/` turns the garden into a breeding population. Three unrelated founders (A♀, B♂, C♀) each carry a diploid genome (two copies of every gene, one from each parent): smell receptor sensitivities, learning rate, Giant Fiber escape threshold, flight speed, lifespan, clutch size and body colour, plus their Kenyon-cell wiring. Learned memories are not inherited.

- **Life cycle** on a compressed clock (one fly day is 20 seconds at 1× speed), with durations from real *Drosophila* at 25 °C: egg 1 day, larva 4 days, pupa 4 days, adults living about 40 days. Flies die of old age or starvation.
- **Mating**: a mature, receptive female picks the least related free male, measured by kinship coefficient from the family tree. After mating she carries a clutch and, like a real fly after sex peptide, rejects males for a while.
- **Egg laying**: she flies to rotting fruit and lays her eggs there; larvae and pupae develop on and around the fruit. Each fruit and the garden have a capacity limit.
- **Inbreeding** lowers lifespan and clutch size. An unrelated wild fly arrives every 14 fly-days (or on demand) to bring in new genes.
- **Survival is hard.** Ageing risk rises steeply with age (Gompertz), sooner for inbred flies. Birds hunt by day and chase their prey; an early Giant Fiber jump (a heritable threshold) is the best defence. Spider webs hang at flying height near the clover. Cold nights and rainstorms make flight costly, and rain knocks flies down and drowns weak ones. Only one fly can feed on a clover at a time and nectar refills slowly, so flies compete; populations boom, starve and recover. Larvae eat the fruit, and starve when it is eaten bare. An Environment card switches birds, webs and weather on or off, sets the food supply, and tallies every death by cause. When fewer than 4 adults are left, wild flies arrive more often.
- **Family tree & timeline** window: every fly's life as a bar on a day axis, grouped by generation, with links from both parents at the moment the egg was laid. Hover a fly to see its whole line of ancestors and its story (sim day and real time of birth and death, parents, mates, clutches, offspring, inbreeding). The timeline shows eggs, larvae, pupae and adults per generation over time, with mean inbreeding.

## Controls

- **Left-click a fly:** swoop a looming shadow at it.
- **Right-click a fly:** the camera follows it. **Right-click the ground** to go back to the free camera.
- Drag to orbit, scroll to zoom.

## Brain circuit 3D window

The top-right window shows the model's neurons placed inside the real 3D brain. The brain volume is filled with a lattice of points in the shape of the fly brain, and the points inside each real region (antennal lobe, mushroom body, lateral horn, optic lobes, gnathal ganglia) glow with that region's activity. Each neuron sits in the region where that real cell type lives, and its connections follow the real routes: from the antenna into the antennal lobe, along projection-neuron tracts through the calyx to the lateral horn, from Kenyon cells down the peduncle into the lobes, and from the optic lobe to the Giant Fiber and out through the neck. Sparks travel along a connection while its source neuron is firing. The Kenyon-cell-to-MBON connections get brighter or dimmer as dopamine changes their weights, so you can watch learning happen.

**Real neurons.** The window also draws 78 real neurons from the FlyWire whole-brain connectome, downloaded as skeletons from Virtual Fly Brain: Or42b and Or56a smell receptor neurons, DM1 and DA2 projection neurons, lateral horn output neurons, γ, α/β and α′/β′ Kenyon cells, MBON-11 and MBON-1, PAM and PPL1 dopamine neurons, LPLC2 and LC10a visual neurons, the Giant Fiber, the DNa02 steering neuron and labellar taste neurons, each on both sides of the brain. Each real neuron is driven by the model neuron of the same type: when it fires, its whole branching arbor lights up and a wave runs out from the cell body. The menu in the window header switches between real neurons, the model wiring, or both. `tools/list_neurons.py` and `tools/fetch_neurons.py` rebuild that data.

It runs on the same signals as the 2D diagram in the sidebar. Hover a neuron to see its name, its FlyWire ID (for real neurons) and its activity, use A/B to switch flies, ⤢ to enlarge the window and – to collapse it. Positions come from real anatomy; the wiring is the model's.

## Brain meshes

The region meshes come from the JRC2018Unisex template on Virtual Fly Brain: the whole brain, antennal lobe, lateral horn, mushroom-body calyx, peduncle and lobes, medulla, lobula, lobula plate and gnathal ganglia. They were downloaded as OBJ files and shrunk with `tools/shrink.py` (vertex-clustering decimation, 16-bit quantized, base64 inline).

To rebuild the meshes, put the `.obj` files in a folder and run `python tools/shrink.py <mesh_dir> brain-meshes.json`.

Virtual Fly Brain data is shared under CC BY 4.0. Please credit Virtual Fly Brain and the JRC2018 templates (Bogovic et al., 2020) if you reuse them.

The brain model is a toy for exploration. It borrows the names and wiring logic of real circuits but is not a faithful simulation of them.
