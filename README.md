
# TI's IWR6843ISK FMCW radar serial data parsing , Python API , MATLAB API.

This repository provides a Python interface for the IWR6843ISK radar sensor, enabling real-time vital signs monitoring (heart rate and breath rate) along with advanced data processing and visualization. It captures and processes data from the sensor, providing real-time vital signs, waveforms, and additional data outputs like coordinates, number of detected objects, Doppler values, and point cloud data.

The IWR6843ISK is a 60- to 64-GHz mmWave sensor with 4 receive (RX) and 3 transmit (TX) antennas, providing a wide 120° azimuth field of view (FoV) and 30° elevation FoV. It interfaces directly with the MMWAVEICBOOST and DCA1000 and supports a 60-pin high-speed interface for host control. This platform also provides onboard capability for power-consumption monitoring.
![image](https://github.com/user-attachments/assets/e981bfb8-ae88-48e4-8c7e-8359e2184407)

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
   
![image](https://github.com/user-attachments/assets/45f48325-8eb0-43b5-aad2-e26da11765de)


## Project Structure

-   `RadarSystemIntegration.py`: Main script for running the vital signs monitoring application.  Includes parsing logic, plotting functions, and rolling average calculations.
-   `[Configuration File]`: Radar configuration file (e.g., `vital_signs_ISK_2m.cfg`).  This file is read by the script to configure the radar sensor.


