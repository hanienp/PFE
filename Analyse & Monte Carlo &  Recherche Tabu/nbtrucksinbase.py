import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'EnteryExit.csv'  # Replace with your CSV file path
data = pd.read_csv(file_path)

# Ensure the time columns are in HH:MM:SS format by adding :00 for seconds
data['EntryTime'] = data['EntryTime'].apply(lambda x: x if len(x.split(':')) == 3 else x + ':00')
data['ExitTime'] = data['ExitTime'].apply(lambda x: x if len(x.split(':')) == 3 else x + ':00')

# Convert the 'Date' and 'Time' columns to datetime objects, specifying the correct date format (day first)
data['EntryDatetime'] = pd.to_datetime(data['Date'] + ' ' + data['EntryTime'], dayfirst=True)
data['ExitDatetime'] = pd.to_datetime(data['Date'] + ' ' + data['ExitTime'], dayfirst=True)

# Combine entry and exit times into a single DataFrame for processing
entry_data = data[['EntryDatetime']].rename(columns={'EntryDatetime': 'Datetime'})
entry_data['Event'] = 'Entry'

exit_data = data[['ExitDatetime']].rename(columns={'ExitDatetime': 'Datetime'})
exit_data['Event'] = 'Exit'

combined_data = pd.concat([entry_data, exit_data]).sort_values('Datetime').reset_index(drop=True)

# Initialize a DataFrame to keep track of truck count at each hour
unique_dates = sorted(combined_data['Datetime'].dt.date.unique())
truck_count = pd.DataFrame(index=range(24), columns=unique_dates)
truck_count = truck_count.fillna(0)

# Calculate the cumulative number of trucks in the base for each hour of each day
for date in unique_dates:
    daily_data = combined_data[combined_data['Datetime'].dt.date == date]
    for hour in range(24):
        hourly_data = daily_data[daily_data['Datetime'].dt.hour == hour]
        prevhourly_data = daily_data[daily_data['Datetime'].dt.hour == (hour-1)]
        hourly_entries = hourly_data[hourly_data['Event'] == 'Entry'].shape[0]
        hourly_exits = prevhourly_data[prevhourly_data['Event'] == 'Exit'].shape[0]
        
        if hour == 0:
            previous_count = 0
        else:
            previous_count = truck_count.at[hour-1, date]
        
        truck_count.at[hour, date] = previous_count + hourly_entries - hourly_exits
        

# Plot the truck count for each day
n_rows = 3
n_cols = 3

def create_figure(dates_subset, figure_number):
    # Create a figure with subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 12))
    axes = axes.flatten()  # Flatten the 2D array of axes to iterate easily

    # Plot the truck count for each day
    for i, date in enumerate(dates_subset):
        if i < len(axes):
            ax = axes[i]
            truck_count[date].plot(kind='line', ax=ax)
            ax.set_title(f'Date: {date}', fontsize=8)
            ax.set_xlabel('Hour of the Day', fontsize=6)
            ax.set_ylabel('Number of Trucks in Base', fontsize=6)
            ax.set_xticks(range(24))
            ax.set_xticklabels(range(24), fontsize=6)
            ax.set_yticklabels(ax.get_yticks(), fontsize=6)

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.suptitle(f'Figure {figure_number}: Number of Trucks in Base for Days {dates_subset[0]} to {dates_subset[-1]}', y=1.02)
    plt.show()

# Create the first figure for the first 9 days
create_figure(unique_dates[:9], 1)

# Create the second figure for the next 9 days
create_figure(unique_dates[9:18], 2)
