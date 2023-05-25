from dependency_injector.wiring import Provide, inject

from containers.Container import Container

from services.CommandLineService import CommandLineService
from services.ModuleLoaderService import ModuleLoaderService
from services.GeneratorService import GeneratorService

@inject
def main(
    moduleLoaderService: ModuleLoaderService = Provide[Container.moduleLoaderService],
    commandLineService: CommandLineService = Provide[Container.commandLineService],
    generatorService: GeneratorService = Provide[Container.generatorService],
):
    generatorService.generate(
        moduleLoaderService.construct(
            moduleLoaderService.loadModule(
                commandLineService.args.module,
                commandLineService.args.file,
            ),
            commandLineService.args.id,
        ),
        commandLineService.args.output,
        commandLineService.args.name,
    )

if __name__ == '__main__':
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    main()
