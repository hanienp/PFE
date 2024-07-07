import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# Load the CSV file into a DataFrame
df = pd.read_csv('ToolWaitingPerSegPerHour.csv')

# Convert ToolWaiting to Timedelta
df['ToolWaiting'] = pd.to_timedelta(df['ToolWaiting'])

# Filter out rows with zero ToolWaiting values
df = df[df['ToolWaiting'] > pd.Timedelta(0)]

# Convert ToolWaiting to hours
df['ToolWaiting_hours'] = df['ToolWaiting'].dt.total_seconds() / 3600

# Bin ToolWaiting times into 5-minute intervals
bin_width = 5 / 60  # 5 minutes in hours
bins = np.arange(0, df['ToolWaiting_hours'].max() + bin_width, bin_width)
df['ToolWaiting_binned'] = pd.cut(df['ToolWaiting_hours'], bins, right=False)

# Initialize a dictionary to store the distributions
distributions = {
    'norm': stats.norm,
    'expon': stats.expon,
    'lognorm': stats.lognorm,
    'weibull_min': stats.weibull_min,
    'poisson': stats.poisson
}

# Initialize a dictionary to store the results
results = {}

# Fit data to distributions and perform K-S test
for segment in df['Seg'].unique():
    seg_data = df[df['Seg'] == segment]['ToolWaiting_hours']
    
    best_fit = None
    best_params = None
    best_ks_stat = np.inf
    
    for dist_name, dist in distributions.items():
        if dist_name == 'poisson':
            params = (seg_data.mean(),)  # For Poisson distribution, we need the mean
        else:
            params = dist.fit(seg_data)
        
        ks_stat, p_value = stats.kstest(seg_data, dist_name, args=params)
        
        if ks_stat < best_ks_stat:
            best_fit = dist_name
            best_params = params
            best_ks_stat = ks_stat
    
    results[segment] = {
        'best_fit': best_fit,
        'params': best_params,
        'ks_stat': best_ks_stat
    }
    
    # Print parameters of the best fit distribution
    print(f"Segment: {segment}")
    print(f"Best Fit Distribution: {best_fit}")
    print(f"Parameters: {best_params}")
    print(f"KS Statistic: {best_ks_stat}\n")

    # Plot the data and the best fitting distribution
    plt.figure(figsize=(10, 6))
    plt.hist(seg_data, bins=bins, density=True, alpha=0.6, color='g', label='Data')
    
    dist = distributions[best_fit]
    x = np.linspace(0, seg_data.max(), 1000)
    if best_fit == 'poisson':
        x = np.arange(0, seg_data.max() + 1)
        plt.plot(x, dist.pmf(x, *best_params), 'r-', label=f'{best_fit} fit')
    else:
        plt.plot(x, dist.pdf(x, *best_params), 'r-', label=f'{best_fit} fit')
    
    plt.title(f'Tool Waiting Time Distribution for Segment: {segment}')
    plt.xlabel('Tool Waiting Time (hours)')
    plt.ylabel('Density')
    plt.legend()
    plt.show()
