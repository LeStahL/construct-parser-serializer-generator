from dependency_injector.wiring import inject
from importlib.util import spec_from_file_location, module_from_spec
import sys
from types import ModuleType
from construct import Subconstruct
from os.path import exists

from construct_psg.services.LogService import LogService, StatusStrings

@inject
class ModuleLoaderService:
    def __init__(self,
        logService: LogService,
    ) -> None:
        super().__init__()

        self.logService = logService

    def loadModule(self, moduleName: str, modulePath: str) -> ModuleType:
        if not exists(modulePath):
            self.logService.log('Cannot load Python file {}; no such file.'.format(modulePath), StatusStrings.Error)
        
        try:
            spec = spec_from_file_location(moduleName, modulePath)
            module = module_from_spec(spec)
            sys.modules[moduleName] = module
            spec.loader.exec_module(module)
            self.logService.log('Loaded module {} from {}.'.format(moduleName, modulePath), StatusStrings.Success)
            return module
        except:
            self.logService.log('Failed to load module {} from {}.'.format(moduleName, modulePath), StatusStrings.Error)

    def construct(self, module: ModuleType, constructId: str) -> Subconstruct:
        return getattr(module, constructId)
