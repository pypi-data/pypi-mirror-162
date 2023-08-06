# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining a custom yolox trainer class
"""

import argparse
import os
from typing import cast

from yolox.core.trainer import Trainer

from mlcvzoo_yolox.exp.custom_yolox_exp import CustomYOLOXExp


class YoloxTrainer(Trainer):
    """
    Define a custom yolox Trainer class to adapt some of the
    predefined behavior.
    """

    def __init__(self, exp: CustomYOLOXExp, args: argparse.Namespace) -> None:

        Trainer.__init__(self, exp=exp, args=args)

        self.exp = cast(CustomYOLOXExp, self.exp)  # type: ignore

        # Save the original configured evaluation interval for use in the method before_epoch(...)
        self.original_eval_interval = self.exp.eval_interval

        # Overwrite file_name attribute of the yolox Trainer class and use
        # the output_dir that is configured via the yolox experiment.
        # Yolox normally creates an extra subfolder on the basis of the
        # experiment name. This is an unwanted behavior.
        self.file_name = os.path.join(exp.output_dir)

    def after_epoch(self) -> None:
        """
        Define relevant steps that are executed after each training epoch

        Returns:
            None
        """

        if self.epoch % self.exp.checkpoint_interval == 0:
            self.save_ckpt(ckpt_name=f"{self.exp.exp_name}_{self.epoch}")

        Trainer.after_epoch(self=self)

    def before_epoch(self) -> None:
        """
        NOTE: Currently it is needed to overwrite this method to ensure that the value for
              self.exp.eval_interval is correctly set. Unfortunately the yolox.core.trainer.Trainer
              is setting the value to a fixed value of 1 in its before_epoch(...) implementation.

        Returns:
            None
        """

        Trainer.before_epoch(self=self)

        # ensure to use the configured value for "eval_interval"
        # TODO: Add a PR in the yolox implementation that removes the hard coded setting for this
        #       attribute
        self.exp.eval_interval = self.original_eval_interval
