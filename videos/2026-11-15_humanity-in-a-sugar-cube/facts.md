# Fact sheet — All 8 Billion Humans in a Sugar Cube (2026-11-15, Short)

**Using the data:** vidIQ (Oct 18–Nov 15) shows ~90% of views come from the Shorts feed and the opening second decides reach (engaged-view rate 44–59% on the 8 Shorts that reached ~1,200–1,600 views vs 17–23% on the flops). Space / "you vs. tiny" scale wins, and statement hooks did at least as well as cliffhanger questions (Betelgeuse 59%, SS United States 59% vs Lightning 48%, Voyager 47%). So today: a "you vs. tiny" scale topic, frame 1 = the impossible-sounding claim on screen over the sugar cube (statement hook, no question), plus an explicit share line. Shares are near zero (7 total), so this tests a direct "send this to someone" trigger.

## Topic shortlist (score /50: shock, 2-second hook, proven demand, visual payoff, Explorer Man fit)

| Topic | Shock | Hook | Demand | Visual | Fit | Total |
|---|---|---|---|---|---|---|
| **All 8 billion humans fit in a sugar cube (atoms are mostly empty space)** | 10 | 10 | 10 (atoms/"empty space" Shorts trending this week: "You Never Actually Touch Anything" 1.0M views in a day, "You Are 99.9999999% Empty Space" 170k in 12 h) | 8 | 10 | **48** |
| Starship lands from orbit, first ship catch (Flight 15, Nov 14) | 8 | 8 | 9 (news) | 9 | 6 — near-duplicate of Nov 13 Starship Short | 40 (repeat risk) |
| Neutron star: a sugar cube weighs a billion tons | 9 | 8 | 8 | 7 | 9 | 41 (folded in as the payoff instead) |
| Beaver supermoon Nov 24: how much bigger, really? | 6 | 7 | 8 | 7 | 8 | 36 (better closer to Nov 24) |
| What if you dropped a tungsten rod from space | 8 | 8 | 7 | 7 | 7 | 37 |
| How many moons does each planet have | 6 | 7 | 7 | 7 | 8 | 35 |

**Pick:** humanity in a sugar cube. Highest score, evergreen mass appeal, rides this week's trending "empty space" wave with a different, concrete payoff (the cube and its weight), fits "You vs…" (#3; last series Short was Nov 12, not back-to-back). Not a repeat: the earlier "You vs. The Smallest Thing" Short was a size ladder from a fingertip down to the Planck length; this one is about compressing matter (mass vs volume).

## Claims, sources, numbers

1. **World population ≈ 8.3 billion (2026).** UN World Population Prospects 2024 projection, 8.30 bn on 1 Jul 2026 — https://statisticstimes.com/demographics/world-population.php ; IPS / UN, "world population in 2026 is 8.3 billion" — https://www.ipsnews.net/2026/03/planet-earths-increasing-population-of-8-billion/ . Said as "eight billion people" (true, rounded down).
2. **Almost all of an atom is space; the nucleus is tiny.** Britannica: nucleus "makes up more than 99.9% of the atom's mass but only" a tiny fraction of its volume — https://www.britannica.com/summary/atom ; Univ. of Oregon: nucleus "constitutes more than 99.9 percent of the mass… though it occupies only about 10^-14 of the volume" — https://pages.uoregon.edu/jschombe/glossary/atom.html . Atom is ~22,000–63,000× wider than its nucleus (compute.py, H/C/O radii).
3. **"If an atom were a stadium, the nucleus would be about a pea in the middle."** Standard analogy (e.g., Indiana Univ. STEM for Educators — https://iu.pressbooks.pub/stemforeducators/chapter/chapter-1-3-atomic-structure-isotope/ ; UCAR Windows to the Universe — https://windows2universe.org/physical_science/physics/atom_particle/atomic_nucleus.html ). Check: stadium 100–200 m ÷ pea 5–9 mm = 11,000–40,000×, same order as the real 22,000–63,000× (compute.py).
4. **More than 99.9% of an atom's mass is in the nucleus.** Britannica + Univ. of Oregon (above); proton is 1,836× an electron → even hydrogen's nucleus holds 99.95% (compute.py).
5. **Squeeze one person's nuclei together → a speck thinner than a hair.** Nuclear density ≈ 2.3×10^17 kg/m³ (HyperPhysics / standard texts; Astronomy magazine gives neutron-star matter ~10^14 g/cm³ = 10^17 kg/m³ — https://www.astronomy.com/science/the-cubic-centimeter-a-cosmic-measuring-cup/ ). 62 kg adult (Walpole 2012) → sphere ~8 µm across; human hair ~17–180 µm (compute.py).
6. **All of humanity → about a sugar cube.** Astronomy magazine (Mar 2023): "everyone's combined atomic nuclei — would fit inside a single sugar cube"; "our entire species amounts to 1 cubic centimeter… after you've removed the empty spaces" — URL above. Space.com: a neutron-star sugar cube "weighs as much as… the entire human race" — https://www.space.com/22180-neutron-stars.html . Our computation: 1.4–2.1 cm³, a cube 1.1–1.3 cm on a side → "a cube just over a centimeter wide, about the size of a sugar cube" (compute.py).
7. **It would still weigh about 400 million tonnes.** Mass is unchanged. Walpole et al. 2012 (BMC Public Health; LSHTM): adults alone 287 million tonnes in 2005, average 62 kg — https://www.lshtm.ac.uk/newsevents/news/2012/tacking_population_weight_crucial_for_food%20security.html ; Bar-On, Phillips & Milo 2018 (PNAS): humans ≈ 0.06 Gt carbon — https://pmc.ncbi.nlm.nih.gov/articles/6016768 . Scaled to 8.3 bn: 354–426 Mt (compute.py) → "about four hundred million tonnes".
8. **More than a thousand Empire State Buildings.** ESB fact sheet: "The building weighs 365,000 tons" (short tons = 331,000 t) — https://esbnyc.com/sites/default/files/esb_fact_sheet_final.pdf ; humanity = 1,070–1,290 ESBs (compute.py).
9. **Neutron stars really do this: a Sun's worth of mass in a ball about 20 km wide (city-sized).** NASA Imagine the Universe: "about 20 kilometers (12.5 miles) across", "the mass of a sun squished down to the size of a city"; "one sugar cube of neutron star material would weigh about 1 trillion kilograms" — https://imagine.gsfc.nasa.gov/science/objects/pulsars1.html ; Space.com: "10 and 20 kilometers" — URL above.

Not used (could not cleanly verify or contested): "you never actually touch anything"; exact % of empty space (sources disagree: 10^-14 vs 1/100,000 of volume).

Scripts: compute.py → compute_output.txt. Step-0 analysis: step0_analysis.py → step0_output.txt.
