from PySide2.QtCore import QSettings

from core.DataTypes import DataType


class BaseModule:
    version = "1.0"
    required_packages = None
    allow_instances = True
    allow_maininstance = False
    description = "Basic Module for ModuleManager, please overwrite with sufficient description"

    def __init__(self, name, inputs, settings: QSettings):
        super(BaseModule, self).__init__()
        self.name = name
        self.path = name
        self.settings = settings

        self.inputs = inputs

        self._module = {'description': 'Shutter Module for two binary outputs',
                        'value': 'NOT_INITIALIZED',
                        'type': DataType.MODULE,
                        'interval': -1}

    def get_inputs(self) -> dict:
        raise NameError('Please provide a function that export module properties.')

        return {}

    def delete_inputs(self) -> list:
        raise NameError('Please provide a function that export propertie keys for deletion.')

        return []
