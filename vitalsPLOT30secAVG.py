# gives the average 30 seccond overlapped plot of wavefroms 

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
            plot_average_waveforms(heart_waveform_readings, breath_waveform_readings)
            heart_waveform_readings.clear()
            breath_waveform_readings.clear()

def plot_average_waveforms(heart_waveform_readings, breath_waveform_readings):
    # Convert list of arrays into a 2D array for averaging
    heart_waveforms = np.array(heart_waveform_readings)
    breath_waveforms = np.array(breath_waveform_readings)
    
    # Compute the average across the collected readings
    avg_heart_waveform = np.mean(heart_waveforms, axis=0)
    avg_breath_waveform = np.mean(breath_waveforms, axis=0)
    
    plt.figure(figsize=(14, 6))

    # Plot average heart waveform
    plt.subplot(2, 1, 1)
    plt.title('Average Heart Waveform Over 30 Readings')
    plt.plot(avg_heart_waveform, alpha=0.7)
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')

    # Plot average breath waveform
    plt.subplot(2, 1, 2)
    plt.title('Average Breath Waveform Over 30 Readings')
    plt.plot(avg_breath_waveform, alpha=0.7)
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')

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

















# import binascii

# import serial
# import numpy as np
# # import cv2
# import queue
# import struct

# cnt = 0
# i = 0
# synPattern = [0x02, 0x01, 0x04, 0x03, 0x06, 0x05, 0x08, 0x07]
# mmWaveUARTData = serial.Serial("COM7", 921600, timeout=3.0)
# while True:
#     header = mmWaveUARTData.read(48)
#     sync1, sync2, sync3, sync4, sync5, sync6, sync7, sync8, version, totalPacketLen, platform, frameNumber, subFrameNumber, chirpProcessingMargin, frameProcssingMargin, trackProcessTime, uartSentTiem, numTLVs, checksum = struct.unpack('8B9I2H', header)
#     if sync1 == 0x02 and sync2 == 0x01 and sync3 == 0x04 and sync4 == 0x03 and sync5 == 0x06 and sync6 == 0x05 and sync7 == 0x08 and sync8 == 0x07:
#         print("#################################### found header ##################################")
#         print("total length : {}".format(totalPacketLen))
#         print("frame number : {}".format(frameNumber))
#         print("no of TLVs : {}".format(numTLVs))
#         data = mmWaveUARTData.read(totalPacketLen - 48)
#         if data == b'':
#             continue
#         if numTLVs < 1:
#             continue

#         cnt = numTLVs
#         while True:
#             print("********* tlv cnt : {}".format(cnt))
#             tlvType, tlvLength = struct.unpack('2I', data[:8])
#             print("tlvType : {}".format(tlvType))
#             print("tlvLength : {}".format(tlvLength))
#             data1 = data[8:]
#             if tlvType > 20:
#                 break
#             if tlvType == 0x06:
#                 pointCloud = data[8:tlvLength]
#                 if ((tlvLength - 28) % 8) != 0:
#                     break
#                 else:
#                     #print(data[8:tlvLength])
#                     elevationUnit, azimuthUnit, dopplerUnit, rangeUnit, snrUnit = struct.unpack('5f', pointCloud[:20])
#                     print("elevationUnit : {}".format(elevationUnit))
#                     print("azimuthUnit : {}".format(azimuthUnit))
#                     print("dopplerUnit : {}".format(dopplerUnit))
#                     print("rangeUnit : {}".format(rangeUnit))
#                     print("snrUnit : {}".format(snrUnit))
#                     pointCloud = pointCloud[20:]
#                     pointValue = binascii.hexlify((pointCloud))
#                     #print(pointValue)
#                     cnt1 = tlvLength-28

#                     while True:
#                     #for k in range(0, tlvLength-28, 8):
#                         elevation, azimuth, doppler, range, snr = struct.unpack("2B3H", pointValue[:8])
#                         print("elevation : {}".format(elevation * elevationUnit))
#                         print("azimuth : {}".format(azimuth * azimuthUnit))
#                         print("doppler : {}".format(doppler * dopplerUnit))
#                         print("range : {}".format(range * rangeUnit))
#                         print("snr : {}".format(snr * snrUnit))
#                         cnt1 = cnt1 - 8
#                         if cnt1 == 0:
#                             break
#                         pointValue = pointValue[8:]
#             elif tlvType == 0x07:
#                 targetList = data[8:tlvLength]
#                 targetValue = binascii.hexlify((targetList))
#                 tid, posX, posY, posZ, velX, velY, velZ, accX, accY, accz, ec0, ec1, ec2, ec3, ec4, ec5, ec6, ec7, ec8, ec9, ec10, ec11, ec12, ec13, ec14, ec15, g, confidenceLevel = struct.unpack("I9f16f2f", targetList[:112])
#                 print("tid : {}".format(tid))
#                 print("posX : {}".format(posX))
#                 print("posY : {}".format(posY))
#                 print("posZ : {}".format(posZ))
#                 print("velX : {}".format(velX))
#                 print("velY : {}".format(velY))
#                 print("velZ : {}".format(velZ))
#                 targetList = targetList[112:]
#                 #print(data[8:tlvLength])
#             elif tlvType == 0x08:
#                 targetIndex = data[8:tlvLength]
#                 #print(data[8:tlvLength])
#             elif tlvType == 0x0c:
#                 presence = data[8:tlvLength]
#                 exit = struct.unpack("I", presence)
#                 print("Presence : {}".format(exit))
#                 #print(data[8:tlvLength])
#             elif tlvType == 0x0a:
#                 targetIndex = data[8:tlvLength]
#                 unwrap_waveform1, unwra_waveform2,heart_waveform1, heart_waveform2, breathing_waveform1, breathing_waveform2, heart_rate1, heart_rate2, breathing_rate1, breathing_rate2, x1, x2, y1, y2, z1, z2, id1, id2, range1, range2, angle1, angele2, rangeidx1, rangeidx2, angleidx1, angleidx2 = struct.unpack("22f4H", targetIndex[:96])

#                 print("heart_rate1 : {}".format(heart_rate1))
#                 print("heart_rate2 : {}".format(heart_rate2))
#                 print("breathing1 : {}".format(breathing_waveform1))
#                 print("breathing2 : {}".format(breathing_waveform2))
#                 #print(data[8:tlvLength])
#             cnt = cnt - 1
#             if cnt == 0:
#                 break
#             data = data[tlvLength:]

#     else:
#         pass
