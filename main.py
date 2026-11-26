import ctypes
import os
from dataclasses import dataclass


def main():
    path = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"
    f = open(path, "rb")  # noqa: SIM115
    parser = FontParser(f)
    # read header and skip scaler type (4)
    parser.skip_bytes(ctypes.sizeof(ctypes.c_uint32))
    num_tables = parser.read_uint16()  # uint16_t

    # skip searchRange, entrySelector, rangeShift
    parser.skip_bytes(ctypes.sizeof(ctypes.c_uint16) * 3)

    # process directories:
    directory = parser.get_table_directory(num_tables)

    # read cmap directory:
    cmap_offset = directory[b"cmap"].offset
    parser.load_unicode_to_glyph_code_map(cmap_offset)

    # glyphcode -> glyphoffset (loca table)
    parser.jump_to(directory[b"maxp"].offset + 4)
    num_glyphs = parser.read_uint16()
    parser.jump_to(directory[b"head"].offset)
    parser.skip_bytes(50)  # skip to indexToLocFormat
    is_two_byte = parser.read_int16() == 0
    glyph_table_offset = directory[b"glyf"].offset
    location_table_offset = directory[b"loca"].offset

    parser.jump_to(location_table_offset)

    glyph_code_to_offset = [0] * (num_glyphs + 1)  # pre-allocate array
    for i in range(num_glyphs + 1):
        glyph_offset = parser.read_uint16() * 2 if is_two_byte else parser.read_uint32()
        glyph_code_to_offset[i] = glyph_table_offset + glyph_offset

    for i in range(num_glyphs):
        if glyph_code_to_offset[i] == glyph_code_to_offset[i + 1]:
            glyph_code_to_offset[i] = 0

    print(glyph_code_to_offset)


@dataclass
class TableEntry:
    checkSum: int
    offset: int
    length: int


class FontParser:
    def __init__(self, file):
        self.file = file

    def skip_bytes(self, bytes_to_skip):
        self.file.seek(bytes_to_skip, os.SEEK_CUR)

    def jump_to(self, byte_offset):
        self.file.seek(byte_offset, os.SEEK_SET)

    def load_unicode_to_glyph_code_map(self, cmap_offset):
        self.jump_to(cmap_offset)

        self.skip_bytes(2)  # skip version
        num_sub_tables = self.read_uint16()

        subtable_offset = -1
        for _ in range(num_sub_tables):
            platform, encoding, offset = (
                self.read_uint16(),
                self.read_uint16(),
                self.read_uint32(),
            )
            if platform == 0 and encoding == 4:  # we only support format12
                subtable_offset = offset
                break

        if subtable_offset == -1:
            raise RuntimeError("Not supported format. We only support format12")

        # read subtable header to detect format
        self.jump_to(cmap_offset + subtable_offset)
        format = self.read_uint16()
        unicode_to_glyph_code = {}

        if format == 12:
            self.skip_bytes(10)
            n_groups = self.read_uint32()
            for _ in range(n_groups):
                start_char_code, end_char_code, start_glyph_code = (
                    self.read_uint32(),
                    self.read_uint32(),
                    self.read_uint32(),
                )
                unicode_to_glyph_code[start_char_code] = start_glyph_code
                diff = end_char_code - start_char_code
                for j in range(1, diff + 1):
                    unicode_to_glyph_code[start_char_code + j] = start_glyph_code + j
        else:
            raise RuntimeError("Not supported format. We support format12")

        return unicode_to_glyph_code

    def get_table_directory(self, num_tables):
        directory: dict[bytes, TableEntry] = {}
        for _ in range(num_tables):
            bytes_len = 4
            tag = self.file.read(bytes_len)
            if len(tag) != bytes_len:
                raise EOFError("unexpected EOF while reading table tag")
            checkSum, offset, length = (
                self.read_uint32(),
                self.read_uint32(),
                self.read_uint32(),
            )
            directory[tag] = TableEntry(checkSum, offset, length)
        return directory

    # byte readers:
    def read_be(self, num_bytes, *, signed=False):
        data = self.file.read(num_bytes)
        if len(data) != num_bytes:
            raise EOFError("unexpected EOF")
        return int.from_bytes(data, byteorder="big", signed=signed)

    def read_uint8(self):
        return self.read_be(1)

    def read_uint16(self):
        return self.read_be(2)

    def read_uint32(self):
        return self.read_be(4)

    def read_int8(self):
        return self.read_be(1, signed=True)

    def read_int16(self):
        return self.read_be(2, signed=True)

    def read_int32(self):
        return self.read_be(4, signed=True)

    def readf2dot14(self):
        raw = self.read_int16()
        return raw / (1 << 14)


if __name__ == "__main__":
    main()
