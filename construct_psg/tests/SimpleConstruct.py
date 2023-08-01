from construct import Struct, Int8un, Int32un, Int32sn, this, StringEncoded, Bytes, Array, Enum
from enum import IntEnum

class InternalFormat(IntEnum):
    Screen = 0x0
    Rgba32f = 0x1
    Rg32f = 0x2
    Rgba = 0x3
    Rgba8 = 0x4
    R32f = 0x5
    Rgb8 = 0x6

exampleStructInstance = "exampleFormat" / Struct(
    "data" / Int8un,
    "subStruct" / Struct(
        "otherData" / Int32un,
        "moreData" / Int32sn,
    ),
    "size" / Int32un,
    "string" / StringEncoded(
        Bytes(this.size),
        'ascii',
    ),
    "arraySize" / Int32un,
    "weNeedArraySupport" / Array(
        this.arraySize,
        "ArrayContent" / Struct(
            "structEntry" / Int8un,
            "thisAString" / StringEncoded(
                Bytes(this.structEntry),
                'ascii',
            ),
            "nestedArraySize" / Int8un,
            "nestedArray" / Array(
                this.nestedArraySize,
                "nestedArrayFields" / Int8un,
            ),
            'TextureInternalFormat' / Enum(
                'InternalFormat' / Int8un,
                InternalFormat,
            ),
        ),
    ),
)
