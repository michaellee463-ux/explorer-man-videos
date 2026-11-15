c = 299_792.458            # km/s
AU = 149_597_870.7         # km
KM_MI = 1.609344
mars, jup = 195.0e6, 786.9e6   # km from Earth, morning of Nov 16 2026 (astropy builtin; sky-tonight 195.5/787.8; telescopeadvisor 196/790)
gap = jup - mars
print('Mars distance  %.0f M km = %.0f M mi' % (mars/1e6, mars/KM_MI/1e6))
print('Jup distance   %.0f M km = %.0f M mi' % (jup/1e6, jup/KM_MI/1e6))
print('Jup/Mars distance ratio %.2f' % (jup/mars))
print('gap %.0f M km = %.0f M mi = %.2f AU' % (gap/1e6, gap/KM_MI/1e6, gap/AU))
print('light time Mars %.1f min, Jupiter %.1f min, gap %.1f min' % (mars/c/60, jup/c/60, gap/c/60))
# sizes (NASA fact sheets)
print('diameter ratio Jup/Mars %.1f' % (142984/6792))
print('volume ratio Jup/Mars %.0f (fact-sheet volumes)  %.0f (mean radii)' % (143128/16.312, (69911/3389.5)**3))
# brightness: mag -2.1 vs +0.7
print('Jupiter brighter by factor %.1f' % (10**(0.4*(0.7+2.1))))
