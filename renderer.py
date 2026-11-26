from dataclasses import dataclass

from PIL import Image


def render():
    FrameBufferCanvas(60, 60)


@dataclass
class RGB:
    r: int
    g: int
    b: int

    def __init__(self, *values: int):
        if len(values) == 1:
            self.r = self.g = self.b = values[0]
        elif len(values) == 3:
            self.r, self.g, self.b = values
        else:
            raise TypeError("RGB expects one grayscale value or three color values")


class FrameBufferCanvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.framebuffer = [RGB(0, 0, 0) for _ in range(width * height)]

    def set(self, x: int, y: int, color: RGB):
        if x < 0 or y < 0:
            return
        if x >= self.width or y >= self.height:
            return
        i = (y * self.width) + x
        self.framebuffer[i] = color

    def draw_line(self, ax: int, ay: int, bx: int, by: int, thickness: int, color: RGB):
        w = abs(ax - bx)
        h = abs(ay - by)
        is_steep = w < h
        if is_steep:
            ax, ay = ay, ax
            bx, by = by, bx
        if ax > bx:
            ax, bx = bx, ax
            ay, by = by, ay
        y = float(ay)
        for x in range(ax, bx + 1):
            if is_steep:
                self.draw_rect(int(y), x, thickness, thickness, color)
            else:
                self.draw_rect(x, int(y), thickness, thickness, color)
            y += float(by - ay) / float(bx - ax)

    def draw_rect(
        self,
        center_x: int,
        center_y: int,
        rect_width: int,
        rect_height: int,
        color: RGB,
    ):
        half_w = rect_width // 2
        half_h = rect_height // 2
        left = center_x - half_w
        top = center_y - half_h
        right = left + rect_width
        bottom = top + rect_height

        # clip to framebuffer
        if right <= 0 or bottom <= 0:
            return
        if left >= self.width or top >= self.height:
            return

        left = max(left, 0)
        top = max(top, 0)
        right = min(right, self.width)
        bottom = min(bottom, self.height)

        for y in range(top, bottom):  # top left corner is 0,0
            for x in range(left, right):
                self.set(x, y, color)

    def write_png_file(self, file_name):
        pixels = bytearray()

        for color in self.framebuffer:
            pixels.extend((color.r, color.g, color.b))

        image = Image.frombytes("RGB", (self.width, self.height), bytes(pixels))
        image.save(file_name, format="PNG")
