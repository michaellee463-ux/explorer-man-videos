# Fact sheet — "This Volcano Is 2.5× Taller Than Everest… You Might Not Even Notice It" (Short, 2026-11-24)

**Using the data:** Studio analytics are still blocked (vidIQ is signed in with only the MoneyScope channel), so this run used public vidIQ counts (Nov 24). Starship catch is still the best at 2,587 views. Grain of sand has 2,414 views and 193 likes (8%). Mars–Jupiter has 2,390 views and 338 likes (14%), and Sugar cube has 2,064. Jupiter What If is at 1,502 after 2 days, slowing to about 31 views/hour. The music-only jump Short is stuck at 512. Space and "you vs. something huge" with an extreme number in frame 0 still win, and the visual scale comparisons get the most likes. So today: a space scale comparison (Olympus Mons vs Everest) with "2.5× EVEREST" big in frame 0, plus a statement hook built on a paradox. The last Short used a cliffhanger, so this one alternates. Niche demand is proven: Olympus Mons vs Everest Shorts reached 751K, 706K, 531K and 124K views (vidIQ outliers, Nov 24).

## Topic shortlist (score /10: curiosity, 2-second hook, proven demand, visual payoff, fit → avg)
| Candidate | Cur | Hook | Demand | Visual | Fit | Avg | Note |
|---|---|---|---|---|---|---|---|
| **Olympus Mons: 2.5× Everest, yet you might not notice you're on it** | 9 | 9 | 9 | 9 | 10 | **9.2** | 4 niche outliers 124K–751K (one this week); paradox hook; fully verifiable (NASA/ESA) |
| How many Earths fit inside each planet | 8 | 9 | 10 | 8 | 9 | 8.8 | 1.4M outlier this week, but it overlaps "How Big Is the Sun" and Jupiter (11 Earths wide), so too close to a repeat |
| Earth vs the largest star | 8 | 8 | 9 | 8 | 9 | 8.4 | too close to What If Betelgeuse |
| Krakatoa: the loudest sound ever | 9 | 8 | 8 | 7 | 8 | 8.0 | Earth field, keep for later |
| Thanksgiving science (turkey/food numbers) | 5 | 6 | 6 | 5 | 5 | 5.4 | weak fit |
Pick: Olympus Mons. No-repeat check: no earlier video is about volcanoes, Olympus Mons or mountains on other worlds. I checked posted.md, videos/ and thumbnails/. Mars appeared only in the Mars–Jupiter conjunction Short. It's a one-off, and the hook is a statement, not a cliffhanger (the last Short was a cliffhanger).

