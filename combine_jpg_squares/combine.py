from PIL import Image

chessboard = Image.new('RGB', (1024, 1024))
images = [Image.open(f'cropped_block_{i}.jpg') for i in range(0, 64)]
for row in range(8):
    for col in range(8):
        img = images[row * 8 + col]
        chessboard.paste(img, (col * 128, row * 128))
chessboard.save('chessboard_output.jpg')