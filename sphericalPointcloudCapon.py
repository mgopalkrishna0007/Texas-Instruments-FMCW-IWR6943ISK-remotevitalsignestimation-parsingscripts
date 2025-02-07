# # sending config and accesing radar outputs 

# import struct
# import time
# import serial

# # Define the configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Define the CLI and Data serial ports
# cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
# dataSerialPort = 'COM7'  # Data port (change as per your setup)

# # Initialize serial connections
# cliDevice = serial.Serial(cliSerialPort, 115200, timeout=3.0)  # CLI port for sending configuration
# dataDevice = serial.Serial(dataSerialPort, 921600, timeout=3.0)  # Data port for receiving sensor data

# headerLength = 40  # Length of the header as specified in the protocol

# # Function to send configuration commands to the sensor
# def send_config_to_sensor(cliDevice, radarCfgFile):
#     """Send configuration commands to the mmWave sensor."""
#     print("Sending configuration commands to the sensor...")
#     cliDevice.write(('\r').encode())  # Initial command to clear buffer
#     with open(radarCfgFile, 'r') as file:
#         for line in file:
#             cliDevice.write(line.encode())
#             response = cliDevice.readline()
#             print(f"Sent: {line.strip()} | Response: {response.strip()}")
#             time.sleep(0.05)  # Brief pause to ensure command is processed
#     print("Configuration commands sent successfully.")
#     cliDevice.close()

# def tlvHeaderDecode(data):
#     tlvType, tlvLength = struct.unpack('2I', data)
#     return tlvType, tlvLength

# def parseDetectedObjects(data, tlvLength, numDetectedObj, frameNum):
#     """Parse detected objects from the data."""
#     pointCloud = ""
#     for i in range(numDetectedObj):
#         x, y, z, vel = struct.unpack('4f', data[16*i:16*i+16])
#         pointCloud += "%d, %07.3f, %07.3f, %07.3f, %07.3f\n" % (frameNum, x, y, z, vel)
#     return pointCloud

# # Function to read and save sensor data to CSV
# def read_sensor_data(dataDevice):
#     """Read and save sensor data to CSV file."""
#     print("Reading sensor data...")
#     filename = "/path/to/your/directory/sphericalpointcloudCapon.csv".format(ts=time.strftime("%Y%m%d-%H%M"))
#     with open(filename, "w", 1) as result:
#         result.write("FrameNum, X, Y, Z, Velocity\n")
#         try:
#             while True:
#                 header = dataDevice.read(headerLength)  # Read the header part
#                 if len(header) < headerLength:
#                     print("Incomplete header received. Skipping this data.")
#                     continue

#                 # Unpack the header to extract necessary information
#                 magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs, subFrameNum = struct.unpack('Q8I', header)

#                 # If the magic word is incorrect, attempt to realign the stream
#                 while magic != 506660481457717506:
#                     print("Bad magic word. Realigning data stream...")
#                     header = header[1:] + dataDevice.read(1)  # Shift and realign
#                     magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs, subFrameNum = struct.unpack('Q8I', header)

#                 print(f"FrameNum: {frameNum}, NumTLVs: {numTLVs}, NumObj: {numObj}")

#                 # Read the payload data based on length specified in the header
#                 data = dataDevice.read(length - headerLength)
                
#                 while data:
#                     # Parse TLVs
#                     for i in range(numTLVs):
#                         tlvType, tlvLength = tlvHeaderDecode(data[:8])
#                         data = data[8:]
#                         if tlvType == 1:  # Detected Objects
#                             framePointCloud = parseDetectedObjects(data, tlvLength, numObj, frameNum)
#                             result.write(framePointCloud)
                            
#                         # Skip over TLVs not currently being processed
#                         data = data[tlvLength:]
#         except KeyboardInterrupt:
#             print("Data reading stopped by user.")
#         finally:
#             dataDevice.close()

# # Send configuration to the sensor
# send_config_to_sensor(cliDevice, radarCfgFile)

# # Start reading data from the sensor
# read_sensor_data(dataDevice)




