from parse_table import parse_table
from renderer import RGB, FrameBufferCanvas


def main():
    path = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"
    parse_table(path)
    canvas = FrameBufferCanvas(500, 500)
    canvas.draw_line(100, 100, 300, 400, 5, RGB(255, 255, 255))
    canvas.draw_line(400, 200, 50, 300, 2, RGB(200, 0, 0))
    canvas.draw_rect(200, 400, 50, 50, RGB(0, 200, 0))
    canvas.write_png_file("out.png")


if __name__ == "__main__":
    main()
