

import resource
import self_documenting_struct as struct
import logging

## A collection of bitmaps displayed in the screensaver.
class Rlep:
    def __init__(self, stream, resource_declaration, resource_library):
        self.frames = []
        chunk_start_pointer = stream.tell()
        chunk_type = stream.read(4)
        # There seems to be 0x10 bytes of zeroes at the end of the 
        # file. This makes sense, as the chunk header (including type)
        # takes exactly 0x10 bytes. We will just watch for the 
        # type being all zeroes.
        while chunk_type != b'\x00\x00\x00\x00' and stream.tell() < resource_declaration.data_end_offset:
            logging.warning(f'Reading chunk: {chunk_type}...')
            if chunk_type == b'RLID':
                chunk = RLID(stream, chunk_start_pointer)
                self.rlid = chunk
            elif chunk_type == b'CSTM':
                chunk = CSTM(stream, chunk_start_pointer)
                self.frames.append({'stream': chunk})
            elif chunk_type == b'CTAB':
                chunk = CTAB(stream, chunk_start_pointer)
                self.ctab = chunk
            elif chunk_type == b'IHDR':
                chunk = IHDR(stream, chunk_start_pointer)
                self.frames[chunk.id].update({'header': chunk})
            else:
                raise ValueError(f'Unknown chunk type read: {chunk_type}')
            logging.warning(f' > Success: {chunk.chunk_length} bytes read')

            chunk_start_pointer = stream.tell()
            chunk_type = stream.read(4) 

# Each of the three possible chunk types uses a common header format,
# which we specify in a base-class object for all chunks.
class Chunk:
    def __init__(self, stream, start_pointer):
        # The first field is a numeric ID that differentiates chunks
        # of the same type in this file. The ID is unique to chunks
        # of the same type.
        self.id = struct.unpack.uint32_be(stream)
        self.last_chunk = struct.unpack.uint32_be(stream)

        # The second field specifies the length of the entire chunk.
        # This is a bit irritating, as we have to subtract out the 
        # bytes already read to calculate the true payload size.
        self.chunk_length = struct.unpack.uint32_be(stream)
        chunk_bytes_read = stream.tell() - start_pointer
        # The payload size is the true size of the 
        # application data remaining in the chunk (payload).
        self.payload_size = self.chunk_length - chunk_bytes_read

class RLID(Chunk):
    def __init__(self, stream, start_pointer):
        super().__init__(stream, start_pointer)
        self.data = stream.read(self.payload_size)

# CSTM: Compressed stream
class CSTM(Chunk):
    def __init__(self, stream,  start_pointer):
        super().__init__(stream, start_pointer)
        # All of these stream IDs seem to be prefixed with 0x5f01 << 0x02, such that
        # the ID for the second CSTM chunk (chunk 1) is given as 0x5f010001.
        self.id -= 0x5f010000
        self.data = stream.read(self.payload_size)

# CTAB: Color table
class CTAB(Chunk):
    def __init__(self, stream, start_pointer):
        super().__init__(stream, start_pointer)
        # The ID for the palette seems to always be 0xf01 (3841).
        # Not sure why.
        #
        # Also, the data seem to be 0x38 bytes long, which is unusual for a 16-color palette.
        # (We would expect 0x30 or 0x40 bytes for the palette, depending on whether padding is used.)
        self.data = stream.read(self.payload_size)

# IHDR: Image header (but not PNG)
class IHDR(Chunk):
    def __init__(self, stream, start_pointer):
        super().__init__(stream, start_pointer)
        self.unk1 = struct.unpack.uint32_be(stream)
        self.unk2 = struct.unpack.uint32_be(stream)
        self.width = struct.unpack.uint16_be(stream)
        self.height = struct.unpack.uint16_be(stream)
        self.data = b''
