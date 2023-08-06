from PIL import Image as image_pil_main
from PIL.Image import Image
import cv2
import numpy
import requests
import tempfile
import io
import base64
from numpy import ndarray
from injectable import injectable, autowired, Autowired
from tekleo_common_utils.utils_random import UtilsRandom


@injectable
class UtilsImage:
    @autowired
    def __init__(self, utils_random: Autowired(UtilsRandom)):
        self.utils_random = utils_random

    def convert_image_pil_to_image_cv(self, image_pil: Image) -> ndarray:
        return cv2.cvtColor(numpy.array(image_pil), cv2.COLOR_RGB2BGR)

    def convert_image_cv_to_image_pil(self, image_cv: ndarray) -> Image:
        return image_pil_main.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

    def open_image_pil(self, image_path: str) -> Image:
        return image_pil_main.open(image_path)

    def open_image_cv(self, image_path: str) -> ndarray:
        return self.convert_image_pil_to_image_cv(self.open_image_pil(image_path))

    def save_image_pil(self, image_pil: Image, image_path: str) -> str:
        image_pil.save(image_path)
        return image_path

    def save_image_cv(self, image_cv: ndarray, image_path: str) -> str:
        return self.save_image_pil(self.convert_image_cv_to_image_pil(image_cv), image_path)

    def debug_image_cv(self, image_cv: ndarray, window_name: str = 'Debug Image'):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, image_cv)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def download_image_pil(self, image_url: str, timeout_in_seconds: int = 90) -> Image:
        # Make request
        headers = {'User-Agent': self.utils_random.get_random_user_agent()}
        response = requests.get(image_url, headers=headers, timeout=timeout_in_seconds, stream=True)
        response.raise_for_status()

        # Download the image into buffer
        buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
        downloaded = 0
        for chunk in response.iter_content(chunk_size=1024):
            downloaded += len(chunk)
            buffer.write(chunk)
        buffer.seek(0)

        # Convert buffer to image
        image = image_pil_main.open(io.BytesIO(buffer.read()))
        return image

    def encode_image_pil_as_base64(self, image_pil: Image) -> str:
        bytes_io = io.BytesIO()
        image_pil.save(bytes_io, format="PNG")
        return str(base64.b64encode(bytes_io.getvalue()), 'utf-8')

    def decode_image_pil_from_base64(self, image_base64: str) -> Image:
        image_bytes = base64.b64decode(bytes(image_base64, 'utf-8'))
        image = image_pil_main.open(io.BytesIO(image_bytes))
        return image

    def clear_exif_data(self, image_pil: Image) -> Image:
        image_data = list(image_pil.getdata())
        image_without_exif_pil = image_pil_main.new(image_pil.mode, image_pil.size)
        image_without_exif_pil.putdata(image_data)
        return image_without_exif_pil
