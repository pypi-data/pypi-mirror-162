from math import ceil, floor
from random import randint
from sage.arith.all import gcd, lcm, nth_prime, srange, factorial, xgcd
from sage.functions.all import log
from sage.matrix.constructor import matrix
from sage.misc.all import prod
from sage.misc.latex import view as show
from sage.rings.all import CIF, ComplexIntervalField, RIF, RealIntervalField
from sage.rings.imaginary_unit import I
from sage.rings.rational_field import QQ
from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.symbolic.all import SR, pi

# This function was moved in Sage 9.5, so earlier versions of Sage will get an
# import error and must be imported from the old file
try:
    from sage.misc.all import sqrt
except:
    from sage.misc.other import sqrt