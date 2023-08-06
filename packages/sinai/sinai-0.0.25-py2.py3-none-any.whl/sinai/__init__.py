"""Sinai is a library to help you monitor everything."""
from abc import ABC

from sinai.types import JDict, MonitorInstance

VERSION = "0.0.25"


class BaseView(ABC):
    def __init__(self, monitor: MonitorInstance):
        self.monitor = monitor
        self.data: JDict = {}  # Freeform working space to store your data.
