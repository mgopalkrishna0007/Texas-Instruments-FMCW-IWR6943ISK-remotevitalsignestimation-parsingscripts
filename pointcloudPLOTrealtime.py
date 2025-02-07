

# import serial
# import numpy as np
# import struct
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.animation import FuncAnimation
# import time

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE

# def parsePointCloudTLV(tlvData, tlvLength, outputDict):
#     pointCloud = outputDict['pointCloud']
#     pointStruct = '4f'  # X, Y, Z, and Doppler
#     pointStructSize = struct.calcsize(pointStruct)
#     numPoints = int(tlvLength / pointStructSize)

#     for i in range(numPoints):
#         try:
#             x, y, z, doppler = struct.unpack(pointStruct, tlvData[:pointStructSize])
#         except:
#             numPoints = i
#             print('ERROR: Point Cloud TLV Parsing Failed')
#             break
#         tlvData = tlvData[pointStructSize:]
#         pointCloud[i, 0] = x
#         pointCloud[i, 1] = y
#         pointCloud[i, 2] = z
#         pointCloud[i, 3] = doppler
#     outputDict['numDetectedPoints'], outputDict['pointCloud'] = numPoints, pointCloud

# def read_and_parse_data(serial_port, outputDict):
#     byte_buffer = bytearray()
    
#     if serial_port.in_waiting > 0:
#         byte_buffer.extend(serial_port.read(serial_port.in_waiting))
        
#         if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#             header = byte_buffer[:HEADER_SIZE]
#             total_packet_length = int.from_bytes(header[12:16], byteorder='little')
            
#             if len(byte_buffer) >= total_packet_length:
#                 data = byte_buffer[:total_packet_length]
#                 byte_buffer = byte_buffer[total_packet_length:]
                
#                 # Example processing of TLV data
#                 tlvData = data[HEADER_SIZE:]  # Assuming TLV data starts after the header
#                 tlvLength = len(tlvData)
                
#                 # Initialize output dictionary for point cloud data
#                 outputDict['pointCloud'] = np.zeros((100000, 4))  # Adjust size based on your needs
                
#                 # Call parsePointCloudTLV function
#                 parsePointCloudTLV(tlvData, tlvLength, outputDict)

# def animate(i, serial_port, scatter, outputDict):
#     read_and_parse_data(serial_port, outputDict)
#     pointCloud = outputDict['pointCloud']
#     num_points = outputDict['numDetectedPoints']
    
#     scatter._offsets3d = (pointCloud[:num_points, 0], pointCloud[:num_points, 1], pointCloud[:num_points, 2])
#     return scatter,

# def serialConfig(configFileName):
#     global CLIport
#     global Dataport

#     print("Starting serial configuration...")
#     # Open the serial ports for the configuration and the data ports
#     try:
#         CLIport = serial.Serial('COM3', 115200)
#         Dataport = serial.Serial('COM7', 921600)
#         print("Serial ports opened successfully.")
#     except serial.SerialException as e:
#         print(f"Error opening serial ports: {e}")
#         return None, None

#     # Read the configuration file and send it to the board
#     try:
#         with open(configFileName, 'r') as f:
#             config = [line.rstrip('\r\n') for line in f]
#             print(f"Configuration file {configFileName} loaded.")
#     except FileNotFoundError:
#         print(f"Error: The configuration file {configFileName} was not found.")
#         return None, None

#     for i in config:
#         CLIport.write((i + '\n').encode())
#         print(f"Sent config: {i}")
#         time.sleep(0.01)
        
#     print("Serial configuration completed.")
#     return CLIport, Dataport

# def main():
#     # Configuration
#     configFileName = 'C:/ti/radar_toolbox_2_10_00_04/source/ti/examples/Medical/Vital_Signs_With_People_Tracking/chirp_configs/vital_signs_ISK_6m.cfg'
#     CLIport, Dataport = serialConfig(configFileName)

#     if CLIport is None or Dataport is None:
#         print("Failed to configure radar. Exiting...")
#         return

#     # Initialize the output dictionary
#     outputDict = {
#         'pointCloud': np.zeros((10000, 4)),
#         'numDetectedPoints': 0
#     }

#     # Create a 3D plot
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     scatter = ax.scatter([], [], [], c='b', marker='o', s=10)
#     ax.set_xlabel('X')
#     ax.set_ylabel('Y')
#     ax.set_zlabel('Z')
#     ax.set_title('Real-Time 3D Point Cloud')

#     # Create an animation function
#     ani = FuncAnimation(fig, animate, fargs=(Dataport, scatter, outputDict), interval=100, blit=False)

#     plt.show()

# if __name__ == "__main__":
#     main()

import serial
import numpy as np
import struct
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import time

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
                outputDict['pointCloud'] = np.zeros((100000, 4))  # Adjust size based on your needs
                
                # Call parsePointCloudTLV function
                parsePointCloudTLV(tlvData, tlvLength, outputDict)

def animate(i, serial_port, scatter, outputDict):
    read_and_parse_data(serial_port, outputDict)
    pointCloud = outputDict['pointCloud']
    num_points = outputDict['numDetectedPoints']
    
    scatter._offsets3d = (pointCloud[:num_points, 0], pointCloud[:num_points, 1], pointCloud[:num_points, 2])
    return scatter,

def serialConfig(configFileName):
    global CLIport
    global Dataport

    print("Starting serial configuration...")
    # Open the serial ports for the configuration and the data ports
    try:
        CLIport = serial.Serial('COM3', 115200)
        Dataport = serial.Serial('COM7', 921600)
        print("Serial ports opened successfully.")
    except serial.SerialException as e:
        print(f"Error opening serial ports: {e}")
        return None, None

    # Read the configuration file and send it to the board
    try:
        with open(configFileName, 'r') as f:
            config = [line.rstrip('\r\n') for line in f]
            print(f"Configuration file {configFileName} loaded.")
    except FileNotFoundError:
        print(f"Error: The configuration file {configFileName} was not found.")
        return None, None

    for i in config:
        CLIport.write((i + '\n').encode())
        print(f"Sent config: {i}")
        time.sleep(0.01)
        
    print("Serial configuration completed.")
    return CLIport, Dataport

def check_radar_output(serial_port):
    # Check if the radar is sending data correctly
    print("Checking radar output...")
    # Read a few bytes to verify data output
    start_time = time.time()
    while time.time() - start_time < 10:  # 10 seconds timeout
        if serial_port.in_waiting > 0:
            print("Radar output detected.")
            return True
        time.sleep(1)
    print("No radar output detected.")
    return False

def main():
    # Configuration
    configFileName = 'C:/ti/radar_toolbox_2_10_00_04/source/ti/examples/Medical/Vital_Signs_With_People_Tracking/chirp_configs/vital_signs_ISK_6m.cfg'
    CLIport, Dataport = serialConfig(configFileName)

    if CLIport is None or Dataport is None:
        print("Failed to configure radar. Exiting...")
        return

    # Check for radar output
    if not check_radar_output(Dataport):
        print("Radar is not producing output. Exiting...")
        return

    # Initialize the output dictionary
    outputDict = {
        'pointCloud': np.zeros((10000, 4)),
        'numDetectedPoints': 0
    }

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter([], [], [], c='b', marker='o', s=10)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Real-Time 3D Point Cloud')

    # Create an animation function
    ani = FuncAnimation(fig, animate, fargs=(Dataport, scatter, outputDict), interval=100, blit=False)

    plt.show()

if __name__ == "__main__":
    main()
