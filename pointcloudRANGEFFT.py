# GIVES THE RANGE FFT PLOT 

import serial
import numpy as np
import struct
import matplotlib.pyplot as plt

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

def calculate_range(pointCloud):
    # Calculate the range for each point
    ranges = np.sqrt(np.sum(pointCloud[:, :3] ** 2, axis=1))
    return ranges

def read_and_parse_data(serial_port):
    byte_buffer = bytearray()
    range_values = []
    
    while True:
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
                    outputDict = {
                        'pointCloud': np.zeros((1000, 4))  # Adjust size based on your needs
                    }
                    
                    # Call parsePointCloudTLV function
                    parsePointCloudTLV(tlvData, tlvLength, outputDict)
                    
                    # Extract range values
                    ranges = calculate_range(outputDict['pointCloud'])
                    range_values.extend(ranges[:outputDict['numDetectedPoints']])
                    
                    # If we have collected 1000 points, perform FFT
                    if len(range_values) >= 1000:
                        perform_fft(range_values[:1000])
                        range_values = range_values[1000:]  # Keep remaining points for the next batch

def perform_fft(range_values):
    # Perform FFT on the range data
    fft_result = np.fft.fft(range_values, n=1000)
    fft_magnitude = np.abs(fft_result)

    # Plot the FFT result
    plt.clf()
    plt.plot(fft_magnitude[:500])  # Plot the first half of the FFT result
    plt.title('Range FFT')
    plt.xlabel('Frequency Bin')
    plt.ylabel('Magnitude')
    plt.pause(0.01)

def main():
    comport = 'COM7'
    baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
    plt.ion()  # Enable interactive mode for real-time plotting

    try:
        serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
        print(f"Connected to {comport} at {baudrate} baud rate.")
        
        while True:
            read_and_parse_data(serial_port)

    except serial.SerialException as e:
        print(f"SerialException: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'serial_port' in locals() and serial_port.is_open:
            serial_port.close()
        print("Serial port closed.")

if __name__ == "__main__":
    main()


















# import serial
# import numpy as np
# import struct
# import matplotlib.pyplot as plt

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

# def read_and_parse_data(serial_port):
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Example processing of TLV data
#                     tlvData = data[HEADER_SIZE:]  # Assuming TLV data starts after the header
#                     tlvLength = len(tlvData)
                    
#                     # Initialize output dictionary for point cloud data
#                     outputDict = {
#                         'pointCloud': np.zeros((1000, 4))  # Adjust size based on your needs
#                     }
                    
#                     # Call parsePointCloudTLV function
#                     parsePointCloudTLV(tlvData, tlvLength, outputDict)
                    
#                     # Print parsed data
#                     print(f"Parsed Point Cloud Data: {outputDict['pointCloud'][:outputDict['numDetectedPoints']]}")
                    
#                     # Perform and plot range FFT
#                     perform_range_fft(outputDict['pointCloud'][:outputDict['numDetectedPoints']])

# def perform_range_fft(pointCloud):
#     # Extract range from point cloud data
#     # Assuming range = sqrt(x^2 + y^2 + z^2)
#     ranges = np.sqrt(np.sum(pointCloud[:, :3] ** 2, axis=1))

#     # Perform FFT on the range data
#     fft_result = np.fft.fft(ranges)
#     fft_freq = np.fft.fftfreq(len(ranges))

#     # Plot the FFT results
#     plt.clf()  # Clear the plot to update it in real-time
#     plt.plot(fft_freq, np.abs(fft_result))
#     plt.title('Range FFT')
#     plt.xlabel('Frequency')
#     plt.ylabel('Amplitude')
#     plt.pause(0.01)  # Pause to allow the plot to update

# def main():
#     comport = 'COM7'
#     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
#     try:
#         serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
#         print(f"Connected to {comport} at {baudrate} baud rate.")
        
#         plt.ion()  # Turn on interactive plotting mode
        
#         while True:
#             read_and_parse_data(serial_port)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'serial_port' in locals() and serial_port.is_open:
#             serial_port.close()
#         print("Serial port closed.")

# if __name__ == "__main__":
#     main()









# this code gave the 2D point cloud enough , there is another copy of this code line whihc does the similar thing 
# called pointcloudparsingPLOT-2Dedits.py
# import serial
# import numpy as np
# import struct
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

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
#                 outputDict['pointCloud'] = np.zeros((1000, 4))  # Adjust size based on your needs
                
#                 # Call parsePointCloudTLV function
#                 parsePointCloudTLV(tlvData, tlvLength, outputDict)

# def animate(i, serial_port, scatter, outputDict):
#     read_and_parse_data(serial_port, outputDict)
#     pointCloud = outputDict['pointCloud']
#     num_points = outputDict['numDetectedPoints']
    
#     scatter.set_offsets(pointCloud[:num_points, :2])  # Set the X and Y data for 2D plot
#     return scatter,

# def main():
#     comport = 'COM7'
#     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
#     outputDict = {
#         'pointCloud': np.zeros((1000, 4)),
#         'numDetectedPoints': 0
#     }

#     fig, ax = plt.subplots()
#     scatter = ax.scatter([], [], c='b', marker='o', s=1)
#     ax.set_xlabel('X')
#     ax.set_ylabel('Y')
#     ax.set_title('Real-Time 2D Point Cloud')

#     ani = FuncAnimation(fig, animate, fargs=(serial.Serial(comport, baudrate=baudrate, timeout=1), scatter, outputDict), interval=100, blit=False)

#     plt.show()

# if __name__ == "__main__":
#     main()
