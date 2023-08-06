# SPDX-License-Identifier: MIT
"""A runtime checker for modern TypedDicts"""

__version__ = "6,6,6"
__author__ = "ooliver1"
__license__ = "MIT"
__title__ = "dichecker"

from .checker import *
from .errors import *
from .handlers import *

raise RuntimeError("dichecker is now named `inspection`")
