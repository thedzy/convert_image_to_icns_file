# convert_image_to_icns_file
## Convert an image to Apple icns format

Intended as a replacement to Xcode's missing icon composer and a simplified interface for iconutils.

```bash
Usage: convert_image_to_icns_file.py [options]
 convert_image_to_icns_file.py will take an image and save it to Apple icns file.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -i INFILE, --infile=INFILE
                        Image file, required
  -o OUTFILE, --outfile=OUTFILE
                        Icns file, optional. Default: Same as infile and icns
                        extension
  -c, --crop            Crop image when resizing
  -k, --keep_aspect     When resizing keep aspect ratio
  -m METHOD, --method=METHOD
                        Method to use. Valid choices are ('NEAREST',
                        'BILINEAR', 'BICUBIC', 'LANCZOS', 'ANTIALIAS').
                        Default: ANTIALIAS
  -a, --allsizes        When scaling, scale up to all sizes.  Not recommended
```
