
import self_documenting_struct as struct

## An array of C strings.
## The name for this class comes from the STRINGLIST
## resource type name observed in some modules.
class StringList:
    def __init__(self, stream, resource_declaration, resource_library):
        # READ THE STRINGS.
        self.strings = []
        string_count = struct.unpack.uint16_le(stream)
        for index in range(string_count):
            string = self._read_null_terminated_ascii_string(stream)
            self.strings.append(string)

    @classmethod
    def _read_null_terminated_ascii_string(cls, stream):
        string = b''
        byte = stream.read(1)
        while byte != b'\x00':
            string += byte
            byte = stream.read(1)
        
        return string.decode('latin-1')