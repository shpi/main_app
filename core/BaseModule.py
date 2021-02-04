
from core.DataTypes import DataType
from core.Toolbox import Pre_5_15_2_fix
import logging




class BaseModule:

    version = "1.0"
    required_packages = None
    allow_instances = True
    allow_maininstance = False
    description = "Basic Module for ModuleManager, please overwrite with sufficient description"

    def __init__(self, name, inputs,  settings: QSettings):

        super(BaseModule, self).__init__()
        self.name = name
        self.path = name
        self.settings = settings

        self.inputs = inputs

        self._module =                      {'description': 'Shutter Module for two binary outputs',
                                             'value': 'NOT_INITIALIZED',
                                             'type': DataType.MODULE,
                                             'lastupdate': 0,
                                             'interval': -1 }


    def get_inputs(self) -> dict:


        raise NameError('Please provide a function that export module properties.')

        return {}

    def delete_inputs(self) -> list:

        raise NameError('Please provide a function that export propertie keys for deletion.')


        return []

    def
