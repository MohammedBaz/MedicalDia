import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
import os
import re

# Configure API Key using Streamlit Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to highlight regions on the image
def highlight_regions(image_path, coordinates):
    """
    Highlights regions on the image based on the provided coordinates.
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
    """
    coordinates = []
    # Example: Look for bounding box coordinates in the format (x1, y1, x2, y2)
    matches = re.findall(r"\((\d+), (\d+), (\d+), (\d+)\)", response_text)  # Adjust regex as needed
    for match in matches:
        x1, y1, x2, y2 = map(int, match)
        coordinates.append((x1, y1, x2, y2))
    return coordinates

# Function to extract key features and format the output
def format_gemini_response(response_text):
    """
    Formats the Gemini response into a table-like structure for better readability.
    """
    # 1. Extract Key Features (using regular expressions or other methods)
    vertebrae_matches = re.findall(r"vertebrae:.*?\.", response_text, re.IGNORECASE)
    alignment_matches = re.findall(r"alignment:.*?\.", response_text, re.IGNORECASE)
    disc_matches = re.findall(r"disc.*?:.*?\.", response_text, re.IGNORECASE)
    curvature_matches = re.findall(r"curvature:.*?\.", response_text, re.IGNORECASE)

    # 2. Create a dictionary to store findings
    findings = {}
    if vertebrae_matches:
        findings["Vertebrae"] = vertebrae_matches[0]
    if alignment_matches:
        findings["Alignment"] = alignment_matches[0]
    if disc_matches:
        findings["Disc Spaces"] = disc_matches[0]
    if curvature_matches:
        findings["Curvature"] = curvature_matches[0]

    # 3. Build a table-like output using Streamlit
    if findings:
        st.subheader("Key Findings:")
        for key, value in findings.items():
            st.markdown(f"**{key}:** {value}")
    else:
        st.write("No specific findings extracted.")

    # 4. Add further analysis or summary if needed
    st.subheader("Overall Analysis:")
    st.write(response_text)  # Display the original response for reference

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

# Streamlit Interface
st.title("Lumbar Spine X-ray Analysis (using Gemini)")
st.write(
    "Upload a frontal lumbar spine X-ray image for analysis. This app uses Google's Gemini AI, which has been trained on a vast dataset of medical images."
)

# Add an "About" section
with st.expander("About the Technology"):
    st.markdown(
        """
        This application leverages the power of Google's Gemini 1.5 Flash, a large language model with advanced image understanding capabilities.

        **How it Works:**

        *   **Data-Driven Analysis:** Gemini has been trained on a massive dataset of images, including X-rays, and associated medical reports. It has learned to identify patterns and relationships between image features and medical conditions.
        *   **Comparative Approach:** When you upload an X-ray, Gemini analyzes it by comparing it to its internal representation of normal and abnormal spinal anatomy, derived from its training data. This is similar to how a radiologist would compare an X-ray to their knowledge gained from studying many examples.
        *   **Structured Reporting:** The AI is prompted to provide a structured report, highlighting key findings and comparing them to expected normal values. This facilitates a more systematic and objective analysis.
        *   **Coordinate Extraction:** The AI attempts to identify regions of concern and provide their approximate coordinates or bounding boxes.

        **Engineering Science Principles:**

        *   **Machine Learning:** The core of this application is based on machine learning, a field of computer science that enables systems to learn from data without explicit programming.
        *   **Pattern Recognition:** Gemini uses pattern recognition algorithms to identify relevant features in the X-ray images.
        *   **Statistical Inference:** The AI draws conclusions based on statistical patterns learned from the training data.

        **Disclaimer:** This application is for informational purposes only and should not be considered a substitute for professional medical advice.
        """
    )

uploaded_file = st.file_uploader("Choose an X-ray image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("temp_image.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display the image
    st.image("temp_image.jpg", caption="Uploaded Image", use_container_width=True)

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

    # Clean up the temporary file
    os.remove("temp_image.jpg")
