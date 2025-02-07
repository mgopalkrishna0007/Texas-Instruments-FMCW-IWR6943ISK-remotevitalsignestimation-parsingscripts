# saves the point cloud data in a csv file , with x , y , z and doppler
 
import serial
import numpy as np
import struct
import csv
import os

# Define sizes for header and packet (update these sizes based on your radar data format)
HEADER_SIZE = 32  # Example size, replace with actual header size
EXPECTED_HEADER_SIZE = HEADER_SIZE
CSV_FILE_PATH = '/path/to/your/directory/point_cloud_data_2m1.csv'  # Path to save CSV file

def parsePointCloudTLV(tlvData, tlvLength, outputDict):
    pointCloud = outputDict['pointCloud']
    pointStruct = '4f'  # X, Y, Z, and Doppler
    pointStructSize = struct.calcsize(pointStruct)
    numPoints = int(tlvLength / pointStructSize)

    for i in range(numPoints):
        try:
            x, y, z, doppler = struct.unpack(pointStruct, tlvData[:pointStructSize])
        except:
            numPoints = i
            print('ERROR: Point Cloud TLV Parsing Failed')
            break
        tlvData = tlvData[pointStructSize:]
        pointCloud[i, 0] = x
        pointCloud[i, 1] = y
        pointCloud[i, 2] = z
        pointCloud[i, 3] = doppler
    outputDict['numDetectedPoints'], outputDict['pointCloud'] = numPoints, pointCloud

def save_to_csv(data, file_path):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['X', 'Y', 'Z', 'Doppler'])  # Write header if file does not exist
        for point in data:
            if not np.array_equal(point, [0, 0, 0, 0]):  # Avoid writing empty rows
                writer.writerow(point)

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
                    
                    # Example processing of TLV data
                    tlvData = data[HEADER_SIZE:]  # Assuming TLV data starts after the header
                    tlvLength = len(tlvData)
                    
                    # Initialize output dictionary for point cloud data
                    outputDict = {
                        'pointCloud': np.zeros((1000, 4))  # Adjust size based on your needs
                    }
                    
                    # Call parsePointCloudTLV function
                    parsePointCloudTLV(tlvData, tlvLength, outputDict)
                    
                    # Save parsed data to CSV
                    save_to_csv(outputDict['pointCloud'], CSV_FILE_PATH)
                    
                    # Print parsed data
                    print(f"Parsed Point Cloud Data: {outputDict}")

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





#######################################################################################################################################
#######################################################################################################################################

# # gives the point cloud array of the radar realtime

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


#######################################################################################################################################
#######################################################################################################################################


# # # also gives point cloud array of the radar 
# # import serial
# # import numpy as np
# # import struct

# # # Define sizes for header and packet (update these sizes based on your radar data format)
# # HEADER_SIZE = 32  # Example size, replace with actual header size
# # EXPECTED_HEADER_SIZE = HEADER_SIZE

# # def parsePointCloudTLV(tlvData, tlvLength, outputDict):
# #     pointCloud = outputDict['pointCloud']
# #     pointStruct = '4f'  # X, Y, Z, and Doppler
# #     pointStructSize = struct.calcsize(pointStruct)
# #     numPoints = int(tlvLength / pointStructSize)

# #     for i in range(numPoints):
# #         try:
# #             x, y, z, doppler = struct.unpack(pointStruct, tlvData[:pointStructSize])
# #         except:
# #             numPoints = i
# #             print('ERROR: Point Cloud TLV Parsing Failed')
# #             break
# #         tlvData = tlvData[pointStructSize:]
# #         pointCloud[i, 0] = x
# #         pointCloud[i, 1] = y
# #         pointCloud[i, 2] = z
# #         pointCloud[i, 3] = doppler
# #     outputDict['numDetectedPoints'], outputDict['pointCloud'] = numPoints, pointCloud

# # def read_and_parse_data(serial_port):
# #     byte_buffer = bytearray()
    
# #     while True:
# #         if serial_port.in_waiting > 0:
# #             byte_buffer.extend(serial_port.read(serial_port.in_waiting))
            
# #             if len(byte_buffer) > EXPECTED_HEADER_SIZE:
# #                 header = byte_buffer[:HEADER_SIZE]
# #                 total_packet_length = int.from_bytes(header[12:16], byteorder='little')
                
# #                 if len(byte_buffer) >= total_packet_length:
# #                     data = byte_buffer[:total_packet_length]
# #                     byte_buffer = byte_buffer[total_packet_length:]
                    
# #                     # Example processing of TLV data
# #                     tlvData = data[HEADER_SIZE:]  # Assuming TLV data starts after the header
# #                     tlvLength = len(tlvData)
                    
# #                     # Initialize output dictionary for point cloud data
# #                     outputDict = {
# #                         'pointCloud': np.zeros((1000, 4))  # Adjust size based on your needs
# #                     }
                    
# #                     # Call parsePointCloudTLV function
# #                     parsePointCloudTLV(tlvData, tlvLength, outputDict)
                    
# #                     # Print parsed data
# #                     print(f"Parsed Point Cloud Data: {outputDict}")

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



