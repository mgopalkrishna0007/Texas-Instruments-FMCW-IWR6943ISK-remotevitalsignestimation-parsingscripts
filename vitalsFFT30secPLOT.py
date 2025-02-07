# plots the vitals wavefrom of both heart and breath , along with FFT on it , overlapped of 30 secconds

import serial
import numpy as np
import struct
import logging
import matplotlib.pyplot as plt

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 32  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE
MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# List to hold 30 readings for plotting
heart_waveform_readings = []
breath_waveform_readings = []

def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
    vitalsStruct = '2H33f'
    vitalsSize = struct.calcsize(vitalsStruct)
    
    # Initialize struct in case of error
    vitalsOutput = {}
    vitalsOutput['id'] = 999
    vitalsOutput['rangeBin'] = 0
    vitalsOutput['breathDeviation'] = 0
    vitalsOutput['heartRate'] = 0
    vitalsOutput['breathRate'] = 0
    vitalsOutput['heartWaveform'] = []
    vitalsOutput['breathWaveform'] = []

    # Capture data for active patient
    try:
        vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
    except:
        log.error('ERROR: Vitals TLV Parsing Failed')
        outputDict['vitals'] = vitalsOutput
        return

    # Parse this patient's data
    vitalsOutput['id'] = vitalsData[0]
    vitalsOutput['rangeBin'] = vitalsData[1]
    vitalsOutput['breathDeviation'] = vitalsData[2]
    vitalsOutput['heartRate'] = vitalsData[3]
    vitalsOutput['breathRate'] = vitalsData[4]
    vitalsOutput['heartWaveform'] = np.asarray(vitalsData[5:20])
    vitalsOutput['breathWaveform'] = np.asarray(vitalsData[20:35])

    # Advance tlv data pointer to end of this TLV
    tlvData = tlvData[vitalsSize:]
    outputDict['vitals'] = vitalsOutput

def read_and_parse_data(serial_port):
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
    global heart_waveform_readings, breath_waveform_readings
    # Define TLV header size and initialize parsing
    tlv_header_size = 8
    tlv_data = data[HEADER_SIZE:]
    
    outputDict = {}
    
    while len(tlv_data) > tlv_header_size:
        try:
            # Decode TLV header
            tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
            tlv_data = tlv_data[tlv_header_size:]
            
            # Parse TLV data based on type
            if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
                parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength, outputDict)
            
            # Move to next TLV
            tlv_data = tlv_data[tlvLength:]
        
        except Exception as e:
            log.error(f'Failed to process TLV data: {e}')
            break
    
    # Collect data for 30 readings
    if 'vitals' in outputDict:
        heart_waveform_readings.append(outputDict['vitals']['heartWaveform'])
        breath_waveform_readings.append(outputDict['vitals']['breathWaveform'])
        
        if len(heart_waveform_readings) >= 30:
            plot_waveforms_and_fft(heart_waveform_readings, breath_waveform_readings)
            heart_waveform_readings.clear()
            breath_waveform_readings.clear()

def plot_waveforms_and_fft(heart_waveform_readings, breath_waveform_readings):
    # Convert list of arrays into a 2D array for plotting
    heart_waveforms = np.array(heart_waveform_readings)
    breath_waveforms = np.array(breath_waveform_readings)
    
    # FFT calculation
    def calculate_fft(data):
        n = len(data)
        fft_data = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(n)
        return fft_freq, np.abs(fft_data)

    plt.figure(figsize=(18, 12))  # Increase figure size for better visibility

    # Plot heart waveforms
    plt.subplot(4, 2, 1)
    plt.title('Heart Waveforms Over 30 Readings')
    plt.plot(heart_waveforms.T, alpha=0.7)  # Transpose to plot each reading
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.xlim(0, heart_waveforms.shape[1] - 1)  # Adjust x-axis limit based on number of samples

    # Plot FFT of heart waveforms
    plt.subplot(4, 2, 2)
    plt.title('FFT of Heart Waveforms')
    for waveform in heart_waveforms:
        freq, fft_values = calculate_fft(waveform)
        plt.plot(freq, fft_values, alpha=0.7)
    plt.xlabel('Frequency')
    plt.ylabel('Magnitude')
    plt.xlim(0, 0.5)  # Typically, the significant frequencies are in the [0, 0.5] range

    # Plot breath waveforms
    plt.subplot(4, 2, 3)
    plt.title('Breath Waveforms Over 30 Readings')
    plt.plot(breath_waveforms.T, alpha=0.7)  # Transpose to plot each reading
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.xlim(0, breath_waveforms.shape[1] - 1)  # Adjust x-axis limit based on number of samples

    # Plot FFT of breath waveforms
    plt.subplot(4, 2, 4)
    plt.title('FFT of Breath Waveforms')
    for waveform in breath_waveforms:
        freq, fft_values = calculate_fft(waveform)
        plt.plot(freq, fft_values, alpha=0.7)
    plt.xlabel('Frequency')
    plt.ylabel('Magnitude')
    plt.xlim(0, 0.5)  # Typically, the significant frequencies are in the [0, 0.5] range

    plt.tight_layout()
    plt.show()

def main():
    comport = 'COM7'
    baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
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
# import logging
# import matplotlib.pyplot as plt

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE
# MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)

# # List to hold 30 readings for plotting
# heart_waveform_readings = []
# breath_waveform_readings = []

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
#     global heart_waveform_readings, breath_waveform_readings
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
    
#     # Collect data for 30 readings
#     if 'vitals' in outputDict:
#         heart_waveform_readings.append(outputDict['vitals']['heartWaveform'])
#         breath_waveform_readings.append(outputDict['vitals']['breathWaveform'])
        
#         if len(heart_waveform_readings) >= 30:
#             plot_waveforms(heart_waveform_readings, breath_waveform_readings)
#             heart_waveform_readings.clear()
#             breath_waveform_readings.clear()

# def plot_waveforms(heart_waveform_readings, breath_waveform_readings):
#     # Convert list of arrays into a 2D array for plotting
#     heart_waveforms = np.array(heart_waveform_readings)
#     breath_waveforms = np.array(breath_waveform_readings)
    
#     plt.figure(figsize=(16, 8))  # Increase figure size for better visibility

#     # Plot heart waveforms
#     plt.subplot(2, 1, 1)
#     plt.title('Heart Waveforms Over 30 Readings')
#     plt.plot(heart_waveforms.T, alpha=0.7)  # Transpose to plot each reading
#     plt.xlabel('Sample Index')
#     plt.ylabel('Amplitude')
#     plt.xlim(0, heart_waveforms.shape[1] - 1)  # Adjust x-axis limit based on number of samples

#     # Plot breath waveforms
#     plt.subplot(2, 1, 2)
#     plt.title('Breath Waveforms Over 30 Readings')
#     plt.plot(breath_waveforms.T, alpha=0.7)  # Transpose to plot each reading
#     plt.xlabel('Sample Index')
#     plt.ylabel('Amplitude')
#     plt.xlim(0, breath_waveforms.shape[1] - 1)  # Adjust x-axis limit based on number of samples

#     plt.tight_layout()
#     plt.show()

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

