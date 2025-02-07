import serial
import numpy as np
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 32  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE

def parsePointCloudTLV(tlvData, tlvLength, outputDict):
    pointCloud = outputDict['pointCloud']
    pointStruct = '4f'  # X, Y, Z, and Doppler
    pointStructSize = struct.calcsize(pointStruct)
    numPoints = int(tlvLength / pointStructSize)

    for i in range(numPoints):
        try:
            x, y, z, doppler = struct.unpack(pointStruct, tlvData[:pointStructSize])
        except:
            numPoints = i
            print('ERROR: Point Cloud TLV Parsing Failed')
            break
        tlvData = tlvData[pointStructSize:]
        pointCloud[i, 0] = x
        pointCloud[i, 1] = y
        pointCloud[i, 2] = z
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
                
                # Call parsePointCloudTLV function
                parsePointCloudTLV(tlvData, tlvLength, outputDict)

def animate(i, serial_port, scatter, outputDict):
    read_and_parse_data(serial_port, outputDict)
    pointCloud = outputDict['pointCloud']
    num_points = outputDict['numDetectedPoints']
    
    scatter.set_offsets(pointCloud[:num_points, :2])  # Set the X and Y data for 2D plot
    return scatter,

def main():
    comport = 'COM7'
    baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
    outputDict = {
        'pointCloud': np.zeros((1000, 4)),
        'numDetectedPoints': 0
    }

    fig, ax = plt.subplots()
    scatter = ax.scatter([], [], c='b', marker='o', s=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Real-Time 2D Point Cloud')

    ani = FuncAnimation(fig, animate, fargs=(serial.Serial(comport, baudrate=baudrate, timeout=1), scatter, outputDict), interval=100, blit=False)

    plt.show()

if __name__ == "__main__":
    main()
