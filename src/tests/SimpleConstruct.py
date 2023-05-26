from construct import Struct, Int8un, Int32un, Int32sn, this, StringEncoded, Bytes

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
)
