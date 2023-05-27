from dependency_injector.wiring import inject
from construct import *
from jinja2 import Environment, FileSystemLoader, select_autoescape
from os.path import join, dirname
from datetime import datetime
from typing import Iterable
from json import dumps

from services.LogService import LogService, StatusStrings
from services.CaseConversionService import CaseConversionService, Case

@inject
class GeneratorService:
    HeaderTemplate = 'Parser.h'
    SourceTemplate = 'Parser.c'

    UniqueIdentifierIndex = 0

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
        elif type(subcon) in [StringEncoded, Bytes]:
            return 'char *'
        elif type(subcon) is Array:
            return self.cType(subcon.subcon) + ' *'
        
        if 'subcon' in dir(subcon):
            return self.cType(subcon.subcon)
        
        return "void *"


    def hasComputableSize(self, subcon: Subconstruct) -> bool:
        if type(subcon) in [
            Array,
            Struct,
            StringEncoded,
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
        # if type(subcon) in [
        #     Struct,
        # ]:
            
        
        if maxdepth != 0:
            if depth > maxdepth:
                return size

        if depth == 0:
            print("====")
        print("Computable size", subcon, size, depth, maxdepth)

        
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
        print(tree)
        arrayList = list(filter(
            lambda _key: type(tree[_key]) is Array,
            tree.keys(),
        ))
        print(arrayList)
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
   
    def isArrayLike(self, key: str, tree: dict) -> bool:
        return self.isArray(key, tree) or self.isString(key, tree)

    def uniqueIdentifier(self) -> str:
        GeneratorService.UniqueIdentifierIndex += 1
        return "ra{}".format(GeneratorService.UniqueIdentifierIndex - 1)
    
    def tree(self, subcon: Subconstruct, tree: str = "", serial: Iterable = None) -> dict:
        if serial is None:
            serial = {}

        if type(subcon) is Renamed:
            tree += ('.' if tree != "" else "") + self.caseConversionService.convertToSnake(subcon.name)
            if type(subcon.subcon) in [
                FormatField,
                Bytes,
                Array,
                Struct,
            ]:
                serial[tree] = subcon

        if type(subcon) in [
            FormatField,
            Bytes,
            Array,
        ]:
            serial[tree] = subcon         
        
        if 'subcon' in dir(subcon):
            serial = self.tree(subcon.subcon, tree, serial)
        if 'subcons' in dir(subcon):
            for subsubcon in subcon.subcons:
                serial = self.tree(subsubcon, tree, serial)

        return serial
    
    def subtree(self, parent: str, tree: dict) -> dict:
        # print("Subtree", parent, tree)
        subKeys = list(filter(
            lambda key: key.startswith(parent) and key != parent and key.count('.') == parent.count('.') + 1,
            tree.keys(),
        ))
        # print("subtree subKeys", subKeys)
        result = {}
        for subKey in subKeys:
            result[subKey] = tree[subKey]
        # print("subtree",result)
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
    
    def referencedSize(self, tree: dict, key: str) -> int:
        # print(key, tree)
        # print(dir(tree[key]))
        if type(tree[key]) is Array:
            return list(self.this(tree, tree[key].count._Path__field).keys())[0]    
        else:
            return list(self.this(tree, tree[key].length._Path__field).keys())[0]
    
    def instance(self, key: str, identifier: str) -> str:
        return  '->'.join([identifier, '.'.join(key.split('.')[1:])])
 
    # def arrayList(self, subcon: Subconstruct) -> Iterable:


    def generate(self, subcon: Subconstruct, outputDir: str, outputBaseName: str) -> None:
        structStack = self.structStack(subcon)
        self.logService.log('Generated struct stack.', StatusStrings.Success)

        tree = self.tree(subcon)
        self.logService.log('Generated traversable tree.', StatusStrings.Success)

        # self.printSubconstruct(subcon)
        # print(self.tree(subcon))

        class Info:
            def __init__(innerSelf) -> None:
                innerSelf.baseName = outputBaseName
                innerSelf.now = datetime.now()
                innerSelf.structStack = list(reversed(structStack))
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
