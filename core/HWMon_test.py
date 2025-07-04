#!/usr/bin/env python3
"""Simple program to display hwmon properties using the core HWMon module."""

import os
import sys
import logging

# Allow running this script from anywhere
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.HWMon import HWMon
from core.DataTypes import Convert


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    hw = HWMon()
    for prop in hw.get_inputs():
        prop.update()
        value = Convert.rawvalue_to_readable(prop.type, prop.value)
        print(f"{prop.path}")
        print(f"  value: {value}")
        print(f"  type: {Convert.type_to_str(prop.type)}")
        print(f"  output: {prop.is_output}")
        if prop.min is not None or prop.max is not None:
            print(f"  range: {prop.min}-{prop.max} step={prop.step}")
        if prop.description:
            print(f"  desc: {prop.description}")
        print()


if __name__ == "__main__":
    main()
