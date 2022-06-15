# Copyright 2022 Paul W. Graham

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

import argparse
import json
import os.path
import sys
import zipfile

OUTPUT_FILENAME_FORMAT  = "{}.png"
MANIFEST_NAME = "manifest.json"
BUNDLE_VERSION = "0.1"
BUNDLE_VERSION_KEY = "version"
BUNDLE_FRAMES_KEY = "frames"
FONT_SIZE = 20

def pngify(ascii_image, font):
    i = PIL.Image.new("1", (100,100))
    d = PIL.ImageDraw.Draw(i)

    ascii_image_lines = ascii_image.splitlines()
    image_width, image_height = d.textsize(ascii_image_lines[0], font)
    image_height *= len(ascii_image_lines)
    image = PIL.Image.new("1", (image_width, image_height))
    draw = PIL.ImageDraw.Draw(image)
    draw.multiline_text((0, 0), ascii_image, font = font, fill = 255)
    return image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Create an ascii image bundle from an image or directory of images')
    parser.add_argument('input_filename', type = str, help = 'Textfile or bundle.')
    parser.add_argument('output_directory', type = str, help = 'Directory to save output to')
    parser.add_argument('font_filename', type = str, help = 'TTF font to use')
    args = parser.parse_args()

    input_filename = args.input_filename
    output_directory = args.output_directory
    font_filename = args.font_filename

    font = PIL.ImageFont.truetype(font_filename, FONT_SIZE)
    if not os.path.exists(output_directory):
        raise InputError()

    if zipfile.is_zipfile(input_filename):
        with zipfile.ZipFile(input_filename, mode = "r") as bundle:
            manifest = json.loads(bundle.read(MANIFEST_NAME))
            frame_count = 0
            for ascii_frame in manifest['frames']:
                frame_path = os.path.join(output_directory, OUTPUT_FILENAME_FORMAT.format(frame_count))
                frame = pngify(str(bundle.read(ascii_frame), encoding = 'ascii'), font)
                frame.save(frame_path)
                frame_count += 1
    else:
        frame_path = os.path.join(output_directory, OUTPUT_FILENAME_FORMAT.format(0))
        frame = pngify(str(bundle.read(ascii_frame), encoding = 'ascii'), font)
        frame.save(frame_path)