# the below code out puts - 
# FrameNum: 18, NumTLVs: 2, NumObj: 29
# Decoded TLV Header - Type: 1020, Length: 252
# Decoded TLV Header - Type: 1021, Length: 4
# FrameNum: 19, NumTLVs: 2, NumObj: 10
# Decoded TLV Header - Type: 1020, Length: 100
# Decoded TLV Header - Type: 1021, Length: 4

import struct
import time
import serial
import os

# Define the configuration file path
radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# Define the CLI and Data serial ports
cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
dataSerialPort = 'COM7'  # Data port (change as per your setup)

# Initialize serial connections
cliDevice = serial.Serial(cliSerialPort, 115200, timeout=3.0)  # CLI port for sending configuration
dataDevice = serial.Serial(dataSerialPort, 921600, timeout=3.0)  # Data port for receiving sensor data

headerLength = 40  # Length of the header as specified in the protocol

# Ensure the directory for saving CSV files exists
os.makedirs('/radarCSV', exist_ok=True)

# Function to send configuration commands to the sensor
def send_config_to_sensor(cliDevice, radarCfgFile):
    """Send configuration commands to the mmWave sensor."""
    print("Sending configuration commands to the sensor...")
    cliDevice.write(('\r').encode())  # Initial command to clear buffer
    with open(radarCfgFile, 'r') as file:
        for line in file:
            cliDevice.write(line.encode())
            response = cliDevice.readline()
            print(f"Sent: {line.strip()} | Response: {response.strip()}")
            time.sleep(0.05)  # Brief pause to ensure command is processed
    print("Configuration commands sent successfully.")
    cliDevice.close()

def tlvHeaderDecode(data):
    tlvType, tlvLength = struct.unpack('2I', data)
    print(f"Decoded TLV Header - Type: {tlvType}, Length: {tlvLength}")
    return tlvType, tlvLength

def parseDetectedObjects(data, tlvLength, numDetectedObj, frameNum):
    """Parse detected objects from the data."""
    pointCloud = ""
    print(f"Parsing {numDetectedObj} detected objects...")
    
    if len(data) < tlvLength:
        print(f"TLV data length mismatch. Expected: {tlvLength}, Got: {len(data)}")
        return pointCloud  # Return empty if there's a length mismatch

    for i in range(numDetectedObj):
        try:
            x, y, z, vel = struct.unpack('4f', data[16*i:16*i+16])
            pointCloud += "%d, %07.3f, %07.3f, %07.3f, %07.3f\n" % (frameNum, x, y, z, vel)
            # Print the details of each detected object
            print(f"Frame {frameNum}: Object {i+1} - X: {x:.3f}, Y: {y:.3f}, Z: {z:.3f}, Velocity: {vel:.3f}")
        except struct.error as e:
            print(f"Error parsing object {i+1}: {e}")
            break  # If there is an error in unpacking, exit the loop
    return pointCloud

# Function to read and save sensor data to CSV
def read_sensor_data(dataDevice):
    """Read and save sensor data to CSV file."""
    print("Reading sensor data...")
    # Save the CSV in the /radarCSV directory
    filename = "/radarCSV/sphericalpointcloudCapon_{ts}.csv".format(ts=time.strftime("%Y%m%d-%H%M"))
    with open(filename, "w", 1) as result:
        result.write("FrameNum, X, Y, Z, Velocity\n")
        try:
            while True:
                header = dataDevice.read(headerLength)  # Read the header part
                if len(header) < headerLength:
                    print("Incomplete header received. Skipping this data.")
                    continue

                # Unpack the header to extract necessary information
                magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs, subFrameNum = struct.unpack('Q8I', header)

                # If the magic word is incorrect, attempt to realign the stream
                while magic != 506660481457717506:
                    print("Bad magic word. Realigning data stream...")
                    header = header[1:] + dataDevice.read(1)  # Shift and realign
                    magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs, subFrameNum = struct.unpack('Q8I', header)

                print(f"FrameNum: {frameNum}, NumTLVs: {numTLVs}, NumObj: {numObj}")

                # Read the payload data based on length specified in the header
                data = dataDevice.read(length - headerLength)
                
                if len(data) < (length - headerLength):
                    print(f"Incomplete data payload. Expected: {length - headerLength}, Got: {len(data)}")
                    continue  # Skip if the data is incomplete
                
                # Parse TLVs
                offset = 0
                for i in range(numTLVs):
                    # Check if there are enough bytes left for TLV header
                    if offset + 8 > len(data):
                        print("Not enough data left for TLV header.")
                        break
                    
                    tlvType, tlvLength = tlvHeaderDecode(data[offset:offset+8])
                    offset += 8
                    
                    # Check if there are enough bytes left for the TLV payload
                    if offset + tlvLength > len(data):
                        print("Not enough data left for TLV payload.")
                        break
                    
                    if tlvType == 1:  # Detected Objects
                        framePointCloud = parseDetectedObjects(data[offset:offset+tlvLength], tlvLength, numObj, frameNum)
                        result.write(framePointCloud)
                    
                    # Move to the next TLV block
                    offset += tlvLength
        except KeyboardInterrupt:
            print("Data reading stopped by user.")
        finally:
            dataDevice.close()

