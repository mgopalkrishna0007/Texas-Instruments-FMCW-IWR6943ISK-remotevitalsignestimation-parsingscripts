import serial
import numpy as np
import struct
import logging
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define sizes for header and packet
HEADER_SIZE = 32
EXPECTED_HEADER_SIZE = HEADER_SIZE
MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Variables to store data for plotting
heart_waveform_data = []
breath_waveform_data = []

# Matplotlib setup
fig, (ax1, ax2) = plt.subplots(2, 1)
line1, = ax1.plot([], [], lw=2)
line2, = ax2.plot([], [], lw=2)
ax1.set_ylim(-1, 1)
ax2.set_ylim(-1, 1)
ax1.set_title('Heart Waveform')
ax2.set_title('Breath Waveform')

def init_plot():
    ax1.set_xlim(0, 30)
    ax2.set_xlim(0, 30)
    line1.set_data([], [])
    line2.set_data([], [])
    return line1, line2

def update_plot(frame):
    if heart_waveform_data:
        heart_data = np.array(heart_waveform_data[-30:])
        line1.set_data(np.arange(len(heart_data)), heart_data)
    if breath_waveform_data:
        breath_data = np.array(breath_waveform_data[-30:])
        line2.set_data(np.arange(len(breath_data)), breath_data)
    return line1, line2

def parseVitalSignsTLV(tlvData, tlvLength, outputDict):
    vitalsStruct = '2H33f'
    vitalsSize = struct.calcsize(vitalsStruct)
    
    vitalsOutput = {'id': 999, 'rangeBin': 0, 'breathDeviation': 0,
                    'heartRate': 0, 'breathRate': 0, 'heartWaveform': [], 'breathWaveform': []}

    try:
        vitalsData = struct.unpack(vitalsStruct, tlvData[:vitalsSize])
    except:
        log.error('ERROR: Vitals TLV Parsing Failed')
        outputDict['vitals'] = vitalsOutput
        return

    vitalsOutput['id'] = vitalsData[0]
    vitalsOutput['rangeBin'] = vitalsData[1]
    vitalsOutput['breathDeviation'] = vitalsData[2]
    vitalsOutput['heartRate'] = vitalsData[3]
    vitalsOutput['breathRate'] = vitalsData[4]
    vitalsOutput['heartWaveform'] = np.asarray(vitalsData[5:20])
    vitalsOutput['breathWaveform'] = np.asarray(vitalsData[20:35])

    tlvData = tlvData[vitalsSize:]
    outputDict['vitals'] = vitalsOutput

    heart_waveform_data.extend(vitalsOutput['heartWaveform'])
    breath_waveform_data.extend(vitalsOutput['breathWaveform'])

def read_and_parse_data(serial_port):
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
                    
                    process_tlv_data(data)

def process_tlv_data(data):
    tlv_header_size = 8
    tlv_data = data[HEADER_SIZE:]
    
    outputDict = {}
    
    while len(tlv_data) > tlv_header_size:
        try:
            tlvType, tlvLength = struct.unpack('2I', tlv_data[:tlv_header_size])
            tlv_data = tlv_data[tlv_header_size:]
            
            if tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS:
                parseVitalSignsTLV(tlv_data[:tlvLength], tlvLength, outputDict)
            
            tlv_data = tlv_data[tlvLength:]
        
        except Exception as e:
            log.error(f'Failed to process TLV data: {e}')
            break
    
    if 'vitals' in outputDict:
        print(f"Parsed Vital Signs: {outputDict['vitals']}")

def main():
    comport = 'COM7'
    baudrate = 921600
    
    try:
        serial_port = serial.Serial(comport, baudrate=baudrate, timeout=1)
        print(f"Connected to {comport} at {baudrate} baud rate.")
        
        ani = FuncAnimation(fig, update_plot, init_func=init_plot, blit=True, interval=100)
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
    plt.show()
    main()
