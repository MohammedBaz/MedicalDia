import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import re

# Configure API Key using Streamlit Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to extract key features and format the output
def format_gemini_response(response_text):
    """
    Formats the Gemini response into a table-like structure for better readability.
    """
    # 1. Extract Key Features (using regular expressions or other methods)
    # Example: Find sentences containing specific keywords
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
    st.write(response_text) # Display the original response for reference

# Function to get comments from Gemini API
def get_gemini_comments(image_path):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        image = Image.open(image_path)
        response = model.generate_content(
            [
                "You are a medical expert. Analyze this lumbar spine X-ray and provide comments, specifically focusing on the presence and severity of scoliosis. Use medical terms and the output should highlight the key findings and a small summery",
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
    "Upload a frontal lumbar spine X-ray image for analysis. This app uses Google's Gemini through the google-generativeai library."
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

    # Display results
    if comment:
        format_gemini_response(comment)  # Use the new formatting function

    # Clean up the temporary file
    os.remove("temp_image.jpg")
