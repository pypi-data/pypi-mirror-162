# TekLeo Common Utils
A python package with shared utils methods that can be used in a variety of python projects, but are mostly tailored towards web / ml applications.

Feel free to drop your suggestions, hopefully one day this will be a pretty comprehensive library of cool shared tools.

# Description
Under construction... This shit is boring to write, will finish description and examples when I have more free time.

### Utils ID
- `generate_uuid` self-explanatory

### Utils Image
Conversion between PIL and OpenCV formats. Opening, saving, downloading, encoding images.
- `convert_image_pil_to_image_cv` convert PIL image to OpenCV image
- `convert_image_cv_to_image_pil` convert OpenCV image to PIL image
- `open_image_pil` load PIL image from file
- `open_image_cv` load OpenCV image from file
- `save_image_pil` save PIL image to file
- `save_image_cv` save OpenCV image to file
- `debug_image_cv` show a GUI window with an OpenCV image displayed in it
- `download_image_pil` download PIL image from url
- `encode_image_pil_as_base64` convert PIL image to base 64 encoded string
- `decode_image_pil_from_base64` convert base 64 encoded string to PIL image

### Utils OpenCV
Various OpenCV tools you might commonly need
- `blur_gaussian` apply Gaussian blur
- `rotate_bound` rotate image bounded, preserving the original dimensions and cutting all rotated content that doesn't fit into original image size 
- `rotate_free` rotate image freely, changing dimensions to make sure all rotated content fits inside
- `deskew` deskew (straighten) image, works best on text images, like page scans and etc.

### Utils Random
Random related stuff beyond the default `random` module
- `get_random_user_agent` generate a random User-Agent for HTTP headers (using [user_agent library](https://pypi.org/project/user-agent/)) 

### UtilsPing
Special utils to generate ping replies. Useful in web services.
- `build` generate ping reply object

# TODO / next updates
- Needs a lot of unit tests & usage examples

# Installation
 
## Normal installation

```bash
pip install tekleo-common-utils
```

## Development installation

```bash
git clone https://github.com/jpleorx/tekleo-common-utils.git
cd tekleo-common-utils
pip install --editable .
```

# Links
In case you’d like to check my other work or contact me:
* [Personal website](https://tekleo.net/)
* [GitHub](https://github.com/jpleorx)
* [PyPI](https://pypi.org/user/JPLeoRX/)
* [DockerHub](https://hub.docker.com/u/jpleorx)
* [Articles on Medium](https://medium.com/@leo.ertuna)
* [LinkedIn (feel free to connect)](https://www.linkedin.com/in/leo-ertuna-14b539187/)