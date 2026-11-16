# vidIQ, Oct 19 - Nov 16 2026 (pulled Nov 16); judge only videos published <= Nov 13
rows=[("You vs Smallest","11-06",1613,715,83.3,32,1,1),("small earth BIG SUN","11-05",1605,747,72.6,43,4,2),
("All 7 Planets","11-07",1533,869,85.0,23,1,0),("Betelgeuse","11-06",1384,809,75.0,36,0,0),("Drive to Sun","11-07",1373,631,69.1,23,0,0),
("SS United States","11-12",1356,800,66.1,24,0,0),("Starship","11-13",1257,681,77.1,37,2,3),("Lightning vs Sun","11-08",1246,595,83.6,20,0,1),
("Voyager","11-10",1216,573,114.2,25,1,0),("Doomsday","11-13",963,478,73.6,19,0,2),("Ocean depth","11-05",443,77,53.7,5,0,0),
("Water ball","11-09",371,84,49.4,6,0,0),("Blue whale heart","11-12",165,58,54.0,4,0,0),("Strep throat","11-12",68,27,52.6,3,0,0)]
print(f"{'video':22}{'views':>6}{'EVR%':>6}{'avg%':>6}{'like%':>6}{'sh/1k':>6}{'cmt':>4}")
for n,d,v,e,a,l,s,c in rows: print(f"{n:22}{v:6}{100*e/v:6.0f}{a:6.0f}{100*l/v:6.1f}{1000*s/v:6.1f}{c:4}")
print("Traffic: SHORTS feed 13,457 of ~15,200 views (~89%); search 675; subscribers 300; related 289")
