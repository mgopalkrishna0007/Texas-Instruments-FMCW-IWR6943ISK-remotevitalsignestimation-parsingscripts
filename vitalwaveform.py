
# #  this code outputs the vitals serial data

# # import serial
# # import numpy as np
# # import struct
# # import logging
# # import time
# # import signal

# # # Configuration file path
# # radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # # Serial port names for CLI and Data ports
# # cliSerialPort = 'COM3'  # CLI port for sending configuration
# # dataSerialPort = 'COM7'  # Data port for receiving sensor data

# # # Define sizes for header and packet (update these sizes based on your radar data format)
# # HEADER_SIZE = 32  # Example size, replace with actual header size
# # EXPECTED_HEADER_SIZE = HEADER_SIZE
# # MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # # Initialize logger
# # logging.basicConfig(level=logging.DEBUG)
# # log = logging.getLogger(__name__)

# # def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
# #     """Parse the TLV data for vital signs."""
# #     vitalsStruct = '2H33f'
# #     vitalsSize = struct.calcsize(vitalsStruct)
    
# #     # Initialize struct in case of error
# #     vitalsOutput = {}
# #     vitalsOutput['id'] = 999
# #     vitalsOutput['rangeBin'] = 0
# #     vitalsOutput['breathDeviation'] = 0
# #     vitalsOutput['heartRate'] = 0
# #     vitalsOutput['breathRate'] = 0
# #     vitalsOutput['heartWaveform'] = []
# #     vitalsOutput['breathWaveform'] = []

# #     # Capture data for active patient
# #     try:
# #         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
# #     except:
# #         log.error('ERROR: Vitals TLV Parsing Failed')
# #         outputDict['vitals'] = vitalsOutput
# #         return

# #     # Parse this patient's data
# #     vitalsOutput['id'] = vitalsData[0]
# #     vitalsOutput['rangeBin'] = vitalsData[1]
# #     vitalsOutput['breathDeviation'] = vitalsData[2]
# #     vitalsOutput['heartRate'] = vitalsData[3]
# #     vitalsOutput['breathRate'] = vitalsData[4]
# #     vitalsOutput['heartWaveform'] = np.asarray(vitalsData[5:20])
# #     vitalsOutput['breathWaveform'] = np.asarray(vitalsData[20:35])

# #     # Advance tlv data pointer to end of this TLV
# #     tlvData = tlvData[vitalsSize:]
# #     outputDict['vitals'] = vitalsOutput

# # def read_and_parse_data(serial_port):
# #     """Read and parse data from the serial port."""
# #     byte_buffer = bytearray()
    
# #     while True:
# #         if serial_port.in_waiting > 0:
# #             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
# #             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
# #                 # Example parsing logic
# #                 header = byte_buffer[:HEADER_SIZE]
# #                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
# #                 if len(byte_buffer) >= total_packet_length:
# #                     data = byte_buffer[:total_packet_length]
# #                     byte_buffer = byte_buffer[total_packet_length:]
                    
# #                     # Process TLV data
# #                     process_tlv_data(data)

# # def process_tlv_data(data):
# #     """Process TLV data from the radar sensor."""
# #     # Define TLV header size and initialize parsing
# #     tlv_header_size = 8
# #     tlv_data = data[HEADER_SIZE:]
    
# #     outputDict = {}
    
# #     while len(tlv_data) > tlv_header_size:
# #         try:
# #             # Decode TLV header
# #             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
# #             tlv_data = tlv_data[tlv_header_size:]
            
# #             # Parse TLV data based on type
# #             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
# #                 parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength, outputDict)
            
# #             # Move to next TLV
# #             tlv_data = tlv_data[tlvLength:]
        
# #         except Exception as e:
# #             log.error(f'Failed to process TLV data: {e}')
# #             break
    
# #     # Output parsed data (for demonstration purposes)
# #     if 'vitals' in outputDict:
# #         print(f"Parsed Vital Signs: {outputDict['vitals']}")

# # def send_config_to_sensor(cliDevice, radarCfgFile):
# #     """Send configuration commands to the mmWave sensor."""
# #     print("Sending configuration commands to the sensor...")
# #     cliDevice.write(('\r').encode())  # Initial command to clear buffer
# #     with open(radarCfgFile, 'r') as file:
# #         for line in file:
# #             cliDevice.write(line.encode())
# #             response = cliDevice.readline()
# #             print(f"Sent: {line.strip()} | Response: {response.strip()}")
# #             time.sleep(0.05)  # Brief pause to ensure command is processed
# #     print("Configuration commands sent successfully.")
# #     cliDevice.close()

# # def signal_handler(sig, frame):
# #     """Handle termination signals to clean up and close serial ports."""
# #     print("\nTermination signal received. Cleaning up...")
# #     if 'dataDevice' in locals() and dataDevice.is_open:
# #         dataDevice.close()
# #     if 'cliDevice' in locals() and cliDevice.is_open:
# #         cliDevice.close()
# #     print("Serial ports closed.")
# #     exit(0)

# # def main():
# #     # Register signal handler for termination
# #     signal.signal(signal.SIGINT, signal_handler)
# #     signal.signal(signal.SIGTERM, signal_handler)
    
