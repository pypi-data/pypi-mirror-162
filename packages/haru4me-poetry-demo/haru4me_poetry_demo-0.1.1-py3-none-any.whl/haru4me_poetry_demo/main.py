import numpy as np


def diff(arr: np.ndarray, h: float) -> np.ndarray:
    """Numerical differential method.

    Parameters
    ----------
    arr: np.ndarray
        Input array will be differentiated
    h: float
        Step function

    Returns
    -------
    np.ndarray

    """
    return (arr[2:] - arr[:-2]) / 2
