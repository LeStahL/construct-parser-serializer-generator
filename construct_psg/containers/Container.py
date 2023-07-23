from dependency_injector.wiring import Provide, inject
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Configuration, Factory

from construct_psg.services.CommandLineService import CommandLineService
from construct_psg.services.LogService import LogService
from construct_psg.services.GeneratorService import GeneratorService
from construct_psg.services.ModuleLoaderService import ModuleLoaderService
from construct_psg.services.CaseConversionService import CaseConversionService

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
        commandLineService,
    )