# Send configuration to the sensor
send_config_to_sensor(cliDevice, radarCfgFile)

# Start reading data from the sensor
read_sensor_data(dataDevice)




# DECODES THE TLV 1020 , AND OUTPUTS THE OBJECTS IN ONE FRAME WITH THEIR COORIDNATES AND ALSO WEIRD VALUES

# import struct
# import time
# import serial

# # Define the configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Define the CLI and Data serial ports
# cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
# dataSerialPort = 'COM7'  # Data port (change as per your setup)

# # Initialize serial connections
# cliDevice = serial.Serial(cliSerialPort, 115200, timeout=3.0)  # CLI port for sending configuration
# dataDevice = serial.Serial(dataSerialPort, 921600, timeout=3.0)  # Data port for receiving sensor data

# headerLength = 40  # Length of the header as specified in the protocol

# # Function to send configuration commands to the sensor
# def send_config_to_sensor(cliDevice, radarCfgFile):
#     """Send configuration commands to the mmWave sensor."""
#     print("Sending configuration commands to the sensor...")
#     cliDevice.write(('\r').encode())  # Initial command to clear buffer
#     with open(radarCfgFile, 'r') as file:
#         for line in file:
#             cliDevice.write(line.encode())
#             response = cliDevice.readline()
#             print(f"Sent: {line.strip()} | Response: {response.strip()}")
#             time.sleep(0.05)  # Brief pause to ensure command is processed
#     print("Configuration commands sent successfully.")
#     cliDevice.close()

# def tlvHeaderDecode(data):
#     """Decode the TLV header to get the type and length."""
#     tlvType, tlvLength = struct.unpack('2I', data)
#     print(f"Decoded TLV Header - Type: {tlvType}, Length: {tlvLength}")
#     return tlvType, tlvLength

# def parseCompressedPointCloud(data, tlvType, tlvLength, frameNum):
#     """Parse compressed point cloud data from the TLV type 1020."""
#     pointCloud = ""
    
#     if tlvType == 1020:  # Compressed Point Cloud Data
#         numDetectedObj = (tlvLength - 8) // 16  # Assuming 4 floats (16 bytes) per detected object
        
#         print(f"Parsing {numDetectedObj} detected objects for TLV Type {tlvType}...")

#         # Ensure there is enough data to parse
#         if len(data) < tlvLength:
#             print(f"TLV data length mismatch. Expected: {tlvLength}, Got: {len(data)}")
#             return pointCloud  # Return empty if there's a length mismatch

#         # Decompress and parse point cloud data
#         for i in range(numDetectedObj):
#             try:
#                 # Assuming the compressed format is in 4 float values per detected object: x, y, z, and velocity
#                 x, y, z, vel = struct.unpack('4f', data[16*i:16*i+16])
#                 pointCloud += "%d, %07.3f, %07.3f, %07.3f, %07.3f\n" % (frameNum, x, y, z, vel)
#                 # Print the details of each detected object
#                 print(f"Frame {frameNum}: Object {i+1} - X: {x:.3f}, Y: {y:.3f}, Z: {z:.3f}, Velocity: {vel:.3f}")
#             except struct.error as e:
#                 print(f"Error parsing object {i+1}: {e}")
#                 break  # If there is an error in unpacking, exit the loop
#     else:
#         print(f"Unsupported TLV type {tlvType} for point cloud parsing. Skipping...")
    
