"""Every number used in the Voyager 1 one-light-day Short, computed (not typed by hand)."""
import math, json, datetime as dt

C = 299_792.458            # km/s, exact (SI definition)
AU = 149_597_870.7         # km, exact (IAU 2012)
DAY = 86_400               # s
MILE = 1.609344            # km
LY = C * DAY * 365.25      # km, Julian light-year
out = {}

# --- one light-day
LD = C * DAY
out["light_day_km"] = LD
out["light_day_billion_km"] = LD / 1e9
out["light_day_billion_miles"] = LD / MILE / 1e9
out["light_day_AU"] = LD / AU

# --- time in flight: launch Sept 5, 1977 -> milestone Nov 18, 2026 (NASA)
launch, mile = dt.date(1977, 9, 5), dt.date(2026, 11, 18)
days = (mile - launch).days
out["flight_days"] = days
out["flight_years"] = days / 365.25

# --- speed (NASA: "nearly 38,000 mph (61,000 kph)")
v_kmh = 61_000
out["speed_km_s"] = v_kmh / 3600
out["speed_mph_from_kmh"] = v_kmh / MILE
out["38000mph_in_kmh"] = 38_000 * MILE
out["sanity_distance_if_constant_speed_billion_km"] = v_kmh * 24 * days / 1e9   # should be near 25.9

# --- light-time ladder
out["moon_light_s"] = 384_400 / C
out["sun_light_s"] = AU / C
out["sun_light_min_s"] = divmod(AU / C, 60)
nep_au = 30.07
out["neptune_from_sun_light_h"] = nep_au * AU / C / 3600
out["voyager_light_h"] = LD / C / 3600
out["round_trip_h"] = 2 * LD / C / 3600

# --- nearest star (Proxima Centauri, 4.2465 ly from parallax 768.07 mas)
prox_ly = 4.2465
prox_km = prox_ly * LY
out["proxima_km"] = prox_km
out["years_to_proxima_at_61000kmh"] = prox_km / v_kmh / (24 * 365.25)
out["years_to_proxima_at_17.0km_s"] = prox_km / 17.0 / (DAY * 365.25)
out["proxima_in_light_days"] = prox_km / LD
out["light_day_as_pct_of_proxima"] = 100 * LD / prox_km

# --- geometry for the map on Nov 18, 2026 10:16 UTC (JPL approximate Keplerian elements, 1800-2050)
EL = {  # a, e, I, L, long.peri, long.node ; then rates per Julian century
    "Mercury": (0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593, 0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081),
    "Venus": (0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255, 0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418),
    "Earth": (1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0, 0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0),
    "Mars": (1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891, 0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343),
    "Jupiter": (5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909, -0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106),
    "Saturn": (9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448, -0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794),
    "Uranus": (19.18916464, 0.04725744, 0.77263783, 313.23810451, 170.95427630, 74.01692503, -0.00196176, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589),
    "Neptune": (30.06992276, 0.00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574, 0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664),
}


def jd(y, m, d, h=0.0):
    a = (14 - m) // 12; yy = y + 4800 - a; mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045 - 0.5 + h / 24


def helio(name, J):
    a0, e0, I0, L0, w0, O0, da, de, dI, dL, dw, dO = EL[name]
    T = (J - 2451545.0) / 36525
    a, e, I, L, wb, O = a0 + da * T, e0 + de * T, I0 + dI * T, L0 + dL * T, w0 + dw * T, O0 + dO * T
    w = math.radians(wb - O); M = math.radians((L - wb) % 360); I = math.radians(I); O = math.radians(O)
    E = M
    for _ in range(30):
        E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    xp, yp = a * (math.cos(E) - e), a * math.sqrt(1 - e * e) * math.sin(E)
    cw, sw, cO, sO, cI, sI = math.cos(w), math.sin(w), math.cos(O), math.sin(O), math.cos(I), math.sin(I)
    x = (cw * cO - sw * sO * cI) * xp + (-sw * cO - cw * sO * cI) * yp
    y = (cw * sO + sw * cO * cI) * xp + (-sw * sO + cw * cO * cI) * yp
    z = (sw * sI) * xp + (cw * sI) * yp
    return x, y, z


J = jd(2026, 11, 18, 10 + 16 / 60)
E = helio("Earth", J)
geo = {}
for n in EL:
    p = helio(n, J)
    if n == "Earth":
        continue
    dx, dy, dz = p[0] - E[0], p[1] - E[1], p[2] - E[2]
    geo[n] = {"helio_lon": math.degrees(math.atan2(p[1], p[0])) % 360, "helio_r": math.hypot(p[0], p[1], p[2]),
              "geo_lon": math.degrees(math.atan2(dy, dx)) % 360, "geo_dist_AU": math.sqrt(dx * dx + dy * dy + dz * dz)}
