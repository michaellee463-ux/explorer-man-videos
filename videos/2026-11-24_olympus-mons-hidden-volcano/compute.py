import math
everest_km = 8.84886            # 2020 China-Nepal survey
oly_h = {'ESA/Britannica 22':22.0,'Wikipedia/SkyAtNight datum 21.3':21.287,'Space.com/HyperPhysics 25':25.0,'Astronomy.com 26':26.0}
for k,h in oly_h.items(): print(f'height {k} km -> {h/everest_km:.2f}x Everest')
cruise_ft=35000; cruise_km=cruise_ft*0.3048/1000
print(f'cruise 35,000 ft = {cruise_km:.2f} km (range 35-42k ft = {35000*0.0003048:.1f}-{42000*0.0003048:.1f} km); 22 km / cruise = {22/cruise_km:.2f}x, vs 42k ft {22/(42000*0.0003048):.2f}x; 22 km = {22/0.3048*1000:,.0f} ft = {22/1.609344:.1f} mi')
for w in (500,600,700):
    for h in (21.3,22,25,26):
        print(f'width {w} / height {h} = {w/h:.1f}')
area=math.pi*300**2; az=295234
print(f'area of 600 km circle = {area:,.0f} km2 ; Arizona {az:,} km2 ; ratio {area/az:.2f}; 600 km = {600/1.609344:.0f} mi')
R=3389.5e3
for h in (1.5,1.7,1.8):
    print(f'horizon distance on Mars, eye {h} m: {math.sqrt(2*R*h)/1000:.2f} km')
print('5 percent slope = {:.2f} degrees'.format(math.degrees(math.atan(0.05))))
print('drop over 3 km at 5 percent: {:.0f} m'.format(3000*0.05))
print('to-scale drawing: 1000 px wide => height %.1f px' % (1000*22/600))
