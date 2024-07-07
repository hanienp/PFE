import numpy as np
import matplotlib.pyplot as plt

# Parameters
num_kilometers = 100  # Example distance from X to Y
av_trip = 2.0  # Average time to pass 1 km (minutes)
min_trip = 1.0  # Minimum time to pass 1 km (minutes)
sdev_trip = 0.5  # Standard deviation of time to pass 1 km (minutes)
num_simulations = 10000  # Number of Monte Carlo simulations

# Monte Carlo simulation
total_times = []
for _ in range(num_simulations):
    #calculating trip time :
    times = np.random.normal(av_trip, sdev_trip, num_kilometers)
    # Apply the minimum time constraint
    times = np.maximum(times, min_trip)
    total_time = np.sum(times)
    total_times.append(total_time)
    #calculating nb of trucks at base :
    


# Results
mean_time = np.mean(total_times)
std_dev_time = np.std(total_times)

print(f"Estimated mean travel time: {mean_time:.2f} minutes")
print(f"Estimated standard deviation of travel time: {std_dev_time:.2f} minutes")

# Plotting the results
plt.hist(total_times, bins=50, edgecolor='black')
plt.title('Monte Carlo Simulation of Truck Travel Time')
plt.xlabel('Total Travel Time (minutes)')
plt.ylabel('Frequency')
plt.show()