# #     try:
# #         # Initialize serial connections
# #         cliDevice = serial.Serial(cliSerialPort, 115200, timeout=3.0)  # CLI port for sending configuration
# #         dataDevice = serial.Serial(dataSerialPort, 921600, timeout=3.0)  # Data port for receiving sensor data
        
# #         # Send configuration to the sensor
# #         send_config_to_sensor(cliDevice, radarCfgFile)
        
# #         # Start reading data from the sensor
# #         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
# #         read_and_parse_data(dataDevice)

# #     except serial.SerialException as e:
# #         print(f"SerialException: {e}")
# #     except Exception as e:
# #         print(f"An unexpected error occurred: {e}")
# #     finally:
# #         if 'dataDevice' in locals() and dataDevice.is_open:
# #             dataDevice.close()
# #         if 'cliDevice' in locals() and cliDevice.is_open:
# #             cliDevice.close()
# #         print("Serial ports closed.")

# # if __name__ == "__main__":
# #     main()



####################################################################################################################################
####################################################################################################################################



# # this code only outputs the heartwaveform and breathwaveform

# import serial
# import numpy as np
# import struct
# import logging
# import time
# import signal

# # Configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Serial port names for CLI and Data ports
# cliSerialPort = 'COM3'  # CLI port for sending configuration
# dataSerialPort = 'COM7'  # Data port for receiving sensor data

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# def parseVitalSignsTLV(tlvData, tlvLength):
#     """Parse the TLV data for heart and breath waveforms."""
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize empty arrays for output
#     heartWaveform = []
#     breathWaveform = []

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#     except:
#         log.error('ERROR: Vitals TLV Parsing Failed')
#         return heartWaveform, breathWaveform

#     # Extract heartWaveform and breathWaveform
#     heartWaveform = np.asarray(vitalsData[5:20])
#     breathWaveform = np.asarray(vitalsData[20:35])

#     return heartWaveform, breathWaveform

# def read_and_parse_data(serial_port):
#     """Read and parse data from the serial port."""
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def process_tlv_data(data):
#     """Process TLV data from the radar sensor."""
#     # Define TLV header size and initialize parsing
#     tlv_header_size = 8
#     tlv_data = data[HEADER_SIZE:]
    
#     while len(tlv_data) > tlv_header_size:
#         try:
#             # Decode TLV header
#             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
#             tlv_data = tlv_data[tlv_header_size:]
            
#             # Parse TLV data based on type
#             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
#                 heartWaveform, breathWaveform = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
#                 # Print the extracted heartWaveform and breathWaveform
#                 print(f"Heart Waveform: {heartWaveform}")
#                 print(f"Breath Waveform: {breathWaveform}")
            
#             # Move to next TLV
#             tlv_data = tlv_data[tlvLength:]
        
#         except Exception as e:
#             log.error(f'Failed to process TLV data: {e}')
#             break

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

# def signal_handler(sig, frame):
#     """Handle termination signals to clean up and close serial ports."""
#     print("\nTermination signal received. Cleaning up...")
#     if 'dataDevice' in locals() and dataDevice.is_open:
#         dataDevice.close()
#     if 'cliDevice' in locals() and cliDevice.is_open:
#         cliDevice.close()
#     print("Serial ports closed.")
#     exit(0)

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
        
#         # Start reading data from the sensor
#         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
#         read_and_parse_data(dataDevice)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'dataDevice' in locals() and dataDevice.is_open:
#             dataDevice.close()
#         if 'cliDevice' in locals() and cliDevice.is_open:
#             cliDevice.close()
#         print("Serial ports closed.")

# if __name__ == "__main__":
#     main()


#####################################################################################################################################
#####################################################################################################################################


# this code saves the waveforms in a csv file. along with timestamps 

import serial
import numpy as np
import struct
import logging
import time
import signal
import csv
from datetime import datetime

# Configuration file path
radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# Serial port names for CLI and Data ports
cliSerialPort = 'COM3'  # CLI port for sending configuration
dataSerialPort = 'COM7'  # Data port for receiving sensor data

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 32  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE
MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# CSV file path
csv_file_path = r'C:\\path\\to\\your\\directory\\vitalwaveLL.csv'

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def parseVitalSignsTLV(tlvData, tlvLength):
    """Parse the TLV data for heart and breath waveforms."""
    vitalsStruct = '2H33f'
    vitalsSize = struct.calcsize(vitalsStruct)
    
    # Initialize empty arrays for output
    heartWaveform = []
    breathWaveform = []

    # Capture data for active patient
    try:
        vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
    except:
        log.error('ERROR: Vitals TLV Parsing Failed')
        return heartWaveform, breathWaveform

    # Extract heartWaveform and breathWaveform
    heartWaveform = np.asarray(vitalsData[5:20])
    breathWaveform = np.asarray(vitalsData[20:35])

    return heartWaveform, breathWaveform

def read_and_parse_data(serial_port):
    """Read and parse data from the serial port."""
    byte_buffer = bytearray()
    
    while True:
        if serial_port.in_waiting > 0:
            byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
            if len(byte_buffer) > EXPECTED_HEADER_SIZE:
                # Example parsing logic
                header = byte_buffer[:HEADER_SIZE]
                total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
                if len(byte_buffer) >= total_packet_length:
                    data = byte_buffer[:total_packet_length]
                    byte_buffer = byte_buffer[total_packet_length:]
                    
                    # Process TLV data
                    process_tlv_data(data)

