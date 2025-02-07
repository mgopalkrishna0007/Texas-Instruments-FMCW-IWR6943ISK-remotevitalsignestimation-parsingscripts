# this code recieves data from IWR6843ISK and ouputs the following :
# 1) realtime breathrate and heartrate output , and waveforms with hodling breath trigger. add the thresholding. 
# 2) rolling average of last 40 readings (adjustable , refer to "if reading_counter == 40:"). 
# 3) lastly when the code is terminated , it out puts a list of all the rolling average values in a list called "print(f"List of Rolling Averages: {list_of_averages}").
# 4) also prints out the latest value of the element appended in the above list (latest rolling average).import serial.

import numpy as np
import struct
import logging
import time
import serial
import signal
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import sys

# Configuration file path
radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# Serial port names for CLI and Data ports
cliSerialPort = 'COM3'  # CLI port for sending configuration
dataSerialPort = 'COM7'  # Data port for receiving sensor data
# cliSerialPort = '/dev/ttyUSB0'  # CLI port for sending configuration
# dataSerialPort = '/dev/ttyUSB1'  # Data port for receiving sensor data

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 32  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE
MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Initialize plots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
heart_line, = ax1.plot([], [], lw=2, label='Heart Waveform')
breath_line, = ax2.plot([], [], lw=2, label='Breath Waveform')
ax1.set_ylim(-2, 2)  # Set y-axis limits for Heart Waveform
ax2.set_ylim(-2, 2)  # Set y-axis limits for Breath Waveform
ax1.set_xlabel('Sample')
ax1.set_ylabel('Amplitude')
ax2.set_xlabel('Sample')
ax2.set_ylabel('Amplitude')
ax1.legend()
ax2.legend()
ax1.grid()
ax2.grid()

# Buffers for waveforms and readings
heart_waveform_buffer = []
breath_waveform_buffer = []
breath_rate_readings = deque(maxlen=40)
heart_rate_readings = deque(maxlen=40)

# Lists to store rolling averages
list_of_breath_averages = []
list_of_heart_averages = []
reading_counter = 0

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

    # Extract breath rate and heart rate
    breathRate = vitalsData[4]
    heartRate = vitalsData[3]

    return heartWaveform, breathWaveform, breathRate, heartRate

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
    tlv_header_size = 8
    tlv_data = data[HEADER_SIZE:]
    
    while len(tlv_data) > tlv_header_size:
        try:
            # Decode TLV header
            tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
            tlv_data = tlv_data[tlv_header_size:]
            
            # Parse TLV data based on type
            if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
                heartWaveform, breathWaveform, breathRate, heartRate = parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength)
                
                # Append new data to buffers
                heart_waveform_buffer.extend(heartWaveform)
                breath_waveform_buffer.extend(breathWaveform)
                
                # Check if breath waveform indicates holding breath
                holding_breath = all(-0.1 <= val <= 0.1 for val in breath_waveform_buffer[-10:])  # Last 10 samples

                # Update the plot with new data
                update_plot()

                # Output breath rate and heart rate, handle holding breath
                print(f"Heart Rate: {heartRate:.2f} BPM")
                if holding_breath:
                    print("Breath Rate: Not Detected (Holding Breath)")
                else:
                    print(f"Breath Rate: {breathRate:.2f} BPM")

                # Update rolling averages for breath rate and heart rate
                update_rolling_average(breathRate, heartRate, holding_breath)
            
            # Move to next TLV
            tlv_data = tlv_data[tlvLength:]
        
        except Exception as e:
            log.error(f'Failed to process TLV data: {e}')
            break

def update_rolling_average(breath_rate, heart_rate, holding_breath):
    global reading_counter

    # Append new breath rate and heart rate readings
    heart_rate_readings.append(heart_rate)

    # Only append breath rate if not holding breath
    if not holding_breath:
        breath_rate_readings.append(breath_rate)

    reading_counter += 1

    # Calculate and store rolling averages when we have 40 new readings
    if reading_counter == 40:
        breath_average = float(np.mean(breath_rate_readings)) if breath_rate_readings else 'Not Detected'
        heart_average = float(np.mean(heart_rate_readings))
        
        if breath_average != 'Not Detected':
            list_of_breath_averages.append(breath_average)
        list_of_heart_averages.append(heart_average)

        print(f"Rolling Average of Last 40 Breath Readings: {breath_average if breath_average != 'Not Detected' else 'Not Detected'} BPM")
        print(f"Rolling Average of Last 40 Heart Readings: {heart_average:.2f} BPM")
        
        reading_counter = 0

