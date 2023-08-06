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

"""Custom Configuration object."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from logging import WARNING
from typing import Any, Dict, Optional

import toml

from modalic.logging.logging import logger


@dataclass
class Conf(object):
    r"""Configuration object class that stores the parameters regarding the federated learning process.

    :param server_address: (Default: ``'[::]:8080'``) GRPC endpoint for aggregation server.
    :param client_id: (Default: ``0``) Client identifier which must be unique.
    :param timeout: (Default: ``0``) Defines a timeout length in seconds which is mainly used for simulating some waiting periode
        after each training round. Should always be non-negative.
    :param training_rounds: (Default: ``0``) Number of training rounds that should be performed.
    :param data_type: (Default: ``'F32'``) Models data type which defines the (de-)serialization of the model.
        Type is determined automatically for the endpoints.
    :param certificates: (Default: ``''``) TLS certificates for establishing secure channel with server.

    :Example:

    Two main ways to construct a Conf object.
        >>> # via dictionary
        >>> custom_dict = {
        >>>     "api": {"server_address": "[::]:8080"},
        >>>     "process":
        >>>         {"training_rounds": 10, "timeout": 5.0},
        >>> }
        >>> conf = Conf.create_conf(custom_dict)
        >>> # ----------------------------------------------
        >>> # via .toml (example config.toml below)
        >>> [api]
        >>> server_address = "[::]:8080"
        >>>
        >>> [process]
        >>> training_rounds = 10
        >>> participants = 3
        >>> strategy = "FedAvg"
        >>> #
        >>> conf = Conf.from_toml(path)
    """
    server_address: str = "[::]:8080"
    client_id: int = 0
    timeout: float = 0.0
    training_rounds: int = 0
    data_type: str = "F32"
    certificates: str = ""

    def set_params(self, conf: dict[str, dict[str, Any]]) -> None:
        r"""Overwrites default parameters with external is stated.

        :param conf: Produced by .toml config. Dict which contains dicts. The values
            of conf will overwrite the default values.
        """
        if conf is not None:
            if value := self._find_keys(conf, "server_address"):
                self.server_address = value
            if value := self._find_keys(conf, "client_id"):
                self.client_id = value
            if value := self._find_keys(conf, "timeout"):
                self.timeout = value
            if value := self._find_keys(conf, "training_rounds"):
                self.training_rounds = value
            if value := self._find_keys(conf, "data_type"):
                self.data_type = value
            if value := self._find_keys(conf, "certificates"):
                self.certificates = value

    def _find_keys(self, blob: Dict[str, dict[str, Any]], key_str: str = "") -> Any:
        r"""Finds the value for certain key in dictionary with arbitrary depth.

        :param blob: Dictionary in which the key value pair is searched for.
        :param key_str: Key that is searched for.
        :returns: Any value that belongs to the key.
        """
        value = None
        for (k, v) in blob.items():
            if k == key_str:
                return v
            if isinstance(v, dict):
                value = self._find_keys(v, key_str)
        return value

    @classmethod
    def create_conf(
        cls, conf: dict[str, dict[str, Any]] = None, cid: Optional[int] = None
    ) -> Conf:
        r"""Constructs a (default) conig object with external conf if given.

        :param conf: Produced by .toml config. Dict which contains dicts. The values
            of conf will overwrite the default values.
        :param cid: (Optional) Option to overwrite client_id when creating a conf.
        """
        instance = cls()
        instance.set_params(conf)
        if cid:
            instance.client_id = cid
        return instance

    @classmethod
    def from_toml(cls, path: str, cid: Optional[int] = None) -> Conf:
        r"""Constructs a conig object from external .toml configuration file.

        :param path: String path to .toml config file.
        :param cid: (Optional) Option to overwrite client_id when creating a conf.
        """
        instance = cls()
        try:
            instance.set_params(toml.load(path))
            if cid:
                instance.client_id = cid
        except FileNotFoundError:
            logger.log(
                WARNING,
                f"Config .toml via path '{path}' cannot be found. Default configuration parameters are used.",
            )
        return instance

    def __str__(self) -> str:
        r"""Custom output string."""
        s = ", ".join(
            f"{field.name}={getattr(self, field.name)!r}"
            for field in dataclasses.fields(self)
            if field.name != "certificates"
        )
        return f"{type(self).__name__}({s})"
