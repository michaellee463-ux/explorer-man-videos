# Derived figures for "Journey to the Center of the Earth" (long-form, 2026-11-11)
R_center_km = 6370          # Britannica "some 6,370 km"; USGS diameter ~12,750 km -> 6,375
usgs_diam = 12750
kola_m = 12262              # Wikipedia, WorldAtlas
start, reached = 1970, 1989
print("USGS radius from diameter:", usgs_diam/2, "km")
print("Years drilling to reach max depth:", reached - start)
frac = kola_m/1000 / R_center_km
print(f"Kola fraction of way to centre: {frac*100:.3f} %  (with 6,375 km: {kola_m/1000/6375*100:.3f} %)")
print(f"Unexplored remainder: {100-frac*100:.2f} %")
globe_mm = 1000 * (kola_m/1000)/(2*R_center_km)   # 1 m wide globe
print(f"On a globe 1 m wide, Kola depth = {globe_mm:.2f} mm")
# layers (depths from surface)
mantle_bottom = 2900; outer_core_thick = 2200
print("Outer core bottom depth (USGS 2900+2200):", mantle_bottom+outer_core_thick, "km (Britannica: ~5,100 km)")
print("Inner core radius from depths: ", R_center_km-(mantle_bottom+outer_core_thick), "km (Space.com 1,221; USGS 1,250)")
print(f"Mantle base as fraction of the way to centre: {mantle_bottom/R_center_km*100:.1f} %")
print(f"Kola vs thinnest crust (5 km oceanic): {kola_m/1000/5:.2f}x ; vs 30-40 km continental: {kola_m/1000/30*100:.0f}% - {kola_m/1000/40*100:.0f}%")
# drawing scale checks: cross-section radius in px
for Rpx in (420, 470):
    print(f"Cross-section R={Rpx}px: mantle base r={Rpx*(1-2900/6370):.0f}px, inner core r={Rpx*1270/6370:.0f}px, Kola depth={Rpx*kola_m/1000/6370:.2f}px, crust 35km={Rpx*35/6370:.2f}px")
# walking
speed = 5.0  # km/h, assumed brisk walking pace, stated on screen
hours = R_center_km/speed
print(f"Walk to centre at {speed} km/h nonstop: {hours:.0f} h = {hours/24:.1f} days")
# falling: Klotz 2015 38 min (realistic), 42 min uniform. Check uniform value from physics:
import math
G=6.674e-11; M=5.972e24; R=6.371e6
rho_uniform_T = math.pi*math.sqrt(R**3/(G*M))
print(f"Uniform-density half-period (fall end to end): {rho_uniform_T/60:.1f} min ; to centre {rho_uniform_T/120:.1f} min")
print(f"Pressure: 3.3–3.6 million atm -> 'more than 3 million times sea-level air pressure' OK")
print(f"Temperature: 5,200 C (Space.com) – 6,000 C (LiveScience) -> 'about 5,000-6,000 C' OK")
