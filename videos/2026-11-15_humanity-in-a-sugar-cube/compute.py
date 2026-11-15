import math
pop = 8.30e9                 # UN WPP 2024, 1 Jul 2026 (StatisticsTimes; IPS/UN)
rho_lo, rho_hi = 2.0e17, 2.5e17   # nuclear density, kg/m^3 (commonly ~2.3e17)
rho = 2.3e17
# Total human mass, two independent routes
# A) Walpole 2012: 287 Mt for 4.63 bn adults (62 kg avg). Scale adults to 2026 (~6.2 bn adults est.) + children ~2.1 bn at ~20 kg
adults_2026 = 6.2e9; kids_2026 = pop - adults_2026
mA = adults_2026*62 + kids_2026*20
# B) Bar-On et al. 2018 PNAS: humans ~0.06 Gt C (2018 pop ~7.6 bn); carbon ~18.5% of body mass
mB = 0.06e12/0.185 * pop/7.6e9
print(f"total human mass A (Walpole-scaled): {mA/1e9:.0f} Mt ; B (Bar-On carbon): {mB/1e9:.0f} Mt")
for m in (mB, mA):
    for r in (rho_lo, rho, rho_hi):
        V = m/r*1e6  # cm^3
        print(f"  m={m/1e9:.0f} Mt rho={r:.1e}: volume {V:.2f} cm^3, cube side {V**(1/3):.2f} cm")
# Empire State Building: 365,000 short tons (ESB fact sheet)
esb = 365000*907.185
print(f"ESB mass {esb/1e3:.0f} t; humanity = {mB/esb:.0f} to {mA/esb:.0f} ESBs")
# one person: 62 kg average adult
for r in (rho_lo, rho_hi):
    V = 62/r; d = (6*V/math.pi)**(1/3)
    print(f"one 62 kg adult at rho={r:.1e}: sphere diameter {d*1e6:.1f} um (human hair ~17-180 um)")
# atom vs nucleus: hydrogen (Bohr radius 52.9 pm vs proton 0.84 fm), carbon (~70 pm vs ~2.7 fm)
for name, ra, rn in (("H",52.9e-12,0.84e-15),("C",70e-12,2.7e-15),("O",60e-12,2.7e-15)):
    print(f"{name}: atom/nucleus width ratio {ra/rn:,.0f}")
for stad in (100,200):
    for pea in (0.005,0.009):
        print(f"stadium {stad} m / pea {pea*1000:.0f} mm = {stad/pea:,.0f}")
# proton/electron mass: share of atom's mass in nucleus (hydrogen-1, worst case)
print(f"H-1 nucleus mass share {1836.15/(1836.15+1)*100:.3f}%")
