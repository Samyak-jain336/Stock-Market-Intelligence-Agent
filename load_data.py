import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

password = quote_plus(os.getenv('DB_PASSWORD'))

engine = create_engine(
    f"mysql+pymysql://root:{password}@localhost/nifty_db"
)

csv_folder = r"C:\\Users\\samya\\OneDrive\\Documents\\GitHub\\Stock Market Intelligence Agent\\Nifty 50 (2007 - 2021)"

for file in os.listdir(csv_folder):
    if file.endswith(".csv"):
        filepath = os.path.join(csv_folder, file)
        df = pd.read_csv(filepath)
        df.columns = [
            "date", "symbol", "series", "prev_close", "open",
            "high", "low", "last", "close", "vwap",
            "volume", "turnover", "trades",
            "deliverable_volume", "pct_deliverable"
        ]
        df["date"] = pd.to_datetime(df["date"], format='mixed', dayfirst=True)
        df.to_sql("stock_prices", engine, if_exists="append", index=False)
        print(f"Loaded: {file}")

print("All files loaded.")


sector_data = [
    ("ADANIPORTS", "Adani Ports", "Infrastructure"),
    ("ASIANPAINT", "Asian Paints", "Consumer Goods"),
    ("AXISBANK", "Axis Bank", "Banking"),
    ("BAJAJ-AUTO", "Bajaj Auto", "Automobile"),
    ("BAJAJFINSV", "Bajaj Finserv", "Financial Services"),
    ("BAJFINANCE", "Bajaj Finance", "Financial Services"),
    ("BHARTIARTL", "Bharti Airtel", "Telecom"),
    ("BPCL", "BPCL", "Oil & Gas"),
    ("BRITANNIA", "Britannia", "FMCG"),
    ("CIPLA", "Cipla", "Pharma"),
    ("COALINDIA", "Coal India", "Energy"),
    ("DRREDDY", "Dr Reddys", "Pharma"),
    ("EICHERMOT", "Eicher Motors", "Automobile"),
    ("GAIL", "GAIL", "Oil & Gas"),
    ("GRASIM", "Grasim", "Cement"),
    ("HCLTECH", "HCL Tech", "IT"),
    ("HDFC", "HDFC", "Financial Services"),
    ("HDFCBANK", "HDFC Bank", "Banking"),
    ("HEROMOTOCO", "Hero MotoCorp", "Automobile"),
    ("HINDALCO", "Hindalco", "Metals"),
    ("HINDUNILVR", "HUL", "FMCG"),
    ("ICICIBANK", "ICICI Bank", "Banking"),
    ("INDUSINDBK", "IndusInd Bank", "Banking"),
    ("INFRATEL", "Infratel", "Telecom"),
    ("INFY", "Infosys", "IT"),
    ("IOC", "Indian Oil", "Oil & Gas"),
    ("ITC", "ITC", "FMCG"),
    ("JSWSTEEL", "JSW Steel", "Metals"),
    ("KOTAKBANK", "Kotak Bank", "Banking"),
    ("LT", "L&T", "Infrastructure"),
    ("MARUTI", "Maruti Suzuki", "Automobile"),
    ("MM", "M&M", "Automobile"),
    ("NESTLEIND", "Nestle India", "FMCG"),
    ("NTPC", "NTPC", "Energy"),
    ("ONGC", "ONGC", "Oil & Gas"),
    ("POWERGRID", "Power Grid", "Energy"),
    ("RELIANCE", "Reliance", "Oil & Gas"),
    ("SBIN", "SBI", "Banking"),
    ("SHREECEM", "Shree Cement", "Cement"),
    ("SUNPHARMA", "Sun Pharma", "Pharma"),
    ("TATAMOTORS", "Tata Motors", "Automobile"),
    ("TATASTEEL", "Tata Steel", "Metals"),
    ("TCS", "TCS", "IT"),
    ("TECHM", "Tech Mahindra", "IT"),
    ("TITAN", "Titan", "Consumer Goods"),
    ("ULTRACEMCO", "UltraTech Cement", "Cement"),
    ("UPL", "UPL", "Chemicals"),
    ("VEDL", "Vedanta", "Metals"),
    ("WIPRO", "Wipro", "IT"),
    ("ZEEL", "Zee Entertainment", "Media"),
]

df_sectors = pd.DataFrame(sector_data, columns=["symbol", "company_name", "sector"])
df_sectors.to_sql("company_info", engine, if_exists="append", index=False)
print("Sector data loaded.")