def update_plot():
    """Update the plot with new data and print the current waveforms."""
    global breath_waveform_buffer
    
    heart_line.set_ydata(heart_waveform_buffer)
    breath_line.set_ydata(breath_waveform_buffer)
    
    heart_line.set_xdata(np.arange(len(heart_waveform_buffer)))
    breath_line.set_xdata(np.arange(len(breath_waveform_buffer)))
    
    # Adjust x-axis limits to show data from 0 to the current length
    ax1.set_xlim(0, len(heart_waveform_buffer))
    ax2.set_xlim(0, len(breath_waveform_buffer))
    
    # Adjust y-axis limits to fit all data
    ax1.set_ylim(min(heart_waveform_buffer) - 1, max(heart_waveform_buffer) + 1)
    ax2.set_ylim(min(breath_waveform_buffer) - 1, max(breath_waveform_buffer) + 1)
    
    # Refresh the plot
    fig.canvas.draw()
    fig.canvas.flush_events()

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
    if list_of_breath_averages:
        print(f"List of all Rolling Breath Averages: {list_of_breath_averages}")
        print(f"Latest Rolling Breath Average : {list_of_breath_averages[-1]:.2f} BPM")
    if list_of_heart_averages:
        print(f"List of all Rolling Heart Averages: {list_of_heart_averages}")
        print(f"Latest Rolling Heart Average: {list_of_heart_averages[-1]:.2f} BPM")
    sys.exit(0)

