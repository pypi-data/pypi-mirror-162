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

from modalic.utils.misc import all_equal_list


def test_all_equal_list() -> None:
    r"""."""
    assert (
        all_equal_list(
            ["torch.float32", "torch.float32", "torch.float32", "torch.float32"]
        )
        == "torch.float32"
    )
    assert (
        all_equal_list(
            ["torch.float32", "torch.double", "torch.float32", "torch.float32"]
        )
        is None
    )
    assert (
        all_equal_list(
            ["torch.double", "torch.float32", "torch.float32", "torch.float32"]
        )
        is None
    )
