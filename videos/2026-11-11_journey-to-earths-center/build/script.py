SCENES = [
 ("intro", "Intro: 6,370 km to the center", [
  "Right now, about six thousand three hundred seventy kilometers below your feet, is the center of the Earth.",
  "Nobody has ever been there. Nobody has even come close.",
  "So how far down have we actually gone? And what's waiting the rest of the way?",
  "Let's take the trip."]),
 ("kola", "The deepest hole ever drilled", [
  "In nineteen seventy, scientists started drilling a hole called the Kola Superdeep Borehole.",
  "They kept going for nineteen years.",
  "By nineteen eighty-nine, it reached twelve thousand two hundred sixty-two meters. More than twelve kilometers straight down.",
  "It is still the deepest hole humans have ever drilled.",
  "Twelve kilometers sounds enormous. But compared to the whole trip, it's almost nothing."]),
 ("scale", "How far is that, really?", [
  "Divide twelve kilometers by six thousand three hundred seventy, and Kola got about zero point one nine percent of the way to the center.",
  "Shrink the Earth into a globe one meter wide, and the deepest hole in history would be about one millimeter deep.",
  "More than ninety-nine point eight percent of the way down, no drill has ever reached."]),
 ("crust", "Layer 1: The crust", [
  "Kola never even left the first layer: the crust, Earth's thin outer skin.",
  "Under the oceans, the crust is only about five to six kilometers thick.",
  "Under the continents, it's about thirty to forty kilometers.",
  "Kola was drilled into a continent, so it only made it part of the way through."]),
 ("mantle", "Layer 2: The mantle", [
  "Below the crust is the mantle: hot rock that goes all the way down to about two thousand nine hundred kilometers.",
  "That's almost halfway to the center.",
  "The mantle is the biggest layer by far. More than eighty percent of Earth's volume."]),
 ("outer", "Layer 3: The liquid outer core", [
  "At about two thousand nine hundred kilometers down, the rock ends, and we hit a sea of liquid metal.",
  "The outer core is molten iron and nickel, about two thousand two hundred kilometers thick.",
  "And it's always moving. As that liquid metal swirls, it creates Earth's magnetic field."]),
 ("inner", "Layer 4: The solid inner core", [
  "About five thousand one hundred kilometers down, we reach the inner core: a ball of metal with a radius of more than twelve hundred kilometers.",
  "It's about five to six thousand degrees Celsius. Roughly as hot as the surface of the Sun.",
  "At that temperature, you might expect it to be liquid too.",
  "But the pressure here is more than three million times the air pressure at sea level.",
  "That pressure squeezes the inner core into a solid."]),
 ("fall", "What if you fell through the Earth?", [
  "So what if you could skip the drilling?",
  "Imagine a tunnel straight through the planet, with no air and no heat to worry about. Jump in, and gravity does the rest.",
  "If Earth had the same density all the way through, the fall to the other side would take about forty-two minutes.",
  "But Earth isn't the same all the way through. Using its real, measured density, a physicist found the fall takes only about thirty-eight minutes.",
  "Under forty minutes, from one side of the planet to the other."]),
 ("walk", "How long to walk there?", [
  "Or you could walk.",
  "At a brisk five kilometers per hour, nonstop, with no sleep, it would take about fifty-three days just to reach the center."]),
 ("outro", "The 99.8% we've never seen", [
  "So here's the real scale of it.",
  "Nineteen years of drilling got us about zero point one nine percent of the way down.",
  "Everything else, the mantle, the ocean of liquid metal, a solid core as hot as the Sun's surface, no one has ever seen with their own eyes.",
  "If this blew your mind, subscribe to Explorer Man for more science you can feel the scale of."]),
]
# on-screen caption versions (digits) — same words, numerals for readability
CAP = {
 "about six thousand three hundred seventy kilometers": "about 6,370 kilometers",
 "nineteen seventy": "1970", "nineteen years": "19 years", "nineteen eighty-nine": "1989",
 "twelve thousand two hundred sixty-two meters": "12,262 meters", "twelve kilometers": "12 kilometers",
 "Twelve kilometers": "12 kilometers", "six thousand three hundred seventy": "6,370",
 "zero point one nine percent": "0.19%", "one meter": "1 meter", "one millimeter": "1 millimeter",
 "ninety-nine point eight percent": "99.8%", "five to six kilometers": "5 to 6 kilometers",
 "thirty to forty kilometers": "30 to 40 kilometers", "two thousand nine hundred kilometers": "2,900 kilometers",
 "eighty percent": "80%", "two thousand two hundred kilometers": "2,200 kilometers",
 "five thousand one hundred kilometers": "5,100 kilometers", "twelve hundred kilometers": "1,200 kilometers",
 "five to six thousand degrees Celsius": "5,000 to 6,000 °C", "three million": "3 million",
 "forty-two minutes": "42 minutes", "thirty-eight minutes": "38 minutes", "forty minutes": "40 minutes",
 "five kilometers per hour": "5 km/h", "fifty-three days": "53 days", "Nineteen years": "19 years",
}
def caption(s):
    for k in sorted(CAP, key=len, reverse=True):
        s = s.replace(k, CAP[k])
    return s
