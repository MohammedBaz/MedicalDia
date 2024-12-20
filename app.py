import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# Configure API Key using Streamlit Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to get comments from Gemini API
def get_gemini_comments(image_path):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
        image = Image.open(image_path)
        response = model.generate_content(
            [
                "You are a medical expert. Analyze this lumbar spine X-ray and provide comments, specifically focusing on the presence and severity of scoliosis. Use medical terms",
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
    st.image("temp_image.jpg", caption="Uploaded Image", use_container_width=True)  # Updated parameter

    # Analyze
    with st.spinner("Analyzing..."):
        comment = get_gemini_comments("temp_image.jpg")

    # Display results
    if comment:
        st.subheader("Analysis:")
        st.write(f"**Comment:** {comment}")

    # Clean up the temporary file
    os.remove("temp_image.jpg")
