import polynomial as poly

test_polynomials = [[0],[1],[2],[0,1],[1,0],[1,2,3],[0,1,2,3,4,5],[5,4,3,2,1,0]]

def test_sq():
    for p in test_polynomials:
        p2 = poly.sq(p)
        
        for x in range(-10,10):
            assert poly.eval(p2, x) == poly.eval(p, x) ** 2


def test_pow():    
    for p in test_polynomials:
        if p != [0]:
            assert  poly.pow(p,0) == [1]        
        assert  poly.pow(p,1) == p

        for k in range(2, 8):
            pk = poly.pow(p,k)

            for x in range(-10,10):
                assert poly.eval(pk,x) == poly.eval(p,x)**k

def test_composite():
    for f in test_polynomials:
        for g in test_polynomials:
            h = poly.composite(f, g)

            for x in range(-10,10):
                y1 = poly.eval(f, poly.eval(g,x))
                y2 = poly.eval(h, x)

                assert y1 == y2

def test_shift():
    for f in test_polynomials:
        for b in range(-10, 10):
            g = poly.shift(f, b)
            for x in range(-10, 10):
                assert poly.eval(f,x) == poly.eval(g, x-b)
