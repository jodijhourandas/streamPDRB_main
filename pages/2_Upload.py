import streamlit as st 
from st_aggrid import AgGrid
import pandas as pd



st.title("You're in the home")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    AgGrid(df)

