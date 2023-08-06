from numpy import linspace, zeros, asarray


def ode_FE(f, U0, dt, T):
    r"""
    Forward Euler method (forward difference) to compute the solution of first order ODE

    .. math ::
        u' = f(u, t)

        Forward Euler scheme

        u^{n+1} = u^n + \Delta t f(u^n, t_n)

    :param f: Function
    :param list[int] U0: Initial value
    :param float dt: Time step
    :param float T: Final time
    """

    Nt = int(round(float(T)/dt))
    u = zeros(Nt+1)
    t = linspace(0, Nt*dt, len(u))
    u[0] = U0
    for n in range(Nt):
        u[n+1] = u[n] + dt*f(u[n], t[n])

    return u, t


def ode_system_FE(f, U0, dt, T):
    """
    Forward Euler method to compute the solution of system of first order ODE

    :param f: Array of functions
    :param float U0: Initial value
    :param float dt: Time step
    :param float T: Final time
    """
    Nt = int(round(float(T)/dt))
    f_ = lambda u, t: asarray(f(u, t))  # convert user function in array
    u = zeros((Nt+1, len(U0)))
    t = linspace(0, Nt*dt, len(u))
    u[0] = U0
    for n in range(Nt):
        u[n+1] = u[n] + dt*f_(u[n], t[n])
    return u, t


def ode_EulerCromer(f, s, F, m, T, U0, V0, dt):
    r"""
    Semi-implicit Euler or Euler-Cromer method to compute the solution of second order ODE
    (Forward difference for the first equation and backward difference for the second equation)

    .. math ::
            mu'' + f(u') + s(u) = F(t)

            Euler-Cromer scheme

            v^{n+1} = v^n + \frac{\Delta t}{m}(f(t_n) - s(u^n) - f(v^n))

            u^{n+1} = u^n + \Delta t v^{n+1}

    :param f: Function - Damping force
    :param s: Function - Elastic force
    :param F: Function - External force
    :param float m: Mass
    :param float T: Final time
    :param float U0: Initial value for u
    :param float V0: Initial value for u'
    :param float dt: Time step
    """
    Nt = int(round(T/dt))
    t = linspace(0, Nt*dt, Nt+1)

    u = zeros(Nt+1)
    v = zeros(Nt+1)

    u[0] = U0
    v[0] = V0

    for n in range(Nt):
        v[n+1] = v[n] + dt*(1./m)*(F(t[n]) - f(v[n]) - s(u[n]))
        u[n+1] = u[n] + dt*v[n+1]
    return u, v, t


def ode_RK2(X0, omega, dt, T):
    r"""
    2nd-order Rugge-Kutta method (RK2) to compute the solution of second order ODE
    of oscillating systems (Centered finite difference)

    .. math ::
        u^\star = u^n + \Delta t f(u^n, t_n)

        u^{n+1} = u^n + \frac{1}{2}(f(u^n, t_n) + f(u^\star, t_{n+1})

    :param float X0: Initial value for u
    :param float omega: Damping factor
    :param float dt: Time step
    :param float T: Final time
    """
    Nt = int(round(T / dt))
    u = zeros(Nt + 1)
    v = zeros(Nt + 1)
    t = linspace(0, Nt * dt, Nt + 1)

    # Initial condition
    u[0] = X0
    v[0] = 0

    # Step equations forward in time
    for n in range(Nt):
        u_star = u[n] + dt * v[n]
        v_star = v[n] - dt * omega ** 2 * u[n]
        u[n + 1] = u[n] + 0.5 * dt * (v[n] + v_star)
        v[n + 1] = v[n] - 0.5 * dt * omega ** 2 * (u[n] + u_star)
    return u, v, t


def ode_RK4():
    r"""
    4th-order Rugge-Kutta method to compute the solution of first order ODE
    (Combination of forward, backward and central difference schemes)

    .. math ::
        u^{n+1} = u^n + \frac{\Delta t}{6}(f^n + 2*\hat{f}^{n+1/2} + 2*\tilde{f}^{n+1/2} + \overline{f}^{n+1}

        where

        \hat{f}^{n+1/2} = f(u^n + \frac{1}{2}\Delta t f^n, t_{n+1/2})

        \tilde{f}^{n+1/2} = f(u^n + \frac{1}{2}\Delta t \hat{f}^{n+1/2}, t_{n+1/2})

        \overline{f}^{n+1} = f(u^n + \frac{1}{2}\Delta t \tilde{f}^{n+1/2}, t_{n+1})
    """
    #TODO


def ode_Stormer(U0, omega, dt, T):
    r"""
    Stormer's method to compute the solution of second order ODE of oscillatory systems

    .. math ::
        u'' + \omega^2 u = 0

        u'' \approx \frac{u^{n+1} -2u^n + u^{n-1}}{\Delta t^2}

        u'(0) \approx \frac{u^1 - u^{-1}}{2 \Delta t}

        Stormer scheme

        u^{n+1} = 2*u^n - u^{n-1} - \Delta t^2 * \omega^2 * u^n

    :param float U0: Initial value for u
    :param float omega: Damping factor
    :param float dt: Time step
    :param float T: Final time
    """
    dt = float(dt)
    Nt = int(round(T/dt))
    u = zeros(Nt+1)
    t = linspace(0, Nt*dt, Nt+1)

    u[0] = U0
    u[1] = u[0] - 0.5*dt**2*omega**2*u[0]
    for n in range(1, Nt):
        u[n+1] = 2*u[n] - u[n-1] - dt**2*omega**2*u[n]
    return u, t
