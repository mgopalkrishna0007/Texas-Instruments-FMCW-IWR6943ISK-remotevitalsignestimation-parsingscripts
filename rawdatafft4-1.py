# # GIVES HEX RAW DATA OUTPUT 

# import serial
# import numpy as np

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 40  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE

# def read_and_parse_data(serial_port):
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 # Parse header - you might need to adjust this according to your format
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process data - update this with your actual data processing
#                     print(f"Data Received: {data}")

# def main():
#     comport = 'COM7'
#     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
#     try:
#         serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
#         print(f"Connected to {comport} at {baudrate} baud rate.")
        
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


#####################################################################################################################################
#####################################################################################################################################


# reads visualizer raw serial data 

# import time
# import serial
# import logging
# import signal
# import sys

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 40  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE

# # Define the configuration file path
# radarCfgFile = r'C:\Users\GOPAL\Downloads\xwr68xx_profile_2024_09_02T18_52_17_362.cfg'

# # c:\Users\GOPAL\Downloads\xwr68xx_profile_2024_09_02T18_52_17_362.cfg
# # Define the CLI and Data serial ports
# cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
# dataSerialPort = 'COM7'  # Data port (change as per your setup)

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

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

# def read_and_print_data(dataDevice):
#     byte_buffer = bytearray()
    
#     while True:
#         if dataDevice.in_waiting > 0:
#             byte_buffer.extend(dataDevice.read(dataDevice.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Print raw data in hexadecimal format
#                     print(f"Raw Data: {data.hex()}")

# def signal_handler(sig, frame):
#     print("\nTerminating...")
#     sys.exit(0)

# def main():
#     # Register signal handler for termination
#     signal.signal(signal.SIGINT, signal_handler)
#     signal.signal(signal.SIGTERM, signal_handler)
    
#     try:
#         # Initialize serial connections
#         cliDevice = serial.Serial(cliSerialPort, 115200, timeout=3.0)  # CLI port for sending configuration
#         dataDevice = serial.Serial(dataSerialPort, 921600, timeout=3.0)  # Data port for receiving sensor data
        
#         # Send configuration to the sensor
#         send_config_to_sensor(cliDevice, radarCfgFile)
        
#         # Start reading and printing raw data from the sensor
#         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
#         read_and_print_data(dataDevice)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'dataDevice' in locals() and dataDevice.is_open:
#             dataDevice.close()
#         print("Serial port closed.")

# if __name__ == "__main__":
#     main()


#####################################################################################################################################
#####################################################################################################################################



# import time
# import serial
# import logging
# import signal
# import sys
# import struct
# import math
# import binascii
# import codecs

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE

# # Define the configuration file path
# radarCfgFile = r'C:\Users\GOPAL\Downloads\xwr68xx_profile_2024_09_02T18_52_17_362.cfg'

# # Define the CLI and Data serial ports
# cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
# dataSerialPort = 'COM7'  # Data port (change as per your setup)

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

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
#     """Decode the TLV header and print the TLV type and length."""
#     tlvType, tlvLength = struct.unpack('2I', data)
#     print(f"Decoded TLV Header - Type: {tlvType}, Length: {tlvLength}")
#     return tlvType, tlvLength


# def getUint32(data):
#     """Convert 4 bytes to a 32-bit unsigned integer."""
#     return (data[0] +
#             data[1]*256 +
#             data[2]*65536 +
#             data[3]*16777216)

# def getUint16(data):
#     """Convert 2 bytes to a 16-bit unsigned integer."""
#     return (data[0] +
#             data[1]*256)

# def getHex(data):
#     """Convert 4 bytes to a 32-bit unsigned integer in hex."""
#     return (binascii.hexlify(data[::-1]))

# def checkMagicPattern(data):
#     """Check if the data array contains the magic pattern indicating the start of an mmw demo output packet."""
#     if (data[0] == 2 and data[1] == 1 and data[2] == 4 and data[3] == 3 and data[4] == 6 and data[5] == 5 and data[6] == 8 and data[7] == 7):
#         return 1
#     return 0
          
# def parser_helper(data, readNumBytes):
#     """Helper function to parse the mmw demo output packet and extract header information."""
#     headerStartIndex = -1

#     for index in range(readNumBytes):
#         if checkMagicPattern(data[index:index+8:1]) == 1:
#             headerStartIndex = index
#             break
  
#     if headerStartIndex == -1:
#         # Unable to find the magic number, return default error values
#         return -1, -1, -1, -1, -1
    
