# this code plots the point cloud data saved in a csv file , it extracts X Y Z naand plots them all combined 

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Path to the CSV file
file_path = 'C:\\path\\to\\your\\directory\\outdoor12.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path, sep=',')  # Adjust separator if needed

# Strip leading/trailing spaces from column names
df.columns = df.columns.str.strip()

# Print the columns to check their names
print("Columns in the CSV file:", df.columns)

# Check if required columns are present
if 'X' in df.columns and 'Y' in df.columns and 'Z' in df.columns:
    # Extract X, Y, Z columns
    x = df['X'].astype(float)
    y = df['Y'].astype(float)
    z = df['Z'].astype(float)

    # Plotting the point cloud data
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the point cloud data
    ax.scatter(x, y, z, c='r', marker='o', s = 1,  label='Point Cloud Data')

    # Plot the radar position at (0, 0, 0)
    ax.scatter(0, 0, 0, c='b', marker='x', s=100, label='Radar Position')

    # Set labels
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')

    # Set plot title
    ax.set_title('3D Point Cloud Data')

    # Add legend
    ax.legend()

    # Show plot
    plt.show()
else:
    print("Required columns 'X', 'Y', 'Z' are not found in the CSV file.")
