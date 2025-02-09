
# TI's IWR6843ISK FMCW radar serial data parsing , Python API , MATLAB API.

This repository provides a Python interface for the IWR6843ISK radar sensor, enabling real-time vital signs monitoring (heart rate and breath rate) along with advanced data processing and visualization. It captures and processes data from the sensor, providing real-time vital signs, waveforms, and additional data outputs like coordinates, number of detected objects, Doppler values, and point cloud data.

The IWR6843ISK is a 60- to 64-GHz mmWave sensor with 4 receive (RX) and 3 transmit (TX) antennas, providing a wide 120° azimuth field of view (FoV) and 30° elevation FoV. It interfaces directly with the MMWAVEICBOOST and DCA1000 and supports a 60-pin high-speed interface for host control. This platform also provides onboard capability for power-consumption monitoring.
![image](https://github.com/user-attachments/assets/e981bfb8-ae88-48e4-8c7e-8359e2184407)

## Features

-   **Real-time Heart Rate and Breath Rate Monitoring**: Displays heart rate and breath rate in real-time.
    -   Includes thresholding for breath hold detection.
-   **Waveform Visualization**: Visualizes heart and breath waveforms.
    -   Dynamically updates plot limits for optimal viewing.
-   **Holding Breath Detection**: Detects when the user is holding their breath based on waveform data.
-   **Rolling Average Calculation**: Calculates and displays the rolling average of the last 40 heart rate and breath rate readings (adjustable in code).
-   **Data Logging**: Logs all rolling average values for heart rate and breath rate.
    -   Prints a list of all rolling averages and the latest rolling average upon script termination.
-   **Radar Data Parsing**: Includes parsing scripts to decode serial data from the IWR6843ISK sensor.
-   **GUI Data Output**: Outputs GUI data, including coordinates, waveforms, the number of objects detected.
-   **Doppler Values**: Extracts and processes Doppler values.
-   **Point Cloud Data**: Extracts and processes point cloud data.

  ![image](https://github.com/user-attachments/assets/0db2d2f3-11c8-4587-a45f-e5122c324cda)


## Requirements

-   Python 3.6+
-   Required Python libraries:
    -   numpy
    -   matplotlib
    -   pyserial
-   IWR6843ISK radar sensor
-   mmWave SDK
-   MMWAVEICBOOST and DCA1000 (optional, for advanced configurations)

## Installation

1.  Clone the repository:

    ```
    git clone [https://github.com/mgopalkrishna0007/Texas-Instruments-FMCW-IWR6943ISK-remotevitalsignestimation-parsingscripts/]
    cd [https://github.com/mgopalkrishna0007/Texas-Instruments-FMCW-IWR6943ISK-remotevitalsignestimation-parsingscripts/]
    ```

2.  Install the required Python libraries:

    ```
    pip install numpy matplotlib pyserial
    ```

## Configuration

1.  **Radar Configuration**:
    -   Ensure the correct chirp configuration file (`.cfg`) is specified in the `radarCfgFile` variable in `main.py`.  Example path: `C:\ti\radar_toolbox_2_10_00_04\source\ti\examples\Medical\Vital_Signs_With_People_Tracking\chirp_configs\vital_signs_ISK_2m.cfg`
2.  **Serial Port Configuration**:
    -   Update `cliSerialPort` and `dataSerialPort` with the correct COM ports for the CLI and Data ports of the IWR6843ISK sensor in `main.py`.  Example:

        ```
        cliSerialPort = 'COM3'  # CLI port (Windows)
        dataSerialPort = 'COM7' # Data port (Windows)
        # OR
        # cliSerialPort = '/dev/ttyUSB0'  # CLI port (Linux)
        # dataSerialPort = '/dev/ttyUSB1'  # Data port (Linux)
        ```

    -   **Important:** Ensure you comment out the Windows ports when using Linux, and vice versa.

## Usage

1.  Connect the IWR6843ISK radar sensor to your computer.
2.  Run the main script:

    ```
    python3 RadarSystemIntegration.py
    ```

3.  The script will:

    -   Send the configuration commands to the sensor.
    -   Display real-time heart rate and breath rate.
    -   Show heart and breath waveforms in a plot.
    -   Calculate and display rolling averages of heart rate and breath rate.
    -   Output additional data such as coordinates, the number of detected objects, Doppler values, and point cloud data.

4.  To terminate the script, press `Ctrl+C`. The script will output a list of all rolling average values calculated during the session, along with the most recent rolling average.

## Project Structure

-   `RadarSystemIntegration.py`: Main script for running the vital signs monitoring application.  Includes parsing logic, plotting functions, and rolling average calculations.
-   `[Configuration File]`: Radar configuration file (e.g., `vital_signs_ISK_2m.cfg`).  This file is read by the script to configure the radar sensor.

## Key Code Elements

-   **`parseVitalSignsTLV(tlvData, tlvLength)`:** Parses the TLV data to extract heart and breath waveforms, heart rate, and breath rate.
-   **`read_and_parse_data(serial_port)`:** Reads data from the serial port and calls `process_tlv_data` to parse the data.
-   **`process_tlv_data(data)`:** Processes the TLV data, extracts vital signs, and calls functions to update plots and calculate rolling averages.
-   **`update_rolling_average(breath_rate, heart_rate, holding_breath)`:** Calculates and stores rolling averages of breath rate and heart rate.  The number of readings for the rolling average can be adjusted by changing the `maxlen` parameter when initializing `breath_rate_readings` and `heart_rate_readings` and modifying the `if reading_counter == 40:` condition.
-   **`update_plot()`:** Updates the matplotlib plot with new waveform data.
-   **`send_config_to_sensor(cliDevice, radarCfgFile)`:** Sends configuration commands to the mmWave sensor through the CLI serial port.
-   **`signal_handler(sig, frame)`:** Handles program termination, printing the list of rolling averages.

## Additional Information

-   **Antenna Configuration**: The IWR6843ISK features a sophisticated antenna array with 4 RX and 3 TX antennas. This configuration enables a wide 120° azimuth field of view and 30° elevation FoV.

## Troubleshooting

-   **Serial Port Issues**:
    -   Ensure the correct serial ports are configured in `main.py`.  Remember to select the appropriate ports for your operating system (Windows or Linux).
    -   Verify that the sensor is properly connected to your computer.
-   **Data Parsing Errors**:
    -   Check that the `HEADER_SIZE` and data structures match the sensor's output format.  Verify the byte order (`byteorder='little'`) is correct for your sensor.
-   **Plotting Issues**:
    -   Make sure `matplotlib` is installed correctly.
-   **Configuration Issues**:
    -   Double-check the path to the `.cfg` file and ensure it exists.
    -   Verify the configuration commands are being sent to the sensor successfully by observing the output in the console.

