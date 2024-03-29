from os.path import join, abspath, dirname
from argparse import ArgumentParser

class CommandLineService:
    def __init__(self) -> None:
        self.argumentParser = ArgumentParser('construct-c', description='Tool for generating parser and serializer code in C from Python constructs.')
        self.argumentParser.add_argument('-o,--output', dest='output', help='Output folder for saving the generated files to.', default='.')
        self.argumentParser.add_argument('-n,--name', dest='name', help='Basename for generated files.', default='construct')
        self.argumentParser.add_argument('-i,--id', dest='id', help='Identifier of construct to generate from.', default='binaryFormat')
        self.argumentParser.add_argument('-m,--module', dest='module', help='Module to load construct for generation from.', default='BinaryFormat')
        self.argumentParser.add_argument('-f,--file', dest='file', help='Python file with module to load construct from.', default='BinaryFormat.py')
        self.argumentParser.add_argument('-v,--verbose', dest='verbose', action='store_true', help='Enable verbose output.', default=False)
        self.argumentParser.add_argument('-p,--python-data-binding', dest='python', action='store_true', help='Export a Python module with data binding instead of the C parser.', default=False)
        self.argumentParser.add_argument('-s,--shader', dest='shader', action='store_true', help='Export a fragment shader parser and serializer implementation.')

    def parse(self, argv=None):
        self.args = self.argumentParser.parse_args() if argv is None else self.argumentParser.parse_args(argv)
