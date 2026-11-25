import ctypes
import os


def main():
    path = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"
    f = open(path, "rb")  # noqa: SIM115
    parser = FontParser(f)
    # read header and skip scaler type (4)
    parser.skip_bytes(ctypes.sizeof(ctypes.c_uint32))
    num_tables = parser.read_uint16()  # uint16_t

    # skip searchRange, entrySelector, rangeShift
    parser.skip_bytes(ctypes.sizeof(ctypes.c_uint16) * 3)

    # read table directory:
    directory = {}
    for _ in range(num_tables):
        bytes_len = 4
        tag = parser.file.read(bytes_len)
        if len(tag) != bytes_len:
            raise EOFError("unexpected EOF while reading table tag")
        checkSum, offset, length = (
            parser.read_uint32(),
            parser.read_uint32(),
            parser.read_uint32(),
        )

        directory[tag] = (checkSum, offset, length)


class FontParser:
    def __init__(self, file):
        self.file = file

    def skip_bytes(self, bytes_to_skip):
        self.file.seek(bytes_to_skip, os.SEEK_CUR)

    def jump_to(self, byte_offset):
        self.file.seek(byte_offset, os.SEEK_SET)

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
