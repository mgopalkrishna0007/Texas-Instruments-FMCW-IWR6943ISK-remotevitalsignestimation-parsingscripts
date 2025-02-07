# GIVES REAL TIME RANGE PROFILE PLOT

import serial
import numpy as np
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 32  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE

def parseRangeProfileTLV(tlvData, tlvLength, outputDict):
    rangeProfile = []
    rangeDataStruct = 'I'  # Each range bin gets a uint32_t
    rangeDataSize = struct.calcsize(rangeDataStruct)

    numRangeBins = int(len(tlvData) / rangeDataSize)
    for i in range(numRangeBins):
        # Read in single range bin data
        try:
            rangeBinData = struct.unpack(rangeDataStruct, tlvData[:rangeDataSize])
        except Exception as e:
            print(f'ERROR: Range Profile TLV Parser Failed To Parse Range Bin Number {i}: {e}')
            break
        rangeProfile.append(rangeBinData[0])

        # Move to next value
        tlvData = tlvData[rangeDataSize:]
    
    outputDict['rangeProfile'] = rangeProfile

def read_and_parse_data(serial_port, outputDict):
    byte_buffer = bytearray()

    if serial_port.in_waiting > 0:
        byte_buffer.extend(serial_port.read(serial_port.in_waiting))

        if len(byte_buffer) > EXPECTED_HEADER_SIZE:
            header = byte_buffer[:HEADER_SIZE]
            total_packet_length = int.from_bytes(header[12:16], byteorder='little')

            if len(byte_buffer) >= total_packet_length:
                data = byte_buffer[:total_packet_length]
                byte_buffer = byte_buffer[total_packet_length:]

                # Process TLV data
                tlvData = data[HEADER_SIZE:]  # Assuming TLV data starts after the header
                tlvLength = len(tlvData)

                # Parse Range Profile TLV
                parseRangeProfileTLV(tlvData, tlvLength, outputDict)

def animate(i, serial_port, ax, outputDict):
    read_and_parse_data(serial_port, outputDict)
    rangeProfile = outputDict.get('rangeProfile', [])
    
    if rangeProfile:
        ax.clear()
        ax.plot(rangeProfile, color='b')
        ax.set_xlabel('Range Bin')
        ax.set_ylabel('Intensity')
        ax.set_title('Real-Time Range Profile')
    else:
        print("No range profile data to plot")

def main():
    comport = 'COM7'
    baudrate = 921600  # Ensure this matches your radar sensor's baud rate

    outputDict = {
        'rangeProfile': []
    }

    fig, ax = plt.subplots()

    # Open serial port
    try:
        serial_port = serial.Serial(comport, baudrate=baudrate, timeout=0.1)
    except Exception as e:
        print(f"ERROR: Unable to open serial port {comport}: {e}")
        return

    ani = FuncAnimation(fig, animate, fargs=(serial_port, ax, outputDict), interval=100, blit=False)

    plt.show()

    serial_port.close()

if __name__ == "__main__":
    main()
