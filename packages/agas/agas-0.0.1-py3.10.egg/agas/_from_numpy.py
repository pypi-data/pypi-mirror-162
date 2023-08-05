""""""
import inspect
import typing
import warnings

import numpy as np
import numpy.typing as npt

from agas import constants

__all__ = ['pair_from_array']

RETURN_FILTER_ERROR_STR = (
    f"return_filter must be one of {constants.RETURN_TYPE_OPTIONS} "
    f"or a float (0≤x<1)")


def pair_from_array(input_array,
                    similarity_function: typing.Callable,
                    divergence_function: typing.Callable,
                    similarity_weight: typing.Union[
                        float, int] = constants.DEFAULT_SIMILARITY_WEIGHT,
                    return_filter: typing.Union[
                        str, float, int] = constants.RETURN_FILTER_STR_FIRST,
                    return_matrix: bool = False):
    r"""
    Calculate the optimality score of each unique pair of rows in a 2D array.

    Optimality is such that when that the difference between two rows is minimal
    when each is aggregated using the `similarity_function` and maximal when
    each is aggregated using `divergence_function`.

    For elaborate description, see Notes below or the agas Tutorial.

    Parameters
    ----------
    input_array: array-like, shape (N, T)
        The data to be processed. Each row of N rows (the first axis, 0) is a 
        unique group\unit of values to be aggregated together (e.g., subjects
        from an experiment). Each column of T columns (the second axis, 1)
        represent the different observations within each group\unit (e.g.,
        across timestamps).
    similarity_function, divergence_function: Callable
        Each of these two functions is used to aggregate groups of observations
        within `input_array` (i.e., along the columns axis). The absoluet
        differences between any pair out of the aggregated values for each
        group. Pairs with minimal normalized absolute differences on
        `similarity_function` and maximal normalized absolute differences on
        `divergence_function` are scored as more optimal, while pairs with
        maximal normalized absolute differences on `similarity_function` and
        minimal normalized absolute differences on `divergence_function` are
        scored as least optimal.
    similarity_weight: int, float, default=0.5
        Used to weight the `similarity_function` function in weighted average of
        aggragted diffrecnces. Must be between 0 and 1, inclusive. The weight of
        `divergence_function` will be 1 - `maximize weight`.
    return_filter: typing.Union[str, Int, Float, ], default 'first'
        If string must be one of {'first', 'top', 'bottom', 'last', 'all'}:
            - 'first', returns the indices the optimal pair.
            - 'top' return all pairs equivilent with the most optimal pair.
            - 'last' returns the least optimal pair.
            - 'bottom' returns all pairs eqivilent with the least optimal pair.
            - 'all' returns all pairs sorted by optimality (descending).
        If int or float
            - Must be in the range of [0, 1] (inclusive). Returns all pairs
            up to the input value, including. i.e., 0 is equivilent to 'top',
            1 is equivilent to 'all'.
    return_matrix: bool: optional, default False
        if return_matrix is True, returns the matrix of optimality scores,
        regardless of `return_filter` value. If False, follows the specification
        under return_filter.

    Returns
    -------
    If return_matrix is False (default), returns
        indices : npt.NDArray
            A 2D array, column-axis size is always 2. Each row contains the row-indices of a pair from the original array.
                - If `return_filter` is 'first' or 'last', then `indices` is of length 1 as only a single pair is returened.
                - If `return_filter` is 'all', then `indices` is of length N(N-1)/2 as all pairs are returned.
                - If `return_filter` 'top', 'bottom' or numeric then shape is subject to the data.
        scores : npt.NDArray
            A 1D array of the optimality scores corresponding to the indices
            found in `indices`.
    If return_matrix is True, returns a 2d array of size [N(N-1)/2, N(N-1)/2],
    containing the optimality scores (ranging from 0 to 1 , inclusive), between
    each pair of row-indice pairs. The matrix diagonal is filled with NaNs.

    Notes
    -----
    Given a matrix of size N X T, for each set of {ri, rj} out of
    the N * (N - 1) / 2 unique pairs of rows, a set differences {dij1, dij2}
    is calculated by applying two aggregation functions {f1, f2} to r1 and r2
    separately (i.e., dij1 = \|f1(ri) - f1(rj)\|, d2 = \|f2(ri) - f2(rj)\|).

    Each of dijx in {dij1, dij2} is scaled between 0 and 1, relative to the
    set of absolute difference between pairs of rows, obtained using function
    fx.

    f1 and f2 correspond to the arguments `similarity_function` and
    `divergence_function`, respectively. f1 rewards minimal differences
    between pairs and penalizes maximal differences. d2 is multiplied by -1 to
    penalize for minimal differences and reward maximal differences between
    pairs. w1 and w2 correspond to `similarity_weight` and
    `1 - similarity_weight`, respectively.

    The optimality score oij is calcualted as a weighted sum
    dij1 * w1 - dij2 * w2, then scaled again between 0 and 1, relative to
    the set of all other scores.

    Examples
    --------
    Find an optimal pair of sub-arrays which have the most similar standard
    deviation (relative to all other sub-arrays), and the most different mean
    (relative to all other sub-arrays).

    .. doctest::

    >>> a = np.vstack([[0, 0.5], [0.5, 0.5], [5, 5], [4, 10]])
    >>> indices, scores = agas.pair_from_array(a, similarity_function=np.std,
    ...    divergence_function=np.mean)
    >>> indices, a[indices]
    (array([1, 2], dtype=int64), array([[0.5, 0.5],
           [5. , 5. ]]))

    The pair of rows [[0.5, 0.5], [5, 5]] out of the input statisfies the lowest
    absolute difference in standard deviation (i.e., 0) and the largest
    absolute difference in mean values (4.5). The score of the most optimal
    pair is 0.

    >>> scores
    array([0.])

    Optimality scores are more useful when asking agas.pair_from_array for a
    subset of pairs. For example, if we want to get the optimality scores of all
    pairs, we can set return_filter argument (default, 'first') to 'all'.

    Printing the pairs of rows from `a`, sorted by optimality (0 is most optimal
    1 is least optimal).

    >>> indices, scores = agas.pair_from_array(a, similarity_function=np.std,
    ...         divergence_function=np.mean, return_filter='all')
    >>> print(*list(zip(indices.tolist(), scores.round(2))), sep='\n')
    ([1, 2], 0.0)
    ([0, 2], 0.03)
    ([0, 3], 0.41)
    ([1, 3], 0.5)
    ([0, 1], 0.53)
    ([2, 3], 1.0)

    The `return_filter` argument can also be specified using a float, selecting
    pairs which are up to a specific threshold (including).

    >>> indices, scores = agas.pair_from_array(a, similarity_function=np.std,
    ...          divergence_function=np.mean, return_filter=0.5)
    >>> print(*list(zip(indices.tolist(), scores.round(2))), sep='\n')
    ([1, 2], 0.0)
    ([0, 2], 0.03)
    ([0, 3], 0.41)
    ([1, 3], 0.5)


    Control the weight of the function maximizing similarity in the calculation
    of optimality scores, using the `similarity_weight` keyword argument. Here
    we prioritize differences in means over lack of differences in variance,
    by decreasing similarity_weight from 0.5 (default) to 0.2. This returns a
    a differnet pair then before.

    >>> agas.pair_from_array(a, similarity_function=np.std,
    ...         divergence_function=np.mean, similarity_weight=.2)
    (array([0, 3], dtype=int64), array([0.]))

    """

    if not isinstance(input_array, np.ndarray):
        try:
            input_array = np.array(input_array)
            if input_array.ndim != 2:
                raise ValueError("input_array must be 2-dimensional")
        except TypeError as e:
            raise RuntimeError("input_array must be a 2-dimensional array or "
                               "an object that can be converted to a 2-dimensional"
                               " array")

    if input_array.size == 0:
        raise RuntimeError("input_array must not be empty")

    if input_array.shape[0] == 1:
        raise RuntimeError(
            "input_array must have more than one element on the samples"
            f" axis. If trying to pass an input_array containing {input_array.shape[1]} series"
            "and 1 sample per series, (e.g., shape == [2, 1], consider transposing the"
            "input_array (input_array.T).")

    if (not isinstance(similarity_function, typing.Callable)
    ) or not isinstance(divergence_function, typing.Callable):
        raise TypeError(
            "Both `similarity_function` and `divergence_function` must be callables,"
            f" but received {type(similarity_function)} and "
            f"{type(divergence_function)}, respectively")

    if return_filter not in constants.RETURN_TYPE_OPTIONS:
        if isinstance(return_filter, str):
            raise ValueError(
                RETURN_FILTER_ERROR_STR + f"; received {return_filter}")
        if isinstance(return_filter, float) or isinstance(return_filter, int):
            if not 0 <= return_filter <= 1.0:
                raise ValueError(
                    RETURN_FILTER_ERROR_STR + f"; received {return_filter}")
        else:
            raise TypeError(RETURN_FILTER_ERROR_STR +
                            f" ; received {type(return_filter)}")

    if isinstance(similarity_weight, float) or isinstance(similarity_weight,
                                                          int):
        if not ((0 <= similarity_weight) & (similarity_weight <= 1)):
            raise ValueError("similarity_weight must a float or an int be "
                             "between 0 and 1 (0≤x<1)")
    else:
        raise TypeError("similarity_weight must be between 0 and 1 (0≤x<1), "
                        f"received {type(similarity_weight)}")

    if not isinstance(return_matrix, bool):
        raise TypeError("return_matrix must be a boolean, received  "
                        f"{type(return_matrix)}")

    divergence_weight = 1 - similarity_weight

    input_array = input_array.copy()

    similarity_mat = _calc_differences(input_array, similarity_function)
    dissimilarity_mat = _calc_differences(input_array, divergence_function)

    optimized_differences = _calc_optimality_scores(
        similarity_mat, dissimilarity_mat, similarity_weight, divergence_weight)

    if return_matrix:
        return optimized_differences


    return _form_return_result(*_find_optimal_pairs(optimized_differences),
                               return_filter)


