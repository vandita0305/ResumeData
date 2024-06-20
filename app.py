import streamlit as st
import fitz  # PyMuPDF
import json
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_first_page(pdf_path):
    doc = fitz.open(pdf_path)
    first_page = doc.load_page(0)  # Load the first page
    text = first_page.get_text("text")
    return text

def extract_data_with_openai(text, template):
    prompt = f"Extract the following information from the resume text and format it as JSON:\n"
    for key in template.keys():
        prompt += f"{key}: \n"
    prompt += f"\nResume Text:\n{text}"

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=500
    )
    extracted_data = response.choices[0].text.strip()
    
    # Attempt to fix JSON if it's malformed
    try:
        return json.loads(extracted_data)
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON: {e}")
        st.error("Attempting to fix JSON format...")
        try:
            # Fix common JSON issues
            fixed_data = extracted_data
            # Ensure proper closing brackets
            if fixed_data.count('{') > fixed_data.count('}'):
                fixed_data += '}' * (fixed_data.count('{') - fixed_data.count('}'))
            if fixed_data.count('[') > fixed_data.count(']'):
                fixed_data += ']' * (fixed_data.count('[') - fixed_data.count(']'))

            return json.loads(fixed_data)
        except Exception as e:
            st.error(f"Could not fix JSON: {e}")
            return {}

def save_to_json(data, output_path):
    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Define the template with common resume fields
template = {
    "name": "",
    "email": "",
    "phone": "",
    "address": "",
    "summary": "",
    "skills": "",
    "education": "",
    "work_experience": "",
    "certifications": "",
    "projects": "",
    "languages": "",  # New field for languages
    "hobbies": "",    # New field for hobbies
    "linkedin": "",   # New field for LinkedIn profile
    "github": ""      # New field for GitHub profile
}

# Streamlit app
st.title("Resume PDF to JSON Converter")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Save uploaded file to disk
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("PDF uploaded successfully!")

    # Extract text from the first page of the PDF
    extracted_text = extract_text_from_first_page("uploaded_resume.pdf")

    st.text("Extracted Text:")
    st.write(extracted_text)

    # Convert extracted text to JSON format using OpenAI
    try:
        resume_data = extract_data_with_openai(extracted_text, template)
        
        # Ensure all fields from the template are present
        for key in template.keys():
            if key not in resume_data:
                resume_data[key] = ""

        # Save JSON data to file
        json_output_path = "resume_data.json"
        save_to_json(resume_data, json_output_path)

        st.success("Data extracted and saved to JSON!")

        # Display JSON file content
        with open(json_output_path, 'r') as json_file:
            st.json(json.load(json_file))
    except Exception as e:
        st.error(f"An error occurred: {e}")
