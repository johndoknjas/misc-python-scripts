for img in *.jpg; do magick "$img" -crop 120x120+4+4 +repage -resize 128x128 "cropped_$img"; done
# Note: replace numbers with desired pixel dimensions