import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
file_path = 'EnteryExit.csv'  # Replace with your CSV file path
data = pd.read_csv(file_path)

# Ensure the time column is in HH:MM:SS format by adding :00 for seconds
data['Time'] = data['Time'].apply(lambda x: x if len(x.split(':')) == 3 else x + ':00')

# Convert the 'Date' and 'Time' columns to datetime objects, specifying the correct date format (day first)
data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], dayfirst=True)

# Extract date and hour from the datetime
data['Date'] = data['Datetime'].dt.date
data['Hour'] = data['Datetime'].dt.hour

# Get unique dates and sort them
unique_dates = sorted(data['Date'].unique())

# Determine the number of rows and columns for subplots
n_rows = 3
n_cols = 3

def create_figure(dates_subset, figure_number):
    # Create a figure with subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 12))
    axes = axes.flatten()  # Flatten the 2D array of axes to iterate easily

    # Plot the distribution for each day
    for i, date in enumerate(dates_subset):
        daily_data = data[data['Date'] == date]
        truck_distribution = daily_data['Hour'].value_counts().reindex(range(24), fill_value=0) * 2
        
        ax = axes[i]
        truck_distribution.plot(kind='bar', ax=ax)
        ax.set_title(f'Date: {date}', fontsize=8)
        ax.set_xlabel('Hour of the Day', fontsize=6)
        ax.set_ylabel('Number of Trucks', fontsize=6)
        ax.set_xticks(range(24))
        ax.set_xticklabels(range(24), fontsize=6)
        ax.set_yticklabels(ax.get_yticks(), fontsize=6)

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.suptitle(f'Figure {figure_number}: Truck Distribution for Days {dates_subset[0]} to {dates_subset[-1]}', y=1.02)
    plt.show()

# Create the first figure for the first 9 days
create_figure(unique_dates[:9], 1)

# Create the second figure for the next 9 days
create_figure(unique_dates[9:18], 2)
