# Derived figures for the Starship Short
ft=0.3048; lbf=4.4482216153
print(f"Starship V3 408 ft = {408*ft:.1f} m")
print(f"Statue of Liberty 305 ft 1 in = {(305+1/12)*ft:.2f} m ; Starship taller by {408*ft-(305+1/12)*ft:.1f} m")
print(f"Saturn V 363 ft = {363*ft:.1f} m ; Starship taller by {408*ft-363*ft:.1f} m")
print(f"Starship 80.8 MN = {80.8e6/lbf/1e6:.2f} million lbf ; 33 x 551,156 lbf = {33*551156/1e6:.2f} million lbf")
sv=34.5e6/lbf/1e6; print(f"Saturn V 34.5 MN = {sv:.2f} million lbf ; NASA: SLS 8.8M is 15% more than Saturn V -> {8.8/1.15:.2f} million lbf")
print(f"thrust ratio Starship/Saturn V = {18.0/sv:.2f} (using 18.0M) to {18.2/(8.8/1.15):.2f}  -> 'more than twice' holds: {18.0/sv>2}")
print(f"draw scale: Starship 124.4, Saturn V 110.6, Liberty 93.0 (m)")
