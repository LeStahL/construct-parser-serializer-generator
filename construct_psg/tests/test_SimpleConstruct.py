from construct_psg.__main__ import generate
from os.path import (
    dirname,
    join,
)

generate([
    "-v",
    "-o", dirname(__file__),
    "-n", "exampleFormat",
    "-i", "exampleStructInstance",
    "-m", "SimpleConstruct",
    "-f", join(dirname(__file__), "SimpleConstruct.py"),
    "-p",
])

from unittest import TestCase, main
from .SimpleConstruct import *
from .exampleFormat import *

class TestSimpleConstruct(TestCase):
    def _assertInstanceCorrectness(self, instance, other):
        self.assertEqual(instance.data, other["Data"])
        self.assertEqual(instance.subStruct.otherData, other["SubStruct"]["OtherData"])        
        self.assertEqual(instance.subStruct.moreData, other["SubStruct"]["MoreData"])
        self.assertEqual(instance.size, other["Size"])
        self.assertEqual(instance.string, other["String"])
        self.assertEqual(instance.arraySize, other["ArraySize"])
        self.assertEqual(instance.weNeedArraySupport[0].structEntry, other["WeNeedArraySupport"][0]["StructEntry"])
        self.assertEqual(instance.weNeedArraySupport[0].thisAString, other["WeNeedArraySupport"][0]["ThisAString"])
        self.assertEqual(instance.weNeedArraySupport[0].nestedArraySize, other["WeNeedArraySupport"][0]["NestedArraySize"])
        self.assertListEqual(instance.weNeedArraySupport[0].nestedArray, other["WeNeedArraySupport"][0]["NestedArray"])
        self.assertIsInstance(instance.weNeedArraySupport[0].textureInternalFormat, InternalFormat)
        self.assertEqual(instance.weNeedArraySupport[0].textureInternalFormat, other["WeNeedArraySupport"][0]["TextureInternalFormat"])

    def _assertObjectCorrectness(self, _object, other, typed: bool):
        self.assertEqual(_object["Data"], exampleConstructDict["Data"])
        self.assertEqual(_object["SubStruct"]["OtherData"], exampleConstructDict["SubStruct"]["OtherData"])        
        self.assertEqual(_object["SubStruct"]["MoreData"], exampleConstructDict["SubStruct"]["MoreData"])
        self.assertEqual(_object["Size"], exampleConstructDict["Size"])
        self.assertEqual(_object["String"], exampleConstructDict["String"])
        self.assertEqual(_object["ArraySize"], exampleConstructDict["ArraySize"])
        self.assertEqual(_object["WeNeedArraySupport"][0]["StructEntry"], exampleConstructDict["WeNeedArraySupport"][0]["StructEntry"])
        self.assertEqual(_object["WeNeedArraySupport"][0]["ThisAString"], exampleConstructDict["WeNeedArraySupport"][0]["ThisAString"])
        self.assertEqual(_object["WeNeedArraySupport"][0]["NestedArraySize"], exampleConstructDict["WeNeedArraySupport"][0]["NestedArraySize"])
        self.assertListEqual(_object["WeNeedArraySupport"][0]["NestedArray"], exampleConstructDict["WeNeedArraySupport"][0]["NestedArray"])
        if typed:
            self.assertIsInstance(_object["WeNeedArraySupport"][0]["TextureInternalFormat"], InternalFormat)
        else:
            self.assertIsInstance(_object["WeNeedArraySupport"][0]["TextureInternalFormat"], int)
        self.assertEqual(_object["WeNeedArraySupport"][0]["TextureInternalFormat"], exampleConstructDict["WeNeedArraySupport"][0]["TextureInternalFormat"])

    def test_buildable_object_to_binary(self):
        self.assertEqual(exampleStructInstance.build(exampleConstructDict), exampleConstructBinary)
    
    def test_binary_to_Instance(self):
        instance: ExampleFormat = ExampleFormat.parseFromContainer(exampleStructInstance.parse(exampleConstructBinary))
        self._assertInstanceCorrectness(instance, exampleConstructDict)

    def test_instance_to_buildable_object(self):
        instance: ExampleFormat = ExampleFormat.parseFromContainer(exampleStructInstance.parse(exampleConstructBinary))
        _object = instance.serializeToDict()
        self._assertObjectCorrectness(_object, exampleConstructDict, True)
        
    def test_instance_to_json_serializable_object(self):
        instance: ExampleFormat = ExampleFormat.parseFromContainer(exampleStructInstance.parse(exampleConstructBinary))
        _object = instance.serializeToDict(convertEnumValues=True)
        self._assertObjectCorrectness(_object, exampleJSONDict, False)

    def test_json_serializable_object_to_instance(self):
        instance: ExampleFormat = ExampleFormat.parseFromContainer(exampleJSONDict)
        self._assertInstanceCorrectness(instance, exampleConstructDict)

    def test_deep_copy_instance(self):
        instance: ExampleFormat = ExampleFormat.parseFromContainer(exampleJSONDict)
        other = deepcopy(instance)

        other.data = 5
        other.subStruct.otherData = 0
        other.subStruct.moreData = 0
        other.size = 3
        other.string = "hi!"
        other.weNeedArraySupport[0].structEntry = 3
        other.weNeedArraySupport[0].thisAString = "tes"
        other.weNeedArraySupport[0].nestedArraySize = 3
        other.weNeedArraySupport[0].nestedArray += [5]
        other.weNeedArraySupport[0].textureInternalFormat = InternalFormat.Rgb8

        self._assertInstanceCorrectness(instance, exampleConstructDict)

if __name__ == '__main__':
    main()
