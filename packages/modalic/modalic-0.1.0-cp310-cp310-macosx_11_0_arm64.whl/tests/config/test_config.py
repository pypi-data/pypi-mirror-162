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

from modalic.config.config import Conf


def test_create_conf() -> None:
    r"""."""
    default_conf = Conf.create_conf()

    assert default_conf == Conf()

    testing_conf = Conf()
    testing_conf.client_id = 42
    testing_conf.training_rounds = 10
    testing_conf.participants = 10

    custom_settings = {
        "process": {"training_rounds": 10, "participants": 10},
        "client_id": 42,
    }
    custom_conf = Conf.create_conf(custom_settings)

    assert custom_conf == testing_conf


def test_find_keys() -> None:
    r"""."""
    conf = Conf()

    attrs_1 = {
        "process": {"training_rounds": 10, "participants": 10},
        "client_id": 42,
    }
    assert conf._find_keys(attrs_1, "client_id") == 42

    attrs_2 = {
        "process": {"training": {"training_rounds": 10}, "participants": 10},
        "client_id": 42,
    }
    assert conf._find_keys(attrs_2, "training_rounds") == 10

    attrs_3 = {
        "process": {
            "training": {"training_rounds": 10, "k": 25},
            "participants": 10,
        },
        "client_id": 42,
    }
    assert conf._find_keys(attrs_3, "k") == 25

    attrs_4 = {
        "process": {
            "training": {"training_rounds": 10, "k": 25},
            "participants": 10,
        },
        "client_id": 42,
    }
    assert conf._find_keys(attrs_4, "data_type") is None
