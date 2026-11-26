# Cosmic calendar: whole history of the universe squeezed into one 365-day year.
import datetime as dt
AGE = 13.787e9            # Planck 2018 (13.8 bn rounded, NASA)
YEAR_S = 365*86400
def when(years_ago, age=AGE):
    frac = 1 - years_ago/age
    t = dt.datetime(2026,1,1) + dt.timedelta(seconds=frac*YEAR_S)
    return t, (years_ago/age)*YEAR_S
print(f"1 calendar day  = {AGE/365/1e6:.1f} million years")
print(f"1 calendar hour = {AGE/365/24/1e6:.2f} million years")
print(f"1 calendar sec  = {AGE/YEAR_S:.0f} years")
ev = [("MoM-z14 galaxy seen (280 My after BB)", AGE-280e6),
      ("Sun / solar system (4.57 bn)", 4.57e9), ("Sun (4.6 bn)", 4.6e9), ("Earth (4.54 bn)", 4.54e9),
      ("Life, earliest widely accepted (3.5 bn)", 3.5e9), ("Life, 3.8 bn", 3.8e9),
      ("Cambrian explosion (538.8 My)", 538.8e6), ("First dinosaurs (230 My)", 230e6), ("First dinosaurs (233 My)", 233e6),
      ("Asteroid / K-Pg (66 My)", 66e6), ("Genus Homo (~2.8 My)", 2.8e6), ("Homo sapiens (300,000 y)", 3e5),
      ("Writing (~5,200 y, cuneiform c.3200 BCE)", 5226), ("Great Pyramid (c.2560 BCE)", 2560+2026), ("80-year life", 80)]
for n, y in ev:
    t, s = when(y)
    print(f"{n:45s} -> {t:%b %d %H:%M:%S}   ({s:,.2f} s before midnight; {s/60:,.2f} min)")
for age in (13.7e9, 13.8e9, 13.9e9):
    t, s = when(3e5, age); print(f"Homo sapiens with age {age/1e9} bn -> {t:%H:%M:%S}")
for y in (2.8e5, 3.15e5, 3.5e5):
    t, s = when(y); print(f"Homo sapiens {y:,.0f} y -> {t:%H:%M:%S}")
print("80 yr life in s:", when(80)[1], "< 0.2:", when(80)[1] < 0.2, "; blink 0.1-0.4 s")
print("Pyramid seconds:", when(4586)[1])
