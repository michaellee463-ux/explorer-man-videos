# Independent check — "The Moon Is Narrower Than the USA" (2026-11-27)

A separate agent did the check. It had not seen the fact sheet or the code, and it received only the mp4, the thumbnail, narration.txt, phonemes.txt and copy.md. It re-verified every claim with its own searches and its own Python, and measured scale drawings in sampled frames.

## Round 1 — PASS (1 optional nit)
- Duration: 65.63 s (1080x1920) ✔
- 20 claims checked across the narration, on-screen text, thumbnail and copy, all CORRECT:
  - Moon 3,475 km; USA 4,500+ km (great circle Cape Mendocino–West Quoddy 4,628 km); Moon/USA 0.75.
  - Australia ~4,000 km (ABS: Steep Point–Cape Byron).
  - Ceres is the largest object in the belt, and its disk ≈ Texas area (0.996; JPL calls it "Texas-sized").
  - Pluto 2,377 km is half the US width (NASA's own words).
  - Mercury is 1.05–1.08× the US width; Ganymede (5,268 km) is bigger than Mercury (NASA).
  - Mars is 1.46–1.51× the US width; Earth is 2.75–2.83×.
  - Moon surface 37.93 M km² = 3.86× total US area, 1.25× Africa (30.4 M, Britannica).
  - The flattened disk is exactly 2× as wide.
  - Pluto's surface is 17.74 M km² vs Russia's 17.1 M (1.04×).
- Scale drawings measured in frames, all proportional:
  - Moon vs US bar: 695 vs 930 px = 4,649 km line.
  - Pluto 0.51; Mercury/US 1.05; Ganymede/Mercury 1.08; Mars 1.48; Earth 2.8.
  - Flat Moon 1.97×; Russia vs flat Pluto by area 0.99.
- Hook, share line and comment question are honest: the video says "narrower", never "smaller", and states outright that the Moon is not smaller.
- Phonemes are fine (U S, Ceres, Ganymede, kilometers, versus).
- Nit: the small Pluto globe in the Pluto-surface scene was ~10% too small (flat disk 2.23× the globe instead of 2×), though nothing claims 2× there.

## Fix
Pluto globe in that scene redrawn at true scale (261 px vs the 523 px flat disk). Re-rendered frames 1476–1969 only.

## Round 2 — PASS
- Globe 262 px vs flat disk 520–524 px = 2.00× ✔; Russia/disk area 0.993 ✔.
- On-screen text unchanged and correct.
- Frames outside the scene are pixel-identical; spot checks at 0, 1, 12, 45, 60 and 64 s are unchanged.
- Duration 65.63 s ✔.

Key sources the checker used: NASA Pluto facts, NSSDC planetary fact sheets, NASA Ganymede facts, JPL "A Texas-sized space rock", Britannica (Ceres, Ganymede, Africa, United States), Snopes (Australia vs Moon), ABS (Australia's dimensions), Space.com (Moon).
