import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
import os
import re
import pandas as pd

# Configure API Key using Streamlit Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- Checklist of Diagnostic Points ---
checklist = {
    "Lungs": [
        "cancer",
        "infection",
        "air collecting",
        "lung collapse",
        "emphysema",
        "cystic fibrosis",
        "complications",
    ],
    "Heart-Related Lung Problems": ["fluid in your lungs", "congestive heart failure"],
    "Heart Size and Outline": [
        "heart failure",
        "fluid around the heart",
        "heart valve problems",
    ],
    "Blood Vessels": [
        "aortic aneurysms",
        "blood vessel problems",
        "congenital heart disease",
    ],
    "Calcium Deposits": [
        "calcium in your heart",
        "calcium in blood vessels",
        "damage to heart valves",
        "damage to coronary arteries",
        "damage to heart muscle",
        "calcified nodules",
    ],
    "Fractures": ["rib.*fracture", "spine.*fracture", "bone.*problem"],
    "Postoperative Changes": ["air leaks", "fluid.*buildup", "air buildup"],
    "Pacemaker, Defibrillator, Catheter": [
        "pacemaker",
        "defibrillator",
        "catheter",
        "positioned correctly",
    ],
}

# Function to highlight regions on the image (if coordinates are provided)
def highlight_regions(image_path, coordinates):
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        for coord in coordinates:
            draw.rectangle(coord, outline="red", width=3)
        img.save("temp_image_highlighted.jpg")
        st.image("temp_image_highlighted.jpg", caption="Highlighted Image", use_container_width=True)
    except Exception as e:
        st.error(f"Error highlighting regions: {e}")

# Function to extract coordinates from Gemini's response
def extract_coordinates_from_response(response_text):
    coordinates = []
    matches = re.findall(r"\((\d+), (\d+), (\d+), (\d+)\)", response_text)
    for match in matches:
        x1, y1, x2, y2 = map(int, match)
        coordinates.append((x1, y1, x2, y2))
    return coordinates

# Function to format the Gemini response into a table
def format_gemini_response(response_text):
    """
    Formats the Gemini response into a table for better readability.
    """
    data = []

    for category, keywords in checklist.items():
        findings = []
        status = "Normal"
        for keyword in keywords:
            pattern = re.compile(keyword, re.IGNORECASE)
            matches = pattern.findall(response_text)
            if matches:
                status = "Potential Issue"
                findings.extend(matches)

        data.append(
            {
                "Category": category,
                "Findings": ", ".join(findings) if findings else "No issues detected",
                "Status": status,
            }
        )

    df = pd.DataFrame(data)
    st.subheader("Key Findings (Table):")
    st.table(df)

    # Minimize Overall Analysis to a single line summary
    st.subheader("Summary:")
    st.write(response_text)  # Display a summarized or the first sentence of the original response

# Function to get comments from Gemini API (Modified Prompt)
def get_gemini_comments(image_path):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        image = Image.open(image_path)
        response = model.generate_content(
            [
                "You are an AI medical expert trained on a massive dataset of X-rays. Analyze this X-ray and provide a structured report based on the following criteria: "
                + ", ".join(checklist.keys())
                + ". For each point, indicate if there are any findings suggestive of a problem or if it appears normal. Use medical terminology.",
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
    "Upload a frontal lumbar spine X-ray image for analysis. This app uses Google's Gemini AI."
)

# Remove the "About" section

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

    # Display results in a table
    if comment:
        format_gemini_response(comment)

        # Attempt to extract coordinates and highlight regions (if applicable)
        coordinates = extract_coordinates_from_response(comment)
        if coordinates:
            highlight_regions("temp_image.jpg", coordinates)
        else:
            st.write("Could not extract coordinates for highlighting from the response.")

    # Clean up the temporary file
    os.remove("temp_image.jpg")
