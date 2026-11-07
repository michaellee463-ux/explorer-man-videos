# Fact sheet — "How Long to DRIVE to the Sun?"

Vertical Short, 1080×1920. This sheet is the only source of figures for the video, the thumbnail, the title and the description.
All derived figures come from `compute.py`; its results are in `compute_output.txt`.

## Sources
- [N3] NASA NSSDC Moon Fact Sheet — https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html (semimajor axis 0.3844×10⁶ km)
- [BM] Britannica, Moon — https://www.britannica.com/place/Moon (mean distance 384,400 km)
- [NS] NASA NSSDC Sun Fact Sheet — https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html (mean distance from Earth 149.6×10⁶ km)
- [NE] NASA NSSDC Earth Fact Sheet — https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html (semimajor axis 149.598×10⁶ km)
- [BA] Britannica, astronomical unit — https://www.britannica.com/science/astronomical-unit (149,597,870.7 km, fixed by IAU 2012)
- [NSF] NASA Science, Sun facts — https://science.nasa.gov/sun/facts/:
  - Sun "about 93 million miles (150 million kilometers)" away
  - "Proxima Centauri is 4.24 light-years away"
  - light-year "about … 9.5 trillion kilometers"
- [BP] Britannica, Proxima Centauri — https://www.britannica.com/place/Proxima-Centauri ("the closest star to the Sun, about 4.2 light-years distant"; elsewhere 4.23 ly)
- [BL] Britannica, light-year — https://www.britannica.com/science/light-year (9.46073×10¹² km)
- [BC] Britannica, speed of light — https://www.britannica.com/science/speed-of-light (exactly 299,792,458 m/s)
- [NIST] https://physics.nist.gov/cgi-bin/cuu/Value?c (c exact)

## Input figures (≥2 sources each)
| # | Claim | Value used | Sources |
|---|---|---|---|
| 1 | Mean Earth–Moon distance | 384,400 km | N3, BM |
| 2 | Mean Earth–Sun distance | ≈149.6 million km (1 au = 149,597,870.7 km); "about 150 million km" | NS, NE, BA, NSF |
| 3 | Proxima Centauri is the nearest star to the Sun | — | BP ("closest star to the Sun"), NSF ("nearest stellar neighbor") |
| 4 | Distance to Proxima | about 4.2 light-years (sources give 4.2–4.24) | NSF, BP |
| 5 | Light-year | ≈9.46 trillion km | BL, NSF (≈9.5 trillion) |
| 6 | Speed of light | 299,792.458 km/s | BC, NIST |
| 7 | Car speed | 100 km/h (our assumption; stated on screen) | — |

## Derived figures (compute_output.txt)
- 100 km/h = 62.1 mph → "about 62 mph"
- Moon: 3,844 h = 160.2 days = 5.3 months → **"about 160 days, over 5 months"**
- Sun: 170.7 years, whether you use 1 au or 149.6 million km → **"about 171 years"**
  - Leaving in Nov 2026 means arriving around 2197.5 → **"around the year 2197"**
- Sunlight Earth→Sun distance: 499.0 s → **"about 8 minutes 19 seconds" / "just over 8 minutes"**
- Proxima: 4.2–4.24 ly = 39.7–40.1 trillion km → **"about 40 trillion km"**
  - Drive time 45.3–45.8 million years → **"over 45 million years"**

## Presentation rules
- Driving means nonstop, at a constant 100 km/h, along the average straight-line distance. The video says so ("nonstop", "no stops, no sleep").
- Path drawings are diagrams, **not to scale**, and they are labelled that way.
- Avoided: lifetime comparisons and the dinosaur-extinction comparison. Two sources could not be retrieved for them this run.
