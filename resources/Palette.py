
from PIL import Image
import self_documenting_struct as struct
import os

## Models an After Dark palette. 
class Palette:
    def __init__(self, stream, resource_declaration, resource_library):
        # READ THE METADATA.
        self.unk1 = struct.unpack.uint16_le(stream)
        # TODO: This is often less than the actual number of 
        # 4-tuples in the file.
        self.color_count = struct.unpack.uint16_le(stream)

        # READ THE COLOR DEFINITIONS.
        self.data = bytearray()
        for color_index in range(self.color_count):
            # The color triple is in red/green/blue color order.
            color_triple = stream.read(3)                   
            self.data += color_triple
            # TODO: Is this just padding?
            stream.read(1)

    @classmethod
    def valid_signature(self, stream):
        SIGNATURE = b'\x00\x03'

    ## Builds an image that shows each color in a palette.
    ## TODO: Also numbers each image strip 
    def export(self, filepath):
        # VALIDATE THAT THE PALETTE CAN BE EXPORTED.
        # Due to the limitations of PIL's paletted image type, there can be 
        # up to 256 colors shown in a single palette.
        MAX_PALETTE_ENTRIES = 0x100

        # CALCULATE THE DIMENSIONS.
        # The dimensions of the block for each color.
        BLOCK_WIDTH = 32
        BLOCK_HEIGHT = 4
        color_strip_size_in_bytes = (BLOCK_WIDTH * BLOCK_HEIGHT)
        total_image_size = (BLOCK_WIDTH, BLOCK_HEIGHT * self.color_count)

        # GENERATE THE IMAGE.
        image_bytes = bytearray()
        for color_index in range(self.color_count):
            color_index_byte = struct.pack.uint8(color_index) # int.to_bytes(color_index, length = 1, byteorder='little')
            # Create a solid rectangle with the current color index at the 
            # given size.
            image_bytes += color_index_byte * color_strip_size_in_bytes
        image = Image.frombytes('P', size = total_image_size, data = bytes(image_bytes))
        image.putpalette(self.data)

        image_filepath = os.path.join()
        image.save('palette.bmp')