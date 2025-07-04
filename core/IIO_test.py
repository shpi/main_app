#!/usr/bin/env python3

import sys
import logging

# Optional: erweitere den Pfad, wenn du z. B. in einem Subordner testest
# sys.path.insert(0, "/path/to/your/module/")

# Alte instanzbasierte Klasse
from core.IIO import IIO as IIO_old

# Neue statische Klasse (du musst sie in IIO_static.py evtl. umbenennen!)
from core.IIO_static import IIO as IIO_static

from core.DataTypes import Convert


def collect_props(prop_list):
    """Hilfsfunktion zur geordneten Darstellung."""
    result = {}
    for p in prop_list:
        key = p.path
        value = Convert.rawvalue_to_readable(p.type, p.value) if p.value is not None else None
        result[key] = {
            "type": Convert.type_to_str(p.type),
            "value": value,
            "output": p.is_output,
            "range": (p.min, p.max, p.step),
            "desc": p.description
        }
    return result


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("Collecting properties from old (instanzbasiert) IIO...")
    old_iio = IIO_old()
    old_props = collect_props(old_iio.get_inputs())

    print("Collecting properties from new (statisch) IIO...")
    new_props = collect_props(IIO_static.get_inputs())

    old_keys = set(old_props.keys())
    new_keys = set(new_props.keys())

    print("\n--- Vergleich der Property-Pfade ---")
    only_in_old = sorted(old_keys - new_keys)
    only_in_new = sorted(new_keys - old_keys)
    common = sorted(old_keys & new_keys)

    if only_in_old:
        print("\nNur in ALT:")
        for k in only_in_old:
            print("  ", k)

    if only_in_new:
        print("\nNur in NEU:")
        for k in only_in_new:
            print("  ", k)

    print(f"\nGemeinsame Properties: {len(common)}")

    differences = 0
    for k in common:
        if old_props[k] != new_props[k]:
            differences += 1
            print(f"\nUnterschiede in '{k}':")
            print("  ALT :", old_props[k])
            print("  NEU :", new_props[k])

    if differences == 0:
        print("\nAlle gemeinsamen Properties stimmen überein ✅")
    else:
        print(f"\nUnterschiede bei {differences} gemeinsamen Properties ❗")


if __name__ == "__main__":
    main()
