# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for handling the writing of a darknet data file,
which defines the main information that is needed for training
a model in the darknet framework.
"""

from mlcvzoo_base.utils.file_utils import ensure_dir

darknet_data_file_template = """classes = {classes}
train   = {train}
valid   = {valid}
names   = {names}
backup  = {backup}
eval    = {eval}
"""


class DarknetDataFile:
    """
    Class that handles the writing of a darknet data file,
    which defines the main information that is needed for training
    a model in the darknet framework.
    """

    def __init__(
        self,
        classes: int,
        names: str,
        valid: str,
        backup: str,
        eval: str,
        train: str,
    ) -> None:
        self.data = {
            "classes": classes,
            "names": names,
            "train": train,
            "valid": valid,
            "backup": backup,
            "eval": eval,
        }

    def write_file(self, path: str) -> None:
        file_content = darknet_data_file_template.format(**self.data)
        ensure_dir(file_path=path, verbose=True)
        with open(path, "w") as f:
            f.write(file_content)
