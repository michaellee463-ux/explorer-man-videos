# All derived figures for the Earth-as-a-black-hole Short
G=6.67430e-11; c=299792458.0; Msun=1.98847e30   # CODATA 2018 / IAU nominal
AU=1.495978707e11
def rs(M): return 2*G*M/c**2
Mearth=5.9722e24   # NASA Earth fact sheet
print(f"Earth mass = {Mearth/1e3:.3e} tonnes (= {Mearth/1e3/1e21:.2f} sextillion tonnes)")
re=rs(Mearth); print(f"Earth Schwarzschild radius = {re*1000:.2f} mm, diameter = {2*re*100:.2f} cm")
rsun=rs(Msun); print(f"Sun Schwarzschild radius = {rsun/1000:.2f} km, diameter = {2*rsun/1000:.2f} km")
print(f"Walk across Sun-BH at 5 km/h = {2*rsun/1000/5:.2f} h")
print(f"Sun real diameter 1,392,700 km -> shrink factor {1392700/(2*rsun/1000):,.0f}x")
sgr=4.297e6*Msun; rg=rs(sgr); merc=57.909e9
print(f"Sgr A* (4.297e6 Msun) Rs = {rg/1e9:.2f} million km = {rg/AU:.3f} AU; Mercury orbit radius 57.9 million km; ratio {rg/merc:.3f}")
m87=6.5e9*Msun; rm=rs(m87); nep=30.07*AU
print(f"M87* (6.5e9 Msun) Rs = {rm/1e12:.2f} billion km = {rm/AU:.1f} AU; diameter = {2*rm/1e12:.1f} billion km")
print(f"M87* radius / Neptune orbit radius (30.07 AU) = {rm/nep:.2f}; Pluto aphelion 49.3 AU ratio {rm/(49.3*AU):.2f}")
t=2*rm/c; print(f"Light time across M87* diameter = {t/3600:.1f} h = {t/86400:.2f} days")
print(f"M87* mass range 5.8-7.2e9: Rs {rs(5.8e9*Msun)/AU:.0f}-{rs(7.2e9*Msun)/AU:.0f} AU -> ratio vs Neptune {rs(5.8e9*Msun)/nep:.2f}-{rs(7.2e9*Msun)/nep:.2f}")
print(f"Escape speed: Earth 11.19 km/s vs light {c/1000:,.0f} km/s ({c/11186:,.0f}x)")
