# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for handling utility methods that are used across the
mlcvzoo_mmdetection package.
"""

import logging
from typing import Any, Dict, List, Tuple

from mmcv import Config

from mlcvzoo_mmdetection.configuration import MMDetectionTrainArgparseConfig

logger = logging.getLogger(__name__)


# TODO: do we really need this method, or is it enough to have "modify_config"
def init_mmdetection_config(
    config_path: str, string_replacement_map: Dict[str, str]
) -> Tuple[Config, str]:

    new_config_path = modify_config(
        config_path=config_path, string_replacement_map=string_replacement_map
    )

    # Build config provided by mmdetection framework
    logger.info("Load mmdetection config from: %s", new_config_path)

    cfg = Config.fromfile(new_config_path)

    return cfg, new_config_path


def modify_config(config_path: str, string_replacement_map: Dict[str, str]) -> str:

    with open(file=config_path, mode="r", encoding="'utf-8") as config_file:
        config_file_content = config_file.readlines()

    new_config_file_content = list()
    for config_content in config_file_content:

        new_config_content = config_content

        for replacement_key, replacement_value in string_replacement_map.items():

            if replacement_key in config_content:
                new_config_content = new_config_content.replace(
                    replacement_key, replacement_value
                )

                logger.info(
                    "Replace '%s' in config-line '%s' with '%s'",
                    replacement_key,
                    new_config_content,
                    replacement_value,
                )

        new_config_file_content.append(new_config_content)

    new_config_path = config_path.replace(".py", "_local.py")
    with open(file=new_config_path, mode="w", encoding="'utf-8") as new_config_file:
        new_config_file.writelines(new_config_file_content)

    return new_config_path


def run_str_string_replacement(
    input_string: str, string_replacement_map: Dict[str, str]
) -> str:

    for replacement_key, replacement_value in string_replacement_map.items():

        if replacement_key in input_string:

            input_string = input_string.replace(replacement_key, replacement_value)

            logger.info(
                "Replace '%s' in string %s with '%s'",
                replacement_key,
                input_string,
                replacement_value,
            )

    return input_string
