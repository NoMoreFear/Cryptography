from math import inf

def gcdex(a, b):  # расширенный алгоритм Евклида
    if b == 0:
        return a, 1, 0
    else:
        d, x, y = gcdex(b, a % b)
        return d, y, x - y * (a // b)

class Curve:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p

        if not (4*pow(a, 3) + 27*pow(b, 2)) % self.p != 0:
            raise Exception("The curve %s is not smooth!" % self)

    def testPoint(self, x, y):
        if x == inf:
            return True
        return pow(y, 2) % self.p == (pow(x, 3) + self.a*x + self.b) % self.p

    def __eq__(self, other):
        return self.a, self.b, self.p == other.a, other.b, other.p

class Point:
    def __init__(self, curve, x, y):
        self.x = x
        self.y = y
        self.curve = curve

        if not curve.testPoint(x, y):
            raise Exception("Point %s does not belong to the specified curve %s!" % (self, curve))

    def inverse(self, k, p):    # обратная точка
        if k == 0:
            raise ZeroDivisionError('Division by zero')

        if k < 0:
            return p - self.inverse(-k, p)

        if gcdex(k, p)[0] != 1:
            raise Exception("The point does not have an inverse")
        else:
            return gcdex(k, p)[1]

    def __neg__(self):  # унарный минус
        if self.x == inf:
            return self
        return Point(self.curve, self.x, -self.y % self.curve.p)

    def __eq__(self, other):    # ==
        if self.curve != other.curve:
            raise Exception("Can't compare points on different curves!")
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):    # !=
        return not self == other

    def __add__(self, Q):   # сложение двух точек
        if self.curve != Q.curve:
            raise Exception("Can't add points on different curves!")

        if self.x == inf:
            return Q

        if Q.x == inf:
            return self

        if self == -Q:
            return Point(self.curve, inf, inf)

        if self.x == Q.x:
            m = (3 * self.x**2 + self.curve.a) * self.inverse(2*self.y, self.curve.p) % self.curve.p
        else:
            m = (self.y - Q.y) * self.inverse(self.x - Q.x, self.curve.p) % self.curve.p

        x3 = (m**2 - self.x - Q.x) % self.curve.p
        y3 = (self.y + m*(x3 - self.x)) % self.curve.p

        return -Point(self.curve, x3, y3)

    def __sub__(self, Q):
        return self + -Q

    def __mul__(self, k):   # умножение числа на точку k*point
        if not type(k) == int:
            raise Exception("Can't scale a point by something which isn't an int!")

        if k < 0:
            return -self * -k

        if k == 0:
            return Point(self.curve, inf, inf)

        Q = self
        if k & 1 == 1:
            R = self
        else:
            R = Point(self.curve, inf, inf)

        i = 2
        while i <= k:
            Q = Q + Q
            if k & i == i:
                R += Q
            i *= 2
        return R

    def __rmul__(self, n):
        return self * n

    def __getitem__(self, index):
        return [self.x, self.y][index]

    def __str__(self):
        return "(%r, %r)" % (self.x, self.y)

# curve = Curve(-1, 3, 127)
# p = Point(curve, 16, 20)
# q = Point(curve, 41, 120)
# print(p+q)
# print(36*p)
