from dependency_injector.wiring import Provide, inject

from construct_psg.containers.Container import Container

from construct_psg.services.CommandLineService import CommandLineService
from construct_psg.services.ModuleLoaderService import ModuleLoaderService
from construct_psg.services.GeneratorService import GeneratorService

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
