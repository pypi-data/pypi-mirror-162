from sage_acsv.helpers import *

########################################
#
# Kronecker (A translation of Maple Code)
#
# Given: A (regular reduced) sequence of polynomials F.
# 
# Goal: Achieve a symbolic Kronecker representation of the solutions to the system {f = 0 : f in F}.
#
# INPUT:
#   - system: {f = 0 : f in F}
#   - u: a new variable not containing the variables in system
#   - lambda_: parameter introduced for critical point computation
#   - vs: variables of the system
#   - Optional: A linear form in the given variables and u
#
# OUTPUT:
#   - P: a polynomial in u
#   - Qs: a list of polynomials in u
#
########################################

def Kronecker(system, u_, vs, lambda_=None, linf_constant = None):
    # Generate a linear form
    linf = GenerateLinearForm(system, vs, u_, linf_constant)

    expanded_R = u_.parent()
    if lambda_:
        x0_Ring, x0 = PolynomialRing(expanded_R, 'x0').objgen()
        rabinowitsch_R = PolynomialRing(QQ, [x0] + list(expanded_R.gens()), len(expanded_R.gens()) + 1, order="degrevlex")
    else:
        rabinowitsch_R = PolynomialRing(QQ, list(expanded_R.gens()), len(expanded_R.gens()), order="degrevlex")

    u_ = rabinowitsch_R(u_)
    if lambda_:
        lambda_, x0 = rabinowitsch_R(lambda_), rabinowitsch_R(x0)

    rabinowitsch_system = [rabinowitsch_R(f) for f in system] + [rabinowitsch_R(linf)]
    if lambda_:
        if (MPolynomialIdeal(rabinowitsch_R, rabinowitsch_system + [lambda_*(1-lambda_*x0)]).dimension() > 0):
            print(f"{bcolors.WARNING}Warning:{bcolors.ENDC} A critical point exists with λ = 0.")
            print(f"{bcolors.WARNING}Warning:{bcolors.ENDC} Any minimal critical point computations performed may be incomplete.")
        rabinowitsch_system += [1-lambda_*x0]
    n = len(rabinowitsch_R.gens())

    # Compute Grobner basis for ordered system of polynomials
    I = MPolynomialIdeal(rabinowitsch_R, rabinowitsch_system)
    try:
        I = MPolynomialIdeal(rabinowitsch_R, I.groebner_basis())
    except:
        raise ACSVException("Trouble computing Groebner basis. System may be too large.")
    
    big_gb = I.transformed_basis('fglm')

    rabinowitsch_R = rabinowitsch_R.change_ring(order="lex")
    u_ = rabinowitsch_R(u_)
    if lambda_:
        lambda_, x0 = rabinowitsch_R(lambda_), rabinowitsch_R(x0)

    gb = [p for p in big_gb if not lambda_ or p.polynomial(x0).is_constant()] # the ones without x0
    #print("GB", gb)
    Ps = [p for p in gb if len(p.variables()) != 0 and not any([z in vs for z in p.variables()])]
    if len(Ps) != 1:
        print(rabinowitsch_system)
        print(Ps)
        print(gb)
        raise ACSVException("No P polynomial found for Kronecker Representation.")
    u_ = Ps[0].variables()[0]
    R = PolynomialRing(QQ, u_)
    P = R(Ps[0])
    P, _ = P.quo_rem(gcd(P, P.derivative(u_)))
    Pd = P.derivative(u_)

    # Find Q_i for each variable
    Qs = []
    for z in vs:
        z = rabinowitsch_R(z)
        eqns = [f for f in gb if z in f.variables()]
        if len(eqns) != 1:
            print(eqns, z, vs)
            raise ACSVException("Linear form does not separate the roots.")
            return

        eq = eqns[0].polynomial(z)

        if eq.degree() != 1:
            print(eq, z)
            raise ACSVException("Linear form does not separate the roots.")
            return
        _, rem = (Pd*eq.roots()[0][0]).quo_rem(P)
        Qs.append(rem)

    # Forget base ring, move to univariate polynomial ring in u over a field
    Qs = [R(Q) for Q in Qs]

    return P, Qs

