# Derived figures for the Leonids Short (facts.md)
v = 71.0            # km/s, Leonid entry speed (NASA, Britannica, Sky at Night, Star Walk; AMS/IMO say 72)
print(f"speed: {v} km/s = {v*3600:,.0f} km/h = {v*3600/1.609344:,.0f} mph")
ny_la = 3936        # km, great-circle NYC-LA (~3,940 km / 2,445 mi)
print(f"NY->LA at 71 km/s: {ny_la/v:.1f} s ; at 69.7: {ny_la/69.7:.1f} s ; at 72: {ny_la/72:.1f} s  (all < 60 s)")
moon = 384400       # km average Earth-Moon distance
for vv in (69.7, 71, 72):
    print(f"Earth->Moon at {vv} km/s: {moon/vv/60:.1f} min = {moon/vv/3600:.2f} h")
# pea-sized Leonid ~10 mm, ~0.5 g (AMS)
m = 0.5e-3
for vv in (69.7, 71, 72):
    print(f"KE of 0.5 g at {vv} km/s: {0.5*m*(vv*1000)**2/1e6:.2f} MJ")
for mass, kmh in ((1500, 100), (2000, 105), (2000, 113), (2500, 113)):
    ke = 0.5*mass*(kmh/3.6)**2/1e6
    print(f"car {mass} kg at {kmh} km/h ({kmh/1.609344:.0f} mph): {ke:.2f} MJ ; pea/car ratio at 69.7 km/s = {0.5*m*(69.7e3)**2/1e6/ke:.2f}")
print("1966: 40 per second =", 40*60, "per minute =", 40*3600, "per hour")
print("Tempel-Tuttle period 33 yr -> 1966 + 33 =", 1966+33)
