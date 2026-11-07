# Independent fact-check — 2026-11-07 "All 7 Planets Fit Between Earth and the Moon… Sometimes"

Checks were run by separate agents that had not seen the build. Each got only the mp4, thumbnail, narration script and copy. Each re-verified claims with its own web searches, did its own Python arithmetic, and measured pixel scale in sampled frames.

## Round 1 (first render) — 1 required fix
- Every number in the video, narration and description: CORRECT.
- Scale drawing: within 1–2 px everywhere; overlap and spare boxes within 2.4%.
- **WRONG (misleading):** the thumbnail said "ALL 7 PLANETS FIT IN HERE… BARELY" with no condition. At the Moon's average distance the planets don't fit. **Fixed:** changed to "…SOMETIMES".
- Optional changes, all applied:
  - Title now says "All 7 Planets".
  - Narration now says "four hundred five thousand five hundred km", matching the 9,000+ km spare.
  - Right-side labels moved left so the Shorts buttons don't cover them.

## Round 2 (final render) — no required fixes
| Claim | Result | Computation / source |
|---|---|---|
| Only sometimes fits | CORRECT | Needs centre distance > 396,049 km |
| Moon ≈384,400 km | CORRECT | NASA NSSDC semimajor axis |
| ≈30 Earths | CORRECT | 384,400/12,756 = 30.1 |
| Jupiter 11× Earth | CORRECT | 11.2 |
| 7 planets ≈388,000 km | CORRECT | 387,941 |
| ≈11,600 km too long at average distance | CORRECT | 11,649 |
| Farthest ≈405,500 km | CORRECT | NASA mean apogee |
| 9,000+ km (≈9,450) to spare | CORRECT | 9,451 |
| Light ≈1.3 s | CORRECT | 1.33 s |
| Drifts a few cm/yr | CORRECT | 3.8 cm/yr (NASA JPL) |
| To-scale drawing (video & thumbnail) | CORRECT | All bodies within ~1–2 px; thumbnail within 0.8% |

Sources:
- https://nssdc.gsfc.nasa.gov/planetary/factsheet/
- https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html
- https://www.jpl.nasa.gov/news/the-apollo-experiment-that-keeps-on-giving/
- https://eclipse.gsfc.nasa.gov/help/ApolloLaser.html

Optional note applied: the description says "on average about 405,500 km" for the farthest point.
