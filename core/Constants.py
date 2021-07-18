# -*- coding: utf-8 -*-

# Import standard module classes here to get compiled in by nuitka
from modules.Appearance import Appearance
from modules.InputDevs import InputDevs
from modules.MLX90615 import MLX90615
# from core.Wifi import Wifi
# from hardware.Alsa import AlsaMixer
# from hardware.Backlight import Backlight
from modules.CPU import CPU
# from hardware.Disk import DiskStats
# from hardware.HWMon import HWMon
# from hardware.IIO import IIO
# from hardware.Leds import Led
# from hardware.System import SystemInfo
# from core.Git import Git
# from modules.HTTPServer import HTTPServer
from interfaces.DemoModules import DemoThreadModule, EndlessThreadModule, DemoModule

# Other imports
import inspect
from typing import Set, Type

from interfaces.Module import ModuleBase

# Collect all ModuleBase classes.
# Classes are callable, filter simple variables.
_module_classes = tuple(cls for cls in locals().values()
                        if inspect.isclass(cls) and issubclass(cls, ModuleBase) and cls is not ModuleBase)


def internal_modules() -> Set[Type[ModuleBase]]:
    return set(_module_classes)


def external_modules() -> Set[Type[ModuleBase]]:
    # ToDo find external classes and check duplicated names
    return set()


always_instantiate_modules = Appearance, CPU


GIT_CLONE_PATH = 'https://github.com/shpi/main_app'
