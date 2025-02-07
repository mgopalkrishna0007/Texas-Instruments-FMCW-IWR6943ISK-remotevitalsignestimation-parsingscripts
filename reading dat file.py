import os
import sys
import numpy as np
import pandas as pd

# Add the path to parser_mmw_demo.py to sys.path
parser_mmw_demo_path = r"C:\ti\mmwave_sdk_03_05_00_04\packages\ti\demo\parser_scripts"
sys.path.append(parser_mmw_demo_path)

from parser_mmw_demo import parser_one_mmw_demo_output_packet

def populate_result_dictionary(dictionary, frame_number, results, obj):
    """
    Populates the dictionary with parsed data for a specific object.
    
    Args:
        dictionary (dict): Dictionary to store results.
        frame_number (int): Current frame number.
        results (list): Parsed results from the packet.
        obj (int): Index of the object to be processed.
    """
    dictionary["frame_number"].append(frame_number)
    dictionary["x"].append(results[6][obj])
    dictionary["y"].append(results[7][obj])
    dictionary["z"].append(results[8][obj])
    dictionary["v"].append(results[9][obj])
    dictionary["azimuth"].append(results[11][obj])
    dictionary["snr"].append(results[13][obj])

if __name__ == "__main__":
    # Hardcode the data path
    data_path = r"C:\Users\GOPAL\Downloads\xwr68xx_processed_stream_2024_09_02T18_52_42_661.dat"

    try:
        # Load the file
        with open(data_path, "rb") as f:
            data = f.read()

        data = np.frombuffer(data, dtype="uint8")
        byte_count = len(data)
        magic_word = np.array([2, 1, 4, 3, 6, 5, 8, 7], dtype="uint8")

        # Finding frames
        condition = data == magic_word[0]
        possible_idxs = np.argwhere(condition)
        frame_start_idx = [idx for idx in possible_idxs.squeeze() if np.all(data[idx: idx + 8] == magic_word)]

        print(f"Found {len(frame_start_idx)} packets/frames")

        # Dictionary initialization
        output_columns = ["frame_number", "x", "y", "z", "v", "azimuth", "snr"]
        output_data_dict = {k: [] for k in output_columns}

        for frame_number, idx in enumerate(frame_start_idx):
            temp_data = data[idx:]
            temp_byte_count = len(temp_data)
            results = parser_one_mmw_demo_output_packet(temp_data, temp_byte_count)
            
            if results[0] == 0:  # Check frame validity
                count_objects = results[3]
                if count_objects > 0:
                    for obj in range(count_objects):
                        populate_result_dictionary(output_data_dict, frame_number, results, obj)

        # Convert to DataFrame and save
        df = pd.DataFrame(output_data_dict)

        if not os.path.exists("out_data"):
            os.makedirs("out_data")

        out_filename = input("Specify the output filename: ")
        df.to_csv(os.path.join("out_data", out_filename), index=None)
        print(f"Data saved to 'out_data/{out_filename}'")

    except Exception as e:
        print(f"An error occurred: {e}")
