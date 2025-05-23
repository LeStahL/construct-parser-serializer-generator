/* 
 * Generated by construct-parser-serializer-generator (c) 2023 Alexander Kraus <nr4@z10.info>.
 * Generation timestamp: 2025-05-02 13:23:45.391291
 * Note: If you plan to edit this file, please reconsider your plan.
 */

#pragma once

#include <stdint.h>
#ifdef __linux__
#include <stddef.h>
#endif // __linux__
    
typedef enum {
    TEXTURE_INTERNAL_FORMAT_SCREEN = 0,
    TEXTURE_INTERNAL_FORMAT_RGBA32F = 1,
    TEXTURE_INTERNAL_FORMAT_RG32F = 2,
    TEXTURE_INTERNAL_FORMAT_RGBA = 3,
    TEXTURE_INTERNAL_FORMAT_RGBA8 = 4,
    TEXTURE_INTERNAL_FORMAT_R32F = 5,
    TEXTURE_INTERNAL_FORMAT_RGB8 = 6
} texture_internal_format_t;
    
typedef struct {
    uint8_t struct_entry;
    char * this_a_string;
    uint8_t nested_array_size;
    uint8_t * nested_array;
    texture_internal_format_t texture_internal_format;
} array_content_t;
    
typedef struct {
    uint32_t other_data;
    int32_t more_data;
} sub_struct_t;
    
typedef struct {
    uint8_t data;
    sub_struct_t sub_struct;
    uint32_t size;
    char * string;
    uint32_t array_size;
    array_content_t * we_need_array_support;
    float floats_are_cool;
} example_format_t;

#ifdef EXAMPLE_FORMAT_SIZEOF
// Sizeof-related forward declarations.
size_t sizeof_array_content_t(array_content_t *);
size_t sizeof_sub_struct_t(sub_struct_t *);
size_t sizeof_example_format_t(example_format_t *);
#endif /* EXAMPLE_FORMAT_SIZEOF */

#ifdef EXAMPLE_FORMAT_PARSER
// Parser-related forward declarations.
void parse_array_content_t(array_content_t *, uint8_t *);
void parse_sub_struct_t(sub_struct_t *, uint8_t *);
void parse_example_format_t(example_format_t *, uint8_t *);
#endif /* EXAMPLE_FORMAT_PARSER */

#ifdef EXAMPLE_FORMAT_SERIALIZER
// Serializer-related forward declarations.
void serialize_array_content_t(array_content_t *, uint8_t *);
void serialize_sub_struct_t(sub_struct_t *, uint8_t *);
void serialize_example_format_t(example_format_t *, uint8_t *);
#endif /* EXAMPLE_FORMAT_SERIALIZER */

#ifdef EXAMPLE_FORMAT_DESTRUCTOR
// Destructor-related forward declarations
void free_array_content_t(array_content_t *);
void free_sub_struct_t(sub_struct_t *);
void free_example_format_t(example_format_t *);
#endif /* EXAMPLE_FORMAT_DESTRUCTOR */

#ifdef EXAMPLE_FORMAT_HEADER_ONLY
#include "exampleFormat.c"
#endif /* EXAMPLE_FORMAT_HEADER_ONLY */