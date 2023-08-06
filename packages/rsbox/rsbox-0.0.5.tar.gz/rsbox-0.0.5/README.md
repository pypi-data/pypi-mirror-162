# `rsbox`: Utility Toolbox

([Github](https://github.com/rosikand/rsbox) | [PyPI](https://pypi.org/project/rsbox))

A toolbox of utility functions [I](http://rosikand.github.io/) commonly use when programming in Python.

The full API consists of importable functions from modules located in `src/rsbox/`. Functions are documented via comment blocks under the function header. 

## Installation 

```
$ pip install rsbox
```

## Modules 

The modules are located in `src/rsbox/`

- `ml.py`: machine learning programming utilities. 
- `misc.py`: misc. utilities. 


## Version changelog 

### `0.0.5`

- Improved documentation. 
- Added `plot` function in `ml.py` and removed redundant `plot_tensor` function. `plot_np_img` was kept for longevity purposes. 
- Added `misc.timestamp`, `misc.pickle` and `misc.unpickle`. 

### `0.0.4`

- Changed `ml_utils.py` to `ml.py` for ease-of-use. 

### `0.0.3`

- Added more documentation.  

### `0.0.2`

- Removed Jax functions to enable use of `rsbox` on m1 without needing to build Jax from source. 

### `0.0.1`

- Initial module upload. Contains `ml_utils.py`. 
