import os
import logging
from typing import Union

from core.DataTypes import DataType
from core.Property import EntityProperty


class Backlight:
    name = 'backlight'
    base_path = "/sys/class/backlight"

    @staticmethod
    def get_inputs():
        properties = []

        if not os.path.isdir(Backlight.base_path):
            logging.warning("No backlight devices found in /sys/class/backlight")
            return properties

        for entry in os.listdir(Backlight.base_path):
            path = os.path.join(Backlight.base_path, entry)
            brightness_file = os.path.join(path, "brightness")
            max_brightness_file = os.path.join(path, "max_brightness")

            if os.path.isfile(brightness_file) and os.path.isfile(max_brightness_file):
                try:
                    with open(max_brightness_file) as f:
                        max_brightness = int(f.read().strip())
                except Exception as e:
                    logging.error(f"Failed to read max_brightness for {entry}: {e}")
                    continue

                prop = EntityProperty(
                    category='system',
                    name=f'backlight_brightness_{entry}',
                    description=f'Backlight brightness for {entry} in %',
                    min=0,
                    step=1,
                    max=100,
                    type=DataType.PERCENT_INT,
                    interval=10,
                    call=lambda p=path, m=max_brightness: Backlight.get_brightness(p, m),
                    set=lambda val, p=path, m=max_brightness: Backlight.set_brightness(val, p, m)
                )

                properties.append(prop)

        return properties

    @staticmethod
    def set_brightness(brightness: Union[int, float], path: str, max_brightness: int):
        try:
            value = int((max_brightness / 100.0) * brightness)
            if value == 0 and brightness > 0:
                value = 1

            bl_power_path = os.path.join(path, "bl_power")
            if os.path.exists(bl_power_path):
                with open(bl_power_path, "w") as f:
                    f.write("4" if brightness < 1 else "0")

            with open(os.path.join(path, "brightness"), "w") as f:
                f.write(str(value))

        except Exception as e:
            logging.error(f"Failed to set brightness for {path}: {e}", exc_info=True)

    @staticmethod
    def get_brightness(path: str, max_brightness: int) -> int:
        try:
            with open(os.path.join(path, "brightness"), "r") as f:
                current = int(f.read().strip())
                return int((100 / max_brightness) * current)
        except Exception as e:
            logging.error(f"Failed to read brightness for {path}: {e}", exc_info=True)
            return 0
