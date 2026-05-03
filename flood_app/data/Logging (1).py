import csv
import time
import requests
import re
import os

# --- CONFIGURATION ---
ESP32_URL = "http://192.168.4.1/reading"   # ESP32 endpoint
FILE_NAME = "data/sample_readings.csv"
POLL_INTERVAL = 0.5  # seconds → 2 readings per second

# --- Accept ONLY lines like: number,number ---
data_pattern = re.compile(r"^\d+,\d+$")

try:
    # Ensure folder exists
    os.makedirs(os.path.dirname(FILE_NAME), exist_ok=True)

    print(f"Connecting to ESP32 at {ESP32_URL}")
    print(f"Logging data to {FILE_NAME}")
    print("Press Ctrl+C to stop.\n")

    with open(FILE_NAME, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header if file is empty
        if file.tell() == 0:
            writer.writerow(["Distance_CM", "Timestamp_MS"])

        while True:
            try:
                response = requests.get(ESP32_URL, timeout=2)
                line = response.text.strip()

                # ✅ Filter valid sensor output
                if data_pattern.match(line):
                    distance, timestamp = line.split(",")
                    writer.writerow([distance, timestamp])
                    file.flush()
                    print(f"Recorded → Distance: {distance} cm | Time: {timestamp} ms")
                else:
                    print("Ignored:", line)

            except requests.exceptions.RequestException as e:
                print("ESP32 not reachable:", e)

            time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("\nLogging stopped by user.")

except Exception as e:
    print("Error:", e)