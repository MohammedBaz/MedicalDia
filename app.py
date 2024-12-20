import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
import os
import re

# Configure API Key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to highlight regions on the image (if coordinates are provided)
def highlight_regions(image_path, coordinates):
    """
    Highlights regions on the image based on the provided coordinates.
    
    Args:
        image_path: Path to the image file.
        coordinates: A list of coordinates (or bounding boxes) to highlight. 
                     The format depends on how Gemini provides them in the response.
                     Example: [(x1, y1, x2, y2), (x1, y1, x2, y2), ...]
    """
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        for coord in coordinates:
            # Assuming coordinates are provided as (x1, y1, x2, y2) bounding boxes
            draw.rectangle(coord, outline="red", width=3)
        img.save("temp_image_highlighted.jpg")  # Save the modified image
        st.image("temp_image_highlighted.jpg", caption="Highlighted Image", use_container_width=True)
    except Exception as e:
        st.error(f"Error highlighting regions: {e}")

# Function to extract coordinates from Gemini's response (using regular expressions)
def extract_coordinates_from_response(response_text):
    """
    Attempts to extract coordinate information from the Gemini response text.

    This is a very basic example and might need to be significantly improved
    based on the actual format of Gemini's output.
    """
    coordinates = []
    # Example: Look for bounding box coordinates in the format (x1, y1, x2, y2)
    matches = re.findall(r"\((\d+), (\d+), (\d+), (\d+)\)", response_text)  # Adjust regex as needed
    for match in matches:
        x1, y1, x2, y2 = map(int, match)
        coordinates.append((x1, y1, x2, y2))
    return coordinates

# ... (rest of the code: format_gemini_response, etc.)

# Function to get comments from Gemini API (Modified Prompt)
def get_gemini_comments(image_path):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        image = Image.open(image_path)
        response = model.generate_content(
            [
                "You are an AI medical expert trained on a massive dataset of lumbar spine X-rays. Analyze this X-ray and provide a structured report. Highlight key findings and compare them to expected normal values. If you identify any regions of concern (e.g., areas of significant curvature, disc abnormalities), specify their approximate coordinates or bounding boxes in the format (x1, y1, x2, y2).",
                image,
            ]
        )
        response.resolve()
        return response.text
    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return None

# ... (Streamlit Interface code)

if uploaded_file is not None:
    # ... (Save the uploaded file temporarily)

    # Analyze
    with st.spinner("Analyzing..."):
        comment = get_gemini_comments("temp_image.jpg")

    # Display results and attempt to highlight regions
    if comment:
        format_gemini_response(comment)  # Display the formatted text response

        # Attempt to extract coordinates and highlight regions
        coordinates = extract_coordinates_from_response(comment)
        if coordinates:
            highlight_regions("temp_image.jpg", coordinates)
        else:
            st.write("Could not extract coordinates for highlighting from the response.")

    # ... (Clean up the temporary file)
