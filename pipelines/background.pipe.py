pipe = [
    lambda bg, o, f, s: bg.blend(s.mask(f!=0, bg[f!=0]), 0.7),     # blending [selective] - blend the current background with the change mask, preserving from ghosting and foreground aperture problems
    lambda bg, o, f, s: bg.blend(s, 0.2),                   # blending [blind] - blend the current background with the current frame, preserving from gradual light changes problem
    lambda bg: bg.blend(init_bg, 0.95)                      # blending [blind] - blend the current background with the initial background, preserving from camouflange, flickering and stationary object problems
]