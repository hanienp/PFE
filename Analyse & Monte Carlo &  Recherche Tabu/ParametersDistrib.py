import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
from scipy.stats import norm, expon, lognorm, weibull_min, poisson, kstest

# Read the CSV file
df = pd.read_csv('time_loss_data.csv')

# Function to convert time string to timedelta
def to_timedelta(time_str):
    h, m, s = map(int, time_str.split(':'))
    return timedelta(hours=h, minutes=m, seconds=s)

# Function to convert timedelta to HH:MM:SS format
def to_hhmmss(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'

# Function to fit distributions and find the best fit
def fit_distributions(data):
    distributions = {
        "norm": norm,
        "expon": expon,
        "lognorm": lognorm,
        "weibull_min": weibull_min
    }
    best_fit = None
    best_stat = float('inf')
    best_params = None
    
    for name, distribution in distributions.items():
        if name == "lognorm":
            params = distribution.fit(data, floc=0)
        elif name == "weibull_min":
            params = distribution.fit(data, floc=0)
        else:
            params = distribution.fit(data)
        
        stat, p = kstest(data, name, args=params)
        
        if stat < best_stat:
            best_fit = name
            best_stat = stat
            best_params = params
    
    # Fit Poisson distribution separately (it assumes integer data)
    poisson_lambda = np.mean(data)
    poisson_data = np.random.poisson(poisson_lambda, len(data))
    poisson_stat, poisson_p = kstest(data, 'poisson', args=(poisson_lambda,))
    
    if poisson_stat < best_stat:
        best_fit = "poisson"
        best_stat = poisson_stat
        best_params = (poisson_lambda,)
    
    return best_fit, best_params

# Calculate the average time for each reason and plot the distribution
average_times = {}
best_fits = {}
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(12, 10))

for i, column in enumerate(df.columns):
    if i >= 9:  # Check if index exceeds the number of subplots
        break  # Exit the loop if all subplots are filled

    # Filter out empty or zero values
    non_empty_times = df[column].dropna()
    non_empty_times = non_empty_times[non_empty_times != '0']

    # Convert times to timedelta
    timedeltas = non_empty_times.apply(to_timedelta)

    # Plot the distribution if not empty
    if not timedeltas.empty:
        # Calculate the average time
        average_time = sum(timedeltas, timedelta()) / len(timedeltas)
        average_times[column] = to_hhmmss(average_time)

        # Convert timedeltas to total minutes for binning
        total_minutes = timedeltas.dt.total_seconds() / 60

        # Create bins of 5-minute intervals
        max_minutes = int(total_minutes.max()) + 1
        bins = [x * 5 for x in range(max_minutes // 5 + 1)]

        # Fit distributions and determine the best fit
        best_fit, best_params = fit_distributions(total_minutes)
        best_fits[column] = (best_fit, best_params)

        # Plot the distribution
        sns.histplot(total_minutes, bins=bins, kde=True, ax=axes[i // 3, i % 3])
        axes[i // 3, i % 3].set_title(f' {column}\nBest fit: {best_fit}', fontsize=10)
        axes[i // 3, i % 3].set_xlabel('Time (Minutes)', fontsize=8)
        axes[i // 3, i % 3].set_ylabel('Frequency', fontsize=8)
        axes[i // 3, i % 3].tick_params(labelsize=6)
        axes[i // 3, i % 3].grid(True)

# Adjust layout and spacing
plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.5, hspace=0.5)

# Show the plot
plt.show()

# Print the average times and best-fit distributions
for reason, avg_time in average_times.items():
    best_fit, best_params = best_fits[reason]
    params_str = ', '.join(f'{param:.2f}' for param in best_params)
    print(f'Average time for {reason}: {avg_time}, Best fit: {best_fit}, Parameters: {params_str}')

# Plot the 10th graph in a separate figure
if len(df.columns) >= 10:
    plt.figure(figsize=(6, 5))
    non_empty_times = df[df.columns[9]].dropna()
    non_empty_times = non_empty_times[non_empty_times != '0']
    timedeltas = non_empty_times.apply(to_timedelta)
    total_minutes = timedeltas.dt.total_seconds() / 60
    max_minutes = int(total_minutes.max()) + 1
    bins = [x * 5 for x in range(max_minutes // 5 + 1)]
    sns.histplot(total_minutes, bins=bins, kde=True)
    best_fit, best_params = fit_distributions(total_minutes)
    best_fits[df.columns[9]] = (best_fit, best_params)
    plt.title(f' {df.columns[9]}\nBest fit: {best_fit}', fontsize=10)
    plt.xlabel('Time (Minutes)', fontsize=8)
    plt.ylabel('Frequency', fontsize=8)
    plt.tick_params(labelsize=6)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Print the best-fit distribution for the 10th graph
    best_fit, best_params = best_fits[df.columns[9]]
    params_str = ', '.join(f'{param:.2f}' for param in best_params)
    print(f'Average time for {df.columns[9]}: {to_hhmmss(average_time)}, Best fit: {best_fit}, Parameters: {params_str}')
