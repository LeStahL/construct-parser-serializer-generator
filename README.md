# construct-c
Generate parser and serializer code in C from constructs (https://github.com/construct/construct).

# Instructions
Write a construct (documentation: https://construct.readthedocs.io/en/latest/index.html) and save it as Python module. For example
```
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
```

Run the command line tool:
```
python -m tool -v -o output -n ExampleFormat -i exampleStructInstance -m SimpleConstruct -f tests\SimpleConstruct.py
```

A header and source file with the parser and serializer will be generated.


See also the command line argument reference by running the command
```
python -m tool -h
```

# License
The code is GPLv3 and (c) 2023 Alexander Kraus <nr4@z10.info>; see LICENSE for details.
