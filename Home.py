import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="Patient Medical Records",
    page_icon="home",
)

st.title("Patient Medical Records")

# Load the data
data = pd.read_csv('discharge_test_final.csv')

if "subject_id_input" not in st.session_state:
    st.session_state["subject_id"] =""


# User input for Subject ID
subject_id_input = st.text_input("Enter Subject ID:", st.session_state["subject_id"])
submit = st.button("Submit")
if submit:
    st.session_state["subject_id"] = subject_id_input
    st.write("You have selected the Subject ID: ", subject_id_input)

        