#     # Extract header and packet information
#     totalPacketNumBytes = getUint32(data[headerStartIndex+12:headerStartIndex+16:1])
#     numDetObj = getUint32(data[headerStartIndex+28:headerStartIndex+32:1])
#     numTlv = getUint32(data[headerStartIndex+32:headerStartIndex+36:1])
#     subFrameNumber = getUint32(data[headerStartIndex+36:headerStartIndex+40:1])
    
#     print("headerStartIndex    = %d" % (headerStartIndex))
#     print("totalPacketNumBytes = %d" % (totalPacketNumBytes))
#     print("numDetObj           = %d" % (numDetObj)) 
#     print("numTlv              = %d" % (numTlv))
#     print("subFrameNumber      = %d" % (subFrameNumber))
    
#     return headerStartIndex, totalPacketNumBytes, numDetObj, numTlv, subFrameNumber

# def parser_one_mmw_demo_output_packet(data, readNumBytes):
#     """Main parser function to extract packet data including detected objects and other information."""
#     headerNumBytes = 40
#     PI = 3.14159265

#     detectedX_array = []
#     detectedY_array = []
#     detectedZ_array = []
#     detectedV_array = []
#     detectedRange_array = []
#     detectedAzimuth_array = []
#     detectedElevAngle_array = []
#     detectedSNR_array = []
#     detectedNoise_array = []

#     # Call helper function to parse packet header
#     (headerStartIndex, totalPacketNumBytes, numDetObj, numTlv, subFrameNumber) = parser_helper(data, readNumBytes)

#     if headerStartIndex == -1:
#         print("************ Frame Fail, cannot find the magic words *****************")
#         return 1, headerStartIndex, totalPacketNumBytes, numDetObj, numTlv, subFrameNumber, detectedX_array, detectedY_array, detectedZ_array, detectedV_array, detectedRange_array, detectedAzimuth_array, detectedElevAngle_array, detectedSNR_array, detectedNoise_array

#     nextHeaderStartIndex = headerStartIndex + totalPacketNumBytes

#     if headerStartIndex + totalPacketNumBytes > readNumBytes:
#         print("********** Frame Fail, readNumBytes may not be long enough ***********")
#         return 1, headerStartIndex, totalPacketNumBytes, numDetObj, numTlv, subFrameNumber, detectedX_array, detectedY_array, detectedZ_array, detectedV_array, detectedRange_array, detectedAzimuth_array, detectedElevAngle_array, detectedSNR_array, detectedNoise_array

#     # Update TLV header parsing
#     tlvStart = headerStartIndex + headerNumBytes
#     tlvType, tlvLen = tlvHeaderDecode(data[tlvStart:tlvStart+8])
#     offset = 8

#     if tlvType == 1 and tlvLen < totalPacketNumBytes:
#         for obj in range(numDetObj):
#             x = struct.unpack('<f', data[tlvStart + offset:tlvStart + offset+4])[0]
#             y = struct.unpack('<f', data[tlvStart + offset+4:tlvStart + offset+8])[0]
#             z = struct.unpack('<f', data[tlvStart + offset+8:tlvStart + offset+12])[0]
#             v = struct.unpack('<f', data[tlvStart + offset+12:tlvStart + offset+16])[0]
#             detectedX_array.append(x)
#             detectedY_array.append(y)
#             detectedZ_array.append(z)
#             detectedV_array.append(v)
#             detectedRange_array.append(math.sqrt(x**2 + y**2 + z**2))
#             detectedAzimuth_array.append(math.atan2(x, y) * 180 / PI)
#             detectedElevAngle_array.append(math.atan2(z, math.sqrt(x**2 + y**2)) * 180 / PI)
#             offset += 16
    
#     tlvStart += 8 + tlvLen
#     tlvType, tlvLen = tlvHeaderDecode(data[tlvStart:tlvStart+8])
#     offset = 8

#     if tlvType == 7:
#         for obj in range(numDetObj):
#             snr = getUint16(data[tlvStart + offset:tlvStart + offset+2])
#             noise = getUint16(data[tlvStart + offset+2:tlvStart + offset+4])
#             detectedSNR_array.append(snr)
#             detectedNoise_array.append(noise)
#             offset += 4
    
