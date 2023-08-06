# Copyright (C) 2021,2022 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Console tools to download online novel and convert to text file."""

import logging
import os
import sys
from argparse import Namespace
from datetime import datetime as dt
from importlib.resources import read_text
from pathlib import Path
from typing import Dict

import tomlkit

__version__ = "0.1.3"

_logger = logging.getLogger(__name__)


class ConfigFileCorruptedError(Exception):
    """Config file corrupted after reading."""


class ConfigFileExistsError(Exception):
    """Config file found when generating a new config file."""


def setup_logging(debug: bool = False) -> None:
    """Set up logging by level."""
    conf = {
        True: {
            "level": logging.DEBUG,
            "msg": "[%(asctime)s] %(levelname)s: %(name)s: %(message)s",
        },
        False: {"level": logging.INFO, "msg": "%(message)s"},
    }

    logging.basicConfig(
        level=conf[debug]["level"],
        stream=sys.stdout,
        format=conf[debug]["msg"],
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_or_create_config(parsed_args: Namespace, app: str) -> Dict:
    """Load config from file or create config to file."""
    config = vars(parsed_args)

    if parsed_args.config:
        config = _load_config(parsed_args, app)
    elif parsed_args.gen_config:
        config = _create_config(parsed_args, app)

    return config


def _load_config(parsed_args: Namespace, app: str) -> Dict:
    """Load the config from command line options or from config file."""
    config_file = parsed_args.config
    with open(config_file, "r", encoding="utf8") as file:
        toml = tomlkit.load(file)

        if len(toml) == 0:
            raise ConfigFileCorruptedError(
                f"Corrupted config file: {config_file}"
            )

        toml_tpl = tomlkit.parse(read_text(__package__, f"{app}.toml"))
        if toml_tpl["config_version"] != toml.get("config_version"):
            _logger.info("Upgrade config file: %s", config_file)
            config = Namespace(**dict(toml))
            config.gen_config = config_file
            config.config_version = toml_tpl["config_version"]
            return _upgrade_config(config, app)

        _logger.info("Load from config file: %s", config_file)
        for key, value in toml.items():
            _logger.debug("config: %s, value: %s", repr(key), repr(value))

        return toml


def _upgrade_config(config: Namespace, app: str) -> Dict:
    toml_filename = Path(config.gen_config)

    ymd_hms = dt.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = Path(
        toml_filename.resolve().parent.joinpath(
            toml_filename.stem + "_" + ymd_hms + "_backup.toml"
        )
    )
    os.rename(toml_filename, backup_filename)
    _logger.info("Backup config file: %s", backup_filename)

    return _create_config(config, app)


def _create_config(parsed_args: Namespace, app: str) -> Dict:
    """Create config to toml file."""
    config_filename = parsed_args.gen_config

    if Path(config_filename).exists():
        raise ConfigFileExistsError(
            f"Existing config file found: {config_filename}"
        )

    with open(config_filename, "w", encoding="utf8") as file:
        config_dict = vars(parsed_args)
        _logger.debug(config_dict)

        toml = read_text(__package__, f"{app}.toml")
        doc = tomlkit.parse(toml)

        for key, value in config_dict.items():
            if key in doc:
                doc[key] = value

        file.write(tomlkit.dumps(doc))
        _logger.info("Create config file: %s", config_filename)

        return vars(parsed_args)
