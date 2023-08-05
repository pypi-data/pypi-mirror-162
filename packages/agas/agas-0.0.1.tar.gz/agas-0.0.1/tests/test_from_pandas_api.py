import typing

import numpy as np
import pandas as pd
import pytest

import agas
from . test_from_numpy_api import EXAMPLE_DATA

TOY_DATA_DF = pd.DataFrame(EXAMPLE_DATA,
                           columns=[f'Day {i}' for i in range(1, 11)]).assign(
    subject_ids=['Foo', 'Bar', 'Baz'])


def test_invalid_arguments():
    with pytest.raises(TypeError):
        agas.pair_from_wide_df(None, np.mean, np.std)

    with pytest.raises(ValueError):
        # Select no rows
        agas.pair_from_wide_df(
            TOY_DATA_DF.loc[TOY_DATA_DF['subject_ids'] == 'Foobaz'].filter(
                like='Day'), np.mean, np.std)
        # Select a single row
        agas.pair_from_wide_df(
            TOY_DATA_DF.loc[TOY_DATA_DF['subject_ids'] == 'Bar'].filter(
                like='Day'), np.mean, np.std)


@pytest.mark.parametrize("values_columns",
                         [None, TOY_DATA_DF.filter(like='Day').columns])
def test_return_type(values_columns: typing.Union[None, typing.List]):

    if values_columns is None:
        inp_vals = TOY_DATA_DF.filter(like='Day')
    else:
        inp_vals = TOY_DATA_DF.copy()

    expected_return = inp_vals.iloc[[0, 1], :]
    pd.testing.assert_frame_equal(
        inp_vals.iloc[agas.pair_from_wide_df(inp_vals, np.std, np.mean,
                               values_columns=values_columns)[0], :],
        expected_return)
