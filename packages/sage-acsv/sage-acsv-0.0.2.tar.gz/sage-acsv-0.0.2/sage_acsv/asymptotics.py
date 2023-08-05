"""Functions for determining asymptotics of the coefficients
of multivariate rational functions.
"""

from sage.rings.rational_field import QQ
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage_acsv.kronecker import *

def general_asy(F, r, linf_constant=None, show_points=False, show_formula=False, show_time=False):
    r"""Asymptotics in a given direction r of the multivariate rational function F

    INPUT:

    * ``F`` -- The rational function ``G/H`` in ``d`` variables
    * ``r`` -- A vector in ``Z^d``
    * ``linf_constant`` -- (Optional) A linear combination of the input variables that separates the critical point solutions
    * ``show_points`` -- (Optional) Display the minimal critical points
    * ``show_formula`` -- (Optional) Display a prettified asymptotic formula

    OUTPUT:

    Functions ``A``, ``B``, ``C``, in ``u``, ``P``, in ``u``, and list ``U`` of the roots of ``P`` such that 
    the asymptotics is ``(2 * pi * rd * k)^((1-d)/2) * A * sqrt(B) * C^k``, where ``A``, ``B``, and ``C``
    are evaluated at each ``u`` in ``U``.

    Examples::

        >>> from sage_acsv import general_asy
        >>> var('x,y,z,t')
        (x, y, z, t)
        >>> general_asy(1/(1-(1+x)*y), [1,2], linf_constant=x+y+t)
        (1, 4, 4, u_ - 5/2, [2.5000000000000000?])
        >>> general_asy(1/(1-(x+y+z)+(3/4)*x*y*z), [1,1,1], linf_constant=x+y+z+t)
        (-4/39*u_^2 + 2/39*u_ + 137/39,
         1/36*u_^2 - 5/36*u_ + 4/9,
         -3/4*u_^2 + 3/4*u_ + 105/4,
         u_^3 - 3*u_^2 - 33*u_ + 71,
         [2.030387827908656025570492697201935828983865761216885039051492948852913493936307754616070648948255809431258756394232344287418683980?])
        """
    # TODO - variable substitution

    G, H = F.numerator(), F.denominator()

    # Initialize variables
    vs = list(H.variables())

    RR, (t, lambda_, u_) = PolynomialRing(QQ, 't, lambda_, u_').objgens()
    expanded_R, _ = PolynomialRing(QQ, len(vs)+3, vs + [t, lambda_, u_]).objgens()

    vs = [expanded_R(v) for v in vs]
    t, lambda_, u_ = expanded_R(t), expanded_R(lambda_), expanded_R(u_)
    vsT = vs + [t, lambda_]

    all_variables = (vs, lambda_, t, u_)
    d = len(vs)
    rd = r[-1]

    # Make sure G and H are coprime, and that H does not vanish at 0
    G, H = RationalFunctionReduce(G, H)
    G, H = expanded_R(G), expanded_R(H)
    if H.subs({v: 0 for v in H.variables()}) == 0:
        print("ValueError: H vanishes at 0.")
        return

    # In case form doesn't separate, we want to try again
    for _ in range(MAX_MIN_CRIT_RETRIES):
        try:
            # Find minimal critical points in Kronecker Representation
            P, Qs, torus, kappa2 = MinimalCriticalCombinatorial(
                G, H, all_variables, 
                r = r, linf_constant = linf_constant, show_points = show_points,
                show_time=show_time
            )
            break
        except Exception as e:
            print(f"{bcolors.ERROR}Error:{bcolors.ENDC}", e)
    else:
        return

    Pd = P.derivative(u_)
    
    # Find det(zH_z Hess) where Hess is the Hessian of z_1...z_n * log(g(z_1, ..., z_n))
    Det = DetHessianWithLog(H, P, Qs, vsT, u_, expanded_R)

    Pd = expanded_R(Pd)

    # Find exponential growth
    T = prod([vs[i]**r[i] for i in range(d)])

    # Find constant (recall lambda_ = z_n * diff(H, z_n))
    # P' in numerator and denominator cancel out
    A = KroneckerReduce(-G/(rd * lambda_), P, Qs, vsT, u_, expanded_R)
    B = KroneckerReduce((rd * lambda_)**(d-1) / Det, P, Qs, vsT, u_, expanded_R)
    C = KroneckerReduce(1/T, P, Qs, vsT, u_, expanded_R)

    Uni = PolynomialRing(QQ, u_)
    A, B, C = SR(A), SR(B), SR(C)

    # Optionally, print an explicit asymptotic formula
    if (show_formula):
        k = SR('k')

        u_dom = torus[0]
        # F does not incldue the exponential growth (for pretty printing reasons)
        F = (2 * pi * rd * k)**((1-d)/2) * A * sqrt(B)
        print("The dominant asymptotics of G/H are given by: ")
        print(F.simplify() * C**k)
        print("When u takes the value: ")
        print(Prettify(u_dom), "...")

        if len(torus) > 1: 
            print()
            print("Other values of u with the same root moduli are: ")
            print([Prettify(u_other) for u_other in torus[1:]])

    return A, B, C, P, torus

