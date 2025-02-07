
#####################################################################################################################################
#####################################################################################################################################


# range fft from csv visualiser 

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Define file path for the CSV
csv_file_path = r'C:\path\to\your\directory\Indoor.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Get unique frames
frames = df['Frame Number'].unique()

# Create an empty list to store amplitude values for each frame
amplitude_data = []

# Process each frame
for frame in frames:
    # Filter data for the current frame
    frame_data = df[df['Frame Number'] == frame]
    # Get amplitude values sorted by Range Profile Index
    amplitudes = frame_data.sort_values('Range Profile Index')['Amplitude'].values
    # Ensure we have 256 bins, fill with zeros if less
    if len(amplitudes) < 256:
        amplitudes = np.pad(amplitudes, (0, 64 - len(amplitudes)), 'constant')
    amplitude_data.append(amplitudes)

# Convert the list of amplitude data to a NumPy array
amplitude_matrix = np.array(amplitude_data)

# Transpose the amplitude matrix to flip axes
amplitude_matrix = amplitude_matrix.T

# Plot the heatmap
plt.figure(figsize=(12, 6))
plt.imshow(amplitude_matrix, aspect='auto', cmap='viridis', interpolation='none', origin='upper')
plt.colorbar(label='Amplitude')
plt.xlabel('Frame Number')
plt.ylabel('Range Profile Index')
plt.title('Range FFT Heatmap')
plt.gca().invert_yaxis()  # Invert y-axis to ensure range profile indices start from 0 at the top
plt.show()

################################################################################################################################
################################################################################################################################
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Define file path for the CSV
csv_file_path = r'C:\path\to\your\directory\radar96data02.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Get unique frames
frames = df['Frame Number'].unique()

# Create an empty list to store amplitude values for each frame
amplitude_data = []

# Process each frame
for frame in frames:
    # Filter data for the current frame
    frame_data = df[df['Frame Number'] == frame]
    # Get amplitude values sorted by Range Profile Index
    amplitudes = frame_data.sort_values('Range Profile Index')['Amplitude'].values
    # Ensure we have 256 bins, fill with zeros if less
    if len(amplitudes) < 256:
        amplitudes = np.pad(amplitudes, (0, 256 - len(amplitudes)), 'constant')
    amplitude_data.append(amplitudes)

# Convert the list of amplitude data to a NumPy array
amplitude_matrix = np.array(amplitude_data)

# Apply a different windowing function to experiment
window = np.hamming(len(frames))
amplitude_matrix = amplitude_matrix * window[:, None]

# Perform Doppler FFT across frames for each range bin
# Zero-pad the FFT to increase Doppler resolution
doppler_fft_size = 512  # Increase the FFT size to improve Doppler resolution
range_doppler_matrix = np.fft.fftshift(np.fft.fft(amplitude_matrix, n=doppler_fft_size, axis=0), axes=0)

# Take the magnitude (absolute value) of the FFT result
range_doppler_magnitude = np.abs(range_doppler_matrix)

# Normalize the magnitude to bring the values to a smaller scale (e.g., 0 to 1)
range_doppler_magnitude = range_doppler_magnitude / np.max(range_doppler_magnitude)

# Plot the Range-Doppler Map
plt.figure(figsize=(12, 6))
plt.imshow(range_doppler_magnitude, aspect='auto', cmap='viridis', interpolation='none', origin='upper')
plt.colorbar(label='Normalized Amplitude')
plt.xlabel('Range Bin')
plt.ylabel('Doppler Bin')
plt.title('Normalized Range-Doppler Map with Improved Doppler Resolution')
plt.show()
