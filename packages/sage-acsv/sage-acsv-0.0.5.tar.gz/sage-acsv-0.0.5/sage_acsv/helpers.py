from sage_acsv.debug import *

########################################
#
# RationalFunctionReduce
#
# Given: Two polynomials G and H
# 
# Goal: Reduce G and H by dividing out their GCD
#
# INPUT:
#   - Polynomials G, H
#
# OUTPUT:
#   - G/GCD(G,H), H/GCD(G,H)
#
########################################

def RationalFunctionReduce(G, H):
    g = gcd(G, H)
    return G/g, H/g

########################################
#
# Gets the height of a polynomial, which is the max abs of its coefficients
#
# Input:
#    - A polynomial F
#
# Output:
#    - Height of F
#
########################################

def GetHeight(F):
    return max([abs(x) for x in F.coefficients()])

########################################
#
# Gets the norm of a polynomial, which is the 2-norm of its coefficients
#
# Input:
#    - A polynomial F
#
# Output:
#    - Norm(F)
#
########################################

def GetNorm(F):
    return sqrt(sum([abs(x**2) for x in F.coefficients()]))

########################################
#
# Takes the log of x, minimized at 0
#
# Input:
#    - Real number x
#    - Optional: Base of log (usually 2 for bitsize)
#
# Output:
#    - log x if x > 1, else 0
#
########################################

def SafeLog(x, base = 2):
    return log(max(x, 1), 2)

########################################
#
# NewtonRefine
#
# Given: A function `F` with root `p`, and a precision in binary digits
# 
# Goal: Refine the root `p` to `digits` digits of accuracy
#
# INPUT:
#   - A polynomial F
#   - A root p of F as a complex number (or complex interval field)
#   - A positive integer `digits`
#   - Optional: A boolean `real` indicating if we know that it's a real root
#
# OUTPUT:
#   - The root `p` as a complex interval field (or real interval field if `real`)
#     to `digits` binary digits of precision
#
########################################

def NewtonRefine(F, p, digits, real=False):
    CF = ComplexIntervalField(2*digits + 5)  # Computation field.
    RF = RealIntervalField(2*digits + 5)
    x = CF(CF(p).center())
    MAX_STEPS = 2*digits
    delta = 1

    for _ in range(MAX_STEPS):
        y = x
        delta = CF((-F(y)/F.derivative()(y)).center())
        x = y + delta
        if abs(delta).contains_zero() or -log(abs(delta)) >= digits + 1:
            # Assuming Newton's method is converging, the value of the root p0 is within delta of x
            delta = abs(delta)
            re = RF(x.real() - delta/2, x.real() + delta/2)
            im = RF(x.imag() - delta/2, x.imag() + delta/2)
            return CF(re, 0) if real else CF(re, im)
    
    print("Did not converge")
    delta = abs(delta)
    re = RF(x.real() - delta, x.real() + delta)
    im = RF(x.imag() - delta, x.imag() + delta)
    return CF(re, 0) if real else CF(re, im)

########################################
#
# Smale Alpha test
#
# Get the alpha value of Smale's Alpha test to check for Newton convergence
#
# INPUT:
#   - A polynomial F
#   - A root p of F as a complex interval field
#
# OUTPUT:
#   - The root `p` as a complex interval field (or real interval field if `real`)
#     to `digits` binary digits of precision
#
########################################

def SmaleAlphaValue(F, p):
    Fd = F.derivative()
    beta = abs(F(p)/Fd(p))
    gamma = 0
    Fk = Fd
    for k in range(2, F.degree() + 2):
        Fk = Fk.derivative()
        gamma = ceil(max(gamma, abs(Fk(p)/Fd(p)/factorial(k)).upper()**(1/(k-1))))

    alpha = beta.upper() * gamma
    return alpha

########################################
#
# Generate Linf
#
# Computes the determinant of z_n H_{z_n} Hess, where Hess is the Hessian
# of the map: z_1*...*z_{n-1}*log(g(z_1,...,z_{n-1}))
# where with g defined from IFT via H(z_a1,...,z_{n-1},g(z_1,...,z_{n-1}))
# assuming it is possible.
#
# Input:
#   - system: A polynomial system
#   - vsT: A list of variables in the system
#   - u_: A variable not in vsT
#   - (Optional) linf_constant:
#
# Output:
#   - A linear form that (hopefully) separate the roots of the system
########################################

def GenerateLinearForm(system, vsT, u_, linf_constant = None):
    if linf_constant is not None:
        return u_ - linf_constant

    maxcoeff = ceil(max([max([abs(x) for x in f.coefficients()]) for f in system]))
    maxdegree = max([f.degree() for f in system])
    return u_ - sum([randint(-maxcoeff*maxdegree-31, maxcoeff*maxdegree+31)*z for z in vsT])

########################################
#
# Gets the annihilating polynomial of variable v corresponding to Q
#
# Input:
#    - P: A polynomial P in u_
#    - Q: Polynomial such that Pd * v - Q = 0
#    - u_: A variable
#
# Output:
#    - A minimal polynomial in x0 that is 0 at all roots of v
#
########################################

def GetAnnihilatingPolyonimial(P, Q, u_):
    R = P.parent()
    Rx, x0 = PolynomialRing(R, 'x0').objgen()
    flat = Rx.flattening_morphism()
    Flat_Ring = flat.codomain()
    x0 = Flat_Ring(x0)
    AnnRing = PolynomialRing(QQ, x0) # May need to be QQ(i) eventually
    Pd = P.derivative(u_)

    resultant = flat(P).resultant(flat(Pd)*x0-Q, Flat_Ring(u_))
    r_squarefree, _ = resultant.quo_rem(gcd(resultant, resultant.derivative(x0)))
    return AnnRing(r_squarefree/r_squarefree.content())

########################################
#
# Converts x to an int, if possible
#
# Input:
#    - x: A value
#
# Output:
#    - x as an integer
#
########################################

def SafeInt(x):
    try:
        return int(x)
    except:
        if type(x) == type(RIF(0)):
            return int(x.center())