import cv2
import numpy as np


def model3(image, smoothness=5, remove_noise="none"):
    # Check if the image has 3 or 4 channels before converting
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Convert to grayscale if the image is colored
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image

    # Invert the grayscale image
    inverted_image = 255 - gray_image

    # Apply GaussianBlur to the inverted image with a kernel size dependent on smoothness
    kernel_size = max(
        3, 2 * int(smoothness // 2) + 1
    )  # Ensure the kernel is odd and >= 3
    blurred = cv2.GaussianBlur(inverted_image, (kernel_size, kernel_size), 0)

    # Invert the blurred image
    inverted_blur = 255 - blurred

    # Create the pencil sketch by dividing the grayscale image by the inverted blur
    sketch = cv2.divide(gray_image, inverted_blur, scale=256.0)

    # Print debug information for noise removal
    print(f"Noise removal type: {remove_noise}")

    # Apply noise removal if needed
    median = cv2.medianBlur(sketch,11)
    if remove_noise.lower() in ["blacks", "white", "both"]:
        sketch = remove_image_noise(sketch, noise_type=remove_noise)
    return median


def remove_image_noise(image, noise_type="both"):
    """
    Remove black or white noise from the image based on the noise_type parameter.
    noise_type can be "black", "white", or "both".
    """
    # Define a kernel size for morphological operations based on image size
    kernel_size = (7, 7)  # Try increasing the kernel size for stronger noise removal
    kernel = np.ones(kernel_size, np.uint8)  # You can adjust the size of the kernel
    resizeBeforeImage = cv2.resize(image,(500,500))
    cv2.imshow('before ',resizeBeforeImage)
    cv2.waitKey(0) 
    if noise_type == "black":
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        # Use morphological closing to remove black noise (small black spots)
    elif noise_type == "white":
        # Use morphological opening to remove white noise (small white spots)
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    elif noise_type == "both":
        # First remove white noise, then remove black noise
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    resizeAfterImage = cv2.resize(image,(500,500))
    cv2.imshow('after ',resizeAfterImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return image


# Example usage:
# sketch = model3(input_image, smoothness=5, remove_noise="both")  # Remove both black and white noise
# sketch = model3(input_image, smoothness=5, remove_noise="white")  # Remove only white noise
# sketch = model3(input_image, smoothness=5, remove_noise="black")  # Remove only black noise
