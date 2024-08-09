import streamlit as st
import fitz
import easyocr
import tempfile
import shutil
from PIL import Image
import openai
import json

# Initialize OpenAI API key
openai.api_key = "sk-proj-g7MtvmSyg2Ei65NI7cDpT3BlbkFJRJAz3rVT8G7CVec2Ne8r"

def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pdf_invoice = ''
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text()
        pdf_invoice += text.replace("\n", " ")
    return pdf_invoice



def extract_text_from_image(uploaded_file):

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
        
    reader = easyocr.Reader(['en']) 
    results = reader.readtext(temp_file_path)    
    os.remove(temp_file_path)
    text = ''
    for result in results:
        text += result[1] + '\n'
    return text

def analyze_invoice(content):
    user_message = '''
    Act as a text agent and intelligent document parsing system designed to extract information from documents.
    You need to analyse the invoice/bills and provide necessary fields that are required for invoice
    creation. The output needs to be in the below json format.
    If price and total price fields have currency codes like ₹ (INR), $ (USD), do not consider these codes.
    You also need to extract all necessary details from the invoice and include them in the output json.
    {
        "Supplier_details": {
                "Supplier_name": "Name of Supplier",
                "Supplier address": "Address of supplier",
                "invoice date":"09-10-2023",
                "GSTIN": ""
            } ,
        "Customer_details": {
                "Customer_name": "Name of Customer",
                "Customer address": "Address of customer",
                "invoice date":"09-10-2023",
            } ,
        "Data": {
            "Total":"$100",
            "LineItems":[
                {
                    "Id":"name and description of item",
                    "Price":10,
                    "Totalprice":"10",
                    "Quantity":5
                },
                {
                    "Id":"name and description of item" ,
                    "Price":10,
                    "Totalprice":"10",
                    "Quantity":5
                }
            ]
        }
    }
    ''' + content

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": user_message}
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.3,
    )
    return json.loads(response['choices'][0]['message']['content'])

def main():
    st.title("Invoice Analyzer")
    st.write("Upload an invoice in PDF or Image format for analysis.")

    uploaded_file = st.file_uploader("Choose a PDF or Image file", type=['pdf', 'png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            st.write("Extracting text from PDF...")
            invoice_text = extract_text_from_pdf(uploaded_file)
        else:
            st.write("Extracting text from Image...")
            invoice_text = extract_text_from_image(uploaded_file)

        st.write("Analyzing the invoice...")
        response = analyze_invoice(invoice_text)
        st.write("Analysis Result:")
        st.json(response)

        # Save the response to a JSON file
        with open("output.json", 'w') as json_file:
            json.dump(response, json_file, indent=4)
        st.success("Analysis complete! The result is saved as output.json.")

if __name__ == "__main__":
    main()
