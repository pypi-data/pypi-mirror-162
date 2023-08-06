# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Definition of Enums that are used across the mlcvzoo_mmocr package
"""

from mlcvzoo_base.configuration.structs import BaseType


class ClassTypes(BaseType):
    TEXT_CLASS_NAME: str = "text"
    TEXT_CLASS_ID: int = -1
