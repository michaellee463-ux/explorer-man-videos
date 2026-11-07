# Derived figures for "How long to DRIVE to the Sun?"
V = 100.0                       # km/h, chosen car speed
MI = 1.609344                   # km per mile (exact)
YEAR_H = 365.25 * 24            # hours in a Julian year
MOON = 384_400                  # km, mean Earth-Moon distance (NASA NSSDC, Britannica)
SUN = 149_597_870.7             # km, 1 au (IAU 2012 via Britannica; NASA NSSDC 149.6e6 mean)
LY = 9.4607e12                  # km per light-year (Britannica 9.46073e12; NASA ~9.5e12)
C = 299_792.458                 # km/s (exact SI)
print(f"100 km/h in mph: {V/MI:.2f}")
h = MOON / V; print(f"Moon: {h:.0f} h = {h/24:.1f} days = {h/24/30.4375:.2f} months")
h = SUN / V; print(f"Sun: {h:.0f} h = {h/YEAR_H:.1f} years; arrive year if leaving Nov 2026: {2026 + 10.2/12 + h/YEAR_H:.1f}")
h = 149.6e6 / V; print(f"Sun (NSSDC 149.6e6 km): {h/YEAR_H:.1f} years")
t = SUN / C; print(f"Sunlight time: {t:.1f} s = {int(t//60)} min {t%60:.1f} s")
for ly in (4.2, 4.23, 4.24):
    km = ly * LY; h = km / V
    print(f"Proxima at {ly} ly: {km:.3e} km = {km/1e12:.1f} trillion km; drive {h/YEAR_H/1e6:.2f} million years")
