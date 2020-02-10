pipe = [
    lambda f: bg.bilateral(5, 75, 50) - f.bilateral(5, 75, 50),
    lambda f: f.extend(60),
    lambda f: f.threshold(data.threshold),
    lambda f: f.fillContours(minArea=10, rects=False),
    lambda f: f.closing(kernel=(18,18), shape='ellipse', iterations=4),
    lambda f: f.closing(kernel=(50, 1)),
    lambda f: f.opening(kernel=(5,5), shape='ellipse'),
    lambda f: f.implode(60),
    lambda f, o: o.mask(f==0,0) if data.render else f,
    lambda f: f.toNormalizedByte()
]
