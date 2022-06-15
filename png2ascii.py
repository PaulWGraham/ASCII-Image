# Copyright 2022 Paul W. Graham

import PIL.Image

import argparse
import json
import os.path
import sys
import zipfile

ASCII_CHARS = ' .:;rsA23hHG#9&@'
OUTPUT_FILENAME_FORMAT  = "{}.txt"
MANIFEST_NAME = "manifest.json"
BUNDLE_VERSION = "0.1"
BUNDLE_VERSION_KEY = "version"
BUNDLE_FRAMES_KEY = "frames"

def asciify(input_filename, target_width, target_height, ascii_chars):
    raw_image = PIL.Image.open(input_filename)
    raw_image_width, raw_image_height = raw_image.size

    # Stretching the image is not supported.
    if target_width > raw_image_width or target_height > raw_image_height:
        raise NotImplementedError()

    target_aspect_ratio = target_width / target_height
    current_aspect_ratio = raw_image_width / raw_image_height

    # Set aspect ratio
    cropped_image = raw_image
    if current_aspect_ratio != target_aspect_ratio:
        if current_aspect_ratio > target_aspect_ratio:
            new_width = raw_image_height * target_aspect_ratio
            new_height = raw_image_height
            left = (raw_image_width - new_width) / 2
            upper = 0
            right = left + new_width
            lower = raw_image_height
        else:
            new_height = raw_image_width / target_aspect_ratio
            left = 0
            upper = (raw_image_height - new_height) / 2
            right = raw_image_width
            lower = upper + new_height

        cropped_image = raw_image.crop((left, upper, right, lower))

    # Set resolution
    resized_image = cropped_image.resize((target_width, target_height), resample = PIL.Image.Resampling.LANCZOS)
    greyscale_image = resized_image.convert("L")
    greyscale_image_width, greyscale_image_height = greyscale_image.size

    # Map pixels to ASCII characters. Pixels are binned to closest charater.
    value_range = 255 // (len(ascii_chars) - 1)
    output = []
    for y in range(greyscale_image_height):
        for x in range(greyscale_image_width):
            output.append(ascii_chars[greyscale_image.getpixel((x,y)) // value_range])
        output.append("\n")

    ascii_image = "".join(output)

    return ascii_image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Create an ascii image bundle from an image or directory of images')
    parser.add_argument('input_filename', type = str, help = 'Image or directory of images.')
    parser.add_argument('output_bundle_filename', type = str, help = 'Filename Of The Output Bundle.')
    parser.add_argument('target_width', type = int, help = 'Target width of the ascii image(s).')
    parser.add_argument('target_height', type = int, help = 'Target height of the ascii image(s).')
    args = parser.parse_args()

    input_filename = args.input_filename
    target_width = args.target_width
    target_height = args.target_height
    bundle_name = args.output_bundle_filename

    if os.path.exists(bundle_name) and not zipfile.is_zipfile(bundle_name):
        raise InputError()

    manifest = {}
    manifest[BUNDLE_VERSION_KEY] = BUNDLE_VERSION
    manifest[BUNDLE_FRAMES_KEY] = []
    with zipfile.ZipFile(bundle_name, "w") as bundle:
        if os.path.isdir(input_filename):
            for image_name in os.listdir(input_filename):
                ascii_image = asciify(os.path.join(input_filename, image_name), target_width, target_height, ASCII_CHARS)
                output_name = OUTPUT_FILENAME_FORMAT.format(image_name)
                manifest[BUNDLE_FRAMES_KEY].append(output_name)
                bundle.writestr(output_name, ascii_image)
        else:
            ascii_image = asciify(input_filename, target_width, target_height, ASCII_CHARS)
            output_name = OUTPUT_FILENAME_FORMAT.format(input_filename)
            manifest[BUNDLE_FRAMES_KEY].append(output_name)
            bundle.writestr(output_name, ascii_image)

        bundle.writestr(MANIFEST_NAME, json.dumps(manifest))
