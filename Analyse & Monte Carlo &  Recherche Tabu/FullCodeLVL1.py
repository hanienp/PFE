import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import lognorm, expon, weibull_min, norm
import datetime

# Define the distributions and their parameters
distributions = {
    "Base maneuvering time": ("lognorm", (0.77, 0.00, 5.76)),
    "load/unloading time": ("expon", (1.00, 10.91)),
    "TOOL WAITING": ("weibull_min", (0.94, 0.00, 28.28)),
    "LOAD SECUREMENT": ("lognorm", (0.71, 0.00, 9.73)),
    "Crane waiting": ("weibull_min", (0.79, 0.00, 91.62)),
    "LiftTruck wait time": ("lognorm", (0.94, 0.00, 14.81)),
    "Administrative papers/authorisations": ("weibull_min", (1.51, 0.00, 20.89)),
    "Service Planification Delays": ("lognorm", (1.03, 0.00, 18.83)),
    "Coordination SEG - DRIVERS": ("lognorm", (0.56, 0.00, 33.21)),
    "other delays": ("weibull_min", (1.82, 0.00, 26.23)),
}

# Function to sample base maneuvering time based on number of trucks
def sample_base_maneuvering_time(num_trucks):
    if num_trucks < 2:
        shape, loc, scale = 0.77, 0.0, 4.253023255813953
    elif 2 <= num_trucks < 4:
        shape, loc, scale = 0.77, 0.0, 5.927441860465116
    elif 4 <= num_trucks < 6:
        shape, loc, scale = 0.77, 0.0, 7.166511627906976
    else:
        shape, loc, scale = 0.77, 0.0, 8.606511627906976
        
    # Convert shape and scale to mean and sigma for the normal distribution
    mean = np.log(scale)
    sigma = shape
    return np.random.lognormal(mean, sigma) 

# Tool waiting data
tool_waiting_data = pd.read_csv("ExportedToolWaitingPerSegPerHour.csv")

def sample_tool_waiting_time(hour, segment):
    segment_data = tool_waiting_data[(tool_waiting_data["Hour"] == hour) & (tool_waiting_data["Segment"] == segment)]
    if not segment_data.empty:
        mean_waiting = segment_data.iloc[0]["Average"]
        std_dev_waiting = segment_data.iloc[0]["StdDev"]
        return np.random.normal(mean_waiting, std_dev_waiting) 
    else:
        return 0

# Hardcoded probabilities for each event
probabilities = {
    "Base maneuvering time": 1.00,
    "load/unloading time": 1.00,
    "TOOL WAITING": 0.22,
    "LOAD SECUREMENT": 1.00,
    "Crane waiting": 0.14,
    "LiftTruck wait time": 0.24,
    "Administrative papers/authorisations": 0.28,
    "Service Planification Delays": 0.12,
    "Coordination SEG - DRIVERS": 0.09,
    "other delays": 0.09,
}

# Number of simulations
n_simulations = 10000

# Function to get random samples from a distribution
def get_samples(dist_name, params, size):
    if dist_name == "lognorm":
        s, loc, scale = params
        return lognorm.rvs(s, loc, scale, size=size)
    elif dist_name == "expon":
        loc, scale = params
        return expon.rvs(loc, scale, size=size)
    elif dist_name == "weibull_min":
        c, loc, scale = params
        return weibull_min.rvs(c, loc, scale, size=size)
    else:
        raise ValueError("Unknown distribution")

