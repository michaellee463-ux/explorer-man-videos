# Derived figures for "What If You Fell Into Jupiter?" (all inputs from facts.md sources)
G_M_J = 126.687e6        # km^3/s^2 (NSSDC GM Jupiter)
R_J = 71492              # km equatorial radius at 1 bar (NSSDC)
R_E_eq = 6378.1          # km (NSSDC)
v_esc = 59.5             # km/s (NSSDC)
import math
print("check v_esc from GM/R:", round(math.sqrt(2*G_M_J/R_J),2),"km/s")
mph = v_esc*3600/1.609344
print("fall-in speed ~ escape speed:", v_esc,"km/s =", round(mph),"mph =", round(v_esc*3600),"km/h")
earth_circ = 40075.017  # km equatorial circumference
print("time to circle Earth at 59.5 km/s:", round(earth_circ/v_esc/60,1),"min")
print("Jupiter width / Earth width (equatorial):", round(R_J/R_E_eq,2))
print("Jupiter width / Earth width (mean radii 69911/6371):", round(69911/6371.0,2))
print("Volume ratio (NSSDC):", 1321.33)
g_ratio_mean, g_eq, g_pol = 25.92/9.82, 23.12/9.78, 27.01/9.83
print("gravity ratios mean/eq/polar:", round(g_ratio_mean,2), round(g_eq,2), round(g_pol,2))
galileo_mph=106000; print("Galileo probe km/s:", round(galileo_mph*1.609344/3600,1))
print("Galileo final pressure 22.7 atm ~", round(22.7*1.01325,1),"bar")
for c in (16000,20000,24000,24700,30000): print("core",c,"C vs Sun surface 5500C ratio",round(c/5500,1))
# metallic hydrogen layer thickness (from transition depth to core radius ~0.1 R_J) under each source
for frac,name in ((0.25,'Britannica 1/4 down'),(1/3,'Juno 1/3 down'),(0.5,'NASA ~halfway')):
    print(name,"layer thickness ~",round((1-frac-0.1)*69911),"km  (Earth diameter 12742 km)")
