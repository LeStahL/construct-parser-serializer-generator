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

exampleStructInstance = "ExampleFormat" / Struct(
    "Data" / Int8un,
    "SubStruct" / Struct(
        "OtherData" / Int32un,
        "MoreData" / Int32sn,
    ),
    "Size" / Int32un,
    "String" / StringEncoded(
        Bytes(this.Size),
        'ascii',
    ),
    "ArraySize" / Int32un,
    "WeNeedArraySupport" / Array(
        this.ArraySize,
        "ArrayContent" / Struct(
            "StructEntry" / Int8un,
            "ThisAString" / StringEncoded(
                Bytes(this.StructEntry),
                'ascii',
            ),
            "NestedArraySize" / Int8un,
            "NestedArray" / Array(
                this.NestedArraySize,
                "NestedArray" / Int8un,
            ),
            'TextureInternalFormat' / Enum(
                'InternalFormat' / Int8un,
                InternalFormat,
            ),
        ),
    ),
)

exampleConstructDict = {
    "Data": 3,
    "SubStruct": {
        "OtherData": 12349,
        "MoreData": -23,
    },
    "Size": 2,
    "String": "hi",
    "ArraySize": 1,
    "WeNeedArraySupport": [
        {
            "StructEntry": 5,
            "ThisAString": "test1",
            "NestedArraySize": 2,
            "NestedArray": [
                1,
                2,
            ],
            "TextureInternalFormat": InternalFormat.Rg32f,
        },
    ],
}

exampleJSONDict = {
    "Data": 3,
    "SubStruct": {
        "OtherData": 12349,
        "MoreData": -23,
    },
    "Size": 2,
    "String": "hi",
    "ArraySize": 1,
    "WeNeedArraySupport": [
        {
            "StructEntry": 5,
            "ThisAString": "test1",
            "NestedArraySize": 2,
            "NestedArray": [
                1,
                2,
            ],
            "TextureInternalFormat": 0x2,
        },
    ],
}

exampleConstructBinary = b'\x03=0\x00\x00\xe9\xff\xff\xff\x02\x00\x00\x00hi\x01\x00\x00\x00\x05test1\x02\x01\x02\x02'
