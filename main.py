from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import cv2
import numpy as np
import svgwrite
from werkzeug.utils import secure_filename
import logging
from waitress import serve
import uuid
from image_models.model2 import model2
from image_models.model3 import model3
from image_models.model6 import model6

app = Flask(__name__)
# Enable CORS
CORS(app)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


# Enable CORS
CORS(app)

upload_folder = os.path.join("static", "uploads")

app.config["UPLOAD"] = upload_folder
# Configure the folder to save uploaded images temporarily
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
app.config["UPLOAD_FOLDER"] = upload_folder
app.config["OUTPUT_FOLDER"] = upload_folder

# Make sure upload and output folders exist
os.makedirs(upload_folder, exist_ok=True)
os.makedirs(upload_folder, exist_ok=True)


def convert_to_outline_svg(
    image_path, output_svg_path, blur_value, canny_thresh1, canny_thresh2
):
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
                dwg.add(dwg.circle(center=(x, y), r=0.5, fill="black"))

    # Save the SVG file
    dwg.save()
    print(f"Outline SVG saved as: {output_svg_path}")


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
        raise ValueError(
            "CLAHE contrast enhancement is only valid for grayscale images."
        )


# Function to adjust brightness (simple addition of pixel values)
def adjust_brightness(image, value=30):
    return cv2.convertScaleAbs(image, alpha=1, beta=value)


# Function to apply sketching (Canny edge detection)
def apply_sketching(image, blur_value, canny_thresh1, canny_thresh2):
    """Applies edge detection to create a sketch-like effect."""
    blurred_image = cv2.GaussianBlur(image, (blur_value, blur_value), 0)
    edges = cv2.Canny(blurred_image, canny_thresh1, canny_thresh2)
    edges = cv2.bitwise_not(edges)
    return edges


@app.route("/convert", methods=["POST"])
def convert_image():
    # Check if an image file was uploaded
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "No image selected for uploading."}), 400

    # Secure the filename and save it
    filename = secure_filename(image_file.filename)

    # Validate file extension
    if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        return jsonify({"error": "Unsupported file format."}), 400

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image_file.save(image_path)

    # Read the image in grayscale
    image = cv2.imread(image_path, 0)

    # Get the optional parameters from the request (with defaults)
    blur_value = int(request.form.get("blur", 5))
    canny_thresh1 = int(request.form.get("canny_thresh1", 50))
    canny_thresh2 = int(request.form.get("canny_thresh2", 150))
    output_type = request.form.get("output_type", "image").lower()  # Default to 'svg'
    sharpness = float(request.form.get("sharpness", 1.5))  # Default to '1.5'
    contrast = (
        request.form.get("contrast", "true").lower() == "true"
    )  # Default to 'True'
    brightness = int(request.form.get("brightness", 30))  # Default to '30'
    model = int(request.form.get("model", 1))  # Default to '30'
    smoothness = int(request.form.get("smoothness", 5))  # Default smoothness value of 5
    denoise = int(request.form.get("denoise",  5))  # Default smoothness value of 5
    sigmaColor = int(
        request.form.get("sigmaColor", 75)
    )  # Default smoothness value of 5
   
    if denoise >= 2 or sigmaColor >= 2:
        image = cv2.bilateralFilter(image, denoise, sigmaColor, sigmaColor)
     
    # Step 1: Adjust sharpness
    if sharpness > 0 & model == 1:
        print("model 1 sharpness")
        image = increase_sharpness(image, alpha=sharpness)

    # Step 2: Adjust contrast
    
    if contrast & model == 1:
        print("model 1 contrast")
        try:
            image = increase_contrast(image)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # Step 3: Adjust brightness
    if brightness != 0 & model == 1:
        print("model 1 brightness")
        image = adjust_brightness(image, value=brightness)

    sketch_image = image
    image = increase_contrast(image)
    if model == 1:
        print("model 1")
        # Step 4: Apply sketching effect (edge detection)
        sketch_image = apply_sketching(
            image,
            blur_value=blur_value,
            canny_thresh1=canny_thresh1,
            canny_thresh2=canny_thresh2,
        )

    elif model == 2:
        print("model 2")
        sketch_image = model2(image, blur_value=21)
    elif model == 6:
        print("model 6")
        sketch_image = model6(image, smoothness=smoothness)

    elif model == 3:
        print("model 3")
        sketch_image = model3(image, smoothness=smoothness)

    # Generate a unique identifier (UUID) for the output filename
    unique_id = str(uuid.uuid4())

    if output_type == "svg":
        # Set the output file path for SVG
        output_svg_filename = f"{os.path.splitext(filename)[0]}_{unique_id}_outline.svg"
        output_svg_path = os.path.join(app.config["OUTPUT_FOLDER"], output_svg_filename)

        # Convert to SVG (assuming a function exists)
        convert_to_outline_svg(
            image_path, output_svg_path, blur_value, canny_thresh1, canny_thresh2
        )

        # Return the path to the output file
        return jsonify(
            {"message": "Image converted successfully.", "output_file": output_svg_path}
        )

    elif output_type == "image":
        # Set the output file path for image (e.g., PNG)
        output_image_filename = (
            f"{os.path.splitext(filename)[0]}_{unique_id}_outline.png"
        )
        output_image_path = os.path.join(
            app.config["OUTPUT_FOLDER"], output_image_filename
        )

        # Save the sketch image
        cv2.imwrite(output_image_path, sketch_image)

        # Return the path to the output file
        return jsonify(
            {
                "message": "Image converted successfully.",
                "output_file": output_image_path,
            }
        )

    else:
        return jsonify({"error": "Invalid output type. Must be 'svg' or 'image'."}), 400


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
    #app.run(debug=True)
