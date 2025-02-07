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
csv_file_path = r'C:\\path\\to\\your\\directory\\vitalwaveL2.csv'

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


#####################################################################################################################################
#####################################################################################################################################


# import serial
# import numpy as np
# import struct
# import logging
# import csv
# import os

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Define the CSV file path
# CSV_FILE_PATH = '/path/to/your/directory/wavefromsave1.csv'  # Replace with your path

# def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize struct in case of error
#     vitalsOutput = {}
#     vitalsOutput['id'] = 999
#     vitalsOutput['rangeBin'] = 0
#     vitalsOutput['breathDeviation'] = 0
#     vitalsOutput['heartRate'] = 0
#     vitalsOutput['breathRate'] = 0
#     vitalsOutput['heartWaveform'] = []
#     vitalsOutput['breathWaveform'] = []

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#     except:
#         log.error('ERROR: Vitals TLV Parsing Failed')
#         outputDict['vitals'] = vitalsOutput
#         return

#     # Parse this patient's data
#     vitalsOutput['id'] = vitalsData[0]
#     vitalsOutput['rangeBin'] = vitalsData[1]
#     vitalsOutput['breathDeviation'] = vitalsData[2]
#     vitalsOutput['heartRate'] = vitalsData[3]
#     vitalsOutput['breathRate'] = vitalsData[4]
#     vitalsOutput['heartWaveform'] = np.asarray(vitalsData[5:20])
#     vitalsOutput['breathWaveform'] = np.asarray(vitalsData[20:35])

#     # Advance tlv data pointer to end of this TLV
#     tlvData = tlvData[vitalsSize:]
#     outputDict['vitals'] = vitalsOutput

# def write_to_csv(data):
#     # Check if the file exists
#     file_exists = os.path.isfile(CSV_FILE_PATH)
    
#     # Open the file in append mode
#     with open(CSV_FILE_PATH, mode='a', newline='') as file:
#         writer = csv.writer(file)
        
#         # Write header if file does not exist
#         if not file_exists:
#             header = ['id', 'rangeBin', 'breathDeviation', 'heartRate', 'breathRate'] + \
#                      [f'heartWaveform_{i}' for i in range(15)] + \
#                      [f'breathWaveform_{i}' for i in range(15)]
#             writer.writerow(header)
        
#         # Write the data
#         row = [
#             data['id'],
#             data['rangeBin'],
#             data['breathDeviation'],
#             data['heartRate'],
#             data['breathRate']
#         ] + list(data['heartWaveform']) + list(data['breathWaveform'])
#         writer.writerow(row)

# def read_and_parse_data(serial_port):
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
#     # Define TLV header size and initialize parsing
#     tlv_header_size = 8
#     tlv_data = data[HEADER_SIZE:]
    
#     outputDict = {}
    
#     while len(tlv_data) > tlv_header_size:
#         try:
#             # Decode TLV header
#             tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
#             tlv_data = tlv_data[tlv_header_size:]
            
#             # Parse TLV data based on type
#             if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
#                 parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength, outputDict)
            
#             # Move to next TLV
#             tlv_data = tlv_data[tlvLength:]
        
#         except Exception as e:
#             log.error(f'Failed to process TLV data: {e}')
#             break
    
#     # Output parsed data to CSV and terminal
#     if 'vitals' in outputDict:
#         write_to_csv(outputDict['vitals'])
#         print(f"Parsed and saved Vital Signs: {outputDict['vitals']}")

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

