# Derived figures for "How Big Does an Asteroid Have to Be to End the World?" (2026-11-18)
import math
HIRO_KT = 15.0                      # Hiroshima yield, kt TNT (Britannica, DOE/OSTI)
KT_J = 4.184e12                     # 1 kt TNT in joules

# Chelyabinsk
chel_kt = 500.0                     # ~500 kt (Planetary Society, ESA, NatGeo)
print(f"Chelyabinsk / Hiroshima = {chel_kt/HIRO_KT:.1f}x  (470 kt -> {470/HIRO_KT:.1f}x)")
print(f"Chelyabinsk speed 19 km/s = {19*3600:,} km/h")

# Tunguska
for mt in (10, 15):
    print(f"Tunguska {mt} Mt / Hiroshima = {mt*1000/HIRO_KT:.0f}x")
area = 2000.0
print(f"Tunguska area {area:.0f} km2 = circle {2*math.sqrt(area/math.pi):.1f} km across")

# Meteor Crater
w = 1200.0
field = 120*0.9144                  # US football field incl. end zones (120 yd)
print(f"Meteor Crater 1.2 km / football field ({field:.1f} m) = {w/field:.1f}")

# Apophis
R_E = 6371.0
d_surface = 32000.0                 # NASA: ~32,000 km from surface
geo = 35786.0                       # geosynchronous altitude, km
print(f"Apophis 5.9 Earth radii from centre -> {5.9*R_E - R_E:,.0f} km above surface (Space.com/Binzel)")
print(f"Apophis 32,000 km vs GEO {geo:,.0f} km: closer by {geo-d_surface:,.0f} km")
moon = 384400.0
print(f"32,000 km = {d_surface/moon*100:.1f}% of Moon distance")
print(f"Apophis 340 m / Chelyabinsk 20 m = {340/20:.0f}x wider; volume {(340/20)**3:,.0f}x")

# Chicxulub
everest = 8.849
for d in (10, 12, 15):
    print(f"Chicxulub {d} km vs Everest {everest} km: taller by {d-everest:.2f} km ({d/everest:.2f}x)")
tt = 100e6                          # NSF: ~100 teratons TNT = 1e8 Mt = 1e11 kt
print(f"Chicxulub 100 Tt / Hiroshima = {tt*1000/HIRO_KT/1e9:.1f} billion; {tt*1e3*KT_J:.1e} J")
print(f"Chicxulub 10 km / Chelyabinsk 20 m = {10000/20:.0f}x wider")

# DART
before = 11*60+55; after = 11*60+23
print(f"DART: {before} -> {after} min, change {before-after} min ({(before-after)/before*100:.1f}%)")
# ladder sanity: 20 m -> 50-100 m -> 340 m -> 1 km -> 10 km
for a,b in ((20,340),(340,1000),(1000,10000)):
    print(f"{b}/{a} = {b/a:.0f}x")
