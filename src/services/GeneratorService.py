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
        name = ""
        if type(subcon) is Renamed:
            name = subcon.name
            subcon = subcon.subcon

        if type(subcon) is Struct:
            return self.caseConversionService.convertToSnake(name) + '_t'
        elif type(subcon) is FormatField:
            if subcon.fmtstr[0] == '=':
                prefix = 'u' if subcon.fmtstr[1].isupper() else ''
                if subcon.sizeof() == 1:
                    return prefix + 'int8_t'
                elif subcon.sizeof() == 2:
                    return prefix + 'int16_t'
                elif subcon.sizeof() == 4:
                    return prefix + 'int32_t'
        elif type(subcon) == StringEncoded:
            return 'char *'

    def hasComputableSize(self, subcon: Subconstruct) -> bool:
        try:
            subcon.sizeof()
            return True
        except SizeofError:
            return False

    def computableSize(self, subcon: Subconstruct, size: int = 0) -> int:
        if self.hasComputableSize(subcon):
            size += subcon.sizeof()
        else:
            if 'subcon' in dir(subcon):
                size = self.computableSize(subcon.subcon, size)
            if 'subcons' in dir(subcon):
                for subsubcon in subcon.subcons:
                    size = self.computableSize(subsubcon, size)
        return size
    
    def tree(self, subcon: Subconstruct, tree: str = "", serial: Iterable = None) -> dict:
        if serial is None:
            serial = {}

        if type(subcon) is Renamed:
            tree += ('.' if tree != "" else "") + self.caseConversionService.convertToSnake(subcon.name)

        if type(subcon) in [
            FormatField,
            Bytes,
        ]:
            serial[tree] = subcon
        
        if 'subcon' in dir(subcon):
            serial = self.tree(subcon.subcon, tree, serial)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                serial = self.tree(subsubcon, tree, serial)

        return serial
    
    def this(self, tree: dict, identifier: str) -> dict:
        key = list(filter(
            lambda key: key.endswith(identifier),
            tree.keys(), 
        ))[0]
        return { key: tree[key] }
    
    def referencedSize(self, tree: dict, key: str) -> int:
        return list(self.this(tree, tree[key].length._Path__field).keys())[0]
    
    def instance(self, key: str, identifier: str) -> str:
        return  '->'.join([identifier, '.'.join(key.split('.')[1:])])
 
    def generate(self, subcon: Subconstruct, outputDir: str, outputBaseName: str) -> None:
        structStack = self.structStack(subcon)
        self.logService.log('Generated struct stack.', StatusStrings.Success)

        tree = self.tree(subcon)
        self.logService.log('Generated traversable tree.', StatusStrings.Success)

        class Info:
            def __init__(innerSelf) -> None:
                innerSelf.baseName = outputBaseName
                innerSelf.now = datetime.now()
                innerSelf.structStack = reversed(structStack)
                innerSelf.needsMalloc = not self.hasComputableSize(subcon)
                innerSelf.tree = tree
                innerSelf.subcon = subcon

        # Save source file
        with open(join(outputDir, '{}.c'.format(outputBaseName)), 'wt') as f:
            f.write(self.sourceTemplate.render(
                info=Info(),
                generatorService=self,
                caseConversionService=self.caseConversionService,
            ))
            f.close()
        self.logService.log('Generated source file.', StatusStrings.Success)

        # Save header file
        with open(join(outputDir, '{}.h'.format(outputBaseName)), 'wt') as f:
            f.write(self.headerTemplate.render(
                info=Info(),
                generatorService=self,
                caseConversionService=self.caseConversionService,
            ))
            f.close()
        self.logService.log('Generated header file.', StatusStrings.Success)