########################################
#
# Numerical Kronecker (A translation of Maple Code)
#
# Given: The symbolic Kronecker representation encoded by a polynomial in the variable u and a list of polynomials in u.
# 
# Goal: Achieve the isolating intervals (resp. disks) for the real (resp. complex) roots of the polynomial up to a certain precision.
#
# INPUT:
#   - P: polynomial in the variable u
#   - Qs: list of polynomials in the variable u
#   - torus: list of approximate bounds for the roots of P(u)
#
# OUTPUT:
#   - precise_roots: list of approximated roots
#   - N: Array of sanitized roots data of the form [root: [Qs: [root]]]
#   - kappa: precision in number of digits
#
########################################

def NumericalKronecker(P, Qs, show_time=False):
    u_ = P.variables()[0] # ordered ring
    Pd = P.derivative(u_)

    # Precision should at least be enough to separate the roots of P
    # using the bounds given in Proposition 7.7 of the textbook
    deg = P.polynomial(u_).degree() # degree of P
    norm = GetNorm(P)
    precision = deg**((deg+2)/2)*norm**(deg-1)

    timer = Timer(show_time)

    # Find real and complex roots of P, ignoring multiplicities
    # Run Smale test to see if Newton's method will work on these points
    root_precision = 53
    roots = P.polynomial(u_).roots(ComplexIntervalField(53), multiplicities=False)
    for _ in range(max(MIN_SMALE_RETRIES, deg)):
        if any([SmaleAlphaValue(P, root) > SMALE_CONSTANT for root in roots]):
            root_precision *= 2
            roots = P.polynomial(u_).roots(ComplexIntervalField(root_precision), multiplicities=False)
        else:
            break
    else:
        print(f"{bcolors.WARNING}Warning: {bcolors.ENDC} Could not find roots close enough to pass Smale's alpha test. Root approximations may be inaccurate.")
    
    timer.checkpoint("Final Smale Iteration")

    precisionByQ = []
    for Q in Qs:
        # Precision for Q depends on degree and height of annihilating polynomial
        # In this case, the annihilating polynomial has the same degree as P
        PdQDegree = max(Pd.degree(), Q.degree())
        PdQHeight = max(GetHeight(Pd), GetHeight(Q))
        h = GetHeight(P) * PdQDegree + PdQHeight * P.degree() + log(factorial(P.degree() + PdQDegree)) + PdQDegree + P.degree()
        precisionByQ.append(deg**((deg+2)/2)*(h * sqrt(P.degree()))**(deg-1) + 5)

    # Number of binary digits needed in approximation of Q_j/P'
    digits = int(SafeLog(max(precisionByQ+[precision]))) + 1

    approx_Pds = [abs(Pd(p)) for p in roots]
    approx_Qs = [[abs(Q(p)) for p in roots] for Q in Qs]

    Pdm = floor(min(approx_Pds))
    Qm = ceil(max([max(values_of_one_Q) for values_of_one_Q in approx_Qs]))

    digits = digits + ceil(SafeLog(1/Pdm + 2*Qm/(Pdm**2)))

    Umax = max([abs(r) for r in roots]+[1])
    Pd_max = abs(sum([abs(coeff)*(Umax+1)**k for (k,coeff) in Pd.dict().items()]))
    Q_max = max([abs(sum([abs(coeff)*(Umax+1)**k for (k,coeff) in Q.dict().items()])) for Q in Qs])
    kappa = SafeInt(RIF(SafeLog(max(Pd_max, Q_max))).upper()) + digits
    kappa = SafeInt(kappa)

    timer.checkpoint()

    precise_roots = roots

    N = []
    for i in range(len(precise_roots)):
        root = precise_roots[i]
        # Calculate the values of the variables at the solution corresponding to this root
        pd_val = Pd(root)
        while (pd_val.contains_zero() and root.prec() < kappa):
            root = NewtonRefine(P, root, root.prec() * 2, real = root.imag() == 0)
            pd_val = Pd(root)

        precise_roots[i] = root

        Qt = Qs[-2]
        vt = Qt(root)/pd_val
        valid_t = True
        while root.prec() < kappa:
            if vt.real() < 0 or vt.real() > 1 or not vt.imag().contains_zero():
                valid_t = False
                break

            root = NewtonRefine(P, root, min(root.prec() * 2, kappa), real = root.imag() == 0)
            precise_roots[i] = root
            vt = Qt(root)/pd_val

        if not valid_t:
            row = [Q(root)/Pd(root) for Q in Qs]
            N.append(row)
            continue

        row = []
        for Q in Qs:
            v = Q(root)/pd_val
            if v.contains_zero():
                v = 0
            elif v.real().contains_zero():
                v = v.imag() * I 
            elif v.imag().contains_zero():
                v = v.real()
            row.append(v)

        for j in range(i):
            row_j = N[j]
            root_j = precise_roots[j]
            if not row_j[-2].imag() == 0 or row_j[-2] < 0 or row_j[-2] > 1:
                continue

            if all([row[r].real().overlaps(row_j[r].real()) and row[r].imag().overlaps(row_j[r].imag()) for r in range(len(row[:-2]))]):
                for r in range(len(row[:-2])):
                    if row[r].real().overlaps(row_j[r].real()) and row[r].imag().overlaps(row_j[r].imag()):
                        row[r] = row_j[r]

        N.append(row)

    timer.checkpoint("Refine Roots")

    return precise_roots, N, kappa

