import streamlit as st
import pandas as pd
import re
import requests

st.title("Radiology Records")

# Load the data
data = pd.read_csv('radiology_test_final.csv')

# User input for Subject ID
subject_id_input = st.session_state.get("subject_id", "")

data['subject_id'] = data['subject_id'].astype(str)
data['hadm_id'] = data['hadm_id'].astype(str)

patterns = {
    "Examination": r"EXAMINATION:\s*(.+?)\n",
    "Indication": r"INDICATION:\s*(.+?)\n",
    "Technique": r"TECHNIQUE:\s*(.+?)\n",
    "Comparison": r"COMPARISON:\s*(.+?)\n",
    "Findings": r"FINDINGS:\s*(.+?)\nIMPRESSION:",
    "Impression": r"IMPRESSION:\s*(.+)"
}

# Initialize columns for each key in patterns
for key in patterns:
    data[key] = None

# Iterate over each row in the DataFrame
for index, row in data.iterrows():
    text_entry = row['text']
    for key, pattern in patterns.items():
        match = re.search(pattern, text_entry, re.DOTALL)
        if match:
            data.at[index, key] = match.group(1).strip()


def clean_text(x):
    if x == None: return x
    
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
    x = re.sub(r"([^A-Za-z0-9\s](\s)){2,}", "", x)##remove consecutive punctuations
    x = re.sub(r'', '\n', x)
    x = re.sub(r'\n{2,}', '\n\n', x)
    x = re.sub(r'\n([A-Za-z])', r' \1', x)
    return(x.replace("  ", " "))
    

            

def generate_summary(data):
    
    clean_Impression = [clean_text(instruction) for instruction in data["Impression"]]

    
    for cleaned_text in clean_Impression:
        my_request = "Summary this: " + cleaned_text
        
    API_TOKEN = "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"
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    # Assume formatted_requests is a list of strings each prefixed with "Summary this: "
    formatted_requests = ["Summary this: " + text for text in clean_Impression]

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
            st.write('Patient Radiology Records Information:')
            if table_view_option == 'Full View':
                st.table(filtered_data)  # Full view with interactive sorting but fixed dimensions
            else:
                st.dataframe(filtered_data, width=700, height=300)  # Customizable size view
                
            # Button to generate summary
            if st.button("Generate Summary"):
                summaries = generate_summary(filtered_data)
                # Convert summary results to DataFrame for better display
                column_names = ['Radiology Summary']
                summaries_with_names = pd.DataFrame(summaries, columns=column_names)
                st.table(summaries_with_names)
                
                
                
                overall_output = " ".join([item for sublist in summaries for item in sublist])
                my_request = "Summary this multiple radiologies for 1 patient: " + overall_output
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
                st.markdown("<h3 style='text-align: center; color: gray;'>Overall Radiology Summary</h3>", unsafe_allow_html=True)
                st.write(summary_text)
                
            else:
                        st.write("No data found for the given Subject ID.")
    else:
        st.error(f"The column '{column_name}' does not exist in the data.")
