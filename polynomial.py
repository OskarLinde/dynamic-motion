import numpy as np
from math import inf, floor, log2

def _to_poly(p):
    if isinstance(p, (int, float, np.float64)):
        return [p]
    return p

def differentiate(polynomial):
    order = len(polynomial)-1
    if order == 0:
        return [0]
    out = np.zeros(order)
    for i in range(order):
        out[i] = polynomial[i+1] * (i+1)
    return out
    
def integrate(polynomial):
    order = len(polynomial)-1
    out = np.zeros(order+2)
    for i in range(order+1):
        out[i+1] = polynomial[i] / (i+1)
    return out

# basic helper, defines a linear function from two points
def line_from_to(x0, y0, x1, y1):
    slope = (y1-y0) / (x1-x0)
    intercept = y0 - slope * x0
    return [intercept, slope]

def to_string(poly):
    str = ""
    sep = ""
    for i in range(len(poly)):
        if i > 0 and poly[i] == 0:
            continue
        str += sep
        str += f'{poly[i]:.8g}'
        if i >= 1:
            str += 'x'
            if i >= 2:
                str += f'^{i}'
        sep = " + "
    return str
    
def add(poly1, poly2):
    poly1 = _to_poly(poly1)
    poly2 = _to_poly(poly2)

    if len(poly2) > len(poly1):
        poly1,poly2 = poly2,poly1
    ret = poly1.copy()
    for i in range(len(poly2)):
        ret[i] += poly2[i]
    return ret

def sub(poly1, poly2):
    return add(poly1, neg(poly2))

def neg(poly):
    poly = _to_poly(poly)
    return [-k for k in poly]

def mul(poly1, poly2):
    poly1 = _to_poly(poly1)
    poly2 = _to_poly(poly2)
        
    ret = [0] * (len(poly1) + len(poly2) - 1)
    for i in range(len(poly1)):
        for j in range(len(poly2)):
            ret[i+j] += poly1[i] * poly2[j]
    return ret

def sq(poly):
    n = len(poly)
    ret = [0] * (n*2-1)
    for i in range(n):
        for j in range(i, n):
            ret[i+j] += poly[i] * poly[j] * ((i!=j) + 1)
    return ret

def pow(poly, exp):
    n = floor(log2(exp)) + 1 if exp > 0 else 0
    ret = [1]
    for i in range(0,n):
        if exp & (2**i):
            ret = mul(ret, poly)
        if i < n:
            poly = sq(poly)
    return ret    
    
def eval(poly, x):
    order = len(poly)
    y = 0
    for j in range(order):
        i = order-j-1
        y = x * y + poly[i]
    return y

def shift(a, x0):
    """transform p(x) -> p(x+x0)"""
    
    if x0 == 0:
        return a[:]
    
    #Given the n-degree polynomial: p(x) = anxn+an-1xn-1+...+a1x+a0
    m = len(a)
    n = m-1
    
    #We must obtain new polynomial coefficients qi, by Taylor shift q(x) = p(x+ x0).
    #We'll use the matrix t of dimensions m x m, m=n+1 to store data.
    t = [x[:] for x in [[0] * m] * m] 
    
    #Compute ti,0 = an-i-1x0n-i-1 for i=0..n-1
    for i in range(n):
        t[i][0] = a[n-i-1] * x0**(n-i-1)
    
    #Store ti,i+1 = anx0n for i=0..n-1
    for i in range(n):
        t[i][i+1] = a[n]*x0**n
    
    #Compute ti,j+1 = ti-1,j+ti-1,j+1 for j=0..n-1, i=j+1..n
    for j in range(n):
        for i in range(j+1,n+1):        
            t[i][j+1] = t[i-1][j] + t[i-1][j+1]
    
    #Compute the coefficients: qi = tn,i+1/x0i for i=0..n-1
    q = np.zeros(m)
    for i in range(n):
        q[i] = t[n][i+1]/x0**i
        
    #The highest degree coefficient is the same: qn = an
    q[n] = a[n]
    
    return q

# find all real roots between x_min and x_max (exclusive)
def find_roots(poly, x_min, x_max):
    # eliminate (near) zero high-order coefficients
    while len(poly) > 1 and abs(poly[-1]) < 1e-16:
        poly = list(poly)
        poly.pop()
        
    if len(poly) == 0:
        return []
    elif len(poly) == 1:
        return []
    elif len(poly) == 2:
        x = -poly[0] / poly[1]
        return [x] if x_min < x and x < x_max else []
    elif len(poly) == 3:
        b = poly[1] / poly[2]
        c = poly[0] / poly[2]
        discriminant = b**2 - 4*c
        if discriminant == 0:
            x = -b/2
            return [x] if x_min < x and x < x_max else []
        elif discriminant > 0:
            sd = discriminant ** 0.5
            return [x for x in [(-b - sd)/2, (-b + sd)/2] if x_min < x and x < x_max]
        else:
            return []
    else:
        # TODO
        assert False, "unimplemented"

# return the (min, max) range of the polynomial in the given domain (inclusive)
def minmax(poly, x_min, x_max):
    r = find_roots(differentiate(poly), x_min, x_max)
    r.extend([x_min, x_max])
    y_min = inf
    y_max = -inf
    for x in r:
        y = eval(poly, x)
        y_min = min(y_min, y)
        y_max = max(y_max, y)
    return y_min, y_max

# return a new polynomial f(g(x))
def composite(f, g):
    ret = [0]
    for i in range(len(f)):
        ret = add(ret, mul(f[i], pow(g, i)))
    return ret