def _apply_func(array, func):
    """Apply the given function to the input array along the second dimension
    (1).

    Assumes that if the function does not receive the axis positional or keyword
    parameter 'axis' it is predfined (e.g., using partial).
    """

    sig = inspect.signature(func)
    args = [p.name for p in sig.parameters.values() if
            p.kind == p.POSITIONAL_OR_KEYWORD]
    if 'axis' in args:
        return func(array, axis=1)
    else:
        # It is very likely that the function will be called along first axis
        # therefore we need to transpose the array prior to applying the function
        return func(array.T)


def _calc_differences(array: npt.NDArray, func: typing.Callable):
    aggregated_array = _apply_func(array, func)
    if (np.any(np.isnan(aggregated_array))):
        warnings.warn(f"The result of aggregating the input scores using the "
                      f"function {func.__name__} resulted in "
                      f"{np.isnan(aggregated_array).sum()} NaN scores.",
                      RuntimeWarning)
    if (np.all(np.isnan(aggregated_array))):
        raise ValueError(
            "Aggregating the input scores using the {func.__name__}"
            f" function resulted in all NaN scores.")

    return _get_diffs_matrix(aggregated_array)


def _get_diffs_matrix(array: npt.NDArray):
    """
    Return a matrix of the absolute difference between each element and all
    other elements in the input_array.

    :param array: npt.NDArray of size 1 X n.
    :return: npt.NDArray of size n X n.
    """

    # After taking the absolute differences, cast the differences' matrix as
    # float, given we need nans on the diagonal
    diffs_mat = np.abs(np.subtract.outer(array, array), dtype=float)
    # We can ignore the difference between each sample and itself
    np.fill_diagonal(diffs_mat, np.nan)
    return diffs_mat