#     print("                  x(m)         y(m)         z(m)        v(m/s)    Range(m)  Azimuth(deg)  ElevAngle(deg)  SNR(0.1dB)  Noise(0.1dB)")
#     for obj in range(numDetObj):
#         print("    obj%3d: %12f %12f %12f %12f %12f %12f %12f %12d %12d" % (obj, detectedX_array[obj], detectedY_array[obj], detectedZ_array[obj], detectedV_array[obj], detectedRange_array[obj], detectedAzimuth_array[obj], detectedElevAngle_array[obj], detectedSNR_array[obj], detectedNoise_array[obj]))

#     return 0, headerStartIndex, totalPacketNumBytes, numDetObj, numTlv, subFrameNumber, detectedX_array, detectedY_array, detectedZ_array, detectedV_array, detectedRange_array, detectedAzimuth_array, detectedElevAngle_array, detectedSNR_array, detectedNoise_array

# def read_and_parse_data(dataDevice):
#     """Read and parse raw data from the sensor."""
#     byte_buffer = bytearray()
    
#     while True:
#         if dataDevice.in_waiting > 0:
#             byte_buffer.extend(dataDevice.read(dataDevice.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 result, headerStartIndex, totalPacketNumBytes, numDetObj, numTlv, subFrameNumber, detectedX_array, detectedY_array, detectedZ_array, detectedV_array, detectedRange_array, detectedAzimuth_array, detectedElevAngle_array, detectedSNR_array, detectedNoise_array = parser_one_mmw_demo_output_packet(byte_buffer, len(byte_buffer))
                
#                 if result == 0:
#                     # If parsing was successful, clear the buffer up to the next header
#                     byte_buffer = byte_buffer[headerStartIndex + totalPacketNumBytes:]
#                 else:
#                     # If parsing failed, clear the buffer to try again
#                     byte_buffer = byte_buffer[headerStartIndex:]
#             else:
#                 time.sleep(0.1)

# def signal_handler(sig, frame):
#     """Handle signal interrupt."""
#     print('Exiting gracefully...')
#     sys.exit(0)

# def main():
#     """Main function to set up serial ports and start reading data."""
#     signal.signal(signal.SIGINT, signal_handler)

#     # Open CLI serial port
#     cliDevice = serial.Serial(cliSerialPort, 115200)
    
#     # Send configuration to sensor
#     send_config_to_sensor(cliDevice, radarCfgFile)
    
#     # Open Data serial port
#     dataDevice = serial.Serial(dataSerialPort, 921600)

#     try:
#         # Start reading and parsing data
#         read_and_parse_data(dataDevice)
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         dataDevice.close()

# if __name__ == "__main__":
#     main()


###################################################################################################################################
###################################################################################################################################


# this code out puts the visualiser data frame wise 

import struct
import time
import serial
import logging
import signal
import sys
import math

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 40  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE

# Define the configuration file path
radarCfgFile = r'C:\Users\GOPAL\Downloads\xwr68xx_profile_2024_09_03T12_08_49_816.cfg'

# Define the CLI and Data serial ports
cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
dataSerialPort = 'COM7'  # Data port (change as per your setup)

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

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
    """Decodes the TLV header to get the TLV type and length."""
    tlvType, tlvLength = struct.unpack('2I', data)
    return tlvType, tlvLength

def parseDetectedObjects(data, tlvLength):
    """Parses detected objects from the TLV section."""
    try:
        numDetectedObj, xyzQFormat = struct.unpack('2H', data[:4])
        print("\tDetected Objects: %d " % numDetectedObj)
        if numDetectedObj == 0:
            return  # No objects to parse

        objectSize = 12  # Size of each detected object in bytes
        for i in range(numDetectedObj):
            start = 4 + i * objectSize
            if start + objectSize > len(data):
                print(f"Insufficient data for object {i}, expected {objectSize} bytes but found {len(data) - start}")
                break

            rangeIdx, dopplerIdx, peakVal, x, y, z = struct.unpack('3H3h', data[start:start + objectSize])
            print(f"\tObject ID: {i}")
            print(f"\t\tDoppler Index: {dopplerIdx}")
            print(f"\t\tRange Index: {rangeIdx}")
            print(f"\t\tPeak Value: {peakVal}")
            print(f"\t\tX: {x}, Y: {y}, Z: {z} (Raw)")

            # Converting to float and handling overflow
            try:
                x_float = x * 1.0 / (1 << xyzQFormat)
                y_float = y * 1.0 / (1 << xyzQFormat)
                z_float = z * 1.0 / (1 << xyzQFormat)
                print(f"\t\tX: {x_float:.3f}, Y: {y_float:.3f}, Z: {z_float:.3f}")

                # Calculate range
                range_m = math.sqrt(x_float ** 2 + y_float ** 2)
                print(f"\t\tRange: {range_m:.3f}m")
            except OverflowError as e:
                print(f"\t\tOverflow error: {e}, skipping object.")
    except struct.error as e:
        print("Error unpacking detected objects:", e)
    except Exception as e:
        print("Unexpected error while parsing detected objects:", e)

