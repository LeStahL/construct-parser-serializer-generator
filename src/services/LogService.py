from dependency_injector.wiring import inject
from termcolor import colored
from enum import Enum
from datetime import datetime
from traceback import print_exc
from sys import exit, exc_info

from services.CommandLineService import CommandLineService

class StatusStrings(Enum):
    Error = 'red'
    Warning = 'yellow'
    Information = 'cyan'
    Success = 'green'
    Message = 'white'

@inject
class LogService:
    def __init__(self,
        commandLineService: CommandLineService,
    ) -> None:
        super().__init__()

        self.commandLineService = commandLineService

    def log(self, message: str, status: StatusStrings, exitOnError: bool = True) -> None:
        if self.commandLineService.args.verbose or status == StatusStrings.Error:
            print('{} - {}: {}'.format(
                colored(str(datetime.now()), StatusStrings.Message.value),
                colored(status.name, status.value),
                colored(message, StatusStrings.Message.value),
            ))
            if status == StatusStrings.Error:
                (_type, exception, traceback) = exc_info()
                if traceback is not None:
                    print_exc()

                if exitOnError:
                    exit(1)
