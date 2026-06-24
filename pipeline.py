import duckdb



def get_schema_description(csv_path: str) -> str:
    schema_df = duckdb.sql(f"DESCRIBE SELECT * FROM '{csv_path}'").df()
    lines = []
    for _, row in schema_df.iterrows():
        lines.append(f"- {row['column_name']} ({row['column_type']})")
    return "\n".join(lines)

def build_prompt(question: str,table_name: str,schema_description : str)->str:
      return f"""you are a SQL generator. You will be given a table name,its columns,and
and a question in plain english. respond with only a single valid SQL query that answer the question.
Don't include any explanation,markdown formating, or code fences - just the raw sql query text.

Table name:{table_name}
Columns:
{schema_description}

Question{question}

SQL query :"""


def clean_sql_output(raw_text: str)->str:
    text= raw_text.strip()
    if text.startswith("```"):
        lines =text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text    

def run_text_to_sql(question:str,csv_path:str,table_name: str, call_llm_fn):
      schema_description = get_schema_description(csv_path)
      prompt = build_prompt(question, table_name,schema_description)

      raw_sql= call_llm_fn(prompt)
      sql = clean_sql_output(raw_sql)

      duckdb.sql(f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM'{csv_path}'")
      result_df= duckdb.sql(sql).df()

      return sql,result_df

   

print(get_schema_description("sample_data.csv"))