# Independent fact-check: "How Fast Are You Moving RIGHT NOW?"

Checked 2026-11-17. Inputs: the video (69 frames sampled at 1 fps plus full-res frames at 13, 37, 40, 58, 59, 60, 65 and 69.3 s), thumbnail.jpg, narration.txt, phonemes.txt, build/lines.json and copy.md. I did not open facts.md, compute.py or anything else in build/.

## Technical
| Item | Result | Notes |
|---|---|---|
| Duration | CORRECT | ffprobe gives 69.38 s, inside 61-75 s. 1080x1920, 30 fps |
| Frame 0 / 1.0 s | CORRECT | "HOW FAST ARE YOU MOVING RIGHT NOW?" is large with a "???" km/h gauge. No black or empty frame |
| Thumbnail | CORRECT | "YOU'RE NOT SITTING STILL / 1.3M km/h / RIGHT NOW" matches the reveal |

## Numbers and claims
| # | Claim (where) | Result | Check / source |
|---|---|---|---|
| 1 | Equator spin about 1,670 km/h, ≈1,040 mph (narration, screen, description) | CORRECT | 465.1 m/s × 3.6 = 1,674 km/h; 1,670/1.609 = 1,038 mph. https://www.britannica.com/story/what-is-earths-velocity , https://www.spacecentre.nz/resources/faq/solar-system/earth/rotation-speed.html |
| 2 | Jet airliner about 900 km/h; spin is "almost 2×" | CORRECT | 1,670/900 = 1.86. Typical cruise is 880-930 km/h. https://pilotinstitute.com/how-fast-do-airplanes-fly/ |
| 3 | Bar chart jet vs spin, "bars to scale" | CORRECT | Measured 459 px vs 860 px = 0.534. Expected 900/1,670 = 0.539 |
| 4 | Orbit about 107,000 km/h, ≈67,000 mph | CORRECT | 29.78 km/s × 3600 = 107,208 km/h = 66,600 mph. 67,000 mph is the standard NASA/Britannica figure. https://www.britannica.com/story/what-is-earths-velocity |
| 5 | Moon in under 4 hours (384,400 km ÷ 107,000 km/h ≈ 3.6 h) | CORRECT | 3.59 h. Still 3.79 h at apogee (405,500 km) |
| 6 | Sun around galaxy about 828,000 km/h, ≈514,000 mph | CORRECT | 230 km/s × 3600 = 828,000 km/h = 514,500 mph. Source range is about 220-250 km/s. https://www.britannica.com/story/what-is-earths-velocity , https://en.wikipedia.org/wiki/Galactic_year |
| 7 | One lap over 200 million years; on screen "~225 million years" | CORRECT | Published values are about 225-250 Myr. My own check: 26,000 ly at 230 km/s ≈ 213 Myr. https://en.wikipedia.org/wiki/Galactic_year |
| 8 | "All the dinosaurs 164 million (230 to 66 million years ago)"; "came and went in less than one lap" | CORRECT | 230 − 66 = 164. 164 < 213-250 Myr. Extinction 66 Ma: https://www.usgs.gov/faqs/when-did-dinosaurs-become-extinct . Optional pedantic note: birds are technically dinosaurs, so this means non-avian dinosaurs. That is normal popular usage and fine as it stands |
| 9 | Dinosaur bars "to scale" | CORRECT | Measured 628 px vs 861 px = 0.729. Expected 164/225 = 0.729 |
| 10 | Speed relative to the CMB about 1.3 million km/h, ≈830,000 mph, "about 370 km every second" | CORRECT | Planck 2018: 369.82 ± 0.11 km/s = 1,331,000 km/h = 827,000 mph. https://arxiv.org/pdf/1807.06205 , https://www.aanda.org/articles/aa/full_html/2020/09/aa33880-18/T3.html . Minor note: 1.3 M km/h on its own converts to 808k mph. 830k mph is the true value (1.33 M km/h), so both numbers are within normal rounding. Earth's orbit moves this value by about ±30 km/s over the year, so "about" is appropriate |
| 11 | Live counter "370 km per second" | CORRECT | Values read from frames match 370 × t: t = 59.0 s shows 21,819 (370 × 58.97); 60.0 s shows 22,189 (59.97 s); 65.0 s shows 24,038 (64.97 s). The roughly 33 ms offset is the frame seek. The counter starts at video start |
| 12 | Narration: "Since this video started, you've traveled more than twenty thousand kilometers" | CORRECT | The share line starts at about 58.3 s (audio pause from 57.9 to 58.5 s). By the time it is spoken (59-60 s), 370 km/s × 59 s = 21,800 km. It stays true even at the yearly minimum (about 340 km/s × 60 s = 20,400 km) |
| 13 | "Orbit and Earth–Moon scenes not to scale; bar charts to scale" (description) | CORRECT | Matches the on-screen labels |
| 14 | "The light that fills the whole universe (cosmic microwave background)" = afterglow of the Big Bang | CORRECT | Standard description |

## Framing and honesty
- **Hook answered truthfully: CORRECT.** The video gives the spin, orbit and galactic speeds. It then says plainly that "these motions point in different directions, so they don't simply add up" (on screen: "THEY DON'T JUST ADD UP" with arrows pointing different ways). The final figure is framed as relative to a reference ("measure us against the afterglow of the Big Bang"). Nothing implies that the speeds add together.
- **"That's not even close to the real answer": acceptable.** It is a rhetorical tease, and the "real answer" is then given with its reference frame.
- **"Why don't you feel it? Because the speed is steady": CORRECT.** This is the standard simplification. The accelerations involved are tiny.
- **Share line "Send this to someone who thinks they're sitting still": honest.** The video establishes that you are moving relative to Earth's axis, the Sun, the galaxy and the CMB.
- **Comment question "Too low... or way too low?" and pinned comment: honest.** This is engagement framing, not a factual claim. 1.3 M km/h is far above most people's guesses.
- **Title, description, tags and TikTok caption:** all numbers match the video and the sources above.

## Narration / phonemes
All 13 lines were checked in phonemes.txt. There are no mispronunciations, no letters read as "uh" and no odd numbers. All numbers are spelled out and voiced correctly: "sixteen hundred and seventy", "a hundred and seven thousand", "eight hundred and twenty-eight thousand", "one point three million", "twenty thousand". "equator" is /ɪkwˈeɪɾɚ/, "universe" is /jˈuːnɪvˌɜːs/, "directions" is /dᵻɹˈɛkʃənz/, and "dinosaurs" is /dˈaɪnəsˌɔːɹz/. All are fine. Phrasing is natural.

## Optional polish (not required)
- You could write "≈1.33 million km/h" in the description so viewers who convert 1.3 M km/h to mph do not wonder why it says 830k and not 808k. Not wrong as it stands.

VERDICT: PASS
Required fixes: none.
