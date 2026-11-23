# Derived figures for the Andromeda Short (2026-11-23)
moon_deg = 0.5           # LCO: ~31 arcmin ~ 1/2 deg; UO: 30 arcmin
moon_arcmin = (30, 31)
m31_arcmin = {"freestarcharts 3.0x1.0 deg": 180, "freestarcharts table": 189, "wikibooks": 190}
for k, v in m31_arcmin.items():
    print(f"M31 width {v}' ({k}) / Moon 30-31' = {v/31:.2f}-{v/30:.2f} Moons")
mph = 250_000
kmh = mph * 1.609344
print(f"250,000 mph = {kmh:,.0f} km/h = {kmh/3600:.1f} km/s")
print(f"100-140 km/s = {100*3600/1.609344:,.0f}-{140*3600/1.609344:,.0f} mph")
d_ly = 2.5e6
print(f"Light left {d_ly:,.0f} years ago; Homo sapiens ~300,000 yr -> light is {d_ly/3e5:.1f}x older; species appeared {d_ly-3e5:,.0f} years after it left")
# miles per hour -> distance per video second
print(f"distance Andromeda closes per second: {mph/3600:.1f} miles ({kmh/3600:.0f} km)")
# visual scale in the video: Moon 120 px wide -> galaxy 6x = 720 px along the long axis, 1/3 that on the short axis
moon_px = 140
print("visual: moon", moon_px, "px ; galaxy", 180/30*moon_px, "x", 60/30*moon_px, "px (3.0 x 1.0 deg vs 0.5 deg)")
