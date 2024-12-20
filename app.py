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
    st.write(response_text)  # Display the original response for reference

# Function to get comments from Gemini API
def get_gemini_comments(image_path):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        image = Image.open(image_path)
        response = model.generate_content(
            [
                "You are an AI medical expert trained on a massive dataset of lumbar spine X-rays and their corresponding radiological reports. Analyze this X-ray as if you were comparing it to your learned knowledge of normal and abnormal spinal anatomy, derived from analyzing thousands of peer images. Provide a structured report, highlighting key findings and comparing them to expected normal values. Use medical terminology.",
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

    # Display results
    if comment:
        format_gemini_response(comment)  # Use the new formatting function

    # Clean up the temporary file
    os.remove("temp_image.jpg")
