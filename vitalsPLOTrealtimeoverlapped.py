#gives the waveform plot in 30 seccond and updates in realtime (overlapped) 


import serial
import numpy as np
import struct
import logging
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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
            update_plots(heart_waveform_readings, breath_waveform_readings)

def update_plots(heart_waveform_readings, breath_waveform_readings):
    # Convert list of arrays into a 2D array for plotting
    heart_waveforms = np.array(heart_waveform_readings)
    breath_waveforms = np.array(breath_waveform_readings)
    
    # Clear the previous figure and axis
    plt.clf()

    # Plot heart waveforms
    plt.subplot(2, 1, 1)
    plt.title('Heart Waveforms Over 30 Readings')
    for i in range(heart_waveforms.shape[0]):
        plt.plot(heart_waveforms[i], alpha=0.7)
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')

    # Plot breath waveforms
    plt.subplot(2, 1, 2)
    plt.title('Breath Waveforms Over 30 Readings')
    for i in range(breath_waveforms.shape[0]):
        plt.plot(breath_waveforms[i], alpha=0.7)
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.draw()
    plt.pause(0.1)

def main():
    comport = 'COM7'
    baudrate = 921600  # Ensure this matches your radar sensor's baud rate
    
    try:
        serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
        print(f"Connected to {comport} at {baudrate} baud rate.")
        
        plt.ion()  # Enable interactive mode for real-time updating
        
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
