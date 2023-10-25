import os
import pandas as pd
import numpy as np

input_directory = '../data'
output_directory = '../data/ISO/'

os.makedirs(output_directory, exist_ok=True)

csv_files = [f for f in os.listdir(input_directory) if f.endswith('.csv')]

for csv_file in csv_files:
    print(csv_file)
    if 'Units' in csv_file: continue
    input_csv = os.path.join(input_directory, csv_file)
    output_csv = os.path.join(output_directory, csv_file)

    df = pd.read_csv(input_csv)

    # Convert the "timestamp" column to ISO 8601 format
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', origin='unix')
    if 'Device' in csv_file:         
        df['calibration'] = df['calibration'].apply(lambda x: bool(int(x)) if not np.isnan(x) else None)
    df.to_csv(output_csv, index=False)

    print(f'Converted data saved to {output_csv}')
