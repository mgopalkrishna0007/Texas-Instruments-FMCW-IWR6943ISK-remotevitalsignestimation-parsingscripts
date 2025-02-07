# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from scipy.signal import butter, filtfilt

# # Path to the CSV file
# csv_file_path = r'C:\path\to\your\directory\point_cloud_data_6m.csv'

# def read_csv_file(file_path):
#     df = pd.read_csv(file_path)
#     # Assuming columns are named 'x', 'y', 'z', and 'velocity'
#     return df[['X', 'Y', 'Z', 'Doppler']].values

# def compute_normalized_accumulated_values(points, range_bins):
#     range_data = np.array([np.linalg.norm([p[0], p[1], p[2]]) for p in points])
#     range_hist, bin_edges = np.histogram(range_data, bins=range_bins, range=(0, 50))
#     max_value = np.max(range_hist) if np.max(range_hist) > 0 else 1
#     normalized_accumulated_values = range_hist / max_value
#     return bin_edges[:-1], normalized_accumulated_values

# def calculate_phase(points):
#     I = np.array([p[0] for p in points])
#     Q = np.array([p[1] for p in points])
#     complex_signal = I + 1j * Q
#     phase = np.angle(complex_signal)
#     return phase

# def unwrap_phase(phase):
#     unwrapped_phase = np.copy(phase)
#     n = len(phase)
#     for i in range(n - 1):
#         if np.abs(phase[i + 1] - phase[i]) > np.pi:
#             unwrapped_phase[i + 1] = unwrapped_phase[i + 1] - 2 * np.pi * np.sign(phase[i + 1] - phase[i])
#     return unwrapped_phase

# def apply_second_fft(matrix):
#     fft_matrix = np.fft.fft(matrix, axis=0)
#     magnitude_matrix = np.abs(fft_matrix)
#     return magnitude_matrix

# def gaussian_interpolation(max_vibration_index, range_vibration_map):
#     i = max_vibration_index[0]
#     j = max_vibration_index[1]
#     y1, y2, y3 = range_vibration_map[i, j-1:j+2]
#     fine_frequency = j + (np.log(y1) - np.log(y3)) / (2 * (np.log(y1) - 2*np.log(y2) + np.log(y3)))
#     return fine_frequency

# def butter_bandpass(lowcut, highcut, fs, order=5):
#     nyquist = 0.5 * fs
#     low = lowcut / nyquist
#     high = highcut / nyquist
#     b, a = butter(order, [low, high], btype='band')
#     return b, a

# def bandpass_filter(data, lowcut, highcut, fs, order=5):
#     b, a = butter_bandpass(lowcut, highcut, fs, order=order)
#     y = filtfilt(b, a, data)
#     return y

# def calculate_breathing_rate(breathing_waveform, fs):
#     n = len(breathing_waveform)
#     fft_result = np.fft.fft(breathing_waveform)
#     fft_frequencies = np.fft.fftfreq(n, d=1/fs)
#     positive_frequencies = fft_frequencies[:n//2]
#     positive_magnitudes = np.abs(fft_result[:n//2])
#     lowcut = 0.2
#     highcut = 0.34
#     valid_indices = np.where((positive_frequencies >= lowcut) & (positive_frequencies <= highcut))
#     peak_index = np.argmax(positive_magnitudes[valid_indices])
#     peak_frequency = positive_frequencies[valid_indices][peak_index]
#     breathing_rate_bpm = peak_frequency * 60
#     return breathing_rate_bpm

# # Parameters
# range_bins = 3
# fs = 10

# # Read data from CSV file
# points = read_csv_file(csv_file_path)

# # Initialize matrices
# range_slowtime_matrix = np.zeros((range_bins, 1))
# unwrapped_phase_matrix = np.zeros((range_bins, 1))

# # Process the data
# if len(points) > 0:
#     range_edges, accumulated_values = compute_normalized_accumulated_values(points, range_bins)
#     range_slowtime_matrix[:, 0] = accumulated_values

#     phase = calculate_phase(points)
#     if len(phase) > 0:
#         phase_bin_indices = np.linspace(0, range_bins - 1, num=len(phase), dtype=int)
#         unwrapped_phase = unwrap_phase(phase)
#         for idx, bin_index in enumerate(phase_bin_indices):
#             if bin_index < range_bins:
#                 unwrapped_phase_matrix[bin_index, 0] = unwrapped_phase[idx]

# # Apply the second FFT to the unwrapped phase matrix
# range_vibration_map = apply_second_fft(unwrapped_phase_matrix)

# # Find the cell with the maximum vibration
# max_vibration_value = np.max(range_vibration_map)
# max_vibration_index = np.unravel_index(np.argmax(range_vibration_map), range_vibration_map.shape)

