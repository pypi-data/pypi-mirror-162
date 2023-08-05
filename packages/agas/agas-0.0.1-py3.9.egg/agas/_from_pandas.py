import typing

import numpy as np
import pandas as pd

from agas import constants
from agas import _from_numpy

__all__ = ['pair_from_wide_df']


def pair_from_wide_df(df: pd.DataFrame,
                      similarity_function: typing.Callable,
                      divergence_function: typing.Callable,
                      similarity_weight: typing.Union[float, int] = 0.5,
                      return_filter: typing.Union[
                          str, float, int] = constants.RETURN_FILTER_STR_FIRST,
                      values_columns: typing.Union[
                          typing.Tuple, typing.List, np.ndarray] = None,
                      return_matrix: bool = False
                      ):
    """
    Calculate the optimality score of each unique pair of rows in a
    wide-format dataframe.

    Optimality is such that when that the difference between two rows is minimal
    when each is aggregated using the `similarity_function` and maximal when
    each is aggregated using `divergence_function`.

    For an explenation on the optimization process See the Notes section
    in the docstring of :py:func:`pair_from_array <pair_from_array>`.


    Parameters
    ----------
    df: pd.DataFrame
        A wide (unstacked, pivoted) dataframe, where scores are stored in
        columns and unique units are stored in rows.
    similarity_function, divergence_function: Callable
        Each of these two functions is used to aggregate groups of observations
        within `input_array` (i.e., along the columns axis). The absoluet
        differences between any pair out of the aggregated values for each group
        . Pairs with minimal normalized absolute differences on
        `similarity_function` and maximal normalized absolute differences on
        `divergence_function` are scored as more optimal, while pairs with
        maximal normalized absolute differences on
        `similarity_function` and minimal normalized absolute differences on
        `divergence_function` are scored as least optimal.
    similarity_weight: int, float, default=0.5
        Used to weight the `similarity_function` function in weighted average of
        aggragted diffrecnces. Must be between 0 and 1, inclusive. The weight of
        `divergence_function` will be 1 - `maximize weight`.
    return_filter: typing.Union[str, int, float], default 'first'
        If string must be one of {'first', 'top', 'bottom', 'last', 'all'}:
            - 'first', returns the indices the optimal pair.
            - 'top' return all pairs equivilent with the most optimal pair.
            - 'last' returns the least optimal pair.
            - 'bottom' returns all pairs eqivilent with the least optimal pair.
            - 'all' returns all pairs sorted by optimality (descending).
        If int or float
            - Must be in the range of [0, 1] (inclusive). Returns all pairs up
              to the input value, including. i.e., 0 is equivilent to 'top',
              1 is equivilent to 'all'.
    return_matrix: bool: optional, default False
        if return_matrix is True, returns the matrix of optimality scores,
        regardless of `return_filter` value. If False, follows the specification
        under return_filter.
    values_columns: array-like, Default None
        List, Tuple or Array of the column names of the scores to aggregate. If
        None, assumes all columns should be aggregated.

    Returns
    -------
    If return_matrix is False (default)
        - If `return_filter` is 'indices', returns the indices of the
        optimal pair of rows out of `df` (e.g., df.iloc[optimal, :]).
        - If `return_filter` is 'scores' returns a dataframe composed of the
        optimal pair of rows out of `df`.
    If return_matrix is True, returns a 2d array of size [N(N-1)/2, N(N-1)/2],
    containing the optimality scores (ranging from 0 to 1 , inclusive), between
    each pair of row-indice pairs. The matrix diagonal is filled with NaNs.

    See Also
    --------
    :func:`~agas.pair_from_array`.

    Notes
    -----
    Currently Agas doesn't allow usage of string function names for aggregation,
    unlike what can be done using pandas.

    Examples
    -----

    .. testsetup:: *
       import pandas as pd
       import numpy as np
       import agas



    .. doctest::

    Setting up a small dataset of angle readings from fictitious sensors,
    collected in 3-hour intervals.

    >>> data = np.array([(0, 2, 1), (10, 11, 100), (120, 150, 179)])
    >>> df = pd.DataFrame(data, columns=['3PM', '6PM', '9PM'],
    ...             index=['Yaw', 'Pitch', 'Roll'])
    >>> df.agg([np.std, 'sum'], axis=1)
             std    sum
    Yaw     1.00    3.0
    Pitch  51.68  121.0
    Roll   29.50  449.0

    Yaw and Roll display the highest normalized similarity in mean value,
    and the lowest normalized similarity in sum value.

    >>> indices, scores = agas.pair_from_wide_df(df, np.std, np.sum)
    >>> df.iloc[indices, :]
          3PM  6PM  9PM
    Yaw     0    2    1
    Roll  120  150  179

    Giving standard deviation a heavier weight, leads to Pitch and Roll
    selected as the optimal value.

    >>> indices, scores = agas.pair_from_wide_df(df, np.std, np.sum, 0.8)
    >>> df.iloc[indices, :]
           3PM  6PM  9PM
    Pitch   10   11  100
    Roll   120  150  179

    Prioritizing small differences between sums, and large differences in
    variance:

    >>> indices, scores = agas.pair_from_wide_df(df, np.sum, np.std)
    >>> df.iloc[indices, :]
           3PM  6PM  9PM
    Yaw      0    2    1
    Pitch   10   11  100
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f'df must be a pandas DataFrame, received {type(df)}')
    else:
        if df.shape[0] < 2:  # Less than 2 rows
            raise ValueError(f'df must contain at least two rows')

    if values_columns is not None:
        _df = df.loc[:, values_columns]
    else:
        _df = df.copy()

    res = _from_numpy.pair_from_array(
        _df.values, similarity_function, divergence_function,
        similarity_weight, return_filter)

    return res
