from datetime import datetime
import csv
import json
import os

def save_candidates_to_csv(data):
    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_file_name = f"candidates_{timestamp}.csv"
    csv_file_path = os.path.join(output_folder, csv_file_name)

    print(f"Saving to file: {csv_file_path}")

    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["name", "email", "phone_number", "matching_score"])

    for i in data:
        json_data = json.loads(i)
        if "error" not in json_data:
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([json_data["name"], json_data["email"], json_data["phone_number"], json_data["matching_score"]])
    print(f"File Saved at: {csv_file_path}")