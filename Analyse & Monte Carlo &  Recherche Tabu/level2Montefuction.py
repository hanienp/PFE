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




def MontecarloSim(arrival_time_at_base,num_trucks_at_base, segment ):
    
    

    # Load the CSV data
    data = pd.read_csv("ExportedTimePerSegPreHour.csv")
    segment_data = data[data["Segment"] == "All"]

    # Simulate the process
    simulation_results = []
    
    time_at_base_list = []
   
   

    for _ in range(n_simulations):
        
        arrival_hour = arrival_time_at_base.hour
        hourly_param = segment_data[segment_data["Hour"] == arrival_hour].iloc[0]
        
        

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
        total_mission_time = (total_time_at_base / 60)
        
        
        
        simulation_results.append(total_mission_time)
        

    # Convert results to array
    simulation_results = np.array(simulation_results)

    average = np.percentile(simulation_results, 50)
    standard_dev = np.std(simulation_results)

    return average, standard_dev