sun_lon = math.degrees(math.atan2(-E[1], -E[0])) % 360
out["earth_helio_lon"] = math.degrees(math.atan2(E[1], E[0])) % 360
out["earth_sun_dist_AU"] = math.hypot(*E)
out["sun_geo_lon"] = sun_lon
out["planets"] = geo
out["neptune_geo_light_h"] = geo["Neptune"]["geo_dist_AU"] * AU / C / 3600
out["neptune_geo_light_h_m"] = divmod(geo["Neptune"]["geo_dist_AU"] * AU / C / 60, 60)

# Moon (low-precision mean longitude + largest term), d = days since J2000
d = J - 2451545.0
Lm = (218.316 + 13.176396 * d) % 360; Mm = math.radians((134.963 + 13.064993 * d) % 360)
out["moon_geo_lon"] = (Lm + 6.289 * math.sin(Mm)) % 360
out["moon_elongation_from_sun"] = (out["moon_geo_lon"] - sun_lon) % 360


def eq2ecl(ra_deg, dec_deg):
    eps = math.radians(23.4365); a, dd = math.radians(ra_deg), math.radians(dec_deg)
    b = math.asin(math.sin(dd) * math.cos(eps) - math.cos(dd) * math.sin(eps) * math.sin(a))
    lam = math.atan2(math.sin(a) * math.cos(eps) + math.tan(dd) * math.sin(eps), math.cos(a))
    return math.degrees(lam) % 360, math.degrees(b)


# Voyager 1 direction (constellation Ophiuchus; RA ~17h14m, Dec ~+12.1 deg) and Proxima Centauri (RA 14h29m43s, Dec -62d40m46s)
v_lon, v_lat = eq2ecl(15 * (17 + 14.4 / 60), 12.1)
p_lon, p_lat = eq2ecl(15 * (14 + 29 / 60 + 43 / 3600), -(62 + 40 / 60 + 46 / 3600))
out["voyager_ecl_lon_lat"] = (v_lon, v_lat)
out["proxima_ecl_lon_lat"] = (p_lon, p_lat)
cs = (math.sin(math.radians(v_lat)) * math.sin(math.radians(p_lat)) +
      math.cos(math.radians(v_lat)) * math.cos(math.radians(p_lat)) * math.cos(math.radians(v_lon - p_lon)))
out["angle_voyager_to_proxima_deg"] = math.degrees(math.acos(cs))
# Voyager's distance from the Sun when it is exactly one light-day from Earth
ve = (math.cos(math.radians(v_lat)) * math.cos(math.radians(v_lon)), math.cos(math.radians(v_lat)) * math.sin(math.radians(v_lon)), math.sin(math.radians(v_lat)))
# |r*ve - E| = LD/AU  -> solve for r
b_ = -2 * (ve[0] * E[0] + ve[1] * E[1] + ve[2] * E[2]); c_ = sum(k * k for k in E) - (LD / AU) ** 2
r = (-b_ + math.sqrt(b_ * b_ - 4 * c_)) / 2
out["voyager_sun_dist_AU_at_milestone"] = r
out["voyager_sun_light_h"] = r * AU / C / 3600
# range rate that day: Voyager 16.9 km/s outward + Earth's orbital motion along the line of sight
ev = (-29.78 * math.sin(math.radians(out["earth_helio_lon"])), 29.78 * math.cos(math.radians(out["earth_helio_lon"])), 0)
out["range_rate_km_s"] = 16.9 - (ev[0] * ve[0] + ev[1] * ve[1])

# opposition sanity checks for the ephemeris (expected: Neptune ~Sep 25-26 2026, Saturn ~Oct 4 2026, Uranus ~Nov 25 2026, Jupiter ~Jan 10 2026)
chk = {}
for n in ("Jupiter", "Saturn", "Uranus", "Neptune"):
    best = None
    for k in range(-420, 120):
        Jk = jd(2026, 11, 18) + k
        Ek, Pk = helio("Earth", Jk), helio(n, Jk)
        dl = abs(((math.degrees(math.atan2(Pk[1], Pk[0])) - math.degrees(math.atan2(Ek[1], Ek[0]))) + 180) % 360 - 180)
        if best is None or dl < best[0]:
            best = (dl, k)
    chk[n] = str(dt.date(2026, 11, 18) + dt.timedelta(days=best[1]))
out["opposition_dates_check"] = chk

if __name__ == "__main__":
    print(json.dumps(out, indent=1, default=str))
    json.dump(out, open("voy_facts.json", "w"), indent=1, default=str)
