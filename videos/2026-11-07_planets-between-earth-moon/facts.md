# Fact sheet — "Every Planet Fits Between Earth and the Moon… Barely"

Short, 1080×1920. Every figure below is the only source of numbers for the video, thumbnail, title and description.
Derived figures: `compute.py` → `compute_output.txt` (same folder).

## Sources
- [N1] NASA NSSDC Planetary Fact Sheet — https://nssdc.gsfc.nasa.gov/planetary/factsheet/
- [N2] NASA NSSDC fact sheet notes ("Diameter … at the equator") — https://nssdc.gsfc.nasa.gov/planetary/factsheet/planetfact_notes.html
- [N3] NASA NSSDC Moon Fact Sheet — https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html
- [N4] NASA NSSDC Earth Fact Sheet — https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html
- [N5] NASA Science, Moon Facts — https://science.nasa.gov/moon/facts/
- [H] HyperPhysics (Georgia State Univ.) Planetary Data, "Equatorial diameter, km" — https://hyperphysics.gsu.edu/hbase/Solar/soldata.html
- [B] Encyclopaedia Britannica, Moon — https://www.britannica.com/place/Moon
- [P] Phil Plait, "Can You Really Fit All the Planets Between the Earth and Moon?" — https://www.syfy.com/syfy-wire/can-you-really-fit-all-planets-between-earth-and-moon
- [E] EarthSky, close and far moons — https://earthsky.org/astronomy-essentials/definition-perigee-apogee-close-and-far-moons/
- [NIST] Speed of light, exact 299,792,458 m/s — https://physics.nist.gov/cgi-bin/cuu/Value?c

## Input figures (each confirmed by ≥2 sources)
| # | Claim | Value used | Sources |
|---|---|---|---|
| 1 | Equatorial diameters (km): Mercury 4,879 · Venus 12,104 · Mars 6,792 · Jupiter 142,984 · Saturn 120,536 · Uranus 51,118 · Neptune 49,528 · Earth 12,756 | as listed | N1+N2 (equatorial), H (identical values) |
| 2 | Mean Earth–Moon distance (centre to centre) | 384,400 km | N3 (semimajor axis 0.3844×10⁶ km), N5, B, E |
| 3 | Moon at its farthest (mean apogee, centre to centre) | about 405,500 km | N3 (mean apogee 0.4055×10⁶ km); P (~406,000 km); E (2021 farthest 406,512 km) |
| 4 | Moon at its closest (mean perigee) | about 363,300 km | N3 (0.3633×10⁶); P/E (closest ≈ 357,000 km — even closer, so conclusion "doesn't fit" holds a fortiori) |
| 5 | Earth mean radius 6,371 km; Moon mean radius 1,737.4 km | — | N4, N3; B |
| 6 | The Moon's orbit is an ellipse (oval), distance changes every month | — | N3 (range ≈357,000–407,000 km), E, B (eccentricity 0.0549) |
| 7 | The Moon is slowly drifting away, "a few centimetres a year" | NASA: ~1 inch/yr; Britannica: 3.8 cm/yr → both are "a few cm" | N5, B |
| 8 | Speed of light | 299,792.458 km/s | NIST |
| 9 | At average distance the planets don't fit using equatorial diameters; at apogee they do | — | P (same conclusion), compute.py |

## Derived figures (compute_output.txt)
- Sum of the 7 other planets' equatorial diameters = **387,941 km → "about 388,000 km"**.
- Surface-to-surface gap at mean distance = 376,292 km → planets **≈11,600 km too long** (shown as "about 11,600 km short").
- Gap at mean apogee = 397,392 km → **9,451 km to spare → "over 9,000 km to spare"**.
- Gap at mean perigee = 355,192 km → ≈32,700 km short ("they don't fit").
- 384,400 / 12,756 = 30.1 → **"about 30 Earths"** fit across the average distance.
- Jupiter / Earth diameter = 11.2 → **"11 times wider than Earth"**.
- Light time over 384,400 km = 1.28 s → **"about 1.3 seconds"**.
- 384,400 km = 238,855 mi; 388,000 km ≈ 241,000 mi (description only).

## Presentation rules / caveats
- "Every planet" = the seven planets other than Earth (Pluto is not a planet; Earth is one end of the line). Say "all 7 other planets".
- Planets are lined up by their equatorial widths (conservative: lined up pole-to-pole they'd take even less room). Saturn's rings not counted — on-screen footnote says so.
- On-screen layout is to scale: one vertical px scale for all bodies and distances.
- Avoided: specific apogee extremes, exact recession rate (sources differ: 1 inch vs 3.8 cm).
