 
import cv2
import numpy as np

def model5(input_path,output_path):
    # Read the image
    image = cv2.imread(input_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to create a binary image
    _, roi = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an empty image for drawing contours
    output = np.zeros_like(gray)

    # Draw the contours on the empty image
    cv2.drawContours(output, contours, -1, (255, 255, 255), thickness=1)

    # Remove the boundary by masking the edges
    boundary = 255 * np.ones_like(gray)
    boundary[1:-1, 1:-1] = 0

    # Mask the boundary from the output image
    output = cv2.bitwise_xor(output, boundary)
    inverted_blur = cv2.bitwise_not(output)
    # Save the output image
    cv2.imwrite(output_path, inverted_blur)

    print("Outline sketch saved successfully!")
