# Folder path where images are stored
import time
from kafka import KafkaProducer
import json
import datetime
import os

folder_path = "/app/picture"

# Get current date
current_date = datetime.datetime.now()

print(current_date)
# Function to list files in the folder
def get_files(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

# Filter files with date earlier than current date
def filter_files(files, current_date):
    filtered_files = []
    # Strip the time part from current_date
    current_date = current_date.date()
    
    for file in files:
        try:
            # Extract the date part from the filename (excluding the .jpg extension)
            file_date_str = file.replace('.jpg', '')
            
            # Parse the date from the filename
            file_date = datetime.datetime.strptime(file_date_str, '%B %d, %Y').date()
            
            # Check if the file date is earlier than the current date
            if file_date < current_date:
                filtered_files.append(file)
        except ValueError:
            # If the filename doesn't match the expected format, skip it
            continue
    return filtered_files



# Kafka Producer
producer = KafkaProducer(bootstrap_servers='172.25.0.13:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def send_to_kafka(file_path):
    metadata = {
        "file_path": file_path,
        "timestamp": datetime.datetime.now().isoformat()
    }
    print(metadata)
    print("send ok")
    producer.send('photos_topic', metadata)
    producer.flush()
'''
# Monitor the folder
while True:
    files = get_files(folder_path)
    filtered_files = filter_files(files, current_date)
    print(files)
    print(filter_files)
    # Send filtered files to Kafka
    for file in filtered_files:
        file_path = os.path.join(folder_path, file)
        print(file_path)
        send_to_kafka(file_path)
    print('done')
    # Sleep or set a scheduled interval
    time.sleep(5)  # Check every minute
'''

files = get_files(folder_path)
filtered_files = filter_files(files, current_date)
print(files)
print(filter_files)
# Send filtered files to Kafka
for file in filtered_files:
    file_path = os.path.join(folder_path, file)
    print(file_path)
    send_to_kafka(file_path)
print('done')
