# Generated by construct-parser-serializer-generator (c) 2023 Alexander Kraus <nr4@z10.info>.
# Generation timestamp: {{ info.now }}
# Note: If you plan to edit this file, please reconsider your plan.

from construct import *
from typing import Any, Iterable
from enum import IntEnum
from .{{ info.module }} import {{ info.constructIdentifier }}
{%- if generatorService.joinEnumNames(info.subcon) != '' %}
from .{{ info.module }} import {{ generatorService.joinEnumNames(info.subcon) }}
{%- endif %}

{%- macro generate_binding(_tree, con) %}
class {{ caseConversionService.convertToPascal(con.name) }}:
    def __init__(self,
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
        {%- set name = key.split('.')[-1] %}
        {%- if generatorService.isEnum(key, _tree) %}
        {{ caseConversionService.convertToCamel(name) }}: {{ generatorService.pythonType(subcon) }} = {{ generatorService.pythonType(subcon) }}({{ generatorService.pythonDefaultValue(subcon) }}),
        {%- else %}
        {{ caseConversionService.convertToCamel(name) }}: {{ generatorService.pythonType(subcon) }} = {{ generatorService.pythonDefaultValue(subcon) }},
        {%- endif %}
    {%- endfor %}
    ) -> None:
        self._container = None
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
        {%- set name = key.split('.')[-1] %}
        {%- if generatorService.isEnum(key, _tree) %}
        self.{{ caseConversionService.convertToCamel(name) }} = {{ caseConversionService.convertToCamel(name) }}.value
        {%- elif generatorService.isArray(key, _tree) %}
        self.{{ caseConversionService.convertToCamel(name) }} = [] if {{ caseConversionService.convertToCamel(name) }} is None else {{ caseConversionService.convertToCamel(name) }}
        {%- else %}
        self.{{ caseConversionService.convertToCamel(name) }} = {{ caseConversionService.convertToCamel(name) }}
        {%- endif %}
    {%- endfor %}
    
    @staticmethod
    def parseFromContainer(container: Container) -> Any:
        instance = {{ caseConversionService.convertToPascal(con.name) }}()
        instance._container = container
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
        {%- set name = key.split('.')[-1] %}
        {%- if generatorService.isStruct(key, _tree) %}
        instance.{{ caseConversionService.convertToCamel(name) }} = {{ caseConversionService.convertToPascal(subcon.name) }}.parseFromContainer(container['{{ caseConversionService.convertToPascal(subcon.name) }}'])
        {%- elif generatorService.isArray(key, _tree) %}
        instance.{{ caseConversionService.convertToCamel(name) }} = list(map(
            {%- if generatorService.isStruct(key + '.' + caseConversionService.convertToSnake(subcon.subcon.name), generatorService.tree(subcon, key)) %}
            lambda child: {{ subcon.subcon.name }}.parseFromContainer(child),
            {%- else %}
            lambda child: child,
            {%- endif %}
            container['{{ caseConversionService.convertToPascal(name) }}'],
        ))
        {%- elif generatorService.isEnum(key, _tree) %}
        instance.{{ caseConversionService.convertToCamel(name) }} = {{ caseConversionService.convertToPascal(subcon.subcon.subcon.name) }}(int(container['{{ caseConversionService.convertToPascal(name) }}']))
        {%- else %}
        instance.{{ caseConversionService.convertToCamel(name) }} = container['{{ caseConversionService.convertToPascal(name) }}']
        {%- endif %}
    {%- endfor %}
        return instance

    def serializeToDict(self, convertEnumValues: bool = False) -> dict:
        return {
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
        {%- set name = key.split('.')[-1] %}
        {%- if generatorService.isStruct(key, _tree) %}
            '{{ caseConversionService.convertToPascal(name) }}': self.{{ caseConversionService.convertToCamel(name) }}.serializeToDict(convertEnumValues),
        {%- elif generatorService.isArray(key, _tree) %}
            '{{ caseConversionService.convertToPascal(name) }}': list(map(
            {%- if generatorService.isStruct(key + '.' + caseConversionService.convertToSnake(subcon.subcon.name), generatorService.tree(subcon, key)) %}
                lambda child: child.serializeToDict(convertEnumValues),
            {%- else %}
                lambda child: child,
            {%- endif %}
                self.{{ caseConversionService.convertToCamel(name) }},
            )),
        {%- elif generatorService.isEnum(key, _tree) %}
            '{{ caseConversionService.convertToPascal(name) }}': self.{{ caseConversionService.convertToCamel(name) }}.value if convertEnumValues else self.{{ caseConversionService.convertToCamel(name) }},
        {%- else %}
            '{{ caseConversionService.convertToPascal(name) }}': self.{{ caseConversionService.convertToCamel(name) }},
        {%- endif %}
    {%- endfor %}
        }

    JSONSchema = {
        "type": "object",
        "properties": {
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
        {%- set name = key.split('.')[-1] %}
        {%- if generatorService.isStruct(key, _tree) %}
            "{{ caseConversionService.convertToPascal(name) }}": {{ generatorService.schemaType(subcon) }}.JSONSchema,
        {%- elif generatorService.isEnum(key, _tree) %}
            "{{ caseConversionService.convertToPascal(name) }}": {
                "type": "string",
                "enum": [
            {%- for key, value in subcon.subcon.encmapping.items() %}
                    "{{ key }}",
            {%- endfor %}
                ],
            },
        {%- elif generatorService.isArray(key, _tree) %}
            "{{ caseConversionService.convertToPascal(name) }}": {
                "type": "array",
            {%- if generatorService.isStruct(key + '.' + caseConversionService.convertToSnake(subcon.subcon.name), generatorService.tree(subcon, key)) %}
                "items": {{ generatorService.schemaType(subcon) }}.JSONSchema,
            {%- else %}
                "items": {
                    "type": "{{ generatorService.schemaType(subcon.subcon) }}",
                },
            {%- endif %}
            },            
        {%- else %}
            "{{ caseConversionService.convertToPascal(name) }}": {
                "type": "{{ generatorService.schemaType(subcon) }}",
            },
        {%- endif %}
    {%- endfor %}
        },
        "required": [
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
        {%- set name = key.split('.')[-1] %}
            "{{ caseConversionService.convertToPascal(name) }}",
    {%- endfor %}
        ],
    }
{%- endmacro %}

# Python data bindings
{%- for _struct in generatorService.structStack(info.subcon) %}
    {{ generate_binding( generatorService.subtree(caseConversionService.convertToSnake(_struct.name), generatorService.tree(_struct)), _struct) }}
{%- endfor %}
