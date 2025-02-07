# import serial
# import sys

# def main():
#     comport = input("data port = ")
#     try:
#         ser = serial.Serial(comport, 921600, timeout=1)
#         print(f"Connected to {comport} at 921600 baud.")
#     except serial.SerialException as e:
#         print(f"Error: {e}")
#         sys.exit(1)
    
#     try:
#         while True:
#             if ser.in_waiting > 0:
#                 bytecount = ser.in_waiting  # Corrected this line
#                 s = ser.read(bytecount)
#                 print(s.decode('utf-8', errors='ignore'))  # Decode bytes to string
#     except KeyboardInterrupt:
#         print("\nInterrupted by user.")
#     finally:
#         ser.close()
#         print("Serial port closed.")

# if __name__ == "__main__":
#     main()


import struct
import time
import serial
import logging
import signal
import sys
import csv

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 40  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE

# Define the configuration file path
radarCfgFile = r'C:\Users\GOPAL\Downloads\xwr68xx_profile_2024_09_03T12_08_49_816.cfg'

# Define the CLI and Data serial ports
cliSerialPort = 'COM3'  # Command Line Interface (CLI) port (change as per your setup)
dataSerialPort = 'COM7'  # Data port (change as per your setup)

# Define the CSV file path
csvFilePath = r'C:\path\to\your\directory\Indoor1.csv'

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

def parseRangeProfile(data, tlvLength, frameNum, csv_writer):
    """Parses the range profile from the TLV section and writes to CSV."""
    print("Range Profile Data:")
    for i in range(tlvLength // 2):  # Assuming each range profile entry is 2 bytes
        rangeProfile = struct.unpack('H', data[2 * i:2 * i + 2])[0]
        amplitude = rangeProfile * 1.0 * 6 / 8 / (1 << 8)  # Adjust scaling as per radar specification
        print(f"Range Profile[{i}]: {amplitude:07.3f}")
        # Write data to CSV
        csv_writer.writerow([frameNum, i, amplitude])

def parseTLVs(data, frameNum, csv_writer):
    """Parses the TLV sections from the raw data and writes to CSV."""
    offset = 0
    while offset < len(data):
        try:
            tlvType, tlvLength = tlvHeaderDecode(data[offset:offset + 8])
            offset += 8
            tlvData = data[offset:offset + tlvLength]
            offset += tlvLength
            
            if tlvType == 2:  # TLV Type for Range Profile
                parseRangeProfile(tlvData, tlvLength, frameNum, csv_writer)
        except struct.error as e:
            print("Error parsing TLV:", e)
            break

def parsePacket(packet, csv_writer):
    """Parses an entire packet starting from the magic number and writes to CSV."""
    if len(packet) < HEADER_SIZE:
        print("Error: Packet too short.")
        return

    header = packet[:HEADER_SIZE]
    try:
        magic, version, totalPacketLength, platform, frameNum, cpuCycles, numObj, numTLVs = struct.unpack('Q7I', header[:36])
    except struct.error as e:
        print("Error unpacking header:", e)
        return

    print(f"Packet Frame Number: {frameNum}")

    # Check if the total length of the packet is correct
    if len(packet) < totalPacketLength:
        print("Error: Packet length mismatch.")
        return

    data = packet[HEADER_SIZE:totalPacketLength]
    parseTLVs(data, frameNum, csv_writer)

def read_and_print_data(dataDevice, csv_writer):
    """Reads data from the radar device and parses it in real-time."""
    byte_buffer = bytearray()
    magicWord = b'\x02\x01\x04\x03\x06\x05\x08\x07'  # Replace with your radar's actual magic word
    
    while True:
        if dataDevice.in_waiting > 0:
            byte_buffer.extend(dataDevice.read(dataDevice.in_waiting))
            
            # Check for the presence of the magic word
            magicWordIdx = byte_buffer.find(magicWord)
            while magicWordIdx != -1:
                if len(byte_buffer) > EXPECTED_HEADER_SIZE:
                    header = byte_buffer[magicWordIdx:magicWordIdx + HEADER_SIZE]
                    try:
                        total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                    except IndexError:
                        print("Error: Header parsing issue.")
                        byte_buffer.clear()
                        break
                    
                    if len(byte_buffer) >= magicWordIdx + total_packet_length:
                        # Extract a complete packet from the buffer
                        data = byte_buffer[magicWordIdx:magicWordIdx + total_packet_length]
                        byte_buffer = byte_buffer[magicWordIdx + total_packet_length:]
                        
                        # Parse the extracted packet
                        parsePacket(data, csv_writer)
                    else:
                        print("Warning: Incomplete packet data.")
                        break
                else:
                    print("Warning: Incomplete header data.")
                    break
                
                # Search for the next occurrence of the magic word
                magicWordIdx = byte_buffer.find(magicWord)
            
            # Optionally add a small delay to prevent overwhelming the system
            time.sleep(0.01)

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
        
        # Open CSV file for writing
        with open(csvFilePath, 'w', newline='') as csvFile:
            csv_writer = csv.writer(csvFile)
            # Write header row
            csv_writer.writerow(['Frame Number', 'Range Profile Index', 'Amplitude'])
            
            # Start reading and printing raw data from the sensor
            print(f"Connected to {dataSerialPort} at 921600 baud rate.")
            read_and_print_data(dataDevice, csv_writer)

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
