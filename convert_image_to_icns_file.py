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
__version__ = "1.0"
__maintainer__ = "thedzy"
__email__ = "thedzy@hotmail.com"
__status__ = "Developer"

import optparse
import os
import subprocess

from PIL import Image


def main():
    """
    Convert image to icns file
    :return: (void)
    """

    # Check that the png exists
    if os.path.isfile(options.infile):
        image_name = os.path.basename(options.infile).split('.')[0]
    else:
        print('File {} does not exist, please check the path'.format(options.infile))
        return 1

    if options.outfile is None:
        options.outfile = os.path.join(os.path.dirname(options.infile), os.path.basename(options.infile).split('.')[0] + b'.icns')
    else:
        if not os.path.exists(os.path.dirname(options.outfile)):
            print('Check out file path')

    base_path = os.path.dirname(os.path.abspath(__file__))
    temp_path = '/tmp/{}.iconset'.format(image_name)
    temp_file = '/tmp/{}.icns'.format(image_name)
    os.makedirs(temp_path, exist_ok=True)
    os.chdir(base_path)

    # Files that need to be created
    # (name, size and scale)
    icon_files = [
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
        image = image.convert('RGBA')

        # Pad image to prevent needing to crop or stretch
        image_width, image_height = image.size
        if image_width != image_height and options.keep_aspect:
            print('Padding image')
            max_size = max(image_width, image_height)
            blank_image = Image.new('RGBA', (max_size, max_size), 0)
            if image_width > image_height:
                image_size_differnce = int((image_width - image_height) / 2)
                blank_image.paste(image, (0, image_size_differnce))
            else:
                image_size_differnce = int((image_height - image_width) / 2)
                blank_image.paste(image, (image_size_differnce, 0))
            image = blank_image

        # Crop image image
        image_width, image_height = image.size
        if image_width != image_height and options.crop:
            print('Cropping image')
            min_size = min(image_width, image_height)
            print(min_size)
            if image_width == min_size:
                resized_image = image.crop((0, (image_height - image_width) / 2, min_size, ((image_height - image_width) / 2) + min_size))
            else:
                print((image_width - image_height) / 2)
                print(image_width, image_height)
                resized_image = image.crop(((image_width - image_height) / 2, 0, ((image_width - image_height) / 2) + min_size, min_size))
            image = resized_image

        image_width, _ = image.size

        last_size = 0
        for icon_file in icon_files:
            name = icon_file[0]
            size = icon_file[1]
            multiplier = icon_file[2]

            # Scale for retina
            adjusted_size = size * multiplier

            if image_width > last_size or options.all_sizes:
                last_size = size

                print('Processed: {}'.format(name))
                new_image = image.copy()
                new_image = new_image.resize((adjusted_size, adjusted_size), resize_methods.get(options.method, 0))
                new_image.save(os.path.join(temp_path, name), "PNG")

    # Convert using iconutil
    binary = '/usr/bin/iconutil'
    if os.path.isfile(binary):
        # Shell command
        command = '{0} -c icns {1}'.format(binary, temp_path)

        # Run the command and return results
        try:
            process_info = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except AttributeError:
            process_info = subprocess.popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except ValueError as err:
            print(err)
            return 2

        if process_info.returncode == 0:
            print('Creating file: {}'.format(options.outfile))
            os.rename(temp_file, options.outfile)
        else:
            print('Error creating file, error {}'.format(process_info.returncode))
            return process_info.returncode
    else:
        print('Please install {}'.format(binary))

    print('Done')
    return 0


if __name__ == '__main__':

    # Create the parser and give it the program version #
    parser = optparse.OptionParser('%prog [options]\n %prog will take an image and save it to Apple icns file.',
                                   version='%prog 1.0')

    # input file
    parser.add_option('-i', '--infile',
                      action='store', dest='infile', default=None,
                      help='Image file, required')

    # output file, assumed if missing
    parser.add_option('-o', '--outfile',
                      action='store', dest='outfile', default=None,
                      help='Icns file, optional. Default: Same as infile and icns extension')

    # crop image?
    parser.add_option('-c', '--crop',
                      action='store_true', dest='crop', default=False,
                      help='Crop image when resizing')

    # Maintain aspect ratio?
    parser.add_option('-k', '--keep_aspect',
                      action='store_true', dest='keep_aspect', default=False,
                      help='When resizing keep aspect ratio')

    # Scaling mathod
    parser.add_option('-m', '--method',
                      action='store', type='choice', dest='method', default='ANTIALIAS',
                      choices=('NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS', 'ANTIALIAS'),
                      help='Method to use. Valid choices are {}. Default: {}'.format(('NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS', 'ANTIALIAS'), 'ANTIALIAS'))

    # Maintain aspect ratio?
    parser.add_option('-a', '--allsizes',
                      action='store_true', dest='all_sizes', default=False,
                      help='When scaling, scale up to all sizes.  Not recommended')

    options, args = parser.parse_args()

    if options.infile is None:
        parser.print_help()
        exit(128)

    exit(main())
