import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    database_url = st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")
except:
    database_url = os.getenv("DATABASE_URL")

if not database_url:
    from urllib.parse import quote_plus
    password = quote_plus(os.getenv('DB_PASSWORD', ''))
    database_url = f"mysql+pymysql://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
else:
    database_url = database_url.replace("mysql://", "mysql+pymysql://")

engine = create_engine(database_url)

def run_query(sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()
        return columns, [list(row) for row in rows]