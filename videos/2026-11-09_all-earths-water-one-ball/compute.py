import math
V_all=1.386e9      # km^3 USGS/NOAA
V_fresh_liq=10_633_450  # km^3 USGS
V_lr=93_113        # km^3 USGS lakes+rivers
d=lambda V:(6*V/math.pi)**(1/3)
print(f"all-water sphere diameter from volume: {d(V_all):.1f} km (USGS says ~1,385)")
print(f"liquid fresh sphere diameter: {d(V_fresh_liq):.1f} km (USGS 272.8)")
print(f"lakes+rivers sphere diameter: {d(V_lr):.1f} km (USGS 56.2)")
print(f"1,385 km in miles: {1385/1.609344:.0f}")
print(f"56.2 km in miles: {56.2/1.609344:.1f}")
moon_d_nasa=2*1740; moon_d=3474
for m in (moon_d_nasa,moon_d): print(f"water ball / Moon diameter ({m} km): {1385/m:.3f}")
earth_eq=12756
print(f"Earth eq. diameter / water ball: {earth_eq/1385:.2f}")
print(f"Earth / lakes+rivers ball: {earth_eq/56.2:.0f}")
print(f"water ball / lakes ball diameter: {1385/56.2:.1f}; volume ratio {V_all/V_lr:.0f}")
print(f"lakes+rivers share of all water: {V_lr/V_all*100:.4f}% (USGS ~1/150 of 1% = {1/150:.4f}%)")
# drawing scale used in the video
R=400; s=R/(earth_eq/2)
print(f"draw scale {s:.6f} px/km: ball r={1385/2*s:.2f}px moon r={moon_d/2*s:.2f}px lakes r={56.2/2*s:.3f}px")
