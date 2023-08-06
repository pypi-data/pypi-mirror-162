# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Model that wraps all objection detection models of mmdetection
"""

import copy
import logging
import os
import shlex
import subprocess
import sys
import time
from abc import ABC
from typing import Any, Callable, Dict, Generic, Optional, Tuple

import torch
import torch.nn
from config_builder.replacement_map import get_replacement_map_copy
from mlcvzoo_base.api.interfaces import NetBased, Trainable
from mlcvzoo_base.api.model import ConfigurationType, Model
from mlcvzoo_base.configuration.class_mapping_config import ClassMappingConfig
from mlcvzoo_base.configuration.reduction_mapping_config import ReductionMappingConfig
from mlcvzoo_base.data_preparation.annotation_handler import AnnotationHandler
from mmcv import Config, runner
from mmcv.runner import get_dist_info, init_dist, load_checkpoint, set_random_seed
from mmcv.utils import Registry
from mmdet.utils import replace_cfg_vals, setup_multi_processes, update_data_root
from nptyping import Int, NDArray, Shape
from related import to_dict

from mlcvzoo_mmdetection.configuration import (
    MMDetectionConfig,
    MMDetectionDistributedTrainConfig,
    MMDetectionTrainArgparseConfig,
)
from mlcvzoo_mmdetection.mlcvzoo_mmdet_dataset import MLCVZooMMDetDataset
from mlcvzoo_mmdetection.third_party.mmdetection import (
    create_meta_dict,
    create_random_seed,
    init_work_dir,
    set_checkpoint_config,
)
from mlcvzoo_mmdetection.utils import init_mmdetection_config

logger = logging.getLogger(__name__)

ImageType = NDArray[Shape["Height, Width, Any"], Int]


class MMDetectionModel(
    Model,  # type: ignore[type-arg]
    NetBased[torch.nn.Module],
    Trainable,
    ABC,
):
    """
    Class for wrapping mmdetection models
    """

    def __init__(
        self,
        from_yaml: Optional[str] = None,
        configuration: Optional[MMDetectionConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
        init_for_inference: bool = False,
        is_multi_gpu_instance: bool = False,
    ) -> None:
        self.net: Optional[torch.nn.Module] = None

        self.yaml_config_path: Optional[str] = from_yaml
        self.is_multi_gpu_instance: bool = is_multi_gpu_instance

        self.configuration: MMDetectionConfig = self.create_configuration(
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )

        Model.__init__(
            self,
            unique_name=self.configuration.base_config.MODEL_SPECIFIER,
            configuration=self.configuration,
            init_for_inference=init_for_inference,
        )
        NetBased.__init__(self, net=self.net)
        Trainable.__init__(self)

    @staticmethod
    def _get_framework_imports() -> Tuple[  # type: ignore[type-arg]
        Callable,
        Callable,
        Callable,
        Callable,
        Callable,
        Callable,
    ]:
        from mmdet.apis import init_detector, init_random_seed, train_detector
        from mmdet.datasets import build_dataset
        from mmdet.models import build_detector
        from mmdet.utils import collect_env

        return (
            init_detector,
            init_random_seed,
            train_detector,
            build_dataset,
            build_detector,
            collect_env,
        )

    @staticmethod
    def _get_dataset_type() -> str:
        return "MLCVZooMMDetDataset"

    @staticmethod
    def _get_framework_version() -> Any:
        from mmdet import __version__ as framework_version

        return framework_version

    def _build_val_dataset(self, cfg: Config) -> Any:

        (
            _,
            _,
            _,
            build_dataset,
            _,
            _,
        ) = self._get_framework_imports()

        val_dataset = copy.deepcopy(cfg.data.val)
        val_dataset.pipeline = cfg.data.train.pipeline
        return build_dataset(val_dataset)

    def get_net(self) -> Optional[torch.nn.Module]:
        return self.net

    def _init_inference_model(self) -> None:

        (
            init_detector,
            _,
            _,
            _,
            _,
            _,
        ) = self._get_framework_imports()

        if self.net is None:
            (
                cfg,
                self.configuration.inference_config.config_path,
            ) = init_mmdetection_config(
                config_path=self.configuration.inference_config.config_path,
                string_replacement_map=self.configuration.string_replacement_map,
            )

            if self.configuration.train_config.argparse_config.cfg_options is not None:
                cfg.merge_from_dict(
                    self.configuration.train_config.argparse_config.cfg_options
                )

            self.net = init_detector(
                config=cfg,
                checkpoint=None,
                device=self.configuration.inference_config.device_string,
            )

            self.restore(
                checkpoint_path=self.configuration.inference_config.checkpoint_path
            )

    def store(self, checkpoint_path: str) -> None:
        pass

    def restore(self, checkpoint_path: str) -> None:

        if self.net is None:
            raise ValueError(
                "In order to restore a checkpoint, the net attribute has"
                "to be initialized!"
            )

        logger.info(
            "Load model for %s from %s",
            self.get_name(),
            self.configuration.inference_config.checkpoint_path,
        )

        checkpoint = load_checkpoint(
            self.net,
            self.configuration.inference_config.checkpoint_path,
            map_location="cpu",
        )

        if "CLASSES" in checkpoint.get("meta", {}):
            self.net.CLASSES = checkpoint["meta"]["CLASSES"]

    def save_reduced_checkpoint(
        self, input_checkpoint_path: str, output_checkpoint_path: str
    ) -> None:
        """
        Saves a reduced version of a stored checkpoint that does not contain optimizer states
        anymore. Therefore, it keeps the weights and meta information of the source checkpoint.

        Args:
            input_checkpoint_path: Path to source checkpoint file
            output_checkpoint_path: Path to where the checkpoint is saved
        """

        (
            init_detector,
            _,
            _,
            _,
            _,
            _,
        ) = self._get_framework_imports()

        # loading config of current model
        cfg, _ = init_mmdetection_config(
            config_path=self.configuration.inference_config.config_path,
            string_replacement_map=self.configuration.string_replacement_map,
        )

        # load checkpoint from source directory to a model
        model = init_detector(
            config=cfg,
            checkpoint=input_checkpoint_path,
            device=self.configuration.inference_config.device_string,
        )

        # Load input checkpoint dict from and extract the metadata for the output checkpoint.
        # Save reduced checkpoint with metadata of full checkpoint to target directory.
        runner.checkpoint.save_checkpoint(
            model,
            output_checkpoint_path,
            meta=runner.load_checkpoint(
                model, input_checkpoint_path, map_location="cpu"
            )["meta"],
        )

        logger.info(
            "Saved checkpoint from '%s' in a reduced version to '%s'.",
            input_checkpoint_path,
            output_checkpoint_path,
        )

    def train(self) -> None:

        if self.configuration.train_config.argparse_config.launcher == "none":
            self._train(
                argparse_config=self.configuration.train_config.argparse_config,
                string_replacement_map=self.configuration.string_replacement_map,
                class_mapping_config=self.configuration.class_mapping,
                reduction_mapping_config=self.configuration.inference_config.reduction_class_mapping,
            )
        else:
            if self.configuration.train_config.multi_gpu_config is None:
                raise ValueError(
                    "In order to run a multi GPU training, "
                    "the config attribute train_config.multi_gpu_config has to be provided"
                )

            self._train_multi_gpu(
                argparse_config=self.configuration.train_config.argparse_config,
                multi_gpu_config=self.configuration.train_config.multi_gpu_config,
                string_replacement_map=self.configuration.string_replacement_map,
            )

    @staticmethod
    def _register_dataset() -> None:
        """
        Register the custom dataset of the MLCVZoo in the registry of mmcv

        Returns:
            None
        """
        mmdet_registry = Registry("dataset")
        mmdet_registry.register_module(MLCVZooMMDetDataset.__name__)

    @staticmethod
    def _train_multi_gpu(
        argparse_config: MMDetectionTrainArgparseConfig,
        multi_gpu_config: MMDetectionDistributedTrainConfig,
        string_replacement_map: Dict[str, str],
    ) -> None:
        """
        Run mmdet multi-gpu/distributed training.

        Returns:
            None
        """

        cuda_visible_devices = multi_gpu_config.cuda_visible_devices
        gpus = argparse_config.gpus
        port = multi_gpu_config.multi_gpu_sync_port

        env = os.environ.copy()
        env[
            "PYTHONPATH"
        ] = f"{os.environ.get('PYTHONPATH') if os.environ.get('PYTHONPATH') is not None else ''}"

        env["cuda_visible_devices"] = cuda_visible_devices

        for key, value in get_replacement_map_copy().items():
            env[key] = value

        _, new_config_path = init_mmdetection_config(
            config_path=argparse_config.config,
            string_replacement_map=string_replacement_map,
        )

        command = (
            f"-m torch.distributed.run "
            f"--nproc_per_node={gpus} "
            f"--master_port={port} "
            f"{__file__} "
            f"{new_config_path} "
        )

        logger.debug("Run command: %s", command)

        command_split = [sys.executable]
        command_split.extend(shlex.split(command))
        result = subprocess.run(args=command_split, env=env, check=False)

        if result.returncode:
            logger.error(
                "Command '%s' returned with exit code %i", command, result.returncode
            )
            raise RuntimeError(
                f"Distributed training exited with exitcode != 0, "
                f"exitcode: {result.returncode}"
            )

    def _train_pre_init(self, cfg: Config) -> Config:
        # replace the ${key} with the value of cfg.key
        cfg = replace_cfg_vals(cfg)
        # update data root according to MMDET_DATASETS
        update_data_root(cfg)

        return cfg

    def _train(
        self,
        argparse_config: MMDetectionTrainArgparseConfig,
        string_replacement_map: Dict[str, str],
        class_mapping_config: Optional[ClassMappingConfig] = None,
        reduction_mapping_config: Optional[ReductionMappingConfig] = None,
    ) -> None:
        (
            _,
            init_random_seed,
            train_detector,
            build_dataset,
            build_detector,
            collect_env,
        ) = self._get_framework_imports()

        self._register_dataset()

        _, new_config_path = init_mmdetection_config(
            config_path=argparse_config.config,
            string_replacement_map=string_replacement_map,
        )

        cfg = Config.fromfile(new_config_path)

        cfg = self._train_pre_init(cfg=cfg)

        cfg.merge_from_dict(argparse_config.cfg_options)
        # set multi-process settings
        setup_multi_processes(cfg)

        cfg.work_dir = argparse_config.work_dir
        if argparse_config.resume_from:
            cfg.resume_from = argparse_config.resume_from
        cfg.auto_resume = argparse_config.auto_resume

        # set cudnn_benchmark
        if cfg.get("cudnn_benchmark", False):
            torch.backends.cudnn.benchmark = True

        cfg.gpu_ids = argparse_config.gpu_ids
        distributed = False
        if not cfg.gpu_ids:
            # TODO: cpu use-case currently broken => fix in mmdet
            cfg.device = "cpu"
        # init distributed env first, since logger depends on the dist info.
        elif argparse_config.launcher == "none":
            cfg.device = "cuda"
            cfg.gpu_ids = [cfg.gpu_ids[0]]
        else:
            cfg.device = "mlu"
            distributed = True
            init_dist(
                argparse_config.launcher,
                **cfg.dist_params,
            )
            # re-set gpu_ids with distributed training mode
            _, world_size = get_dist_info()

        init_work_dir(cfg=cfg, config_path=new_config_path)

        cfg = create_random_seed(
            argparse_config=argparse_config,
            cfg=cfg,
            init_random_seed=init_random_seed,
            set_random_seed=set_random_seed,
        )

        logger.debug(f"Config:\n{cfg.pretty_text}")

        model = build_detector(
            cfg.model, train_cfg=cfg.get("train_cfg"), test_cfg=cfg.get("test_cfg")
        )
        model.init_weights()

        dataset_type = self._get_dataset_type()
        for data_type in ["train", "test", "val"]:
            if cfg.data[data_type].type == dataset_type:
                annotation_handler_config = AnnotationHandler.create_configuration(
                    from_yaml=cfg.data[data_type].annotation_handler_config_path,
                    string_replacement_map=string_replacement_map,
                )

                if class_mapping_config is None:
                    raise ValueError(
                        "In order to use MLCVZooMMDetDataset as valid "
                        "class_mapping_config has to be provided, "
                        "class_mapping_config=None"
                    )

                annotation_handler_config.class_mapping = class_mapping_config
                annotation_handler_config.reduction_class_mapping = (
                    reduction_mapping_config
                )

                cfg.data[data_type].annotation_handler_config_dict = to_dict(
                    annotation_handler_config
                )

        datasets = [build_dataset(cfg.data.train)]

        if len(cfg.workflow) == 2:
            datasets.append(self._build_val_dataset(cfg=cfg))

        cfg = set_checkpoint_config(
            cfg=cfg,
            framework_version=self._get_framework_version(),
            classes=datasets[0].CLASSES,
            model=model,
        )

        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        train_detector(
            model,
            datasets,
            cfg,
            distributed=distributed,
            validate=(not argparse_config.no_validate),
            timestamp=timestamp,
            meta=create_meta_dict(
                cfg=cfg, collect_env=collect_env, exp_name=self.get_name()
            ),
        )