def diagonal_asy(F, linf_constant=None, show_points=False, show_formula=False, show_time=False):
    r"""Asymptotics in the main diagonal direction of the multivariate rational function F

    INPUT:

    * ``F`` -- The rational function ``G/H`` in ``d`` variables
    * ``linf_constant`` -- (Optional) A linear combination of the input variables that separates the critical point solutions
    * ``show_points`` -- (Optional) Display the minimal critical points
    * ``show_formula`` -- (Optional) Display a prettified asymptotic formula

    OUTPUT:

    Functions ``A``, ``B``, ``C``, in ``u``, ``P``, in ``u``, and list ``U`` of the roots of ``P`` such that 
    the asymptotics is ``(2 * pi * rd * k)^((1-d)/2) * A * sqrt(B) * C^k``, where ``A``, ``B``, and ``C``
    are evaluated at each ``u`` in ``U``.

    Examples::
        >>> from sage_acsv import diagonal_asy
        >>> var('w,x,y,z,t')
        (w, x, y, z, t)
        >>> diagonal_asy(1/(1-x-y), x+y)
        (2, 1/2, 4, u_ - 1, [1])
        >>> diagonal_asy(1/(1-w*(1+x)*(1+y)*(1+z)*(1+y+z+y*z+x*y*z)), w+t)
        (1,
         17/232*u_ + 2769/232,
         6/29*u_ + 979/29,
         u_^2 + 162*u_ - 167,
         [1.0243866176395128304979460041624885570409687718629882442474248034624837508022082533224769910032112186308030813929132274456404912393427583333590468317962782219669146237953243798363971290668613595131452663544783531462759230066179968542540102811715735193540350953680899054306441487062310104237245816634018606969996872449121191559956849844389131752535166900777803304633627795768477066585537269976929331353024401983005422792717715536118383543463737379725903412800516735508604726067853547549058770012597596467335373619525?]) 
    """
    n = len(F.denominator().variables())
    return general_asy(F, [1 for _ in range(n)], linf_constant, show_points, show_formula, show_time)

def kronecker(system, vs, linf_constant=None):
    r"""Computes the Kronecker Representation of a system of polynomials

    INPUT:

    * ``system`` -- A system of polynomials in ``d`` variables
    * ``linf_constant`` -- (Optional) A linear combination of the input variables that separates the critical point solutions

    OUTPUT:

    A polynomial ``P`` and ``d`` polynomials ``Q1, ..., Q_d`` such that ``z_i = Q_i(u)/P'(u)`` for ``u``
    ranging over the roots of ``P``

    Examples::
        >>> from sage_acsv import kronecker
        >>> var('x,y')
        (x, y)
        >>> kronecker([x**3+y**3-10, y**2-2], [x,y], x+y)
        (u_^6 - 6*u_^4 - 20*u_^3 + 36*u_^2 - 120*u_ + 100,
         [60*u_^3 - 72*u_^2 + 360*u_ - 600, 12*u_^4 - 72*u_^2 + 240*u_])
    """
    R, u_ = PolynomialRing(QQ, 'u_').objgen()
    R = PolynomialRing(QQ, len(vs)+1, vs + [u_])
    system = [R(f) for f in system]
    vs = [R(v) for v in vs]
    u_ = R(u_)
    return Kronecker(system, u_, vs, linf_constant = linf_constant)

def eval_asy(F, krange, r = None, compute_exact = False, show_time = False):
    r"""Computes numerical approximations to the coefficients of a rational generating function and prints them to the console

    INPUT:

    * ``F`` -- The rational function ``G/H`` in ``d`` variables
    * ``krange`` -- Integers for the multiples of the direction ``r``
    * ``r`` -- A vector in ``Z^d``
    * ``compute_exact`` -- (Optional) Compute the actual power series coefficients (very slow!)
    * ``show_time`` -- (Optional) Display execution time

    OUTPUT:

    None
    """
    vs = list(F.variables())
    if r == None:
        r = [1 for i in vs]

    kend = krange[-1] * sum(r)
    
    if compute_exact    :
        taylor = F.taylor(*[(v, 0) for v in vs] + [kend])

    k = SR('k')
    A, B, C, P, U = general_asy(F, r, show_time = show_time)

    _u = P.variables()[0]
    d = len(vs)
    rd = r[-1]
    asymptotics = sum([((2 * pi * rd * k)**((1-d)/2) * A * sqrt(B) * C**k).subs({_u: u.center()}) for u in U])

    for _k in krange:
        kr = [r[i] * _k for i in range(d)]
        print()
        print("[" + "*".join([str(vs[i])+"^" + str(kr[i]) for i in range(d)]) + "]F(" + ",".join([str(v) for v in vs]) + ")")
        approx = float(asymptotics.subs({k: _k}))
        print("Approximation:", approx)

        if compute_exact:
            actual = taylor.coefficient(prod([vs[i]**kr[i] for i in range(d)]))
            print("Actual value: ", actual)
            error = float(abs(approx - actual)/actual * 100)
            print("Percent error:", str(round(error, 2)) + "%")


