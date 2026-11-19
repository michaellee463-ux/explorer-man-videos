# Explorer Man 2026-11-19: "If Earth Were a Grain of Sand" scale model. All derived figures.
from math import radians, sin, cos, asin, sqrt
EARTH_D_KM = 12756          # NASA NSSDC equatorial diameter
GRAIN_MM = 1.0              # coarse sand grain (sand = 0.0625-2 mm, SLB glossary)
k = EARTH_D_KM*1e6 / GRAIN_MM   # real mm per model mm
def model_mm(km): return km*1e6/k
def fmt(mm):
    if mm < 1e-3: return f"{mm*1e6:.3g} nm"
    if mm < 1: return f"{mm*1000:.3g} um"
    if mm < 1000: return f"{mm:.4g} mm"
    if mm < 1e6: return f"{mm/1000:.4g} m"
    return f"{mm/1e6:.4g} km"
LY = 9.46073e12
items = {
 "person 1.5 m": 1.5e-3, "person 1.7 m": 1.7e-3, "person 2.0 m": 2.0e-3,
 "Moon diameter 3,475 km": 3475, "Moon distance 384,400 km": 384400,
 "ISS altitude ~400 km": 400,
 "Artemis II record 406,773 km (planned max) ": 406773, "Artemis II 400,171 km (record-break point)": 400171,
 "Sun diameter 1,392,000 km": 1392000, "Earth-Sun 149.6e6 km": 149.6e6,
 "Jupiter diameter 142,984 km": 142984, "Jupiter from Sun 778.6e6 km": 778.6e6,
 "Neptune diameter 49,528 km": 49528, "Neptune from Sun 4495.1e6 km": 4495.1e6,
 "Voyager 1 one light-day 25,902,068,371 km": 25902068371,
 "Proxima NASA 40,208e9 km": 40.208e12, "Proxima 4.2465 ly": 4.2465*LY, "Proxima 4.2 ly": 4.2*LY,
 "Milky Way 100,000 ly": 1e5*LY,
}
print(f"scale: 1 model mm = {k/1e6:,.0f} real km  (1 : {k:.4e})")
for n,km in items.items(): print(f"{n:45s} -> {fmt(model_mm(km))}")
mw = model_mm(1e5*LY)/1e6
print(f"Milky Way model {mw/1e6:.1f} million km = {mw/149.6e6:.3f} of real Earth-Sun distance; = {mw/384400:.0f} x real Earth-Moon")
print(f"person 1.7 m model in nm: {model_mm(1.7e-3)*1e6:.3f} nm (atoms 0.1-0.5 nm)")
print(f"ISS model {model_mm(400)*1000:.1f} um vs hair 17-181 um")
print(f"Sun model {model_mm(1392000)/10:.1f} cm vs grapefruit 10-15 cm")
def gc(a,b):
    la1,lo1,la2,lo2=map(radians,a+b); d=sin((la2-la1)/2)**2+cos(la1)*cos(la2)*sin((lo2-lo1)/2)**2
    return 2*6371.0088*asin(sqrt(d))
nyc=(40.7128,-74.0060)
for city,c in {"Salt Lake City":(40.7608,-111.8910),"Denver":(39.7392,-104.9903),"Las Vegas":(36.1699,-115.1398),"Phoenix":(33.4484,-112.0740),"Los Angeles":(34.0522,-118.2437)}.items():
    print(f"NYC-{city}: {gc(nyc,c):,.0f} km")
print("London-Moscow:", round(gc((51.5074,-0.1278),(55.7558,37.6173))), "km; Lisbon-Moscow:", round(gc((38.7223,-9.1393),(55.7558,37.6173))))
