#!/usr/bin/env python3
"""
Script:	progress_bar1.py
Date:	2020-01-19

Platform: macOS

Description:
Converts an image to icns file.  Replaces the xcode icon composer and simplifies the iconutil command

"""
__author__ = "thedzy"
__copyright__ = "Copyright 2020, thedzy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Developer"

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


def main() -> int:
    """
    Convert image to icns file
    :return: return code
    """

    if options.outfile is None:
        input_file_parent: Path = Path(options.infile).parent
        input_file_name: str = Path(options.infile).stem
        options.outfile = input_file_parent / f'{input_file_name}.icns'

    temp_dir: Path = Path(tempfile.TemporaryDirectory().name)
    temp_path: Path = temp_dir / f'{Path(options.infile).stem}.iconset'
    temp_file: Path = temp_dir / f'{Path(options.infile).stem}.icns'
    temp_path.mkdir(parents=True, exist_ok=True)

    # Files that need to be created
    # (name, size and scale)
    icon_files: list[tuple[str, int, int]] = [
        ('icon_16x16.png', 16, 1),
        ('icon_16x16@2x.png', 16, 2),
        ('icon_32x32.png', 32, 1),
        ('icon_32x32@2x.png', 32, 2),
        ('icon_128x128.png', 128, 1),
        ('icon_128x128@2x.png', 128, 2),
        ('icon_256x256.png', 256, 1),
        ('icon_256x256@2x.png', 256, 2),
        ('icon_512x512.png', 512, 1),
        ('icon_512x512@2x.png', 512, 2),
        ('icon_1024x1024.png', 1024, 1),
    ]

    resize_methods = {
        'NEAREST': 0,
        'ANTIALIAS': 1,
        'LANCZOS': 1,
        'BILINEAR': 2,
        'BICUBIC': 3,
    }

    # Create all the resized images
    with Image.open(options.infile) as image:
        # Convert to image with Alpha
        image: Image.Image = image.convert('RGBA')

        # Pad image to prevent needing to crop or stretch
        image_width, image_height = image.size
        if image_width != image_height and options.keep_aspect:
            print('Padding image')
            max_size: int = max(image_width, image_height)
            blank_image = Image.new('RGBA', (max_size, max_size), 0)
            if image_width > image_height:
                image_size_difference: int = int(
                    (image_width - image_height) / 2)
                blank_image.paste(image, (0, image_size_difference))
            else:
                image_size_difference: int = int(
                    (image_height - image_width) / 2)
                blank_image.paste(image, (image_size_difference, 0))
            image: Image.Image = blank_image

        # Crop image image
        image_width, image_height = image.size
        if image_width != image_height and options.crop:
            print('Cropping image')
            min_size: int = min(image_width, image_height)
            if image_width == min_size:
                resized_image = image.crop((
                    0,
                    (image_height - image_width) / 2,
                    min_size,
                    ((image_height - image_width) / 2) + min_size
                ))
            else:
                print((image_width - image_height) / 2)
                print(image_width, image_height)
                resized_image: Image.Image = image.crop((
                    (image_width - image_height) / 2, 0,
                    ((image_width - image_height) / 2) + min_size, min_size
                ))
            image: Image.Image = resized_image

        image_width, _ = image.size

        last_size: int = 0
        for icon_file in icon_files:
            name: str = icon_file[0]
            size: int = icon_file[1]
            multiplier: int = icon_file[2]

            # Scale for retina
            adjusted_size: int = size * multiplier

            if image_width > last_size or options.all_sizes:
                last_size: int = size

                print(f'Processed: {name}')
                new_image: Image.Image = image.copy()
                new_image: Image.Image = new_image.resize(
                    (adjusted_size, adjusted_size), resize_methods.get(options.method, 0))
                new_image.save(temp_path / name, "PNG")

    # Convert using iconutil
    if options.binary.is_file():
        options.outfile.unlink(missing_ok=True)  # Remove old file if it exists
        command: list[str] = [
            options.binary.as_posix(), '-c', 'icns', temp_path.as_posix()
        ]

        # Run the command and return results
        try:
            process_info: subprocess.CompletedProcess = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except ValueError as err:
            print(err)
            return 2

        if process_info.returncode == 0:
            print(f'Creating file: {options.outfile.absolute()}')
            temp_file.rename(options.outfile)
        else:
            print(f'Error creating file, error {process_info.returncode} with {options.binary}')
            return process_info.returncode
    else:
        print(f'Please install {options.binary.stem}')

    print('Done')
    return 0


if __name__ == '__main__':
    def valid_path(path):
        parent: Path = Path(path).parent
        if not parent.is_dir():
            print(f'{parent} is not a directory, make it?', end=' ')
            if input('y/n: ').lower()[0] == 'y':
                parent.mkdir(parents=True, exist_ok=True)
                return Path(path)
            raise argparse.ArgumentTypeError(f'{path} is an invalid path')
        return Path(path)


    # Create argument parser
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='%prog [options]\n %prog will take an image and save it to Apple icns file.')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)

    # Input file, required
    parser.add_argument('-i', '--infile', type=valid_path,
                        action='store', dest='infile',
                        required=True,
                        help='image file, required')

    # output file, assumed if missing
    parser.add_argument('-o', '--outfile', type=valid_path, default=None,
                        action='store', dest='outfile',
                        help='icns file, optional. Default: Same as infile and icns extension')

    # binary path of iconutil
    parser.add_argument('-b', '--binaary', type=valid_path, default=Path('/usr/bin/iconutil'),
                        action='store', dest='binary',
                        help='path of iconutil')

    # crop image?
    parser.add_argument('-c', '--crop', default=False,
                        action='store_true', dest='crop',
                        help='crop image when resizing')

    # Maintain aspect ratio?
    parser.add_argument('-k', '--keep_aspect', default=False,
                        action='store_true', dest='keep_aspect',
                        help='when resizing keep aspect ratio')

    # Scaling mathod
    parser.add_argument('-m', '--method', default='ANTIALIAS',
                        action='store', dest='method',
                        choices=('NEAREST', 'BILINEAR', 'BICUBIC',
                                 'LANCZOS', 'ANTIALIAS'),
                        help='method to use. Valid choices are {}. Default: {}'.format(('NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS', 'ANTIALIAS'), 'ANTIALIAS'))

    # Maintain aspect ratio?
    parser.add_argument('-a', '--allsizes', default=False,
                        action='store_true', dest='all_sizes',
                        help='when scaling, scale up to all sizes.  Not recommended')

    options: argparse.Namespace = parser.parse_args()

    exit(main())
