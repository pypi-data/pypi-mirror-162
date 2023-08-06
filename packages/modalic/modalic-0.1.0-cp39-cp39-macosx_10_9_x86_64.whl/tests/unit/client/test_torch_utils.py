#  Copyright (c) modalic 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import numpy as np

from modalic.api.torch.torch_utils import (
    _get_torch_model_dtype,
    _get_torch_model_shape,
    _get_torch_weights,
    _set_torch_weights,
)


def test_get_set_torch_weights(torch_model) -> None:
    r"""."""
    weights = _get_torch_weights(torch_model)
    processed = _set_torch_weights(torch_model, weights)

    assert torch_model == processed


def test_get_torch_model_dtype(torch_model) -> None:
    r"""."""
    assert _get_torch_model_dtype(torch_model) == "F32"


def test_get_torch_model_shape(torch_model) -> None:
    r"""."""
    np.testing.assert_equal(
        _get_torch_model_shape(torch_model), [np.array([1, 4]), np.array([1])]
    )
