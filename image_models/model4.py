import cv2

def model4(input_path,output_path):
    # Read the image
    image = cv2.imread(input_path)

    # Convert the image to grayscale
    grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    invert = cv2.bitwise_not(grey_img)

    # Apply a Gaussian blur to the inverted image
    blur = cv2.GaussianBlur(invert, (51, 151), 0)

    # Invert the blurred image
    inverted_blur = cv2.bitwise_not(blur)

    # Create the sketch by dividing the grayscale image by the inverted blurred image
    sketch = cv2.divide(grey_img, inverted_blur, scale=256.0)
    cv2.imwrite(output_path, sketch)
