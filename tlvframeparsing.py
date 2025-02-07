import serial
import time
import struct
import numpy as np

# Define formats and sizes for frame header and TLV header
frame_header_format = 'QIIIHHIIIHH'
frame_header_size = struct.calcsize(frame_header_format)

tlv_header_format = 'II'
tlv_header_size = struct.calcsize(tlv_header_format)

def parsePointCloudTLV(tlvData, tlvLength, outputDict):
    print("Parsing Point Cloud TLV...")  # Debug statement
    pointStruct = '4f'  # X, Y, Z, and Doppler
    pointStructSize = struct.calcsize(pointStruct)
    
    # Check if TLV length is correctly aligned
    if tlvLength % pointStructSize != 0:
        print(f"ERROR: TLV Length {tlvLength} is not a multiple of Point Struct Size {pointStructSize}.")
        return
    
    numPoints = int(tlvLength / pointStructSize)
    pointCloud = np.zeros((numPoints, 4))  # Allocate space for points
    
    for i in range(numPoints):
        try:
            x, y, z, doppler = struct.unpack(pointStruct, tlvData[:pointStructSize])
            pointCloud[i] = [x, y, z, doppler]
            tlvData = tlvData[pointStructSize:]
        except struct.error as e:
            print(f'ERROR: Point Cloud TLV Parsing Failed at point {i}. Exception: {e}')
            numPoints = i
            break
            
    outputDict['numDetectedPoints'] = numPoints
    outputDict['pointCloud'] = pointCloud
    print(f"Point Cloud Parsing Complete. Number of Points: {numPoints}")  # Debug statement

def parse_frame_header(data):
    print("Parsing Frame Header...")  # Debug statement
    return struct.unpack(frame_header_format, data[:frame_header_size])

def parse_tlv_header(data):
    print("Parsing TLV Header...")  # Debug statement
    return struct.unpack(tlv_header_format, data[:tlv_header_size])

def handle_point_cloud(tlv_payload, tlv_length):
    print("Handling Point Cloud Data...")  # Debug statement
    outputDict = {
        'pointCloud': np.zeros((1000, 4)),  # Assuming a maximum of 1000 points
        'numDetectedPoints': 0
    }
    parsePointCloudTLV(tlv_payload, tlv_length, outputDict)
    num_points = outputDict['numDetectedPoints']
    point_cloud = outputDict['pointCloud']
    
    # Print the number of detected points
    print(f"Number of Detected Points: {num_points}")

    # Print the coordinates of each detected point
    if num_points > 0:
        print("Point Cloud Data (Sample):")
        for i in range(num_points):
            x, y, z, doppler = point_cloud[i]
            print(f"Point {i}: X={x:.2f}, Y={y:.2f}, Z={z:.2f}, Doppler={doppler:.2f}")
    else:
        print("No points detected.")

def handle_target_list(tlv_payload):
    print("Handling Target List data...")  # Debug statement
    # Add processing for Target List data here

def handle_target_index(tlv_payload):
    print("Handling Target Index data...")  # Debug statement
    # Add processing for Target Index data here

def handle_presence_indication(tlv_payload):
    print("Handling Presence Indication data...")  # Debug statement
    # Add processing for Presence Indication data here

def perform_fft(data):
    print("Performing FFT...")  # Debug statement
    fft_result = np.fft.fft(data)
    fft_freq = np.fft.fftfreq(len(fft_result))
    return fft_freq, np.abs(fft_result)

