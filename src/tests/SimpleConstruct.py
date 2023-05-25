from construct import Struct, Int8un, Int32un, Int32sn, CString

exampleStructInstance = "format" / Struct(
    "data" / Int8un,
    "subStruct" / Struct(
        "otherData" / Int32un,
        "moreData" / Int32sn,
    ),
    "aString" / CString('ascii'),
)