def process_tlv_data(data):
    """Process TLV data from the radar sensor."""
    # Define TLV header size and initialize parsing
    tlv_header_size = 8
    tlv_data = data[HEADER_SIZE:]
    
    while len(tlv_data) > tlv_header_size:
        try:
            # Decode TLV header
            tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
            tlv_data = tlv_data[tlv_header_size:]
            
            # Parse TLV data based on type
            if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
                heartWaveform, breathWaveform = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
                # Save the extracted waveforms to CSV
                save_waveforms_to_csv(heartWaveform, breathWaveform)
                
                # Print the extracted heartWaveform and breathWaveform
                print(f"Heart Waveform: {heartWaveform}")
                print(f"Breath Waveform: {breathWaveform}")
            
            # Move to next TLV
            tlv_data = tlv_data[tlvLength:]
        
        except Exception as e:
            log.error(f'Failed to process TLV data: {e}')
            break

unix_timestamp_st = time.time()


def save_waveforms_to_csv(heartWaveform, breathWaveform):
    """Save heart and breath waveforms to a CSV file with labels and UNIX timestamps with milliseconds."""
    # Get the current UNIX timestamp with milliseconds
    unix_timestamp = time.time() - unix_timestamp_st
    
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write 'Heart Waveform' label with UNIX timestamp (including milliseconds) followed by the heartWaveform array as a row
        writer.writerow([unix_timestamp, 'Heart Waveform'] + heartWaveform.tolist())
        
        # Write 'Breath Waveform' label with UNIX timestamp (including milliseconds) followed by the breathWaveform array as a row
        writer.writerow([unix_timestamp, 'Breath Waveform'] + breathWaveform.tolist())



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

