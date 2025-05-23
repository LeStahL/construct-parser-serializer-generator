from dependency_injector.wiring import inject
from construct import *
from jinja2 import Environment, FileSystemLoader, select_autoescape
from os.path import join, dirname
from datetime import datetime
from typing import Iterable
from json import dumps
from typing import Any

from construct_psg.services.LogService import LogService, StatusStrings
from construct_psg.services.CaseConversionService import CaseConversionService, Case
from construct_psg.services.CommandLineService import CommandLineService

@inject
class GeneratorService:
    HeaderTemplate = 'Parser.h'
    SourceTemplate = 'Parser.c'
    PythonTemplate = 'Parser.py'
    ShaderTemplate = 'Parser.frag'

    UniqueIdentifierIndex = 0

    def __init__(self,
        logService: LogService,
        caseConversionService: CaseConversionService,
        commandLineService: CommandLineService,
    ) -> None:
        super().__init__()

        self.logService = logService
        self.caseConversionService = caseConversionService
        self.commandLineService = commandLineService

        self.environment = Environment(
            loader=FileSystemLoader(join(dirname(__file__), '..', 'templates')),
            autoescape=select_autoescape(),
        )
        self.sourceTemplate = self.environment.get_template(GeneratorService.SourceTemplate)
        self.headerTemplate = self.environment.get_template(GeneratorService.HeaderTemplate)
        self.pythonTemplate = self.environment.get_template(GeneratorService.PythonTemplate)
        self.shaderTemplate = self.environment.get_template(GeneratorService.ShaderTemplate)

    def printSubconstruct(self, subcon: Subconstruct, depth=0):
        print(' ' * depth + '{}, {}'.format(subcon, type(subcon)))
        if 'subcon' in dir(subcon):
            self.printSubconstruct(subcon.subcon, depth+1)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                self.printSubconstruct(subsubcon, depth+1)

    def structStack(self, subcon: Subconstruct, stack: Iterable = None):
        if stack is None:
            stack = []
        if type(subcon) is Renamed and \
            type(subcon.subcon) in [Struct]:
            for knownSucon in stack:
                if knownSucon.name == subcon.name:
                    stack.remove(knownSucon)
            stack = [subcon] + stack

        if 'subcon' in dir(subcon):
            stack = self.structStack(subcon.subcon, stack)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                stack = self.structStack(subsubcon, stack)
        
        return stack
    
    def enumStack(self, subcon: Subconstruct, stack: Iterable = None):
        if stack is None:
            stack = []
        if type(subcon) is Renamed and \
            type(subcon.subcon) in [Enum]:
            for knownSucon in stack:
                if knownSucon.name == subcon.name:
                    stack.remove(knownSucon)
            stack = [subcon] + stack

        if 'subcon' in dir(subcon):
            stack = self.enumStack(subcon.subcon, stack)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                stack = self.enumStack(subsubcon, stack)

        return stack

    def structEnumStack(self, subcon: Subconstruct, stack: Iterable = None):
        if stack is None:
            stack = []
        if type(subcon) is Renamed and \
            type(subcon.subcon) in [Struct, Enum]:
            for knownSucon in stack:
                if knownSucon.name == subcon.name:
                    stack.remove(knownSucon)
            stack = [subcon] + stack

        if 'subcon' in dir(subcon):
            stack = self.structEnumStack(subcon.subcon, stack)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                stack = self.structEnumStack(subsubcon, stack)

        return stack

    def cType(self, subcon: Subconstruct) -> str:
        name = ""
        if type(subcon) is Renamed:
            name = subcon.name
            subcon = subcon.subcon

        if type(subcon) in [Struct, Enum]:
            return self.caseConversionService.convertToSnake(name) + '_t'
        elif type(subcon) is FormatField:
            if subcon.fmtstr[0] in ['=', '<', '>']:
                prefix = 'u' if subcon.fmtstr[1].isupper() else ''
                if subcon.fmtstr[1].lower() in 'blhic':
                    if subcon.sizeof() == 1:
                        return prefix + 'int8_t'
                    elif subcon.sizeof() == 2:
                        return prefix + 'int16_t'
                    elif subcon.sizeof() == 4:
                        return prefix + 'int32_t'
                elif subcon.fmtstr[1].lower() in 'efd':
                    if subcon.sizeof() == 4:
                        return 'float'
                    elif subcon.sizeof() == 8:
                        return 'double'
        elif type(subcon) in [StringEncoded, Bytes]:
            return 'char *'
        elif type(subcon) is Array:
            return self.cType(subcon.subcon) + ' *'

        if 'subcon' in dir(subcon):
            return self.cType(subcon.subcon)

        return "void *"
    
    def cFormatString(self, subcon: Subconstruct) -> str:
        if type(subcon) is Renamed:
            subcon = subcon.subcon

        if type(subcon) is FormatField:
            if subcon.fmtstr[0] in ['=', '<', '>']:
                if subcon.fmtstr[1] == 'h':
                    return '%hd'
                elif subcon.fmtstr[1] == 'H':
                    return '%hu'
                elif subcon.fmtstr[1] == 'i':
                    return '%d'
                elif subcon.fmtstr[1] == 'I':
                    return '%u'
                elif subcon.fmtstr[1] == 'l':
                    return '%ld'
                elif subcon.fmtstr[1] == 'L':
                    return '%lu'
                elif subcon.fmtstr[1] == 'q':
                    return '%lld'
                elif subcon.fmtstr[1] == 'Q':
                    return '%llu'
                elif subcon.fmtstr[1] == 'f':
                    return '%e'
                elif subcon.fmtstr[1] == 'd':
                    return '%le'

    def glslType(self, subcon: Subconstruct) -> str:
        name = ""
        if type(subcon) is Renamed:
            name = subcon.name
            subcon = subcon.subcon

        if type(subcon) is Struct:
            return self.caseConversionService.convertToSnake(name) + '_t'
        elif type(subcon) is Enum:
            return 'int'
        elif type(subcon) is FormatField:
            if subcon.fmtstr[0] in ['=', '<', '>']:
                prefix = 'u' if subcon.fmtstr[1].isupper() else ''
                return prefix + 'int'
        elif type(subcon) in [StringEncoded, Bytes]:
            return 'int[MAX_ARRAY_SIZE]'
        elif type(subcon) is Array:
            return self.glslType(subcon.subcon) + '[MAX_ARRAY_SIZE]'

        if 'subcon' in dir(subcon):
            return self.glslType(subcon.subcon)

        return "void *"

    def pythonType(self, subcon: Subconstruct) -> str:
        name = ""
        if type(subcon) is Renamed:
            name = subcon.name
            subcon = subcon.subcon

        if type(subcon) is Struct:
            return self.caseConversionService.convertToPascal(name)
        elif type(subcon) is Enum:
            return self.caseConversionService.convertToPascal(subcon.subcon.name)
        elif type(subcon) is FormatField and (
            'b' in subcon.fmtstr.lower() or
            'h' in subcon.fmtstr.lower() or
            'l' in subcon.fmtstr.lower() or
            'q' in subcon.fmtstr.lower()
        ):
            return 'int'
        elif type(subcon) is FormatField and (
            'e' in subcon.fmtstr.lower() or
            'f' in subcon.fmtstr.lower() or
            'd' in subcon.fmtstr.lower()
        ):
            return 'float'
        elif type(subcon) in [StringEncoded, Bytes]:
            return 'str'
        elif type(subcon) is Array:
            return 'Optional[list[' + self.pythonType(subcon.subcon) + ']]'

        if 'subcon' in dir(subcon):
            return self.pythonType(subcon.subcon)

        return "Any"
    
    def pythonDefaultValue(self, subcon: Subconstruct) -> Any:
        name = ""
        if type(subcon) is Renamed:
            name = subcon.name
            subcon = subcon.subcon

        if type(subcon) is Struct:
            return self.caseConversionService.convertToPascal(name) + '()'
        elif type(subcon) is FormatField and (
            'b' in subcon.fmtstr.lower() or
            'h' in subcon.fmtstr.lower() or
            'l' in subcon.fmtstr.lower() or
            'q' in subcon.fmtstr.lower()
        ):
            return '0'
        elif type(subcon) is FormatField and (
            'e' in subcon.fmtstr.lower() or
            'f' in subcon.fmtstr.lower() or
            'd' in subcon.fmtstr.lower()
        ):
            return '0.0'
        elif type(subcon) is Enum:
            return '0'
        elif type(subcon) in [StringEncoded, Bytes]:
            return "''"
        elif type(subcon) is Array:
            return 'None'
        
        if 'subcon' in dir(subcon):
            return self.pythonType(subcon.subcon)
        
        return 'None'

    def schemaType(self, subcon: Subconstruct) -> str:
        name = ""
        if type(subcon) is Renamed:
            name = subcon.name
            subcon = subcon.subcon

        if type(subcon) in [Struct, Enum]:
            return self.caseConversionService.convertToPascal(name)
        elif type(subcon) is FormatField:
            return 'integer'
        elif type(subcon) in [StringEncoded, Bytes]:
            return 'string'

        if 'subcon' in dir(subcon):
            return self.schemaType(subcon.subcon)

        return "null"

    def hasArrayInSubtree(self, subcon: Subconstruct) -> bool:
        if type(subcon) in [
            Array,
            StringEncoded,
        ]:
            return True
        
        if 'subcon' in dir(subcon):
            return self.hasArrayInSubtree(subcon.subcon)
        elif 'subcons' in dir(subcon):
            result = False
            for subsubcon in subcon.subcons:
                result = result or self.hasArrayInSubtree(subsubcon)
            return result
        
        return False

    def hasComputableSize(self, subcon: Subconstruct) -> bool:
        if type(subcon) in [
            Array,
            Struct,
            StringEncoded,
            Enum,
        ]:
            return False
        
        if type(subcon) in [
            FormatField,
        ]:
            return True

        if 'subcon' in dir(subcon):
            return self.hasComputableSize(subcon.subcon)
        elif 'subcons' in dir(subcon):
            result = True
            for subsubcon in subcon.subcons:
                result = result and self.hasComputableSize(subsubcon)
            return result

        return False

    def computableSize(self, subcon: Subconstruct, size: int = 0, depth=0, maxdepth=0) -> int:
        if maxdepth != 0:
            if depth > maxdepth:
                return size
        
        if type(subcon) in [
            FormatField,
        ]:
            size += subcon.sizeof()
        else:
            if 'subcon' in dir(subcon):
                size = self.computableSize(subcon.subcon, size, depth + 1)
            if 'subcons' in dir(subcon):
                for subsubcon in subcon.subcons:
                    size = self.computableSize(subsubcon, size, depth + 1)

        return size
    
    def isInArray(self, key: str, tree: dict) -> bool:
        arrayList = list(filter(
            lambda _key: type(tree[_key]) is Array,
            tree.keys(),
        ))
        result = False
        groups = key.split('.')
        while len(groups) > 0:
            result = result or ('.'.join(groups) in arrayList)
            groups = groups[:-1]
        return result
    
    def isType(self, key: str, tree: dict, _types: Iterable) -> bool:
        typeList = list(filter(
            lambda _key: type(tree[_key]) in _types,
            tree.keys(),
        ))
        return key in typeList

    def isArray(self, key: str, tree: dict) -> bool:
        return self.isType(key, tree, [Array])
    
    def isString(self, key: str, tree: dict) -> bool:
        return self.isType(key, tree, [StringEncoded, Bytes])
    
    def isStruct(self, key: str, tree: dict) -> bool:
        return type(tree[key]) is Renamed and type(tree[key].subcon) is Struct

    def isInt(self, key: str, tree: dict) -> bool:
        return type(tree[key]) is FormatField and (
            'b' in tree[key].fmtstr.lower() or
            'h' in tree[key].fmtstr.lower() or
            'l' in tree[key].fmtstr.lower() or
            'q' in tree[key].fmtstr.lower()
        )

    def isFloat(self, key: str, tree: dict) -> bool:
        return type(tree[key]) is FormatField and (
            'e' in tree[key].fmtstr.lower() or
            'f' in tree[key].fmtstr.lower() or
            'd' in tree[key].fmtstr.lower()
        )

    def _isStruct(self, subcon: Subconstruct) -> bool:
        return type(subcon) == Struct

    def isArrayLike(self, key: str, tree: dict) -> bool:
        return self.isArray(key, tree) or self.isString(key, tree)

    def isEnum(self, key: str, tree: dict) -> bool:
        return type(tree[key]) is Renamed and type(tree[key].subcon) is Enum

    def uniqueIdentifier(self) -> str:
        GeneratorService.UniqueIdentifierIndex += 1
        return "ra{}".format(GeneratorService.UniqueIdentifierIndex - 1)
    
    def tree(self, subcon: Subconstruct, tree: str = "", serial: dict = None) -> dict:
        if serial is None:
            serial = {}

        if type(subcon) is Renamed:
            tree += ('.' if tree != "" else "") + self.caseConversionService.convertToSnake(subcon.name)

            if type(subcon.subcon) in [
                FormatField,
                Bytes,
                Array,
                Struct,
                Enum,
            ]:
                serial[tree] = subcon

        if type(subcon) in [
            FormatField,
            Bytes,
            Array,
        ]:
            serial[tree] = subcon

        if type(subcon) is Enum:
            return serial

        if 'subcon' in dir(subcon):
            serial = self.tree(subcon.subcon, tree, serial)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                serial = self.tree(subsubcon, tree, serial)

        return serial
    
    def subtree(self, parent: str, tree: dict) -> dict:
        subKeys = list(filter(
            lambda key: key.startswith(parent) and key != parent and key.count('.') == parent.count('.') + 1,
            tree.keys(),
        ))
        result = {}
        for subKey in subKeys:
            result[subKey] = tree[subKey]
        return result
    
    def this(self, tree: dict, identifier: str) -> dict:
        identifier = self.caseConversionService.convertToSnake(identifier)
        endList = list(filter(
            lambda key: key.endswith(identifier),
            tree.keys(), 
        ))
        if len(endList) < 1:
            self.logService.log('Identifier {} not in tree {}.'.format(identifier, tree), StatusStrings.Error)
        key = endList[0]
        return { key: tree[key] }
    
    def joinEnumNames(self, subcon: Subconstruct) -> str:
        return ', \\\n    '.join(map(lambda _enum: _enum.subcon.subcon.name, self.enumStack(subcon)))

    def referencedSize(self, tree: dict, key: str) -> int:
        if type(tree[key]) is Array:
            return list(self.this(tree, tree[key].count._Path__field).keys())[0]
        else:
            return list(self.this(tree, tree[key].length._Path__field).keys())[0]
    
    def instance(self, key: str, identifier: str) -> str:
        return  '->'.join([identifier, '.'.join(key.split('.')[1:])])
 
    def generate(self, subcon: Subconstruct, outputDir: str, outputBaseName: str) -> None:
        self.logService.log('Generated struct stack.', StatusStrings.Success)

        tree = self.tree(subcon)
        self.logService.log('Generated traversable tree.', StatusStrings.Success)

        class Info:
            def __init__(innerSelf) -> None:
                innerSelf.baseName = outputBaseName
                innerSelf.module = self.commandLineService.args.module
                innerSelf.constructIdentifier = self.commandLineService.args.id
                innerSelf.now = datetime.now()
                innerSelf.tree = tree
                innerSelf.subcon = subcon

        if self.commandLineService.args.python:
            # Save Python data bindings.
            with open(join(outputDir, '{}.py'.format(outputBaseName)), 'wt') as f:
                f.write(self.pythonTemplate.render(
                    info=Info(),
                    generatorService=self,
                    logService=self.logService,
                    caseConversionService=self.caseConversionService,
                ))
                f.close()
            self.logService.log('Generated Python data binding module file.', StatusStrings.Success)
        elif self.commandLineService.args.shader:
            # Save shader file.
            with open(join(outputDir, '{}.frag'.format(outputBaseName)), 'wt') as f:
                f.write(self.shaderTemplate.render(
                    info=Info(),
                    generatorService=self,
                    logService=self.logService,
                    caseConversionService=self.caseConversionService,
                ))
                f.close()
            self.logService.log('Generated shader file.', StatusStrings.Success)
        else:
            # Save source file
            with open(join(outputDir, '{}.c'.format(outputBaseName)), 'wt') as f:
                f.write(self.sourceTemplate.render(
                    info=Info(),
                    generatorService=self,
                    logService=self.logService,
                    caseConversionService=self.caseConversionService,
                ))
                f.close()
            self.logService.log('Generated source file.', StatusStrings.Success)

            # Save header file
            with open(join(outputDir, '{}.h'.format(outputBaseName)), 'wt') as f:
                f.write(self.headerTemplate.render(
                    info=Info(),
                    generatorService=self,
                    logService=self.logService,
                    caseConversionService=self.caseConversionService,
                ))
                f.close()
            self.logService.log('Generated header file.', StatusStrings.Success)
