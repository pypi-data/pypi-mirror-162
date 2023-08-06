import numpy as np
from numba import jit

if __package__ is None or __package__ == '':
    from fractal_result import fractal_result
else:
    from .fractal_result import fractal_result


@jit
def _lyapunov(string, xbound, ybound, maxiter=100, width=3, height=3, dpi=100):

    """
        returns a Lyupanov fractal according to the proved string (e.g. 'ABAA')
    """

    length = len(string)

    xmin, xmax = [float(xbound[0]), float(xbound[1])]
    ymin, ymax = [float(ybound[0]), float(ybound[1])]
    nx = width*dpi
    ny = height*dpi

    xvals = np.array([xmin + i*(xmax - xmin)/(nx) for i in range(nx)], dtype=np.float64)
    yvals = np.array([ymin + i*(ymax - ymin)/(ny) for i in range(ny)], dtype=np.float64)

    lattice = np.zeros((int(nx), int(ny)), dtype=np.float64)

    for i in range(len(xvals)):
        for j in range(len(yvals)):

            count = 0
            x = 0.5
            lamd = 0.0

            xv = xvals[j]
            yv = xvals[i]

            for iteration in range(maxiter):

                S = string[count % length]
                if S == 'A':
                    rn = xv
                else:
                    rn = yv
                count += 1

                x = (rn*x)*(1-x)
                lamd += np.log(np.abs(rn*(1-(2*x))))
                
            lattice[i, j] += lamd
            lamd /= maxiter

    return (lattice.T, width, height, dpi)


def lyapunov(string, xbound, ybound, maxiter=100, width=3, height=3, dpi=100):

    res = _lyapunov(string, xbound, ybound, maxiter=maxiter,
                    width=width, height=height, dpi=dpi)

    return fractal_result(*res)
