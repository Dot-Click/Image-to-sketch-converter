from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
import numpy as np
import svgwrite
from werkzeug.utils import secure_filename
import logging
from waitress import serve
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
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)
    
    # Get the optional parameters from the request (with defaults)
    blur_value = int(request.form.get('blur', 5))
    canny_thresh1 = int(request.form.get('canny_thresh1', 50))
    canny_thresh2 = int(request.form.get('canny_thresh2', 150))
    
    # Set the output file path
    output_svg_filename = os.path.splitext(filename)[0] + '_outline.svg'
    output_svg_path = os.path.join(app.config['OUTPUT_FOLDER'], output_svg_filename)
    
    # Call the function to convert the image to an outline SVG
    convert_to_outline_svg(image_path, output_svg_path, blur_value, canny_thresh1, canny_thresh2)
    
    # Return the path to the output file
    return jsonify({"message": "Image converted successfully.", "output_svg": output_svg_path})

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)