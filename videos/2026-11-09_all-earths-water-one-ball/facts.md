# Fact sheet — "All of Earth's Water in One Ball" (Short, 1080×1920)

Only figures in this sheet may appear in the video, thumbnail, title or description. Derived figures come from `compute.py` (output in `compute_output.txt`).

## Sources
- [USGS-HOW] USGS Water Science School, How Much Water is There on Earth? — https://www.usgs.gov/special-topics/water-science-school/science/how-much-water-there-earth — "be about 860 miles (about 1,385 kilometers) in diameter"; "1,386 million cubic kilometers (km3)"; "About 71 percent of the Earth's surface is water-covered"
- [USGS-IMG] USGS, All of Earth's water in a single sphere! — https://www.usgs.gov/media/images/all-earths-water-a-single-sphere — "Its diameter is about 860 miles"; "(1,386,000,000 cubic kilometers (km3))"; lakes and rivers sphere "about 22,339 mi3 (93,113 km3)", "about 34.9 miles (56.2 kilometers)"
- [USGS-WHERE] USGS, Where is Earth's Water? — https://www.usgs.gov/special-topics/water-science-school/science/where-earths-water — lakes and rivers "about 22,300 cubic miles (93,100 cubic kilometers), which is about 1/150th of one percent of total water"
- [SCIAM] Scientific American, It's a Water-Full World — https://www.scientificamerican.com/article/its-a-water-full-world — "about 1,385 kilometers in diameter"; "56.2 kilometers in diameter" (lakes and rivers); "a little more than 70 percent of the Earth's surface is covered by water"
- [EARTHSKY] EarthSky, If you made a sphere of all Earth's water… — https://earthsky.org/earth/if-you-made-a-sphere-of-all-earths-water-how-big-would-it-be/ — "All the water on Earth would fit into a sphere 860 miles (1,385 km) wide."
- [NOAA] NOAA Ocean Service, How much water is in the ocean? — https://oceanservice.noaa.gov/facts/oceanwater.html — "over 1,386,000,000 cubic kilometers"; "About 97 percent of Earth's water is in the ocean."
- [NASA-E] NASA Science, Earth Facts — https://science.nasa.gov/earth/facts/ — "equatorial diameter of 7,926 miles (12,756 kilometers)"; ocean "covers about 71% of the planet's surface"
- [NASA-M] NASA Science, Moon Facts — https://science.nasa.gov/moon/facts/ — "radius of about 1,080 miles (1,740 kilometers)"
- [UT-M] Universe Today, Diameter of the Moon — https://www.universetoday.com/19677/diameter-of-the-moon/ — "The diameter of the Moon is 3,474 km"

## Claims used
| # | Claim (as worded in video) | Sources |
|---|---|---|
| 1 | Water covers about 71% of Earth's surface | USGS-HOW, NASA-E, SCIAM (">70%") |
| 2 | All of Earth's water (oceans, ice, lakes, rivers, underground, air) ≈ 1.4 billion km³ | USGS-HOW, USGS-IMG, NOAA (1.386 billion) |
| 3 | Gathered into one ball it is only about 1,385 km (≈860 miles) wide | USGS-HOW, USGS-IMG, SCIAM, EARTHSKY |
| 4 | That ball is less than half the width of the Moon | NASA-M (d≈3,480 km), UT-M (3,474 km); computed 0.40 |
| 5 | All the fresh water in the world's lakes and rivers: a ball about 56 km (≈35 miles) wide | USGS-IMG, SCIAM; USGS-WHERE (93,100 km³); computed 56.2 km from volume |

## Derived (compute_output.txt)
- Sphere of 1.386e9 km³ → 1,383 km diameter (USGS rounds to 1,385) ✔
- Sphere of 93,113 km³ → 56.2 km ✔; 56.2 km = 34.9 mi
- 1,385 / 3,474–3,480 = 0.40 → "less than half the Moon's width" ✔
- Earth (12,756 km) is ≈ 9.2× wider than the water ball.

## Presentation rules
- Earth, water ball, Moon and lakes-and-rivers ball are drawn to one scale (Earth r = 400 px ↔ 6,378 km): ball r = 43.4 px, Moon r = 108.9 px, lakes ball r = 1.76 px (the zoomed shot keeps the same ratio).
- The Moon is shown beside the ball for size only — not at its real distance (labelled "sizes to scale, not distance").
- "1.4 billion" is said with "about". Ocean share of water (97%) not used on screen.
- Dropped: the 272.8 km liquid-fresh-water sphere (keeps it to one reveal).
