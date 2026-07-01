import streamlit as st
import os
import duckdb
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import json
import time

# Load enterprise configuration
load_dotenv()

st.set_page_config(page_title="DuckBrain SQL Enterprise", layout="wide", initial_sidebar_state="expanded")

# Clean corporate styling
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .status-banner {
        background-color: #1e293b; border-left: 4px solid #38bdf8;
        color: #38bdf8; padding: 12px; border-radius: 4px; font-weight: 500; margin-bottom: 15px;
    }
    .question-wizard {
        background-color: #1e293b; border: 1px solid #38bdf8;
        padding: 20px; border-radius: 8px; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: #ffffff; font-family: sans-serif; font-weight: 700;'>DuckBrain SQL Engine <span style='color:#38bdf8; font-size:1rem; font-weight:400;'>v6.2 Automated Architecture Core</span></h2>", unsafe_allow_html=True)

# 1. State Machine Initialization
if "db_conn" not in st.session_state:
    st.session_state["db_conn"] = duckdb.connect(database=':memory:')
if "active_dataframe" not in st.session_state:
    st.session_state["active_dataframe"] = None
if "wizard_step" not in st.session_state:
    st.session_state["wizard_step"] = "idle"  # idle -> onboarding -> compiled
if "parsed_questions" not in st.session_state:
    st.session_state["parsed_questions"] = None
if "user_prompt" not in st.session_state:
    st.session_state["user_prompt"] = ""
if "target_dialect" not in st.session_state:
    st.session_state["target_dialect"] = "MySQL 8.0 (Workbench Sandbox)"
if "saved_schemas" not in st.session_state:
    st.session_state["saved_schemas"] = {}

# Initialize API Client
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

# Robust API Caller with Exponential Backoff
def call_llm_with_backoff(messages, system_instruction=None):
    backoffs = [1, 2, 4]
    formatted_messages = []
    if system_instruction:
        formatted_messages.append({"role": "system", "content": system_instruction})
    formatted_messages.extend(messages)
    
    for i, delay in enumerate(backoffs):
        try:
            response = client.chat.completions.create(
                model="qwen-plus",
                messages=formatted_messages,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            if i == len(backoffs) - 1:
                raise e
            time.sleep(delay)

def extract_clean_json(raw_text):
    raw_text = raw_text.strip()
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0].strip()
    start_idx = raw_text.find('{')
    end_idx = raw_text.rfind('}')
    if start_idx != -1 and end_idx != -1:
        return raw_text[start_idx:end_idx+1]
    return raw_text

# --- SIDEBAR WORKSPACE MATCHING YOUR LAYOUT ---
with st.sidebar:
    st.markdown("<h3 style='color: #ffffff; margin-bottom: 5px; font-size:1.1rem;'>Target Workspace</h3>", unsafe_allow_html=True)
    st.session_state["target_dialect"] = st.selectbox(
        "Target SQL Engine Dialect:", 
        options=["MySQL 8.0 (Workbench Sandbox)", "DuckDB (In-Memory Execution)"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("<h3 style='color: #ffffff; margin-bottom: 5px; font-size:1.1rem;'>Data Catalog</h3>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload CSV datasets", type=["csv"], accept_multiple_files=True, label_visibility="collapsed")

# Parse and lock schemas into memory persistently
if uploaded_files:
    for file in uploaded_files:
        table_name = file.name.lower().replace(".csv", "").replace(" ", "_").replace("-", "_")
        if table_name not in st.session_state["saved_schemas"]:
            try:
                df = st.session_state["db_conn"].execute(
                    f"SELECT * FROM read_csv('{file.name}', all_varchar=True, ignore_errors=True)"
                ).df()
            except Exception:
                df = pd.read_csv(file, on_bad_lines='skip', keep_default_na=False)
                
            st.session_state["db_conn"].register(table_name, df)
            st.session_state["saved_schemas"][table_name] = ", ".join([f"{col}" for col in df.columns])

# Display locked schemas on sidebar layout
if st.session_state["saved_schemas"]:
    st.sidebar.markdown("<p style='color: #94a3b8; font-size:0.8rem; font-weight:600; margin-top:15px; margin-bottom:5px;'>REGISTERED SCHEMAS</p>", unsafe_allow_html=True)
    for name, fields in st.session_state["saved_schemas"].items():
        st.sidebar.code(f"Table: {name}\nFields: {fields}", language="text")

# --- MAIN CONTROLLER LINE ---
if not st.session_state["saved_schemas"]:
    st.info("System Ready. Please upload your company CSV files to start the security configuration stream.")
else:
    user_prompt = st.text_area(
        "Analytical Directive / Creation Request:", 
        value=st.session_state["user_prompt"],
        placeholder="e.g., Let's build a new database and setup tracking tables from scratch...",
        disabled=(st.session_state["wizard_step"] != "idle")
    )
    st.session_state["user_prompt"] = user_prompt

    # Restored Action Controls Configuration Matrix Block
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        is_idle_state = (st.session_state["wizard_step"] == "idle")
        process_trigger = st.button("Analyze Requirements & Evaluate Roles", use_container_width=True, disabled=not is_idle_state)
    with col_btn2:
        show_visuals = st.checkbox("Enable Dynamic Charting Tools", value=False)

    # Phase 1: Run Analysis
    if is_idle_state and process_trigger:
        if st.session_state["user_prompt"].strip():
            schema_context = "\n".join([f"- Table `{name}` fields: {fields}" for name, fields in st.session_state["saved_schemas"].items()])
            
            wizard_generation_prompt = f"""
            You are a senior database security architect inspecting these schemas:
            {schema_context}
            The user wants to process this request: "{st.session_state["user_prompt"]}"
            
            Generate exactly 2 practical access governance choices required before writing the code.
            You MUST return your response as a valid JSON object matching this structure exactly, with NO other text:
            {{
              "q1_title": "Short title for question 1",
              "q1_options": ["Option A text", "Option B text"],
              "q2_title": "Short title for question 2",
              "q2_options": ["Option A text", "Option B text"]
            }}
            """
            with st.spinner("Analyzing data relationships for roles and security boundaries..."):
                try:
                    ai_res = call_llm_with_backoff([{"role": "user", "content": wizard_generation_prompt}])
                    clean_json_str = extract_clean_json(ai_res)
                    st.session_state["parsed_questions"] = json.loads(clean_json_str)
                    st.session_state["wizard_step"] = "onboarding"
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate wizard questions safely: Connection error.")
        else:
            st.warning("Please enter an analytical request directive before proceeding.")

    # Phase 2: User Access Mapping Interaction Wizard
    if st.session_state["wizard_step"] == "onboarding" and st.session_state["parsed_questions"]:
        questions = st.session_state["parsed_questions"]
        
        st.markdown("<div class='question-wizard'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #38bdf8; margin-top:0;'>🛡️ Database Security & Role Configuration Wizard</h4>", unsafe_allow_html=True)
        
        ans1 = st.radio(f"1. {questions.get('q1_title')}", options=questions.get('q1_options'))
        st.markdown("<br>", unsafe_allow_html=True)
        ans2 = st.radio(f"2. {questions.get('q2_title')}", options=questions.get('q2_options'))
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("Reset / Edit Prompt", use_container_width=True):
                st.session_state["wizard_step"] = "idle"
                st.rerun()
        with col_nav2:
            if st.button("Apply Security Policies & Generate Query", use_container_width=True):
                st.session_state["user_choices_context"] = f"Question 1 selection: {ans1}. Question 2 selection: {ans2}."
                st.session_state["wizard_step"] = "compiled"
                st.rerun()

    # Phase 3: Final Safe Execution and Graph Render Matrix
    if st.session_state["wizard_step"] == "compiled":
        schema_context = "\n".join([f"- Table `{name}` fields: {fields}" for name, fields in st.session_state["saved_schemas"].items()])
        dialect_rules = "DuckDB" if "DuckDB" in st.session_state["target_dialect"] else "MySQL 8.0"
        
        system_instructions = f"""
        You are an enterprise data architect writing database scripts optimized for {dialect_rules} syntax.
        Available schemas: {schema_context}
        The user has chosen these explicit data security policies: {st.session_state.get('user_choices_context')}
        
        Generate the requested SQL code matching their original intent. Incorporate their security choices.
        Output ONLY raw SQL enclosed within ```sql ... ``` code blocks. No prose dialog.
        """
        
        with st.spinner("Injecting governance parameters and compiling final query..."):
            try:
                response_content = call_llm_with_backoff(
                    messages=[{"role": "user", "content": st.session_state["user_prompt"]}],
                    system_instruction=system_instructions
                )
                
                generated_sql = response_content
                if "```sql" in generated_sql:
                    generated_sql = generated_sql.split("```sql")[1].split("```")[0].strip()
                elif "```" in generated_sql:
                    generated_sql = generated_sql.split("```")[1].split("```")[0].strip()

                st.markdown("<div class='status-banner'>Secured Compilation Output Matrix</div>", unsafe_allow_html=True)
                st.code(generated_sql, language="sql")
                
                if "DuckDB" in st.session_state["target_dialect"]:
                    if any(kw in generated_sql.lower() for kw in ["drop table", "truncate"]):
                        st.error("Security Exception: Operation blocked.")
                    else:
                        df_results = st.session_state["db_conn"].execute(generated_sql).df()
                        st.success("Query completed successfully inside local memory layout.")
                        st.dataframe(df_results, use_container_width=True)
                        st.session_state["active_dataframe"] = df_results
                else:
                    st.info("Sandbox Generation Complete: Paste the code directly into MySQL Workbench.")
                    st.session_state["active_dataframe"] = None
                
                if st.button("Start New Configuration Session", use_container_width=True):
                    st.session_state["wizard_step"] = "idle"
                    st.session_state["user_prompt"] = ""
                    st.session_state["parsed_questions"] = None
                    st.session_state["saved_schemas"] = {}
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Runtime Exception: {str(e)}")
                if st.button("Return to Config Window"):
                    st.session_state["wizard_step"] = "idle"
                    st.rerun()

    # --- RESTORED DYNAMIC VISUALIZATION MATRIX ---
    if show_visuals and st.session_state["active_dataframe"] is not None:
        res_df = st.session_state["active_dataframe"]
        if not res_df.empty:
            st.markdown("---")
            st.markdown("<h3 style='color: #ffffff; font-size: 1.2rem;'>Interactive Data Visualizations</h3>", unsafe_allow_html=True)
            all_columns = res_df.columns.tolist()
            
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                x_axis = st.selectbox("Select X-Axis Data Column:", options=all_columns, index=0)
            with col_sel2:
                y_axis = st.selectbox("Select Y-Axis Data Column:", options=all_columns, index=min(1, len(all_columns)-1))
            
            clean_chart_df = res_df.dropna(subset=[x_axis, y_axis])
            if not clean_chart_df.empty:
                chart_data = clean_chart_df[[x_axis, y_axis]].set_index(x_axis)
                graph_col1, graph_col2 = st.columns(2)
                with graph_col1:
                    st.bar_chart(chart_data)
                with graph_col2:
                    st.line_chart(chart_data)