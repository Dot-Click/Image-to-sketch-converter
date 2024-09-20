import cv2

def model2(input_path,output_path):
    # Load the image
    image = cv2.imread(input_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    inverted = 255 - gray_image

    # Apply Gaussian Blur to the inverted image
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)

    # Invert the blurred image
    inverted_blur = 255 - blurred

    # Create the pencil sketch by dividing the grayscale image by the inverted blur
    pencil_sketch = cv2.divide(gray_image, inverted_blur, scale=256.0)

    # Apply Canny Edge Detection to the pencil sketch for enhanced effect
    edges = cv2.Canny(pencil_sketch, 50, 150)  # Adjust thresholds as needed

    # Invert the edges to get white edges on a black background
    edges_inverted = cv2.bitwise_not(edges)

    # Save the resulting pencil sketch with edges
    cv2.imwrite(output_path, edges_inverted)
