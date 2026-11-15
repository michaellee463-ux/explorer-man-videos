# vidIQ channel_analytics, Oct 18 - Nov 15 2026, per video
rows=[("small earth BIG SUN","11-05",1604,746,72.6,42,4,2,2),
("You vs. Smallest Thing","11-06",1600,704,84.2,31,1,1,1),
("All 7 Planets","11-07",1532,868,85.1,22,1,0,2),
("What If Betelgeuse","11-06",1384,809,75.0,35,0,0,1),
("Drive to the Sun","11-07",1373,631,69.1,22,0,0,0),
("Lightning vs Sun (cliffhanger)","11-08",1245,594,83.7,19,0,1,0),
("SS United States reef (news)","11-12",1225,727,66.7,22,0,0,0),
("Voyager light-day (cliffhanger)","11-10",1184,559,114.7,23,1,0,2),
("Ocean depth","11-05",443,77,53.7,4,0,0,1),
("Earth's water ball","11-09",369,84,49.4,5,0,0,0),
("Blue whale heart (You vs #2)","11-12",142,48,54.7,2,0,0,0),
("Billion seconds v2","11-06",66,32,57.7,1,0,0,0),
("Strep throat","11-12",45,17,63.5,1,0,0,0)]
print(f"{'video':34s} views engaged% shares/1k likes% avg%")
for t,d,v,e,p,l,s,c,sub in rows:
    print(f"{t:34s} {v:5d} {100*e/v:6.1f} {1000*s/v:8.2f} {100*l/v:5.2f} {p:5.1f}")
tot=sum(r[2] for r in rows); sh=sum(r[6] for r in rows)
print("total views",tot,"total shares",sh)
print("Shorts feed share of views: %.1f%%"%(100*11340/(11340+3+156+1+234+12+208+185+25+19+1+435)))
