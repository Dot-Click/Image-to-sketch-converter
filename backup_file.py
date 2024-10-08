from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import cv2
import numpy as np
import svgwrite
from werkzeug.utils import secure_filename
import logging
from waitress import serve
import uuid
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

app = Flask(__name__)

# Enable CORS
CORS(app)

# Configure the folder to save uploaded images temporarily
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Make sure upload and output folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_to_outline_svg(image_path, output_svg_path, blur_value, canny_thresh1, canny_thresh2):
    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Use a Gaussian Blur to smooth the image and reduce noise
    blurred_image = cv2.GaussianBlur(image, (blur_value, blur_value), 0)
    
    # Apply edge detection (Canny edge detection)
    edges = cv2.Canny(blurred_image, threshold1=canny_thresh1, threshold2=canny_thresh2)

    # Create an SVG drawing
    height, width = edges.shape
    dwg = svgwrite.Drawing(output_svg_path, size=(width, height))
    
    # Draw the edges as lines in the SVG file
    for y in range(height):
        for x in range(width):
            if edges[y, x] > 0:  # If an edge pixel is detected
                dwg.add(dwg.circle(center=(x, y), r=0.5, fill='black'))

    # Save the SVG file
    dwg.save()
    print(f"Outline SVG saved as: {output_svg_path}")

def convert_to_outline_image(image_path, output_image_path, blur_value, canny_thresh1, canny_thresh2):
    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Use a Gaussian Blur to smooth the image and reduce noise
    blurred_image = cv2.GaussianBlur(image, (blur_value, blur_value), 0)
    
    # Apply edge detection (Canny edge detection)
    edges = cv2.Canny(blurred_image, threshold1=canny_thresh1, threshold2=canny_thresh2)
    
    # Invert the colors so the edges are black and background is white
    edges_inverted = cv2.bitwise_not(edges)
    
    # Save the output image
    cv2.imwrite(output_image_path, edges_inverted)
    print(f"Outline Image saved as: {output_image_path}")


# Function to adjust sharpness using an unsharp mask
def increase_sharpness(image, alpha=1.5, beta=-0.5):
    """Increase sharpness by blending the original image with a blurred version."""
    blurred_image = cv2.GaussianBlur(image, (9, 9), 10)
    sharp_image = cv2.addWeighted(image, alpha, blurred_image, beta, 0)
    return sharp_image

# Function to adjust contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
def increase_contrast(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    if len(image.shape) == 2:  # Grayscale image
        return clahe.apply(image)
    else:
        raise ValueError("CLAHE contrast enhancement is only valid for grayscale images.")

# Function to adjust brightness (simple addition of pixel values)
def adjust_brightness(image, value=30):
    return cv2.convertScaleAbs(image, alpha=1, beta=value)

@app.route('/convert', methods=['POST'])
def convert_image():
    # Check if an image file was uploaded
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided."}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No image selected for uploading."}), 400
    
    # Secure the filename and save it
    filename = secure_filename(image_file.filename)
    
    # Validate file extension
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        return jsonify({"error": "Unsupported file format."}), 400
    
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)
    
    # Read the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Get the optional parameters from the request (with defaults)
    blur_value = int(request.form.get('blur', 5))
    canny_thresh1 = int(request.form.get('canny_thresh1', 50))
    canny_thresh2 = int(request.form.get('canny_thresh2', 150))
    output_type = request.form.get('output_type', 'svg').lower()  # Default to 'svg'
    sharpness = float(request.form.get('sharpness', 1.5))  # Default to '1.5'
    contrast = request.form.get('contrast', 'true').lower() == 'true'  # Default to 'True'
    brightness = int(request.form.get('brightness', 30))  # Default to '30'
    
    # Increase sharpness
    if sharpness > 0:
        image = increase_sharpness(image, alpha=sharpness)
    
    # Adjust contrast
    if contrast:
        try:
            image = increase_contrast(image)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    # Adjust brightness
    if brightness != 0:
        image = adjust_brightness(image, value=brightness)
    
    # Generate a unique identifier (UUID) for the output filename
    unique_id = str(uuid.uuid4())
    
    if output_type == 'svg':
        # Set the output file path for SVG
        output_svg_filename = f"{os.path.splitext(filename)[0]}_{unique_id}_outline.svg"
        output_svg_path = os.path.join(app.config['OUTPUT_FOLDER'], output_svg_filename)
        
        # Convert to SVG
        convert_to_outline_svg(image_path, output_svg_path, blur_value, canny_thresh1, canny_thresh2)
        
        # Return the path to the output file
        return jsonify({"message": "Image converted successfully.", "output_file": output_svg_path})

    elif output_type == 'image':
        # Set the output file path for image (e.g., PNG)
        output_image_filename = f"{os.path.splitext(filename)[0]}_{unique_id}_outline.png"
        output_image_path = os.path.join(app.config['OUTPUT_FOLDER'], output_image_filename)
        
        # Convert to Image
        convert_to_outline_image(image_path, output_image_path, blur_value, canny_thresh1, canny_thresh2)
        
        # Return the path to the output file
        return jsonify({"message": "Image converted successfully.", "output_file": output_image_path})

    else:
        return jsonify({"error": "Invalid output type. Must be 'svg' or 'image'."}), 400


if __name__ == '__main__':
    app.run(debug=True)