# # Apply Gaussian interpolation to find the fine vibration frequency
# fine_vibration_frequency = gaussian_interpolation(max_vibration_index, range_vibration_map)

# # Use a bandpass filter for breathing rate detection
# best_range_bin = max_vibration_index[0]
# breathing_waveform = range_slowtime_matrix[best_range_bin, :]

# # Bandpass filter for breathing frequency range (0.2 to 0.34 Hz)
# lowcut = 0.2
# highcut = 0.34
# filtered_breathing_waveform = bandpass_filter(breathing_waveform, lowcut, highcut, fs)

# # Calculate the breathing rate
# breathing_rate_bpm = calculate_breathing_rate(filtered_breathing_waveform, fs)

# # Plotting the Range-Vibration Map with the Maximum Vibration Point Highlighted
# fig, ax = plt.subplots(figsize=(12, 8))

# # Plot the full Range-Vibration Map
# cax = ax.imshow(range_vibration_map, aspect='auto', cmap='plasma', origin='lower',
#                  extent=[0, 1, 0, range_bins])  # Adjust extent as needed
# cbar = plt.colorbar(cax, ax=ax, orientation='vertical', pad=0.02)
# cbar.set_label('Magnitude of Vibration Frequency')

# # Highlight the maximum vibration point
# ax.scatter(max_vibration_index[1], max_vibration_index[0], color='white', s=10, label='Max Vibration')

# ax.set_xlabel('Frame Index (Slow Time)')
# ax.set_ylabel('Range Index')
# ax.set_title(f'Range-Vibration Map with Maximum Vibration Point at {max_vibration_index}')
# ax.legend()

# plt.show()

# # Output the results
# print(f"Maximum Vibration Value: {max_vibration_value} at Index: {max_vibration_index}")
# print(f"Fine Vibration Frequency: {fine_vibration_frequency:.2f} Hz")
# print(f"Breathing Rate: {breathing_rate_bpm:.2f} breaths per minute")



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

file_path =  r'C:\path\to\your\directory\point_cloud_data_6m.csv'


def read_csv_file(file_path):
    data = pd.read_csv(file_path)
    return data

def remove_dc_component(points):
    I = points['x'].values
    Q = points['y'].values
    
    I_detrended = I - np.mean(I)
    Q_detrended = Q - np.mean(Q)
    
    points_dc_removed = points.copy()
    points_dc_removed['x'] = I_detrended
    points_dc_removed['y'] = Q_detrended
    
    return points_dc_removed

def compute_normalized_accumulated_values(points, range_bins):
    range_data = np.linalg.norm(points[['x', 'y', 'z']].values, axis=1)
    
    range_hist, bin_edges = np.histogram(range_data, bins=range_bins, range=(0, 50))
    
    max_value = np.max(range_hist) if np.max(range_hist) > 0 else 1
    normalized_accumulated_values = range_hist / max_value
    
    return bin_edges[:-1], normalized_accumulated_values

def calculate_phase(points):
    I = points['x'].values
    Q = points['y'].values
    
    complex_signal = I + 1j * Q
    
    phase = np.angle(complex_signal)
    
    return phase

def unwrap_phase(phase):
    unwrapped_phase = np.copy(phase)
    n = len(phase)
    
    for i in range(n - 1):
        if np.abs(phase[i + 1] - phase[i]) > np.pi:
            unwrapped_phase[i + 1] = unwrapped_phase[i + 1] - 2 * np.pi * np.sign(phase[i + 1] - phase[i])
    
    return unwrapped_phase

def apply_second_fft(matrix):
    fft_matrix = np.fft.fft(matrix, axis=0)
    magnitude_matrix = np.abs(fft_matrix)
    return magnitude_matrix

