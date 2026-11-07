# Independent fact-check — 2026-11-07 "How Long Would It Take to DRIVE to the Sun? 🚗☀️"

Each check was done by a separate agent that had not seen the build. It got only the mp4, the thumbnail, the narration script and the copy. It re-verified every claim with its own research and its own Python arithmetic, and it inspected frames sampled with ffmpeg.

## Round 1 — no factual errors; 2 layout fixes required
- All figures CORRECT:
  - 100 km/h ≈ 62 mph
  - Moon 384,400 km → ≈160 days (over 5 months)
  - Sun ≈150 million km → ≈171 years, arriving ≈2197
  - Sunlight 499 s = 8 min 19 s ("just over 8 minutes")
  - Proxima Centauri ≈4.2 ly ≈40 trillion km → over 45 million years
- Fix 1: the "Diagram, not to scale" footnote sat under the Shorts bottom overlay. **Fixed:** moved to y≈445 and enlarged to 32 px.
- Fix 2: the counter pills sat under the Shorts right-side buttons. **Fixed:** moved to the left side.
- Optional changes, both applied:
  - Removed the speedometer's brief "101" overshoot.
  - The description now says "on average 384,400 km".
- Also fixed: a hard rectangular edge on the Sun's glow.

## Round 2 (final render) — required fixes: none
| Claim | Result | Computation |
|---|---|---|
| 100 km/h ≈ 62 mph | CORRECT | 62.14 |
| Moon ≈384,400 km; ≈160 days; over 5 months | CORRECT | 160.17 d = 5.26 mo |
| Sun ≈150 million km; ≈171 years | CORRECT | 170.66 y |
| Arrive ≈ year 2197 | CORRECT | mid-2197 |
| Sunlight just over 8 min (8 min 19 s) | CORRECT | 499.0 s |
| Proxima ≈4.2 ly, nearest star | CORRECT | Britannica, NASA |
| ≈40 trillion km | CORRECT | 3.97–4.02e13 km |
| Over 45 million years | CORRECT | 45.3–45.8 My |
| Thumbnail "171 YEARS NONSTOP · AT 100 km/h" | CORRECT | — |
| "Not to scale" label visible; no false proportions | CORRECT | — |

Sources:
- https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html
- https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html
- https://www.britannica.com/science/astronomical-unit
- https://www.britannica.com/place/Proxima-Centauri
- https://science.nasa.gov/sun/facts/
- https://science.nasa.gov/exoplanets/what-is-a-light-year/
- https://www.britannica.com/science/light-year
