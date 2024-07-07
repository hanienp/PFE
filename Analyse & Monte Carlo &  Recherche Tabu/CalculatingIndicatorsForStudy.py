import pandas as pd
from datetime import timedelta
import numpy as np

def calculate_time_statistics(csv_file):
    # Read the CSV file
    df = pd.read_csv(csv_file, header=None, names=["Time"])

    # Function to convert time string to timedelta
    def to_timedelta(time_str):
        if isinstance(time_str, str):
            h, m, s = map(int, time_str.split(':'))
            return timedelta(hours=h, minutes=m, seconds=s)
        else:
            return None

    # Convert times to timedelta
    df["Timedelta"] = df["Time"].apply(to_timedelta)

    # Drop rows with None values in Timedelta column
    df.dropna(subset=["Timedelta"], inplace=True)

    # Convert timedeltas to total minutes
    df["TotalMinutes"] = df["Timedelta"].dt.total_seconds() / 60

    # Calculate statistics
    average_minutes = np.mean(df["TotalMinutes"])
    median_minutes = np.median(df["TotalMinutes"])
    std_dev_minutes = np.std(df["TotalMinutes"])

    return average_minutes, median_minutes, std_dev_minutes

# Example usage:
csv_file = "TimeAtBaseData.csv"
average, median, std_dev = calculate_time_statistics(csv_file)
print("Average Time (minutes):", average)
print("Median Time (minutes):", median)
print("Standard Deviation (minutes):", std_dev)
