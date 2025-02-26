import os
import csv
import pandas as pd

# Define the base directory where all the directories are located
base_directory = "/loghub"


def merge_each_column():
    df = pd.read_csv(f'{base_directory}/HDFS_v3_TraceBench/tracebench/AN_Data_corruptBlk_r_00FDN_30C_1to19B_0to120INT_15RT_5WT/event.csv', index_col=False)
    df['OriginalLog'] = df.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    # Save the updated DataFrame to a new CSV file
    df.to_csv(f'{base_directory}/HDFS_v3_TraceBench/tracebench/AN_Data_corruptBlk_r_00FDN_30C_1to19B_0to120INT_15RT_5WT/merged_logs.csv', index=False)
    print("CSV saved as 'merged_logs.csv'")



def merge_log_csv():
    # Iterate through all directories in the base directory
    for dirname in os.listdir(base_directory):
        dir_path = os.path.join(base_directory, dirname)
        
        # Only process if it's a directory
        if os.path.isdir(dir_path):
            # Define the .log and .csv file paths
            log_file_path = os.path.join(dir_path, f"{dirname}_2k.log")
            csv_file_path = os.path.join(dir_path, f"{dirname}_2k.log_structured.csv")
            output_csv_path = os.path.join(dir_path, f"{dirname}_merged.csv")

            # Check if both log file and CSV file exist
            if os.path.exists(log_file_path) and os.path.exists(csv_file_path):
                print(f"Processing directory: {dirname}")
                
                # Step 1: Read the log file and store lines
                with open(log_file_path, 'r') as log_file:
                    log_lines = log_file.readlines()

                # Step 2: Open the CSV file and read its content
                with open(csv_file_path, mode='r', newline='') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    csv_data = list(csv_reader)  # Read all the data into a list

                # Step 3: Add a new field 'OriginalLog' to each row in the CSV
                for i, row in enumerate(csv_data):
                    if i < len(log_lines):
                        row['OriginalLog'] = log_lines[i].strip()  # Add corresponding log line
                    else:
                        row['OriginalLog'] = ""  # If no matching log line, leave it empty

                # Step 4: Write the updated CSV data with the new 'OriginalLog' field
                with open(output_csv_path, mode='w', newline='') as output_csv:
                    fieldnames = csv_reader.fieldnames + ['OriginalLog']  # Add the new field to the header
                    csv_writer = csv.DictWriter(output_csv, fieldnames=fieldnames)

                    csv_writer.writeheader()  # Write header
                    csv_writer.writerows(csv_data)  # Write updated rows

                print(f"Updated CSV file saved at: {output_csv_path}")
            else:
                print(f"Skipping directory {dirname}: log or CSV file not found")

if __name__ == "__main__":
    merge_each_column()