def parseRangeProfile(data, tlvLength):
    """Parses the range profile from the TLV section."""
    for i in range(tlvLength // 2):  # Assuming each range profile entry is 2 bytes
        rangeProfile = struct.unpack('H', data[2 * i:2 * i + 2])[0]
        print("\tRange Profile[%d]: %07.3f" % (i, rangeProfile * 1.0 * 6 / 8 / (1 << 8)))  # Adjust scaling as per radar specification

def parseStats(data, tlvLength):
    """Parses the statistics from the TLV section."""
    interProcess, transmitOut, frameMargin, chirpMargin, activeCPULoad, interCPULoad = struct.unpack('6I', data[:24])
    print("\tOutput Message Stats:")
    print("\t\tChirp Margin: %d " % chirpMargin)
    print("\t\tFrame Margin: %d " % frameMargin)
    print("\t\tInter CPU Load: %d " % interCPULoad)
    print("\t\tActive CPU Load: %d " % activeCPULoad)
    print("\t\tTransmit Out: %d " % transmitOut)
    print("\t\tInterprocess: %d " % interProcess)

def parseTLVs(data):
    """Parses the TLV sections from the raw data."""
    offset = 0
    while offset < len(data):
        try:
            tlvType, tlvLength = tlvHeaderDecode(data[offset:offset + 8])
            offset += 8
            tlvData = data[offset:offset + tlvLength]
            offset += tlvLength
            
            print("TLV Type:", tlvType)
            print("TLV Length:", tlvLength)
            
            if tlvType == 1:  # Example: Detected Objects
                parseDetectedObjects(tlvData, tlvLength)
            elif tlvType == 2:  # Example: Range Profile
                parseRangeProfile(tlvData, tlvLength)
            elif tlvType == 6:  # Example: Stats
                parseStats(tlvData, tlvLength)
            else:
                print("\tUnknown TLV Type:", tlvType)
        except struct.error as e:
            print("Error parsing TLV:", e)
            break

def parsePacket(packet):
    """Parses an entire packet starting from the magic number."""
    header = packet[:HEADER_SIZE]
    magic, version, totalPacketLength, platform, frameNum, cpuCycles, numObj, numTLVs = struct.unpack('Q7I', header[:36])
    
    print("Packet Frame Number:", frameNum)
    print("Packet Version:", hex(version))
    print("Number of TLVs:", numTLVs)
    
    data = packet[HEADER_SIZE:totalPacketLength]
    parseTLVs(data)

def read_and_print_data(dataDevice):
    """Reads data from the radar device and parses it in real-time."""
    byte_buffer = bytearray()
    magicWord = b'\x02\x01\x04\x03\x06\x05\x08\x07'  # Replace with your radar's actual magic word
    
    while True:
        if dataDevice.in_waiting > 0:
            byte_buffer.extend(dataDevice.read(dataDevice.in_waiting))
            
            # Check for the presence of the magic word
            magicWordIdx = byte_buffer.find(magicWord)
            if magicWordIdx != -1 and len(byte_buffer) > EXPECTED_HEADER_SIZE:
                header = byte_buffer[magicWordIdx:magicWordIdx + HEADER_SIZE]
                total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
                if len(byte_buffer) >= magicWordIdx + total_packet_length:
                    # Extract a complete packet from the buffer
                    data = byte_buffer[magicWordIdx:magicWordIdx + total_packet_length]
                    byte_buffer = byte_buffer[magicWordIdx + total_packet_length:]
                    
                    # Parse the extracted packet
                    parsePacket(data)

def signal_handler(sig, frame):
    print("\nTerminating...")
    sys.exit(0)

def main():
    # Register signal handler for termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize serial connections
        cliDevice = serial.Serial(cliSerialPort, 115200, timeout=3.0)  # CLI port for sending configuration
        dataDevice = serial.Serial(dataSerialPort, 921600, timeout=3.0)  # Data port for receiving sensor data
        
        # Send configuration to the sensor
        send_config_to_sensor(cliDevice, radarCfgFile)
        
        # Start reading and printing raw data from the sensor
        print(f"Connected to {dataSerialPort} at 921600 baud rate.")
        read_and_print_data(dataDevice)

    except serial.SerialException as e:
        print(f"SerialException: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'dataDevice' in locals() and dataDevice.is_open:
            dataDevice.close()
        print("Serial port closed.")

if __name__ == "__main__":
    main()


###################################################################################################################################
###################################################################################################################################


#this code out puts the range profile for a given frame 

# import struct
# import time
# import serial
# import logging
# import signal
# import sys

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 40  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE

# # Define the configuration file path
# radarCfgFile = r'C:\Users\GOPAL\Downloads\xwr68xx_profile_2024_09_02T18_52_17_362.cfg'

# # Define the CLI and Data serial ports
# cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
# dataSerialPort = 'COM7'  # Data port (change as per your setup)

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

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
#     """Decodes the TLV header to get the TLV type and length."""
#     tlvType, tlvLength = struct.unpack('2I', data)
#     return tlvType, tlvLength

# def parseRangeProfile(data, tlvLength):
#     """Parses the range profile from the TLV section."""
#     print("Range Profile Data:")
#     for i in range(tlvLength // 2):  # Assuming each range profile entry is 2 bytes
#         rangeProfile = struct.unpack('H', data[2 * i:2 * i + 2])[0]
#         print(f"Range Profile[{i}]: {rangeProfile * 1.0 * 6 / 8 / (1 << 8):07.3f}")  # Adjust scaling as per radar specification

# def parseTLVs(data):
#     """Parses the TLV sections from the raw data."""
#     offset = 0
#     while offset < len(data):
#         try:
#             tlvType, tlvLength = tlvHeaderDecode(data[offset:offset + 8])
#             offset += 8
#             tlvData = data[offset:offset + tlvLength]
#             offset += tlvLength
            
#             if tlvType == 2:  # TLV Type for Range Profile
#                 parseRangeProfile(tlvData, tlvLength)
#         except struct.error as e:
#             print("Error parsing TLV:", e)
#             break

# def parsePacket(packet):
#     """Parses an entire packet starting from the magic number."""
#     header = packet[:HEADER_SIZE]
#     magic, version, totalPacketLength, platform, frameNum, cpuCycles, numObj, numTLVs = struct.unpack('Q7I', header[:36])
    
#     print(f"Packet Frame Number: {frameNum}")
    
#     data = packet[HEADER_SIZE:totalPacketLength]
#     parseTLVs(data)

# def read_and_print_data(dataDevice):
#     """Reads data from the radar device and parses it in real-time."""
#     byte_buffer = bytearray()
#     magicWord = b'\x02\x01\x04\x03\x06\x05\x08\x07'  # Replace with your radar's actual magic word
    
#     while True:
#         if dataDevice.in_waiting > 0:
#             byte_buffer.extend(dataDevice.read(dataDevice.in_waiting))
            
#             # Check for the presence of the magic word
#             magicWordIdx = byte_buffer.find(magicWord)
#             if magicWordIdx != -1 and len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 header = byte_buffer[magicWordIdx:magicWordIdx + HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= magicWordIdx + total_packet_length:
#                     # Extract a complete packet from the buffer
#                     data = byte_buffer[magicWordIdx:magicWordIdx + total_packet_length]
#                     byte_buffer = byte_buffer[magicWordIdx + total_packet_length:]
                    
#                     # Parse the extracted packet
#                     parsePacket(data)

# def signal_handler(sig, frame):
#     print("\nTerminating...")
#     sys.exit(0)

# def main():
#     # Register signal handler for termination
#     signal.signal(signal.SIGINT, signal_handler)
#     signal.signal(signal.SIGTERM, signal_handler)
    
#     try:
#         # Initialize serial connections
#         cliDevice = serial.Serial(cliSerialPort, 115200, timeout=3.0)  # CLI port for sending configuration
#         dataDevice = serial.Serial(dataSerialPort, 921600, timeout=3.0)  # Data port for receiving sensor data
        
#         # Send configuration to the sensor
#         send_config_to_sensor(cliDevice, radarCfgFile)
        
#         # Start reading and printing raw data from the sensor
#         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
#         read_and_print_data(dataDevice)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'dataDevice' in locals() and dataDevice.is_open:
#             dataDevice.close()
#         print("Serial port closed.")

# if __name__ == "__main__":
#     main()
