import streamlit as st
import fitz  # PyMuPDF
import json
import re

# Function to extract text from all pages of the PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text

# Function to extract table data from text
def extract_table_data(text, start_marker, end_marker, column_headers):
    start = text.find(start_marker) + len(start_marker)
    end = text.find(end_marker, start)
    table_text = text[start:end].strip()

    lines = table_text.split('\n')
    data = []
    for line in lines[1:]:
        values = line.split()
        if len(values) == len(column_headers):
            row = {column_headers[i]: values[i] for i in range(len(column_headers))}
            data.append(row)
    return data

# Function to parse the text and extract all fields and tables
def extract_fields_from_text(text):
    fields = {}

    patterns = {
        'passport_no': r'Passport No\.\s*(\w+)',
        'sbook_no': r'S/book No\.\s*(\w+)',
        'schengen_visa': r'Schengen visa\s*([^\n]+)',
        'korean_keta_visa': r'Korean K-ETA Visa\s*([^\n]+)',
        'position_applied': r'Position Applied:\s*([^\n]+)',
        'date_available': r'Date Available:\s*([^\n]+)',
        'name': r'Name\s*:\s*([^\n]+)',
        'nationality': r'Nationality:\s*([^\n]+)',
        'date_place_of_birth': r'Date /Place of birth:\s*([^\n]+)',
        'home_address': r'Currently Home address:\s*([^\n]+)',
        'phone_email': r'Phone/email\s*([^\n]+)',
        'nearest_airport': r'Nearest  international airport:\s*([^\n]+)',
    }
    
    for field_name, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            fields[field_name] = match.group(1).strip()

    licence_particulars_headers = ["STCW Code", "Cert No", "Place of Issue", "Date of Issue", "Expiry date"]
    certificates_headers = ["Cert No", "Date of Issue", "Expiry date"]
    sea_service_headers = ["Name of Vessel", "Flag", "DWT Type of Vessel", "Rank", "Date of Sign-on", "Date of Sign-off", "Name of Owners"]

    fields['licence_particulars'] = extract_table_data(text, "LICENCE PARTICULARS", "CERTIFICATES", licence_particulars_headers)
    fields['certificates'] = extract_table_data(text, "CERTIFICATES", "SEA SERVICE", certificates_headers)
    fields['sea_service'] = extract_table_data(text, "SEA SERVICE", "References", sea_service_headers)

    return fields

# Streamlit app
st.title("Resume PDF to JSON Converter")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Save uploaded file to disk
    pdf_path = "uploaded_resume.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("PDF uploaded successfully!")

    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(pdf_path)

    # Extract fields from the text
    extracted_fields = extract_fields_from_text(extracted_text)
    
    # Save extracted fields to a JSON file
    json_output_path = "extracted_resume_data.json"
    with open(json_output_path, 'w') as json_file:
        json.dump(extracted_fields, json_file, indent=4)

    st.success("Data extracted and saved to JSON!")

    # Display JSON file content
    st.json(extracted_fields)
    
    # Provide a download link for the JSON file
    with open(json_output_path, "rb") as file:
        btn = st.download_button(
            label="Download JSON",
            data=file,
            file_name="extracted_resume_data.json",
            mime="application/json"
        )
