import numpy as np
from numpy import array
from numpy.random import randint
from itertools import combinations
from numba import jit

if __package__ is None or __package__ == '':
    from fractal_result import fractal_result
else:
    from .fractal_result import fractal_result


def construct_moves(basis):

    basis = np.r_[basis, -1*basis, [array([0, 0, 0])]]
    moves = np.unique(array([b0 + b1 for b0, b1 in combinations(basis, 2)]), axis=0)
    moves = array([m for m in moves if np.any(m)])

    return moves


@jit
def _random_walk(moves, niter, width=5, height=5, depth=1, dpi=100,
                 tracking='visitation', displacement=0.0, bias=0):

    """
        A 3D random walk on a lattice, points can be colored by the number
        of times visited or by the step number (time)
    """

    lattice = np.zeros((int(height*dpi), int(width*dpi), int(depth)), dtype=np.float32)
    shape = array([height*dpi, width*dpi, depth])
    nmoves = len(moves)
    
    l0, l1, l2 = shape
    indices = array([height*dpi, width*dpi, depth])/2.0 + displacement*shape

    for iteration in range(niter):

        move = moves[randint(0, nmoves-bias)]
        indices += move
        i, j, k = int(indices[0] % l0), int(indices[1] % l1), int(indices[2] % l2)

        if tracking == 'visitation':
            lattice[i, j, k] += 1.0
        elif tracking == 'temporal':
            if lattice[i, j, k] == 0.0:
                lattice[i, j, k] += iteration

    lattice /= np.amax(lattice)

    return (lattice, width, height, dpi)


def random_walk(moves, niter, width=5, height=5, depth=1, dpi=100,
                tracking='visitation', displacement=0.0, bias=0):

    res = _random_walk(moves, niter, width=width, height=height, depth=depth, dpi=dpi,
                       tracking=tracking, displacement=displacement, bias=bias)

    return fractal_result(*res)
