# Independent fact-check — 2026-11-09 "All of Earth's Water in ONE Ball Is Shockingly Small 🌍💧"

Done by separate agents that had not seen the build. Each got only the mp4, the thumbnail, the narration script and the copy, sampled frames with ffmpeg, re-verified every claim with its own web research and Python arithmetic, and measured the drawn spheres in pixels.

## Round 1 (first render) — required fixes: none
All claims CORRECT. Optional note applied: during the zoom (≈23.5–25 s) the "≈56 KM" headline appeared before the big ball was labelled and before the small ball showed, so a viewer could briefly mistake the big ball for the 56 km one. Fixed: big ball now labelled "ALL WATER ≈1,385 KM" from the start of the zoom, and the headline waits until the small ball appears. Scene 4 re-rendered.

## Round 2 (final render) — required fixes: none
| Claim | Result | Source / computation |
|---|---|---|
| Water covers ≈71% of Earth's surface | CORRECT | USGS How Much Water; NOAA globalocean.noaa.gov/the-ocean |
| All water ≈1.4 billion km³ | CORRECT | USGS 1,386,000,000 km³ |
| All-water ball ≈1,385 km (≈860 mi) wide | CORRECT | USGS; d=(6V/π)^(1/3)=1,383 km |
| Ball includes oceans, ice, lakes, rivers, groundwater, air | CORRECT | USGS sphere definition |
| Less than half the Moon's width | CORRECT | NASA NSSDC r=1,737.4 km → 1,385/3,474.8 = 0.399 |
| Fresh water in lakes & rivers → ball ≈56 km (≈35 mi) | CORRECT | USGS 93,113 km³, 56.2 km; computed 56.2 km |
| Earth vs water ball to scale | CORRECT | 800 px vs 86–88 px (expected 87.0) |
| Earth, ball, Moon to scale | CORRECT | Moon ≈217 px (expected 218.2) |
| Lakes ball vs all-water ball to scale | CORRECT | 523 px vs ≈21 px (expected 21.1) |
| Thumbnail "TO SCALE" | CORRECT | Earth limb fit 1,119 px, ball ≈121 px, ratio 0.108 (real 0.1087) |
| Opening line delivered truthfully | CORRECT | drained Earth + labelled "ALL WATER" ball from frame 0 |
| Title / description | OK | no overstatement |

Optional note (not applied): on-screen "EVERY LAKE & RIVER" matches USGS's own label; narration and description say "fresh water", which is the USGS figure (saline lakes excluded).
