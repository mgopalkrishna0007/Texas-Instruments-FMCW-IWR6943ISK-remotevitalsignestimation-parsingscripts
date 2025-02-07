import serial
import numpy as np
import struct
import logging
import matplotlib.pyplot as plt

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 40  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE
MMWDEMO_OUTPUT_MSG_VITALSIGNS = 1040


# Initialize logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

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
    
    # Output parsed data (for demonstration purposes)
    if 'vitals' in outputDict:
        print(f"Parsed Vital Signs: {outputDict['vitals']}")

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

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
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