def main():
    """Main function to set up serial communication and start data reading."""
    try:
        # Open serial ports for CLI and Data
        cliDevice = serial.Serial(cliSerialPort, 115200, timeout=0.5)
        dataDevice = serial.Serial(dataSerialPort, 921600, timeout=0.5)
        
        # Send configuration to sensor
        send_config_to_sensor(cliDevice, radarCfgFile)
        
        # Register signal handler for graceful termination
        signal.signal(signal.SIGINT, signal_handler)

        # Set up real-time plot animation
        ani = animation.FuncAnimation(fig, update_plot, interval=1000)
        plt.show(block=False)
        
        # Read and parse data from the sensor in real-time
        read_and_parse_data(dataDevice)

    except Exception as e:
        log.error(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

##################################################################################################################################
##################################################################################################################################


# this code recieves data from IWR6843ISK and ouputs the following :
# 1) realtime breathrate and heartrate output.
# 2) rolling average of last 40 readings (adjustable , refer to "if reading_counter == 40:"). 
# 3) lastly when the code is terminated , it out puts a list of all the rolling average values in a list called "print(f"List of Rolling Averages: {list_of_averages}")
# 4) also prints out the latest value of the element appended in the above list (latest rolling average).

# import struct
# import time
# import serial
# import numpy as np
# import logging
# from collections import deque
# import signal
# import sys
# import matplotlib.pyplot as plt
# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Define the configuration file path for 2 meteres
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'
 
# # Define the configuration file path for 6 meteres
# # radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_6m.cfg'

# # Define the CLI and Data serial ports for windows 
# cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
# dataSerialPort = 'COM7'  # Data port (change as per your setup)

# # Define the ports for ubuntu  
# # cliSerialPort = '/dev/ttyUSB0'  # Command Line Interface (CLI) port (change as per your setup)
# # dataSerialPort = '/dev/ttyUSB1'  # Data port (change as per your setup)

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # Lists to store breath rate and heart rate readings
# breath_rate_readings = deque(maxlen=40)
# heart_rate_readings = deque(maxlen=40)

# # Lists to store calculated rolling averages
# list_of_breath_averages = []
# list_of_heart_averages = []

# # Counter for tracking the number of readings
# reading_counter = 0

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

# def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
#     vitalsStruct = '2H33f'
#     vitalsSize = struct.calcsize(vitalsStruct)
    
#     # Initialize struct in case of error
#     vitalsOutput = {}
#     vitalsOutput['breathRate'] = 0  # Initialize breathRate
#     vitalsOutput['heartRate'] = 0   # Initialize heartRate

#     # Capture data for active patient
#     try:
#         vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
#         # Parse breathRate and heartRate
#         vitalsOutput['breathRate'] = vitalsData[4]
#         vitalsOutput['heartRate'] = vitalsData[3]
#     except Exception as e:
#         log.error(f'ERROR: Vitals TLV Parsing Failed - {e}')
#         outputDict['vitals'] = vitalsOutput
#         return
#     tlvData = tlvData[vitalsSize:] # Advance tlv data pointer to end of this TLV
#     outputDict['vitals'] = vitalsOutput

# def update_rolling_average(breath_rate, heart_rate):
#     global reading_counter

#     # Append new breath rate and heart rate readings
#     breath_rate_readings.append(breath_rate)
#     heart_rate_readings.append(heart_rate)
#     reading_counter += 1

#     # Calculate and store rolling averages when we have 40 new readings
#     if reading_counter == 40:
#         breath_average = float(np.mean(breath_rate_readings))  # Convert to Python float
#         heart_average = float(np.mean(heart_rate_readings))  # Convert to Python float
        
#         list_of_breath_averages.append(breath_average)
#         list_of_heart_averages.append(heart_average)

#         print(f"Rolling Average of Last 40 Breath Readings: {breath_average:.2f} BPM")
#         print(f"Rolling Average of Last 40 Heart Readings: {heart_average:.2f} BPM")
        
#         # Reset the counter after calculating the averages
#         reading_counter = 0

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
    
#     # Output both the breathRate and heartRate
#     if 'vitals' in outputDict:
#         breath_rate = outputDict['vitals'].get('breathRate', 0)
#         heart_rate = outputDict['vitals'].get('heartRate', 0)
#         print(f"Breath Rate: {breath_rate:.2f} BPM")
#         print(f"Heart Rate: {heart_rate:.2f} BPM")
#         update_rolling_average(breath_rate, heart_rate)

# def read_and_parse_data(dataDevice):
#     byte_buffer = bytearray()
    
#     while True:
#         if dataDevice.in_waiting > 0:
#             byte_buffer.extend(dataDevice.read(dataDevice.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def signal_handler(sig, frame):
#     print("\nTerminating...")
#     if list_of_breath_averages:
#         print(f"List of Rolling Breath Averages: {list_of_breath_averages}")
#         print(f"Latest Rolling Breath Average: {list_of_breath_averages[-1]:.2f} BPM")
#     if list_of_heart_averages:
#         print(f"List of Rolling Heart Averages: {list_of_heart_averages}")
#         print(f"Latest Rolling Heart Average: {list_of_heart_averages[-1]:.2f} BPM")
#     else:
#         print("No rolling averages recorded.")
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
#         print("Serial port closed.")

# if __name__ == "__main__":
#     main()



####################################################################################################################################
####################################################################################################################################



# # # # this code recieves data from IWR6843ISK and ouputs the following :
# # # 1) realtime breathrate output only. 
# # # 2) rolling average of last 40 readings (adjustable , refer to "if reading_counter == 40:").
# # # 3) lastly when the code is terminated , it out puts a list of all the rolling average values in a list called "print(f"List of Rolling Averages: {list_of_averages}").
# # # 4) also prints out the latest value of the element appended in the above list (latest rolling average).

# import struct
# import time
# import serial
# import numpy as np
# import logging
# from collections import deque
# import signal
# import sys

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Define the configuration file path
# radarCfgFile = r'C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg'

# # Define the CLI and Data serial ports for windows
# cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
# dataSerialPort = 'COM7'  # Data port (change as per your setup)

# # for ubuntu 
# # cliSerialPort = '/dev/ttyUSB0'  # Command Line Interface (CLI) port (change as per your setup)
# # dataSerialPort = '/dev/ttyUSB1'  # Data port (change as per your setup)

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # List to store breath rate readings
# breath_rate_readings = deque(maxlen=4)
# # List to store calculated rolling averages
# list_of_averages = []
# # Counter for tracking the number of readings
# reading_counter = 0

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

#     # Calculate and store rolling average when we have 40 new readings
#     if reading_counter == 40:
#         average = float(np.mean(breath_rate_readings))  # Convert to Python float
#         list_of_averages.append(average)
#         print(f"Rolling Average of Last 40 Readings: {average:.2f} BPM")
#         # Reset the counter after calculating the average
#         reading_counter = 0

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

# def read_and_parse_data(dataDevice):
#     byte_buffer = bytearray()
    
#     while True:
#         if dataDevice.in_waiting > 0:
#             byte_buffer.extend(dataDevice.read(dataDevice.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 # Example parsing logic
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Process TLV data
#                     process_tlv_data(data)

# def signal_handler(sig, frame):
#     print("\nTerminating...")
#     if list_of_averages:
#         print(f"List of Rolling Averages: {list_of_averages}")
#         print(f"Latest Rolling Average: {list_of_averages[-1]:.2f} BPM")
#     else:
#         print("No rolling averages recorded.")
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
#         print("Serial port closed.")

# if __name__ == "__main__":
#     main()


