import serial
import time
import numpy as np
import matplotlib.pyplot as plt

# Change the configuration file name
configFileName = 'C:/ti/radar_toolbox_2_10_00_04/source/ti/examples/Medical/Vital_Signs_With_People_Tracking/chirp_configs/vital_signs_ISK_6m.cfg'

CLIport = {}
Dataport = {}
byteBuffer = np.zeros(2**15, dtype='uint8')
byteBufferLength = 0

# Function to configure the serial ports and send the data from the configuration file to the radar
def serialConfig(configFileName):
    global CLIport
    global Dataport

    print("Starting serial configuration...")
    # Open the serial ports for the configuration and the data ports
    try:
        CLIport = serial.Serial('COM3', 115200)
        Dataport = serial.Serial('COM7', 921600)
        print("Serial ports opened successfully.")
    except serial.SerialException as e:
        print(f"Error opening serial ports: {e}")
        return None, None

    # Read the configuration file and send it to the board
    try:
        with open(configFileName, 'r') as f:
            config = [line.rstrip('\r\n') for line in f]
            print(f"Configuration file {configFileName} loaded.")
    except FileNotFoundError:
        print(f"Error: The configuration file {configFileName} was not found.")
        return None, None

    for i in config:
        CLIport.write((i + '\n').encode())
        print(f"Sent config: {i}")
        time.sleep(0.01)
        
    print("Serial configuration completed.")
    return CLIport, Dataport

