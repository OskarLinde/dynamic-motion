import numpy as np
import copy
import polynomial as poly
from math import inf, isinf

# simple spline curve made up of piecewise polynomials
class curve:
    # n knots
    # n+1 polys
    
    # initialize linear interpolation
    def __init__(self, x = None, y = None):
        if x is None:
            self.knots = []
            self.polys = [[0]]
            return
            
        if y is None:
            self.knots = copy.deepcopy(x.knots)
            self.polys = copy.deepcopy(x.polys)
            return
            
        assert len(x) == len(y)
        self.knots = x
        self.polys = [None] * (len(x)+1)
        self.polys[0] = [y[0]]
        for i in range(len(x)-1):
            if x[i+1] > x[i]:
                k = (y[i+1]-y[i]) / (x[i+1]-x[i])
                b = y[i] - x[i] * k
                self.polys[i+1] = [b,k]
            else:
                self.polys[i+1] = [y[i]]
        self.polys[len(x)] = [y[-1]]
    
    def poly_index(self, x):        
        assert len(self.knots) == len(self.polys) - 1

        for i in range(len(self.knots)):
            if self.knots[i] > x:
                return i
        return len(self.polys)-1

    # todo, change to __call__
    def __getitem__(self, x):
        ix = self.poly_index(x)
        return poly.eval(self.polys[ix], x)
    
    def __repr__(self):        
        ret = f"Spline:\n"
        for i in range(len(self.polys)):
            if i < len(self.knots):
                ret += f"    x < {self.knots[i]:.6g} \t"
            else:
                ret += "    else    \t"
            ret += f"{poly.to_string(self.polys[i])}\n"
        return ret
    
    def differentiate(self):
        ret = copy.deepcopy(self)
        for i in range(len(self.polys)):
            ret.polys[i] = poly.differentiate(self.polys[i])
        return ret
        
    def integrate(self):
        ret = copy.deepcopy(self)

        for i in range(len(self.polys)):
            ret.polys[i] = poly.integrate(self.polys[i])
            # solve for constant term
            
            if i > 0:
                ret.polys[i][0] = poly.eval(ret.polys[i-1], ret.knots[i-1]) - poly.eval(ret.polys[i], ret.knots[i-1])

        return ret
    
    def shift(self, x0):
        """return a new spline q, such that q(x) = p(x + x0)"""
        ret = copy.deepcopy(self)
        
        if x0 == 0:
            return ret
        
        for i in range(len(ret.knots)):
            ret.knots[i] -= x0
        for i in range(len(ret.polys)):
            ret.polys[i] = poly.shift(ret.polys[i], x0)
            
        return ret
            
    def __mul__(self, factor):
        ret = copy.deepcopy(self)
        for i in range(len(ret.polys)):
            for j in range(len(ret.polys[i])):
                ret.polys[i][j] *= factor
        return ret
        
    def __add__(self, other):
        ret = copy.deepcopy(self)

        if isinstance(other, curve):
            if not np.array_equal(self.knots, other.knots):
                ret.insert_knots(other.knots)

            if not np.array_equal(self.knots, other.knots):
                other = copy.deepcopy(other)
                other.insert_knots(ret.knots)

            assert np.array_equal(ret.knots, other.knots)            

            for i in range(len(ret.polys)):
                ret.polys[i] = poly.add(ret.polys[i], other.polys[i])
            
        elif type(other) == int or type(other) == float:
            for i in range(len(ret.polys)):
                ret.polys[i] = poly.add(ret.polys[i], other)

        return ret

    def range_min(self):
        return self.knots[0]
        
    def range_max(self):
        return self.knots[-1]

    def range(self, i):
        assert len(self.knots) == len(self.polys) - 1

        a = self.knots[i-1] if i > 0 else -inf
        b = self.knots[i] if i < len(self.knots) else +inf
        return a,b
    
    def minmax(self):
        y_min, y_max = inf, -inf
        for i in range(len(self.knots)-1):
            a = self.knots[i]
            b = self.knots[i+1]
            m = poly.minmax(self.polys[i+1], a, b)
            y_min = min(y_min, m[0])
            y_max = max(y_max, m[1])
        return y_min, y_max

    def insert_knots(self, knots):
        assert all(knots[i] < knots[i+1] for i in range(len(knots)-1))

        new_knots = []
        new_polys = [self.polys[0]]

        i,j = 0,0
        while i < len(self.knots) and j < len(knots):
            if self.knots[i] <= knots[j]:
                new_knots.append(self.knots[i])
                new_polys.append(self.polys[i+1])                
                if self.knots[i] == knots[j]:
                    j += 1 # skip this knot
                i += 1
                continue
            # knots[j] is a new knot
            new_knots.append(knots[j])
            new_polys.append(new_polys[-1])
            j += 1

        while j < len(knots):
            new_knots.append(knots[j])
            new_polys.append(new_polys[-1])
            j += 1

        while i < len(self.knots):
            new_knots.append(self.knots[i])
            new_polys.append(self.polys[i+1])
            i += 1


        self.knots = new_knots
        self.polys = new_polys


    
# combines two non-overlapping splines
def combine(spline1, spline2):
    if len(spline1.knots) == 0:
        return curve(spline2)
    elif len(spline2.knots) == 0:
        return curve(spline1)
    
    if spline1.knots[-1] > spline2.knots[0]:
        spline2,spline1 = spline1,spline2
    assert spline1.knots[-1] <= spline2.knots[0]
    
    ret = curve()
    if spline1.knots[-1] == spline2.knots[0]:
        ret.knots = np.concatenate((spline1.knots, spline2.knots[1:]), axis=0)
        ret.polys = np.concatenate((spline1.polys[:-1], spline2.polys[1:]), axis=0)
    else:
        ret.knots = np.concatenate((spline1.knots, spline2.knots), axis=0)
        ret.polys = np.concatenate((spline1.polys, spline2.polys[1:]), axis=0)
    
    assert all(ret.knots[i] <= ret.knots[i+1] for i in range(len(ret.knots)-1))
        
    return ret

def kinked_line(k_neg, k_pos):
    ret = curve()
    ret.knots = [0]
    ret.polys =  [ [0, k_neg], [0, k_pos] ]
    return ret

# create a new spline f(g(t))
def composite(f, g):
    ret = curve()
    ret.polys = []

    # identify all new knots
    for j in range(len(g.polys)):
        
        additional_knots = []
        # find the points where g transitions across a knot in f
        for i in range(len(f.knots)):            
            additional_knots.extend(poly.find_roots(poly.add(g.polys[j], -f.knots[i]), *g.range(j)))

        if additional_knots:
            additional_knots = list(dict.fromkeys(sorted(additional_knots)))
        additional_knots.append(g.range(j)[1])

        knot_left = ret.knots[-1] if ret.knots else additional_knots[0] - 1
        for knot_right in additional_knots:
            if isinf(knot_right):
                knot_right = knot_left + 1
            # pick an arbitrary point well inside the interval
            mid_point = 0.5 * (knot_left + knot_right)
            y = g[mid_point]
            i = f.poly_index(y)
            ret.knots.append(knot_right)
            ret.polys.append(poly.composite(f.polys[i], g.polys[j]))

            knot_left = knot_right

    ret.knots.pop() # remove the bogus +inf knot at the end
    return ret

def harmonize_knots(splines):
    if all([np.array_equal(splines[i].knots, splines[i+1].knots) for i in range(len(splines)-1)]):
        return
        
    knots = set()
    for s in splines:
        knots.update(s.knots)

    knots = list(knots)
    knots.sort()

    for s in splines:
        s.insert_knots(knots)


