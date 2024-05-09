import streamlit as st
import pandas as pd
import re
import requests

st.title("Discharge Records")

# Load the data
data = pd.read_csv('discharge_test_final.csv')

# User input for Subject ID
subject_id_input = st.session_state.get("subject_id", "")

data['subject_id'] = data['subject_id'].astype(str)
data['hadm_id'] = data['hadm_id'].astype(str)

patterns = {
    "Chief Complaint": r"Chief Complaint:\s*(.+?)(?=Major Surgical|History of Present Illness|$)",
    "Major Surgical or Invasive Procedure": r"Major Surgical or Invasive Procedure:\s*(.+?)(?=History of Present Illness|$)",
    "Discharge Diagnosis": r"Discharge Diagnosis:\s*(.+?)(?=Discharge Condition|$)",
    "Discharge Medications": r"Discharge Medications:\s*(.+?)(?=Discharge Diagnosis|$)",
    "Discharge Condition": r"Discharge Condition:\s*(.+?)(?=Discharge Instructions|$)",
    "Discharge Instructions": r"Discharge Instructions:\s*(.+?)(?=Followup Instructions|$)",
    "Followup Instructions": r"Followup Instructions:\s*(.+)$"
}

# Initialize columns for each key in patterns
for key in patterns:
    data[key] = None

# Extracting information based on patterns
for index, row in data.iterrows():
    text_entry = row['text']
    for key, pattern in patterns.items():
        match = re.search(pattern, text_entry, re.DOTALL)
        if match:
            data.at[index, key] = match.group(1).strip()


def clean_text(x):
    if len(x) < 50:
        return x
    x = " ".join(x.split())
    x= " ".join((" ".join(x.split("[**"))).split("**]"))
    x = re.sub(r"\([^()]*\)", "", x)
    key_value_strip =(x.split(":"))
    ##remove all sub strings which have a length lesser than 50 characters
    string = " ".join([sub_unit for sub_unit in key_value_strip if len(sub_unit)>50])
    x = re.sub(r"(\d+)+(\.|\))", "", string)## remove all serialization eg 1. 1)
    x = re.sub(r"(\*|\?|=)+", "", x) ##removing all *, ? and =
    x = re.sub(r"\b(\w+)( \1\b)+", r"\1", x) ## removing consecutive dupicate words
    x = x.replace("FOLLOW UP", "FOLLOWUP")
    x = x.replace("FOLLOW-UP", "FOLLOWUP")
    x = re.sub(r"(\b)(f|F)(irst)(\b)?[\d\-\d]*(\s)*(\b)?(n|N)(ame)[\d\-\d]*(\s)*[\d\-\d]*(\b)","",x)##remove firstname
    x = re.sub(r"(\b)(l|L)(ast)(\b)?[\d\-\d]*(\s)*(\b)?(n|N)(ame)[\d\-\d]*(\s)*[\d\-\d]*(\b)", "", x)
    x = re.sub(r"(\b)(d|D)\.?(r|R)\.?(\b)", "", x) #remove Dr abreviation
    x = re.sub(r"([^A-Za-z0-9\s](\s)){2,}", "", x)##remove consecutive punctuations
    x = re.sub(r'', '\n', x)
    x = re.sub(r'\n{2,}', '\n\n', x)
    x = re.sub(r'\n([A-Za-z])', r' \1', x)
    return(x.replace("  ", " "))
            

def generate_summary(data):
    cleaned_instructions = [clean_text(instruction) for instruction in data["Discharge Instructions"]]
    updated_instructions = []


    for instruction in cleaned_instructions:
        # Replace placeholder with name
        cleaned_text = re.sub(r"(\bMs\.\s)_{2,}", r"\1[Name]", instruction)

        # Standardizing medical terms (e.g., Lasix to lasix)
        cleaned_text = re.sub(r"\bLasix\b", "lasix", cleaned_text, flags=re.IGNORECASE)

        # Cleans ". ___"
        cleaned_text = re.sub(r"\.\s_{2,}", ". [Clinic Name]", cleaned_text)

        # Cleans " ___ "
        cleaned_text = re.sub(r"\s_{2,}\s", " [Information]", cleaned_text)

        # Standardizing units (e.g., liters)
        cleaned_text = re.sub(r"\b(\d+)L\b", r"\1 liters", cleaned_text)

        # Append the processed text to the list
        updated_instructions.append(cleaned_text)
    
    # Assuming updated_instructions is a list of cleaned text strings
    for cleaned_text in updated_instructions:
        my_request = "Summary this: " + cleaned_text
        
    API_TOKEN = "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"
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    # Assume formatted_requests is a list of strings each prefixed with "Summary this: "
    formatted_requests = ["Summary this discharge of 1 patient: " + text for text in updated_instructions]

    # To handle multiple requests
    responses = []
    for my_request in formatted_requests:
        output = query({
            "inputs": my_request
        })
        extracted_texts = [item['summary_text'] for item in output]
        responses.append(extracted_texts)
    return responses


# Toggle between table views
table_view_option = st.radio("Table View Options", ['Full View', 'Custom Size View'])

# Query and display the data
if subject_id_input:
    column_name = 'subject_id'
    if column_name in data.columns:
        filtered_data = data[data[column_name] == subject_id_input]
        if not filtered_data.empty:
            st.write('Patient Discharge Records Information:')
            if table_view_option == 'Full View':
                st.table(filtered_data)  # Full view with interactive sorting but fixed dimensions
            else:
                st.dataframe(filtered_data, width=700, height=300)  # Customizable size view
                
            # Button to generate summary
            if st.button("Generate Summary"):
                summaries = generate_summary(filtered_data)
                # Convert summary results to DataFrame for better display
                column_names = ['Discharge Summary']
                summaries_with_names = pd.DataFrame(summaries, columns=column_names)
                st.table(summaries_with_names)
                
                overall_output = " ".join([item for sublist in summaries for item in sublist])
                my_request = "Summary this multiple discharges for 1 patient: " + overall_output
                import requests
                API_TOKEN = "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"
                API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
                headers = {"Authorization": f"Bearer {API_TOKEN}"}

                def query(payload):
                    response = requests.post(API_URL, headers=headers, json=payload)
                    return response.json()
                    
                output = query({
                    "inputs": my_request
                })

                summary_text = output[0]['summary_text']
                st.markdown("<h3 style='text-align: center; color: gray;'>Overall Discharge Summary</h3>", unsafe_allow_html=True)
                st.write(summary_text)
                
                
            else:
                        st.write("No data found for the given Subject ID.")
    else:
        st.error(f"The column '{column_name}' does not exist in the data.")

