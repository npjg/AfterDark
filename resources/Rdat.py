
import self_documenting_struct as struct

class Rdat:
    def __init__(self, stream, resource_declaration, resource_library):
        self.unk1 = struct.unpack.uint16_le(stream)
        last = struct.unpack.uint16_le(stream)
        self.chunks = []
        chunk = RDatChunk(stream)
        while chunk.id != last:
            self.chunks.append(chunk)
            chunk = RDatChunk(stream)
        self.chunks.append(chunk)

class RDatChunk:
    def __init__(self, stream):
        self.id = struct.unpack.uint16_le(stream)
        self.unk1 = struct.unpack.uint16_le(stream)
        self.unk2 = struct.unpack.uint16_le(stream)
        self.unk3 = struct.unpack.uint16_le(stream)
        self.unk4 = struct.unpack.uint16_le(stream)