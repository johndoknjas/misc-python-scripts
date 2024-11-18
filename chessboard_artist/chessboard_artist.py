from PIL import Image, ImageDraw
import time
import sys

def make_board_png(board_size: int, light_square: str, dark_square: str) -> Image:
    square_size = board_size // 8
    image = Image.new('RGB', (board_size, board_size), light_square)
    draw = ImageDraw.Draw(image)
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 != 0:
                x0, y0 = col * square_size, row * square_size
                x1, y1 = x0 + square_size - 1, y0 + square_size - 1
                draw.rectangle([x0, y0, x1, y1], fill=dark_square)
    return image

print(sys.argv)
light, dark = sys.argv[1:]
board_image = make_board_png(2048, light, dark) # for a 2048x2048 pixel board
board_image.save(f"{time.time()}.png")