def gaussian_interpolation(max_vibration_index, range_vibration_map):
    i = max_vibration_index[0]  # Range index
    j = max_vibration_index[1]  # Frequency index
    
    # Define a list to hold the values y1, y2, and y3
    values = []
    
    # Collect y1, y2, and y3 from the range_vibration_map
    while len(values) < 3:
        # Check if j-1 and j+1 are within bounds
        if j > 0 and j < range_vibration_map.shape[1] - 1:
            values = range_vibration_map[i, j-1:j+2]
        elif j == 0:  # Handle case when j is at the start of the range
            values = range_vibration_map[i, j:j+3]
        elif j == range_vibration_map.shape[1] - 1:  # Handle case when j is at the end of the range
            values = range_vibration_map[i, j-2:j+1]
        
        # If not enough values, move j to next or previous index
        if len(values) < 3:
            if j > 0 and j < range_vibration_map.shape[1] - 1:
                j += 1
            elif j == 0:
                j += 1
            elif j == range_vibration_map.shape[1] - 1:
                j -= 1
    
    y1, y2, y3 = values
    
    # Gaussian interpolation formula to find fine frequency
    fine_frequency = j + (np.log(y1) - np.log(y3)) / (2 * (np.log(y1) - 2 * np.log(y2) + np.log(y3)))
    
    return fine_frequency

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def calculate_breathing_rate(breathing_waveform, fs):
    # Perform FFT on the breathing waveform
    n = len(breathing_waveform)
    fft_result = np.fft.fft(breathing_waveform)
    fft_frequencies = np.fft.fftfreq(n, d=1/fs)
    
    # Take the positive frequencies and corresponding magnitudes
    positive_frequencies = fft_frequencies[:n//2]
    positive_magnitudes = np.abs(fft_result[:n//2])
    
    # Define the breathing rate range (in Hz)
    lowcut = 0.2
    highcut = 0.34
    
    # Find the index range that corresponds to the breathing rate range
    valid_indices = np.where((positive_frequencies >= lowcut) & (positive_frequencies <= highcut))
    
    # Find the peak frequency within the valid range
    peak_index = np.argmax(positive_magnitudes[valid_indices])
    peak_frequency = positive_frequencies[valid_indices][peak_index]
    
    # Convert the peak frequency to breaths per minute
    breathing_rate_bpm = peak_frequency * 60
    
    return breathing_rate_bpm

# Parameters
point_step = 28  # Adjust based on your point data structure
range_bins = 50  # Number of bins for range
fs = 10  # Sampling frequency in Hz

# Read data from CSV file
data = read_csv_file(file_path)

# Initialize matrices
range_slowtime_matrix = np.zeros((range_bins, len(data)))
unwrapped_phase_matrix = np.zeros((range_bins, len(data)))

# Process each frame
for frame_index in range(len(data)):
    # Extract the frame data
    points = data.iloc[frame_index]
    
    # Remove DC component
    points_dc_removed = remove_dc_component(points)
    
    if len(points_dc_removed) > 0:
        range_edges, accumulated_values = compute_normalized_accumulated_values(points_dc_removed, range_bins)
        
        if np.any(accumulated_values > 0):
            range_slowtime_matrix[:, frame_index] = accumulated_values
            
        phase = calculate_phase(points_dc_removed)
        
        if len(phase) > 0:
            phase_bin_indices = np.linspace(0, range_bins - 1, num=len(phase), dtype=int)
            
            unwrapped_phase = unwrap_phase(phase)
            
            for idx, bin_index in enumerate(phase_bin_indices):
                if bin_index < range_bins:
                    unwrapped_phase_matrix[bin_index, frame_index] = unwrapped_phase[idx]
    else:
        print(f"Frame {frame_index} has no valid points.")

# Apply the second FFT to the unwrapped phase matrix
range_vibration_map = apply_second_fft(unwrapped_phase_matrix)

# Find the cell with the maximum vibration
max_vibration_value = np.max(range_vibration_map)
max_vibration_index = np.unravel_index(np.argmax(range_vibration_map), range_vibration_map.shape)

# Apply Gaussian interpolation to find the fine vibration frequency
fine_vibration_frequency = gaussian_interpolation(max_vibration_index, range_vibration_map)

# Use a bandpass filter for breathing rate detection
best_range_bin = max_vibration_index[0]
breathing_waveform = range_slowtime_matrix[best_range_bin, :]

# Bandpass filter for breathing frequency range (0.2 to 0.34 Hz)
lowcut = 0.2
highcut = 0.34
filtered_breathing_waveform = bandpass_filter(breathing_waveform, lowcut, highcut, fs)

# Calculate the breathing rate
breathing_rate_bpm = calculate_breathing_rate(filtered_breathing_waveform, fs)

# Plotting the Range-Vibration Map with the Maximum Vibration Point Highlighted
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the full Range-Vibration Map
cax = ax.imshow(range_vibration_map, aspect='auto', cmap='plasma', origin='lower',
                 extent=[0, len(data), 0, range_bins])
cbar = plt.colorbar(cax, ax=ax, orientation='vertical', pad=0.02)
cbar.set_label('Magnitude of Vibration Frequency')

# Highlight the maximum vibration point
ax.scatter(max_vibration_index[1], max_vibration_index[0], color='white', s=10, label='Max Vibration')

ax.set_xlabel('Frame Index (Slow Time)')
ax.set_ylabel('Range Index')
ax.set_title(f'Range-Vibration Map with Maximum Vibration Point at {max_vibration_index}')
ax.legend()

plt.show()

# Output the results
print(f"Maximum Vibration Value: {max_vibration_value} at Index: {max_vibration_index}")
print(f"Fine Vibration Frequency: {fine_vibration_frequency:.2f} Hz")
print(f"Breathing Rate: {breathing_rate_bpm:.2f} breaths per minute")