#     return pointCloud

# # Function to read and save sensor data to CSV
# def read_sensor_data(dataDevice):
#     """Read and save sensor data to CSV file."""
#     print("Reading sensor data...")
#     filename = "/path/to/your/directory/sphericalpointcloudCapon.csv".format(ts=time.strftime("%Y%m%d-%H%M"))
#     with open(filename, "w", 1) as result:
#         result.write("FrameNum, X, Y, Z, Velocity\n")
#         try:
#             while True:
#                 header = dataDevice.read(headerLength)  # Read the header part
#                 if len(header) < headerLength:
#                     print("Incomplete header received. Skipping this data.")
#                     continue

#                 # Unpack the header to extract necessary information
#                 magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs, subFrameNum = struct.unpack('Q8I', header)

#                 # If the magic word is incorrect, attempt to realign the stream
#                 while magic != 506660481457717506:
#                     print("Bad magic word. Realigning data stream...")
#                     header = header[1:] + dataDevice.read(1)  # Shift and realign
#                     magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs, subFrameNum = struct.unpack('Q8I', header)

#                 print(f"FrameNum: {frameNum}, NumTLVs: {numTLVs}, NumObj: {numObj}")

#                 # Read the payload data based on length specified in the header
#                 data = dataDevice.read(length - headerLength)
                
#                 offset = 0
#                 for i in range(numTLVs):
#                     # Check if there are enough bytes left for TLV header
#                     if offset + 8 > len(data):
#                         print("Not enough data left for TLV header.")
#                         break

#                     tlvType, tlvLength = tlvHeaderDecode(data[offset:offset+8])
#                     offset += 8

#                     # Check if there are enough bytes left for the TLV payload
#                     if offset + tlvLength > len(data):
#                         print("Not enough data left for TLV payload.")
#                         break

#                     if tlvType == 1020:  # Compressed point cloud data
#                         framePointCloud = parseCompressedPointCloud(data[offset:offset+tlvLength], tlvType, tlvLength, frameNum)
#                         if framePointCloud:  # If point cloud data is found, write it
#                             result.write(framePointCloud)

#                     # Move to the next TLV block
#                     offset += tlvLength
#         except KeyboardInterrupt:
#             print("Data reading stopped by user.")
#         finally:
#             dataDevice.close()

# # Send configuration to the sensor
# send_config_to_sensor(cliDevice, radarCfgFile)

# # Start reading data from the sensor
# read_sensor_data(dataDevice)







# import struct
# import time
# import serial
# import numpy as np
# import logging
# import os

# # Local File Imports
# from parseTLVs import *
# from gui_common import *
# from tlv_defines import *

# # Initialize logging
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Define the configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Define the CLI and Data serial ports
# cliSerialPort = 'COM3'  # Command Line Interface (CLI) port
# dataSerialPort = 'COM7'  # Data port

# # Initialize serial connections
# cliDevice = serial.Serial(cliSerialPort, 115200, timeout=3.0)  # CLI port for sending configuration
# dataDevice = serial.Serial(dataSerialPort, 921600, timeout=3.0)  # Data port for receiving sensor data

# headerLength = 40  # Length of the header as specified in the protocol

# def send_config_to_sensor(cliDevice, radarCfgFile):
#     """Send configuration commands to the mmWave sensor."""
#     print("Sending configuration commands to the sensor...")
#     cliDevice.write(('\r').encode())  # Initial command to clear buffer
#     with open(radarCfgFile, 'r') as file:
#         for line in file:
#             cliDevice.write(line.encode())
#             response = cliDevice.readline()
#             print(f"Sent: {line.strip()} | Response: {response.strip()}")
#             time.sleep(0.05)  # Brief pause to ensure command is processed
#     print("Configuration commands sent successfully.")
#     cliDevice.close()

# def parseStandardFrame(frameData):
#     # Constants for parsing frame header
#     headerStruct = 'Q8I'
#     frameHeaderLen = struct.calcsize(headerStruct)
#     tlvHeaderLength = 8

