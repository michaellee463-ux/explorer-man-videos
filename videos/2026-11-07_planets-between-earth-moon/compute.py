# All derived figures for "Every planet fits between Earth and the Moon" (NASA NSSDC fact sheets)
D = dict(Mercury=4879, Venus=12104, Mars=6792, Jupiter=142984, Saturn=120536, Uranus=51118, Neptune=49528)  # equatorial diameter, km
R_earth, R_moon = 6371.0, 1737.4      # volumetric mean radius, km
d_mean, d_apo, d_peri = 384400, 405500, 363300  # km centre-to-centre (semimajor axis, mean apogee, mean perigee)
c = 299792.458  # km/s (exact, NIST)
S = sum(D.values())
print("sum of 7 planet diameters km:", S)
for name, d in (("mean", d_mean), ("apogee", d_apo), ("perigee", d_peri)):
    gap = d - R_earth - R_moon
    print(f"{name}: centre {d} km, surface gap {gap:.0f} km, gap - planets = {gap - S:+.0f} km")
print("Earths across mean distance (centre):", d_mean / 12756)
print("Earths across mean surface gap:", (d_mean - R_earth - R_moon) / 12756)
print("Jupiter share of planet line %:", 100 * D["Jupiter"] / S)
print("Jupiter+Saturn share %:", 100 * (D["Jupiter"] + D["Saturn"]) / S)
print("Jupiter / Earth diameter:", 142984 / 12756)
print("light time mean distance s:", d_mean / c)
print("mean distance miles:", d_mean / 1.609344, " apogee miles:", d_apo/1.609344, " planets miles:", S/1.609344)
