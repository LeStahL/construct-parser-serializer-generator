from dependency_injector.wiring import inject
from enum import Enum

class Case(Enum):
    UNKNOWN_CASE = 0x0
    SNAKE_CASE = 0x1
    MACRO_CASE = 0x2
    PASCAL_CASE = 0x3
    KEBAB_CASE = 0x5
    CAMEL_CASE = 0x6

@inject
class CaseConversionService:
    def __init__(self) -> None:
        pass

    def hasUppercase(self, identifier: str) -> bool:
        for character in identifier:
            if character.upper() == character and not character.isnumeric():
                return True
        return False
    
    def hasLowercase(self, identifier: str) -> bool:
        for character in identifier:
            if character.lower() == character:
                return True
        return False

    def detect(self, identifier: str) -> Case:
        if identifier == '':
            return Case.UNKNOWN_CASE
        
        if '-' in identifier:
            if '_' in identifier or \
                self.hasUppercase():
                return Case.UNKNOWN_CASE
            
            return Case.KEBAB_CASE
        
        if '_' in identifier:
            if self.hasLowercase() and \
                not self.hasUppercase():
                return Case.SNAKE_CASE
            
            if self.hasUppercase() and \
                not self.hasLowercase():
                return Case.MACRO_CASE
            
            return Case.UNKNOWN_CASE
        
        if not self.hasLowercase(identifier[0]):
            return Case.PASCAL_CASE

        return Case.CAMEL_CASE
    
    def canConvert(self, fromCase: Case, toCase: Case) -> bool:
        return fromCase != Case.UNKNOWN_CASE and toCase != Case.UNKNOWN_CASE

    def convert(self, identifier: str, fromCase: Case, toCase: Case) -> str:
        # Determine parts
        parts = []
        if fromCase == Case.SNAKE_CASE or \
            fromCase == Case.MACRO_CASE:
            parts = identifier.split('_')
        elif fromCase == Case.KEBAB_CASE:
            parts = identifier.split('-')
        elif fromCase == Case.CAMEL_CASE or \
            fromCase == Case.PASCAL_CASE:
            if fromCase == Case.PASCAL_CASE:
                identifier = identifier[0].lower() + identifier[1:]
            
            part = ""
            for characterIndex in range(len(identifier)):
                if self.hasUppercase(identifier[characterIndex]):
                    parts.append(part)
                    part = ""
                part += identifier[characterIndex]
            parts.append(part)

        # Map parts to lowercase
        parts = list(map(
            lambda part: part.lower(),
            parts,
        ))

        # Construct new parts
        if toCase == Case.SNAKE_CASE:
            return '_'.join(parts)
        elif toCase == Case.KEBAB_CASE:
            return '-'.join(parts)
        elif toCase == Case.MACRO_CASE:
            return '_'.join(map(
                lambda part: part.upper(),
                parts,
            ))
        elif toCase == Case.PASCAL_CASE:
            return ''.join(map(
                lambda part: part[0].upper() + part[1:],
                parts,
            ))
        elif toCase == Case.CAMEL_CASE:
            pascal = ''.join(map(
                lambda part: part[0].upper() + part[1:],
                parts,
            ))
            pascal[0] = pascal[0].lower()
            return pascal

    def convertTo(self, identifier: str, toCase: Case) -> str:
        return self.convert(identifier, self.detect(identifier), toCase)
    
    def convertToSnake(self, identifier) -> str:
        return self.convertTo(identifier, Case.SNAKE_CASE)
    
    def convertToMacro(self, identifier) -> str:
        return self.convertTo(identifier, Case.MACRO_CASE)
