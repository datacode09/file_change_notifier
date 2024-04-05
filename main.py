import os
import datetime

# Path to the directory you want to scan
directory_to_scan = "/path/to/directory"

# Calculate the cutoff time for files (24 hours ago from now)
cutoff_time = datetime.datetime.now() - datetime.timedelta(days=1)

# Walk through the directory and its subdirectories
for root, dirs, files in os.walk(directory_to_scan):
    for file in files:
        if file.endswith(('.py', '.sh')):
            # Full path to the file
            full_path = os.path.join(root, file)
            # Get the modification time of the file
            modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
            # If the file was modified within the last 24 hours, print it
            if modification_time > cutoff_time:
                print(f"Modified: {full_path}")

