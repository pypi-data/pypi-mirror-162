import numpy as np
import pytest

import agas

TOY_DATA = np.vstack(
    [[0, 1], [2, 3], [0, 8]])

EXAMPLE_DATA = np.vstack((np.zeros(10), np.ones(10) * 10, np.arange(5, 15, )))

SIM_RNG = np.random.RandomState(2022)
SIM_MEANS = np.array((10, 12, 0, -2))
SIM_SDS = np.array((1, 3, 1, 7))
N = 1000
SIM_DATA = np.vstack(
    [SIM_RNG.normal(m, sd, N) for (m, sd) in zip(SIM_MEANS, SIM_SDS)])


def test__apply_func():
    a = np.array([[0, 1], [2, 3]])
    a_sum = np.array([1, 5])

    assert np.array_equal(agas._from_numpy._apply_func(a, sum), a_sum)
    assert np.array_equal(agas._from_numpy._apply_func(a, np.sum), a_sum)

    with pytest.raises(AttributeError):
        assert np.array_equal(agas._from_numpy._apply_func(a.tolist(),
                                                           sum), a_sum)


def test__get_diffs_matrix():
    a = np.array([1, 2, 3])
    expected_return = np.array([[np.nan, 1, 2],
                                [1, np.nan, 1],
                                [2, 1, np.nan]])

    assert np.array_equal(agas._from_numpy._get_diffs_matrix(a),
                          expected_return, equal_nan=True)


def test__normalize():
    np.array_equal(agas._from_numpy._normalize(np.array([1, 2])),
                   np.array([0, 1]))
    np.array_equal(agas._from_numpy._normalize(np.array([-100, 100])),
                   np.array([0, 1]))
    np.array_equal(agas._from_numpy._normalize(np.array([0, 10, 1000])),
                   np.array([0, 0.01, 1]))


def test__optimize():
    np.array_equal(agas.pair_from_array(EXAMPLE_DATA, np.std, np.median, 0.1),
                   agas.pair_from_array(EXAMPLE_DATA, np.std, np.median, 0.9),
                   )


def test__normalize_differences():
    def mean_with_some_nans(a: np.ndarray):
        res = np.mean(a, axis=1)
        res[[0, -1]] = np.nan
        return res

    def return_all_nans(a: np.ndarray):
        res = np.empty(a.shape[0])
        res.fill(np.nan)
        return res

    with pytest.raises(ValueError):
        agas.pair_from_array(EXAMPLE_DATA,
                             similarity_function=mean_with_some_nans,
                             divergence_function=np.std, )
        agas.pair_from_array(EXAMPLE_DATA,
                             similarity_function=mean_with_some_nans,
                             divergence_function=mean_with_some_nans, )

    with pytest.raises(ValueError):
        agas.pair_from_array(EXAMPLE_DATA,
                             similarity_function=return_all_nans,
                             divergence_function=np.std, )
        agas.pair_from_array(EXAMPLE_DATA,
                             similarity_function=return_all_nans,
                             divergence_function=return_all_nans, )

def test_return_matrix_argument():

    with pytest.raises(TypeError):
        agas.pair_from_array(EXAMPLE_DATA,
                             similarity_function=np.mean,
                             divergence_function=np.std,
                             return_matrix=None)
        agas.pair_from_array(EXAMPLE_DATA,
                             similarity_function=np.mean,
                             divergence_function=np.std,
                             return_matrix=1)
        agas.pair_from_array(EXAMPLE_DATA,
                             similarity_function=np.mean,
                             divergence_function=np.std,
                             return_matrix=0.0)

