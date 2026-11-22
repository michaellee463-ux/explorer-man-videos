# Derived figures for You vs #4: space without a suit
armstrong_m = 19202        # US Standard Atmosphere Armstrong limit, 63,000 ft
everest_m = 8849           # Mount Everest (2020 survey)
iss_km_lo, iss_km_avg, iss_km_hi = 370, 400, 420
print("Armstrong limit / Everest =", round(armstrong_m/everest_m, 2))
print("63,000 ft in m =", round(63000*0.3048))
for h in (iss_km_lo, iss_km_avg, iss_km_hi):
    print(f"ISS {h} km / Armstrong = {h*1000/armstrong_m:.1f}x")
print("250 mi in km =", round(250*1.609344))
print("CMB 2.725 K in C =", round(2.725-273.15, 1), "; 2.735 K =", round(2.735-273.15, 1))
print("LeBlanc 120,000 ft in km =", round(120000*0.3048/1000, 1), "=", round(120000*0.3048/armstrong_m, 1), "x Armstrong limit")
print("water vapour pressure at 37C (Buck eq, kPa) =", round(0.61121*2.718281828**((18.678-37/234.5)*(37/(257.14+37))), 2))
print("87 s < 90 s:", 87 < 90)
