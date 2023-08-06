import datetime
import warnings
from typing import Any, Dict, List, NamedTuple, Optional, Sized


class OnedatautilException(Exception):
    """
    Base class for all Onedatautil's errors.

    Each custom exception should be derived from this class.
    """

    status_code = 500


class OnedatautilConfigException(OnedatautilException):
    """Raise when there is configuration problem."""