# Calculate travel time
def calculate_travel_time(distance_km, speed_kph=80, pause_interval=2, pause_duration=15):
    travel_time_hours = distance_km / speed_kph
    num_pauses = int(travel_time_hours // pause_interval)
    total_pause_time = num_pauses * (pause_duration / 60)
    total_travel_time_hours = travel_time_hours + total_pause_time
    return total_travel_time_hours

# Get user inputs
distance_to_md1 = float(input("Enter distance from original location to MD1 (in km): "))
distance_to_base = float(input("Enter distance from MD1 to base (in km): "))
segment = input("Enter the mission's segment (DNM, TST, WL): ")
while segment not in ["DNM", "TST", "WL"]:
    segment = input("Invalid segment. Enter the mission's segment (DNM, TST, WL): ")
start_date_str = input("Enter the start date (YYYY-MM-DD): ")
departure_time_str = input("Enter the time of departure (HH:MM): ")
start_datetime_str = f"{start_date_str} {departure_time_str}"
start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")

# Calculate travel time to the base
travel_time_to_md1 = calculate_travel_time(distance_to_md1)
travel_time_to_base = calculate_travel_time(distance_to_base)
total_travel_time_to_base = travel_time_to_md1 

# Load the CSV data
data = pd.read_csv("ExportedTimePerSegPreHour.csv")
segment_data = data[data["Segment"] == "All"]

# Simulate the process
simulation_results = []
time_at_md1_list = []
time_at_base_list = []
time_to_base_list = []
time_back_list = []
total_mission_time_list = []

for _ in range(n_simulations):
    # Calculate arrival time at the base
    arrival_time_at_base = start_datetime + datetime.timedelta(hours=total_travel_time_to_base)
    time_to_base_list.append(total_travel_time_to_base)

    #add line for arrival time at base

    # Generate the number of trucks at the base
    arrival_hour = arrival_time_at_base.hour
    hourly_param = segment_data[segment_data["Hour"] == arrival_hour].iloc[0]
    average = hourly_param["Average"]
    median = hourly_param["Median"]
    std_dev = hourly_param["StdDev"]
    num_trucks_at_base = np.random.normal(average, std_dev)
    num_trucks_at_base = max(0, int(num_trucks_at_base))  # Ensure non-negative number of trucks

    # Simulate the total time at the base for each event
    total_time_at_base = 0
    
    for name, (dist_name, params) in distributions.items():
        prob = probabilities[name]
        if np.random.rand() < prob:
            if name == "Base maneuvering time":
                total_time_at_base += sample_base_maneuvering_time(num_trucks_at_base)
            elif name == "TOOL WAITING" :
                tool_waiting_time = sample_tool_waiting_time(arrival_hour, segment)
                total_time_at_base += tool_waiting_time
            else:
                total_time_at_base += get_samples(dist_name, params, 1)[0]




    time_at_base_list.append(total_time_at_base / 60)  # Convert to hours

    # Calculate time to leave base and reach the second destination
    total_mission_time = total_travel_time_to_base + (total_time_at_base / 60) + total_travel_time_to_base
    end_time = start_datetime + datetime.timedelta(hours=total_mission_time)
    
    # Calculate time back
    time_back_list.append(travel_time_to_base)

    if end_time.time() > datetime.time(23, 0):
        # Continue the trip the next day
        next_day_start = datetime.datetime.combine(arrival_time_at_base.date() + datetime.timedelta(days=1), datetime.time(8, 0))
        end_time = next_day_start + datetime.timedelta(hours=(end_time - datetime.datetime.combine(arrival_time_at_base.date(), datetime.time(23, 0))).seconds / 3600)

    simulation_results.append(total_mission_time)
    total_mission_time_list.append(total_mission_time)

# Convert results to array
simulation_results = np.array(simulation_results)

# Calculate the 90% confidence interval for total times
lower_bound = np.percentile(simulation_results, 5)
upper_bound = np.percentile(simulation_results, 95)
average_bound = np.percentile(simulation_results, 50)

# Convert bounds to datetime
arrival_time_lower_bound = start_datetime + datetime.timedelta(hours=lower_bound)
arrival_time_upper_bound = start_datetime + datetime.timedelta(hours=upper_bound)
arrival_time_average = start_datetime + datetime.timedelta(hours=average_bound)
print(f"90% confidence interval for arrival time: {arrival_time_lower_bound} to {arrival_time_upper_bound}")
print(f"Average arrival time: {arrival_time_average}")

# Print some summary statistics
print(f"Mean total time: {np.mean(simulation_results):.2f} hours")
print(f"Median total time: {np.median(simulation_results):.2f} hours")
print(f"Standard deviation of total time: {np.std(simulation_results):.2f} hours")

# Print phase-specific times
print(f"Mean travel time to base: {np.mean(time_to_base_list):.2f} hours")
print(f"Mean time at base: {np.mean(time_at_base_list):.2f} hours")
print(f"Mean travel time back: {np.mean(time_back_list):.2f} hours")
print(f"Mean total mission time: {np.mean(total_mission_time_list):.2f} hours")

# Plot the distribution of total times
plt.figure(figsize=(12, 8))
sns.histplot(simulation_results, bins=50, kde=True)
plt.axvline(lower_bound, color='r', linestyle='--', label='5th percentile')
plt.axvline(upper_bound, color='g', linestyle='--', label='95th percentile')
plt.axvline(average_bound, color='b', linestyle='--', label='average')

plt.title("Distribution of Total Mission Times")
plt.xlabel("Total Time (Hours)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.show()
