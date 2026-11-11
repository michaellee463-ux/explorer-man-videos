# Independent fact-check — 2026-11-11 "How Deep Have We REALLY Dug? Journey to the Center of the Earth" (long-form, 3:43)

Done by separate agents that had not seen the build. Each got only the mp4, the thumbnail, the narration script and the copy; sampled frames with ffmpeg, re-verified every claim with its own web research and Python arithmetic, and measured drawings in pixels.

## Round 1 (first render) — 1 required fix
- WRONG: the Kola scene had a running year + depth counter that rose in a straight line, so in-between frames paired real years with invented depths (e.g. "1980 – 6,505 m"; the real record was ≈7,263 m by ≈1974, >9,583 m in 1979, 12,066 m in 1984). **Fixed:** the counter was removed; the scene now shows "1970", then "1970 – 1989 / drilling…" while the drill line grows, then "1989 / 12,262 m". Kola scene re-rendered.
- Optional, applied: chapter "What if you fell…" moved 2:33 → 2:34; tag "earthscore" → "earthcore".
- Everything else CORRECT (all figures, scale drawings, chapters).

## Round 2 (final render) — required fixes: none
| Claim | Result | Sources / arithmetic |
|---|---|---|
| ≈6,370 km to the center | CORRECT | NASA fact sheet 6,371 km; Britannica "some 6,370 km" |
| Kola: started 1970, 12,262 m in 1989, 19 years | CORRECT | Wikipedia; EarthDate (UT Austin) |
| On-screen year/number pairings | CORRECT | no running counter; only 1970, "1970 – 1989", "1989 / 12,262 m" |
| Deepest hole humans have ever drilled | CORRECT (vertical depth) | Wikipedia; Global Times (Shenditake-1 10,910 m, 2nd); longer slanted wells are shallower |
| 12 ÷ 6,370 ≈ 0.19%; >99.8% never reached | CORRECT | 0.188–0.192%; 99.81% |
| 1 m globe → ≈1 mm hole | CORRECT | 0.96 mm |
| "Kola drawn to scale, less than one pixel" | CORRECT | 0.73 px at R = 380 px |
| Kola never left the crust | CORRECT | Wikipedia, EarthDate (≈1/3 through ≈35 km crust) |
| Oceanic crust ≈5–6 km; continental ≈30–40 km | CORRECT | USGS, Britannica |
| Mantle to ≈2,900 km, almost halfway; >80% of volume | CORRECT | USGS, NatGeo (84%), Live Science; 45.5%, 83.7% |
| Outer core liquid iron & nickel, ≈2,200 km thick; makes magnetic field | CORRECT | USGS, NatGeo, Live Science |
| Inner core from ≈5,100 km, radius >1,200 km | CORRECT | Britannica, NatGeo 1,220 km, Wikipedia 1,221 km |
| ≈5,000–6,000 °C, roughly the Sun's surface | CORRECT | NatGeo, Wikipedia, NASA (photosphere 5,500 °C), Live Science |
| Pressure >3 million × sea level; keeps inner core solid | CORRECT | Wikipedia 3.3–3.6 million atm, NatGeo |
| Fall through Earth: ≈42 min uniform, ≈38 min real density | CORRECT | Klotz arXiv:1308.1342, Phys.org; π√(R/g) = 42.2 min |
| Walk 5 km/h nonstop → ≈53 days | CORRECT | 6,370/5 = 1,274 h = 53.1 d |
| Opening question answered truthfully | CORRECT | 12,262 m, ≈0.19% of the way |
| Scale drawings (cross-sections, 50 km crust panel, Kola ruler) | PROPORTIONAL | radii 0.545/0.198 vs 0.546/0.192; crust 6.0, 30–40 km; Kola 12.25 km |
| Chapters | all within 1 s | |
| Title, description, TikTok caption, thumbnail | no overstatement | |

Optional note applied: description adds "deepest by true vertical depth; some slanted oil wells are longer but far shallower."
