import streamlit as st
import pandas as pd
import ollama
from pipeline import run_text_to_sql


st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #2C2C2C;
}
[data-testid="stHeading"] h1 {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

st.title("Offline Text-to-SQL")


uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    st.write("File Uploaded :", uploaded_file.name)
    csv_path ="uploaded_data.csv"
    with open(csv_path,"wb")as f:
        f.write(uploaded_file.getbuffer())
    preview_df = pd.read_csv(csv_path)
    st.subheader("Preview")
    st.dataframe(preview_df.head(10))
    table_name = "data_table"
    question = st.text_input("Ask a question about this data")
    if st.button("Run") and question:
        def call_llm(prompt: str)-> str:
            reponse  = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages =[{"role":"user","content":prompt}],
            )
            return reponse["message"]["content"]
        sql,result_df = run_text_to_sql(question,csv_path,table_name,call_llm)
        st.subheader("Generated SQL")
        st.code(sql,language ="sql")
        st.subheader("Result")
        st.dataframe(result_df)
