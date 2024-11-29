import pandas as pd
from sqlalchemy import create_engine, types
import os

# Database connection parameters
username = 'asad'  
password = 'asad'  
host = 'localhost'
database = 'player_stats'  

# File paths
input_file = '/Users/asad/Desktop/dataScraping/scripts/processed_stats.csv'



# Read the CSV
df = pd.read_csv(input_file)

# Create SQLAlchemy engine
engine = create_engine(f'postgresql://{username}:{password}@{host}/{database}')

# Infer column types and adjust as needed
dtype_mapping = {}
for col in df.columns:
    if df[col].dtype == 'object':
        # For string columns, set a reasonable max length
        max_length = df[col].str.len().max() or 255
        dtype_mapping[col] = types.VARCHAR(max_length)
    elif 'float' in str(df[col].dtype):
        dtype_mapping[col] = types.FLOAT
    elif 'int' in str(df[col].dtype):
        dtype_mapping[col] = types.INTEGER

# Write dataframe to PostgreSQL
df.to_sql('stats_table', engine, if_exists='replace', index=False, dtype=dtype_mapping)

print("CSV successfully imported to PostgreSQL")