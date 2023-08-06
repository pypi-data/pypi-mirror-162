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

from modalic.api.tf.tf_utils import _get_tf_model_dtype, _get_tf_model_shape


def test_get_tf_model_dtype(sub_keras_model) -> None:
    r"""."""
    assert _get_tf_model_dtype(sub_keras_model) == "F32"


def test_get_torch_model_shape(seq_keras_model) -> None:
    r"""."""
    np.testing.assert_equal(
        _get_tf_model_shape(seq_keras_model),
        [
            np.array([3072, 3000]),
            np.array([3000]),
            np.array([3000, 1000]),
            np.array([1000]),
            np.array([1000, 10]),
            np.array([10]),
        ],
    )
