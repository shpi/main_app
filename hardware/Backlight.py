import logging
import os
import sys
from typing import Union

from interfaces.DataTypes import DataType
from core.Property import EntityProperty


class Backlight:
    backlightpath = "/sys/class/backlight/"

    def __init__(self):
        self.backlight_sysfs_path = False
        self.backlight_sysfs_max = 100  # fallback value
        self.backlight_sysfs_has_power = False
        self._module = EntityProperty(parent=self,
                                      category='module',
                                      entity='core',
                                      name='backlight',
                                      description='Backlight Module',
                                      type=DataType.UNDEFINED,  # TODO
                                      interval=-1)
        self._module.value = 'NOT INITIALIZED'

        if not os.path.isdir(Backlight.backlightpath):
            self._module.value = 'ERROR'
            logging.error('No physical backlight found.')
            return  # Nothing to do here, no backlight found.

        for file in os.listdir(Backlight.backlightpath):

            if os.path.exists(Backlight.backlightpath + file + "/brightness"):

                self.backlight_sysfs_path = Backlight.backlightpath + file

                if os.path.exists(Backlight.backlightpath + file + "/backlight_sysfs_has_power"):
                    self.backlight_sysfs_has_power = 1

                if not os.path.exists(Backlight.backlightpath + file + "/max_brightness"):
                    break

                with open(Backlight.backlightpath + file + "/max_brightness") as backlight_sysfs_max:
                    self.backlight_sysfs_max = int(backlight_sysfs_max.readline())

                break  # we're looking only for one backlight now

        self._properties = [self._module]

        if self.backlight_sysfs_path:
            self._brightness = EntityProperty(parent=self,
                                              category='core',
                                              entity='backlight',
                                              name='brightness',
                                              description='Backlight brightness in %',
                                              type=DataType.PERCENT_INT,
                                              call=self.get_brightness,
                                              set=self.set_brightness,

                                              interval=10)

            self._properties = [self._module, self._brightness]

    def delete_inputs(self) -> list:
        [prop.path for prop in self._properties]

    def get_inputs(self) -> list:
        return self._properties

    def set_brightness(self, brightness: Union[float, int]):

        # reducing brightness to 0-100
        setbrightness = int((self.backlight_sysfs_max / 100) * brightness)

        if setbrightness == 0 and brightness > 0:
            setbrightness = 1

        if self.backlight_sysfs_has_power > 0:
            try:
                with open(self.backlight_sysfs_path + "/bl_power", "w") as bright:
                    if brightness < 1:
                        bright.write("4")
                    else:
                        bright.write("0")

            except Exception as e:
                self._module.value = 'ERROR'
                self.inputs.update_remote(self._module.path)
                exception_type, exception_object, exception_traceback = sys.exc_info()
                line_number = exception_traceback.tb_lineno
                logging.error(f'error: {e} in line {line_number}')

        try:
            with open(self.backlight_sysfs_path + "/brightness", "w") as bright:
                bright.write(str(setbrightness))
                self._module.value = 'OK'

        except Exception as e:
            self._module.value = 'ERROR'
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line {line_number}')

    def get_brightness(self) -> int:
        try:
            with open(self.backlight_sysfs_path + "/brightness", "r") as bright:
                value = int((100 / self.backlight_sysfs_max) * int(bright.readline().rstrip()))
                self._module.value = 'OK'
                return value
        except Exception as e:
            self._module.value = 'ERROR'
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(f'error: {e} in line {line_number}')
            return 0
