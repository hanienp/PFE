import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import lognorm, expon, weibull_min

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

# Simulate the total time for each simulation
total_times = np.zeros(n_simulations)
for name, (dist_name, params) in distributions.items():
    prob = probabilities[name]
    random_numbers = np.random.rand(n_simulations)
    events_happen = random_numbers < prob
    samples = get_samples(dist_name, params, n_simulations)
    total_times += samples * events_happen

# Convert total times to hours, minutes, and seconds
total_times_seconds = total_times * 60  # convert minutes to seconds
total_times_hours = total_times_seconds // 3600
total_times_minutes = (total_times_seconds % 3600) // 60
total_times_seconds = total_times_seconds % 60

# Print some summary statistics
print(f"Mean total time: {np.mean(total_times):.2f} minutes")
print(f"Median total time: {np.median(total_times):.2f} minutes")
print(f"Standard deviation of total time: {np.std(total_times):.2f} minutes")

# Plot the distribution of total times
plt.figure(figsize=(10, 6))
sns.histplot(total_times, bins=50, kde=True)
plt.title("Distribution of Total Times")
plt.xlabel("Total Time (Minutes)")
plt.ylabel("Frequency")
plt.grid(True)
plt.show()
