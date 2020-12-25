import spline
import polynomial as poly
from math import nan
import numpy as np
from heapq import merge

# find an optimal discretization point to (if necessary) refine the linear interpolation of curve in the open interval (a,b)
def _find_subdivision_point(polynomials, tolerances, a, b):
    assert b > a
    
    worst_x = nan
    worst_re = 1 # error relative to cordial tolerance

    for i in range(len(polynomials)):
        polynomial = polynomials[i]
        # calculate the equation for the line approximation
        line = poly.line_from_to(a, poly.eval(polynomial,a), b, poly.eval(polynomial,b))

        error = poly.sub(polynomial, line)
        extremes = poly.find_roots(poly.differentiate(error), a, b)

        if extremes:
            errors = [abs(poly.eval(error,e)) for e in extremes]
            worst_index = np.argmax(errors)
            worst_relative_magnitude = errors[worst_index] / tolerances[i]
            if worst_relative_magnitude > worst_re:
                worst_re = worst_relative_magnitude
                worst_x = extremes[worst_index]

    if worst_re > 1:
        return worst_x
    else:
        return None

import sys # tmp

# find a set of internal discretization points for a linear interpolation of a polynomial subject to tolerances
def _recursive_find_points(polynomials, tolerances, min_dt, a, b):
    assert b >= a
    if b-a < min_dt:
        return []

    x = _find_subdivision_point(polynomials, tolerances, a, b)
    if x is not None:
        return _recursive_find_points(polynomials, tolerances, min_dt, a, x) + [x] + _recursive_find_points(polynomials, tolerances, min_dt, x, b)
    else:
        return []

# find a set of discretization points to jointly linearly approximate a set of spline curves
def _find_discretization_points(curves, tolerances, min_dt):
    if not curves:
        return []
    
    # assert all curves have the same knots
    for i in range(len(curves)-1):
        if not np.array_equal(curves[i].knots, np.array(curves[i+1].knots)):
            print(i, file = sys.stderr)
            print(curves[i].knots, file = sys.stderr)
            print(curves[i+1].knots, file = sys.stderr)
        assert np.array_equal(curves[i].knots, np.array(curves[i+1].knots))

    points = curves[0].knots
    additional = []
    for i in range(len(points)-1):
        a = points[i]
        b = points[i+1]
        polys = [curves[j].polys[i+1] for j in range(len(curves))]
        additional.extend(_recursive_find_points(polys, tolerances, min_dt, a, b))
    
    return list(merge(points, additional))
    
# input n curves, output n+1 lists of points, the last one being the t coordinate for the discretized points
# tolerances = list of n cordial tolerances
# min_dt = smallest discretization in t

def linear_interpolate(curves, tolerances, min_dt):

    pts = _find_discretization_points(curves, tolerances, min_dt)

    out = np.zeros((len(curves)+1, len(pts)))
    for i in range(len(curves)):
        for j in range(len(pts)):
            out[i,j] = curves[i][pts[j]]
    out[-1,:] = pts

    return out
