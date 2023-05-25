from dependency_injector.wiring import inject
from construct import *
from jinja2 import Environment, FileSystemLoader, select_autoescape
from os.path import join, dirname
from datetime import datetime
from typing import Iterable

from services.LogService import LogService, StatusStrings
from services.CaseConversionService import CaseConversionService, Case

@inject
class GeneratorService:
    HeaderTemplate = 'Parser.h'
    SourceTemplate = 'Parser.c'

    def __init__(self,
        logService: LogService,
        caseConversionService: CaseConversionService,
    ) -> None:
        super().__init__()

        self.logService = logService
        self.caseConversionService = caseConversionService

        self.environment = Environment(
            loader=FileSystemLoader(join(dirname(__file__), '..', 'templates')),
            autoescape=select_autoescape(),
        )
        self.sourceTemplate = self.environment.get_template(GeneratorService.SourceTemplate)
        self.headerTemplate = self.environment.get_template(GeneratorService.HeaderTemplate)

    def printSubconstruct(self, subcon: Subconstruct, depth=0):
        print(' ' * depth + '{}, {}'.format(subcon, type(subcon)))
        if 'subcon' in dir(subcon):
            self.printSubconstruct(subcon.subcon, depth+1)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                self.printSubconstruct(subsubcon, depth+1)

    def structStack(self, subcon: Subconstruct, stack: Iterable = []):
        if type(subcon) is Renamed and type(subcon.subcon) is Struct:
            stack.append(subcon)

        if 'subcon' in dir(subcon):
            stack = self.structStack(subcon.subcon, stack)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                stack = self.structStack(subsubcon, stack)
        
        return stack
    
    def cType(self, subcon: Subconstruct) -> str:
        if type(subcon) is Renamed:
            if type(subcon.subcon) is Struct:
                return subcon.name + '_t'
            elif type(subcon.subcon) is FormatField:
                print(subcon.subcon.fmtstr, subcon.subcon.sizeof(), subcon.subcon.length)
                if subcon.subcon.fmtstr[0] == '=':
                    prefix = 'u' if subcon.subcon.fmtstr[1].isupper() else ''
                    if subcon.subcon.sizeof() == 1:
                        return prefix + 'int8_t'
                    elif subcon.subcon.sizeof() == 2:
                        return prefix + 'int16_t'
                    elif subcon.subcon.sizeof() == 4:
                        return prefix + 'int32_t'

    def generate(self, subcon: Subconstruct, outputDir: str, outputBaseName: str) -> None:
        fromCase = self.caseConversionService.detect(outputBaseName)
        if not self.caseConversionService.canConvert(
            fromCase,
            Case.MACRO_CASE,
        ):
            self.logService.log('Can not convert parser name to MACRO_CASE: {}.'.format(outputBaseName), StatusStrings.Error)
        if not self.caseConversionService.canConvert(
            fromCase,
            Case.SNAKE_CASE,
        ):
            self.logService.log('Can not convert parser name to SNAKE_CASE: {}.'.format(outputBaseName), StatusStrings.Error)
        
        structStack = self.structStack(subcon)

        class Info:
            def __init__(innerSelf) -> None:
                innerSelf.nameUpperCase = self.caseConversionService.convert(outputBaseName, fromCase, Case.MACRO_CASE)
                innerSelf.nameSnakeCase = self.caseConversionService.convert(outputBaseName, fromCase, Case.SNAKE_CASE)
                innerSelf.baseName = outputBaseName
                innerSelf.size = subcon.sizeof()
                innerSelf.now = datetime.now()
                innerSelf.structStack = reversed(structStack)

        self.printSubconstruct(subcon)

        
        # print("====")
        # for struct in :
            # print(struct.name)
            # self.printSubconstruct(struct)
            # print("====")

        # Save source file
        with open(join(outputDir, '{}.c'.format(outputBaseName)), 'wt') as f:
            f.write(self.sourceTemplate.render(
                info=Info(),
                generatorService=self,
            ))
            f.close()

        # Save header file
        with open(join(outputDir, '{}.h'.format(outputBaseName)), 'wt') as f:
            f.write(self.headerTemplate.render(
                info=Info(),
                generatorService=self,
            ))
            f.close()
        
        # print(subcon.subcons[0].name)
        # print(dir(subcon))
