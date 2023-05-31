/* 
 * Generated by construct-parser-serializer-generator (c) 2023 Alexander Kraus <nr4@z10.info>.
 * Generation timestamp: {{ info.now }}
 * Note: If you plan to edit this file, please reconsider your plan.
 */

{%- macro generate_sizeof(_tree, con) %}
size_t sizeof_{{ caseConversionService.convertToSnake(con.name) }}_t({{ caseConversionService.convertToSnake(con.name) }}_t *instance) {
    size_t result = 0;
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
    // {{ key }} with type {{ generatorService.cType(subcon) }}:
        {%- if generatorService.hasComputableSize(subcon) %}
    result += {{ generatorService.computableSize(subcon) }};
        {%- else %}
            {%- if generatorService.isArrayLike(key, _tree) %}
    result += {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }};
            {%- elif generatorService.isStruct(key, _tree) %}
    result += sizeof_{{ generatorService.cType(subcon) }}(&{{ generatorService.instance(key, 'instance') }});
            {%- elif generatorService.isEnum(key, _tree) %}
    result += {{ generatorService.computableSize(subcon) }};
            {%- else %}
    // Unhandled @ {{ key }} / {{ subcon }}
            {%- endif %}
        {%- endif %}
    {%- endfor %}
    return result;
}
{%- endmacro %}

{%- macro generate_parser(_tree, con) %}
void parse_{{ caseConversionService.convertToSnake(con.name) }}_t({{ caseConversionService.convertToSnake(con.name) }}_t *instance, uint8_t *source) {
    size_t offset = 0;
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
    // {{ key }} with type {{ generatorService.cType(subcon) }}:
        {%- if generatorService.hasComputableSize(subcon) %}
    {{ generatorService.instance(key, 'instance') }} = *({{ generatorService.cType(subcon) }} *)(source + offset);
    offset += {{ generatorService.computableSize(subcon) }};
        {%- else %}
            {%- if generatorService.isString(key, _tree) %}
    {{ generatorService.instance(key, 'instance') }} = (char *) malloc({{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }});
    memcpy({{ generatorService.instance(key, 'instance') }}, source + offset, {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }});
    offset += {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }};
            {%- elif generatorService.isArray(key, _tree) %}
                {%- set index = generatorService.uniqueIdentifier() %}
                {%- set element_size_id = generatorService.uniqueIdentifier() %}
    size_t {{ element_size_id }} = sizeof_{{ caseConversionService.convertToSnake(subcon.subcon.name) }}_t({{ generatorService.instance(key, 'instance') }});
    {{ generatorService.instance(key, 'instance') }} = ({{ generatorService.cType(subcon) }}) malloc({{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }} * sizeof({{ generatorService.cType(subcon.subcon) }}));
                {%- if generatorService.isStruct(key + '.' + caseConversionService.convertToSnake(subcon.subcon.name), generatorService.tree(subcon, key)) %}
    for(size_t {{ index }} = 0; {{ index }} < {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }}; ++{{ index }}) {
        parse_{{ caseConversionService.convertToSnake(subcon.subcon.name) }}_t({{ generatorService.instance(key, 'instance') }} + {{ index }}, source + offset + {{ index }} * {{ element_size_id }});
    }
                {%- else %}
    memcpy({{ generatorService.instance(key, 'instance') }}, source + offset, {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }});
                {% endif %}
    offset += {{ element_size_id }} * {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }};
            {%- elif generatorService.isStruct(key, _tree) %}
    parse_{{ generatorService.cType(subcon) }}(&{{ generatorService.instance(key, 'instance') }}, source + offset);
    offset += sizeof_{{ generatorService.cType(subcon) }}(&{{ generatorService.instance(key, 'instance') }});
            {%- elif generatorService.isEnum(key, _tree) %}
    {{ generatorService.instance(key, 'instance') }} = ({{ generatorService.cType(subcon) }})*({{ generatorService.cType(subcon.subcon.subcon) }} *)(source + offset);
    offset += {{ generatorService.computableSize(subcon) }};
            {%- else %}
    // Unhandled @ {{ key }} / {{ subcon }}
            {%- endif %}
        {%- endif %}
    {%- endfor %}
}
{%- endmacro %}

