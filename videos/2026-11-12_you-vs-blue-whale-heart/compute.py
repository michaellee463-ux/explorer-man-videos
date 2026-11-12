# Derived figures for "You vs. a Blue Whale's Heart" — all from facts.md source values
ft = 0.3048; lb = 0.45359237
length_ft = 110; print(f"110 ft = {length_ft*ft:.1f} m (ROM: about 33 m; Live Science: 34 m)")
w_lb = 330_000; print(f"330,000 lb = {w_lb*lb/1000:.1f} tonnes (ROM: up to 150 tonnes)")
heart_kg = 180; print(f"180 kg = {heart_kg/lb:.0f} lb (NOAA: about 400 lb)")
h_lo, h_hi = 0.200, 0.425  # human heart, kg (Live Science: 200-425 g)
print(f"whale heart / human heart: {heart_kg/h_hi:.0f}x to {heart_kg/h_lo:.0f}x  -> 'more than 400 times heavier' holds for every value in range: {heart_kg/h_hi > 400}")
for g in (230, 280, 340): print(f"  vs {g} g heart: {heart_kg/(g/1000):.0f}x")
print(f"2 beats/min -> one beat every {60/2:.0f} s")
print(f"60-100 bpm -> one beat every {60/100:.1f}-{60/60:.1f} s; in 30 s your heart beats {60*0.5:.0f}-{100*0.5:.0f} times")
human_h = 1.7
print(f"to-scale drawing: whale 33 m vs 1.7 m person -> ratio {33/human_h:.1f}")
