import sys
from sympy import *
from math import log


def root_NewtonRaphson(f, x, dfdx=None, eps=1E-6, max_iterations=100, return_x_list=False):
    r"""
    Newton-Raphson's method for the solution of nonlinear algebraic equations

    .. math ::
        x_{n+1} = x_{n} - \frac{f(x_n)}{f'(x_n)}

    :param f: Function
    :param dfdx: Function derivative
    :param float x: Initial root guest
    :param float eps: Tolerance
    :param int max_iterations: Max number of iterations
    """
    f_value = f(x)
    iteration_counter = 0
    if return_x_list:
        x_list = []
    while abs(f_value) > eps and iteration_counter < max_iterations:
        try:
            if dfdx is None:
                def dfdx():
                    sym_x = symbols('x')
                    dfdx_expr = diff(f(sym_x), sym_x)
                    dfdx_lambda = lambdify([sym_x], dfdx_expr)
                    return dfdx_lambda
                dfdx = dfdx()
            x = x - float(f_value) / dfdx(x)
        except ZeroDivisionError:
            print("Error! Derivative zero for x = ", x)
            sys.exit(1)
        f_value = f(x)
        iteration_counter += 1
        if return_x_list:
            x_list.append(x)

    if abs(f_value) > eps:
        iteration_counter = -1

    if return_x_list:
        return x_list, iteration_counter
    else:
        return x, iteration_counter


def root_secant(f, x0, x1, eps, max_iterations, return_x_list=False):
    r"""
    Secant method for the solution of nonlinear algebraic equations

    :param f: Function
    :param float x0: First root guess
    :param float x1: Second root guess
    :param float eps: Tolerance
    :param int max_iterations: Max number of iterations
    """
    f_x0 = f(x0)
    f_x1 = f(x1)
    iteration_counter = 0
    if return_x_list:
        x_list = []
    while abs(f_x1) > eps and iteration_counter < max_iterations:
        try:
            denominator = float(f_x1 - f_x0) / (x1 - x0)
            x = x1 - float(f_x1) / denominator
        except ZeroDivisionError:
            print("Error! - denominator zero for x = ", x)
            sys.exit(1)  # Abort with error
        x0 = x1
        x1 = x
        f_x0 = f_x1
        f_x1 = f(x1)
        iteration_counter += 1
        if return_x_list:
            x_list.append(x)

    # Here, either a solution is found, or too many iterations
    if abs(f_x1) > eps:
        iteration_counter = -1

    if return_x_list:
        return x_list, iteration_counter
    else:
        return x, iteration_counter


def root_bisection(f, xL, xR, eps, return_x_list=False):
    r"""
    Bisection method for the solution of nonlinear algebraic equations

    :param f: Function
    :param float xL: Left initial bound
    :param float xR: Right initial bound
    :param float eps: Tolerance
    :param return_x_list:
    """
    fL = f(xL)
    if fL * f(xR) > 0:
        print("Error! Function does not have opposite signs at interval endpoints!")
        sys.exit(1)
    xM = float(xL + xR) / 2.0
    fM = f(xM)
    iteration_counter = 1
    if return_x_list:
        x_list = []

    while abs(fM) > eps:
        if fL * fM > 0:  # i.e. same sign
            xL = xM
            fL = fM
        else:
            xR = xM
        xM = float(xL + xR) / 2
        fM = f(xM)
        iteration_counter += 1
        if return_x_list:
            x_list.append(xM)
    if return_x_list:
        return x_list, iteration_counter
    else:
        return xM, iteration_counter


def rate(x, x_exact):
    """ Compute the convergence rate of the root finding method"""
    e = [abs(x_ - x_exact) for x_ in x]
    q = [log(e[n+1]/e[n])/log(e[n]/e[n-1])
         for n in range(1, len(e)-1, 1)]
    return q
