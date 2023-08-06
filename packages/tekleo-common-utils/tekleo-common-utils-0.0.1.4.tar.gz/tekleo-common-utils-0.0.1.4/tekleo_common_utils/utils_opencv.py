import cv2
import numpy
from numpy import ndarray
from injectable import injectable


@injectable
class UtilsOpencv:
    def get_dimensions_hw(self, image_cv: ndarray) -> (int, int):
        h, w = image_cv.shape[:2]
        return h, w

    def get_dimensions_wh(self, image_cv: ndarray) -> (int, int):
        h, w = image_cv.shape[:2]
        return w, h

    def get_number_of_channels(self, image_cv: ndarray) -> int:
        if image_cv.ndim == 2:
            return 1
        elif image_cv.ndim == 3:
            return image_cv.shape[-1]
        else:
            raise ValueError("Weird image with ndim=" + str(image_cv.ndim))

    def are_images_equal(self, image_cv_a: ndarray, image_cv_b: ndarray) -> bool:
        if image_cv_a.shape == image_cv_b.shape:
            difference = cv2.subtract(image_cv_a, image_cv_b)
            b, g, r = cv2.split(difference)
            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                return True
            else:
                return False
        else:
            return False

    def convert_to_grayscale(self, image_cv: ndarray) -> ndarray:
        if self.get_number_of_channels(image_cv) == 1:
            return image_cv
        else:
            return cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

    def blur_gaussian(self, image_cv: ndarray, blur_x: int, blur_y: int) -> ndarray:
        new_image_cv = image_cv.copy()
        new_image_cv = cv2.GaussianBlur(new_image_cv, (blur_x, blur_y), 0)
        return new_image_cv

    def get_most_occurring_color(self, image_cv: ndarray, apply_blur: bool = True) -> (int, int, int):
        if apply_blur:
            image_cv = self.blur_gaussian(image_cv, 25, 25)

        width, height, channels = image_cv.shape
        color_count_map = {}
        for y in range(0, height):
            for x in range(0, width):
                BGR = (int(image_cv[x, y, 0]), int(image_cv[x, y, 1]), int(image_cv[x, y, 2]))
                if BGR in color_count_map:
                    color_count_map[BGR] += 1
                else:
                    color_count_map[BGR] = 1
    
        max_count = 0
        max_BGR = (0, 0, 0)
        for BGR in color_count_map:
            count = color_count_map[BGR]
            if count > max_count:
                max_count = count
                max_BGR = BGR
    
        return max_BGR

    # Image transformations
    #-------------------------------------------------------------------------------------------------------------------
    # Rotate (preserving original dimensions of the image)
    def rotate_bound(self, image_cv: ndarray, angle: float) -> ndarray:
        if angle == 0:
            return image_cv
        image_result = image_cv.copy()
        h, w = image_result.shape[:2]
        c_x, c_y, = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D((c_x, c_y), angle, 1.0)
        image_result = cv2.warpAffine(image_result, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return image_result

    # Rotate (changing dimensions of the original image)
    def rotate_free(self, image_cv: ndarray, angle: float) -> ndarray:
        if angle == 0:
            return image_cv
        image_result = image_cv.copy()
        h, w = image_result.shape[:2]
        c_x, c_y, = (w // 2, h // 2)

        # Compute the rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D((c_x, c_y), angle, 1.0)
        rotation_matrix_cos = numpy.abs(rotation_matrix[0, 0])
        rotation_matrix_sin = numpy.abs(rotation_matrix[0, 1])

        # Compute the new bounding dimensions of the image
        new_w = int((h * rotation_matrix_sin) + (w * rotation_matrix_cos))
        new_h = int((h * rotation_matrix_cos) + (w * rotation_matrix_sin))

        # Adjust the rotation matrix to take into account translation
        rotation_matrix[0, 2] += (new_w / 2) - c_x
        rotation_matrix[1, 2] += (new_h / 2) - c_y

        # Rotate
        image_result = cv2.warpAffine(image_result, rotation_matrix, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return image_result

    # Rotate (smartly, deciding which way of rotation will work better here)
    def rotate(self, image_cv: ndarray, angle: float, rotate_bound_threshold_angle: float = 20.0) -> ndarray:
        if -1.0 * rotate_bound_threshold_angle <= angle <= rotate_bound_threshold_angle:
            return self.rotate_bound(image_cv, angle)
        else:
            return self.rotate_free(image_cv, angle)
    #-------------------------------------------------------------------------------------------------------------------



    # Image deskewing
    #-------------------------------------------------------------------------------------------------------------------
    # Calculate skew angle of an image
    def calculate_skew_angle(self, image_cv: ndarray) -> float:
        # Prep image, copy, convert to gray scale, blur, and threshold
        image_result = image_cv.copy()
        gray = self.convert_to_grayscale(image_result)
        blur = self.blur_gaussian(gray, 9, 9)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Apply dilate to merge text into meaningful lines/paragraphs.
        # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
        # But use smaller kernel on Y axis to separate between different blocks of text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        dilate = cv2.dilate(thresh, kernel, iterations=5)

        # Find all contours
        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)
        if len(contours) == 0:
            return 0

        # Find largest contour and surround in min area box
        largestContour = contours[0]
        minAreaRect = cv2.minAreaRect(largestContour)

        # Determine the angle. Convert it to the value that was originally used to obtain skewed image
        angle = minAreaRect[-1]
        if angle < -45:
            angle = 90 + angle
            return -1.0 * angle
        elif angle > 45:
            angle = 90 - angle
            return angle
        return -1.0 * angle

    # Deskew image
    def deskew(self, image_cv: ndarray) -> (ndarray, float):
        angle = self.calculate_skew_angle(image_cv)
        rotated_image_cv = self.rotate(image_cv, -1.0 * angle)
        return rotated_image_cv, angle
    #-------------------------------------------------------------------------------------------------------------------