def _normalize(a: npt.NDArray):
    """Normalize an input_array to the range between 0 and 1.

    :param a : npt.NDArray
        A 1D input_array to normalize.

    :return:
        The normalized input_array, between 0 and 1.
    """
    return (a - np.nanmin(a)) / (np.nanmax(a) - np.nanmin(a))


def _calc_optimality_scores(maximize_similarity_array,
                            minimize_similarity_array,
                            maximize_weight, minimize_weight):
    """
    Calculates the weighted average of the two similarity arrays, based on their
    respective weights.

    :param maximize_similarity_array:
    :param minimize_similarity_array:
    :param maximize_weight: Float in the range [0.0, 1.0]
    :param minimize_weight: Float in the range [0.0, 1.0],
        Complementary of `divergence_function`.
    :return:

    """
    similarity = _normalize(maximize_similarity_array) * maximize_weight
    dissimilarity = - 1 * _normalize(
        minimize_similarity_array) * minimize_weight
    return _normalize(
        similarity + dissimilarity)  # np.nansum([similarity, dissimilarity], axis=[0, 1])


def _find_optimal_pairs(optimized_differences):
    # Remove repeated pairs from the differences' matrix, by asigning the lower
    #  triangle of the array to NaNs.
    optimized_differences[np.tril_indices(
        optimized_differences.shape[0], -1)] = np.nan

    not_nan_indices = ~np.isnan(optimized_differences)

    # Find all indices of scores which are not NaNs, hence the first occurrence of
    #  of a pair
    indices = np.argwhere(not_nan_indices)
    scores = optimized_differences[not_nan_indices]

    # Sort the indices and scores by the scores, from most optimal (0) to least
    # (1)
    ordered_values = scores.argsort()
    indices = indices[ordered_values]
    scores = scores[ordered_values]

    return scores, indices


def _form_return_result(scores, indices, return_filter):
    if return_filter == constants.RETURN_FILTER_STR_FIRST:
        return (indices[0], scores[[0]])
    elif return_filter == constants.RETURN_FILTER_STR_TOP:
        return indices[scores == 0], scores[scores == 0]
    elif return_filter == constants.RETURN_FILTER_STR_LAST:
        return (indices[-1], scores[[-1]])
    elif return_filter == constants.RETURN_FILTER_STR_BOTTOM:
        return indices[scores == 1], scores[scores == 1]
    elif return_filter == constants.RETURN_FILTER_STR_ALL:
        return indices, scores
    else:  # A float
        return indices[scores <= return_filter], scores[scores <= return_filter]
