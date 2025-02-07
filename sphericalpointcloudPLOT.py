import serial
import numpy as np
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 32  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE

def parseSphericalPointCloudTLV(tlvData, tlvLength, outputDict):
    pointCloud = outputDict['pointCloud']
    pointStruct = '4f'  # Range, Azimuth, Elevation, and Doppler
    pointStructSize = struct.calcsize(pointStruct)
    numPoints = int(tlvLength / pointStructSize)

    for i in range(numPoints):
        try:
            rng, azimuth, elevation, doppler = struct.unpack(pointStruct, tlvData[:pointStructSize])
        except:
            numPoints = i
            print('ERROR: Point Cloud TLV Parsing Failed')
            break
        tlvData = tlvData[pointStructSize:]
        pointCloud[i, 0] = rng
        pointCloud[i, 1] = azimuth
        pointCloud[i, 2] = elevation
        pointCloud[i, 3] = doppler

    outputDict['numDetectedPoints'], outputDict['pointCloud'] = numPoints, pointCloud

def read_and_parse_data(serial_port, outputDict):
    byte_buffer = bytearray()
    
    if serial_port.in_waiting > 0:
        byte_buffer.extend(serial_port.read(serial_port.in_waiting))
        
        if len(byte_buffer) > EXPECTED_HEADER_SIZE:
            header = byte_buffer[:HEADER_SIZE]
            total_packet_length = int.from_bytes(header[12:16], byteorder='little')
            
            if len(byte_buffer) >= total_packet_length:
                data = byte_buffer[:total_packet_length]
                byte_buffer = byte_buffer[total_packet_length:]
                
                # Example processing of TLV data
                tlvData = data[HEADER_SIZE:]  # Assuming TLV data starts after the header
                tlvLength = len(tlvData)
                
                # Initialize output dictionary for point cloud data
                outputDict['pointCloud'] = np.zeros((1000, 4))  # Adjust size based on your needs
                
                # Call parseSphericalPointCloudTLV function
                parseSphericalPointCloudTLV(tlvData, tlvLength, outputDict)

def animate(i, serial_port, scatter, outputDict):
    read_and_parse_data(serial_port, outputDict)
    pointCloud = outputDict['pointCloud']
    num_points = outputDict['numDetectedPoints']
    
    # Update scatter plot with spherical coordinates
    scatter._offsets3d = (pointCloud[:num_points, 0], pointCloud[:num_points, 1], pointCloud[:num_points, 2])
    return scatter,

def main():
    comport = 'COM7'
    baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
    outputDict = {
        'pointCloud': np.zeros((1000, 4)),
        'numDetectedPoints': 0
    }

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Set larger limits for the axes
    ax.set_xlim(-50, 50)  # Adjust these limits as needed
    ax.set_ylim(-50, 50)  # Adjust these limits as needed
    ax.set_zlim(-50, 50)  # Adjust these limits as needed

    # Increase point size
    scatter = ax.scatter([], [], [], c='b', marker='o', s=1)  # Increased size from 1 to 10
    ax.set_xlabel('Range')
    ax.set_ylabel('Azimuth')
    ax.set_zlabel('Elevation')
    ax.set_title('Real-Time Spherical Point Cloud')

    ani = FuncAnimation(fig, animate, fargs=(serial.Serial(comport, baudrate=baudrate, timeout=1), scatter, outputDict), interval=100, blit=False)

    plt.show()

if __name__ == "__main__":
    main()
