import os


# byte readers:
def main():
    path = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"
    f = open(path, "rb")  # noqa: SIM115

    jump_to(f, 3)


def skip_bytes(data, bytes_to_skip):
    data.seek(bytes_to_skip, os.SEEK_CUR)


def jump_to(data, byte_offset):
    data.seek(byte_offset, os.SEEK_SET)


class FontParser:
    def __init__(self, file):
        self.file = file

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