# Function to read and parse the incoming data
def readAndParseData14xx(Dataport, configParameters):
    global byteBuffer, byteBufferLength
    
    print("Starting data read and parse...")
    # Constants
    OBJ_STRUCT_SIZE_BYTES = 12
    BYTE_VEC_ACC_MAX_SIZE = 2**15
    MMWDEMO_UART_MSG_DETECTED_POINTS = 1
    MMWDEMO_UART_MSG_RANGE_PROFILE = 2
    maxBufferSize = 2**15
    magicWord = [2, 1, 4, 3, 6, 5, 8, 7]
    
    # Initialize variables
    magicOK = 0  # Checks if magic number has been read
    dataOK = 0  # Checks if the data has been read correctly
    frameNumber = 0
    detObj = {}
    
    print("Reading from Dataport...")
    readBuffer = Dataport.read(Dataport.in_waiting)
    print(f"Read {len(readBuffer)} bytes from Dataport.")
    byteVec = np.frombuffer(readBuffer, dtype='uint8')
    byteCount = len(byteVec)
    
    # Check that the buffer is not full, and then add the data to the buffer
    if (byteBufferLength + byteCount) < maxBufferSize:
        byteBuffer[byteBufferLength:byteBufferLength + byteCount] = byteVec[:byteCount]
        byteBufferLength += byteCount
        print(f"Added {byteCount} bytes to byteBuffer. Current length: {byteBufferLength}.")
        
    # Check that the buffer has some data
    if byteBufferLength > 16:
        print("Checking for magic word in buffer...")
        # Check for all possible locations of the magic word
        possibleLocs = np.where(byteBuffer == magicWord[0])[0]

        # Confirm that is the beginning of the magic word and store the index in startIdx
        startIdx = []
        for loc in possibleLocs:
            check = byteBuffer[loc:loc+8]
            if np.all(check == magicWord):
                startIdx.append(loc)
               
        # Check that startIdx is not empty
        if startIdx:
            print(f"Magic word found at index: {startIdx[0]}")
            # Remove the data before the first start index
            if startIdx[0] > 0 and startIdx[0] < byteBufferLength:
                byteBuffer[:byteBufferLength-startIdx[0]] = byteBuffer[startIdx[0]:byteBufferLength]
                byteBuffer[byteBufferLength-startIdx[0]:] = np.zeros(len(byteBuffer[byteBufferLength-startIdx[0]:]), dtype='uint8')
                byteBufferLength -= startIdx[0]
                
            # Check that there have no errors with the byte buffer length
            if byteBufferLength < 0:
                byteBufferLength = 0
                
            # word array to convert 4 bytes to a 32 bit number
            word = [1, 2**8, 2**16, 2**24]
            
            # Read the total packet length
            totalPacketLen = np.matmul(byteBuffer[12:12+4], word)
            print(f"Total packet length: {totalPacketLen}")
            # Check that all the packet has been read
            if (byteBufferLength >= totalPacketLen) and (byteBufferLength != 0):
                magicOK = 1
                print("Magic word is OK, proceeding with parsing.")

    # If magicOK is equal to 1 then process the message
    if magicOK:
        print("Parsing the message...")
        # word array to convert 4 bytes to a 32 bit number
        word = [1, 2**8, 2**16, 2**24]
        
        # Initialize the pointer index
        idX = 0
        
        # Read the header
        magicNumber = byteBuffer[idX:idX+8]
        idX += 8
        version = format(np.matmul(byteBuffer[idX:idX+4], word), 'x')
        idX += 4
        totalPacketLen = np.matmul(byteBuffer[idX:idX+4], word)
        idX += 4
        platform = format(np.matmul(byteBuffer[idX:idX+4], word), 'x')
        idX += 4
        frameNumber = np.matmul(byteBuffer[idX:idX+4], word)
        idX += 4
        timeCpuCycles = np.matmul(byteBuffer[idX:idX+4], word)
        idX += 4
        numDetectedObj = np.matmul(byteBuffer[idX:idX+4], word)
        idX += 4
        numTLVs = np.matmul(byteBuffer[idX:idX+4], word)
        idX += 4
        idX += 4
        
        print(f"Frame Number: {frameNumber}, Number of Detected Objects: {numDetectedObj}, Number of TLVs: {numTLVs}")
        
        # Read the TLV messages
        for tlvIdx in range(numTLVs):
            # word array to convert 4 bytes to a 32 bit number
            word = [1, 2**8, 2**16, 2**24]

            # Check the header of the TLV message
            tlv_type = np.matmul(byteBuffer[idX:idX+4], word)
            idX += 4
            tlv_length = np.matmul(byteBuffer[idX:idX+4], word)
            idX += 4
            
            print(f"Processing TLV Type: {tlv_type}, TLV Length: {tlv_length}")
            
            if tlv_type == MMWDEMO_UART_MSG_DETECTED_POINTS:
                # Initialize variables
                rangeIdx = np.zeros(numDetectedObj, dtype='int')
                DopplerIdx = np.zeros(numDetectedObj, dtype='int')
                peakVal = np.zeros(numDetectedObj, dtype='int')
                x = np.zeros(numDetectedObj, dtype='float')
                y = np.zeros(numDetectedObj, dtype='float')
                z = np.zeros(numDetectedObj, dtype='float')
                noise = np.zeros(numDetectedObj, dtype='float')
                
                # Initialize the arrays to store the data
                for i in range(numDetectedObj):
                    # Extract the data
                    rangeIdx[i] = np.matmul(byteBuffer[idX:idX+4], word)
                    DopplerIdx[i] = np.matmul(byteBuffer[idX+4:idX+8], word)
                    peakVal[i] = np.matmul(byteBuffer[idX+8:idX+12], word)
                    
                    # Update the index
                    idX += 12
                    
                    # Store the extracted data
                    detObj[i] = {
                        'rangeIdx': rangeIdx[i],
                        'DopplerIdx': DopplerIdx[i],
                        'peakVal': peakVal[i],
                    }
                    
                dataOK = 1
                print(f"Detected Points: {numDetectedObj}, Data OK: {dataOK}")
                
            elif tlv_type == MMWDEMO_UART_MSG_RANGE_PROFILE:
                print("Range Profile TLV received (not implemented).")
                pass # Implement if needed
                
        if dataOK:
            print("Data processing completed.")
            return detObj
        
    print("Exiting readAndParseData14xx function.")
    return {}

# Function to plot the data
def plot_data(detObj):
    print("Plotting data...")
    ranges = [obj['rangeIdx'] for obj in detObj.values()]
    velocities = [obj['DopplerIdx'] for obj in detObj.values()]

    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(ranges, label='Range Index')
    plt.xlabel('Object Index')
    plt.ylabel('Range Index')
    plt.title('Range Index of Detected Objects')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(velocities, label='Doppler Index')
    plt.xlabel('Object Index')
    plt.ylabel('Doppler Index')
    plt.title('Doppler Index of Detected Objects')
    plt.legend()

    plt.tight_layout()
    plt.show()
    print("Plotting completed.")

# Main code execution
if __name__ == "__main__":
    print("Starting main execution...")
    CLIport, Dataport = serialConfig(configFileName)
    
    if CLIport and Dataport:
        configParameters = {
            "numDopplerBins": 128,
            "numRangeBins": 512,
            "rangeResolutionMeters": 0.01,
            "rangeIdxToMeters": 0.01,
        }
        
        while True:
            detObj = readAndParseData14xx(Dataport, configParameters)
            if detObj:
                plot_data(detObj)
            time.sleep(0.1)
