from numpy import linspace, sum


def trapezoidal_vec(f, a, b, n):
    r"""
    Composite trapezoidal method for integral numerical calculation.

    .. math ::
        \int_{a}^{b} f(x) dx \approx h \left[ \frac{1}{2} f(x_0) + \sum_{i=1}^{n-1} f(x_i) + \frac{1}{2} f(x_n) \right]

    :param float f: function.
    :param float a: Lower interval bound.
    :param float b: Upper interval bound.
    :param int n: Number of subdivision.
    """
    h = float(b - a) / n
    x = linspace(a, b, n+1)
    s = sum(f(x)) - 0.5*f(a) - 0.5*f(b)
    return h*s


def midpoint_vec(f, a, b, n):
    r"""
    Composite trapezoidal method for integral numerical calculation.

    .. math ::
        \int_{a}^{b} f(x) dx \approx h \sum_{i=0}^{n-1} f(x_i)

        where, x_i = (a + \frac{h}{2} + ih

    :param f: function.
    :param float a: Lower interval bound.
    :param float b: Upper interval bound.
    :param int n: Number of subdivision.
    """
    h = float(b - a) / n
    x = linspace(a + h/2, b - h/2, n)
    return h * sum(f(x))
