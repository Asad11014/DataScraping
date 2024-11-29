import pandas as pd
import numpy as np

# File paths
input_file = '/Users/asad/Desktop/dataScraping/scripts/stats.csv'  # Input CSV file path
output_file = '/Users/asad/Desktop/dataScraping/scripts/processed_stats.csv'  # Output processed CSV file path

# Load the CSV file, considering the first two rows as headers
data = pd.read_csv(input_file, header=[0, 1])

# Function to get meaningful header
def get_meaningful_header(header_tuple):
    # First 4 columns or empty/Unnamed get special treatment
    if header_tuple[0] in ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3'] or pd.isna(header_tuple[0]):
        # If second row has a value, use that
        if pd.notna(header_tuple[1]) and str(header_tuple[1]).strip() and 'Unnamed' not in str(header_tuple[1]):
            return str(header_tuple[1])
    
    # If first row has a value and second row is empty, use first row
    if pd.notna(header_tuple[0]) and str(header_tuple[0]).strip() and 'Unnamed' not in str(header_tuple[0]):
        # If second row is empty or Unnamed, just use first row
        if pd.isna(header_tuple[1]) or 'Unnamed' in str(header_tuple[1]):
            return str(header_tuple[0])
        
        # If both have values, combine them
        if pd.notna(header_tuple[1]) and str(header_tuple[1]).strip():
            return f"{header_tuple[0]}_{header_tuple[1]}".strip().replace(" ", "_").lower()
    
    # Fallback to second row if it has a value
    if pd.notna(header_tuple[1]) and str(header_tuple[1]).strip() and 'Unnamed' not in str(header_tuple[1]):
        return str(header_tuple[1])
    
    return ''

# Create new flattened headers
new_headers = [
    get_meaningful_header(col).strip().replace(" ", "_").lower()
    for col in data.columns
]

# Rename columns
data.columns = new_headers

# Save the processed CSV file
data.to_csv(output_file, index=False)

print(f"Processed CSV saved to {output_file}")