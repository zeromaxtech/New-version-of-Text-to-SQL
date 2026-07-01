import duckdb
import os
import glob

def get_multi_schema_description(project_dir: str = ".") -> str:
    """Finds all CSV files in the directory and builds a comprehensive relational schema blueprint."""
    csv_files = glob.glob(os.path.join(project_dir, "*.csv"))
    if not csv_files:
        return "No datasets currently uploaded or available."
        
    schema_blueprint = "=== COMPREHENSIVE DATABASE SCHEMA ===\n\n"
    
    for file_path in csv_files:
        # Extract filename without extension to act as the relational Table Name
        table_name = os.path.splitext(os.path.basename(file_path))[0].lower().replace(" ", "_").replace("-", "_")
        try:
            schema_df = duckdb.sql(f"DESCRIBE SELECT * FROM '{file_path}'").df()
            schema_blueprint += f"Table: {table_name}\nColumns:\n"
            for _, row in schema_df.iterrows():
                schema_blueprint += f"  - {row['column_name']} ({row['column_type']})\n"
            schema_blueprint += "\n"
        except Exception as e:
            continue
            
    return schema_blueprint

def build_complex_agent_prompt(question: str, schema_blueprint: str) -> str:
    """Constructs the prompt engineering layout forcing Qwen to write multi-table joins safely."""
    return f"""You are an elite Autonomous Database Architect and SQL Expert tailored for DuckDB.
Your environment contains multiple relational tables mapped from user-uploaded CSV files.

Review the complete database schema architecture below. Analyze how keys can join across tables, 
then write a single, clean, read-only SQL SELECT query to answer the user's complex multi-step request.

[SECURITY PROTOCOL]
- You are strictly restricted to read-only queries (SELECT).
- Do NOT generate commands like DROP, ALTER, DELETE, UPDATE, or INSERT. 
- If the user asks for a destructive or modification operation, respond with the text: "SECURITY_BLOCK: Unauthorized modification command requested."

Available Schema Layout:
{schema_blueprint}

User Request: {question}
SQL Query:"""

def clean_sql_output(raw_text: str) -> str:
    """Strips markdown and wraps syntax properly."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not (l.strip().startswith("```") or l.strip().lower() == "sql")]
        text = "\n".join(lines).strip()
    if text.endswith(";"):
        text = text[:-1].strip()
    return text    

def run_complex_text_to_sql(question: str, project_dir: str, call_llm_fn):
    """Orchestrates schema compilation, cloud agent generation, safety auditing, and final data execution."""
    # 1. Compile the combined layout of all files
    schema_blueprint = get_multi_schema_description(project_dir)
    prompt = build_complex_agent_prompt(question, schema_blueprint)

    # 2. Call the Qwen Cloud API
    raw_sql = call_llm_fn(prompt)
    
    # Security Firewall Check
    if "SECURITY_BLOCK" in raw_sql:
        return "Unauthorized Command", None, "Security Violation: Destructive operations are completely blocked."
        
    sql = clean_sql_output(raw_sql)

    # 3. Dynamically register every local CSV file as an interactable view inside DuckDB
    csv_files = glob.glob(os.path.join(project_dir, "*.csv"))
    for file_path in csv_files:
        table_name = os.path.splitext(os.path.basename(file_path))[0].lower().replace(" ", "_").replace("-", "_")
        duckdb.sql(f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM '{file_path}'")
    
    # 4. Execute the calculated multi-table query
    try:
        result_df = duckdb.sql(sql).df()
        error_message = None
    except Exception as e:
        result_df = None
        error_message = str(e)

    return sql, result_df, error_message