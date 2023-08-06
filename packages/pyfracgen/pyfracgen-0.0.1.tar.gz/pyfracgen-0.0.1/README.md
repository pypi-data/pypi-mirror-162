## Authors

- Ryther Anderson

## Description
Python Fractal Generation is a package for making interesting/aesthetic fractal images quickly and 
(hopefully) easily. A multitude of unique fractals (from various views) can be generated using only a 
few functions. Each fractal generation function returns a result object containing an array of floats that can 
be converted into an image, the desired width/height in inches, and the number of pixels per inch.
This result object can be passed to various image creation functions that assign colors to the fractal 
array based on a colormap (or creates RGB channels from the array).

## Installation

pyfracgen can currently be installed from the following sources:

### Git
```
git clone https://github.com/rytheranderson/pyfracgen.git
cd pyfracgen
pip install .
```

### PyPi
```
pip install pyfracgen
```

## Example Images

All the package functions can be accessed from a single import:
```
import pyfracgen as pf
from matplotlib import pyplot as plt
```

### Mandelbrot Set
![](https://github.com/rytheranderson/pyfracgen/raw/main/example_images/mandelbrot_ex.png?raw=true)

Image produced with this code:

```
# x and y boundaries, x being the real part and y being the imaginary part in the complex plane
xbound = (0.3602404434376143632361252444495 - 0.00000000000003,
          0.3602404434376143632361252444495 + 0.00000000000025)
ybound = (-0.6413130610648031748603750151793 - 0.00000000000006,
          -0.6413130610648031748603750151793 + 0.00000000000013)

mymap = pf.images.stack_cmaps(plt.cm.gist_gray, 50)
man = pf.mandelbrot(xbound, ybound, pf.updates.power, width=4, height=3, maxiter=5000, dpi=300)
pf.images.image(man, cmap=mymap, gamma=0.8)
plt.savefig('example_images/mandelbrot_ex.png')
```

### Julia Set Animation
![](https://github.com/rytheranderson/pyfracgen/raw/main/example_images/julia_animation_ex.gif?raw=true)

Animation produced with this code:

```
c_vals = np.array([complex(i, 0.75) for i in np.linspace(0.05, 3.0, 100)])
s = pf.julia_series(c_vals, (-1, 1), (-0.75, 1.25), pf.updates.magnetic_2, maxiter=100,
                    width=4, height=3, dpi=200)
pf.images.save_animation(s, gamma=0.9, cmap=plt.cm.gist_ncar,
                         filename='example_images/julia_animation_ex')
```

### Markus-Lyapunov Fractal
![](https://github.com/rytheranderson/pyfracgen/raw/main/example_images/lyapunov_ex.png?raw=true)

Image produced with this code:

```
im = pf.lyapunov(string, xB, yB, maxiter=80, dpi=300, width=4, height=3)
pf.images.image(im, gamma=3.0, vert_exag=10000.0, cmap=plt.cm.gray)
plt.savefig('example_images/lyapunov_ex.png')
```

### Random Walk
![](https://github.com/rytheranderson/pyfracgen/raw/main/example_images/random_walk_ex.png?raw=true)

Image produced with this code:

```
basis = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
moves = pf.construct_moves(basis)
M = pf.random_walk(moves, 5000000, width=4, height=3, depth=1, dpi=300, displacement=0.0,
                   tracking='temporal', bias=0)
pf.images.random_walk_image(M, cmap=plt.cm.gist_yarg, gamma=1.0, single_color=False)
plt.savefig('example_images/random_walk_ex.png')
```

### Buddhabrot with Nebula Coloring
![](https://github.com/rytheranderson/pyfracgen/raw/main/example_images/buddhabrot_ex.png?raw=true)

Image produced with this code:

```
xbound = (-1.75, 0.85)
ybound = (-1.10, 1.10)

cvals = pf.compute_cvals(1000000, xbound, ybound, pf.updates.power, width=4, height=3, dpi=300)
bud0 = pf.buddhabrot(xbound, ybound, cvals, pf.updates.power, horizon=1.0E6, maxiter=100,
                     width=5, height=4, dpi=300)
bud1 = pf.buddhabrot(xbound, ybound, cvals, pf.updates.power, horizon=1.0E6, maxiter=1000,
                     width=5, height=4, dpi=300)    
bud2 = pf.buddhabrot(xbound, ybound, cvals, pf.updates.power, horizon=1.0E6, maxiter=10000,
                     width=5, height=4, dpi=300)

pf.images.nebula_image(bud0, bud1, bud2, gamma=0.4)
plt.savefig('example_images/buddhabrot_ex.png')
```

## Current Status
There are functions for Mandelbrot and Julia set generation, image and animation creation. There is
a function for Buddhabrot generation and a function for the "nebula" coloring of the Buddhabrot. 
There is a class for creating and visualizaing 2- and 3-dimensional random walks (with bias, if desired). 
The most recent addition is a function for generating Markus-Lyapunov fractals, with a special image function
for the "classic" blue/green coloring.
