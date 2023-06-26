
from dataclasses import dataclass

## The three types of engine strings.
@dataclass
class Type:
    RES_CREDIT = 10
    RES_NAME = 20
    RES_ABOUT = 30

## A string that appears on the engine itself to provide
## information about the module. Usually the module does
## not use these internally.
class EngineString:
    def __init__(self, stream, resource_declaration, resource_library):
        # TODO: Handle other encodings.
        self.string = stream.read(resource_declaration.resource_length_in_bytes).rstrip(b'\x00').decode('latin-1')