def signal_handler(sig, frame):
    """Handle termination signals to clean up and close serial ports."""
    print("\nTermination signal received. Cleaning up...")
    if 'dataDevice' in locals() and dataDevice.is_open:
        dataDevice.close()
    if 'cliDevice' in locals() and cliDevice.is_open:
        cliDevice.close()
    print("Serial ports closed.")
    exit(0)

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
        
        # Start reading data from the sensor
        print(f"Connected to {dataSerialPort} at 921600 baud rate.")
        read_and_parse_data(dataDevice)

    except serial.SerialException as e:
        print(f"SerialException: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'dataDevice' in locals() and dataDevice.is_open:
            dataDevice.close()
        if 'cliDevice' in locals() and cliDevice.is_open:
            cliDevice.close()
        print("Serial ports closed.")
if __name__ == "__main__":
    main()



# import serial
# import numpy as np
# import struct
# import logging
# import time
# import signal
# import csv

# # Configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Serial port names for CLI and Data ports
# cliSerialPort = 'COM3'  # CLI port for sending configuration
# dataSerialPort = 'COM7'  # Data port for receiving sensor data

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Path to the CSV file
# csvFilePath = r'C:\path\to\your\directory\waveforms.csv'

# # Flag to check if the header has been written to the CSV
# header_written = False

# def save_waveforms_to_csv(heartWaveform, breathWaveform):
#     """Save heart and breath waveforms to a CSV file, appending each array in a new column."""
#     global header_written

#     try:
#         # Open CSV file for appending
#         with open(csvFilePath, 'a', newline='') as csvfile:
#             csvwriter = csv.writer(csvfile)

#             # Write header once at the start if not already written
#             if not header_written:
#                 header = [f'Heart_{i}' for i in range(len(heartWaveform))] + [f'Breath_{i}' for i in range(len(breathWaveform))]
#                 csvwriter.writerow(header)
#                 header_written = True

#             # Write heart and breath waveforms in a single row (as columns)
#             row = list(heartWaveform) + list(breathWaveform)
#             csvwriter.writerow(row)

#         print(f"Waveforms saved to {csvFilePath}")

#     except Exception as e:
#         log.error(f"Failed to save waveforms to CSV: {e}")

# def parseVitalSignsTLV(tlvData, tlvLength):
#     """Parse the TLV data for heart and breath waveforms."""
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize empty arrays for output
#     heartWaveform = []
#     breathWaveform = []

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#     except:
#         log.error('ERROR: Vitals TLV Parsing Failed')
#         return heartWaveform, breathWaveform

#     # Extract heartWaveform and breathWaveform
#     heartWaveform = np.asarray(vitalsData[5:20])
#     breathWaveform = np.asarray(vitalsData[20:35])

#     return heartWaveform, breathWaveform

# def read_and_parse_data(serial_port):
#     """Read and parse data from the serial port."""
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def process_tlv_data(data):
#     """Process TLV data from the radar sensor."""
#     # Define TLV header size and initialize parsing
#     tlv_header_size = 8
#     tlv_data = data[HEADER_SIZE:]
    
#     while len(tlv_data) > tlv_header_size:
#         try:
#             # Decode TLV header
#             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
#             tlv_data = tlv_data[tlv_header_size:]
            
#             # Parse TLV data based on type
#             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
#                 heartWaveform, breathWaveform = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
#                 # Save the waveforms to CSV (each waveform in a new column)
#                 save_waveforms_to_csv(heartWaveform, breathWaveform)
            
#             # Move to next TLV
#             tlv_data = tlv_data[tlvLength:]
        
#         except Exception as e:
#             log.error(f'Failed to process TLV data: {e}')
#             break

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

# def signal_handler(sig, frame):
#     """Handle termination signals to clean up and close serial ports.""" 
#     print("\nTermination signal received. Cleaning up...")
#     if 'dataDevice' in locals() and dataDevice.is_open:
#         dataDevice.close()
#     if 'cliDevice' in locals() and cliDevice.is_open:
#         cliDevice.close()
#     print("Serial ports closed.")
#     exit(0)

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
        
#         # Start reading data from the sensor
#         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
#         read_and_parse_data(dataDevice)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'dataDevice' in locals() and dataDevice.is_open:
#             dataDevice.close()
#         if 'cliDevice' in locals() and cliDevice.is_open:
#             cliDevice.close()
#         print("Serial ports closed.")

# if __name__ == "__main__":
#     main()


####################################################################################################################################
####################################################################################################################################


# import serial
# import numpy as np
# import struct
# import logging
# import time
# import signal
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

# # Configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Serial port names for CLI and Data ports
# cliSerialPort = 'COM3'  # CLI port for sending configuration
# dataSerialPort = 'COM7'  # Data port for receiving sensor data

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Initialize plots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
# heart_line, = ax1.plot([], [], lw=2, label='Heart Waveform')
# breath_line, = ax2.plot([], [], lw=2, label='Breath Waveform')
# ax1.set_ylim(-2, 2)  # Set y-axis limits for Heart Waveform
# ax2.set_ylim(-2, 2)  # Set y-axis limits for Breath Waveform
# ax1.set_xlim(0, 15)  # Set x-axis limits for Heart Waveform
# ax2.set_xlim(0, 15)  # Set x-axis limits for Breath Waveform
# ax1.set_xlabel('Sample')
# ax1.set_ylabel('Amplitude')
# ax2.set_xlabel('Sample')
# ax2.set_ylabel('Amplitude')
# ax1.legend()
# ax2.legend()
# ax1.grid()
# ax2.grid()

# def parseVitalSignsTLV(tlvData, tlvLength):
#     """Parse the TLV data for heart and breath waveforms."""
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize empty arrays for output
#     heartWaveform = []
#     breathWaveform = []

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#     except:
#         log.error('ERROR: Vitals TLV Parsing Failed')
#         return heartWaveform, breathWaveform

#     # Extract heartWaveform and breathWaveform
#     heartWaveform = np.asarray(vitalsData[5:20])
#     breathWaveform = np.asarray(vitalsData[20:35])

#     return heartWaveform, breathWaveform

# def read_and_parse_data(serial_port):
#     """Read and parse data from the serial port."""
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def process_tlv_data(data):
#     """Process TLV data from the radar sensor."""
#     # Define TLV header size and initialize parsing
#     tlv_header_size = 8
#     tlv_data = data[HEADER_SIZE:]
    
#     while len(tlv_data) > tlv_header_size:
#         try:
#             # Decode TLV header
#             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
#             tlv_data = tlv_data[tlv_header_size:]
            
#             # Parse TLV data based on type
#             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
#                 heartWaveform, breathWaveform = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
#                 # Update the plot with new data
#                 update_plot(heartWaveform, breathWaveform)
            
#             # Move to next TLV
#             tlv_data = tlv_data[tlvLength:]
        
#         except Exception as e:
#             log.error(f'Failed to process TLV data: {e}')
#             break

# def update_plot(heartWaveform, breathWaveform):
#     """Update the plot with new data."""
#     heart_line.set_ydata(heartWaveform)
#     breath_line.set_ydata(breathWaveform)
#     heart_line.set_xdata(np.arange(len(heartWaveform)))
#     breath_line.set_xdata(np.arange(len(breathWaveform)))
    
#     # Adjust x-axis limits
#     if len(heartWaveform) > 15:
#         ax1.set_xlim(len(heartWaveform) - 15, len(heartWaveform))
#     if len(breathWaveform) > 15:
#         ax2.set_xlim(len(breathWaveform) - 15, len(breathWaveform))
    
#     fig.canvas.draw()
#     fig.canvas.flush_events()

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

# def signal_handler(sig, frame):
#     """Handle termination signals to clean up and close serial ports."""
#     print("\nTermination signal received. Cleaning up...")
#     if 'dataDevice' in locals() and dataDevice.is_open:
#         dataDevice.close()
#     if 'cliDevice' in locals() and cliDevice.is_open:
#         cliDevice.close()
#     print("Serial ports closed.")
#     exit(0)

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
        
#         # Set up the plot
#         plt.ion()
#         plt.show()
        
#         # Start reading data from the sensor
#         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
#         read_and_parse_data(dataDevice)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'dataDevice' in locals() and dataDevice.is_open:
#             dataDevice.close()
#         if 'cliDevice' in locals() and cliDevice.is_open:
#             cliDevice.close()
#         print("Serial ports closed.")

# if __name__ == "__main__":
#     main()



####################################################################################################################################
####################################################################################################################################



# import serial
# import numpy as np
# import struct
# import logging
# import time
# import signal
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

# # Configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Serial port names for CLI and Data ports
# cliSerialPort = 'COM3'  # CLI port for sending configuration
# dataSerialPort = 'COM7'  # Data port for receiving sensor data

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Initialize plots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
# heart_line, = ax1.plot([], [], lw=2, label='Heart Waveform')
# breath_line, = ax2.plot([], [], lw=2, label='Breath Waveform')
# ax1.set_ylim(-2, 2)  # Set y-axis limits for Heart Waveform
# ax2.set_ylim(-2, 2)  # Set y-axis limits for Breath Waveform
# ax1.set_xlim(0, 15)  # Set x-axis limits for Heart Waveform
# ax2.set_xlim(0, 15)  # Set x-axis limits for Breath Waveform
# ax1.set_xlabel('Sample')
# ax1.set_ylabel('Amplitude')
# ax2.set_xlabel('Sample')
# ax2.set_ylabel('Amplitude')
# ax1.legend()
# ax2.legend()
# ax1.grid()
# ax2.grid()

# # Buffers for waveforms
# heart_waveform_buffer = []
# breath_waveform_buffer = []

# def parseVitalSignsTLV(tlvData, tlvLength):
#     """Parse the TLV data for heart and breath waveforms."""
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize empty arrays for output
#     heartWaveform = []
#     breathWaveform = []

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#     except:
#         log.error('ERROR: Vitals TLV Parsing Failed')
#         return heartWaveform, breathWaveform

#     # Extract heartWaveform and breathWaveform
#     heartWaveform = np.asarray(vitalsData[5:20])
#     breathWaveform = np.asarray(vitalsData[20:35])

#     return heartWaveform, breathWaveform

# def read_and_parse_data(serial_port):
#     """Read and parse data from the serial port."""
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def process_tlv_data(data):
#     """Process TLV data from the radar sensor."""
#     # Define TLV header size and initialize parsing
#     tlv_header_size = 8
#     tlv_data = data[HEADER_SIZE:]
    
#     while len(tlv_data) > tlv_header_size:
#         try:
#             # Decode TLV header
#             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
#             tlv_data = tlv_data[tlv_header_size:]
            
#             # Parse TLV data based on type
#             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
#                 heartWaveform, breathWaveform = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
#                 # Append new data to buffers
#                 heart_waveform_buffer.extend(heartWaveform)
#                 breath_waveform_buffer.extend(breathWaveform)
                
#                 # Update the plot with new data
#                 update_plot()
            
#             # Move to next TLV
#             tlv_data = tlv_data[tlvLength:]
        
#         except Exception as e:
#             log.error(f'Failed to process TLV data: {e}')
#             break

# def update_plot():
#     """Update the plot with new data."""
#     heart_line.set_ydata(heart_waveform_buffer)
#     breath_line.set_ydata(breath_waveform_buffer)
#     heart_line.set_xdata(np.arange(len(heart_waveform_buffer)))
#     breath_line.set_xdata(np.arange(len(breath_waveform_buffer)))
    
#     # Adjust x-axis limits
#     if len(heart_waveform_buffer) > 15:
#         ax1.set_xlim(len(heart_waveform_buffer) - 15, len(heart_waveform_buffer))
#     if len(breath_waveform_buffer) > 15:
#         ax2.set_xlim(len(breath_waveform_buffer) - 15, len(breath_waveform_buffer))
    
#     fig.canvas.draw()
#     fig.canvas.flush_events()

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

# def signal_handler(sig, frame):
#     """Handle termination signals to clean up and close serial ports."""
#     print("\nTermination signal received. Cleaning up...")
#     if 'dataDevice' in locals() and dataDevice.is_open:
#         dataDevice.close()
#     if 'cliDevice' in locals() and cliDevice.is_open:
#         cliDevice.close()
#     print("Serial ports closed.")
#     exit(0)

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
        
#         # Set up the plot
#         plt.ion()
#         plt.show()
        
#         # Start reading data from the sensor
#         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
#         read_and_parse_data(dataDevice)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'dataDevice' in locals() and dataDevice.is_open:
#             dataDevice.close()
#         if 'cliDevice' in locals() and cliDevice.is_open:
#             cliDevice.close()
#         print("Serial ports closed.")

# if __name__ == "__main__":
#     main()


####################################################################################################################################
####################################################################################################################################



# #  this code plots the realtime wavefroms 

# import serial
# import numpy as np
# import struct
# import logging
# import time
# import signal
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

# # Configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Serial port names for CLI and Data ports
# cliSerialPort = 'COM3'  # CLI port for sending configuration
# dataSerialPort = 'COM7'  # Data port for receiving sensor data

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Initialize plots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
# heart_line, = ax1.plot([], [], lw=2, label='Heart Waveform')
# breath_line, = ax2.plot([], [], lw=2, label='Breath Waveform')
# ax1.set_ylim(-2, 2)  # Set y-axis limits for Heart Waveform
# ax2.set_ylim(-2, 2)  # Set y-axis limits for Breath Waveform
# ax1.set_xlabel('Sample')
# ax1.set_ylabel('Amplitude')
# ax2.set_xlabel('Sample')
# ax2.set_ylabel('Amplitude')
# ax1.legend()
# ax2.legend()
# ax1.grid()
# ax2.grid()

# # Buffers for waveforms
# heart_waveform_buffer = []
# breath_waveform_buffer = []

# def parseVitalSignsTLV(tlvData, tlvLength):
#     """Parse the TLV data for heart and breath waveforms."""
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize empty arrays for output
#     heartWaveform = []
#     breathWaveform = []

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#     except:
#         log.error('ERROR: Vitals TLV Parsing Failed')
#         return heartWaveform, breathWaveform

#     # Extract heartWaveform and breathWaveform
#     heartWaveform = np.asarray(vitalsData[5:20])
#     breathWaveform = np.asarray(vitalsData[20:35])

#     return heartWaveform, breathWaveform

# def read_and_parse_data(serial_port):
#     """Read and parse data from the serial port."""
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def process_tlv_data(data):
#     """Process TLV data from the radar sensor."""
#     # Define TLV header size and initialize parsing
#     tlv_header_size = 8
#     tlv_data = data[HEADER_SIZE:]
    
#     while len(tlv_data) > tlv_header_size:
#         try:
#             # Decode TLV header
#             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
#             tlv_data = tlv_data[tlv_header_size:]
            
#             # Parse TLV data based on type
#             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
#                 heartWaveform, breathWaveform = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
#                 # Append new data to buffers
#                 heart_waveform_buffer.extend(heartWaveform)
#                 breath_waveform_buffer.extend(breathWaveform)
                
#                 # Update the plot with new data
#                 update_plot()
            
#             # Move to next TLV
#             tlv_data = tlv_data[tlvLength:]
        
#         except Exception as e:
#             log.error(f'Failed to process TLV data: {e}')
#             break

# def update_plot():
#     """Update the plot with new data and print the current waveforms."""
#     heart_line.set_ydata(heart_waveform_buffer)
#     breath_line.set_ydata(breath_waveform_buffer)
    
#     heart_line.set_xdata(np.arange(len(heart_waveform_buffer)))
#     breath_line.set_xdata(np.arange(len(breath_waveform_buffer)))
    
#     # Adjust x-axis limits to show data from 0 to the current length
#     ax1.set_xlim(0, len(heart_waveform_buffer))
#     ax2.set_xlim(0, len(breath_waveform_buffer))
    
#     # Adjust y-axis limits to fit all data
#     ax1.set_ylim(min(heart_waveform_buffer) - 1, max(heart_waveform_buffer) + 1)
#     ax2.set_ylim(min(breath_waveform_buffer) - 1, max(breath_waveform_buffer) + 1)
    
#     # Print the real-time waveforms
#     print("Heart Waveform:", heart_waveform_buffer)
#     print("Breath Waveform:", breath_waveform_buffer)
    
#     # Refresh the plot
#     fig.canvas.draw()
#     fig.canvas.flush_events()


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

# def signal_handler(sig, frame):
#     """Handle termination signals to clean up and close serial ports."""
#     print("\nTermination signal received. Cleaning up...")
#     if 'dataDevice' in locals() and dataDevice.is_open:
#         dataDevice.close()
#     if 'cliDevice' in locals() and cliDevice.is_open:
#         cliDevice.close()
#     print("Serial ports closed.")
#     exit(0)

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
        
#         # Set up the plot
#         plt.ion()
#         plt.show()
        
#         # Start reading data from the sensor
#         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
#         read_and_parse_data(dataDevice)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'dataDevice' in locals() and dataDevice.is_open:
#             dataDevice.close()
#         if 'cliDevice' in locals() and cliDevice.is_open:
#             cliDevice.close()
#         print("Serial ports closed.")

# if __name__ == "__main__":
#     main()

####################################################################################################################################
####################################################################################################################################


#  this code plots the realtime wavefroms and holding breath trigger

# import serial
# import numpy as np
# import struct
# import logging
# import time
# import signal
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

# # Configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Serial port names for CLI and Data ports
# cliSerialPort = 'COM3'  # CLI port for sending configuration
# dataSerialPort = 'COM7'  # Data port for receiving sensor data

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Initialize plots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
# heart_line, = ax1.plot([], [], lw=2, label='Heart Waveform')
# breath_line, = ax2.plot([], [], lw=2, label='Breath Waveform')
# ax1.set_ylim(-2, 2)  # Set y-axis limits for Heart Waveform
# ax2.set_ylim(-2, 2)  # Set y-axis limits for Breath Waveform
# ax1.set_xlabel('Sample')
# ax1.set_ylabel('Amplitude')
# ax2.set_xlabel('Sample')
# ax2.set_ylabel('Amplitude')
# ax1.legend()
# ax2.legend()
# ax1.grid()
# ax2.grid()

# # Buffers for waveforms
# heart_waveform_buffer = []
# breath_waveform_buffer = []

# def parseVitalSignsTLV(tlvData, tlvLength):
#     """Parse the TLV data for heart and breath waveforms."""
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize empty arrays for output
#     heartWaveform = []
#     breathWaveform = []

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#     except:
#         log.error('ERROR: Vitals TLV Parsing Failed')
#         return heartWaveform, breathWaveform

#     # Extract heartWaveform and breathWaveform
#     heartWaveform = np.asarray(vitalsData[5:20])
#     breathWaveform = np.asarray(vitalsData[20:35])

#     return heartWaveform, breathWaveform

# def read_and_parse_data(serial_port):
#     """Read and parse data from the serial port."""
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def process_tlv_data(data):
#     """Process TLV data from the radar sensor."""
#     # Define TLV header size and initialize parsing
#     tlv_header_size = 8
#     tlv_data = data[HEADER_SIZE:]
    
#     while len(tlv_data) > tlv_header_size:
#         try:
#             # Decode TLV header
#             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
#             tlv_data = tlv_data[tlv_header_size:]
            
#             # Parse TLV data based on type
#             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
#                 heartWaveform, breathWaveform = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
#                 # Append new data to buffers
#                 heart_waveform_buffer.extend(heartWaveform)
#                 breath_waveform_buffer.extend(breathWaveform)
                
#                 # Update the plot with new data
#                 update_plot()
            
#             # Move to next TLV
#             tlv_data = tlv_data[tlvLength:]
        
#         except Exception as e:
#             log.error(f'Failed to process TLV data: {e}')
#             break

# def update_plot():
#     """Update the plot with new data and print the current waveforms."""
#     global breath_waveform_buffer
    
#     heart_line.set_ydata(heart_waveform_buffer)
#     breath_line.set_ydata(breath_waveform_buffer)
    
#     heart_line.set_xdata(np.arange(len(heart_waveform_buffer)))
#     breath_line.set_xdata(np.arange(len(breath_waveform_buffer)))
    
#     # Adjust x-axis limits to show data from 0 to the current length
#     ax1.set_xlim(0, len(heart_waveform_buffer))
#     ax2.set_xlim(0, len(breath_waveform_buffer))
    
#     # Adjust y-axis limits to fit all data
#     ax1.set_ylim(min(heart_waveform_buffer) - 1, max(heart_waveform_buffer) + 1)
#     ax2.set_ylim(min(breath_waveform_buffer) - 1, max(breath_waveform_buffer) + 1)
    
#     # Check if breath waveform amplitude is between -0.1 and 0.1 (holding breath)
#     if all(-0.1 <= val <= 0.1 for val in breath_waveform_buffer[-10:]):  # Checking the last 10 samples
#         print("Holding breath")
    
#     # Refresh the plot
#     fig.canvas.draw()
#     fig.canvas.flush_events()

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

# def signal_handler(sig, frame):
#     """Handle termination signals to clean up and close serial ports."""
#     print("\nTermination signal received. Cleaning up...")
#     if 'dataDevice' in locals() and dataDevice.is_open:
#         dataDevice.close()
#     if 'cliDevice' in locals() and cliDevice.is_open:
#         cliDevice.close()
#     print("Serial ports closed.")
#     exit(0)

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
        
#         # Set up the plot
#         plt.ion()
#         plt.show()
        
#         # Start reading data from the sensor
#         print(f"Connected to {dataSerialPort} at 921600 baud rate.")
#         read_and_parse_data(dataDevice)

#     except serial.SerialException as e:
#         print(f"SerialException: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'dataDevice' in locals() and dataDevice.is_open:
#             dataDevice.close()
#         if 'cliDevice' in locals() and cliDevice.is_open:
#             cliDevice.close()
#         print("Serial ports closed.")

# if __name__ == "__main__":
#     main()


####################################################################################################################################
####################################################################################################################################


# # this code is meant for integration 


# import serial
# import numpy as np
# import struct
# import logging
# import time
# import signal
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from collections import deque
# import sys

# # Configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Serial port names for CLI and Data ports
# cliSerialPort = 'COM3'  # CLI port for sending configuration
# dataSerialPort = 'COM7'  # Data port for receiving sensor data

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Initialize plots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
# heart_line, = ax1.plot([], [], lw=2, label='Heart Waveform')
# breath_line, = ax2.plot([], [], lw=2, label='Breath Waveform')
# ax1.set_ylim(-2, 2)  # Set y-axis limits for Heart Waveform
# ax2.set_ylim(-2, 2)  # Set y-axis limits for Breath Waveform
# ax1.set_xlabel('Sample')
# ax1.set_ylabel('Amplitude')
# ax2.set_xlabel('Sample')
# ax2.set_ylabel('Amplitude')
# ax1.legend()
# ax2.legend()
# ax1.grid()
# ax2.grid()

# # Buffers for waveforms and readings
# heart_waveform_buffer = []
# breath_waveform_buffer = []
# breath_rate_readings = deque(maxlen=40)
# heart_rate_readings = deque(maxlen=40)

# # Lists to store rolling averages
# list_of_breath_averages = []
# list_of_heart_averages = []
# reading_counter = 0

# def parseVitalSignsTLV(tlvData, tlvLength):
#     """Parse the TLV data for heart and breath waveforms."""
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize empty arrays for output
#     heartWaveform = []
#     breathWaveform = []
    
#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#     except:
#         log.error('ERROR: Vitals TLV Parsing Failed')
#         return heartWaveform, breathWaveform

#     # Extract heartWaveform and breathWaveform
#     heartWaveform = np.asarray(vitalsData[5:20])
#     breathWaveform = np.asarray(vitalsData[20:35])

#     # Extract breath rate and heart rate
#     breathRate = vitalsData[4]
#     heartRate = vitalsData[3]

#     return heartWaveform, breathWaveform, breathRate, heartRate

# def read_and_parse_data(serial_port):
#     """Read and parse data from the serial port."""
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def process_tlv_data(data):
#     """Process TLV data from the radar sensor."""
#     tlv_header_size = 8
#     tlv_data = data[HEADER_SIZE:]
    
#     while len(tlv_data) > tlv_header_size:
#         try:
#             # Decode TLV header
#             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
#             tlv_data = tlv_data[tlv_header_size:]
            
#             # Parse TLV data based on type
#             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
#                 heartWaveform, breathWaveform, breathRate, heartRate = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
#                 # Append new data to buffers
#                 heart_waveform_buffer.extend(heartWaveform)
#                 breath_waveform_buffer.extend(breathWaveform)
                
#                 # Check if breath waveform indicates holding breath
#                 holding_breath = all(-0.1 <= val <= 0.1 for val in breath_waveform_buffer[-10:])  # Last 10 samples

#                 # Update the plot with new data
#                 update_plot()

#                 # Output breath rate and heart rate, handle holding breath
#                 print(f"Heart Rate: {heartRate:.2f} BPM")
#                 if holding_breath:
#                     print("Breath Rate: Not Detected (Holding Breath)")
#                 else:
#                     print(f"Breath Rate: {breathRate:.2f} BPM")

#                 # Update rolling averages for breath rate and heart rate
#                 update_rolling_average(breathRate, heartRate, holding_breath)
            
#             # Move to next TLV
#             tlv_data = tlv_data[tlvLength:]
        
#         except Exception as e:
#             log.error(f'Failed to process TLV data: {e}')
#             break

# def update_rolling_average(breath_rate, heart_rate, holding_breath):
#     global reading_counter

#     # Append new breath rate and heart rate readings
#     heart_rate_readings.append(heart_rate)

#     # Only append breath rate if not holding breath
#     if not holding_breath:
#         breath_rate_readings.append(breath_rate)

#     reading_counter += 1

#     # Calculate and store rolling averages when we have 40 new readings
#     if reading_counter == 40:
#         breath_average = float(np.mean(breath_rate_readings)) if breath_rate_readings else 'Not Detected'
#         heart_average = float(np.mean(heart_rate_readings))
        
#         if breath_average != 'Not Detected':
#             list_of_breath_averages.append(breath_average)
#         list_of_heart_averages.append(heart_average)

#         print(f"Rolling Average of Last 40 Breath Readings: {breath_average if breath_average != 'Not Detected' else 'Not Detected'} BPM")
#         print(f"Rolling Average of Last 40 Heart Readings: {heart_average:.2f} BPM")
        
#         reading_counter = 0

# def update_plot():
#     """Update the plot with new data and print the current waveforms."""
#     global breath_waveform_buffer
    
#     heart_line.set_ydata(heart_waveform_buffer)
#     breath_line.set_ydata(breath_waveform_buffer)
    
#     heart_line.set_xdata(np.arange(len(heart_waveform_buffer)))
#     breath_line.set_xdata(np.arange(len(breath_waveform_buffer)))
    
#     # Adjust x-axis limits to show data from 0 to the current length
#     ax1.set_xlim(0, len(heart_waveform_buffer))
#     ax2.set_xlim(0, len(breath_waveform_buffer))
    
#     # Adjust y-axis limits to fit all data
#     ax1.set_ylim(min(heart_waveform_buffer) - 1, max(heart_waveform_buffer) + 1)
#     ax2.set_ylim(min(breath_waveform_buffer) - 1, max(breath_waveform_buffer) + 1)
    
#     # Refresh the plot
#     fig.canvas.draw()
#     fig.canvas.flush_events()

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

# def signal_handler(sig, frame):
#     """Handle termination signals to clean up and close serial ports."""
#     print("\nTermination signal received. Cleaning up...")
#     if list_of_breath_averages:
#         print(f"List of all Rolling Breath Averages: {list_of_breath_averages}")
#         print(f"Latest Rolling Breath Average : {list_of_breath_averages[-1]:.2f} BPM")
#     if list_of_heart_averages:
#         print(f"List of all Rolling Heart Averages: {list_of_heart_averages}")
#         print(f"Latest Rolling Heart Average: {list_of_heart_averages[-1]:.2f} BPM")
#     sys.exit(0)

# def main():
#     """Main function to set up serial communication and start data reading."""
#     try:
#         # Open serial ports for CLI and Data
#         cliDevice = serial.Serial(cliSerialPort, 115200, timeout=0.5)
#         dataDevice = serial.Serial(dataSerialPort, 921600, timeout=0.5)
        
#         # Send configuration to sensor
#         send_config_to_sensor(cliDevice, radarCfgFile)
        
#         # Register signal handler for graceful termination
#         signal.signal(signal.SIGINT, signal_handler)

#         # Set up real-time plot animation
#         ani = animation.FuncAnimation(fig, update_plot, interval=1000)
#         plt.show(block=False)
        
#         # Read and parse data from the sensor in real-time
#         read_and_parse_data(dataDevice)

#     except Exception as e:
#         log.error(f"Error occurred: {e}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()
