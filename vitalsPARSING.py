# # vital sign parsing array

# import serial
# import numpy as np
# import struct
# import logging
# import matplotlib.pyplot as plt

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040


# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

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
    
#     # Output parsed data (for demonstration purposes)
#     if 'vitals' in outputDict:
#         print(f"Parsed Vital Signs: {outputDict['vitals']}")

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





import struct
import time
import serial
import numpy as np
import logging
import signal
import sys

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 32  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE
MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# Define the configuration file path
radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# Define the CLI and Data serial ports
cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
dataSerialPort = 'COM7'  # Data port (change as per your setup)

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Initialize global variable for data device
dataDevice = None

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

def parseVitalSignsTLV(tlvData, tlvLength):
    """Parse the vital signs TLV and return heart and breath waveforms."""
    vitalsStruct = '2H33f'
    vitalsSize = struct.calcsize(vitalsStruct)
    
    # Initialize struct in case of error
    vitalsOutput = {
        'id': 999,
        'rangeBin': 0,
        'breathDeviation': 0,
        'heartRate': 0,
        'breathRate': 0,
        'heartWaveform': [],
        'breathWaveform': []
    }

    try:
        vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
        
        vitalsOutput['id'] = vitalsData[0]
        vitalsOutput['rangeBin'] = vitalsData[1]
        vitalsOutput['breathDeviation'] = vitalsData[2]
        vitalsOutput['heartRate'] = vitalsData[3]
        vitalsOutput['breathRate'] = vitalsData[4]
        vitalsOutput['heartWaveform'] = np.asarray(vitalsData[5:20])
        vitalsOutput['breathWaveform'] = np.asarray(vitalsData[20:35])
        
        print(f"ID: {vitalsOutput['id']}")
        print(f"Range Bin: {vitalsOutput['rangeBin']}")
        print(f"Breath Deviation: {vitalsOutput['breathDeviation']}")
        print(f"Breath Rate: {vitalsOutput['breathRate']}")
        print(f"Heart Rate: {vitalsOutput['heartRate']}")
        print(f"Heart Waveform: {vitalsOutput['heartWaveform']}")
        print(f"Breath Waveform: {vitalsOutput['breathWaveform']}")
        
        return vitalsOutput['breathWaveform'], vitalsOutput['heartWaveform']

    except Exception as e:
        log.error(f'ERROR: Vitals TLV Parsing Failed - {e}')
        print(f"Error Output: {vitalsOutput}")
        return vitalsOutput['breathWaveform'], vitalsOutput['heartWaveform']

def tlvHeaderDecode(data):
    """Decode TLV header from the data."""
    tlvType, tlvLength = struct.unpack('2I', data)
    return tlvType, tlvLength

def process_tlv_data(data):
    """Processes TLV data to extract vital signs."""
    tlv_header_size = 8
    tlv_data = data[HEADER_SIZE:]
    
    while len(tlv_data) > tlv_header_size:
        try:
            # Decode TLV header
            tlvType, tlvLength = tlvHeaderDecode(tlv_data[:tlv_header_size])
            tlv_data = tlv_data[tlv_header_size:]
            
            if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
                breathWaveform, heartWaveform = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                if breathWaveform is not None and heartWaveform is not None:
                    print(f"Breath Waveform: {breathWaveform}")
                    print(f"Heart Waveform: {heartWaveform}")
            
            # Move to next TLV
            tlv_data = tlv_data[tlvLength:]

        except Exception as e:
            log.error(f'Failed to process TLV data: {e}')
            break

def read_and_parse_data(serial_port):
    """Read data from the radar sensor and process it to extract waveforms."""
    byte_buffer = bytearray()
    
    while True:
        if serial_port.in_waiting > 0:
            byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
            if len(byte_buffer) > EXPECTED_HEADER_SIZE:
                header = byte_buffer[:HEADER_SIZE]
                total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
                if len(byte_buffer) >= total_packet_length:
                    data = byte_buffer[:total_packet_length]
                    byte_buffer = byte_buffer[total_packet_length:]
                    
                    # Process TLV data and extract waveforms
                    process_tlv_data(data)