########################################
#
# MinimalCriticalCombinatorial (A translation of Maple Code)
#
# Given: A combinatorial multivariate rational function F=G/H admitting a finite number of 
# critical points with non-degenerate minimal critical points.
# 
# Goal: Find the minimial critical points of F.
#
# INPUT:
#   - Two polynomials G and H.
#   - Variables: A tuple vs, lambda_, t, u of variables
#      - vs: Variables in G and H
#      - lambda_: A variable not in vs used for determining a Kronecker representation
#      - t: A variable not in vs used for confirming minimality of critical points
#      - u: Variable not in vs used for the polynomial P of a Kronecker system
#   - Optional: A direction vector r in Q**n, n = len(vs)
#   - Optional: A linear form in the given variables and u.
#
# OUTPUT:
#   - P: A polynomial in u representing the minimal polynomial of the algebraic
#     numbers in dominant asymptotics (OR: set of roots of P corresponding to the
#     minimal critical points)
#   - Qs: Polynomials Q[i] for the variables in the Kronecker representation defined by P.
#
# Intermediate Functions:
#   - Kronecker
#   - NumericalKronecker
#
########################################

def MinimalCriticalCombinatorial(G, H, variables, r = None, linf_constant = None, show_points = False, show_time=False):
    timer = Timer(show_time)

    # Fetch the variables we need
    vs, lambda_, t, u_ = variables
    expanded_R = variables[-1].parent()
    vsT = vs + [t, lambda_]

    # If direction r is not given, default to the diagonal
    if r is None:
        r = [1 for i in range(len(vs))]

    # Create the critical point equations system
    vsH = H.variables()
    system = [vsH[i]*H.derivative(vsH[i]) - r[i] * lambda_ for i in range(len(vsH))] + [H, H.subs({z: z*t for z in vsH})]

    # Compute the Kronecker representation of our system
    timer.checkpoint()
    P, Qs = Kronecker(system, u_, vsT, lambda_, linf_constant)
    timer.checkpoint("Kronecker")

    # Find Numerical Approximations to Kronecker system
    U, N, kappa = NumericalKronecker(P, Qs, show_time=show_time)
    timer.checkpoint("NumericalKronecker")

    Qt = Qs[-2] # Qs ordering is H.variables() + [t, lambda_]
    Pd = P.derivative()

    # Solutions to Pt are solutions to the system where t is not 1
    one_minus_t = gcd(Pd-Qt, P)
    Pt, _ = P.quo_rem(one_minus_t) 
    degP, degPt, hPt = P.degree(), Pt.degree(), SafeLog(GetHeight(Pt))
    Pnorm = GetNorm(P)
    tol = (degPt + 1)**(1-degP) * 2**(hPt * (1-degP)) * Pnorm**(-degPt)

    # Get the precision required to determine if t is in (0,1)
    d_t = P.degree()
    PdQDegree = max(Pd.degree(), Qt.degree())
    PdQHeight = max(GetHeight(Pd), GetHeight(Qt))
    h_t = GetHeight(P) * PdQDegree + PdQHeight * P.degree() + log(factorial(P.degree() + PdQDegree)) + PdQDegree + P.degree()
    A_t_norm = sqrt(d_t) * h_t

    precision_t = ceil(max(h_t+1, (d_t+2)/2 * SafeLog(d_t) + (d_t-1) * SafeLog(A_t_norm))) + kappa

    # We are interested if those solutions have t in (0,1), to detect if solutions with t = 1 are minimal
    # We use Prop 7.7 (iii) to check if t is not 1. If it isn't, we need to ensure it's contained in (0,1)
    # (remember that all numerical roots are intervals). 
    R_t = []
    R_exact = []
    for root_i in range(len(U)):
        t_val = (Qt/Pd).subs({u_: U[root_i]})

        if not t_val.imag().contains_zero():
            continue

        if RIF(abs(Pt(U[root_i])) - tol) >= 0:
            # Case 1: t == 1
            R_exact.append((root_i, N[root_i]))
            continue

        t_val = t_val.real()
        precision_t_step = t_val.prec()

        while True:
            if RIF(0, 1).overlaps(t_val) and not t_val.contains_zero() and not (1-t_val).contains_zero():
                # Case 2: t is contained in (0,1)
                R_t.append((root_i, N[root_i]))
                break
            elif not t_val.contains_zero() and not (1-t_val).contains_zero():
                # Case 3: t lies outside [0,1]
                break
            elif precision_t_step >= precision_t:
                # We already found t to enough precision to determine the range
                # Yet the two checks above still failed
                raise ACSVException("Could not determine range of t:" +  str(t_val))
                break
            else:
                # Increase precision of t and try again
                precision_t_step = min(precision_t_step*2, precision_t)
                t_val = NewtonRefine(ann_t, t_val, precision_t_step).real()    

    timer.checkpoint("Precision of t")     

    # We know at least one real root will have minimum modulus, so we filter by real roots for minimals
    pos_R_exact = [(i, row) for i, row in R_exact if all([coord.imag() == 0 and not coord < 0 for coord in row[:-2]])]
    minimals = []
    for i, candidate in pos_R_exact:
        ts = [row[-2] for (_, row) in R_t if all([(row[i]-candidate[i]).contains_zero() for i in range(len(row)-2)])]
        if any([0 < t and t < 1 for t in ts]):
            continue
        minimals.append((i, candidate))

    if len(minimals) == 0:
        raise ACSVException(f"No smooth minimal critical points found.")
    elif len(minimals) > 1:
        raise ACSVException(f"More than one minimal point with positive real coordinates found.")
        print("Error: More than one minimal point with positive real coordinates found.")

    # Change the equations to only deal with t=1 solutions
    newP = one_minus_t
    newPd = one_minus_t.derivative()
    _, invPd, _ = xgcd(Pd, newP)
    Qs = [(Q*newPd*invPd).quo_rem(newP)[1] for Q in Qs]
    P = newP
    Pd = newPd

    # Find annihilating polynomials of coordinates
    # See Melczer and Salvy paper Corollary 53 for the derivation of this bound
    modBoundPerVariable = []
    precisionPerVariable = []
    annPolys = []

    for var_k in range(len(Qs)):
        res = GetAnnihilatingPolyonimial(P, Qs[var_k], u_)
        annPolys.append(res)
        d = res.degree()
        res_norm = max(res.dict().values())

        # Need to know M_k(T) to this accuracy:
        mod_bound = ((d**2+1)*res_norm**2)**(d**2-1)* (res_norm*d)**(2*d**2)
        modBoundPerVariable.append(mod_bound)

        # For this we need to know T to this accuracy
        max_abs_coord_value = max([abs(row[var_k]) for row in N])
        res_max = sum([abs(coeff)*(max_abs_coord_value+1)**k for k, coeff in res.dict().items()])
        precisionPerVariable.append(mod_bound * res_max)

    kappa2 = max(kappa, ceil(SafeLog(max(precisionPerVariable)).upper()))

    # Start with the minimal positive real critical point
    min_i, min_p = minimals[0]
    torus = [U[min_i]]

    # Form a list of candidate roots that might have the same modulus (up to the precision we know already)
    n_vars = len(min_p) - 2
    cand = [(i,row) for i, row in R_exact if i != min_i and all([(abs(row[k])-abs(min_p[k])).contains_zero() for k in range(n_vars)])]

    # Refine each candidate point to the new precision
    # For each candidate point, verify annPolys[k](|x|) * annPolys[k](-|x|) is 0
    for i, row in cand:
        precise_coords = [NewtonRefine(annPolys[k], row[k].center(), kappa2) for k in range(n_vars)]
        
        if all([(annPolys[k](abs(precise_coords[k]))*annPolys[k](-abs(precise_coords[k]))).contains_zero() for k in range(n_vars)]):
            torus.append(U[i])

    # Print list of critical points for visualization and to help with testing
    if (show_points):
        for u in torus:
            print("Point: ", [Prettify(Q(u)/Pd(u)) for Q in Qs[:-2]])

    timer.checkpoint("Minimal Points")
    return P, Qs, torus, kappa2

