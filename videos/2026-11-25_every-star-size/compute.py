import math
RSUN=695700.0   # km, NASA NSSDC
RE=6371.0       # km mean Earth radius (NASA)
C=299792.458    # km/s exact
JET=900.0       # km/h, typical airliner cruise (~Mach 0.85)
AU=149597870.7  # km (IAU)
stars={'Sun':1,'Sirius A':1.7,'Arcturus':25,'Aldebaran':44,'Rigel':75,'Antares':700,'Betelgeuse':750,'VY Canis Majoris':1420,'biggest low':1500,'biggest high':2000,'R136a1 low':35,'R136a1 high':40}
print(f"Sun/Earth width ratio: {RSUN/RE:.1f}; volume ratio {(RSUN/RE)**3:,.0f}")
for n,r in stars.items():
    R=r*RSUN; circ=2*math.pi*R
    print(f"{n:18s} R={r:6g} Rsun  vol={r**3:,.0f} Suns  radius={R/AU:.2f} AU  light-around={circ/C:,.0f} s ({circ/C/3600:.2f} h)  jet-around={circ/JET/24:,.0f} d ({circ/JET/24/365.25:,.1f} yr)  Earths-across={2*R/(2*RE):,.0f}")
# Betelgeuse mean density (Joyce 2020: 16.5-19 Msun, 764 (+116/-62) Rsun)
MSUN=1.989e33; rho_sun=MSUN/(4/3*math.pi*(RSUN*1e5)**3)
print(f"Sun mean density {rho_sun:.3f} g/cm3")
for M in (16.5,19):
  for r in (702,764,880):
    rho=M*MSUN/(4/3*math.pi*(r*RSUN*1e5)**3)
    print(f"Betelgeuse M={M} R={r}: mean density {rho:.2e} g/cm3 = air(1.2e-3)/ {1.225e-3/rho:,.0f}")
print("Jupiter orbit 5.20 AU, Saturn 9.54 AU; VY CMa radius AU:", 1420*RSUN/AU, "range", 1300*RSUN/AU, 1540*RSUN/AU)
print("Betelgeuse vs Sun width", 750, "; VY/Betelgeuse", 1420/750)
print("R136a1 vs Aldebaran width", 35/44, 40/44)