def signal_handler(sig, frame):
    """Handles termination signal to close the serial port gracefully."""
    print("\nTerminating and closing connections...")
    if dataDevice and dataDevice.is_open:
        dataDevice.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    global dataDevice  # Declare dataDevice as global
    
    try:
        # Initialize serial connection for CLI
        cliDevice = serial.Serial(cliSerialPort, 115200, timeout=1)
        send_config_to_sensor(cliDevice, radarCfgFile)

        # Initialize serial connection for data
        dataDevice = serial.Serial(dataSerialPort, 921600, timeout=1)
        print(f"Connected to {dataSerialPort} at 921600 baud rate.")
        
        # Start reading and processing data
        read_and_parse_data(dataDevice)

    except serial.SerialException as e:
        print(f"SerialException: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if dataDevice and dataDevice.is_open:
            dataDevice.close()
        print("Serial port closed.")

if __name__ == "__main__":
    main()





# #  prints the raw data 

# # import serial
# # import numpy as np

# # # Define sizes for header and packet (update these sizes based on your radar data format)
# # HEADER_SIZE = 32  # Example size, replace with actual header size
# # EXPECTED_HEADER_SIZE = HEADER_SIZE

# # def read_and_parse_data(serial_port):
# #     byte_buffer = bytearray()
    
# #     while True:
# #         if serial_port.in_waiting > 0:
# #             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
# #             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
# #                 # Example parsing logic
# #                 header = byte_buffer[:HEADER_SIZE]
# #                 # Parse header - you might need to adjust this according to your format
# #                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
# #                 if len(byte_buffer) >= total_packet_length:
# #                     data = byte_buffer[:total_packet_length]
# #                     byte_buffer = byte_buffer[total_packet_length:]
                    
# #                     # Process data - update this with your actual data processing
# #                     print(f"Data Received: {data}")

# # def main():
# #     comport = 'COM7'
# #     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
# #     try:
# #         serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
# #         print(f"Connected to {comport} at {baudrate} baud rate.")
        
# #         while True:
# #             read_and_parse_data(serial_port)

# #     except serial.SerialException as e:
# #         print(f"SerialException: {e}")
# #     except Exception as e:
# #         print(f"An unexpected error occurred: {e}")
# #     finally:
# #         if 'serial_port' in locals() and serial_port.is_open:
# #             serial_port.close()
# #         print("Serial port closed.")

# # if __name__ == "__main__":
# #     main()


# # prints real time breahtrate 

# # import serial
# # import numpy as np
# # import struct
# # import logging

# # # Define sizes for header and packet (update these sizes based on your radar data format)
# # HEADER_SIZE = 32  # Example size, replace with actual header size
# # EXPECTED_HEADER_SIZE = HEADER_SIZE
# # MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # # Initialize logger
# # logging.basicConfig(level=logging.DEBUG)
# # log = logging.getLogger(__name__)

# # def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
# #     vitalsStruct = '2H33f'
# #     vitalsSize = struct.calcsize(vitalsStruct)
    
# #     # Initialize struct in case of error
# #     vitalsOutput = {}
# #     vitalsOutput['breathRate'] = 0  # Initialize breathRate

# #     # Capture data for active patient
# #     try:
# #         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
# #         # Parse breathRate
# #         vitalsOutput['breathRate'] = vitalsData[4]
# #     except Exception as e:
# #         log.error(f'ERROR: Vitals TLV Parsing Failed - {e}')
# #         outputDict['vitals'] = vitalsOutput
# #         return

# #     # Advance tlv data pointer to end of this TLV
# #     tlvData = tlvData[vitalsSize:]
# #     outputDict['vitals'] = vitalsOutput

# # def read_and_parse_data(serial_port):
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
    
# #     # Output only the breathRate
# #     if 'vitals' in outputDict and 'breathRate' in outputDict['vitals']:
# #         print(f"Breath Rate: {outputDict['vitals']['breathRate']} BPM")
    

# # def main():
# #     comport = 'COM7'
# #     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
# #     try:
# #         serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
# #         print(f"Connected to {comport} at {baudrate} baud rate.")
        
# #         while True:
# #             read_and_parse_data(serial_port)

# #     except serial.SerialException as e:
# #         print(f"SerialException: {e}")
# #     except Exception as e:
# #         print(f"An unexpected error occurred: {e}")
# #     finally:
# #         if 'serial_port' in locals() and serial_port.is_open:
# #             serial_port.close()
# #         print("Serial port closed.")

# # if __name__ == "__main__":
# #     main()


# # import serial
# # import numpy as np
# # import struct
# # import logging
# # from collections import deque

# # # Define sizes for header and packet (update these sizes based on your radar data format)
# # HEADER_SIZE = 32  # Example size, replace with actual header size
# # EXPECTED_HEADER_SIZE = HEADER_SIZE
# # MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # # Initialize logger
# # logging.basicConfig(level=logging.DEBUG)
# # log = logging.getLogger(__name__)

# # # List to store last 30 breath rate readings
# # breath_rate_readings = deque(maxlen=30)
# # # List to store calculated rolling averages
# # rolling_averages = []

# # def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
# #     vitalsStruct = '2H33f'
# #     vitalsSize = struct.calcsize(vitalsStruct)
    
# #     # Initialize struct in case of error
# #     vitalsOutput = {}
# #     vitalsOutput['breathRate'] = 0  # Initialize breathRate

# #     # Capture data for active patient
# #     try:
# #         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
# #         # Parse breathRate
# #         vitalsOutput['breathRate'] = vitalsData[4]
# #     except Exception as e:
# #         log.error(f'ERROR: Vitals TLV Parsing Failed - {e}')
# #         outputDict['vitals'] = vitalsOutput
# #         return

# #     # Advance tlv data pointer to end of this TLV
# #     tlvData = tlvData[vitalsSize:]
# #     outputDict['vitals'] = vitalsOutput

# # def update_rolling_average(breath_rate):
# #     # Append new breath rate reading
# #     breath_rate_readings.append(breath_rate)
    
# #     # Calculate and store rolling average when we have 30 readings
# #     if len(breath_rate_readings) == 30:
# #         average = np.mean(breath_rate_readings)
# #         rolling_averages.append(average)
# #         print(f"Rolling Average of Last 30 Seconds: {average:.2f} BPM")

# # def read_and_parse_data(serial_port):
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
    
# #     # Output only the breathRate
# #     if 'vitals' in outputDict and 'breathRate' in outputDict['vitals']:
# #         breath_rate = outputDict['vitals']['breathRate']
# #         print(f"Breath Rate: {breath_rate} BPM")
# #         update_rolling_average(breath_rate)

# # def main():
# #     comport = 'COM7'
# #     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
# #     try:
# #         serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
# #         print(f"Connected to {comport} at {baudrate} baud rate.")
        
# #         while True:
# #             read_and_parse_data(serial_port)

# #     except serial.SerialException as e:
# #         print(f"SerialException: {e}")
# #     except Exception as e:
# #         print(f"An unexpected error occurred: {e}")
# #     finally:
# #         if 'serial_port' in locals() and serial_port.is_open:
# #             serial_port.close()
# #         print("Serial port closed.")

# # if __name__ == "__main__":
# #     main()



# # calcualtes a rolling average every 5 readings 

# # import serial
# # import numpy as np
# # import struct
# # import logging
# # from collections import deque

# # # Define sizes for header and packet (update these sizes based on your radar data format)
# # HEADER_SIZE = 32  # Example size, replace with actual header size
# # EXPECTED_HEADER_SIZE = HEADER_SIZE
# # MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # # Initialize logger
# # logging.basicConfig(level=logging.DEBUG)
# # log = logging.getLogger(__name__)

# # # List to store breath rate readings
# # breath_rate_readings = deque(maxlen=50)
# # # List to store calculated rolling averages
# # rolling_averages = []
# # # Counter for tracking the number of readings
# # reading_counter = 0

# # def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
# #     vitalsStruct = '2H33f'
# #     vitalsSize = struct.calcsize(vitalsStruct)
    
# #     # Initialize struct in case of error
# #     vitalsOutput = {}
# #     vitalsOutput['breathRate'] = 0  # Initialize breathRate

# #     # Capture data for active patient
# #     try:
# #         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
# #         # Parse breathRate
# #         vitalsOutput['breathRate'] = vitalsData[4]
# #     except Exception as e:
# #         log.error(f'ERROR: Vitals TLV Parsing Failed - {e}')
# #         outputDict['vitals'] = vitalsOutput
# #         return

# #     # Advance tlv data pointer to end of this TLV
# #     tlvData = tlvData[vitalsSize:]
# #     outputDict['vitals'] = vitalsOutput

# # def update_rolling_average(breath_rate):
# #     global reading_counter

# #     # Append new breath rate reading
# #     breath_rate_readings.append(breath_rate)
# #     reading_counter += 1

# #     # Calculate and store rolling average when we have 50 new readings
# #     if reading_counter == 5:
# #         average = np.mean(breath_rate_readings)
# #         rolling_averages.append(average)
# #         print(f"Rolling Average of Last 50 Readings: {average:.2f} BPM")
# #         # Reset the counter after calculating the average
# #         reading_counter = 0

# # def read_and_parse_data(serial_port):
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
    
# #     # Output only the breathRate
# #     if 'vitals' in outputDict and 'breathRate' in outputDict['vitals']:
# #         breath_rate = outputDict['vitals']['breathRate']
# #         print(f"Breath Rate: {breath_rate} BPM")
# #         update_rolling_average(breath_rate)

# # def main():
# #     comport = 'COM7'
# #     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
# #     try:
# #         serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
# #         print(f"Connected to {comport} at {baudrate} baud rate.")
        
# #         while True:
# #             read_and_parse_data(serial_port)

# #     except serial.SerialException as e:
# #         print(f"SerialException: {e}")
# #     except Exception as e:
# #         print(f"An unexpected error occurred: {e}")
# #     finally:
# #         if 'serial_port' in locals() and serial_port.is_open:
# #             serial_port.close()
# #         print("Serial port closed.")

# # if __name__ == "__main__":
# #     main()


# # prints the latest rolling average 

# # import serial
# # import numpy as np
# # import struct
# # import logging
# # from collections import deque
# # import signal
# # import sys

# # # Define sizes for header and packet (update these sizes based on your radar data format)
# # HEADER_SIZE = 32  # Example size, replace with actual header size
# # EXPECTED_HEADER_SIZE = HEADER_SIZE
# # MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # # Initialize logger
# # logging.basicConfig(level=logging.DEBUG)
# # log = logging.getLogger(__name__)

# # # List to store breath rate readings
# # breath_rate_readings = deque(maxlen=50)
# # # List to store calculated rolling averages
# # list_of_averages = []
# # # Counter for tracking the number of readings
# # reading_counter = 0

# # def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
# #     vitalsStruct = '2H33f'
# #     vitalsSize = struct.calcsize(vitalsStruct)
    
# #     # Initialize struct in case of error
# #     vitalsOutput = {}
# #     vitalsOutput['breathRate'] = 0  # Initialize breathRate

# #     # Capture data for active patient
# #     try:
# #         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
# #         # Parse breathRate
# #         vitalsOutput['breathRate'] = vitalsData[4]
# #     except Exception as e:
# #         log.error(f'ERROR: Vitals TLV Parsing Failed - {e}')
# #         outputDict['vitals'] = vitalsOutput
# #         return

# #     # Advance tlv data pointer to end of this TLV
# #     tlvData = tlvData[vitalsSize:]
# #     outputDict['vitals'] = vitalsOutput

# # def update_rolling_average(breath_rate):
# #     global reading_counter

# #     # Append new breath rate reading
# #     breath_rate_readings.append(breath_rate)
# #     reading_counter += 1

# #     # Calculate and store rolling average when we have 50 new readings
# #     if reading_counter == 5:
# #         average = np.mean(breath_rate_readings)
# #         list_of_averages.append(average)
# #         print(f"Rolling Average of Last 50 Readings: {average:.2f} BPM")
# #         # Reset the counter after calculating the average
# #         reading_counter = 0

# # def read_and_parse_data(serial_port):
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
    
# #     # Output only the breathRate
# #     if 'vitals' in outputDict and 'breathRate' in outputDict['vitals']:
# #         breath_rate = outputDict['vitals']['breathRate']
# #         print(f"Breath Rate: {breath_rate} BPM")
# #         update_rolling_average(breath_rate)

# # def signal_handler(sig, frame):
# #     print("\nTerminating...")
# #     if list_of_averages:
# #         print(f"Latest Rolling Average: {list_of_averages[-1]:.2f} BPM")
# #     else:
# #         print("No rolling averages recorded.")
# #     sys.exit(0)

# # def main():
# #     comport = 'COM7'
# #     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
# #     # Register signal handler for termination
# #     signal.signal(signal.SIGINT, signal_handler)
# #     signal.signal(signal.SIGTERM, signal_handler)
    
# #     try:
# #         serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
# #         print(f"Connected to {comport} at {baudrate} baud rate.")
        
# #         while True:
# #             read_and_parse_data(serial_port)

# #     except serial.SerialException as e:
# #         print(f"SerialException: {e}")
# #     except Exception as e:
# #         print(f"An unexpected error occurred: {e}")
# #     finally:
# #         if 'serial_port' in locals() and serial_port.is_open:
# #             serial_port.close()
# #         print("Serial port closed.")

# # if __name__ == "__main__":
# #     main()


# #  this code recieves data from IWR6843ISK and ouputs the following :
# # 1) realtime breathrate output 
# # 2) rolling average of last 40 readings (adjustable , refer to "if reading_counter == 40:") 
# # 3) lastly when the code is terminated , it out puts a list of all the rolling average values in a list called "print(f"List of Rolling Averages: {list_of_averages}")
# # 4) also prints out the latest value of the element appended in the above list (latest rolling average)

# import serial
# import numpy as np
# import struct
# import logging
# from collections import deque
# import signal
# import sys

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 40  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # List to store breath rate readings
# breath_rate_readings = deque(maxlen=50)
# # List to store calculated rolling averages
# list_of_averages = []
# # Counter for tracking the number of readings
# reading_counter = 0

# def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize struct in case of error
#     vitalsOutput = {}
#     vitalsOutput['breathRate'] = 0  # Initialize breathRate

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#         # Parse breathRate
#         vitalsOutput['breathRate'] = vitalsData[4]
#     except Exception as e:
#         log.error(f'ERROR: Vitals TLV Parsing Failed - {e}')
#         outputDict['vitals'] = vitalsOutput
#         return

#     # Advance tlv data pointer to end of this TLV
#     tlvData = tlvData[vitalsSize:]
#     outputDict['vitals'] = vitalsOutput

# def update_rolling_average(breath_rate):
#     global reading_counter

#     # Append new breath rate reading
#     breath_rate_readings.append(breath_rate)
#     reading_counter += 1

#     # Calculate and store rolling average when we have 50 new readings
#     if reading_counter == 40:
#         average = float(np.mean(breath_rate_readings))  # Convert to Python float
#         list_of_averages.append(average)
#         print(f"Rolling Average of Last 40 Readings: {average:.2f} BPM")
#         # Reset the counter after calculating the average
#         reading_counter = 0

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
    
#     # Output only the breathRate
#     if 'vitals' in outputDict and 'breathRate' in outputDict['vitals']:
#         breath_rate = outputDict['vitals']['breathRate']
#         print(f"Breath Rate: {breath_rate:.2f} BPM")
#         update_rolling_average(breath_rate)
        
#     # if 'vitals' in outputDict and 'heartRate' in outputDict['vitals']:
#     #     heart_rate = outputDict['vitals']['heartRate']
#     #     print(f"Breath Rate: {heart_rate:.2f} BPM")
#     #     update_rolling_average(heart_rate)
        
# def signal_handler(sig, frame):
#     print("\nTerminating...")
#     if list_of_averages:
#         print(f"List of Rolling Averages: {list_of_averages}")
#         print(f"Latest Rolling Average: {list_of_averages[-1]:.2f} BPM")
#     else:
#         print("No rolling averages recorded.")
#     sys.exit(0)


# def main():
#     comport = 'COM7'
#     baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
#     # Register signal handler for termination
#     signal.signal(signal.SIGINT, signal_handler)
#     signal.signal(signal.SIGTERM, signal_handler)
    
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
