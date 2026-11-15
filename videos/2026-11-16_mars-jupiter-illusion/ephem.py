from astropy.time import Time
from astropy.coordinates import get_body, solar_system_ephemeris, EarthLocation, AltAz
import astropy.units as u
loc = EarthLocation(lat=39.33*u.deg, lon=-76.63*u.deg)  # Baltimore
solar_system_ephemeris.set('builtin')
for d in ['2026-11-15','2026-11-16','2026-11-17','2026-11-18','2026-11-19','2026-11-20','2026-11-22']:
    t = Time(d+' 10:30')   # 5:30 am EST
    m = get_body('mars', t, loc); j = get_body('jupiter', t, loc)
    aa = AltAz(obstime=t, location=loc)
    ma, ja = m.transform_to(aa), j.transform_to(aa)
    print(d, 'sep %.2f deg'%m.separation(j).deg, 'Mars %.1f Mkm'%(m.distance.to(u.km).value/1e6), 'Jup %.1f Mkm'%(j.distance.to(u.km).value/1e6),
          'Jup alt %.0f az %.0f'%(ja.alt.deg, ja.az.deg), 'Mars alt %.0f az %.0f'%(ma.alt.deg, ma.az.deg))