def main():
    comport = input("mmwave: Auxiliary Data port (Demo output DATA_port) = ")
    
    try:
        ser = serial.Serial(comport, 921600)
        print(f"Connected to {comport} at 921600 baud rate.")
    except serial.SerialException as e:
        print(f"Error: {e}")
        exit(1)

    buffer = bytearray()

    try:
        while True:
            if ser.in_waiting > 0:
                buffer.extend(ser.read(ser.in_waiting))
                
                while len(buffer) >= frame_header_size:
                    frame_header = parse_frame_header(buffer[:frame_header_size])
                    frame_length = frame_header[2]  # totalPacketLen
                    num_tlvs = frame_header[-1]  # numTLVs

                    print(f"Frame Header: {frame_header}")
                    print(f"Buffer Length: {len(buffer)}, Frame Length: {frame_length}")

                    if len(buffer) < frame_length:
                        print(f"Waiting for more data. Buffer length: {len(buffer)}, Frame length: {frame_length}")
                        break  # Wait for more data

                    offset = frame_header_size
                    
                    for i in range(num_tlvs):
                        if offset + tlv_header_size > frame_length:
                            print(f"Incomplete TLV header at TLV {i+1}")
                            break

                        tlv_header = parse_tlv_header(buffer[offset:offset + tlv_header_size])
                        tlv_type, tlv_length = tlv_header
                        offset += tlv_header_size

                        if offset + tlv_length > frame_length:
                            print(f"Incomplete TLV payload at TLV {i+1}. Expected Length: {tlv_length}, Available: {frame_length - offset}")
                            break

                        tlv_payload = buffer[offset:offset + tlv_length]
                        offset += tlv_length

                        print(f"TLV Type: {tlv_type}, TLV Length: {tlv_length}")

                        if tlv_type == 6:  # Point Cloud
                            handle_point_cloud(tlv_payload, tlv_length)
                        elif tlv_type == 7:  # Target List
                            handle_target_list(tlv_payload)
                        elif tlv_type == 8:  # Target Index
                            handle_target_index(tlv_payload)
                        elif tlv_type == 9:  # Presence Indication
                            handle_presence_indication(tlv_payload)
                    
                    buffer = buffer[frame_length:]  # Remove the processed frame from the buffer

            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nExiting program.")
    
    finally:
        ser.close()
        print("Serial port closed.")

if __name__ == "__main__":
    main()

# import serial
# import numpy as np
# import struct

# # Define sizes for header and packet (update these sizes based on your radar data format)
# HEADER_SIZE = 32  # Example size, replace with actual header size
# EXPECTED_HEADER_SIZE = HEADER_SIZE

# def parsePointCloudTLV(tlvData, tlvLength, outputDict):
#     pointCloud = outputDict['pointCloud']
#     pointStruct = '4f'  # X, Y, Z, and Doppler
#     pointStructSize = struct.calcsize(pointStruct)
#     numPoints = int(tlvLength / pointStructSize)

#     for i in range(numPoints):
#         try:
#             x, y, z, doppler = struct.unpack(pointStruct, tlvData[:pointStructSize])
#         except:
#             numPoints = i
#             print('ERROR: Point Cloud TLV Parsing Failed')
#             break
#         tlvData = tlvData[pointStructSize:]
#         pointCloud[i, 0] = x
#         pointCloud[i, 1] = y
#         pointCloud[i, 2] = z
#         pointCloud[i, 3] = doppler
#     outputDict['numDetectedPoints'], outputDict['pointCloud'] = numPoints, pointCloud

# def read_and_parse_data(serial_port):
#     byte_buffer = bytearray()
    
#     while True:
#         if serial_port.in_waiting > 0:
#             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
#             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
#                 header = byte_buffer[:HEADER_SIZE]
#                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
#                 if len(byte_buffer) >= total_packet_length:
#                     data = byte_buffer[:total_packet_length]
#                     byte_buffer = byte_buffer[total_packet_length:]
                    
#                     # Example processing of TLV data
#                     tlvData = data[HEADER_SIZE:]  # Assuming TLV data starts after the header
#                     tlvLength = len(tlvData)
                    
#                     # Initialize output dictionary for point cloud data
#                     outputDict = {
#                         'pointCloud': np.zeros((1000, 4))  # Adjust size based on your needs
#                     }
                    
#                     # Call parsePointCloudTLV function
#                     parsePointCloudTLV(tlvData, tlvLength, outputDict)
                    
#                     # Print parsed data
#                     print(f"Parsed Point Cloud Data: {outputDict}")

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



