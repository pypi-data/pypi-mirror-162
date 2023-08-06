# Copyright (c) OpenMMLab. All rights reserved.
# Copyright 2022 Open Logistics Foundation

"""
This module is used to source out methods that are used in the context of the training
of an mmdetection model. Inspired by
https://github.com/open-mmlab/mmdetection/blob/master/tools/train.py
"""

import logging
import os
from typing import Callable, Dict, List

import torch
import torch.distributed as dist
from mmcv import Config, mkdir_or_exist

from mlcvzoo_mmdetection.configuration import MMDetectionTrainArgparseConfig

logger = logging.getLogger(__name__)


def set_checkpoint_config(
    cfg: Config, framework_version: str, classes: List[str], model: torch.nn.Module
) -> Config:
    if cfg.checkpoint_config is not None:
        # save mmdet version, config file content and class names in
        # checkpoints as meta data
        cfg.checkpoint_config.meta = dict(
            mmdet_version=framework_version,
            CLASSES=classes,
        )

    model.CLASSES = classes  # type: ignore[assignment]

    return cfg


def init_work_dir(cfg: Config, config_path: str) -> None:
    # create work_dir
    mkdir_or_exist(os.path.abspath(cfg.work_dir))
    # dump config
    cfg.dump(
        os.path.join(
            cfg.work_dir,
            os.path.basename(config_path),
        )
    )


def create_random_seed(
    argparse_config: MMDetectionTrainArgparseConfig,
    cfg: Config,
    init_random_seed: Callable,  # type: ignore[type-arg]
    set_random_seed: Callable,  # type: ignore[type-arg]
) -> Config:
    # set random seeds
    seed = init_random_seed(argparse_config.seed, device=cfg.device)

    if argparse_config.diff_seed:
        seed = seed + dist.get_rank()  # type: ignore[no-untyped-call]
    logger.info(
        f"Set random seed to {seed}, " f"deterministic: {argparse_config.deterministic}"
    )
    set_random_seed(
        seed,
        deterministic=argparse_config.deterministic,
    )
    cfg.seed = seed

    return cfg


def create_meta_dict(
    cfg: Config, collect_env: Callable, exp_name: str  # type: ignore[type-arg]
) -> Dict[str, str]:
    # init the meta dict to record some important information such as
    # environment info and seed, which will be logged
    meta = dict()
    # log env info
    env_info_dict = collect_env()
    env_info = "\n".join([f"{k}: {v}" for k, v in env_info_dict.items()])
    dash_line = "-" * 60 + "\n"
    logger.info("Environment info:\n" + dash_line + env_info + "\n" + dash_line)
    meta["env_info"] = env_info
    meta["config"] = cfg.pretty_text

    meta["seed"] = cfg.seed
    meta["exp_name"] = exp_name

    return meta
