import fitparse
import numpy as np
import pandas as pd
import json

# Load settings from JSON
with open('settings.json', 'r') as file:
    settings = json.load(file)

ftp = settings['FTP']
SPEED_THRESHOLD_KMH = settings['SpeedThresholdKMH']
SPEED_THRESHOLD = SPEED_THRESHOLD_KMH / 3.6  # Convert km/h to m/s

# Load the FIT file
fitfile = fitparse.FitFile("test_activity.fit")

# Lists to store data
power_data = []
hr_data = []
speed_data = []
timestamps = []

# Extract data from the FIT file
for record in fitfile.get_messages("record"):
    power = record.get_value('power')
    hr = record.get_value('heart_rate')
    speed = record.get_value('speed')
    timestamp = record.get_value('timestamp')
    
    if power is not None and hr is not None and speed is not None:
        power_data.append(power)
        hr_data.append(hr)
        speed_data.append(speed)
        timestamps.append(timestamp)

# Convert lists to DataFrame for easier processing
df_power = pd.DataFrame({'power': power_data, 'timestamp': timestamps, 'speed': speed_data, 'heart_rate': hr_data})

# Calculate NP, IF, and TSS
norm_power = np.sqrt(np.sqrt(np.mean(df_power['power'].rolling(15).mean() ** 4)))
intensity = norm_power / ftp
moving_time = df_power['timestamp'].iloc[-1].timestamp() - df_power['timestamp'].iloc[0].timestamp()
tss = (moving_time * norm_power * intensity) / (ftp * 3600.0) * 100.0

# Calculate Average Power, Heart Rate, and Duration Metrics
average_power = df_power['power'].mean()
average_heart_rate = df_power['heart_rate'].mean()

# Calculate pause time using speed data
pauses = (df_power[df_power['speed'] < SPEED_THRESHOLD]['timestamp'].diff() > pd.Timedelta(seconds=1)).sum()
activity_duration = int(moving_time) - pauses

# Convert seconds to hh:mm:ss format
def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

# Function to print values in a tabulated manner
def print_tabulated(label, value):
    print("{:<25} {:<15}".format(label, value))

# Print headers
print_tabulated("Metric", "Value")

# Horizontal line
print("-" * 40)

# Output metrics in tabulated format
print_tabulated("FTP", int(ftp))
print_tabulated("Watt Ø", int(average_power))
print_tabulated("bpm Ø", int(average_heart_rate))
print_tabulated("NP ®", int(norm_power))
print_tabulated("IF ®", round(intensity, 2))
print_tabulated("TSS ®", int(tss))
print_tabulated("Total Duration", seconds_to_hms(int(moving_time)))
print_tabulated("Activity Duration", seconds_to_hms(activity_duration))
print_tabulated("Pause Time", seconds_to_hms(pauses))
