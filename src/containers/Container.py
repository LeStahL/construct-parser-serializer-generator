from dependency_injector.wiring import Provide, inject
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Configuration, Factory

from services.CommandLineService import CommandLineService
from services.LogService import LogService
from services.GeneratorService import GeneratorService
from services.ModuleLoaderService import ModuleLoaderService
from services.CaseConversionService import CaseConversionService

class Container(DeclarativeContainer):
    commandLineService = Singleton(CommandLineService)
    caseConversionService = Singleton(CaseConversionService)

    logService = Singleton(LogService,
        commandLineService,
    )

    moduleLoaderService = Singleton(ModuleLoaderService,
        logService,
    )

    generatorService = Singleton(GeneratorService,
        logService,
        caseConversionService,
    )