{%- macro generate_serializer(_tree, con) %}
void serialize_{{ caseConversionService.convertToSnake(con.name) }}_t({{ caseConversionService.convertToSnake(con.name) }}_t *instance, uint8_t *target) {
    size_t offset = 0;
    {%- for key in _tree %}
        {%- set subcon = _tree[key] %}
    // {{ key }} with type {{ generatorService.cType(subcon) }}:
        {%- if generatorService.hasComputableSize(subcon) %}
    *({{ generatorService.cType(subcon) }} *)(target + offset) = {{ generatorService.instance(key, 'instance') }};
    offset += {{ generatorService.computableSize(subcon) }};
        {%- else %}
            {%- if generatorService.isString(key, _tree) %}
    memcpy(target + offset, {{ generatorService.instance(key, 'instance') }}, {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }});
    offset += {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }};
            {%- elif generatorService.isArray(key, _tree) %}
                {%- set index = generatorService.uniqueIdentifier() %}
                {%- set element_size_id = generatorService.uniqueIdentifier() %}
    size_t {{ element_size_id }} = sizeof_{{ caseConversionService.convertToSnake(subcon.subcon.name) }}_t({{ generatorService.instance(key, 'instance') }});
                {%- if generatorService.isStruct(key + '.' + caseConversionService.convertToSnake(subcon.subcon.name), generatorService.tree(subcon, key)) %}
    for(size_t {{ index }} = 0; {{ index }} < {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }}; ++{{ index }}) {
        serialize_{{ caseConversionService.convertToSnake(subcon.subcon.name) }}_t({{ generatorService.instance(key, 'instance') }} + {{ index }}, target + offset + {{ index }} * {{ element_size_id }});
    }
                {%- else %}
    memcpy(target + offset, {{ generatorService.instance(key, 'instance') }}, {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }});
                {% endif %}
    offset += {{ element_size_id }} * {{ generatorService.instance(generatorService.referencedSize(_tree, key), 'instance') }};
            {%- elif generatorService.isStruct(key, _tree) %}
    serialize_{{ generatorService.cType(subcon) }}(&{{ generatorService.instance(key, 'instance') }}, target + offset);
    offset += sizeof_{{ generatorService.cType(subcon) }}(&{{ generatorService.instance(key, 'instance') }});
            {%- elif generatorService.isEnum(key, _tree) %}
    *({{ generatorService.cType(subcon.subcon.subcon) }} *)(target + offset) = ({{ generatorService.cType(subcon.subcon.subcon) }}){{ generatorService.instance(key, 'instance') }};
    offset += {{ generatorService.computableSize(subcon) }};
            {%- else %}
    // Unhandled @ {{ key }} / {{ subcon }}
            {%- endif %}
        {%- endif %}
    {%- endfor %}
}
{%- endmacro %}

#ifndef {{ caseConversionService.convertToMacro(info.baseName) }}_C
#define {{ caseConversionService.convertToMacro(info.baseName) }}_C

#ifndef {{ caseConversionService.convertToMacro(info.baseName) }}_HEADER_ONLY
#include "{{ info.baseName }}.h"
#endif /* {{ caseConversionService.convertToMacro(info.baseName) }}_HEADER_ONLY */

{%- if not generatorService.hasComputableSize(info.subcon) %}
#include <stdlib.h>
{%- endif %}

#ifdef {{ caseConversionService.convertToMacro(info.baseName) }}_SIZEOF
// Sizeof-related implementations.
{%- for _struct in generatorService.structStack(info.subcon) %}
    {{ generate_sizeof( generatorService.subtree(caseConversionService.convertToSnake(_struct.name), generatorService.tree(_struct)), _struct) }}
{%- endfor %}
#endif /* {{ caseConversionService.convertToMacro(info.baseName) }}_SIZEOF */

#ifdef {{ caseConversionService.convertToMacro(info.baseName) }}_PARSER
// Parser-related implementations.
{%- for _struct in generatorService.structStack(info.subcon) %}
    {{ generate_parser( generatorService.subtree(caseConversionService.convertToSnake(_struct.name), generatorService.tree(_struct)), _struct) }}
{%- endfor %}
#endif /* {{ caseConversionService.convertToMacro(info.baseName) }}_PARSER */

#ifdef {{ caseConversionService.convertToMacro(info.baseName) }}_SERIALIZER
// Serializer-related implementations.
{%- for _struct in generatorService.structStack(info.subcon) %}
    {{ generate_serializer( generatorService.subtree(caseConversionService.convertToSnake(_struct.name), generatorService.tree(_struct)), _struct) }}
{%- endfor %}
#endif /* {{ caseConversionService.convertToMacro(info.baseName) }}_SERIALIZER */

#endif /* {{ caseConversionService.convertToMacro(info.baseName) }}_C */