########################################
#
# DetHessianWithLog
#
# Computes the determinant of z_n H_{z_n} Hess, where Hess is the Hessian
# of the map: z_1*...*z_{n-1}*log(g(z_1,...,z_{n-1}))
# where with g defined from IFT via H(z_a1,...,z_{n-1},g(z_1,...,z_{n-1}))
# assuming it is possible.

# Input:
#   - H: polynomial (denominator of F)
#   - P: polynomial in _u
#   - vs: list of variables z_1, z_2, ..., z_n
#   - u: variable not contained in vs

# Output:
#   - A polynomial in _u
########################################

def DetHessianWithLog(H, P, Qs, vsT, _u, R):
    vs = vsT[:-2]
    z_n = vs[-1]
    n = len(vs)

    # Build n x n matrix of U[i,j] = z_i * z_j * H'_{z_i * z_j}
    U = matrix([[v1 * v2 * H.derivative(v1, v2)/(z_n * H.derivative(z_n)) for v2 in vs] for v1 in vs])
    V = [v * H.derivative(v)/(z_n * H.derivative(z_n)) for v in vs]

    # Build (n-1) x (n-1) Matrix for Hessian
    arrH = [[V[i] * V[j] + U[i][j] - V[j] * U[i][-1] - V[i]*U[j][-1] + V[i] * V[j] * U[-1][-1] for j in range(n-1)] for i in range(n-1)]
    for i in range(n-1):
        arrH[i][i] = arrH[i][i] + V[i]

    arrH = vs[-1] * H.derivative(vs[-1]) * matrix(arrH)

    matH = matrix([[KroneckerReduce(F, P, Qs, vsT, _u, R) for F in row] for row in arrH])

    return matH.determinant() % P

