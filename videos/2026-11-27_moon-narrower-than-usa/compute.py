# Explorer Man 2026-11-27 — every derived figure for "The Moon is narrower than the USA"
import json, math
from pyproj import Geod, Transformer
from shapely.geometry import shape, Point
from shapely.ops import transform, unary_union
g = Geod(ellps='WGS84')
D = dict(Moon=3474.8, Ceres=939.4, Pluto=2376.6, Mercury=4879.4, Ganymede=5268.2, Mars=6779.0)  # km, NASA/JPL mean diameters
print('Diameters (km):', D)
US_WIDE = 4509  # km, greatest great-circle distance in the contiguous US (Wikipedia, Florida–Washington)
# independently check the 4,509 km coast-to-coast line: Cape Flattery-ish WA -> Key West-ish FL? use the CONUS outline
st = json.load(open('build/states.geojson'))
lower48 = [f for f in st['features'] if f['properties'].get('iso_a2') == 'US' and f['properties'].get('name') not in ('Alaska', 'Hawaii')]
print('states in lower 48 (incl. DC):', len(lower48))
us = unary_union([shape(f['geometry']) for f in lower48])
tx = [shape(f['geometry']) for f in lower48 if f['properties']['name'] == 'Texas'][0]
pts = []
for geom in (us.geoms if us.geom_type == 'MultiPolygon' else [us]):
    if geom.area < 0.5: continue
    pts += list(geom.exterior.coords)[::3]
best = (0, None, None)
import itertools
W = [p for p in pts if p[0] < -117]; E = [p for p in pts if p[0] > -85]
for a in W:
    for b in E:
        _, _, dd = g.inv(a[0], a[1], b[0], b[1])
        if dd > best[0]: best = (dd, a, b)
print('max great-circle distance across lower-48 outline (Natural Earth 1:50m): %.0f km between %s and %s' % (best[0] / 1000, best[1], best[2]))
print('  -> coast-to-coast is 4,509-4,648 km depending on endpoints; Moon is %.0f-%.0f%% of it; Pluto %.0f-%.0f%%; Mercury %.2f-%.2f x' % (D['Moon']/4648*100, D['Moon']/4509*100, D['Pluto']/4648*100, D['Pluto']/4509*100, D['Mercury']/4648, D['Mercury']/4509))
for k in ('Moon', 'Pluto', 'Mercury', 'Ganymede'):
    print(f'{k}: {D[k]:.0f} km = {D[k]/1.609344:.0f} mi = {D[k]/US_WIDE*100:.0f}% of US coast-to-coast {US_WIDE} km')
print('Pluto / US width (2,800 mi = 4,506 km):', round(D['Pluto'] / 4506, 2))
# Texas
TX_W_MI = 773; print('Texas width 773 mi =', round(TX_W_MI * 1.609344), 'km; Ceres / Texas width =', round(D['Ceres'] / (TX_W_MI * 1.609344), 2))
lae = lambda lat, lon: Transformer.from_crs('EPSG:4326', f'+proj=laea +lat_0={lat} +lon_0={lon} +units=km', always_xy=True).transform
tx_km = transform(lae(31, -99.5), tx)
print('Texas area from outline (equal-area): %.0f km2 (official 695,662 km2)' % tx_km.area)
xmin, ymin, xmax, ymax = tx_km.bounds; print('Texas outline bbox: %.0f km E-W x %.0f km N-S' % (xmax - xmin, ymax - ymin))
# largest Ceres-size circle that fits fully inside Texas?
from shapely.algorithms.polylabel import polylabel
txm = max(tx_km.geoms, key=lambda p: p.area) if tx_km.geom_type == "MultiPolygon" else tx_km
c = polylabel(txm, tolerance=1); r = txm.exterior.distance(c)
print('largest circle inside Texas outline: diameter %.0f km  (Ceres 939 km -> fits fully: %s)' % (2 * r, 2 * r >= D['Ceres']))
print('Ceres disk area %.0f km2 = %.0f%% of Texas' % (math.pi * (D['Ceres'] / 2) ** 2, math.pi * (D['Ceres'] / 2) ** 2 / 695662 * 100))
# Surface areas
def S(d): return 4 * math.pi * (d / 2) ** 2
US_TOTAL = 3796742 * 2.589988  # sq mi (Census, 50 states + DC total area) -> km2
AFRICA = 30.37e6; RUSSIA = 17.1e6; ASIA = 44.58e6
print('Moon surface area: %.2f million km2' % (S(D['Moon']) / 1e6))
print('US total area: %.2f million km2; Moon / US = %.2f' % (US_TOTAL / 1e6, S(D['Moon']) / US_TOTAL))
print('Moon / Africa = %.2f; Moon / Asia = %.2f' % (S(D['Moon']) / AFRICA, S(D['Moon']) / ASIA))
print('Pluto surface area: %.2f million km2; Pluto / Russia = %.3f' % (S(D['Pluto']) / 1e6, S(D['Pluto']) / RUSSIA))
print('Flattened Moon skin as one disk: diameter %.0f km (= 2 x Moon diameter)' % (2 * math.sqrt(S(D['Moon']) / math.pi)))
print('Ganymede - Mercury = %.0f km' % (D['Ganymede'] - D['Mercury']))
EARTH = 12742.0  # km mean diameter (NASA)
for lo, hi in ((4509, 4648),):
    print('Mars / US width: %.2f-%.2f ; Earth / US width: %.2f-%.2f' % (D['Mars'] / hi, D['Mars'] / lo, EARTH / hi, EARTH / lo))
print('Australia ~4,000 km E-W vs Moon 3,475 km: Australia wider by %.0f km' % (4000 - D['Moon']))
co = json.load(open('build/countries.geojson'))
au = [shape(f['geometry']) for f in co['features'] if f['properties']['NAME'] == 'Australia'][0]
main = max(au.geoms, key=lambda p: p.area)
cs = list(main.exterior.coords)
Wp = [p for p in cs if p[0] < 118]; Ep = [p for p in cs if p[0] > 150]
best = max(((g.inv(a[0], a[1], b[0], b[1])[2], a, b) for a in Wp[::2] for b in Ep[::2]), key=lambda x: x[0])
print('Australia mainland widest W->E great-circle (Natural Earth): %.0f km between %s and %s; Moon %.0f km' % (best[0] / 1000, best[1], best[2], D['Moon']))