## Claims (each with ≥2 independent sources)
1. **The biggest volcano in the solar system.** NASA Photojournal PIA00300 ("the largest known volcano in the Solar System"); Britannica ("the largest known volcano in the solar system"); Space.com; Astronomy.com; BBC Sky at Night; ESA 2013. (I don't say "tallest mountain", because Olympus Mons is roughly tied with Rheasilvia on Vesta.)
2. **About 22 km high.** ESA Mars Express 2004 ("average elevation of 22 km"); ESA 2013 ("towers some 22 km above the surrounding plains"); Britannica ("central edifice 22 km high"). Other sources give 21.3 km (above the Mars datum, Wikipedia and Sky at Night) up to 25–27 km (above lower plains, Space.com, NASA), so "about 22" is the middle figure.
3. **About 2.5 times as tall as Everest.** Everest is 8,848.86 m (2020 China–Nepal survey: Kathmandu Post, NPR). compute.py: 22 ÷ 8.85 = 2.49 (2.41 using 21.3 km, 2.8–2.9 using 25–26 km). Wikipedia: "about 2.5 times the elevation of Mount Everest"; JPL: "more than twice as tall". Some sources say about 3× (Space.com, Astronomy.com) because they measure from lower plains, so 2.5× is the conservative figure.
4. **About twice as high as most passenger jets fly.** Typical airliner cruise is about 35,000 ft (Time; Military & Aerospace Electronics "Why commercial aircraft cruise around 35,000 feet"; Stanford Widescope). compute.py: 35,000 ft = 10.7 km; 22 ÷ 10.7 = 2.06×. The on-screen label "PASSENGER JETS ≈ 11 KM" rounds 10.7 km.
5. **About 600 km across.** Wikipedia ("about 600 km wide"); NASA PIA00300 ("over 600 kilometers at the base"); Astronomy.com (600 km); Space.com (601 km).
6. **Roughly the size of Arizona.** Space.com ("roughly the size of the state of Arizona", with an Arizona outline overlay); Astronomy.com ("it would cover the entire state of Arizona"). compute.py: a 600 km circle covers 282,743 km² vs Arizona's ~295,000 km² (ratio 0.96). The on-screen Arizona outline is drawn from real border coordinates at the same scale (its polygon area is 293,976 km²).
7. **Over twenty times wider than it is tall.** compute.py: 600 km ÷ 21.3–26 km = 23–28. On screen: "TRUE SCALE" profile drawn 1,000 px wide × 37 px tall (600 × 22 km), with Everest to the same scale.
8. **A ring of cliffs kilometers high wraps around its edge.** ESA 2013 ("in places reaching 9 km high"; "the scarp circles the entire volcano"); NASA PIA00300 ("scarp that is up to 6 km high"); Wikipedia ("up to 8 km"); Britannica ("as high as 10 km"). Because the figures differ, the narration says only "kilometers high".
9. **A summit crater (caldera) about 80 km wide and about 3 km deep.** Wikipedia (60 × 80 km, up to 3.2 km deep); Space.com and Britannica (85 km); ESA 2004, NASA and HyperPhysics (about 3 km deep).
10. **Why so huge: on Earth, plates drift over hot spots and make chains like Hawaii; Mars's crust stays put, so lava piled up in one place, and weaker gravity let it grow taller.** NASA JPL "Mars in a Minute" ("Mars doesn't have tectonic plates that move over hotspots, like in Hawaii… instead of getting a chain of volcanoes, you could keep building one huge one… With the lower gravity on Mars, that magma could be pushed to great heights"); Space.com ("Both the hot spot and the crust remain unmoving"; "lower surface gravity… allowed for the lava on Mars to pile up higher"); Sky at Night; Wikipedia.
11. **Near the top it just looks like a gentle slope; the slope runs past your horizon, only about 3 km away.** Space.com ("If you were standing on it, it would simply appear to be a gently sloping plain"); Wikipedia ("an observer near the summit would be unaware of standing on a very high mountain, as the slope of the volcano would extend far beyond the horizon, a mere 3 kilometers away"). The average slope is only 5% (Wikipedia, Space.com); compute.py: 2.9°. Horizon distance, computed with Mars radius 3,389.5 km (NASA fact sheet) and d = √(2Rh): 3.2–3.5 km for eye heights of 1.5–1.8 m, so "about three kilometers".
12. **Hook "if you stood on it, you might not even notice."** This rests on claim 11. It says "might" because near the edge cliffs you would notice.

## Sources
- https://science.nasa.gov/mars/resources/22617/olympus-mons/ (NASA Photojournal PIA00300)
- https://www.jpl.nasa.gov/videos/mars-in-a-minute-how-did-mars-get-such-enormous-mountains/
- https://www.esa.int/Science_Exploration/Space_Science/Mars_Express/Olympus_Mons_-_the_caldera_in_close-up
- https://www.esa.int/Our_Activities/Space_Science/Mars_Express/At_the_foot_of_the_Red_Planet_s_giant_volcano
- https://www.britannica.com/place/Olympus-Mons
- https://space.com/20133-olympus-mons-giant-mountain-of-mars.html
- https://www.astronomy.com/science/olympus-mons-mars-mega-volcano-height-formation/
- https://skyatnightmagazine.com/space-science/olympus-mons
- https://hyperphysics.gsu.edu/hbase/solar/marsoly.html
- https://en.wikipedia.org/wiki/Olympus_Mons
- https://kathmandupost.com/national/2020/12/08/it-s-official-mount-everest-is-8-848-86-metres-tall
- https://www.npr.org/2020/12/08/944152693/everest-gets-a-growth-spurt-as-china-nepal-revise-official-elevation-upward
- https://time.com/5309905/how-high-do-planes-fly/
- https://www.militaryaerospace.com/commercial-aerospace/article/55399427/why-commercial-aircraft-cruise-around-35000-feet
- https://widescope.stanford.edu/how-high-do-aeroplanes-fly
- https://www.britannica.com/place/Arizona-state (area ~295,000 km² / 113,990 sq mi)
- https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html (Mars radius)

Script and output: compute.py / compute_output.txt.