#     # Define the function's output structure and initialize error field to no error
#     outputDict = {}
#     outputDict['error'] = 0

#     # A sum to track the frame packet length for verification
#     totalLenCheck = 0   

#     # Read in frame Header
#     try:
#         magic, version, totalPacketLen, platform, frameNum, timeCPUCycles, numDetectedObj, numTLVs, subFrameNum = struct.unpack(headerStruct, frameData[:frameHeaderLen])
#     except Exception as e:
#         log.error(f'Error: Could not read frame header - {e}')
#         outputDict['error'] = 1

#     # Move frameData ptr to start of 1st TLV   
#     frameData = frameData[frameHeaderLen:]
#     totalLenCheck += frameHeaderLen

#     # Save frame number to output
#     outputDict['frameNum'] = frameNum

#     # Initialize the point cloud struct
#     outputDict['pointCloud'] = np.zeros((numDetectedObj, 7), np.float64)
#     outputDict['pointCloud'][:, 6] = 255

#     # Find and parse all TLVs
#     for i in range(numTLVs):
#         try:
#             tlvType, tlvLength = tlvHeaderDecode(frameData[:tlvHeaderLength])
#             frameData = frameData[tlvHeaderLength:]
#             totalLenCheck += tlvHeaderLength
#         except Exception as e:
#             log.warning(f'TLV Header Parsing Failure: Ignored frame due to parsing error - {e}')
#             outputDict['error'] = 2
#             return {}

#         if tlvType in parserFunctions:
#             parserFunctions[tlvType](frameData[:tlvLength], tlvLength, outputDict)
#         elif tlvType in unusedTLVs:
#             log.debug(f"No function to parse TLV type: {tlvType}")
#         else:
#             log.info(f"Invalid TLV type: {tlvType}")

#         frameData = frameData[tlvLength:]
#         totalLenCheck += tlvLength
    
#     totalLenCheck = 32 * math.ceil(totalLenCheck / 32)

#     if totalLenCheck != totalPacketLen:
#         log.warning('Frame packet length read is not equal to totalPacketLen in frame header. Subsequent frames may be dropped.')
#         outputDict['error'] = 3

#     return outputDict

# def read_sensor_data(dataDevice):
#     """Read and save sensor data to CSV file."""
#     print("Reading sensor data...")
#     filename = os.path.join(os.path.expanduser("~"), "sphericalpointcloud.csv")
#     with open(filename, "w", 1) as result:
#         result.write("FrameNum, X, Y, Z, Velocity\n")
#         try:
#             while True:
#                 header = dataDevice.read(headerLength)  # Read the header part
#                 if len(header) < headerLength:
#                     print("Incomplete header received. Skipping this data.")
#                     continue

#                 # Unpack the header to extract necessary information
#                 magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs, subFrameNum = struct.unpack('Q8I', header)

#                 while magic != 506660481457717506:
#                     print("Bad magic word. Realigning data stream...")
#                     header = header[1:] + dataDevice.read(1)
#                     magic, version, length, platform, frameNum, cpuCycles, numObj, numTLVs, subFrameNum = struct.unpack('Q8I', header)

#                 print(f"FrameNum: {frameNum}, NumTLVs: {numTLVs}, NumObj: {numObj}")

#                 # Read the payload data based on length specified in the header
#                 data = dataDevice.read(length - headerLength)
                
#                 while data:
#                     frameData = data
#                     outputDict = parseStandardFrame(frameData)
#                     if 'pointCloud' in outputDict:
#                         for point in outputDict['pointCloud']:
#                             result.write(f"{int(outputDict['frameNum'])}, {point[0]:07.3f}, {point[1]:07.3f}, {point[2]:07.3f}, {point[3]:07.3f}\n")
#                     # Move to next data chunk
#                     data = data[frameData.size:]
#         except KeyboardInterrupt:
#             print("Data reading stopped by user.")
#         finally:
#             dataDevice.close()

# # Send configuration to the sensor
# send_config_to_sensor(cliDevice, radarCfgFile)

# # Start reading data from the sensor
# read_sensor_data(dataDevice)
