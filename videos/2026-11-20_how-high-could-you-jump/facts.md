# Fact sheet: How high could you jump on other worlds? (Short, made 2026-11-19 on request)

Using the data: built from this morning's playbook (learnings.md, Nov 19) instead of a fresh analytics pull: frame 1 carries the most extreme true number mid-action (rule 2), a "you vs. scale" space ladder (rule 4), one share line and one one-word comment question (rule 9), a mid-way tease and a new visual every 2-3 s (rule 3b). Michael's requests for this one: no voice, the music from the first Shorts, graphics as detailed as the Voyager Short.

## Topic shortlist (scores 1-10: curiosity / 2-second hook / proven demand / visual payoff / fit)

| Topic | Score | Note |
|---|---|---|
| **How high could you jump on other worlds (Earth -> Mars -> Moon -> Pluto -> Enceladus -> Phobos -> comet 67P)** | 8/9/8/9/9 = **43** | Picked. Not on posted.md. "You vs." scale ladder like the channel's best Shorts. A 13-second version from a 33-subscriber channel was pulling ~1,260 views/hour today (vidIQ trending, Nov 19). |
| Star size ladder ("there's always a bigger star") | 8/8/9/9/9 = 43 | Rejected: too close to "How Big Is the Sun" and "What If Betelgeuse Replaced the Sun". |
| Neutron star vs. a city | 8/8/8/8/9 = 41 | Rejected: the sugar-cube Short already ends on the neutron star. |
| Tallest mountains in the solar system | 37 | Weaker hook. |
| Fastest winds in the solar system | 34 | Harder to show without narration. |
| A day / a year on every planet | 33 | Weaker payoff. |
| Supernova SN 2026ahvu (news, Nov 18) | 32 | Niche news, weak 2-second hook. |
| Supermoon of Nov 24 | 32 | Small payoff ("7% bigger"). |

Trend sources: vidIQ Shorts outliers "space size comparison" (this month) and vidIQ trending Shorts "space planets universe science" (since Nov 12); web searches for this week's space news.

## The model (stated on screen in the end card and in the description)

- A person's push-off gives the **same take-off speed everywhere**: the speed of a 0.50 m (20 in) standing jump on Earth, v0 = sqrt(2 x 9.80665 x 0.50) = **3.13 m/s (7.0 mph)**.
- Height = how far the body rises (centre of mass). Suit weight is not counted, no air resistance.
- Constant-gravity formulas h = v0^2 / (2g) and air time = 2 v0 / g, except Phobos (gravity weakens with height: exact two-body formulas) and comet 67P (escape).
- All derived numbers come from `compute.py` (output in `compute_output.txt`).

## Claims

