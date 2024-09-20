
import cv2

def model3(input_path,output_path):
    # Load the image
    image = cv2.imread(input_path)

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gray_image = cv2.cvtColor(image, 0)

    # Invert the grayscale image
    inverted_image = 255 - gray_image

    # Apply GaussianBlur to the inverted image
    blurred = cv2.GaussianBlur(inverted_image, (51, 221), 0)

    # Invert the blurred image
    inverted_blur = 255 - blurred

    # Create the pencil sketch by dividing the grayscale image by the inverted blur
    sketch = cv2.divide(gray_image, inverted_blur, scale=256.0)
    # edges = cv2.Canny(sketch, 0, 0)  # Adjust thresholds as needed
    # edges_inverted = cv2.bitwise_not(edges)
    # Save the sketch
    cv2.imwrite(output_path, sketch)

    print("Sketch created successfully!")
