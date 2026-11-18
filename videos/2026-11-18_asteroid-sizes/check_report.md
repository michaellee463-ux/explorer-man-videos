# Independent fact-check — 2026-11-18 "How Big Does an Asteroid Have to Be to End the World? ☄️ Every Size Compared" (long-form, 4:12)

Done by a separate agent that had not seen the build or facts.md. It got only the mp4, thumbnail, narration + phonemes and the copy; sampled frames every 2 s with ffmpeg, re-verified every claim with its own web research and Python, and measured the scale drawings in pixels.

## Round 1 — 4 required fixes
- WRONG: "none of the asteroids we know about has a significant chance of hitting us in the next 100 years" — NASA limits this to asteroids **larger than 140 m** (small known asteroids, e.g. 2008 TC3, 2024 XA1, have hit). **Fixed** in VO and pill ("NO KNOWN ASTEROID OVER 140 m…").
- WRONG: DART was "the first time humans changed the motion of an object in space on purpose" — spacecraft are objects in space; NASA says "celestial object". **Fixed:** "a natural object in space".
- Copy: "1,500 people hurt by flying glass" → **fixed** to "mostly by flying glass".
- Layout: subtitle covered "−32 MINUTES" in the DART scene. **Fixed** (stats moved up).
- Optional, applied: Chicxulub rock rotated so its 10+ km axis is vertical (now clearly taller than Everest); "would have global consequences" → "could have global effects" (JPL wording); chapters re-timed to the cuts.

## Round 2 (final render) — required fixes: none
| Claim | Result | Sources / arithmetic |
|---|---|---|
| Apophis Fri Apr 13 2029, ≈340 m (≈Eiffel Tower), ≈32,000 km up, closer than GEO (~36,000 km), naked-eye from Europe/Africa, ~once every few thousand years, no risk ≥100 yr | CORRECT | NASA Apophis facts; 2029-04-13 is a Friday |
| Shooting stars = dust/sand grains, burn up | CORRECT | standard meteor science (NASA) |
| Chelyabinsk ≈20 m, 15 Feb 2013, ≈19 km/s, unseen, ≈30 km up, brighter than Sun, ≈500 kt ≈30× Hiroshima, ≈1,500 hurt mostly by glass | CORRECT | Planetary Society, JPL; 500/15 = 33 |
| Tunguska 50–100 m, 30 Jun 1908, 5–10 km up, ≈80 M trees, ≈2,000 km², up to 15 Mt ≈ up to 1,000× Hiroshima, no clear crater | CORRECT | Britannica, Live Science; 15,000/15 = 1,000 |
| Meteor Crater: iron ≈50 m, ≈50,000 yr, 1.2 km × ≈180 m, ≈11 football fields | CORRECT | Britannica, NASA EO; 1,200/109.73 = 10.9 |
| ~1 km could have global effects; >90% of 1 km NEAs found; no known >140 m asteroid with significant risk in 100 yr | CORRECT | JPL; NASA Planetary Defense overview |
| Chicxulub ≈66 Mya, 10–15 km, taller than Everest, crater ≈150–180 km, billions × Hiroshima, ≈3 in 4 species, birds survived | CORRECT | NSF (100 Tt → 6.7 bn × 15 kt), NHM, Live Science |
| DART 2022, ≈160 m Dimorphos, orbit 11 h 55 → 11 h 23 min (−32), first deliberate change of a natural object's motion | CORRECT | NASA DART, Smithsonian |
| Scale drawings: orbit diagram (GEO 6.62 vs Apophis 6.02 Earth radii), Eiffel vs Apophis, 20 m/340 m/1 km, crater/rock/fields, Everest vs rock (≈11.6 × 9.1 km, top ≈2.6 km above summit) | PROPORTIONAL | pixel measurements |
| Opening question answered honestly; comment question, share line, title and thumbnail honest (no implication Apophis will hit) | CORRECT | |
| Pronunciation (Apophis, Chelyabinsk, Tunguska, Siberia, Hiroshima, geosynchronous, DART, years) | CORRECT | phonemes.txt |
| Chapters within ≤1 s of the cuts (2:59 and 3:28 nudged onto the cut) | CORRECT | |
| Duration 252.1 s (3–6 min) | PASS | ffprobe |