| # | On screen | Checked value | Sources |
|---|---|---|---|
| 1 | Earth: "0.5 m", "20 inches · a solid standing jump" | Adult vertical-jump norms: men "average" 41-50 cm (16-20 in), women 31-40 cm; one study mean 45 cm (men), 30 cm (women). 0.50 m = 19.7 in | Topend Sports norms [1]; Marathon Handbook [2] |
| 2 | Mars: "GRAVITY 38% OF EARTH", "1.3 m", "4.3 ft · 1.7 s off the ground" | g = 3.73 m/s2 -> 38.0%; 1.315 m = 4.31 ft; 1.68 s | NASA Mars fact sheet [3]; computed |
| 3 | Moon: "17% OF EARTH", "3.0 m", "10 ft · 3.9 s off the ground", "REAL TIME" | g = 1.62 m/s2 -> 16.5%; 3.027 m = 9.93 ft; 3.87 s (the shot runs at real speed) | NASA Moon fact sheet [4]; computed |
| 4 | "BASKETBALL HOOP · rim: 3.05 m (10 ft)" (hologram to scale) | NBA Rule 1: ring "with its upper edge 10' above and parallel to the floor"; backboard 6' x 3.5'; ring 18" inside diameter. 10 ft = 3.048 m. Jump 3.03 m = 0.993 x rim height | NBA official rules [5]; Wikipedia "Basket (basketball)" [6] |
| 5 | Pluto: "6% OF EARTH", "7.9 m", "26 ft · 10 s off the ground", "3x SPEED" | g = 0.62 m/s2 -> 6.3%; 7.909 m = 25.95 ft; 10.1 s (shown in 3.37 s = 3x) | NASA Pluto fact sheet [7]; computed |
| 6 | "GIRAFFE · 5.5 m (18 ft)" (hologram to scale) | "males (bulls) may exceed 5.5 metres (18 feet) in height"; tallest land animal. Jump clears 5.5 m by 2.4 m | Britannica [8]; Live Science [9] |
| 7 | Enceladus: "MOON OF SATURN", "1.2% OF EARTH", "43 m", "142 ft · 55 s off the ground", "15x SPEED" | g = 0.113 m/s2 (0.0116 g) -> 1.15%; 43.39 m = 142.4 ft; 55.4 s (shown in 3.70 s = 15x) | Wikipedia "Enceladus" infobox [10]; The Planetary Society [11]; computed |
| 8 | "14-STORY BUILDING · about 43 m (142 ft)" (hologram to scale) | 14 storeys x 3.1 m = 43.4 m (storey heights vary, hence "about") | computed |
| 9 | Phobos: "MOON OF MARS", "0.06% OF EARTH" | Mean surface gravity 0.0057 m/s2 (581 micro-g) -> 0.058-0.059%. NASA: "about one-thousandth of Earth's gravitational pull" | Wikipedia "Phobos (moon)" [12]; NASA Mars moons facts [13] |
| 10 | Phobos: "≈ 900 m" (live counter stops at 900 m), "≈ 3,000 ft", "about 20 MINUTES off the ground", timer to 20:04, "200x SPEED" | Mass 1.0637e16 kg, mean radius 11.08 km -> GM = 7.0995e5 m3/s2, escape speed 11.3 m/s. Exact rise 918 m = 3,012 ft, 1,205 s = 20.1 min (constant-g check: 848 m, 18.1 min). Shown at ~200x | [12]; computed |
| 11 | Phobos note (left side, from 3.5 s into the wide shot): "USING AVERAGE GRAVITY · In its weakest spots, this same jump could escape Phobos." | Gravity varies a lot over the lumpy, tide-stretched moon (0.003-0.0068 m/s2); a 2018 analysis found the speed needed to escape ranges from about 5 km/h in some places to about 36 km/h in others. The jump is 11.3 km/h. Own rough check (compute.py): straight up from the sub-Mars tip, about 2.66 m/s (9.6 km/h) is enough to reach the L1 point 16.6 km from the centre; the jump is 1.18x that | Science / Eos reports of the Advances in Space Research study [14] [15]; Astronomy [16]; computed |
| 12 | "BURJ KHALIFA · 828 m · tallest building on Earth" (hologram to scale) | Architectural height 828 m (2,717 ft), "#1 Tallest in the World", completed 2010. 918 / 828 = 1.11 | CTBUH Skyscraper Center [17]; ingenieur.de, 1 Sep 2026: still the tallest, Jeddah Tower not finished [18] |
| 13 | Comet 67P: "A 4 KM LUMP OF ICE AND DUST", "GRAVITY ALMOST ZERO" | Lobes 4.1 x 3.3 x 1.8 km and 2.6 x 2.3 x 1.8 km; surface gravity "roughly one hundred thousand times weaker than Earth's" | Wikipedia "67P/Churyumov-Gerasimenko" [19]; ESA "Landing on a comet" [20] |
| 14 | "SPEED NEEDED TO ESCAPE ≈ 1 m/s (2 mph)", "YOUR JUMP 3.1 m/s (7 mph)" | Escape velocity "est. 1 m/s" (= 2.2 mph). Philae touched down at about 1 m/s ("walking pace"), bounced at 0.38 m/s, rose ~1 km and took 1 h 50 min to come back, so even 0.38 m/s nearly left. v0 = 3.13 m/s = 7.0 mph = 3.1x escape speed | [19]; [20]; Science in School (ESA teaching article) [21] |
| 15 | "YOU NEVER COME DOWN", "still leaving at 3 m/s", "You are now orbiting the Sun.", "150x SPEED" | Speed left after escaping = sqrt(3.13^2 - 1^2) = 2.97 m/s. Free of the comet, you share its orbit around the Sun. Distance counter: 0.24 km at 77 s, then +2.97 m/s (3.2 km after ~18 min) | computed |
| 16 | Hook: "ONE JUMP. ≈ 20 MINUTES OFF THE GROUND" over Phobos with Mars behind | Claim 10. Mars from Phobos spans ~42 degrees of sky (Phobos orbits ~6,000 km above the surface) | [13]; computed |
| 17 | End card: Earth 0.5 m, Mars 1.3 m, Moon 3 m, Pluto 7.9 m, Enceladus 43 m, Phobos ≈ 900 m, Comet 67P GONE; "Same push-off as a 0.5 m (20 in) jump on Earth. Suit weight not counted." | Claims 1-15 | — |

## Backdrops (not claims, but drawn from real data)

- Sizes in the sky use real angular diameters: Earth from the Moon 1.9°, Charon from Pluto 3.8°, Saturn from Enceladus 29° with its rings edge-on (Enceladus orbits in the ring plane), Mars from Phobos 42°.
- Enceladus's south-polar plumes and "tiger stripe" fractures are real (Cassini); here they are an illustration on the horizon.
- The astronaut is NASA's own 3D model of the Extravehicular Mobility Unit spacesuit; Mars, Charon, Saturn and the Earth photo are NASA maps/images (NASA 3D Resources, free of copyright). Ground textures, the comet's shape and the star field are illustrations.

## Sources

1. https://www.topendsports.com/testing/norms/vertical-jump.htm
2. https://marathonhandbook.com/average-vertical-jump/
3. https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html
4. https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html
5. https://official.nba.com/rule-no-1-court-dimensions-equipment
6. https://en.wikipedia.org/wiki/Basket_(basketball)
7. https://nssdc.gsfc.nasa.gov/planetary/factsheet/plutofact.html
8. https://www.britannica.com/animal/giraffe
9. https://www.livescience.com/27336-giraffes.html
10. https://en.wikipedia.org/wiki/Enceladus
11. https://www.planetary.org/worlds/enceladus
12. https://en.wikipedia.org/wiki/Phobos_(moon)
13. https://science.nasa.gov/mars/moons/facts
14. https://behindtheblack.com/behind-the-black/points-of-information/escape-velocity-on-phobos-changes-a-lot-depending-on-location
15. https://foss-astro.blogspot.com/2018/11/anything-faster-than-brisk-walk-on-this.html
16. https://astronomy.com/science/what-does-it-take-to-walk-off-another-world
17. https://www.skyscrapercenter.com/building/burj-khalifa/3
18. https://www.ingenieur.de/technik/fachbereiche/architektur/828-meter-reichen-noch-fuer-platz-1-das-sind-die-hoechsten-gebaeude-der-welt/
19. https://en.wikipedia.org/wiki/67P/Churyumov%E2%80%93Gerasimenko
20. https://sci.esa.int/rosetta/54470-landing-on-a-comet
21. https://www.scienceinschool.org/article/2016/teaching-rosetta-and-philae/
