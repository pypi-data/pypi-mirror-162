import functools

import numpy as np
import pytest

import agas
from agas.constants import RETURN_FILTER_STR_FIRST, RETURN_FILTER_STR_LAST

TOY_DATA = np.vstack(
    [[0, 1], [2, 3], [0, 8]])

EXAMPLE_DATA = np.vstack((np.zeros(10), np.ones(10) * 10, np.arange(5, 15, )))

SIM_RNG = np.random.RandomState(2022)
SIM_MEANS = np.array((10, 12, 0, -2))
SIM_SDS = np.array((1, 3, 1, 7))
N = 1000
SIM_DATA = np.vstack(
    [SIM_RNG.normal(m, sd, N) for (m, sd) in zip(SIM_MEANS, SIM_SDS)])


def test_toy_data_sanity_check():
    assert np.array_equal(
        agas.pair_from_array(TOY_DATA, np.mean, np.std, 0, 'last')[0],
        agas.pair_from_array(TOY_DATA, np.std, np.mean, 1, 'first')[0]
    )


def test_toy_data_function_order():
    assert np.array_equal(
        agas.pair_from_array(TOY_DATA, np.std, np.mean, 0.5)[0],
        (0, 1)
    )

    assert np.array_equal(
        agas.pair_from_array(TOY_DATA, np.mean, np.std, 0.5)[0],
        (1, 2)
    )


@pytest.mark.parametrize('return_filter',
                         [RETURN_FILTER_STR_FIRST, RETURN_FILTER_STR_LAST])
def test_example_data_first_first_last(return_filter):
    expected_indices, expected_scores = (
        ((0, 1), (0,)) if return_filter == RETURN_FILTER_STR_FIRST
        else ((1, 2), (1,)))
    indices, scores = agas.pair_from_array(
        EXAMPLE_DATA, similarity_function=np.std, divergence_function=np.mean,
        return_filter=return_filter)
    assert np.array_equal(expected_indices, indices)
    assert np.array_equal(expected_scores, scores)


def test_example_data_return_filter_groups():
    func = functools.partial(agas.pair_from_array,
                             *(SIM_DATA, np.mean, np.std,))

    res_by_str = func(return_filter=agas.constants.RETURN_FILTER_STR_TOP)
    res_by_float = func(return_filter=0.0)
    assert np.array_equal(res_by_str[0], res_by_float[0])
    assert np.alltrue(res_by_str[1] == 0)
    assert np.alltrue(res_by_float[1] == 0)

    res_by_str = func(return_filter=agas.constants.RETURN_FILTER_STR_ALL)
    res_by_float = func(return_filter=1.0)
    assert np.array_equal(res_by_str[0], res_by_float[0])
    assert np.array_equal(res_by_str[1], res_by_float[1])


def test_sim_data():
    assert np.array_equal(agas.pair_from_array(
        SIM_DATA, similarity_function=np.mean, divergence_function=np.std,
    )[0], (2, 3))

    assert np.array_equal(agas.pair_from_array(
        SIM_DATA, similarity_function=np.std, divergence_function=np.mean,
    )[0], (0, 2))

    assert np.array_equal(agas.pair_from_array(
        SIM_DATA, similarity_function=np.mean, divergence_function=np.std,
        similarity_weight=0,
    )[0], (0, 3))


def test_input_arrays():
    assert np.array_equal(
        agas.pair_from_array(EXAMPLE_DATA.tolist(), similarity_function=np.mean,
                             divergence_function=np.std, )[0], (1, 2))

    with pytest.raises(ValueError):
        agas.pair_from_array(EXAMPLE_DATA.tolist()[0],
                             similarity_function=np.mean,
                             divergence_function=np.std, )
        agas.pair_from_array(None, similarity_function=np.mean,
                             divergence_function=np.std, )

    with pytest.raises(RuntimeError):
        (agas.pair_from_array(EXAMPLE_DATA[[0], :], similarity_function=np.mean,
                              divergence_function=np.std, ))

        (agas.pair_from_array(np.empty((0,)), similarity_function=np.mean,
                              divergence_function=np.std, ))
        (agas.pair_from_array(np.empty((0, 0)), similarity_function=np.mean,
                              divergence_function=np.std, ))


def test_input_functions_input_type():
    with pytest.raises(TypeError):
        agas.pair_from_array(EXAMPLE_DATA, similarity_function=np.mean,
                             divergence_function=None, )
        agas.pair_from_array(EXAMPLE_DATA, similarity_function=None,
                             divergence_function=np.std, )
        agas.pair_from_array(EXAMPLE_DATA, similarity_function=None,
                             divergence_function=None, )


def test_similarity_weight_input_type():
    _kwargs = {'input_array': EXAMPLE_DATA, 'similarity_function': np.mean,
               'divergence_function': np.std, }

    with pytest.raises(ValueError):
        agas.pair_from_array(**_kwargs, similarity_weight=5)
        agas.pair_from_array(**_kwargs, similarity_weight=-0.5)
    with pytest.raises(TypeError):
        agas.pair_from_array(**_kwargs, similarity_weight=[5])
        agas.pair_from_array(**_kwargs, similarity_weight='0.5')


def test_return_filter():


    with pytest.raises(ValueError):
        agas.pair_from_array(EXAMPLE_DATA, similarity_function=np.mean,
                             divergence_function=np.std,
                             return_filter=agas.constants.RETURN_FILTER_STR_ALL.title())
    with pytest.raises(TypeError):
        agas.pair_from_array(EXAMPLE_DATA, similarity_function=np.mean,
                             divergence_function=np.std,
                             return_filter=1)
        agas.pair_from_array(EXAMPLE_DATA, similarity_function=np.mean,
                             divergence_function=np.std,
                             return_filter=[])
        agas.pair_from_array(EXAMPLE_DATA, similarity_function=np.mean,
                             divergence_function=np.std,
                             return_filter=None)

def test_return_matrix_output():
    indices, scores = scores_matrix = agas.pair_from_array(TOY_DATA, np.mean,
                                                           np.std,
                                                           return_filter='all')
    scores_matrix = agas.pair_from_array(TOY_DATA, np.mean, np.std,
                                         return_matrix=True)

    assert np.nanmax(scores_matrix) == 1
    assert np.nanmin(scores_matrix) == 0

    assert np.array_equal(
        np.argwhere(scores_matrix == np.nanmin(scores_matrix))[0],
        indices[0]
    )
    assert np.array_equal(
        np.argwhere(scores_matrix == np.nanmin(scores_matrix))[1][::-1],
        indices[0]
    )

    assert np.array_equal(
        np.argwhere(scores_matrix == np.nanmax(scores_matrix))[0],
        indices[-1]
    )

    assert np.array_equal(
        np.argwhere(scores_matrix == np.nanmax(scores_matrix))[1][::-1],
        indices[-1]
    )