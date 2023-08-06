import numpy as np
from numpy import log
from numba import jit

if __package__ is None or __package__ == '':
    from fractal_result import fractal_result
else:
    from .fractal_result import fractal_result


@jit
def _mandelbrot(xbound, ybound, update_func, width=5, height=5,
                dpi=100, maxiter=100, horizon=2.0**40, log_smooth=True):

    """
        function for producing Mandelbrot array
    """

    xmin, xmax = [float(xbound[0]), float(xbound[1])]
    ymin, ymax = [float(ybound[0]), float(ybound[1])]

    nx = width*dpi
    ny = height*dpi

    xvals = np.array([xmin + i*(xmax - xmin)/(nx) for i in range(nx)], dtype=np.float64)
    yvals = np.array([ymin + i*(ymax - ymin)/(ny) for i in range(ny)], dtype=np.float64)

    lattice = np.zeros((int(nx), int(ny)), dtype=np.float64)
    log_horizon = log(log(horizon))/log(2)

    for i in range(len(xvals)):
        for j in range(len(yvals)):

            c = xvals[i] + 1j * yvals[j]
            z = c

            for iteration in range(maxiter):

                az = abs(z)

                if az > horizon:
                    if log_smooth:
                        lattice[i, j] = iteration - log(log(az))/log(2) + log_horizon
                    else:
                        lattice[i, j] = iteration
                    break

                z = update_func(z, c)

    return (lattice.T, width, height, dpi)


def mandelbrot(xbound, ybound, update_func, width=5, height=5,
               dpi=100, maxiter=100, horizon=2.0**40, log_smooth=True):

    res = _mandelbrot(xbound, ybound, update_func, width=width, height=height,
                      dpi=dpi, maxiter=maxiter, horizon=horizon, log_smooth=log_smooth)

    return fractal_result(*res)
