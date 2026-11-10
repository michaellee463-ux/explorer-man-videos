# Fact sheet: Voyager 1 reaches one light-day from Earth (Short, made 2026-11-10)

Every number in the narration, captions, on-screen text and thumbnail. Derived figures were computed in Python (`voy_facts.py`, output in `voy_facts.json`), not by hand.

| # | Claim in the video | Checked value | Sources |
|---|---|---|---|
| 1 | "Flying for 49 years" / "Launched Sept 5, 1977" | Launch Sept 5, 1977. To Nov 18, 2026 = 17,971 days = 49.2 years | NASA [1], EarthSky [4] |
| 2 | "61,000 km/h" / "38,000 mph" / "17 km every second" | NASA: "nearly 38,000 mph (61,000 kph)". 61,000 km/h = 16.9 km/s; 38,000 mph = 61,155 km/h | NASA [1], NASA JPL release [2] |
| 3 | "Light from Earth reaches the Moon in just over a second" (1.3 seconds) | 384,400 km / 299,792.458 km/s = 1.28 s | NASA [1] (1.3 s) + computed |
| 4 | "The Sun, in eight minutes" | 1 AU / c = 499.0 s = 8 min 19 s | NASA [1] ("about eight minutes and 20 seconds") + computed |
| 5 | "Neptune, in four hours" | From Earth on Nov 18, 2026: 29.29 AU = 4 h 04 min. From the Sun (30.07 AU): 4 h 10 min | NASA [1] ("four light-hours and 10 light-minutes") + computed |
| 6 | "And Voyager? One full day" / "24 hours" / "1 LIGHT-DAY" | One light-day = c x 86,400 s = 25,902,068,371 km = 173.14 AU | NASA [1], EarthSky [4] + computed |
| 7 | "On November 18 it becomes the first human-made object to reach one light-day from Earth" / "NOV 18, 2026" | NASA: Wednesday, Nov. 18, 2026, 5:16:07 a.m. EST; "reached by no other human-made object" | NASA [1], NASA JPL release [2], NASA Night Sky Notes [3], EarthSky [4] |
| 8 | "25.9 BILLION KM · 16.1 BILLION MILES" and the odometer ending at 25,902,068,371 km | 25.902 billion km = 16.09 billion miles | NASA [1] (16,094,799,096 mi / 25,902,068,356 km), [2] + computed |
| 9 | "Send it a command on Monday. It arrives Tuesday. The reply comes back Wednesday." / "24 hours", "48 hours" | 24 h each way, 48 h round trip | NASA JPL release [2] |
| 10 | Map label "2012: entered interstellar space" (drawn 121 AU from the Sun) | Crossed the heliopause on or about Aug 25, 2012, 121 AU from the Sun | NASA [1], [3], Nature [5] |
| 11 | "Proxima Centauri, the nearest star" / "4.2 years" of light travel | 4.2465 light-years (NASA rounds to 4.24) | NASA [1], Universe Today [6] |
| 12 | "At that speed, the nearest star is about 75,000 years away" / "75,000 YEARS" | 4.2465 ly at 61,000 km/h = 75,100 years (74,900 at 17.0 km/s). Universe Today gets 76,000 years using 60,000 km/h | computed + Universe Today [6] |
| 13 | "49 years of flight = 0.06% of this distance" | 1 light-day / 4.2465 ly = 1 / 1,551 = 0.064% | computed |
| 14 | Thumbnail: "49 YEARS = 1 DAY AT LIGHT SPEED" | Same as rows 1 and 6 | NASA [1] |
| 15 | Map: "EARTH + SUN + ALL 8 PLANETS" inside the small circles | Neptune's orbit (30 AU) is 17% of one light-day (173 AU) | computed |

## Notes
- The video says "it becomes" with the date, so the wording stays true before and after Nov 18, 2026.
- An older estimate (Popular Science, Nov 2025 [7]) gave Nov 15, 2026. NASA's current page (updated Nov 5, 2026) says Nov 18, so the video uses Nov 18.
- Voyager 1 is not flying toward Proxima Centauri. The video only compares the distance ("at that speed"), and the map draws the star about 81 degrees away from Voyager's direction, which is the real angle between them.
- Map geometry for Nov 18, 2026 comes from JPL's approximate planetary elements. Check: they reproduce the 2026 oppositions of Saturn (Oct 5), Neptune (Sep 26) and Uranus (Nov 26) to within a day.
- Planet, Sun and Moon dots on the map are drawn larger than scale so they can be seen; distances are to scale.
- NASA lost contact with Voyager 1 for about two days on Oct 18-20, 2026 and then recovered it [2]. The video does not mention this.

## Sources
1. NASA Science, "Voyager 1: What Is a Light-Day" (updated Nov 5, 2026): https://science.nasa.gov/mission/voyager/voyager-1/voyager-1-what-is-a-light-day/
2. NASA JPL release via ScienceDaily (Nov 3, 2026): https://www.sciencedaily.com/releases/2026/11/261103003152.htm
3. NASA Night Sky Notes, "Light-Day Away" (Oct 30, 2026): https://science.nasa.gov/solar-system/skywatching/night-sky-network/novembers-night-sky-notes-light-day-away/
4. EarthSky, "Voyager 1 to reach 1 light-day from Earth on November 18": https://earthsky.org/space/voyager-1-1-light-day-from-earth-november-17-18-2026/
5. Nature, "Voyager 1 has reached interstellar space" (2013): https://www.nature.com/news/voyager-1-has-reached-interstellar-space-1.13735
6. Universe Today, "How Long Would It Take To Travel To The Nearest Star?": https://universetoday.com/15403/how-long-would-it-take-to-travel-to-the-nearest-star
7. Popular Science, "Voyager 1 is almost one light-day from Earth" (Nov 2025): https://popsci.com/science/voyager-one-light-day-earth
