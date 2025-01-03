import base64
import sys
import time
import os
import glob

user_input = sys.argv[1] if len(sys.argv) > 1 else ''
if not user_input or '.' in user_input or '>' in user_input:
    # read svg, output bytes
    if not user_input:
        print('Encoding the most recent `.svg` file:\n')
        filename = max(glob.glob('*.svg'), key=os.path.getmtime)
    elif '>' in user_input:
        # svg string given directly
        print(base64.b64encode(str.encode(user_input)).decode("utf-8"))
        sys.exit(0)
    else:
        filename = user_input
    with open(filename, "rb") as svg_file:
        print(base64.b64encode(svg_file.read()).decode("utf-8"))
else:
    # read bytes, output svg
    with open(f"output-{time.time_ns()}.svg", "wb") as svg_file:
        output = base64.b64decode(user_input)
        svg_file.write(output)
        print()
        print(output)
        print('\noutput also written to an svg file')