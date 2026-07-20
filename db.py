import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

password = quote_plus(os.getenv('DB_PASSWORD'))

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
)

def run_query(sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()
        return columns, [list(row) for row in rows]