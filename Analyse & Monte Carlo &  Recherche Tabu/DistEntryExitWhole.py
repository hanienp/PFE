import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'EnteryExit.csv'  # Replace with your CSV file path
data = pd.read_csv(file_path)

# Ensure the time column is in HH:MM:SS format by adding :00 for seconds
data['Time'] = data['Time'].apply(lambda x: x if len(x.split(':')) == 3 else x + ':00')

# Convert the 'Date' and 'Time' columns to datetime objects, specifying the correct date format (day first)
data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], dayfirst=True)

# Extract hour from the datetime
data['Hour'] = data['Datetime'].dt.hour

# Count the number of trucks per hour
truck_distribution = data['Hour'].value_counts().sort_index()

# Plot the distribution
plt.figure(figsize=(10, 6))
truck_distribution.plot(kind='bar')
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Trucks')
plt.title('Distribution of Trucks Throughout the Day')
plt.xticks(range(0, 24))
plt.grid(True)
plt.show()
