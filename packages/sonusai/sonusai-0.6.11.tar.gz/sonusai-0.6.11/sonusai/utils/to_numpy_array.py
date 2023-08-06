import multiprocessing as mp

import numpy as np


def to_numpy_array(arr: mp.Array, dtype=None) -> np.ndarray:
    """Convert multiprocessing array to numpy array"""
    return np.frombuffer(arr.get_obj(), dtype=dtype)
