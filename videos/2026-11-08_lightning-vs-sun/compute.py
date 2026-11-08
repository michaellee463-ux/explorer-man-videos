# Derived figures for "Lightning vs the Sun" Short
sun_C = 5500; sun_F = 10000          # NASA; Britannica gives 10,000 F (5,537 C)
lt_C = 30000; lt_F = 50000           # Britannica, NASA Earthdata, NWS
c2f = lambda c: c*9/5+32
f2c = lambda f: (f-32)*5/9
print(f"Sun 5,500 C -> {c2f(5500):,.0f} F ; 10,000 F -> {f2c(10000):,.0f} C")
print(f"Lightning 30,000 C -> {c2f(30000):,.0f} F ; 50,000 F -> {f2c(50000):,.0f} C")
print(f"Ratio in C: {lt_C/sun_C:.2f}x ; ratio in F: {lt_F/sun_F:.2f}x")
print(f"Ratio in kelvin: {(lt_C+273.15)/(sun_C+273.15):.2f}x ; using Sun 5,772 K effective: {(lt_C+273.15)/5772:.2f}x")
print(f"Ratio w/ Britannica 5,537 C: {lt_C/5537:.2f}x")
rate = 44
print(f"44 flashes/s -> per minute {rate*60:,}, per day {rate*86400:,}, per year {rate*86400*365.25/1e9:.2f} billion")
print("Earthdata seasonal range 35-55/s brackets 44; NTRS 44 +/- 5")
