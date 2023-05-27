from construct import Struct, Int8un, Int32un, Int32sn, this, StringEncoded, Bytes, Array

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
            )
        ),
    ),
)
