# geometry
p = 3.14


def radius(d):
    r = float(d/2)
    return r


def diameter(r):
    d = float(r*2)
    return d


def ST(a, h):
    s = 0.5 * (a * h)
    return s

# operations with π


def Cd(d):
    c = p*d
    return c


def Cr(r):
    c = (2*p)*r
    return c


def Sr(r):
    s = p*(r*r)
    return s


def Sd(d):
    s = (d*d)/4*p
    return s


def Sl(l):
    s = (l*l)/(4*p)
    return s

#density, mass and volume

# Ro


def P(m, v):
    p = m/v
    return p

# Mass


def Mass(p, v):
    m = p * v
    return m

# Volume


def V(m, p):
    v = m/p
    return v

# math convertor


def sm(sm):
    d = sm/10
    m = sm/100
    km = sm/100000
    return "Decimetr:", str(d), "Meter:", str(m), "Kilometer:", str(km)


def dm(dm):
    sm = dm*10
    m = dm/10
    km = dm/10000
    return "Centimeter:", str(sm), "Meter:", str(m), "Kilometer:", str(km)


def m(m):
    sm = m*100
    dm = m*10
    km = m/1000
    return "Centimeter:", str(sm), "Decimetr:", str(dm), "Kilometer:", str(km)


def km(km):
    sm = km/100000
    dm = km/10000
    m = km/1000
    return "Centimeter:", str(sm), "Decimetr:", str(dm), "Meter:", str(m)
