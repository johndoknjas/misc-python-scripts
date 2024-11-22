import os
import sys
import time

import cv2

def split_into_blocks(image_path, block_size=128):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    output_dir = f"output_blocks_{time.time_ns()}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    block_counter = 0
    # Loop over the image and extract 128x128 blocks:
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            # Extract the block:
            block = image[y:y+block_size, x:x+block_size]
            # Ensure we don't go beyond the image dimensions:
            assert block.shape[0] == block_size and block.shape[1] == block_size
            block_filename = os.path.join(output_dir, f"block_{block_counter}.jpg")
            cv2.imwrite(block_filename, block)
            block_counter += 1
    print(f"Finished splitting the image into {block_counter} blocks.")

split_into_blocks(sys.argv[1])
