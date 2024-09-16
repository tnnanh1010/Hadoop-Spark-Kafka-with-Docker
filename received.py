from pyspark import SparkConf
from pyspark.sql import SparkSession
import os
from kafka import KafkaConsumer
import json
import base64
import shutil


# Initialize SparkSession
spark = SparkSession.builder \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.fs.hdfs.impl", "org.apache.hadoop.hdfs.DistributedFileSystem") \
    .appName("read-s3-with-spark") \
    .getOrCreate()


# Kafka Consumer
consumer = KafkaConsumer(
    'photos_topic',
    bootstrap_servers='172.25.0.13:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)
print(consumer)

# Base path for Hadoop
hadoop_base_path = "/app/hadoop"

# Local temporary folder
temp_folder = "/app/temp"

# Ensure temp folder exists
os.makedirs(temp_folder, exist_ok=True)

# Process Kafka messages
for message in consumer:
    print("Received message: {}".format(message.value))
    
    if 'file_path' in message.value:
        file_path = message.value['file_path']
        print("File path: {}".format(file_path))
        
        # Check if the file exists
        if os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            temp_file_path = os.path.join(temp_folder, file_name)

            # Move file to temporary folder
            shutil.copy(file_path, temp_file_path)

            # Read the file as binary data
            with open(temp_file_path, "rb") as file:
                binary_data = file.read()
                encoded_image = base64.b64encode(binary_data).decode('utf-8')
                print("Loaded image (base64): {}...".format(encoded_image[:100]))  # Print first 100 chars for brevity

            # Create an HDFS path for this file
            hadoop_file_path = os.path.join(hadoop_base_path, file_name)

            print(file_name)
            # Save the encoded image to Hadoop
            df = spark.createDataFrame([(file_name, encoded_image)], ["file_name", "image_data"])
            final_path = 'hdfs://namenode:9000/user/hdfs/' + file_name

            print("Writing {} to Hadoop: {}".format(file_name, final_path))

            df.write.mode("overwrite").format("json").save(final_path)

            # Clean up temporary file
            os.remove(temp_file_path)

        else:
            print("File {} does not exist.".format(file_path))
    else:
        print("Error: 'file_path' key not found in the message.")
