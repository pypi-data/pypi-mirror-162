import time
import numpy as np
import pyfracgen as pf
from matplotlib import pyplot as plt


def mandelbrot_example():

    xbound = (0.3602404434376143632361252444495 - 0.00000000000003,
              0.3602404434376143632361252444495 + 0.00000000000025)
    ybound = (-0.6413130610648031748603750151793 - 0.00000000000006,
              -0.6413130610648031748603750151793 + 0.00000000000013)

    start_time = time.time()

    mymap = pf.images.stack_cmaps(plt.cm.gist_gray, 50)

    man = pf.mandelbrot(xbound, ybound, pf.updates.power, width=4, height=3, maxiter=5000, dpi=300)
    pf.images.image(man, cmap=mymap, gamma=0.8)
    plt.savefig('example_images/mandelbrot_ex.png')

    print('calculation took %s seconds ' % np.round((time.time() - start_time), 3))


def julia_animation_example():

    start_time = time.time()

    c_vals = np.array([complex(i, 0.75) for i in np.linspace(0.05, 3.0, 100)])
    s = pf.julia_series(c_vals, (-1, 1), (-0.75, 1.25), pf.updates.magnetic_2, maxiter=300,
                        width=4, height=3, dpi=200)
    pf.images.save_animation(s, gamma=0.9, cmap=plt.cm.gist_ncar,
                             filename='example_images/julia_animation_ex')

    print('calculation took %s seconds ' % np.round((time.time() - start_time), 3))


def lyapunov_example():

    start_time = time.time()

    string = 'AAABA'
    xB = (2.60, 4.0)
    yB = (2.45, 4.0)

    im = pf.lyapunov(string, xB, yB, maxiter=80, dpi=300, width=4, height=3)
    pf.images.image(im, gamma=3.0, vert_exag=10000.0, cmap=plt.cm.gray)
    plt.savefig('example_images/lyapunov_ex.png')

    print('calculation took %s seconds ' % np.round((time.time() - start_time), 3))


def random_walk_example():

    start_time = time.time()

    basis = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    moves = pf.construct_moves(basis)
    M = pf.random_walk(moves, 5000000, width=4, height=3, depth=1, dpi=300, displacement=0.0,
                       tracking='temporal', bias=0)
    pf.images.random_walk_image(M, cmap=plt.cm.gist_yarg, gamma=1.0, single_color=False)
    plt.savefig('example_images/random_walk_ex.png')

    print('calculation took %s seconds ' % np.round((time.time() - start_time), 3))


def buddhabrot_example():  # this will take awhile

    xbound = (-1.75, 0.85)
    ybound = (-1.10, 1.10)
    
    start_time = time.time()

    cvals = pf.compute_cvals(1000000, xbound, ybound, pf.updates.power, width=4, height=3, dpi=100)

    bud0 = pf.buddhabrot(xbound, ybound, cvals, pf.updates.power, horizon=1.0E6, maxiter=100,
                         width=5, height=4, dpi=300)
    bud1 = pf.buddhabrot(xbound, ybound, cvals, pf.updates.power, horizon=1.0E6, maxiter=1000,
                         width=5, height=4, dpi=300)    
    bud2 = pf.buddhabrot(xbound, ybound, cvals, pf.updates.power, horizon=1.0E6, maxiter=10000,
                         width=5, height=4, dpi=300)
    
    pf.images.nebula_image(bud0, bud1, bud2, gamma=0.4)
    plt.savefig('example_images/buddhabrot_ex.png')

    print('calculation took %s seconds ' % np.round((time.time() - start_time), 3))


if __name__ == '__main__':

    mandelbrot_example()
    julia_animation_example()
    lyapunov_example()
    random_walk_example()
    # buddhabrot_example()
