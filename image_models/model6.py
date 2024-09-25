import cv2
import numpy as np


def model6(image, smoothness=5):

   
    # cv2.imshow('model6',resizeImage)
    # cv2.waitKey(0);
    # cv2.destroyAllWindows()

    if len(image.shape) == 3 and image.shape[2] == 3:
        # Convert to grayscale if the image is colored
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        # If the image is already grayscale
        gray_image = image

    # Invert the grayscale image
    inverted_image = 255 - gray_image

    # Apply GaussianBlur to the inverted image with a kernel size dependent on smoothness
    # Ensure the kernel size is odd and positive for GaussianBlur
    kernel_size = max(
        3, 2 * int(smoothness // 2) + 1
    )  # Ensure the kernel is odd and >= 3
    blurred = cv2.GaussianBlur(inverted_image, (kernel_size, kernel_size), 0)
    # Invert the blurred image
   
    # blurred = cv2.medianBlur(inverted_image,  7)
    # resizeImage = cv2.resize(blurred, (500, 500))
    # cv2.imshow('blurredblurred',resizeImage)
    # cv2.waitKey(0);
    # cv2.destroyAllWindows()
    inverted_blur = 255 - blurred

    # Create the pencil sketch by dividing the grayscale image by the inverted blur
    sketch = cv2.divide(gray_image, inverted_blur, scale=256.0)
    return sketch

    # cv2.imwrite(output_path, sketch)

    print("Sketch created successfully!")
