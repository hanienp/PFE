import csv
import copy
import random
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta

from level2Montefuction import MontecarloSim as monte_carlo_simulation


def minutes_to_hhmm(minutes):
    base_time = datetime(1900, 1, 1, 0, 0)  
    time_delta = timedelta(minutes=minutes)
    return base_time + time_delta

def read_csv(file_path):
    trucks = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            trucks.append({
                'truck_id': row['truck_id'],
                'BL': row['BL'],
            })
    return trucks

def convert_to_minutes(time_str):
    # Assumes time_str is in format 'HH:MM'
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def create_time_segments():
    # Time segments between 8 AM and 4:30 PM, each 30 mins
    segments = []
    start_time = 8 * 60  # 8:00 AM in minutes
    end_time = 16 * 60 + 30  # 4:30 PM in minutes
    while start_time < end_time:
        segments.append((start_time, start_time + 30))
        start_time += 30
    return segments

def solution_zero(trucks):
    time_segments = create_time_segments()
    S0_schedule = []
    for truck in trucks:
        random_time = random.choice(time_segments)
        S0_schedule.append({
            "truck_id": truck["truck_id"],
            "BL": truck["BL"],
            "Time Segment": random_time
        })
    return pd.DataFrame(S0_schedule)

def objective_function(schedule):
    time_segments = create_time_segments()
    trucks_per_time_segment = {time_segment: 0 for time_segment in time_segments}
    
    for _, row in schedule.iterrows():
        trucks_per_time_segment[row["Time Segment"]] += 1
    
    simulation_time = 0
    last_nonempty_time = 0  # Initialize the last_nonempty_time
    
    for time_segment in time_segments:
        num_trucks = trucks_per_time_segment[time_segment]
        truck_list = schedule[schedule["Time Segment"] == time_segment]
        
        for _, tr in truck_list.iterrows():
            bl = tr["BL"]
            processing_time, std_dev = monte_carlo_simulation(minutes_to_hhmm(time_segment[0]), num_trucks, bl)
            simulation_time += processing_time
            for time_seg in time_segments:
                if time_seg[0] <= (time_segment[0] + processing_time) and time_seg[0] > time_segment[0]:
                    trucks_per_time_segment[time_seg] += 1
            last_nonempty_time = time_segment
    
    return simulation_time, last_nonempty_time

def generate_neighbor(schedule):
    times = create_time_segments()
    schedule_copy = schedule.copy()
    random_index = random.randint(0, len(schedule_copy) - 1)
    new_time_segment = random.choice(times)
    schedule_copy.at[random_index, "Time Segment"] = new_time_segment
    return schedule_copy

def tabu_search(trucks, max_iterations, tabu_tenure):
    # Initial solution
    best_solution = solution_zero(trucks)  # Ensure it's a DataFrame
    best_time, best_max_time = objective_function(best_solution)
    
    # Tabu list
    tabu_list = []
    
    current_solution = copy.deepcopy(best_solution)
    current_time, current_max_time = best_time, best_max_time
    
    for iteration in range(max_iterations):
        print(iteration)
        print("starting to generate neighbors")
        neighborhood = [generate_neighbor(current_solution) for _ in range(1)]
        neighborhood = sorted(neighborhood, key=lambda x: objective_function(x)[0])
        print("neighborhood ready")
        for neighbor in neighborhood:
            print("neighbor jdid")
            if not any(neighbor.equals(tabu) for tabu in tabu_list):
                current_solution = neighbor
                current_time, current_max_time = objective_function(current_solution)
                if current_time < best_time:
                    best_solution = copy.deepcopy(current_solution)
                    best_time = current_time
                    best_max_time = current_max_time
                elif current_time == best_time:
                    if current_max_time < best_max_time:
                        best_solution = copy.deepcopy(current_solution)
                        best_time = current_time
                        best_max_time = current_max_time
                tabu_list.append(neighbor)
                if len(tabu_list) > tabu_tenure:
                    tabu_list.pop(0)
                break
    
    return best_solution, best_time, best_max_time

if __name__ == "__main__":
    file_path = 'dailylist.csv'
    trucks = read_csv(file_path)
    time_segments = create_time_segments()
    
    max_iterations = 1000
    tabu_tenure = 50
    
    best_schedule, best_time, best_max_time = tabu_search(trucks, max_iterations, tabu_tenure)
    print("Best Schedule:", best_schedule)
    print("Best Loading/Offloading Time:", best_time)
    print("Best max Time:", minutes_to_hhmm(best_max_time[0]))  # Convert minutes to HH:MM
