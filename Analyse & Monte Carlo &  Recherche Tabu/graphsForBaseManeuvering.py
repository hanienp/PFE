import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm, norm

# Convert time from HH:MM:SS to seconds
def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

# Log-normal distribution parameters
shape = 0.77
loc = 0.00
scale_original = 5.76

# Means for each truck range in seconds
means = {
    "0-2": time_to_seconds("00:06:21"),
    "2-4": time_to_seconds("00:08:51"),
    "4-6": time_to_seconds("00:10:42"),
    "6+": time_to_seconds("00:12:51"),
}

# Original mean in seconds
mean_original = time_to_seconds("00:08:36")

# Calculate the adjusted scale for each mean
scales = {k: v / (mean_original / scale_original) for k, v in means.items()}

# Generate x values (time) in seconds
x = np.linspace(0, 50 * 60, 1000)  # 0 to 50 minutes (3000 seconds)

# Plot distributions in separate subplots
fig, axs = plt.subplots(3, 2, figsize=(15, 15))

# Flatten axs array for easy iteration
axs = axs.flatten()

# Original distribution for comparison
rv_original = lognorm(s=shape, loc=loc, scale=scale_original)
rv_original_normal = norm(loc=mean_original, scale=scale_original)

for i, (label, scale) in enumerate(scales.items()):
    rv = lognorm(s=shape, loc=loc, scale=scale)
    rv_normal = norm(loc=means[label], scale=scale)
    axs[i].plot(x / 60, rv.pdf(x), label=f'{label} trucks (Lognorm)')  # Convert x to minutes
    axs[i].plot(x / 60, rv_normal.pdf(x), label=f'{label} trucks (Normal)')
    axs[i].plot(x / 60, rv_original.pdf(x), 'k--', label='Original (Lognorm)')
    axs[i].plot(x / 60, rv_original_normal.pdf(x), 'k:', label='Original (Normal)')
    axs[i].set_xlim(0, 50)  # Limit x-axis to 50 minutes
    axs[i].set_xlabel('Time (minutes)')
    axs[i].set_ylabel('Probability Density')
    axs[i].legend()
    axs[i].grid(True)
    axs[i].set_title(f'Distribution for {label} trucks')
    
    # Print final parameters
    print(f'Parameters for {label} trucks:')
    print(f'  Log-normal: shape={shape}, loc={loc}, scale={scale}')
    print(f'  Normal: mean={means[label]}, std_dev={scale}')

# Hide the last unused subplot
fig.delaxes(axs[-1])

plt.tight_layout()
plt.show()