########################################
#
# Reduces a rational function with respect to a Kronecker system, assuming
# that the denominator does not vanish on the solutions of the system.
#
# Input:
#    - F: rational function in vsT
#    - P: polynomial in u from the (symbolic) Kronecker representation
#    - Qs: list of polynomials in u from the (symbolic) Kronecker representation
#    - vs: list of variables
#    - u: A variable not contained in vs
#
# Output:
#    - A polynomial in u corresponding to F with respect to the Kronecker System [P, Qs]
#
########################################

def KroneckerReduce(F, P, Qs, vsT, u_, R):
    # Need to convert polynomial to univariate ring in order to take xgcd
    Uni = PolynomialRing(QQ, u_)
    P = Uni(P)
    
    # Pdinv is Pd inverse modulo P
    _, _, Pdinv = xgcd(P, P.derivative(u_))

    denF = R(F.denominator())
    numF = R(F.numerator())

    if denF != 1:
        denF = denF.subs({v: Qs[vsT.index(v)] * Pdinv for v in denF.variables() if v != u_}) % P
        # denFInv is denF inverse modulo P
        _, _, denFInv = xgcd(P, Uni(denF))
    else:
        denFInv = Uni(1)

    numF = Uni(numF.subs({v: Qs[vsT.index(v)] * Pdinv for v in numF.variables() if v != u_}))

    # Convert back to multivariate ring before returning
    return R(numF * denFInv % P)

