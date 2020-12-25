import spline
import polynomial as poly
from pytest import approx
import copy

test_polynomials = [[0],[1],[0,1],[1,0],[1,2,3],[4,2,1]]#,[0,1,2,3,4,5],[5,4,3,2,1,0]]
test_knots = [-5, -4.9999, -4, -1, -0.1, -0.00001, 0, 0.00001, 0.1, 1, 2, 4.99999, 5]
test_knots_short = [-5, -0.00001, 0, 0.00001, 5]
def test_splines():
    ret = []
    for p in test_polynomials:
        s = spline.curve()
        s.knots = test_knots
        s.polys = [list(p) for x in range(len(s.knots) + 1)]
        ret.append(s)

        for k in test_knots_short:
            s = spline.curve()
            s.polys = [list(p), list(p)]
            s.knots = [k]
            ret.append(s)

    for p in test_polynomials:
        p = poly.sub(p, poly.eval(p,0))
        for q in test_polynomials:
            q = poly.sub(q, poly.eval(q,0))
            for knot in test_knots_short:
                s = spline.curve()
                s.knots = [knot]
                s.polys = [poly.shift(p, -knot), poly.shift(q, -knot)]
                assert poly.eval(s.polys[0], knot) == approx(poly.eval(s.polys[1], knot))
                ret.append(s)

    for p in test_polynomials:
        p = poly.sub(p, poly.eval(p,0))
        for q in test_polynomials:
            q = poly.sub(q, poly.eval(q,0))
            for knot in test_knots_short:
                knot2 = knot + 1
                p2 = poly.shift(p, -knot)
                q2 = poly.shift(q, -knot)
                for r in test_polynomials:
                    r = poly.sub(r, poly.eval(r,knot2) - poly.eval(q2, knot2))
                    s = spline.curve()
                    s.knots = [knot, knot2]
                    s.polys = [p2, q2, r]
                    assert poly.eval(s.polys[0], knot) == approx(poly.eval(s.polys[1], knot))
                    assert poly.eval(s.polys[1], knot2) == approx(poly.eval(s.polys[2], knot2))
                    ret.append(s)
    
    for s in ret:
        for k in s.knots:
            eps = 1e-15
            assert s[k-eps] == approx(s[k+eps]), "ensure continuity"
    ret = ret[:20] + ret[20::20] # reduce the size of the test set to speed up tests
    return ret

def test_insert_knots():
    for s in test_splines():
        t = copy.deepcopy(s)
        t.insert_knots(test_knots)
        for x in range(-10,10):
            assert s[x] == approx(t[x])

def test_add():
    for f in test_splines():
        for g in test_splines():
            h = f + g
            for x in range(-10,10):
                assert h[x] == approx(f[x] + g[x])

def test_composite():
    splines = test_splines()
    for s in splines:
        for t in splines:
            assert len(t.polys) == len(t.knots)+1
            u = spline.composite(s,t)

            for x in range(-10, 10):
                y1 = u[x]
                y2 = s[t[x]]
                assert y1 == approx(y2)

    for g in splines:
        for k in [-1, 0, 1]:
            for m in [-1, 0, 1]:
                f = spline.curve()
                f.polys = [[m, k]]
                h = spline.composite(f,g)
                for x in range(-10, 10):
                    assert h[x] == k * g[x] + m

def test_kinked_line():
    for g in test_splines():
        k1 = 0.7
        k2 = 1.3
        f = spline.kinked_line(k1, k2)
        h = spline.composite(f,g)
        for x in range(-10, 10):
            o = g[x]
            if o < 0:
                y = k1 * o
            else:
                y = k2 * o
            assert h[x] == approx(y)

