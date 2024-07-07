import pandas as pd
import numpy as np

# Load the CSV file into a DataFrame
df = pd.read_csv('PerSegPerTime.csv')

# Combine Date and Entry/Exit to form datetime objects
df['entry_time'] = pd.to_datetime(df['Date'] + ' ' + df['Entry'], format='%d-%b %H:%M')
df['exit_time'] = pd.to_datetime(df['Date'] + ' ' + df['Exit'], format='%d-%b %H:%M')

# Create a dictionary to store the vehicle counts per hour per day
days = df['entry_time'].dt.date.unique()
segments = df['Seg'].unique()

vehicle_counts = {
    'All': {day: {hour: 0 for hour in range(24)} for day in days},
    **{seg: {day: {hour: 0 for hour in range(24)} for day in days} for seg in segments}
}

# Populate the dictionary with vehicle counts
for index, row in df.iterrows():
    entry_time = row['entry_time']
    exit_time = row['exit_time']
    segment = row['Seg']
    
    day = entry_time.date()
    hours_in_range = pd.date_range(start=entry_time.floor('H'), end=exit_time.ceil('H'), freq='H')[:-1]
    
    for hour in hours_in_range:
        hour_of_day = hour.hour
        vehicle_counts['All'][day][hour_of_day] += 1
        vehicle_counts[segment][day][hour_of_day] += 1

# Initialize the summary dictionary (A)
summary = {
    'All': {'Hour': [], 'Average': [], 'Median': [], 'StdDev': []},
    **{seg: {'Hour': [], 'Average': [], 'Median': [], 'StdDev': []} for seg in segments}
}

# Calculate the statistics
for hour in range(24):
    for key in summary.keys():
        hourly_counts = [vehicle_counts[key][day][hour] for day in days]
        summary[key]['Hour'].append(hour)
        summary[key]['Average'].append(np.mean(hourly_counts))
        summary[key]['Median'].append(np.median(hourly_counts))
        summary[key]['StdDev'].append(np.std(hourly_counts))

# Convert summary dictionary to a single DataFrame for easier viewing and exporting
all_data = []

for key in summary.keys():
    df_temp = pd.DataFrame({
        'Hour': summary[key]['Hour'],
        'Segment': key,
        'Average': summary[key]['Average'],
        'Median': summary[key]['Median'],
        'StdDev': summary[key]['StdDev']
    })
    all_data.append(df_temp)

result_df = pd.concat(all_data, ignore_index=True)

# Save the results to a CSV file
result_df.to_csv('ExportedTimePerSegPreHour.csv', index=False)

# Print the results
print("Statistics for each segment and hour of the day:")
print(result_df)

# Convert vehicle_counts to a DataFrame
vehicle_counts_data = []

for segment, days_data in vehicle_counts.items():
    for day, hours_data in days_data.items():
        for hour, count in hours_data.items():
            vehicle_counts_data.append({
                'Segment': segment,
                'Date': day,
                'Hour': hour,
                'Count': count
            })

vehicle_counts_df = pd.DataFrame(vehicle_counts_data)

# Save vehicle counts to a CSV file
vehicle_counts_df.to_csv('NBTruckPerDay.csv', index=False)

# Print vehicle counts
print("Vehicle counts per segment, day, and hour:")
print(vehicle_counts_df)
